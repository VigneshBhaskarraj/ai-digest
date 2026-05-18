"""
lite_main.py
Orchestrates the AI Digest Lite pipeline:
  1. Fetch global AI news
  2. Fetch India AI news
  3. Summarise both into flip-card format (one Claude call)
  4. Render to docs/lite.html
  5. Store run in memory DB

Run manually:
  python src/lite_main.py

Scheduled: daily at 7AM CST (13:00 UTC) — morning slot, GitHub Actions.
"""

import sys
import os
import re
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_news       import fetch_all
from fetch_india_news import fetch_all_india
from summarize_lite   import summarize_lite, _empty_digest
from render_lite_html import render_lite_html, save_lite_dashboard
from memory           import store_run, get_recent_context

# Sources where OG images are generic/unhelpful — skip fetching
_SKIP_OG_DOMAINS = ("reddit.com", "arxiv.org", "paperswithcode.com",
                    "hnrss.org", "news.ycombinator.com")

def fetch_og_image(url: str) -> str:
    """Return the og:image (or twitter:image) URL from an article page, or ''."""
    if not url or any(d in url for d in _SKIP_OG_DOMAINS):
        return ""
    try:
        r = requests.get(
            url, timeout=5, stream=True,
            headers={"User-Agent": "ai-digest-bot/1.0 (github.com/VigneshBhaskarraj/ai-digest)"},
            allow_redirects=True,
        )
        # Read only the first 40 KB — enough to cover <head>
        chunk = b""
        for c in r.iter_content(chunk_size=4096):
            chunk += c
            if len(chunk) >= 40960:
                break
        html = chunk.decode("utf-8", errors="ignore")
        for pattern in (
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
        ):
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                img = m.group(1).strip()
                # Skip data URIs and obviously generic images
                if img and not img.startswith("data:"):
                    return img
    except Exception:
        pass
    return ""


def run():
    print(f"\n{'='*50}")
    print(f"  AI Digest Lite Pipeline")
    print(f"{'='*50}\n")

    # ── 1. Fetch ──────────────────────────────────────────────────────────────
    print("[1/4] Fetching global AI news...")
    global_articles = fetch_all(max_age_hours=24)
    print(f"      {len(global_articles)} global articles\n")

    print("[2/4] Fetching India AI news...")
    india_articles = fetch_all_india(max_age_hours=24)
    print(f"      {len(india_articles)} India articles\n")

    if not global_articles and not india_articles:
        print("No articles found. Saving empty Lite digest.")
        digest = _empty_digest()
    else:
        # ── 2. Memory context ─────────────────────────────────────────────────
        memory_context = get_recent_context(days=7, pipeline="lite")
        if memory_context:
            print(f"      Memory context: {len(memory_context)} chars\n")

        # ── 3. Summarise ──────────────────────────────────────────────────────
        print("[3/4] Summarising with Claude API (Lite prompt)...")
        digest = summarize_lite(global_articles, india_articles,
                                memory_context=memory_context)
        g_count = len(digest.get("global", []))
        i_count = len(digest.get("india",  []))
        print(f"      {g_count} global cards, {i_count} India cards\n")

        # Enrich each story with its article's OG image
        print("      Fetching OG images for cards...")
        for section in ("global", "india"):
            for story in digest.get(section, []):
                story["image"] = fetch_og_image(story.get("url", ""))
        fetched = sum(
            1 for s in (digest.get("global", []) + digest.get("india", []))
            if s.get("image")
        )
        print(f"      {fetched}/{g_count + i_count} cards have images\n")

    # ── 4. Render & save ──────────────────────────────────────────────────────
    print("[4/4] Rendering Lite dashboard & storing memory...")
    html = render_lite_html(digest)

    output_path = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "docs",
        "lite.html"
    )
    save_lite_dashboard(html, output_path)

    # Store a compact run record so memory context builds over time
    # Map to a simple format compatible with store_run
    lite_record = {
        "headline":    digest.get("global_headline", ""),
        "vike_note":   digest.get("india_headline", ""),
        "top_stories": [
            {
                "title":       s.get("title", ""),
                "source":      s.get("source", ""),
                "url":         s.get("url", ""),
                "category":    s.get("category", ""),
                "credibility": s.get("impact", ""),
            }
            for s in (digest.get("global", []) + digest.get("india", []))
        ],
    }
    run_id = store_run(lite_record, pipeline="lite")
    print(f"      Memory run #{run_id} stored\n")

    print("Lite pipeline complete.")
    print(f"Dashboard: https://vigneshbhaskarraj.github.io/ai-digest/lite.html\n")


if __name__ == "__main__":
    run()
