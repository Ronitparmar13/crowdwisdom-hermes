
# CrowdWisdom Trading — Hermes AI Marketing Agent Team

A multi-agent AI marketing pipeline built for the CrowdWisdom Trading internship assessment. It combines competitor-ad research, audience research, creative scripting, and video production.

**Final creative:** “Who’s Right?” — a 42-second advertisement delivered in vertical (9:16) and landscape (16:9) formats.

> The final advertisement uses an Atelier-style motion-graphics composition rendered with OpenMontage + HyperFrames. It is not presented as AI-generated live-action footage.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Creative Concept](#creative-concept)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Hermes Setup](#hermes-setup)
- [Ads Manager Agent](#ads-manager-agent)
- [Script Agent](#script-agent)
- [OpenMontage and HyperFrames Video Pipeline](#openmontage-and-hyperframes-video-pipeline)
- [Validation](#validation)
- [Final Deliverables](#final-deliverables)
- [Assessment Alignment](#assessment-alignment)
- [Security](#security)
- [Author](#author)

---

## Overview

This project implements a three-stage marketing workflow using Hermes Agent.

```text
                 Hermes Agent / Kanban
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     Ads Manager     Script Agent   Video Pipeline
          |              |              |
        Apify          Tavily       OpenMontage
          |              |          + HyperFrames
          v              v              v
   data/ads.json  data/storyboard.json  output/*.mp4
```

### 1. Ads Manager Agent

The Ads Manager researches competitor advertisements and extracts marketing insights.

- Collects Meta Ads Library data through Apify.
- Filters advertisements for trading relevance.
- Filters the research set to the recent 30-day window.
- Removes duplicate advertisements.
- Selects candidate advertisements for analysis.
- Uses an LLM to extract hooks, pain points, target audiences, marketing angles, creative concepts, CTAs, and observed weaknesses.
- Stores raw records in `data/raw_ads.json`.
- Saves structured analysis in `data/ads.json`.

The candidate selection is based on available Ads Library signals. It should not be interpreted as verified conversion, revenue, or profitability data.

### 2. Script Agent

The Script Agent transforms research into an advertising concept.

- Uses `data/ads.json` as competitive context.
- Uses Tavily for recent trading-market and audience research.
- Identifies the target audience, customer pain point, and creative angle.
- Develops the scene sequence, voiceover, on-screen copy, CTA, and production notes.
- Saves the structured storyboard to `data/storyboard.json`.

### 3. Video Pipeline

The final production stage uses OpenMontage with HyperFrames.

- Builds separate native vertical and landscape compositions.
- Uses an Atelier-style HTML composition.
- Adds animated typography, transitions, graphics, and narration.
- Checks and previews the compositions using HyperFrames.
- Renders the final MP4 files.
- Uses FFmpeg for media processing and encoding.

The final renders are stored in the repository's `output/` directory.

> `agents/video_agent.py` is retained as the earlier procedural video-agent implementation/prototype. The final assessment videos listed in this README were rendered through OpenMontage + HyperFrames.

---

## Architecture

```text
                         +----------------------+
                         |     Hermes Agent     |
                         |  Kanban / Profiles   |
                         +----------+-----------+
                                    |
              +---------------------+---------------------+
              |                     |                     |
              v                     v                     v
      +---------------+     +---------------+     +----------------+
      | Ads Manager   |     | Script Agent  |     | Video Pipeline |
      | Agent         |     |               |     |                |
      +-------+-------+     +-------+-------+     +-------+--------+
              |                     |                     |
              v                     v                     v
            Apify                 Tavily          OpenMontage /
              |                     |               HyperFrames
              v                     v                     |
       data/ads.json       data/storyboard.json            v
                                                   output/*.mp4
```

---

## Creative Concept

# “Who’s Right?”

**Tagline:** “Every expert disagrees. The crowd already knows.”

The advertisement begins with conflicting trading opinions and information overload. It then transitions into a visual representation of crowd sentiment, a CrowdWisdom product reveal, and a final call to action.

### Creative Arc

```text
Conflicting opinions
        |
        v
Information overload
        |
        v
Decision paralysis
        |
        v
Wisdom of the crowd
        |
        v
CrowdWisdom product reveal
        |
        v
Decision clarity
        |
        v
Final CTA
```

### Seven-Scene Structure

| Scene | Purpose |
|---|---|
| 1 | Contradictory market opinions |
| 2 | Retail-trader information overload |
| 3 | Crowd and sentiment visualization |
| 4 | CrowdWisdom product reveal |
| 5 | Resolution and decision clarity |
| 6 | Collective signal / network visualization |
| 7 | Final brand CTA and risk disclaimer |

Trading and performance-related figures shown in the creative should be independently checked against current, approved company sources before reuse in a live campaign. The video includes a trading-risk disclaimer and is not investment advice.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core scripts and build helper |
| Hermes Agent | Multi-agent orchestration and Kanban workflow |
| OpenRouter | LLM gateway |
| DeepSeek V4 Flash | LLM used during development |
| Apify | Meta Ads Library data collection |
| Tavily | Recent market and audience research |
| OpenMontage | Video composition framework |
| HyperFrames | HTML composition checking, preview, and rendering |
| FFmpeg / FFprobe | Media processing, encoding, and verification |
| Git / GitHub | Version control and project hosting |

---

## Repository Structure

```text
crowdwisdom-hermes/
|
+-- agents/
|   +-- ads_manager.py
|   +-- video_agent.py
|
+-- data/
|   +-- raw_ads.json
|   +-- ads.json
|   +-- storyboard.json
|   +-- final_ad.mp4
|
+-- output/
|   +-- crowdwisdom-trading-landscape.mp4
|   +-- crowdwisdom-trading-vertical.mp4
|
+-- scripts/
|   +-- build_openmontage_atelier.py
|
+-- templates/
|   +-- atelier.html
|
+-- third_party/
|   +-- OpenMontage/              # Git submodule
|
+-- .env.example
+-- .gitignore
+-- .gitmodules
+-- README.md
+-- requirements.txt
```

---

## Installation

### Requirements

- Python 3.11+
- Node.js 22+
- FFmpeg
- Git
- Hermes Agent
- OpenRouter API key
- Apify API token
- Tavily API key

OpenMontage is included as a Git submodule.

### 1. Clone the repository

Clone with submodules so the OpenMontage dependency is available:

```bash
git clone --recurse-submodules https://github.com/Ronitparmar13/crowdwisdom-hermes.git
cd crowdwisdom-hermes
```

If the repository was already cloned without submodules:

```bash
git submodule update --init --recursive
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Add your own credentials to `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
APIFY_API_TOKEN=your_apify_api_token
TAVILY_API_KEY=your_tavily_api_key
EXA_API_KEY=your_exa_api_key
OPENROUTER_MODEL=deepseek/deepseek-v4-flash-0731
```

**Never commit `.env` or real API credentials to GitHub.**

---

## Hermes Setup

Initialize the Kanban board:

```bash
hermes kanban init
```

Start the Hermes gateway:

```bash
hermes gateway start
```

Inspect tasks:

```bash
hermes kanban list
```

Profiles used during development included:

```text
default
script-agent2
video-agent
```

The agent workflow coordinates the research, scripting, and video-production stages.

---

## Ads Manager Agent

### Input

Meta Ads Library data collected through Apify.

### Outputs

```text
data/raw_ads.json
data/ads.json
```

### Processing Pipeline

```text
Collect advertisements
        |
        v
Filter trading relevance
        |
        v
Filter recent research window
        |
        v
Remove duplicates
        |
        v
Select candidate ads
        |
        v
LLM analysis
        |
        v
Structured marketing insights
```

### Research Set

The working research pipeline produced the following set:

```text
50 raw advertisements
        |
        v
42 trading-relevant advertisements
        |
        v
40 advertisements from the last 30 days
        |
        v
40 unique advertisements
        |
        v
12 selected candidates
        |
        v
OpenRouter / DeepSeek analysis
        |
        v
data/ads.json
```

These counts describe the collected working dataset, not independently verified ad performance.

### Manual Execution

```bash
python agents/ads_manager.py
```

---

## Script Agent

### Input

```text
data/ads.json
```

### Research

Tavily is used to research:

- Retail-trader pain points
- Trading audience behavior
- Recent market context
- Competitive positioning
- Relevant current information

### Output

```text
data/storyboard.json
```

The storyboard includes:

- Target audience / ICP
- Primary pain point
- Research evidence
- Creative concept
- Visual hook
- Scene structure and timing
- Camera direction
- Visual descriptions
- Voiceover
- On-screen text
- Sound design
- CTA
- Production notes
- Risk/disclaimer notes

The current production storyboard defines a **42-second advertisement**.

---

## OpenMontage and HyperFrames Video Pipeline

The final production stage uses OpenMontage as a submodule and HyperFrames for HTML-based composition and rendering.

### Build the production workspaces

Run from the repository root:

```bash
python scripts/build_openmontage_atelier.py
```

The builder creates the local project under:

```text
third_party/OpenMontage/projects/crowdwisdom-trading-ad/
```

It generates two separate HyperFrames workspaces:

```text
hyperframes/
+-- vertical/
|   +-- index.html
|   +-- hyperframes.json
|   +-- DESIGN.md
|   +-- STORYBOARD.md
|   +-- assets/
|   +-- renders/
|
+-- landscape/
    +-- index.html
    +-- hyperframes.json
    +-- DESIGN.md
    +-- STORYBOARD.md
    +-- assets/
    +-- renders/
```

The builder copies storyboard/design artifacts and writes each composition from `templates/atelier.html`.

When `data/final_ad.mp4` is present, the builder extracts its narration track into each workspace as `assets/narration.wav`.

### Prepare OpenMontage

```bash
cd third_party/OpenMontage
make setup
cd ../..
```

This prepares the OpenMontage / HyperFrames environment.

HyperFrames requires Node.js 22+ and FFmpeg.

---

## Validate the Compositions

### Vertical composition

```bash
cd third_party/OpenMontage/projects/crowdwisdom-trading-ad/hyperframes/vertical
npx hyperframes check
```

### Landscape composition

```bash
cd ../landscape
npx hyperframes check
```

The completed assessment compositions passed the HyperFrames layout, motion, and contrast checks. The checks reported non-blocking lint warnings about composition file size.

---

## Preview Before Rendering

HyperFrames Studio can be used to visually inspect the timeline:

```bash
npx hyperframes preview
```

Review the composition before performing a delivery render.

---

## Render the Final Videos

### Vertical 9:16

From the vertical workspace:

```bash
npx hyperframes render --quality high --strict --output renders/crowdwisdom-trading-vertical.mp4
```

### Landscape 16:9

From the landscape workspace:

```bash
npx hyperframes render --quality high --strict --output renders/crowdwisdom-trading-landscape.mp4
```

Copy the rendered files into the repository's `output/` directory.

From the vertical workspace:

```bash
cp renders/crowdwisdom-trading-vertical.mp4 ../../../../../output/
```

From the landscape workspace:

```bash
cp renders/crowdwisdom-trading-landscape.mp4 ../../../../../output/
```

If you render from another working directory, adjust the destination path accordingly.

---

## Final Render Specifications

| Output | Resolution | Aspect Ratio | Duration | Frame Rate | Video / Audio |
|---|---:|---:|---:|---:|---|
| Vertical | 1080 × 1920 | 9:16 | 42 sec | 30 FPS | H.264 / AAC |
| Landscape | 1920 × 1080 | 16:9 | 42 sec | 30 FPS | H.264 / AAC |

Both deliverables are MP4 files.

---

## Validate Data and Video

### Validate JSON files

```bash
python -m json.tool data/ads.json > /dev/null && echo "ads.json valid"
python -m json.tool data/storyboard.json > /dev/null && echo "storyboard.json valid"
```

### Check that final videos exist

```bash
ls -lh output/crowdwisdom-trading-vertical.mp4
ls -lh output/crowdwisdom-trading-landscape.mp4
```

### Check video metadata

```bash
ffprobe -v error \
  -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,r_frame_rate,codec_type \
  -of default=noprint_wrappers=1 \
  output/crowdwisdom-trading-vertical.mp4
```

Repeat with the landscape filename to inspect that render.

---

## Data Sources

### Apify / Meta Ads Library

Apify is used to collect competitor advertisement data.

The research dataset contains fields including:

- Advertisement identifiers
- Page information
- Ad copy
- Headlines
- CTA information
- Landing URLs
- Media URLs
- Impression information
- Active status
- Start/end dates
- Search query
- Country

Stored outputs:

```text
data/raw_ads.json
data/ads.json
```

### Tavily

Tavily is used by the Script Agent for recent research involving:

- Trading audience behavior
- Retail-trader pain points
- Market sentiment and context
- Competitive trends
- Creative positioning

---

## Hermes Kanban Workflow

The three stages are coordinated through Hermes Kanban:

```text
Ads Manager Agent
        |
        v
   data/ads.json
        |
        v
Script Agent
        |
        v
data/storyboard.json
        |
        v
Video Production
        |
        v
     output/
```

Inspect task status:

```bash
hermes kanban list
```

---

## Assessment Alignment

| Assessment requirement | Implementation |
|---|---|
| Hermes agent team | Hermes Kanban and agent profiles |
| Ads Manager | `agents/ads_manager.py` and Apify research |
| Recent competitor-ad research | Meta Ads Library dataset and recent-window filtering |
| Marketing/pain/concept extraction | `data/ads.json` |
| Script Agent | Hermes Script Agent and Tavily research |
| ICP and pain-point research | Tavily-backed research workflow |
| Human-readable storyboard | `data/storyboard.json` |
| 30–60 second advertisement | 42-second creative |
| Video production | OpenMontage + HyperFrames |
| Final delivery | Native vertical and landscape MP4 outputs |

---

## Final Deliverables

| Deliverable | Repository location |
|---|---|
| Raw competitor-ad research | `data/raw_ads.json` |
| Ads Manager analysis | `data/ads.json` |
| Script/storyboard | `data/storyboard.json` |
| Earlier procedural video-agent prototype | `agents/video_agent.py` |
| OpenMontage build helper | `scripts/build_openmontage_atelier.py` |
| Atelier HTML template | `templates/atelier.html` |
| Vertical final advertisement | `output/crowdwisdom-trading-vertical.mp4` |
| Landscape final advertisement | `output/crowdwisdom-trading-landscape.mp4` |
| OpenMontage dependency | `third_party/OpenMontage` |

---

## Quick Start for Reviewers

Clone the repository and its submodule:

```bash
git clone --recurse-submodules https://github.com/Ronitparmar13/crowdwisdom-hermes.git
cd crowdwisdom-hermes
```

Set up Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure credentials:

```bash
cp .env.example .env
```

Build the local OpenMontage workspaces:

```bash
python scripts/build_openmontage_atelier.py
```

The already-rendered assessment videos are available in:

```text
output/
```

---

## Security

- Keep real credentials in the local `.env` file only.
- Use `.env.example` as a placeholder template.
- Do not paste API keys into source files, README, issues, or commits.
- If a credential is exposed, revoke or rotate it with its provider.
- Do not commit private environment files.

---

## Author

**Ronit Parmar**

GitHub:  
https://github.com/Ronitparmar13

Repository:  
https://github.com/Ronitparmar13/crowdwisdom-hermes

---

## Internship Assessment

Prepared for the **CrowdWisdom Trading Hermes AI Marketing Agent assessment**.

This repository contains the research artifacts, storyboard, build helper and template, OpenMontage submodule reference, and final rendered video outputs.
