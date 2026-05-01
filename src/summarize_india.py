"""
summarize_india.py
Uses Claude API to summarize India AI investment & startup news into a
structured digest focused on VC funding, new startups, policy, and trends.
"""

import os
import json
import anthropic
from typing import List, Dict

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are an expert analyst covering India's AI startup and venture capital ecosystem.
Your job is to read a list of news articles and produce a sharp, structured daily digest
for founders, VCs, and AI professionals tracking India's AI investment landscape.

You will be given a JSON list of articles with title, summary, source, category, and url.

Return ONLY valid JSON (no markdown, no extra text) in this exact structure:
{
  "headline": "One punchy sentence capturing the most important India AI investment or startup development today",
  "funding_rounds": [
    {
      "startup": "Startup name",
      "amount": "Amount raised (e.g. $5M, ₹40 Cr) — write 'Undisclosed' if not mentioned",
      "stage": "Seed / Pre-Series A / Series A / Series B / Growth / Undisclosed",
      "investors": "Lead investor(s) name(s)",
      "focus": "One sentence: what the startup does and why VCs are betting on it",
      "url": "article url",
      "source": "source name"
    }
  ],
  "new_startups": [
    {
      "name": "Startup or product name",
      "founded_by": "Founder name(s) if mentioned, else 'Stealth / Unknown'",
      "what_it_does": "One sentence description",
      "why_interesting": "One sentence on what makes it notable for the India AI ecosystem",
      "url": "article url",
      "source": "source name"
    }
  ],
  "vc_trends": [
    {
      "trend": "Short title for the trend",
      "detail": "2-3 sentences explaining what VCs are betting on, which sectors are hot, and what the signal means for founders"
    }
  ],
  "policy_watch": [
    {
      "title": "Policy/initiative title",
      "body": "2 sentences: what it is and how it affects India AI startups or funding",
      "url": "article url",
      "source": "source name"
    }
  ],
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
      "context": "One sentence on why this is noteworthy",
      "url": "source url or null"
    }
  ],
  "vike_note": "One sharp, opinionated sentence: what should an AI founder or early-stage investor in India pay attention to most from today's news?"
}

Rules:
- funding_rounds: include ALL funding rounds mentioned, even small seed rounds — these are the most important signal
- new_startups: include newly launched or announced AI startups/products; skip if none
- vc_trends: 2 to 3 trends max, synthesized across multiple articles — don't just repeat individual stories
- policy_watch: only include if genuinely significant government/regulatory news exists; return empty array if not
- quick_hits: 3 to 6 items — noteworthy but not big enough for their own section
- If a section has no relevant data, return an empty array — never fabricate
- All monetary values: include both USD and INR equivalent if available
- Be direct and opinionated — no filler phrases like "it remains to be seen"
- The vike_note should be actionable advice, not a summary
- leaders_voices: scan for statements, interviews, or notable posts by Indian AI leaders in the last 24-48h. Include: Sridhar Vembu (Zoho), Pramod Varma (CDPI/Aadhaar), Bhavish Aggarwal (Ola/Krutrim), Sanjeev Sanyal, Vijay Shekhar Sharma (Paytm), Navin Tewari, or any named Indian AI founder/investor/policymaker. Return 2-3 entries max. If none found in articles, return empty array — never fabricate."""


def summarize_india_articles(articles: List[Dict]) -> Dict:
    """Send India articles to Claude and get back a structured digest dict."""
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

    user_message = f"""Here are today's India AI investment and startup news articles.
Today's date: {__import__('datetime').datetime.utcnow().strftime('%B %d, %Y')} (IST: +5:30 ahead of UTC)

Articles JSON:
{json.dumps(payload, indent=2)}

Produce the structured India AI Digest JSON now. Focus on: funding rounds, new AI startups,
VC investment trends, government policy, and notable quick hits from India's AI ecosystem."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
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
        "headline": "No India AI news found in this window — check back later.",
        "funding_rounds": [],
        "new_startups": [],
        "vc_trends": [],
        "policy_watch": [],
        "quick_hits": [],
        "vike_note": "Quiet day — use it to research upcoming Indian AI cohorts and incubator deadlines.",
    }


if __name__ == "__main__":
    test_articles = [
        {
            "title": "Sarvam AI raises $41M Series B led by Peak XV Partners",
            "summary": "Bengaluru-based Sarvam AI, building India-specific LLMs across 22 languages, has raised $41M in Series B funding led by Peak XV Partners.",
            "source": "Inc42",
            "url": "https://inc42.com",
            "category": "Funding Round",
        }
    ]
    result = summarize_india_articles(test_articles)
    print(json.dumps(result, indent=2))
