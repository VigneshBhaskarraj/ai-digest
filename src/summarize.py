"""
summarize.py
Uses Anthropic Claude API to summarize and structure the fetched articles
into a clean digest with sections, key highlights, and brief summaries.
"""

import os
import json
import anthropic
from typing import List, Dict

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are an expert AI industry analyst. Your job is to read a list of raw news articles
and produce a clean, structured daily digest for AI/ML professionals who want signal, not noise.

You will be given a JSON list of articles with title, summary, source, and category.

Return ONLY valid JSON (no markdown, no extra text) in this exact structure:
{
  "headline": "One punchy sentence summarizing the most important development today",
  "signal_surge": {
    "topic": "The single hottest topic appearing across 3+ independent sources today",
    "sources_count": 4,
    "why_surging": "2 sentences on why this topic is dominating right now and what it means",
    "sources": ["Source1", "Source2", "Source3"]
  },
  "top_stories": [
    {
      "title": "Story title (rewritten to be clear and direct)",
      "source": "Source name",
      "url": "original url",
      "why_it_matters": "2-3 sentences explaining the significance for AI practitioners and builders",
      "category": "Model Releases | Research | Tools & Products | Industry News | Community",
      "credibility": "high | medium | community"
    }
  ],
  "quick_hits": [
    {
      "title": "Brief title",
      "source": "Source",
      "url": "url",
      "one_liner": "One sentence max"
    }
  ],
  "arxiv_picks": [
    {
      "title": "Paper title",
      "url": "url",
      "tldr": "One sentence what the paper does and why it matters"
    }
  ],
  "community_pulse": "2-3 sentences summarizing what the AI community on Reddit/forums is discussing or building",
  "leaders_voices": [
    {
      "name": "Leader's full name",
      "role": "Their title / affiliation e.g. CEO OpenAI / AI Researcher",
      "insight": "What they said, shared, or argued — paraphrased in 1-2 punchy sentences",
      "context": "One sentence on why this is noteworthy or what sparked it",
      "url": "source url or null"
    }
  ],
  "vike_note": "One sharp, opinionated sentence about what a data/AI professional transitioning to Gen AI roles should pay attention to most today"
}

Rules:
- top_stories: 4 to 6 most important items only, prioritize model releases and major tool launches
- quick_hits: 5 to 8 shorter items not covered in top stories
- arxiv_picks: 2 to 3 most practically relevant papers only, skip pure theory
- If there are no arXiv articles, return empty array for arxiv_picks
- Be direct and opinionated in why_it_matters — no filler phrases
- The vike_note is personalized career advice based on what matters most in the digest
- signal_surge: identify the ONE topic that appears most across independent sources (e.g. "AI agents", "GPT-5", "open source LLMs"). Count how many distinct sources mention it.
- credibility field: "high" for lab blogs/research papers, "medium" for tech news, "community" for Reddit/HN
- If no clear signal surge (fewer than 3 sources on any one topic), set signal_surge to null
- leaders_voices: scan articles for things said/posted/written by notable AI figures in the last 24-48h. Cast a wide net — include: Sam Altman (OpenAI CEO), Andrej Karpathy (AI researcher/educator), Yann LeCun (Meta Chief AI Scientist), Geoffrey Hinton (AI pioneer), Demis Hassabis (Google DeepMind CEO), Dario Amodei (Anthropic CEO), Jensen Huang (NVIDIA CEO), Ilya Sutskever (SSI founder), Greg Brockman (OpenAI), Fei-Fei Li (Stanford/World Labs), Mark Zuckerberg (Meta CEO), Ali Ghodsi (Databricks CEO), Andrew Ng (AI Fund/DeepLearning.AI), Emad Mostaque (Stability AI founder), Satya Nadella (Microsoft CEO), Sundar Pichai (Google CEO), Yoshua Bengio (AI safety researcher), Mustafa Suleyman (Microsoft AI CEO), or ANY other named AI researcher, founder, or executive with a notable statement. Return 6-10 entries, ranked by how hot/impactful the post or statement is. If fewer than 6 named leader statements exist in the articles, return only what's actually found — never fabricate quotes."""


def summarize_articles(articles: List[Dict], session_label: str = "Morning") -> Dict:
    """
    Send articles to Claude and get back a structured digest dict.
    session_label: 'Morning' or 'Evening'
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Trim articles to keep token usage reasonable
    payload = []
    for a in articles[:60]:  # cap at 60 articles per run
        payload.append({
            "title":    a["title"],
            "summary":  a["summary"][:300],
            "source":   a["source"],
            "url":      a["url"],
            "category": a["category"],
        })

    user_message = f"""Here are the latest AI/ML news articles for the {session_label} digest.
Today's date: {__import__('datetime').datetime.utcnow().strftime('%B %d, %Y')}
Session: {session_label}

Articles JSON:
{json.dumps(payload, indent=2)}

Produce the structured digest JSON now."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


if __name__ == "__main__":
    # Quick test with dummy data
    test_articles = [
        {
            "title": "Anthropic releases Claude 4 with extended thinking",
            "summary": "Anthropic today announced Claude 4, featuring improved reasoning and agentic capabilities.",
            "source": "Anthropic Blog",
            "url": "https://anthropic.com",
            "category": "Model Releases",
        }
    ]
    result = summarize_articles(test_articles, "Morning")
    print(json.dumps(result, indent=2))
