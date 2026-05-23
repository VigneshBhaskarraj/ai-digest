"""
summarize_lite.py
Produces the AI Digest Lite — a curated 15-minute briefing covering Global + India
AI news in a full-screen swipe-card format. Each card has:
  - Front: punchy title + 2-sentence summary + date
  - Back:  business implications targeting CTOs, CFOs, founders, enterprise leaders

Both sections are produced in a single Claude call to minimise API cost.
"""

import os
import json
import anthropic
from datetime import datetime, timezone
from typing import List, Dict

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are a senior technology strategist briefing C-suite executives and founders on AI developments.
Your audience: CTOs and heads of engineering at companies like TCS, Infosys, Wipro, Accenture; CFOs evaluating AI spend;
Series A–C founders deciding where to build; VPs of strategy at Fortune 500s; venture partners deciding what to fund.

For each story you MUST produce:
1. A punchy, specific title — name the company, model, or person (never generic)
2. A 2-sentence summary — what happened, plainly stated
3. Business implications — 4-5 sharp sentences targeting this executive audience:
   - Which business lines, revenue streams, or cost structures are directly affected?
   - What competitive threat or market opportunity does this open in the next 6–18 months?
   - What is the talent, vendor, or build-vs-buy implication?
   - Is there an investment signal — sector heating up, valuations shifting, M&A likely?
   - End with ONE concrete action: what should a smart leader do in the next 90 days?
   For India stories: frame in the context of Indian IT services exports, domestic enterprise adoption, government policy, and MNC vs. local player dynamics.
4. A date — the article's publication date formatted as "Month DD, YYYY" (e.g., "May 14, 2026"). Use the published field if available, else use today's date.

Implication rules:
- Specificity beats hedging. "This halves the cost of document-processing workflows, threatening ₹800Cr/year in BPO contracts" beats "this could impact BPO."
- Name affected sectors, roles, or named companies when relevant.
- Zero hedge words: no "might", "possibly", "could perhaps". Write like it already happened or will happen.
- The 90-day action should be concrete — start an eval, brief the board, pause a vendor contract, hire a specialist.

Selection rules:
- Pick 8 to 10 stories per section (Global and India separately)
- Prefer stories with clear business consequences over model benchmarks or incremental updates
- Skip PR fluff with no concrete development, funding announcements without product context, or conference recaps
- impact: "high" = affects billions in market cap or millions of workers; "medium" = materially shifts a significant sector; "low" = niche but strategically interesting

Return ONLY valid JSON, no markdown, no explanation:
{
  "global_headline": "One sharp sentence capturing the dominant global AI business theme today",
  "india_headline": "One sharp sentence capturing the dominant India AI business theme today",
  "global": [
    {
      "title": "Specific punchy title naming who/what",
      "summary": "Sentence one. Sentence two.",
      "implication": "4-5 sentences of concrete business impact ending with a 90-day action.",
      "source": "Source name",
      "url": "article url",
      "category": "Model Release | Funding | Policy | Research | Product | Industry | Open Source | Workforce",
      "impact": "high | medium | low",
      "date": "Month DD, YYYY"
    }
  ],
  "india": [
    {
      "title": "...",
      "summary": "...",
      "implication": "...",
      "source": "...",
      "url": "...",
      "category": "...",
      "impact": "high | medium | low",
      "date": "Month DD, YYYY"
    }
  ]
}"""


def summarize_lite(global_articles: List[Dict], india_articles: List[Dict],
                   memory_context: str = "") -> Dict:
    """
    Produce the Lite digest from global + India article lists.
    Returns a dict with global_headline, india_headline, global[], india[].
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Trim and format articles — include published date for card display
    def prep(articles, cap=30):
        out = []
        for a in articles[:cap]:
            out.append({
                "title":     a["title"],
                "summary":   a.get("summary", "")[:150],
                "source":    a["source"],
                "url":       a["url"],
                "category":  a.get("category", ""),
                "published": a.get("published", ""),
            })
        return out

    global_payload = prep(global_articles, cap=30)
    india_payload  = prep(india_articles,  cap=25)

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    memory_block = f"\n{memory_context}\n" if memory_context else ""

    user_message = f"""Today is {today}.
{memory_block}
Produce AI Digest Lite — 8-10 high-signal cards per section for C-suite and founder readers.

=== GLOBAL AI NEWS ({len(global_payload)} articles) ===
{json.dumps(global_payload, indent=2)}

=== INDIA AI NEWS ({len(india_payload)} articles) ===
{json.dumps(india_payload, indent=2)}

Return the structured Lite digest JSON. Prioritise stories with clear business impact. Make implications actionable for executives who read this at 7am and need to know what to do next."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Response was truncated — retry with a tighter card cap
        print("      Warning: response truncated, retrying with fewer cards...")
        trimmed_prompt = user_message.replace(
            "8-10 high-signal cards per section", "5-6 high-signal cards per section"
        )
        message2 = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": trimmed_prompt}],
        )
        raw2 = message2.content[0].text.strip()
        if raw2.startswith("```"):
            raw2 = raw2.split("```")[1]
            if raw2.startswith("json"):
                raw2 = raw2[4:]
        return json.loads(raw2.strip())


def _empty_digest() -> Dict:
    return {
        "global_headline": "No global AI news found — check back at the next update.",
        "india_headline":  "No India AI news found — check back at the next update.",
        "global": [],
        "india":  [],
    }
