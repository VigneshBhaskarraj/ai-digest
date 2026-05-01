"""
fetch_tn_news.py
Pulls Tamil Nadu-specific innovation, policy, startup, and tech news from RSS
feeds and curated sources. Focuses on: TN government initiatives, startup
ecosystem, innovation sectors, policies/incentives, and opportunity mapping.
"""

import os
import re
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict

USER_AGENT = "TN-Innovation-Digest/1.0 (Research aggregator; contact: pixerp@yahoo.com)"

# ── TN & South India-focused RSS Sources ─────────────────────────────────────
RSS_FEEDS = {
    # TN Government & Policy
    "TN e-Governance":          "https://tnega.tn.gov.in/rss",
    "PIB Chennai":               "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "MeitY (PIB)":              "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",

    # Chennai / TN Tech & Startup Media
    "YourStory":                "https://yourstory.com/feed",
    "Inc42":                    "https://inc42.com/feed/",
    "ET Startups":              "https://economictimes.indiatimes.com/tech/startups/rssfeeds/78570550.cms",
    "ET Tech":                  "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "Medianama":                "https://www.medianama.com/feed/",
    "Entrackr":                 "https://entrackr.com/feed/",
    "The Hindu BusinessLine":   "https://www.thehindubusinessline.com/feeder/default.rss",
    "The Hindu Tech":           "https://www.thehindu.com/sci-tech/?service=rss",
    "Livemint Tech":            "https://www.livemint.com/rss/technology",
    "NASSCOM":                  "https://nasscom.in/feed",

    # Global with India/TN coverage
    "TechCrunch India":         "https://techcrunch.com/tag/india/feed/",
    "VCCircle":                 "https://www.vccircle.com/feed",
    "TechCircle":               "https://techcircle.vccircle.com/feed",
}

# Keywords to identify TN relevance
TN_KEYWORDS = [
    "tamil nadu", "chennai", "coimbatore", "madurai", "trichy", "tirunelveli",
    "tidel park", "sipcot", "tansim", "startuptn", "tn government",
    "tamilnadu", "tn state", "anna university", "iit madras", "nit trichy",
    "guide program", "iitm research park", "iitm pravartak", "cii southern",
    "iit-m", "iitm", "amrita", "vit vellore", "ssn college",
    "south india", "southern india",
]

# Keywords for AI/innovation relevance
INNOVATION_KEYWORDS = [
    "artificial intelligence", "machine learning", "ai startup", "deep learning",
    "innovation", "startup", "incubat", "accelerat", "funding", "investment",
    "technology", "digital", "semiconductor", "electronics", "ev", "electric vehicle",
    "aerospace", "defense tech", "medtech", "agritech", "fintech", "edtech",
    "policy", "incentive", "scheme", "mission", "hub", "park", "zone",
    "research", "r&d", "patent", "ipr", "manufacturing", "industry 4.0",
    "data center", "cloud", "iot", "robotics", "automation", "drone",
    "cleantech", "greentech", "biotech", "healthtech", "spacetech",
    "venture capital", "vc", "angel", "series a", "seed round",
]


def is_relevant(title: str, summary: str) -> bool:
    """Check if article is relevant to TN innovation ecosystem."""
    text = (title + " " + summary).lower()
    has_tn = any(kw in text for kw in TN_KEYWORDS)
    has_innovation = any(kw in text for kw in INNOVATION_KEYWORDS)
    # Must have TN connection + innovation/tech relevance
    return has_tn and has_innovation


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def categorize(source: str, title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    if any(w in text for w in ["policy", "government", "scheme", "mission", "incentive", "meity", "nasscom", "ministry", "regulation", "initiative", "budget", "cabinet"]):
        return "Policy & Incentives"
    if any(w in text for w in ["raised", "funding", "series a", "series b", "seed", "crore", "million", "valuation", "round", "investment", "vc ", "venture"]):
        return "Startup Funding"
    if any(w in text for w in ["launch", "new startup", "founded", "incubat", "accelerat", "cohort", "yc ", "y combinator", "founded"]):
        return "New Startup"
    if any(w in text for w in ["iit madras", "anna university", "iitm", "research", "r&d", "lab", "institute", "university", "innovation center"]):
        return "Research & Innovation"
    if any(w in text for w in ["semiconductor", "electronics", "ev", "electric vehicle", "aerospace", "defense", "manufacture", "industry"]):
        return "Industry & Manufacturing"
    if any(w in text for w in ["opportunity", "sector", "trend", "market", "growth", "potential", "hub", "ecosystem"]):
        return "Ecosystem & Opportunities"
    return "General"


def fetch_feed(name: str, url: str, max_age_hours: int = 72) -> List[Dict]:
    """Parse a single RSS feed and return recent relevant articles."""
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception:
        try:
            feed = feedparser.parse(url)
        except Exception:
            return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    articles = []

    for entry in feed.entries[:30]:
        try:
            pub_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
            if pub_parsed:
                pub_dt = datetime(*pub_parsed[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue
            else:
                pub_dt = datetime.now(timezone.utc)

            title   = strip_html(entry.get("title", "")).strip()
            summary = strip_html(
                entry.get("summary", "") or entry.get("description", "")
            ).strip()

            if not title:
                continue
            if not is_relevant(title, summary):
                continue

            articles.append({
                "title":     title,
                "summary":   summary[:600],
                "url":       entry.get("link", ""),
                "source":    name,
                "published": pub_dt.strftime("%Y-%m-%d"),
                "category":  categorize(name, title, summary),
            })
        except Exception:
            continue

    return articles


def fetch_all_tn(max_age_hours: int = 72) -> List[Dict]:
    """Fetch from all TN sources; deduplicate by title; return sorted."""
    all_articles: List[Dict] = []
    seen_titles: set = set()

    for name, url in RSS_FEEDS.items():
        articles = fetch_feed(name, url, max_age_hours)
        for a in articles:
            key = a["title"].lower()[:80]
            if key not in seen_titles:
                seen_titles.add(key)
                all_articles.append(a)

    # Sort by published date descending
    all_articles.sort(key=lambda x: x["published"], reverse=True)
    print(f"[TN Fetch] {len(all_articles)} relevant TN innovation articles found")
    return all_articles


if __name__ == "__main__":
    articles = fetch_all_tn(max_age_hours=72)
    for a in articles[:10]:
        print(f"[{a['category']}] {a['source']}: {a['title'][:80]}")
