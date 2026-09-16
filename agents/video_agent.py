"""
CrowdWisdom Trading - Video Agent

Reads:
    data/storyboard.json

Creates:
    data/final_ad.mp4

The agent builds a cinematic 9:16 social ad from the storyboard using:
- Pillow for scene artwork
- MoviePy for animation/compositing
- imageio-ffmpeg for FFmpeg
- macOS `say` for local voiceover generation
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
STORYBOARD_PATH = ROOT / "data" / "storyboard.json"
OUTPUT_DIR = ROOT / "data"
OUTPUT_VIDEO = OUTPUT_DIR / "final_ad.mp4"

WIDTH = 1080
HEIGHT = 1920
FPS = 24

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


# ---------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------

BG = (8, 10, 15)
WHITE = (245, 247, 250)
MUTED = (165, 173, 185)
RED = (238, 72, 82)
GREEN = (55, 210, 130)
BLUE = (70, 130, 255)
GOLD = (242, 190, 70)
CYAN = (70, 220, 220)


# ---------------------------------------------------------------------
# FONT HELPERS
# ---------------------------------------------------------------------

def find_font(size: int, bold: bool = False) -> str:
    candidates = []

    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        ]
    else:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(find_font(size, bold), size)


# ---------------------------------------------------------------------
# TEXT HELPERS
# ---------------------------------------------------------------------

def wrap_text(text: str, draw: ImageDraw.ImageDraw, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=fnt)

        if bbox[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    fnt,
    fill=WHITE,
    max_width=WIDTH - 120,
    stroke_width=0,
):
    lines = wrap_text(text, draw, fnt, max_width)
    line_height = int(fnt.size * 1.18)

    total_height = line_height * len(lines)

    start_y = y - total_height // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2

        draw.text(
            (x, start_y + i * line_height),
            line,
            font=fnt,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0),
        )

    return total_height


# ---------------------------------------------------------------------
# BACKGROUND / CINEMATIC EFFECTS
# ---------------------------------------------------------------------

def dark_gradient(top=(13, 17, 27), bottom=(2, 4, 8)) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()

    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)

        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)

        for x in range(WIDTH):
            px[x, y] = (r, g, b)

    return img


def vignette(img: Image.Image) -> Image.Image:
    overlay = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(overlay)

    center = (WIDTH // 2, HEIGHT // 2)
    radius = int(max(WIDTH, HEIGHT) * 0.72)

    for r in range(radius, 0, -12):
        alpha = int(255 * (1 - r / radius) ** 2)
        box = (
            center[0] - r,
            center[1] - r,
            center[0] + r,
            center[1] + r,
        )
        draw.ellipse(box, fill=alpha)

    overlay = overlay.filter(ImageFilter.GaussianBlur(140))

    black = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(img, black, overlay)


def add_noise(img: Image.Image, amount: int = 8) -> Image.Image:
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-amount, amount + 1, arr.shape[:2] + (1,))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


# ---------------------------------------------------------------------
# SCENE ART
# ---------------------------------------------------------------------

def scene_1() -> Image.Image:
    img = dark_gradient((22, 20, 30), (3, 4, 8))
    draw = ImageDraw.Draw(img)

    cards = [
        ("BUY", GREEN),
        ("SELL", RED),
        ("CRASH\nIMMINENT", RED),
        ("TO THE\nMOON", GOLD),
    ]

    positions = [
        (70, 300),
        (560, 400),
        (150, 850),
        (530, 960),
    ]

    for (text, color), (x, y) in zip(cards, positions):
        draw.rounded_rectangle(
            (x, y, x + 400, y + 280),
            radius=24,
            fill=(18, 22, 31),
            outline=color,
            width=7,
        )

        draw_centered_text(
            draw,
            text,
            y + 140,
            font(68, bold=True),
            color,
            max_width=350,
        )

    draw_centered_text(
        draw,
        "WHO'S RIGHT?",
        1520,
        font(95, bold=True),
        WHITE,
    )

    img = add_noise(img)
    return vignette(img)


def draw_chart(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int):
    draw.rectangle((x, y, x + w, y + h), fill=(10, 14, 22), outline=(39, 47, 61))

    for i in range(1, 6):
        yy = y + int(h * i / 6)
        draw.line((x, yy, x + w, yy), fill=(24, 30, 40), width=2)

    points = []

    for i in range(16):
        xx = x + 25 + i * (w - 50) // 15
        wave = math.sin(i * 0.7) * 45
        trend = i * 9
        yy = y + h // 2 - int(wave + trend)
        points.append((xx, yy))

    draw.line(points, fill=CYAN, width=7)


def scene_2() -> Image.Image:
    img = dark_gradient((11, 19, 30), (3, 5, 10))
    draw = ImageDraw.Draw(img)

    # Desk
    draw.rectangle(
        (0, 1420, WIDTH, HEIGHT),
        fill=(18, 15, 14),
    )

    # Screens
    screen_positions = [
        (40, 430, 500, 850),
        (580, 380, 1040, 820),
        (180, 880, 900, 1280),
    ]

    for pos in screen_positions:
        x1, y1, x2, y2 = pos
        draw.rounded_rectangle(
            pos,
            radius=20,
            fill=(7, 11, 17),
            outline=(42, 50, 65),
            width=6,
        )
        draw_chart(draw, x1 + 20, y1 + 55, x2 - x1 - 40, y2 - y1 - 80)

    # Trader silhouette
    cx = WIDTH // 2
    head_y = 1325

    draw.ellipse(
        (cx - 90, head_y - 120, cx + 90, head_y + 60),
        fill=(8, 9, 12),
    )

    draw.ellipse(
        (cx - 240, head_y + 40, cx + 240, head_y + 500),
        fill=(6, 7, 9),
    )

    # Coffee
    draw.rounded_rectangle(
        (100, 1530, 290, 1680),
        radius=25,
        fill=(50, 38, 32),
    )

    draw.rectangle(
        (290, 1575, 340, 1635),
        outline=(50, 38, 32),
        width=18,
    )

    # Alerts
    alert_font = font(34, bold=True)

    alerts = [
        "14 UNREAD",
        "BUY?",
        "SELL?",
        "CRASH?",
    ]

    for i, text in enumerate(alerts):
        y = 520 + i * 85
        draw.rounded_rectangle(
            (760, y, 1010, y + 60),
            radius=14,
            fill=(50, 15, 20),
            outline=RED,
            width=2,
        )
        draw.text(
            (790, y + 12),
            text,
            font=alert_font,
            fill=RED,
        )

    return vignette(add_noise(img))


def scene_3() -> Image.Image:
    img = dark_gradient((5, 20, 28), (2, 4, 9))
    draw = ImageDraw.Draw(img)

    cx, cy = WIDTH // 2, 820

    # Crowd particles
    np.random.seed(7)

    for _ in range(900):
        angle = np.random.random() * math.tau
        radius = 160 + np.random.random() * 500

        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * 0.75)

        size = np.random.choice([2, 3, 4, 5])

        draw.ellipse(
            (x - size, y - size, x + size, y + size),
            fill=(55, 150, 205),
        )

    # Central ticker
    draw.rounded_rectangle(
        (150, 650, 930, 990),
        radius=35,
        fill=(8, 13, 23),
        outline=(77, 108, 150),
        width=4,
    )

    draw_centered_text(
        draw,
        "MARKET = CROWD",
        730,
        font(64, bold=True),
        WHITE,
    )

    draw_centered_text(
        draw,
        "BEARISH 66.7%",
        850,
        font(76, bold=True),
        RED,
    )

    draw_centered_text(
        draw,
        "1-YEAR HIGH",
        930,
        font(38),
        MUTED,
    )

    draw_centered_text(
        draw,
        "ONE OPINION < THE CROWD",
        1400,
        font(55, bold=True),
        CYAN,
    )

    return vignette(add_noise(img))


def scene_4() -> Image.Image:
    img = dark_gradient((17, 22, 31), (5, 7, 12))
    draw = ImageDraw.Draw(img)

    # Product card
    card = (90, 250, 990, 1440)

    draw.rounded_rectangle(
        card,
        radius=42,
        fill=(245, 247, 250),
    )

    draw.text(
        (150, 325),
        "CROWDWISDOM",
        font=font(48, bold=True),
        fill=(25, 34, 50),
    )

    draw.text(
        (150, 435),
        "WEEKLY CONSENSUS",
        font=font(38, bold=True),
        fill=(82, 93, 110),
    )

    metrics = [
        ("ENTRY", "$612.40"),
        ("STOP", "$584.10"),
        ("TARGET", "$674.80"),
    ]

    for i, (label, value) in enumerate(metrics):
        y = 570 + i * 220

        draw.rounded_rectangle(
            (150, y, 930, y + 160),
            radius=22,
            fill=(232, 237, 244),
        )

        draw.text(
            (185, y + 25),
            label,
            font=font(34, bold=True),
            fill=(83, 96, 112),
        )

        draw.text(
            (185, y + 72),
            value,
            font=font(54, bold=True),
            fill=(23, 34, 51),
        )

    draw.text(
        (150, 1280),
        "Weighted by historical accuracy",
        font=font(33),
        fill=(76, 88, 104),
    )

    draw_centered_text(
        draw,
        "2,000+ VERIFIED TRADERS",
        1590,
        font(52, bold=True),
        WHITE,
    )

    return vignette(add_noise(img))


def scene_5() -> Image.Image:
    img = dark_gradient((39, 29, 17), (8, 10, 13))
    draw = ImageDraw.Draw(img)

    # Morning light
    for r in range(600, 0, -20):
        alpha = int(1.5 * (600 - r))
        color = (
            min(255, 70 + alpha // 3),
            min(255, 55 + alpha // 5),
            min(255, 20 + alpha // 8),
        )
        draw.ellipse(
            (
                1400 - r,
                320 - r,
                1400 + r,
                320 + r,
            ),
            fill=color,
        )

    # Desk
    draw.rectangle(
        (0, 1300, WIDTH, HEIGHT),
        fill=(44, 34, 26),
    )

    # Laptop
    draw.rounded_rectangle(
        (180, 650, 900, 1180),
        radius=35,
        fill=(25, 29, 37),
        outline=(100, 105, 112),
        width=6,
    )

    draw.rounded_rectangle(
        (230, 700, 850, 1040),
        radius=22,
        fill=(235, 239, 242),
    )

    draw.text(
        (285, 760),
        "CONSENSUS",
        font=font(42, bold=True),
        fill=(30, 42, 58),
    )

    draw.text(
        (285, 840),
        "ENTRY  •  STOP  •  TARGET",
        font=font(34, bold=True),
        fill=(50, 70, 90),
    )

    draw.rounded_rectangle(
        (285, 915, 720, 995),
        radius=25,
        fill=(53, 178, 112),
    )

    draw.text(
        (350, 933),
        "DECISION IN HAND",
        font=font(30, bold=True),
        fill=WHITE,
    )

    draw_centered_text(
        draw,
        "FROM RESEARCH\nTO ONE DECISION",
        1500,
        font(62, bold=True),
        WHITE,
    )

    return vignette(add_noise(img))


def scene_6() -> Image.Image:
    img = dark_gradient((7, 20, 24), (2, 5, 10))
    draw = ImageDraw.Draw(img)

    cx, cy = WIDTH // 2, 850

    # Network graph
    np.random.seed(22)
    points = []

    for _ in range(130):
        x = int(cx + np.random.uniform(-400, 400))
        y = int(cy + np.random.uniform(-480, 480))
        points.append((x, y))

    for i, p1 in enumerate(points):
        distances = []

        for j, p2 in enumerate(points):
            if i == j:
                continue

            dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
            distances.append((dist, p2))

        distances.sort(key=lambda x: x[0])

        for dist, p2 in distances[:2]:
            if dist < 220:
                draw.line(
                    (p1[0], p1[1], p2[0], p2[1]),
                    fill=(30, 87, 102),
                    width=2,
                )

    for x, y in points:
        draw.ellipse(
            (x - 6, y - 6, x + 6, y + 6),
            fill=CYAN,
        )

    # Center node
    draw.ellipse(
        (cx - 50, cy - 50, cx + 50, cy + 50),
        fill=WHITE,
    )

    draw_centered_text(
        draw,
        "READ THE CROWD",
        1500,
        font(68, bold=True),
        WHITE,
    )

    return vignette(add_noise(img))


def scene_7() -> Image.Image:
    img = dark_gradient((17, 28, 42), (4, 6, 12))
    draw = ImageDraw.Draw(img)

    draw_centered_text(
        draw,
        "CROWDWISDOM",
        520,
        font(88, bold=True),
        WHITE,
    )

    draw_centered_text(
        draw,
        "Stop trading blind.",
        760,
        font(64, bold=True),
        CYAN,
    )

    draw.rounded_rectangle(
        (180, 980, 900, 1160),
        radius=35,
        fill=(56, 180, 115),
    )

    draw_centered_text(
        draw,
        "GET MY FIRST DECISION",
        1070,
        font(42, bold=True),
        WHITE,
        max_width=650,
    )

    draw_centered_text(
        draw,
        "FREE WEEKLY BRIEFING • NO CREDIT CARD",
        1300,
        font(34, bold=True),
        WHITE,
        max_width=850,
    )

    draw_centered_text(
        draw,
        "Trading involves substantial risk.\nNot investment advice.",
        1660,
        font(28),
        MUTED,
        max_width=850,
    )

    return vignette(add_noise(img))


# ---------------------------------------------------------------------
# SCENE BUILDERS
# ---------------------------------------------------------------------

SCENE_BUILDERS = {
    1: scene_1,
    2: scene_2,
    3: scene_3,
    4: scene_4,
    5: scene_5,
    6: scene_6,
    7: scene_7,
}


def ken_burns_clip(image: Image.Image, duration: float, zoom_start=1.0, zoom_end=1.08):
    base = np.array(image.convert("RGB"))

    def make_frame(t: float):
        progress = min(1.0, max(0.0, t / duration))
        zoom = zoom_start + (zoom_end - zoom_start) * progress

        new_w = int(WIDTH * zoom)
        new_h = int(HEIGHT * zoom)

        frame = Image.fromarray(base).resize(
            (new_w, new_h),
            Image.Resampling.LANCZOS,
        )

        left = (new_w - WIDTH) // 2
        top = (new_h - HEIGHT) // 2

        frame = frame.crop(
            (left, top, left + WIDTH, top + HEIGHT)
        )

        return np.array(frame)

    clip = ImageClip(make_frame(0), duration=duration)
    clip = clip.transform(lambda get_frame, t: make_frame(t))

    return clip


def make_scene_clip(
    scene_number: int,
    duration: float,
):
    builder = SCENE_BUILDERS.get(scene_number)

    if builder is None:
        raise ValueError(f"No scene builder for scene {scene_number}")

    img = builder()

    return ken_burns_clip(
        img,
        duration=duration,
        zoom_start=1.0,
        zoom_end=1.06 if scene_number not in (1, 7) else 1.03,
    )


# ---------------------------------------------------------------------
# VOICEOVER
# ---------------------------------------------------------------------

def generate_voiceover(text: str, output_path: Path) -> Path | None:
    say_bin = shutil.which("say")

    if not say_bin:
        print("⚠️ macOS 'say' command not found; continuing without voiceover.")
        return None

    aiff_path = output_path.with_suffix(".aiff")

    cmd = [
        say_bin,
        "-v",
        "Samantha",
        "-r",
        "185",
        "-o",
        str(aiff_path),
        text,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )

        return aiff_path

    except subprocess.CalledProcessError as exc:
        print("⚠️ Voiceover generation failed:", exc.stderr)
        return None


# ---------------------------------------------------------------------
# MAIN VIDEO PIPELINE
# ---------------------------------------------------------------------

def load_storyboard() -> dict:
    if not STORYBOARD_PATH.exists():
        raise FileNotFoundError(
            f"Missing storyboard: {STORYBOARD_PATH}"
        )

    with STORYBOARD_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def create_video():
    print("🎬 Video Agent starting...")
    print(f"📖 Storyboard: {STORYBOARD_PATH}")
    print(f"🎞️ Output: {OUTPUT_VIDEO}")
    print(f"⚙️ FFmpeg: {FFMPEG}")

    storyboard = load_storyboard()

    scenes = storyboard.get("scenes", [])

    if not scenes:
        raise ValueError("Storyboard contains no scenes.")

    total_duration = float(storyboard.get("total_duration_seconds", 0))

    if not (30 <= total_duration <= 60):
        raise ValueError(
            f"Storyboard duration must be 30–60 seconds, got {total_duration}"
        )

    clips = []

    print(f"🎥 Building {len(scenes)} scenes...")

    for scene in scenes:
        number = int(scene["scene_number"])

        # Some storyboard versions may use 00:04-00:11 rather than duration.
        duration = float(scene["duration_seconds"])

        print(
            f"   Scene {number}: "
            f"{duration:.1f}s — {scene.get('purpose', '')}"
        )

        clip = make_scene_clip(number, duration)

        # Burn the scene's key on-screen text into the clip.
        text = scene.get("on_screen_text", "")

        if text:
            txt_img = Image.new(
                "RGBA",
                (WIDTH - 100, 300),
                (0, 0, 0, 0),
            )

            txt_draw = ImageDraw.Draw(txt_img)

            txt_font = font(37, bold=True)

            lines = wrap_text(
                str(text).replace("•", " • "),
                txt_draw,
                txt_font,
                WIDTH - 180,
            )

            y = 40

            for line in lines[:4]:
                bbox = txt_draw.textbbox((0, 0), line, font=txt_font)
                w = bbox[2] - bbox[0]

                txt_draw.rounded_rectangle(
                    (
                        (WIDTH - 100 - w) // 2 - 20,
                        y - 8,
                        (WIDTH - 100 + w) // 2 + 20,
                        y + 48,
                    ),
                    radius=14,
                    fill=(0, 0, 0, 175),
                )

                txt_draw.text(
                    (
                        (WIDTH - 100 - w) // 2,
                        y,
                    ),
                    line,
                    font=txt_font,
                    fill=WHITE,
                )

                y += 68

            caption = ImageClip(
                np.array(txt_img),
                duration=duration,
            )

            caption = caption.with_position(("center", HEIGHT - 390))

            clip = CompositeVideoClip(
                [clip, caption],
                size=(WIDTH, HEIGHT),
            )

        clips.append(clip)

    print("🔗 Joining scenes...")

    final_video = concatenate_videoclips(
        clips,
        method="compose",
    )

    # -----------------------------------------------------------------
    # Voiceover
    # -----------------------------------------------------------------

    vo_lines = storyboard.get("vo_script_full", [])

    vo_text = " ".join(str(line) for line in vo_lines).strip()

    temp_dir = Path(tempfile.mkdtemp(prefix="crowdwisdom_video_"))

    voiceover_path = None

    if vo_text:
        print("🎙️ Generating local voiceover...")
        voiceover_path = generate_voiceover(
            vo_text,
            temp_dir / "voiceover.aiff",
        )

    if voiceover_path and voiceover_path.exists():
        print("🔊 Adding voiceover...")
        audio = AudioFileClip(str(voiceover_path))

        # Keep voiceover within the video duration.
        audio = audio.with_duration(
            min(audio.duration, final_video.duration)
        )

        final_video = final_video.with_audio(
            CompositeAudioClip([audio])
        )

    # -----------------------------------------------------------------
    # Render
    # -----------------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("🚀 Rendering final MP4...")
    print("   This may take a few minutes.")

    final_video.write_videofile(
        str(OUTPUT_VIDEO),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        preset="medium",
        threads=4,
        ffmpeg_params=[
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
        ],
    )

    final_video.close()

    for clip in clips:
        try:
            clip.close()
        except Exception:
            pass

    if voiceover_path:
        try:
            voiceover_path.unlink(missing_ok=True)
        except Exception:
            pass

    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    if not OUTPUT_VIDEO.exists():
        raise RuntimeError("Video render finished but output file was not created.")

    print()
    print("✅ VIDEO AGENT COMPLETED")
    print(f"📦 Final video: {OUTPUT_VIDEO}")
    print(f"📏 Size: {OUTPUT_VIDEO.stat().st_size / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    create_video()