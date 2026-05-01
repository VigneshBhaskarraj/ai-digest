"""
fetch_tn_news.py
Pulls Tamil Nadu-specific innovation, policy, startup, and community news.
Uses a 7-day window because TN-specific coverage is sparser than global.
Sources span government, startup media, college cells, startup clubs, and
South India regional tech press.
"""

import os
import re
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict

USER_AGENT = "TN-Innovation-Digest/1.0 (Research aggregator; contact: pixerp@yahoo.com)"

# ─────────────────────────────────────────────────────────────────────────────
# Sources — tiered: TN-dedicated (low relevance bar) vs. national (higher bar)
# ─────────────────────────────────────────────────────────────────────────────
TN_DEDICATED_SOURCES = {
    # These are South India / TN-focused — any innovation/tech story qualifies
    "The Hindu (Tech)":         "https://www.thehindu.com/sci-tech/?service=rss",
    "The Hindu Business":       "https://www.thehindubusinessline.com/feeder/default.rss",
    "DT Next":                  "https://www.dtnext.in/rss",
    "New Indian Express TN":    "https://www.newindianexpress.com/states/tamil-nadu/rssfeed/?id=168",
    "Dinamani Business":        "https://www.dinamani.com/business/rss",
    "Chennai Online":           "https://www.chennaionline.com/rss",
}

NATIONAL_SOURCES = {
    # National sources — need explicit TN/Chennai mention to qualify
    "YourStory":                "https://yourstory.com/feed",
    "Inc42":                    "https://inc42.com/feed/",
    "Entrackr":                 "https://entrackr.com/feed/",
    "ET Startups":              "https://economictimes.indiatimes.com/tech/startups/rssfeeds/78570550.cms",
    "ET Tech":                  "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "Medianama":                "https://www.medianama.com/feed/",
    "VCCircle":                 "https://www.vccircle.com/feed",
    "TechCircle":               "https://techcircle.vccircle.com/feed",
    "Livemint Tech":            "https://www.livemint.com/rss/technology",
    "TechCrunch India":         "https://techcrunch.com/tag/india/feed/",
    "NASSCOM":                  "https://nasscom.in/feed",
    "Business Standard Tech":   "https://www.business-standard.com/rss/technology-108.rss",
}

INSTITUTION_SOURCES = {
    # Research and startup ecosystem institutions
    "PIB Chennai":              "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "DST India":                "https://dst.gov.in/rss.xml",
    "Startup India Blog":       "https://www.startupindia.gov.in/content/sih/en/news.html",
}

# ─────────────────────────────────────────────────────────────────────────────
# Keywords
# ─────────────────────────────────────────────────────────────────────────────

# Explicit TN geography
TN_GEOGRAPHY = [
    "tamil nadu", "tamilnadu", "chennai", "coimbatore", "madurai", "trichy",
    "tiruchirappalli", "tirunelveli", "salem", "erode", "tirupur", "vellore",
    "thanjavur", "cuddalore", "puducherry", "pondicherry", "karur",
    "dindigul", "namakkal", "dharmapuri",
]

# TN institutions and orgs
TN_INSTITUTIONS = [
    "iit madras", "iitm", "iit-m", "anna university", "nit trichy", "nit-t",
    "psg tech", "ssn college", "srm university", "sastra", "amrita chennai",
    "vit vellore", "ceg anna university", "tidel park", "sipcot",
    "startuptn", "startup tn", "tansim", "tnega", "iitm pravartak",
    "iitm research park", "anna university bic", "psg science tech",
    "tie chennai", "tie-chennai", "nasscom 10000", "nasscom chennai",
    "cii southern", "cii-sr", "ficci tamilnadu", "assocham south",
    "tvs group", "ashok leyland", "la&t chennai", "zoho", "freshworks",
    "chargebee", "kissflow", "zynga india chennai", "rtcamp",
]

# Innovation / tech / startup keywords (any sector)
INNOVATION_KEYWORDS = [
    "startup", "innovation", "incubat", "accelerat", "funding", "investment",
    "artificial intelligence", "machine learning", "ai", "deep learning",
    "technology", "tech", "digital", "software", "platform", "saas",
    "semiconductor", "electronics", "ev", "electric vehicle", "battery",
    "aerospace", "defense", "drone", "space", "satellite",
    "medtech", "healthtech", "agritech", "fintech", "edtech", "cleantech",
    "robotics", "automation", "iot", "data center", "cloud",
    "policy", "scheme", "incentive", "mission", "hub", "park", "zone",
    "research", "r&d", "patent", "spinoff", "spin-off",
    "venture", "vc", "angel", "series a", "seed round", "grant",
    "hackathon", "demo day", "pitch", "cohort", "fellowship",
    "e-cell", "entrepreneurship cell", "founder", "co-founder",
    "manufacturing", "industry 4.0", "make in india",
    "unicorn", "soonicorn", "yc batch", "y combinator",
    "gcc", "global capability center", "gdc",
]


