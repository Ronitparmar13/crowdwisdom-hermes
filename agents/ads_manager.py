import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RAW_FILE = DATA_DIR / "raw_ads.json"
OUTPUT_FILE = DATA_DIR / "ads.json"

load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-v4-flash-0731",
)

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing from .env"
    )


# =========================================================
# OPENROUTER CLIENT
# =========================================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


# =========================================================
# LOAD ADS
# =========================================================

def load_ads():
    """Load raw Apify ads from JSON."""

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}"
        )

    with RAW_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# =========================================================
# TRADING RELEVANCE
# =========================================================

TRADING_KEYWORDS = [
    "forex",
    "trading",
    "trader",
    "stock",
    "stocks",
    "options",
    "crypto",
    "signals",
    "market",
    "chart",
    "technical analysis",
    "prop trading",
    "day trading",
    "swing trading",
]


def is_trading_relevant(ad):
    """Check whether an ad is related to trading."""

    text = " ".join(
        [
            str(ad.get("pageName", "")),
            str(ad.get("adCopy", "")),
            str(ad.get("headline", "")),
            str(ad.get("linkDescription", "")),
            str(ad.get("caption", "")),
        ]
    ).lower()

    return any(
        keyword in text
        for keyword in TRADING_KEYWORDS
    )


# =========================================================
# LAST 30 DAYS
# =========================================================

def is_within_last_30_days(ad):
    """Return True if the ad started within the last 30 days."""

    date_value = ad.get("startDate")

    if not date_value:
        return False

    try:
        ad_date = datetime.fromisoformat(
            date_value.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)

        cutoff = now - timedelta(days=30)

        return ad_date >= cutoff

    except (ValueError, TypeError):
        return False


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    """Normalize text for duplicate detection."""

    text = text or ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# DEDUPLICATION
# =========================================================

def deduplicate_ads(ads):
    """Remove duplicate advertisements."""

    seen = set()

    unique_ads = []

    for ad in ads:

        archive_id = ad.get(
            "adArchiveId"
        )

        if archive_id:

            key = f"id:{archive_id}"

        else:

            key = (
                normalize_text(
                    ad.get("pageName")
                )
                + "|"
                + normalize_text(
                    ad.get("adCopy")
                )
            )

        if key in seen:
            continue

        seen.add(key)

        unique_ads.append(ad)

    return unique_ads


# =========================================================
# CANDIDATE SCORING
# =========================================================

def candidate_score(ad):
    """
    Create a lightweight candidate score.

    This is only a heuristic for selecting candidates.
    It is NOT proof of ad performance or conversions.
    """

    score = 0.0

    text = " ".join(
        [
            str(ad.get("pageName", "")),
            str(ad.get("adCopy", "")),
            str(ad.get("headline", "")),
        ]
    ).lower()

    # Trading relevance
    for keyword in TRADING_KEYWORDS:

        if keyword in text:
            score += 2

    # Video ads are useful for our eventual
    # video-ad generation task.
    if ad.get("displayFormat") == "VIDEO":

        score += 4

    # Days running = weak signal
    days_running = ad.get(
        "runDurationDays"
    )

    if isinstance(
        days_running,
        (int, float)
    ):

        score += min(
            days_running,
            30
        ) * 0.5

    # Page likes = weak social-proof signal
    page_likes = ad.get(
        "pageLikeCount"
    )

    if isinstance(
        page_likes,
        (int, float)
    ):

        score += min(
            page_likes / 10000,
            5
        )

    # Impression index when available
    impressions_index = ad.get(
        "impressionsIndex"
    )

    if isinstance(
        impressions_index,
        (int, float)
    ):

        score += impressions_index * 2

    # CTA exists
    if ad.get("ctaType"):

        score += 1

    # Actual creative exists
    if ad.get("videoUrls"):

        score += 3

    elif ad.get("imageUrls"):

        score += 2

    return round(
        score,
        2
    )


# =========================================================
# PREPARE LLM INPUT
# =========================================================

def prepare_for_llm(ads):
    """
    Create a compact representation of ads
    for the LLM.
    """

    prepared = []

    for index, ad in enumerate(
        ads,
        start=1
    ):

        prepared.append(
            {
                "candidate": index,
                "page_name": ad.get(
                    "pageName"
                ),
                "ad_copy": ad.get(
                    "adCopy"
                ),
                "headline": ad.get(
                    "headline"
                ),
                "cta": ad.get(
                    "ctaText"
                ),
                "cta_type": ad.get(
                    "ctaType"
                ),
                "format": ad.get(
                    "displayFormat"
                ),
                "days_running": ad.get(
                    "runDurationDays"
                ),
                "page_likes": ad.get(
                    "pageLikeCount"
                ),
                "impressions": ad.get(
                    "impressionsText"
                ),
                "landing_url": ad.get(
                    "landingUrl"
                ),
                "search_query": ad.get(
                    "searchQuery"
                ),
                "platforms": ad.get(
                    "platforms"
                ),
            }
        )

    return prepared


