"""
extract_signals.py
Cheap multi-model signal extraction pass that runs BEFORE the expensive Claude
synthesis step.

Architecture:
  Raw articles (60–70 items)
        ↓
  [Fast/cheap model via OpenRouter]  ← gemini-flash, mistral-7b, or similar
        ↓
  Signal graph JSON: entities, claims, tensions, patterns
        ↓
  [Injected into Claude synthesis prompt]
        ↓
  Final structured digest with cross-source "connect the dots" insights

Why this matters:
- A cheap 7B–20B model can extract structured facts from 60 articles in seconds
- Claude (expensive) then reasons over a dense signal graph rather than raw text
- Cross-source patterns ("4 sources mention the same trend") emerge naturally
- Multiple models can cross-check each other before Claude sees anything

Signal graph schema:
{
  "entities": [
    {"name": str, "type": "company|model|person|regulation|event",
     "mentions": int, "sources": [str], "sentiment": "positive|negative|neutral|mixed"}
  ],
  "claims": [
    {"claim": str, "source_count": int, "sources": [str], "confidence": "high|medium|low"}
  ],
  "tensions": [
    {"topic": str, "side_a": str, "side_b": str, "sources_a": [str], "sources_b": [str]}
  ],
  "emerging_patterns": [
    {"pattern": str, "evidence": [str], "strength": "strong|moderate|weak"}
  ],
  "summary": str  -- 2-3 sentences synthesizing the signal landscape
}
"""

import json
import re
from typing import Dict, List, Optional

from openrouter_client import openrouter_complete, is_available, EXTRACTION_MODEL


# ─────────────────────────────────────────────────────────────────────────────
# Extraction system prompt — tuned for cheap/fast models
# ─────────────────────────────────────────────────────────────────────────────

EXTRACTION_SYSTEM = """You are a structured signal extractor for an AI news digest.
Given a batch of news articles, extract the key signals into a precise JSON object.
Return ONLY valid JSON — no markdown, no explanation, no preamble.

Focus on:
1. ENTITIES — companies, models, people, regulations mentioned across multiple articles
2. CLAIMS — factual claims or developments that appear in 2+ sources (higher confidence)
3. TENSIONS — cases where sources disagree, or where developments pull in opposite directions
4. EMERGING PATTERNS — recurring themes across multiple unrelated sources

Accuracy rules:
- Only include claims corroborated by at least 2 sources when possible
- Mark single-source claims as confidence: "low"
- If a tension is real, name both sides fairly
- "emerging_patterns" should be genuinely cross-source, not just one story
- Keep entity names consistent and canonical (e.g. "OpenAI" not "Open AI")"""


