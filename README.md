# CrowdWisdom Trading — Hermes AI Marketing Agents

A multi-agent AI marketing pipeline built with **Hermes Agent** for the CrowdWisdom Trading internship assessment.

The system researches competing trading advertisements, identifies audience pain points, creates a cinematic video-ad storyboard, and generates the final advertisement.

---

## Project Overview

```text
                    ┌─────────────────────┐
                    │   Hermes Kanban     │
                    │    Orchestrator     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │ Ads Manager  │  │ Script Agent │  │ Video Agent  │
      │    Agent     │  │              │  │              │
      └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
             │                 │                 │
             ▼                 ▼                 ▼
        Apify Ads         Tavily Research    Video Pipeline
             │                 │                 │
             ▼                 ▼                 ▼
      data/ads.json      storyboard.json    final_ad.mp4
```

### Workflow

1. **Ads Manager Agent**
   - Collects and analyzes trading advertisements.
   - Uses Apify for Meta Ads Library research.
   - Filters relevant advertisements from the recent research window.
   - Extracts hooks, pain points, marketing concepts, and competitive patterns.
   - Saves the structured analysis to `data/ads.json`.

2. **Script Agent**
   - Reads the Ads Manager output.
   - Uses Tavily for recent trading-market and audience research.
   - Identifies the ideal customer profile and key pain point.
   - Creates a 30–60 second cinematic advertising storyboard.
   - Saves the storyboard to `data/storyboard.json`.

3. **Video Agent**
   - Reads the approved storyboard.
   - Generates the cinematic scenes and compositions.
   - Adds captions, motion effects, and voiceover.
   - Uses MoviePy, Pillow, NumPy, and FFmpeg.
   - Produces the final advertisement at `data/final_ad.mp4`.

---

## Technologies

| Technology | Purpose |
|---|---|
| Python | Core development |
| Hermes Agent | Agent orchestration and Kanban workflow |
| OpenRouter | LLM provider |
| DeepSeek V4 Flash | LLM used by Hermes agents |
| Apify | Meta Ads Library data collection |
| Tavily | Recent web research |
| Pillow | Scene artwork and graphics |
| MoviePy | Video composition |
| NumPy | Image processing |
| imageio-ffmpeg | FFmpeg distribution |
| FFmpeg | Video encoding |
| macOS `say` | Local voiceover generation |
| Git / GitHub | Version control |

---

## Project Structure

```text
crowdwisdom-hermes/
│
├── agents/
│   ├── ads_manager.py
│   └── video_agent.py
│
├── data/
│   ├── raw_ads.json
│   ├── ads.json
│   ├── storyboard.json
│   └── final_ad.mp4
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Installation

## Requirements

- Python 3.11+
- Git
- Hermes Agent
- OpenRouter API key
- Apify API token
- Tavily API key

---

## 1. Clone the repository

```bash
git clone https://github.com/Ronitparmar13/crowdwisdom-hermes.git
cd crowdwisdom-hermes
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create the local environment file:

```bash
cp .env.example .env
```

Add your own credentials:

```env
OPENROUTER_API_KEY=your_openrouter_key
APIFY_API_TOKEN=your_apify_token
TAVILY_API_KEY=your_tavily_key

OPENROUTER_MODEL=deepseek/deepseek-v4-flash-0731
```

**Never commit `.env` to GitHub.**

---

# Hermes Configuration

Initialize the Hermes Kanban board:

```bash
hermes kanban init
```

Start the Hermes gateway:

```bash
hermes gateway start
```

Check the Kanban board:

```bash
hermes kanban list
```

The project uses separate Hermes profiles for the marketing workflow:

```text
default
script-agent2
video-agent
```

---

# Ads Manager Agent

The Ads Manager is responsible for competitor advertisement research and analysis.

## Input

```text
data/raw_ads.json
```

## Processing

The agent:

- Filters trading-related advertisements.
- Filters advertisements from the recent research window.
- Removes duplicate advertisements.
- Scores candidate advertisements.
- Sends selected candidates to the LLM.
- Extracts marketing insights and competitive patterns.

## Output

```text
data/ads.json
```

## Manual execution

```bash
python agents/ads_manager.py
```

## Example pipeline

```text
50 raw advertisements
        ↓
42 trading-relevant advertisements
        ↓
40 advertisements from the last 30 days
        ↓
40 unique advertisements
        ↓
12 selected candidates
        ↓
OpenRouter / DeepSeek analysis
        ↓
data/ads.json
```

---

# Script Agent

The Script Agent transforms the competitive research into a cinematic advertising concept.

## Input

```text
data/ads.json
```

## Research

Tavily is used to research:

- Retail trader pain points
- Trading audience behavior
- Recent market context
- Competitive positioning
- Relevant current information

## Output

```text
data/storyboard.json
```

The storyboard contains:

- Ideal Customer Profile
- Primary pain point
- Research evidence
- Creative concept
- Visual hook
- Scene structure
- Scene timing
- Camera direction
- Visual descriptions
- Voiceover
- On-screen text
- Sound design
- CTA
- Production notes

The current storyboard defines a **42-second vertical cinematic advertisement**.

---

# Video Agent

The Video Agent converts the approved storyboard into the final advertisement.

## Input

```text
data/storyboard.json
```

## Processing Pipeline

