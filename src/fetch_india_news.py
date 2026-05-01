"""
fetch_india_news.py
Pulls India-specific AI investment, startup, and VC news from RSS feeds.
Focuses on: funding rounds, new AI startups, VC thesis trends, govt policy.
"""

import os
import re
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict

# ── India-focused RSS Sources ─────────────────────────────────────────────────
RSS_FEEDS = {
    # India Startup & Tech News
    "Inc42":                    "https://inc42.com/feed/",
    "YourStory":                "https://yourstory.com/feed",
    "Entrackr":                 "https://entrackr.com/feed/",
    "ET Startups":              "https://economictimes.indiatimes.com/tech/startups/rssfeeds/78570550.cms",
    "ET Tech":                  "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "Medianama":                "https://www.medianama.com/feed/",
    "VCCircle":                 "https://www.vccircle.com/feed",
    "TechCircle":               "https://techcircle.vccircle.com/feed",
    "FactorDaily":              "https://factordaily.com/feed/",
    "Livemint Tech":            "https://www.livemint.com/rss/technology",

    # Global sources with India coverage
    "TechCrunch India":         "https://techcrunch.com/tag/india/feed/",

    # VC & Investor Blogs
    "Blume Ventures":           "https://blume.vc/blog/feed/",
    "3one4 Capital":            "https://3one4.capital/feed/",
    "Stellaris VP":             "https://stellarisvp.com/blog/feed/",
    "Accel Noteworthy":         "https://www.accel.com/noteworthy/feed",

    # Government & Policy
    "NASSCOM":                  "https://nasscom.in/feed",
    "MeitY (PIB)":              "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
}

# Keywords to filter for AI/ML relevance
AI_KEYWORDS = [
    "artificial intelligence", "ai startup", "machine learning", "llm",
    "generative ai", "deep learning", "ai funding", "ai investment",
    "ai incubat", "ai accelerat", "venture capital", "series a", "series b",
    "seed fund", "raised", "funding round", "valuation", "unicorn",
    "ai policy", "indiaai", "nasscom", "gpu", "data center", "foundation model",
    "large language", "ai agent", "computer vision", "nlp", "robotics ai",
]

INDIA_KEYWORDS = [
    "india", "indian", "bengaluru", "bangalore", "mumbai", "delhi", "hyderabad",
    "pune", "chennai", "startup india", "iit", "iim", "nasscom", "meity",
    "rupee", "inr", "crore",
]


def is_relevant(title: str, summary: str) -> bool:
    """Check if an article is relevant to India AI/investment theme."""
    text = (title + " " + summary).lower()
    has_ai = any(kw in text for kw in AI_KEYWORDS)
    has_india = any(kw in text for kw in INDIA_KEYWORDS)
    # For India-specific sources, just require AI relevance
    # For global sources, require both AI + India
    return has_ai or has_india


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def categorize(source: str, title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    if any(w in text for w in ["raised", "funding", "series a", "series b", "seed", "crore", "million", "valuation", "round"]):
        return "Funding Round"
    if any(w in text for w in ["launch", "new startup", "founded", "incubat", "accelerat", "cohort", "yc ", "y combinator"]):
        return "New Startup / Incubation"
    if any(w in text for w in ["policy", "government", "meity", "nasscom", "indiaai", "ministry", "regulation", "mission"]):
        return "Policy & Government"
    if any(w in text for w in ["vc ", "venture", "fund", "invest", "portfolio", "thesis", "lp ", "aum"]):
        return "VC & Investment Trends"
    return "India AI News"


def fetch_india_articles(max_age_hours: int = 24) -> List[Dict]:
    """Fetch articles from all India-focused RSS feeds."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                # Parse date
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                if published and published < cutoff:
                    continue

                title = entry.get("title", "Untitled")[:200]
                summary = strip_html(
                    entry.get("summary", "") or entry.get("description", "")
                )[:500]

                if not is_relevant(title, summary):
                    continue

                articles.append({
                    "title":     title,
                    "url":       entry.get("link", ""),
                    "summary":   summary,
                    "source":    source,
                    "published": published.strftime("%Y-%m-%d %H:%M UTC") if published else "Unknown",
                    "category":  categorize(source, title, summary),
                })
        except Exception as e:
            print(f"[India RSS] Failed {source}: {e}")

    return articles


def deduplicate(articles: List[Dict]) -> List[Dict]:
    seen, unique = set(), []
    for a in articles:
        key = a["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def fetch_all_india(max_age_hours: int = 24) -> List[Dict]:
    """Master fetch for India AI digest."""
    articles = fetch_india_articles(max_age_hours)
    articles = deduplicate(articles)
    articles.sort(key=lambda a: a["published"] if a["published"] != "Unknown" else "0000", reverse=True)
    return articles


if __name__ == "__main__":
    items = fetch_all_india(max_age_hours=48)
    print(f"Fetched {len(items)} India AI articles")
    for item in items[:10]:
        print(f"  [{item['category']}] {item['title']} — {item['source']}")
