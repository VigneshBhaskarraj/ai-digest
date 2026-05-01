"""
summarize_tn.py
Uses Claude API to summarize Tamil Nadu innovation news into a structured
digest covering policies/incentives, startup sectors, research hubs, funding,
and opportunity mapping for the TN ecosystem.
"""

import os
import json
import anthropic
from typing import List, Dict

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are an expert analyst specializing in Tamil Nadu's innovation ecosystem —
startups, government policy, research institutions, and emerging technology sectors.

Your job is to read a list of news articles and produce a sharp, structured daily digest
for founders, policy makers, investors, and professionals tracking Tamil Nadu's innovation landscape.

You will be given a JSON list of articles with title, summary, source, category, and url.

Return ONLY valid JSON (no markdown, no extra text) in this exact structure:
{
  "headline": "One punchy sentence capturing the most important Tamil Nadu innovation development today",
  "policy_incentives": [
    {
      "title": "Policy or initiative title",
      "body": "2-3 sentences: what it is, who it targets, and why it matters for startups or innovators in TN",
      "url": "article url",
      "source": "source name",
      "impact_level": "high | medium | low"
    }
  ],
  "startup_spotlight": [
    {
      "name": "Startup or company name",
      "sector": "AI / HealthTech / AgriTech / EV / Semiconductor / EdTech / FinTech / SpaceTech / CleanTech / Manufacturing / Other",
      "what_it_does": "One sentence description",
      "stage": "Idea / Seed / Series A / Series B / Growth / Undisclosed",
      "funding": "Amount if mentioned, else 'Bootstrapped / Not disclosed'",
      "why_notable": "One sentence on what makes this startup significant for TN's ecosystem",
      "url": "article url",
      "source": "source name"
    }
  ],
  "research_innovation": [
    {
      "institution": "IIT Madras / Anna University / IITM Pravartak / Other",
      "title": "Research project or innovation title",
      "description": "2 sentences: what they're working on and its practical application",
      "url": "article url",
      "source": "source name"
    }
  ],
  "sector_opportunities": [
    {
      "sector": "Sector name (e.g., EV, Semiconductor, AI/ML, Defense Tech)",
      "opportunity": "2-3 sentences: what's happening in this sector in TN, why it's hot right now, and what founders or investors should know",
      "signals": ["signal1", "signal2"]
    }
  ],
  "ecosystem_pulse": "2-3 sentences summarizing the overall mood and momentum of the TN startup/innovation ecosystem today — what's gaining traction, what's the community excited about",
  "quick_hits": [
    {
      "title": "Brief headline",
      "source": "Source",
      "url": "url",
      "one_liner": "One sentence max"
    }
  ],
  "leaders_voices": [
    {
      "name": "Leader's full name",
      "role": "Their title / affiliation",
      "insight": "What they said, shared, or argued — paraphrased in 1-2 punchy sentences",
      "context": "One sentence on why this is noteworthy for TN's innovation ecosystem",
      "url": "source url or null"
    }
  ],
  "vike_note": "One sharp, opinionated sentence: what should a founder, innovator, or policy professional in Tamil Nadu pay attention to most from today's news?"
}

Rules:
- policy_incentives: include ALL significant government schemes, incentives, or policy changes relevant to TN startups/innovators
- startup_spotlight: include all TN-based startups mentioned, from any sector — even early-stage ones
- research_innovation: include notable research outputs from TN universities and research institutes (especially IIT Madras, Anna University, IITM Pravartak, NIT Trichy)
- sector_opportunities: 2-4 sectors max — synthesize cross-article signals, don't just repeat individual stories; focus on where there's momentum right now in TN
- quick_hits: 3-6 items that are noteworthy but don't warrant their own section
- ecosystem_pulse: capture the overall vibe — optimistic, cautious, rapidly growing, etc.
- leaders_voices: include statements from TN CM MK Stalin, Minister TR Baalu, TIDEL Park officials, StartupTN leadership, IITM faculty/directors, or any named TN innovation leader. 2-3 max. Return empty array if none found — never fabricate.
- If a section has no relevant data, return an empty array — never fabricate
- vike_note: actionable advice specifically for the TN context, not a generic summary
- Be direct and opinionated — no filler phrases like "it remains to be seen"

If articles are sparse or TN coverage is thin today, synthesize what IS available and note that coverage may improve with more regional sources."""


def summarize_tn_articles(articles: List[Dict]) -> Dict:
    """Send TN articles to Claude and get back a structured digest dict."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    payload = []
    for a in articles[:60]:
        payload.append({
            "title":    a["title"],
            "summary":  a["summary"][:400],
            "source":   a["source"],
            "url":      a["url"],
            "category": a["category"],
        })

    if not payload:
        return _empty_digest()

    user_message = f"""Here are today's Tamil Nadu innovation and technology news articles.
Today's date: {__import__('datetime').datetime.utcnow().strftime('%B %d, %Y')} (IST: +5:30 ahead of UTC)

Articles JSON:
{json.dumps(payload, indent=2)}

Produce the structured TN Innovation Digest JSON now. Focus on:
- Government policies and incentives for startups/innovators in Tamil Nadu
- New TN-based startups across any sector (AI, EV, HealthTech, AgriTech, Manufacturing, etc.)
- Research and innovation from IIT Madras, Anna University, IITM Pravartak, and other TN institutions
- Sector opportunities: where capital and talent are flowing in TN right now
- Notable statements from TN government officials, innovation leaders, or founders"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=5000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def _empty_digest() -> Dict:
    return {
        "headline": "No TN Innovation news found in this window — expanding search window recommended.",
        "policy_incentives": [],
        "startup_spotlight": [],
        "research_innovation": [],
        "sector_opportunities": [
            {
                "sector": "AI & Deep Tech",
                "opportunity": "IIT Madras and IITM Pravartak continue to be the anchor for Tamil Nadu's AI startup ecosystem. With 400+ startups incubated, this remains the strongest signal for early-stage founders seeking both research depth and institutional support.",
                "signals": ["IITM Pravartak pipeline", "AI-first incubation cohorts"]
            }
        ],
        "ecosystem_pulse": "Quiet news day for Tamil Nadu's innovation ecosystem. The underlying momentum — driven by IIT Madras's research output, StartupTN's programs, and Chennai's growing GCC presence — continues regardless of today's coverage.",
        "quick_hits": [],
        "leaders_voices": [],
        "vike_note": "Use quiet days to research StartupTN's current active schemes and upcoming application deadlines — timing your funding applications around government fiscal cycles is often more impactful than chasing deal flow.",
    }


if __name__ == "__main__":
    test_articles = [
        {
            "title": "Tamil Nadu launches Rs 500 Cr AI startup fund under TN Startup Mission",
            "summary": "The Tamil Nadu government announced a Rs 500 crore AI-focused startup fund under StartupTN to support early-stage founders building in healthcare, agriculture, and manufacturing AI.",
            "source": "The Hindu",
            "url": "https://thehindu.com",
            "category": "Policy & Incentives",
        },
        {
            "title": "IIT Madras spinoff raises Series A for satellite-based crop monitoring",
            "summary": "Chennai-based Krishitantra, an IIT Madras spinoff, has raised Rs 12 crore Series A to expand its AI-powered satellite crop monitoring platform across Tamil Nadu and AP.",
            "source": "YourStory",
            "url": "https://yourstory.com",
            "category": "Startup Funding",
        }
    ]
    result = summarize_tn_articles(test_articles)
    print(json.dumps(result, indent=2))
