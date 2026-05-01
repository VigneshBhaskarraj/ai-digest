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


def run():
    print(f"\n{'='*50}")
    print(f"  India AI Pulse Pipeline")
    print(f"{'='*50}\n")

    print("[1/3] Fetching India AI news...")
    articles = fetch_all_india(max_age_hours=24)
    print(f"      {len(articles)} articles fetched\n")

    if not articles:
        print("No India AI articles found. Saving empty digest.")

    print("[2/3] Summarizing with Claude API...")
    digest = summarize_india_articles(articles)
    funding_count = len(digest.get("funding_rounds", []))
    startup_count = len(digest.get("new_startups", []))
    print(f"      {funding_count} funding rounds, {startup_count} new startups\n")

    print("[3/3] Rendering India HTML dashboard...")
    html = render_india_html(digest)

    output_path = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "docs",
        "india.html"
    )
    save_india_dashboard(html, output_path)
    print(f"      Saved → {output_path}\n")

    print("India pipeline complete.")
    print(f"Dashboard: https://vigneshbhaskarraj.github.io/ai-digest/india.html\n")


if __name__ == "__main__":
    run()
