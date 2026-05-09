"""
memory.py
Temporal memory store for the AI Digest pipelines.

Every pipeline run writes its key signals — headlines, top stories, entities,
and named leaders — into a local SQLite database. Future summarization prompts
can then query the last N days of history and inject it as context, enabling
cross-run insights like:
  "This builds on last week's X..."
  "Three stories this week all point to the same trend as last Tuesday's..."
  "This is the fourth consecutive day Y has appeared in top stories..."

Database location: data/digest_memory.db (relative to repo root, gitignored)

Usage:
    from memory import store_run, get_recent_context, get_entity_trend

    # After each successful summarize() call:
    store_run(digest, pipeline="global", session="morning")

    # Before the summarize() call — inject into user message:
    context = get_recent_context(days=14, pipeline="global")
    # → "Recent signals (last 14 days): ..."
"""

import os
import json
import sqlite3
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# DB path — lives in data/ next to src/, gitignored
# ─────────────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).parent.parent
DB_PATH = os.environ.get("DIGEST_DB_PATH", str(_REPO_ROOT / "data" / "digest_memory.db"))


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call on every startup."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline    TEXT NOT NULL,       -- 'global' | 'india' | 'tn'
            session     TEXT,                -- 'morning' | 'evening' | null
            run_date    TEXT NOT NULL,       -- YYYY-MM-DD
            headline    TEXT,
            vike_note   TEXT,
            raw_json    TEXT,               -- full digest JSON for future replay
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS top_stories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id      INTEGER NOT NULL REFERENCES runs(id),
            pipeline    TEXT NOT NULL,
            run_date    TEXT NOT NULL,
            title       TEXT,
            source      TEXT,
            url         TEXT,
            category    TEXT,
            credibility TEXT
        );

        CREATE TABLE IF NOT EXISTS entities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id      INTEGER NOT NULL REFERENCES runs(id),
            pipeline    TEXT NOT NULL,
            run_date    TEXT NOT NULL,
            name        TEXT NOT NULL,      -- entity name (company / person / model / regulation)
            entity_type TEXT,               -- 'company' | 'model' | 'person' | 'regulation' | 'event'
            context     TEXT                -- brief note on how it appeared
        );

        CREATE TABLE IF NOT EXISTS signal_surge (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id      INTEGER NOT NULL REFERENCES runs(id),
            pipeline    TEXT NOT NULL,
            run_date    TEXT NOT NULL,
            topic       TEXT,
            why_surging TEXT,
            sources_count INTEGER
        );

        CREATE TABLE IF NOT EXISTS leaders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id      INTEGER NOT NULL REFERENCES runs(id),
            pipeline    TEXT NOT NULL,
            run_date    TEXT NOT NULL,
            name        TEXT,
            role        TEXT,
            insight     TEXT,
            url         TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_stories_date     ON top_stories(run_date, pipeline);
        CREATE INDEX IF NOT EXISTS idx_entities_name    ON entities(name, pipeline);
        CREATE INDEX IF NOT EXISTS idx_entities_date    ON entities(run_date, pipeline);
        CREATE INDEX IF NOT EXISTS idx_surge_date       ON signal_surge(run_date, pipeline);
        CREATE INDEX IF NOT EXISTS idx_leaders_name     ON leaders(name, pipeline);
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Write
# ─────────────────────────────────────────────────────────────────────────────

def store_run(digest: Dict, pipeline: str, session: str = "") -> int:
    """
    Persist a completed digest to the memory store.
    Returns the run_id so callers can chain additional writes.
    """
    init_db()
    conn = _get_conn()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Insert the run record
    cur = conn.execute(
        "INSERT INTO runs (pipeline, session, run_date, headline, vike_note, raw_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            pipeline, session, today,
            digest.get("headline", ""),
            digest.get("vike_note", ""),
            json.dumps(digest, ensure_ascii=False)[:8000],  # cap raw JSON size
        )
    )
    run_id = cur.lastrowid

    # Top stories
    for story in digest.get("top_stories", []):
        conn.execute(
            "INSERT INTO top_stories (run_id, pipeline, run_date, title, source, url, category, credibility) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (run_id, pipeline, today,
             story.get("title", ""), story.get("source", ""),
             story.get("url", ""), story.get("category", ""),
             story.get("credibility", ""))
        )

    # Signal surge
    surge = digest.get("signal_surge")
    if surge:
        conn.execute(
            "INSERT INTO signal_surge (run_id, pipeline, run_date, topic, why_surging, sources_count) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, pipeline, today,
             surge.get("topic", ""), surge.get("why_surging", ""),
             surge.get("sources_count", 0))
        )

    # Leaders voices
    for lv in digest.get("leaders_voices", []):
        conn.execute(
            "INSERT INTO leaders (run_id, pipeline, run_date, name, role, insight, url) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, pipeline, today,
             lv.get("name", ""), lv.get("role", ""),
             lv.get("insight", ""), lv.get("url", ""))
        )

    # Extract entities from story titles and signal surge
    _extract_and_store_entities(conn, run_id, pipeline, today, digest)

    conn.commit()
    conn.close()
    print(f"[Memory] Run #{run_id} stored — {pipeline}/{session or 'auto'} on {today}")
    return run_id