def is_relevant_tn_dedicated(title: str, summary: str) -> bool:
    """For TN-dedicated sources — require EITHER geography OR institution."""
    text = (title + " " + summary).lower()
    has_geography = any(kw in text for kw in TN_GEOGRAPHY)
    has_institution = any(kw in text for kw in TN_INSTITUTIONS)
    has_innovation = any(kw in text for kw in INNOVATION_KEYWORDS)
    # Accept if (geo or institution) AND has at least a light innovation angle
    return (has_geography or has_institution) and has_innovation


def is_relevant_national(title: str, summary: str) -> bool:
    """For national sources — require TN geography AND innovation."""
    text = (title + " " + summary).lower()
    has_tn = any(kw in text for kw in TN_GEOGRAPHY) or any(kw in text for kw in TN_INSTITUTIONS)
    has_innovation = any(kw in text for kw in INNOVATION_KEYWORDS)
    return has_tn and has_innovation


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def categorize(source: str, title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    if any(w in text for w in ["raised", "funding", "series a", "series b", "seed", "crore", "million", "valuation", "investment round", "venture"]):
        return "Startup Funding"
    if any(w in text for w in ["hackathon", "demo day", "pitch", "cohort", "fellowship", "bootcamp", "meetup", "e-cell", "entrepreneurship cell", "tie ", "nasscom 10000", "accelerat", "incubat", "yc batch"]):
        return "Startup Club & Events"
    if any(w in text for w in ["policy", "government", "scheme", "mission", "incentive", "ministry", "regulation", "initiative", "budget", "cabinet", "tidel", "sipcot", "tansim"]):
        return "Policy & Incentives"
    if any(w in text for w in ["iit madras", "anna university", "iitm", "research", "r&d", "lab", "patent", "spinoff", "spin-off"]):
        return "Research & Innovation"
    if any(w in text for w in ["launch", "founded", "new startup", "announced"]):
        return "New Startup"
    if any(w in text for w in ["gcc", "global capability center", "talent", "hiring", "jobs", "workforce"]):
        return "Talent & GCC"
    return "General"


def fetch_feed(name: str, url: str, max_age_hours: int, dedicated: bool) -> List[Dict]:
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

    relevance_fn = is_relevant_tn_dedicated if dedicated else is_relevant_national

    for entry in feed.entries[:40]:
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
            if not relevance_fn(title, summary):
                continue

            articles.append({
                "title":     title,
                "summary":   summary[:700],
                "url":       entry.get("link", ""),
                "source":    name,
                "published": pub_dt.strftime("%Y-%m-%d"),
                "category":  categorize(name, title, summary),
            })
        except Exception:
            continue

    return articles


def fetch_all_tn(max_age_hours: int = 168) -> List[Dict]:
    """
    Fetch from all TN sources with a 7-day default window.
    Deduplicates by title; returns sorted newest-first.
    """
    all_articles: List[Dict] = []
    seen_titles: set = set()

    # Fetch TN-dedicated sources (lower bar)
    for name, url in TN_DEDICATED_SOURCES.items():
        for a in fetch_feed(name, url, max_age_hours, dedicated=True):
            key = a["title"].lower()[:80]
            if key not in seen_titles:
                seen_titles.add(key)
                all_articles.append(a)

    # Fetch national sources (higher bar — needs explicit TN mention)
    for name, url in NATIONAL_SOURCES.items():
        for a in fetch_feed(name, url, max_age_hours, dedicated=False):
            key = a["title"].lower()[:80]
            if key not in seen_titles:
                seen_titles.add(key)
                all_articles.append(a)

    # Fetch institution sources
    for name, url in INSTITUTION_SOURCES.items():
        for a in fetch_feed(name, url, max_age_hours, dedicated=False):
            key = a["title"].lower()[:80]
            if key not in seen_titles:
                seen_titles.add(key)
                all_articles.append(a)

    all_articles.sort(key=lambda x: x["published"], reverse=True)

    # Category breakdown for logging
    from collections import Counter
    cats = Counter(a["category"] for a in all_articles)
    print(f"[TN Fetch] {len(all_articles)} articles across {len(seen_titles)} unique titles")
    for cat, cnt in cats.most_common():
        print(f"           {cat}: {cnt}")

    return all_articles


if __name__ == "__main__":
    articles = fetch_all_tn(max_age_hours=168)
    for a in articles[:15]:
        print(f"[{a['category']}] {a['source']}: {a['title'][:80]}")
