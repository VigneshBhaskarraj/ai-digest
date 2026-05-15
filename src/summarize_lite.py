"""
summarize_lite.py
Produces the AI Digest Lite — a curated 15-minute briefing covering Global + India
AI news in a flip-card format. Each card has:
  - Front: punchy title + 2-sentence summary
  - Back:  real-world implication (what does this mean for businesses, jobs,
           consumers, investors, specific industries)

Both sections are produced in a single Claude call to minimise API cost.
"""

import os
import json
import anthropic
from datetime import datetime, timezone
from typing import List, Dict

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are a senior technology analyst writing for a busy professional audience.
Your job is to curate today's most important AI news into a tight 15-minute briefing — split across Global and India sections.

For each story you MUST produce three things:
1. A punchy, specific title (not generic — name the company/model/person)
2. A 2-sentence summary for the card front — what happened, stated plainly
3. A real-world implication for the card back — 3-4 sentences explaining concrete impact:
   - Which industry or profession is most affected?
   - What does this enable or disrupt?
   - Any economic, investment, or consumer angle?
   - For India stories: what does this mean specifically for the Indian market or ecosystem?

Implication rules:
- Be concrete. "This could increase voice-to-text processing speeds by 3x in call centres" beats "This has implications for NLP"
- Name affected industries, roles, or companies when relevant
- Avoid hedge words like "might possibly perhaps"
- Think like an investor or founder reading at 7am — what do they DO with this information?

Selection rules:
- Pick 8 to 10 stories per section (Global and India separately)
- Prefer stories with clear real-world consequences over incremental model benchmarks
- Skip press releases with no concrete development
- If a story is minor, skip it — quality over completeness
- impact: "high" = affects millions of people or billions in market; "medium" = affects a significant sector; "low" = niche but interesting

Return ONLY valid JSON, no markdown, no explanation:
{
  "global_headline": "One sharp sentence capturing the overall global AI mood today",
  "india_headline": "One sharp sentence capturing the overall India AI mood today",
  "global": [
    {
      "title": "Specific punchy title naming who/what",
      "summary": "Sentence one. Sentence two.",
      "implication": "3-4 sentences of concrete real-world impact.",
      "source": "Source name",
      "url": "article url",
      "category": "Model Release | Funding | Policy | Research | Product | Industry | Open Source",
      "impact": "high | medium | low"
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
      "impact": "high | medium | low"
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

    # Trim and format articles — keep it tight
    def prep(articles, cap=30):
        out = []
        for a in articles[:cap]:
            out.append({
                "title":    a["title"],
                "summary":  a.get("summary", "")[:120],
                "source":   a["source"],
                "url":      a["url"],
                "category": a.get("category", ""),
            })
        return out

    global_payload = prep(global_articles, cap=30)
    india_payload  = prep(india_articles,  cap=25)

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    memory_block = f"\n{memory_context}\n" if memory_context else ""

    user_message = f"""Today is {today}.
{memory_block}
Produce AI Digest Lite — a curated 15-minute briefing with 8-10 cards per section.

=== GLOBAL AI NEWS ({len(global_payload)} articles) ===
{json.dumps(global_payload, indent=2)}

=== INDIA AI NEWS ({len(india_payload)} articles) ===
{json.dumps(india_payload, indent=2)}

Return the structured Lite digest JSON now. Focus on stories where the real-world implication is genuinely interesting and actionable."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
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
        "global_headline": "No global AI news found — check back at the next update.",
        "india_headline":  "No India AI news found — check back at the next update.",
        "global": [],
        "india":  [],
    }
