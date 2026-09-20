#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "third_party" / "OpenMontage" / "projects" / "crowdwisdom-trading-ad"
STORYBOARD = ROOT / "data" / "storyboard.json"
SOURCE_VIDEO = ROOT / "data" / "final_ad.mp4"
TEMPLATE = ROOT / "templates" / "atelier.html"

VARIANTS = [
    {"name":"vertical", "cid":"crowdwisdom-ad-portrait", "width":1080, "height":1920},
    {"name":"landscape", "cid":"crowdwisdom-ad-landscape", "width":1920, "height":1080},
]

DESIGN = """# CrowdWisdom Trading — Atelier Art Direction

Visual language: signal vs noise. The opening is compressed, fragmented and red/green; the middle expands into a luminous crowd field; the product reveal becomes clean and precise; the ending warms into a calm single-signal CTA.

Palette: #060A12 ink, #101827 slate, #F5F7FA white, #9BA7B7 muted, #51E5FF cyan, #31E58B green, #FF5563 red, #F5C15F gold.

Typography: Inter bold display; JetBrains Mono utility text.

Motion: impact cards → slow push-in → crowd pull-back → product snap → warm resolution → network orbit → restrained CTA.

Composition mode: atelier. Runtime: hyperframes. Outputs are rendered as native 9:16 and 16:9 variants; the vertical master is not stretched/cropped into landscape.
"""

COORDS = [
    (7,18),(15,31),(24,14),(34,25),(45,10),(54,20),(64,15),(75,26),(86,12),(93,32),
    (11,48),(20,61),(31,45),(42,56),(53,43),(66,57),(77,46),(88,62),(95,50),
    (8,77),(18,88),(28,74),(39,91),(50,76),(60,87),(71,72),(82,90),(92,78),
    (14,39),(27,67),(38,36),(58,67),(73,35),(84,70)
]


def make_nodes() -> str:
    return "\n".join(f'<i class="node n{i}" style="left:{x}%;top:{y}%;"></i>' for i,(x,y) in enumerate(COORDS))


def make_lines() -> str:
    return "\n".join(f'<div class="network-line nl{i}" style="transform:rotate({i*11}deg);"></div>' for i in range(33))


def storyboard_md(sb: dict) -> str:
    out = [f"# {sb.get('title','CrowdWisdom Ad')}", "", f"Duration: {sb.get('total_duration_seconds',42)} seconds", "", f"Tagline: {sb.get('tagline','')}", "", "## Scenes", ""]
    for s in sb.get("scenes", []):
        out += [
            f"### Scene {s.get('scene_number')} — {s.get('purpose','')}",
            f"Time: {s.get('timestamp')}",
            f"Camera: {s.get('camera')}",
            f"Visual: {s.get('visual')}",
            f"VO: {s.get('voiceover')}",
            f"On-screen: {s.get('on_screen_text')}",
            "",
        ]
    return "\n".join(out)


def render_html(template: str, v: dict) -> str:
    return (template
        .replace("__WIDTH__", str(v["width"]))
        .replace("__HEIGHT__", str(v["height"]))
        .replace("__CID__", v["cid"])
        .replace("__FORMAT__", v["name"])
        .replace("__NODES__", make_nodes())
        .replace("__LINES__", make_lines())
    )


def main() -> None:
    if not STORYBOARD.is_file():
        raise SystemExit(f"Missing storyboard: {STORYBOARD}")
    if not TEMPLATE.is_file():
        raise SystemExit(f"Missing template: {TEMPLATE}")
    if not (ROOT / "third_party" / "OpenMontage").is_dir():
        raise SystemExit("OpenMontage submodule is missing")

    sb = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "artifacts").mkdir(exist_ok=True)
    (PROJECT_ROOT / "artifacts" / "storyboard.json").write_text(json.dumps(sb, indent=2, ensure_ascii=False), encoding="utf-8")
    (PROJECT_ROOT / "artifacts" / "DESIGN.md").write_text(DESIGN, encoding="utf-8")
    (PROJECT_ROOT / "artifacts" / "STORYBOARD.md").write_text(storyboard_md(sb), encoding="utf-8")

    template = TEMPLATE.read_text(encoding="utf-8")
    for v in VARIANTS:
        ws = PROJECT_ROOT / "hyperframes" / v["name"]
        (ws / "assets").mkdir(parents=True, exist_ok=True)
        (ws / "renders").mkdir(parents=True, exist_ok=True)
        (ws / "compositions").mkdir(parents=True, exist_ok=True)
        (ws / "DESIGN.md").write_text(DESIGN, encoding="utf-8")
        (ws / "STORYBOARD.md").write_text(storyboard_md(sb), encoding="utf-8")
        (ws / "hyperframes.json").write_text(json.dumps({
            "registry":"https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths":{"blocks":"compositions","components":"compositions/components","assets":"assets"}
        }, indent=2), encoding="utf-8")
        (ws / "index.html").write_text(render_html(template, v), encoding="utf-8")
        if SOURCE_VIDEO.is_file():
            subprocess.run([
                "ffmpeg","-y","-i",str(SOURCE_VIDEO),"-vn","-ac","1","-ar","48000",
                "-c:a","pcm_s16le",str(ws / "assets" / "narration.wav")
            ], check=True)
        print(f"Created {ws}")

if __name__ == "__main__":
    main()
