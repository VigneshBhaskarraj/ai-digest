"""
main.py
Orchestrates the full AI Digest pipeline:
  1. Fetch news from all sources
  2. Summarize with Claude API
  3. Render HTML dashboard
  4. Save to docs/index.html (GitHub Pages)

Run manually:
  python src/main.py --session morning
  python src/main.py --session evening
"""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_news import fetch_all
from summarize import summarize_articles
from render_html import render_html, save_dashboard


def run(session: str = "morning"):
    session_label = "Morning" if session == "morning" else "Evening"
    max_age = 12

    print(f"\n{'='*50}")
    print(f"  AI Digest Pipeline — {session_label} Edition")
    print(f"{'='*50}\n")

    print("[1/3] Fetching news...")
    articles = fetch_all(max_age_hours=max_age)
    print(f"      {len(articles)} articles fetched\n")

    if not articles:
        print("No articles found. Exiting.")
        sys.exit(0)

    print("[2/3] Summarizing with Claude API...")
    digest = summarize_articles(articles, session_label)
    top_count   = len(digest.get("top_stories", []))
    quick_count = len(digest.get("quick_hits", []))
    print(f"      {top_count} top stories, {quick_count} quick hits\n")

    print("[3/3] Rendering HTML dashboard...")
    html = render_html(digest, session_label)

    output_path = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "docs",
        "index.html"
    )
    save_dashboard(html, output_path)
    print(f"      Saved -> {output_path}\n")

    print("Pipeline complete.")
    print(f"Dashboard: https://vigneshbhaskarraj.github.io/ai-digest\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Digest Pipeline")
    parser.add_argument(
        "--session",
        choices=["morning", "evening"],
        default="morning",
    )
    args = parser.parse_args()
    run(args.session)
