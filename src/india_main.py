"""
india_main.py
Orchestrates the India AI Pulse pipeline:
  1. Fetch India AI investment & startup news
  2. Summarize with Claude API (India-focused prompt)
  3. Render HTML dashboard
  4. Save to docs/india.html (GitHub Pages)

Run manually:
  python src/india_main.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_india_news import fetch_all_india
from summarize_india import summarize_india_articles
from render_india_html import render_india_html, save_india_dashboard
from memory import store_run, get_recent_context


def run():
    print(f"\n{'='*50}")
    print(f"  India AI Pulse Pipeline")
    print(f"{'='*50}\n")

    print("[1/4] Fetching India AI news...")
    articles = fetch_all_india(max_age_hours=24)
    print(f"      {len(articles)} articles fetched\n")

    if not articles:
        print("No India AI articles found. Saving empty digest.")

    print("[2/4] Loading memory context (last 14 days)...")
    memory_context = get_recent_context(days=14, pipeline="india")
    if memory_context:
        print(f"      Memory context loaded ({len(memory_context)} chars)\n")
    else:
        print(f"      No prior history yet (first run)\n")

    print("[3/4] Summarizing with Claude API...")
    digest = summarize_india_articles(articles, memory_context=memory_context)
    funding_count = len(digest.get("funding_rounds", []))
    startup_count = len(digest.get("new_startups", []))
    print(f"      {funding_count} funding rounds, {startup_count} new startups\n")

    print("[4/4] Rendering India HTML dashboard & storing memory...")
    html = render_india_html(digest)

    output_path = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "docs",
        "india.html"
    )
    save_india_dashboard(html, output_path)
    print(f"      Saved → {output_path}")

    run_id = store_run(digest, pipeline="india")
    print(f"      Memory run #{run_id} stored\n")

    print("India pipeline complete.")
    print(f"Dashboard: https://vigneshbhaskarraj.github.io/ai-digest/india.html\n")


if __name__ == "__main__":
    run()