EXTRACTION_PROMPT_TEMPLATE = """Here are {count} AI/tech news article summaries. Extract the signal graph.

Articles:
{articles_text}

Return this exact JSON structure (no markdown fences):
{{
  "entities": [
    {{"name": "...", "type": "company|model|person|regulation|event", "mentions": N, "sources": ["..."], "sentiment": "positive|negative|neutral|mixed"}}
  ],
  "claims": [
    {{"claim": "...", "source_count": N, "sources": ["..."], "confidence": "high|medium|low"}}
  ],
  "tensions": [
    {{"topic": "...", "side_a": "...", "side_b": "...", "sources_a": ["..."], "sources_b": ["..."]}}
  ],
  "emerging_patterns": [
    {{"pattern": "...", "evidence": ["..."], "strength": "strong|moderate|weak"}}
  ],
  "summary": "2-3 sentence synthesis of the overall signal landscape"
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def extract_signals(articles: List[Dict], pipeline: str = "global") -> Optional[Dict]:
    """
    Run the cheap extraction pass over articles.
    Returns a signal graph dict, or None if OpenRouter is unavailable.

    This is non-blocking: if OpenRouter isn't configured, returns None and
    the pipeline falls back to running Claude without signal context.

    Args:
        articles:  List of article dicts (title, summary, source, url, category)
        pipeline:  "global" | "india" | "tn" — affects article truncation

    Returns:
        dict with keys: entities, claims, tensions, emerging_patterns, summary
        or None if extraction is skipped/failed
    """
    if not is_available():
        print("[Signals] OpenRouter not configured — skipping extraction pass")
        return None

    # Format articles as compact text (cheaper than JSON for extraction)
    # Use fewer tokens per article since extraction models are token-sensitive
    lines = []
    for i, a in enumerate(articles[:50], 1):  # cap at 50 for extraction
        title   = a.get("title", "")[:120]
        summary = a.get("summary", "")[:200]
        source  = a.get("source", "unknown")
        lines.append(f"[{i}] SOURCE: {source}\nTITLE: {title}\nSUMMARY: {summary}\n")

    articles_text = "\n".join(lines)
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        count=len(lines),
        articles_text=articles_text,
    )

    print(f"[Signals] Extracting signals from {len(lines)} articles via {EXTRACTION_MODEL}...")
    raw = openrouter_complete(
        system=EXTRACTION_SYSTEM,
        user=prompt,
        max_tokens=2500,
        temperature=0.1,  # Very low — we want deterministic structured extraction
    )

    if not raw:
        print("[Signals] Extraction returned empty — skipping")
        return None

    # Strip accidental markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = raw.strip()

    try:
        signals = json.loads(raw)
        entity_count  = len(signals.get("entities", []))
        claim_count   = len(signals.get("claims", []))
        tension_count = len(signals.get("tensions", []))
        pattern_count = len(signals.get("emerging_patterns", []))
        print(f"[Signals] Extracted: {entity_count} entities, {claim_count} claims, "
              f"{tension_count} tensions, {pattern_count} patterns")
        return signals
    except json.JSONDecodeError as e:
        print(f"[Signals] JSON parse failed: {e} — skipping signal injection")
        return None


def format_signals_for_prompt(signals: Dict) -> str:
    """
    Format the signal graph as a readable block for injection into the
    Claude synthesis prompt. Claude understands this better than raw JSON.

    Returns a string block like:

    === SIGNAL GRAPH (pre-extracted by fast model) ===
    Key entities: OpenAI (company, 8 mentions, positive), ...
    High-confidence claims (2+ sources):
      • GPT-5 released with improved reasoning [OpenAI Blog, The Verge, TechCrunch]
    Cross-source tensions:
      • Open-source vs closed: Zuckerberg argues open is safer; Altman says closed needed
    Emerging patterns:
      ↑ STRONG: Inference cost dropping 10x — evidence: [Groq pricing, Together AI post, ...]
    Summary: ...
    === END SIGNAL GRAPH ===
    """
    if not signals:
        return ""

    lines = ["=== SIGNAL GRAPH (pre-extracted cross-source signals) ===",
             "Use these to inform cross-run patterns and 'connect the dots' insights.",
             ""]

    # Entities
    entities = signals.get("entities", [])
    if entities:
        top = sorted(entities, key=lambda e: e.get("mentions", 0), reverse=True)[:12]
        entity_strs = []
        for e in top:
            name     = e.get("name", "?")
            etype    = e.get("type", "?")
            mentions = e.get("mentions", "?")
            sentiment = e.get("sentiment", "")
            s = f"{name} ({etype}, {mentions}×"
            if sentiment and sentiment != "neutral":
                s += f", {sentiment}"
            s += ")"
            entity_strs.append(s)
        lines.append("Key entities: " + " | ".join(entity_strs))
        lines.append("")

    # High-confidence claims
    claims = [c for c in signals.get("claims", []) if c.get("confidence") in ("high", "medium")]
    if claims:
        lines.append("Corroborated claims (2+ sources):")
        for c in claims[:8]:
            srcs = ", ".join(c.get("sources", [])[:3])
            lines.append(f"  • {c.get('claim', '')} [{srcs}]")
        lines.append("")

    # Tensions
    tensions = signals.get("tensions", [])
    if tensions:
        lines.append("Cross-source tensions:")
        for t in tensions[:4]:
            lines.append(f"  ↔ {t.get('topic', '')}: {t.get('side_a', '')} vs. {t.get('side_b', '')}")
        lines.append("")

    # Emerging patterns
    patterns = signals.get("emerging_patterns", [])
    if patterns:
        lines.append("Emerging patterns:")
        for p in patterns[:4]:
            strength = p.get("strength", "").upper()
            evidence = "; ".join(p.get("evidence", [])[:2])
            lines.append(f"  ↑ {strength}: {p.get('pattern', '')} — evidence: {evidence}")
        lines.append("")

    # Summary
    summary = signals.get("summary", "")
    if summary:
        lines.append(f"Signal summary: {summary}")

    lines.append("=== END SIGNAL GRAPH ===")
    return "\n".join(lines)


def extract_and_format(articles: List[Dict], pipeline: str = "global") -> str:
    """
    Convenience function: extract signals and return the formatted string
    ready to inject into a Claude prompt. Returns empty string if unavailable.
    """
    signals = extract_signals(articles, pipeline=pipeline)
    if not signals:
        return ""
    return format_signals_for_prompt(signals)


if __name__ == "__main__":
    # Smoke test with fake articles
    test_articles = [
        {"title": "OpenAI releases GPT-5 with improved reasoning",
         "summary": "OpenAI announced GPT-5, claiming 3x better reasoning than GPT-4.",
         "source": "OpenAI Blog", "url": "https://openai.com", "category": "Model Releases"},
        {"title": "GPT-5 benchmarks show huge leap, analysts say",
         "summary": "Third-party benchmarks confirm GPT-5 dramatically outperforms GPT-4 on math.",
         "source": "The Verge", "url": "https://theverge.com", "category": "Analysis"},
        {"title": "Anthropic's Claude holds its own vs GPT-5",
         "summary": "Analysts find Claude 3.7 competitive with GPT-5 on most benchmarks.",
         "source": "TechCrunch", "url": "https://techcrunch.com", "category": "Analysis"},
        {"title": "Meta open-sources Llama 4 the day after GPT-5 launch",
         "summary": "Meta released Llama 4 as a strategic counter to OpenAI's GPT-5 launch.",
         "source": "Reuters", "url": "https://reuters.com", "category": "Open Source"},
    ]

    if not is_available():
        print("OpenRouter not configured. Set OPENROUTER_API_KEY to test.")
    else:
        result = extract_and_format(test_articles, pipeline="global")
        print(result if result else "No signals extracted")
