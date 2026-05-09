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
from fetch_papers import fetch_all_papers
from summarize import summarize_articles
from render_html import render_html, save_dashboard
from memory import store_run, get_recent_context


def run(session: str = "morning"):
    session_label = "Morning" if session == "morning" else "Evening"
    max_age = 24

    print(f"\n{'='*50}")
    print(f"  AI Digest Pipeline — {session_label} Edition")
    print(f"{'='*50}\n")

    print("[1/5] Fetching news...")
    articles = fetch_all(max_age_hours=max_age)
    print(f"      {len(articles)} articles fetched\n")

    if not articles:
        print("No articles found. Exiting.")
        sys.exit(0)

    print("[2/5] Fetching whitepapers...")
    papers = fetch_all_papers(max_age_hours=48)
    print(f"      {len(papers)} papers fetched\n")

    print("[3/5] Loading memory context (last 14 days)...")
    memory_context = get_recent_context(days=14, pipeline="global")
    if memory_context:
        print(f"      Memory context loaded ({len(memory_context)} chars)\n")
    else:
        print(f"      No prior history yet (first run)\n")

    print("[4/5] Summarizing with Claude API...")
    digest = summarize_articles(articles, session_label, memory_context=memory_context)
    top_count   = len(digest.get("top_stories", []))
    quick_count = len(digest.get("quick_hits", []))
    print(f"      {top_count} top stories, {quick_count} quick hits\n")

    print("[5/5] Rendering HTML dashboard & storing memory...")
    html = render_html(digest, session_label, papers=papers)

    output_path = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "docs",
        "index.html"
    )
    save_dashboard(html, output_path)
    print(f"      Saved -> {output_path}")

    run_id = store_run(digest, pipeline="global", session=session)
    print(f"      Memory run #{run_id} stored\n")

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