def _extract_and_store_entities(conn, run_id: int, pipeline: str, run_date: str, digest: Dict):
    """
    Simple entity extraction from digest text — pulls known company/model names
    and any capitalized multi-word phrases that look like proper nouns.
    This is a lightweight heuristic; the full NER pass happens in extract_signals.py.
    """
    # Known high-signal entities to track explicitly
    KNOWN_ENTITIES = [
        # Labs & companies
        "Anthropic", "OpenAI", "Google DeepMind", "Meta AI", "Mistral", "xAI",
        "Cohere", "Stability AI", "Inflection", "Character AI", "Perplexity",
        "Hugging Face", "NVIDIA", "Microsoft", "Apple", "Amazon", "Databricks",
        "Snowflake", "Scale AI", "Weights & Biases", "Together AI", "Replicate",
        # Models
        "Claude", "GPT-4", "GPT-5", "Gemini", "Llama", "Mistral", "Grok",
        "Stable Diffusion", "Sora", "Gemma", "Phi", "Qwen", "DeepSeek",
        # People
        "Sam Altman", "Andrej Karpathy", "Yann LeCun", "Jensen Huang",
        "Dario Amodei", "Ilya Sutskever", "Demis Hassabis", "Fei-Fei Li",
        "Andrew Ng", "Geoffrey Hinton", "Yoshua Bengio", "Mark Zuckerberg",
        "Satya Nadella", "Sundar Pichai", "Ali Ghodsi", "Mustafa Suleyman",
        # Regulations/events
        "EU AI Act", "Executive Order", "GDPR", "AI Safety Summit",
        "SB 1047", "Model Welfare", "Constitutional AI",
        # India-specific
        "IndiaAI", "NASSCOM", "StartupTN", "IITM Pravartak",
        "Zoho", "Freshworks", "Chargebee", "Uniphore",
        "Bhavish Aggarwal", "Sridhar Vembu",
    ]

    # Collect all text to search
    text_blobs = [
        digest.get("headline", ""),
        digest.get("vike_note", ""),
    ]
    for story in digest.get("top_stories", []):
        text_blobs.append(story.get("title", ""))
        text_blobs.append(story.get("why_it_matters", ""))
    for lv in digest.get("leaders_voices", []):
        text_blobs.append(lv.get("insight", ""))
    surge = digest.get("signal_surge")
    if surge:
        text_blobs.append(surge.get("topic", ""))

    full_text = " ".join(text_blobs)

    seen = set()
    for entity in KNOWN_ENTITIES:
        if entity.lower() in full_text.lower() and entity not in seen:
            seen.add(entity)
            # Classify type
            people = ["Altman", "Karpathy", "LeCun", "Huang", "Amodei", "Sutskever",
                      "Hassabis", "Li", "Ng", "Hinton", "Bengio", "Zuckerberg",
                      "Nadella", "Pichai", "Ghodsi", "Suleyman", "Vembu", "Aggarwal"]
            models = ["Claude", "GPT-4", "GPT-5", "Gemini", "Llama", "Mistral", "Grok",
                      "Stable Diffusion", "Sora", "Gemma", "Phi", "Qwen", "DeepSeek"]
            regs   = ["EU AI Act", "Executive Order", "GDPR", "AI Safety Summit",
                      "SB 1047", "Model Welfare", "Constitutional AI"]

            if any(p in entity for p in people):
                etype = "person"
            elif entity in models:
                etype = "model"
            elif entity in regs:
                etype = "regulation"
            else:
                etype = "company"

            conn.execute(
                "INSERT INTO entities (run_id, pipeline, run_date, name, entity_type, context) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, pipeline, run_date, entity, etype, "auto-extracted")
            )


# ─────────────────────────────────────────────────────────────────────────────
# Read — context injection for prompts
# ─────────────────────────────────────────────────────────────────────────────