```text
Storyboard
    ↓
Scene generation
    ↓
Cinematic graphics
    ↓
Market-chart visualizations
    ↓
Camera motion / zoom
    ↓
On-screen captions
    ↓
Voiceover
    ↓
Video composition
    ↓
FFmpeg encoding
    ↓
data/final_ad.mp4
```

## Manual execution

```bash
python agents/video_agent.py
```

## Final video specification

```text
Duration:   42 seconds
Resolution: 1080 × 1920
Aspect:     9:16
Codec:      H.264
Frame rate: 24 FPS
Format:     MP4
```

---

# Hermes Kanban Workflow

The three stages are coordinated using Hermes Kanban:

```text
┌─────────────────────────────────────┐
│ Ads Manager Agent                   │
│ Assignee: default                   │
└────────────────┬────────────────────┘
                 │
                 ▼
          data/ads.json
                 │
                 ▼
┌─────────────────────────────────────┐
│ Script Agent                        │
│ Assignee: script-agent2             │
└────────────────┬────────────────────┘
                 │
                 ▼
       data/storyboard.json
                 │
                 ▼
┌─────────────────────────────────────┐
│ Video Agent                         │
│ Assignee: video-agent               │
└────────────────┬────────────────────┘
                 │
                 ▼
        data/final_ad.mp4
```

Check task status:

```bash
hermes kanban list
```

A completed workflow should show the three tasks as `done`.

---

# Validation

## Validate Ads Manager JSON

```bash
python -m json.tool data/ads.json > /dev/null && echo "ads.json valid"
```

## Validate Storyboard JSON

```bash
python -m json.tool data/storyboard.json > /dev/null && echo "storyboard.json valid"
```

## Check final video

```bash
ls -lh data/final_ad.mp4
```

## Check video metadata

```bash
"$(python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" \
-i data/final_ad.mp4 2>&1 | grep -E "Duration|Video:"
```

---

# Data Sources

## Apify / Meta Ads Library

The Ads Manager uses an Apify Meta Ads Library scraper to collect competitor advertisements.

The dataset contains fields such as:

- Advertisement ID
- Page name
- Advertisement copy
- Headline
- Call-to-action
- Landing URL
- Media URLs
- Impression information
- Active status
- Start/end dates
- Search query
- Country

## Tavily

Tavily is used by the Script Agent to research recent:

- Trading audience behavior
- Retail trader pain points
- Market sentiment
- Competitive trends
- Current market context

---

# Creative Concept

The current advertisement is titled:

## "Who's Right?"

### Tagline

> Every expert disagrees. The crowd already knows.

The advertisement begins with contradictory market opinions:

```text
BUY
SELL
CRASH IMMINENT
TO THE MOON
```

The story then moves from information overload to a CrowdWisdom-focused solution.

### Creative Arc

```text
Expert conflict
      ↓
Information overload
      ↓
Decision paralysis
      ↓
Wisdom of the crowd
      ↓
CrowdWisdom consensus
      ↓
Clearer decision
      ↓
Free weekly briefing CTA
```

---

# Video Scenes

The current 42-second advertisement contains seven scenes:

```text
Scene 1 — Contradictory market opinions
Scene 2 — Retail trader information overload
Scene 3 — The market as a crowd
Scene 4 — CrowdWisdom product reveal
Scene 5 — From research to one decision
Scene 6 — Collective signal / crowd visualization
Scene 7 — Final CTA and brand card
```

---

# Security

API credentials are kept outside the repository.

Required environment variables:

```env
OPENROUTER_API_KEY=
APIFY_API_TOKEN=
TAVILY_API_KEY=
EXA_API_KEY=
OPENROUTER_MODEL=
```

The `.env` file is intentionally excluded from Git.

Use `.env.example` as the configuration template.

---

# Reproducing the Workflow

Activate the environment:

```bash
source .venv/bin/activate
```

Run the Ads Manager:

```bash
python agents/ads_manager.py
```

Run the Script Agent through Hermes Kanban.

Run the Video Agent:

```bash
python agents/video_agent.py
```

Or use Hermes Kanban to orchestrate the complete agent workflow:

```bash
hermes kanban init
hermes gateway start
hermes kanban list
```

---

# Final Deliverables

| Deliverable | Location |
|---|---|
| Raw advertisement dataset | `data/raw_ads.json` |
| Ads Manager analysis | `data/ads.json` |
| Cinematic storyboard | `data/storyboard.json` |
| Video Agent implementation | `agents/video_agent.py` |
| Final advertisement | `data/final_ad.mp4` |

---

# Assessment Alignment

This project implements the requested three-stage marketing workflow:

```text
Ads Manager Agent
       ↓
Script Agent
       ↓
Video Agent
```

The pipeline combines:

- **Apify** for competitor advertisement research
- **Tavily** for recent trading and audience research
- **Hermes Agent** for agent orchestration
- **OpenRouter / DeepSeek** for language-model reasoning
- **Python + Pillow + MoviePy + FFmpeg** for final video production

The final advertisement is a **42-second vertical cinematic video** designed for social-media formats.

---

# Author

**Ronit Parmar**

GitHub:  
https://github.com/Ronitparmar13

Repository:  
https://github.com/Ronitparmar13/crowdwisdom-hermes

---

# License

This project was created as part of an internship assessment for CrowdWisdom Trading.