# =========================================================
# LLM ANALYSIS
# =========================================================

def analyze_ads(ads):
    """
    Analyze ads in small batches.

    Improvements:
    - Batch size = 2
    - Structured JSON output
    - Retry up to 3 times
    - No streaming
    - Handles malformed/empty responses
    """

    BATCH_SIZE = 2

    all_ranked_ads = []

    cross_ad_insights = {
        "common_pains": [],
        "common_hooks": [],
        "common_marketing_angles": [],
        "creative_patterns": [],
        "opportunities_for_crowdwisdom": [],
    }

    # -----------------------------------------------------
    # Process batches
    # -----------------------------------------------------

    for batch_start in range(
        0,
        len(ads),
        BATCH_SIZE
    ):

        batch = ads[
            batch_start:
            batch_start + BATCH_SIZE
        ]

        batch_end = (
            batch_start +
            len(batch)
        )

        print(
            f"🧠 Analyzing ads "
            f"{batch_start + 1}-{batch_end} "
            f"of {len(ads)}..."
        )

        candidates = prepare_for_llm(
            batch
        )

        # -------------------------------------------------
        # Prompt
        # -------------------------------------------------

        prompt = f"""
You are the Ads Manager Agent for
CrowdWisdomTrading.

Analyze these competitor trading ads.

For EACH advertisement identify:

1. hook
2. pain_point
3. target_audience
4. marketing_angle
5. creative_concept
6. CTA
7. why_effective
8. weakness

Also identify useful patterns across this batch.

IMPORTANT RULES:

- Do not claim an advertisement is proven successful
  unless the supplied data supports that.
- Impressions, reach, spend, page likes and days running
  are signals, not proof of conversions.
- Focus on insights useful for creating a
  CrowdWisdomTrading video advertisement.
- Do not copy competitor wording.
- Describe the marketing technique instead.
- Return ONLY valid JSON.
- Do not use markdown.
- Keep every value concise.
- Do not repeat the full ad copy.

Return exactly this structure:

{{
  "ranked_ads": [
    {{
      "candidate": 1,
      "hook": "...",
      "pain_point": "...",
      "target_audience": "...",
      "marketing_angle": "...",
      "creative_concept": "...",
      "cta": "...",
      "why_effective": "...",
      "weakness": "..."
    }}
  ],
  "cross_ad_insights": {{
    "common_pains": [],
    "common_hooks": [],
    "common_marketing_angles": [],
    "creative_patterns": [],
    "opportunities_for_crowdwisdom": []
  }}
}}

ADS:

{json.dumps(
    candidates,
    ensure_ascii=False,
    indent=2
)}
"""

        # -------------------------------------------------
        # Retry mechanism
        # -------------------------------------------------

        batch_result = None

        for attempt in range(
            1,
            4
        ):

            try:

                print(
                    f"   ↻ LLM attempt "
                    f"{attempt}/3..."
                )

                response = (
                    client.chat.completions.create(
                        model=OPENROUTER_MODEL,

                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a senior "
                                    "performance marketing "
                                    "analyst specializing "
                                    "in trading audiences."
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],

                        temperature=0.3,

                        max_tokens=6000,

                        response_format={
                            "type": "json_object"
                        },

                        timeout=90,
                    )
                )

                # -----------------------------------------
                # Extract response
                # -----------------------------------------

                content = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                if not content:

                    print(
                        f"   ⚠️ Empty response "
                        f"on attempt {attempt}"
                    )

                    if attempt < 3:
                        continue

                    break

                content = content.strip()

                # -----------------------------------------
                # Remove accidental code fences
                # -----------------------------------------

                if content.startswith(
                    "```"
                ):

                    content = re.sub(
                        r"^```(?:json)?\s*",
                        "",
                        content,
                    )

                    content = re.sub(
                        r"\s*```$",
                        "",
                        content,
                    )

                    content = content.strip()

                # -----------------------------------------
                # Parse JSON
                # -----------------------------------------

                batch_result = json.loads(
                    content
                )

                print(
                    "   ✅ LLM response received"
                )

                break

            except json.JSONDecodeError as e:

                print(
                    f"   ⚠️ Invalid JSON "
                    f"on attempt {attempt}: "
                    f"{e}"
                )

                if attempt == 3:

                    print(
                        "   ❌ JSON parsing failed "
                        "after 3 attempts"
                    )

            except Exception as e:

                print(
                    f"   ⚠️ LLM error "
                    f"on attempt {attempt}: "
                    f"{type(e).__name__}: {e}"
                )

                if attempt == 3:

                    print(
                        "   ❌ LLM request failed "
                        "after 3 attempts"
                    )

        # -------------------------------------------------
        # Handle failed batch
        # -------------------------------------------------

        if batch_result is None:

            print(
                f"⚠️ Skipping batch "
                f"{batch_start + 1}-{batch_end}"
            )

            continue

        # -------------------------------------------------
        # Store ranked ads
        # -------------------------------------------------

        ranked_ads = batch_result.get(
            "ranked_ads",
            []
        )

        if isinstance(
            ranked_ads,
            list
        ):

            all_ranked_ads.extend(
                ranked_ads
            )

        # -------------------------------------------------
        # Merge cross-ad insights
        # -------------------------------------------------

        batch_insights = batch_result.get(
            "cross_ad_insights",
            {}
        )

        if not isinstance(
            batch_insights,
            dict
        ):

            batch_insights = {}

        for key in cross_ad_insights:

            values = batch_insights.get(
                key,
                []
            )

            if isinstance(
                values,
                list
            ):

                cross_ad_insights[
                    key
                ].extend(values)

    # =====================================================
    # REMOVE DUPLICATE INSIGHTS
    # =====================================================

    for key in cross_ad_insights:

        cross_ad_insights[key] = list(
            dict.fromkeys(
                cross_ad_insights[key]
            )
        )

    # =====================================================
    # GLOBAL RANKING
    # =====================================================

    for rank, item in enumerate(
        all_ranked_ads,
        start=1
    ):

        if isinstance(
            item,
            dict
        ):

            item["rank"] = rank

    # =====================================================
    # RETURN
    # =====================================================

    return {
        "ranked_ads": all_ranked_ads,
        "cross_ad_insights": cross_ad_insights,
    }


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    print(
        "🚀 Ads Manager Agent starting..."
    )

    # -----------------------------------------------------
    # Load raw dataset
    # -----------------------------------------------------

    raw_ads = load_ads()

    print(
        f"📥 Raw ads loaded: "
        f"{len(raw_ads)}"
    )

    # -----------------------------------------------------
    # Trading relevance filter
    # -----------------------------------------------------

    relevant_ads = [
        ad
        for ad in raw_ads
        if is_trading_relevant(ad)
    ]

    print(
        f"🎯 Trading-relevant ads: "
        f"{len(relevant_ads)}"
    )

    # -----------------------------------------------------
    # Last 30 days
    # -----------------------------------------------------

    recent_ads = [
        ad
        for ad in relevant_ads
        if is_within_last_30_days(ad)
    ]

    print(
        f"📅 Ads from last 30 days: "
        f"{len(recent_ads)}"
    )

    # -----------------------------------------------------
    # Deduplicate
    # -----------------------------------------------------

    unique_ads = deduplicate_ads(
        recent_ads
    )

    print(
        f"♻️ Unique ads: "
        f"{len(unique_ads)}"
    )

    # -----------------------------------------------------
    # Candidate scoring
    # -----------------------------------------------------

    for ad in unique_ads:

        ad["_candidate_score"] = (
            candidate_score(ad)
        )

    unique_ads.sort(
        key=lambda ad: ad[
            "_candidate_score"
        ],
        reverse=True,
    )

    # -----------------------------------------------------
    # Select top candidates
    # -----------------------------------------------------

    selected_ads = unique_ads[:12]

    print(
        f"🧠 Sending "
        f"{len(selected_ads)} "
        f"candidates to the LLM..."
    )

    # -----------------------------------------------------
    # LLM analysis
    # -----------------------------------------------------

    analysis = analyze_ads(
        selected_ads
    )

    # -----------------------------------------------------
    # Final output
    # -----------------------------------------------------

    output = {
        "metadata": {
            "generated_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "source": (
                "Apify Meta Ad Library"
            ),
            "candidate_count": (
                len(selected_ads)
            ),
            "filter": (
                "trading relevance "
                "+ last 30 days"
            ),
            "model": (
                OPENROUTER_MODEL
            ),
        },

        "source_ads": selected_ads,

        "analysis": analysis,
    }

    # -----------------------------------------------------
    # Ensure data directory exists
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save JSON
    # -----------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"✅ Analysis saved to: "
        f"{OUTPUT_FILE}"
    )

    print(
        "🎉 Ads Manager Agent completed."
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()