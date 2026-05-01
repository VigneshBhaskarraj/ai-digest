"""
tn_main.py
Orchestrates the Tamil Nadu Innovation Digest pipeline:
  1. Fetch TN innovation, policy, and startup news
  2. Summarize with Claude API (TN-focused prompt)
  3. Render HTML dashboard
  4. Save to docs/tn.html (GitHub Pages)

Run manually:
  python src/tn_main.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_tn_news import fetch_all_tn
from summarize_tn import summarize_tn_articles
from render_tn_html import render_tn_html, save_tn_dashboard


def run():
    print(f"\n{'='*50}")
    print(f"  TN Innovation Digest Pipeline")
    print(f"{'='*50}\n")

    print("[1/3] Fetching Tamil Nadu innovation news...")
    # Use 72-hour window since TN-specific coverage is sparser than global
    articles = fetch_all_tn(max_age_hours=72)
    print(f"      {len(articles)} articles fetched\n")

    print("[2/3] Summarizing with Claude API...")
    digest = summarize_tn_articles(articles)
    policy_count  = len(digest.get("policy_incentives", []))
    startup_count = len(digest.get("startup_spotlight", []))
    sector_count  = len(digest.get("sector_opportunities", []))
    print(f"      {policy_count} policy items, {startup_count} startups, {sector_count} sector opportunities\n")

    print("[3/3] Rendering TN Innovation HTML dashboard...")
    html = render_tn_html(digest)

    output_path = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "docs",
        "tn.html"
    )
    save_tn_dashboard(html, output_path)
    print(f"      Saved → {output_path}\n")

    print("TN Innovation pipeline complete.")
    print(f"Dashboard: https://vigneshbhaskarraj.github.io/ai-digest/tn.html\n")


if __name__ == "__main__":
    run()