def get_recent_context(days: int = 14, pipeline: str = "global") -> str:
    """
    Returns a compact text summary of the last N days of signals for
    injection into the summarization user message.

    If the DB doesn't exist yet (first run), returns empty string silently.
    """
    try:
        init_db()
        conn = _get_conn()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

        # Recent headlines
        rows = conn.execute(
            "SELECT run_date, session, headline FROM runs "
            "WHERE pipeline=? AND run_date >= ? ORDER BY run_date DESC LIMIT 20",
            (pipeline, cutoff)
        ).fetchall()

        if not rows:
            conn.close()
            return ""

        lines = [f"=== RECENT DIGEST HISTORY (last {days} days, {pipeline} pipeline) ===",
                 "Use this to identify continuing trends and cross-run patterns.",
                 "Do NOT repeat these as new stories unless they have significant new developments.",
                 ""]

        for row in rows:
            session_tag = f" [{row['session']}]" if row['session'] else ""
            lines.append(f"• {row['run_date']}{session_tag}: {row['headline']}")

        # Recent surge topics
        surges = conn.execute(
            "SELECT run_date, topic, sources_count FROM signal_surge "
            "WHERE pipeline=? AND run_date >= ? ORDER BY run_date DESC LIMIT 7",
            (pipeline, cutoff)
        ).fetchall()
        if surges:
            lines.append("")
            lines.append("Recent signal surges:")
            for s in surges:
                lines.append(f"  ↑ {s['run_date']}: {s['topic']} ({s['sources_count']} sources)")

        # Most frequently appearing entities
        entity_counts = conn.execute(
            "SELECT name, entity_type, COUNT(*) as c FROM entities "
            "WHERE pipeline=? AND run_date >= ? "
            "GROUP BY name ORDER BY c DESC LIMIT 10",
            (pipeline, cutoff)
        ).fetchall()
        if entity_counts:
            lines.append("")
            lines.append(f"Most-mentioned entities ({days}d):")
            for e in entity_counts:
                lines.append(f"  {e['name']} ({e['entity_type']}): {e['c']} appearances")

        lines.append("=== END HISTORY ===")
        conn.close()
        return "\n".join(lines)

    except Exception as exc:
        print(f"[Memory] Context retrieval failed (non-fatal): {exc}")
        return ""


def get_entity_trend(entity_name: str, pipeline: str = "global", days: int = 30) -> List[Dict]:
    """
    Returns day-by-day presence of an entity across recent runs.
    Useful for the temporal chain analysis ("3rd consecutive week X appeared").
    """
    try:
        init_db()
        conn = _get_conn()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = conn.execute(
            "SELECT run_date, COUNT(*) as c FROM entities "
            "WHERE pipeline=? AND run_date >= ? AND name LIKE ? "
            "GROUP BY run_date ORDER BY run_date DESC",
            (pipeline, cutoff, f"%{entity_name}%")
        ).fetchall()
        conn.close()
        return [{"date": r["run_date"], "count": r["c"]} for r in rows]
    except Exception:
        return []


def get_repeat_stories(pipeline: str = "global", days: int = 7) -> List[str]:
    """
    Returns story titles that appeared more than once in the last N days.
    Helps the summarization prompt avoid repeating known stories.
    """
    try:
        init_db()
        conn = _get_conn()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = conn.execute(
            "SELECT title, COUNT(*) as c FROM top_stories "
            "WHERE pipeline=? AND run_date >= ? "
            "GROUP BY title HAVING c > 1 ORDER BY c DESC LIMIT 15",
            (pipeline, cutoff)
        ).fetchall()
        conn.close()
        return [r["title"] for r in rows]
    except Exception:
        return []


def get_stats() -> Dict:
    """Quick stats for debugging — total rows per table."""
    try:
        init_db()
        conn = _get_conn()
        stats = {}
        for table in ["runs", "top_stories", "entities", "signal_surge", "leaders"]:
            stats[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        # Per-pipeline run counts
        rows = conn.execute(
            "SELECT pipeline, COUNT(*) as c FROM runs GROUP BY pipeline"
        ).fetchall()
        stats["by_pipeline"] = {r["pipeline"]: r["c"] for r in rows}
        conn.close()
        return stats
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    init_db()
    print("DB initialized at:", DB_PATH)

    # Quick smoke test with fake data
    fake_digest = {
        "headline": "Test: OpenAI ships GPT-5 with native reasoning",
        "top_stories": [
            {"title": "GPT-5 Released", "source": "OpenAI Blog",
             "url": "https://openai.com", "category": "Model Releases", "credibility": "high"},
        ],
        "signal_surge": {"topic": "GPT-5 Release", "why_surging": "Major model drop", "sources_count": 8,
                         "sources": ["OpenAI Blog", "TechCrunch"]},
        "leaders_voices": [
            {"name": "Sam Altman", "role": "CEO OpenAI",
             "insight": "GPT-5 is our best model yet.", "url": "https://x.com/sama"}
        ],
        "quick_hits": [],
        "vike_note": "GPT-5 tool-use improvements are directly relevant to agentic AI roles.",
    }
    run_id = store_run(fake_digest, pipeline="global", session="morning")
    print(f"Stored test run #{run_id}")

    ctx = get_recent_context(days=7, pipeline="global")
    print("\n--- Context that would be injected into next prompt ---")
    print(ctx)

    stats = get_stats()
    print("\n--- DB stats ---")
    for k, v in stats.items():
        print(f"  {k}: {v}")
