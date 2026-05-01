"""
fetch_news.py
Pulls AI news from NewsAPI, RSS feeds (HuggingFace, OpenAI, Anthropic, labs),
Substack newsletters, Reddit, and arXiv.
"""

import os
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")

# ── RSS Sources ──────────────────────────────────────────────────────────────
RSS_FEEDS = {
    # Lab Blogs (direct from source)
    "Anthropic Blog":       "https://www.anthropic.com/rss.xml",
    "OpenAI Blog":          "https://openai.com/blog/rss.xml",
    "Google DeepMind":      "https://deepmind.google/blog/rss.xml",
    "HuggingFace Blog":     "https://huggingface.co/blog/feed.xml",
    "Mistral AI":           "https://mistral.ai/news/rss.xml",
    "Meta AI":              "https://ai.meta.com/blog/feed/",

    # Top Tech News
    "TechCrunch AI":        "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI":         "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "Ars Technica AI":      "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "VentureBeat AI":       "https://venturebeat.com/category/ai/feed/",
    "Wired AI":             "https://www.wired.com/feed/tag/ai/latest/rss",
    "MIT Tech Review AI":   "https://www.technologyreview.com/feed/",
    "Techmeme":             "https://www.techmeme.com/feed.xml",

    # Newsletters via RSS
    "The Rundown AI":       "https://www.therundown.ai/feed",
    "Ben's Bites":          "https://bensbites.beehiiv.com/feed",
    "Import AI":            "https://jack-clark.net/feed/",
    "Simon Willison":       "https://simonwillison.net/atom/everything/",

    # Research
    "arXiv CS.AI":          "https://rss.arxiv.org/rss/cs.AI",
    "arXiv CS.LG":          "https://rss.arxiv.org/rss/cs.LG",

    # Community
    "r/LocalLLaMA":         "https://www.reddit.com/r/LocalLLaMA/.rss",
    "r/MachineLearning":    "https://www.reddit.com/r/MachineLearning/.rss",
}

# NewsAPI query terms
NEWSAPI_QUERIES = [
    "LLM release",
    "AI model launch",
    "artificial intelligence announcement",
    "GPT OR Claude OR Gemini OR Llama release",
    "AI agent tool",
]

def fetch_rss_articles(max_age_hours: int = 12) -> List[Dict]:
    """Fetch articles from all RSS feeds published within max_age_hours."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:  # cap per source
                # Parse published date
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                if published and published < cutoff:
                    continue  # skip old entries

                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary[:400]
                elif hasattr(entry, "description"):
                    summary = entry.description[:400]

                # Strip HTML tags simply
                import re
                summary = re.sub(r"<[^>]+>", "", summary).strip()

                articles.append({
                    "title":     entry.get("title", "Untitled")[:200],
                    "url":       entry.get("link", ""),
                    "summary":   summary,
                    "source":    source,
                    "published": published.strftime("%Y-%m-%d %H:%M UTC") if published else "Unknown",
                    "category":  categorize(source),
                })
        except Exception as e:
            print(f"[RSS] Failed {source}: {e}")

    return articles


def fetch_newsapi_articles(max_age_hours: int = 12) -> List[Dict]:
    """Fetch AI news from NewsAPI.org."""
    if not NEWSAPI_KEY:
        print("[NewsAPI] No API key set, skipping.")
        return []

    articles = []
    from_time = (datetime.utcnow() - timedelta(hours=max_age_hours)).strftime("%Y-%m-%dT%H:%M:%S")

    for query in NEWSAPI_QUERIES[:3]:  # limit to 3 queries to conserve free-tier quota
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q":          query,
                    "from":       from_time,
                    "sortBy":     "publishedAt",
                    "language":   "en",
                    "pageSize":   5,
                    "apiKey":     NEWSAPI_KEY,
                },
                timeout=10,
            )
            data = resp.json()
            for a in data.get("articles", []):
                articles.append({
                    "title":     a.get("title", "")[:200],
                    "url":       a.get("url", ""),
                    "summary":   (a.get("description") or "")[:400],
                    "source":    a.get("source", {}).get("name", "NewsAPI"),
                    "published": a.get("publishedAt", "")[:16].replace("T", " ") + " UTC",
                    "category":  "Industry News",
                })
        except Exception as e:
            print(f"[NewsAPI] Failed query '{query}': {e}")

    return articles


def categorize(source: str) -> str:
    """Map source name to a dashboard category."""
    cats = {
        "Model Releases":   ["HuggingFace", "Anthropic", "OpenAI", "DeepMind", "Mistral", "Meta AI"],
        "Research":         ["arXiv", "Import AI", "MIT Tech Review"],
        "Tools & Products": ["Ben's Bites", "The Rundown", "Simon Willison", "VentureBeat"],
        "Community":        ["r/LocalLLaMA", "r/MachineLearning"],
        "Industry News":    ["TechCrunch", "The Verge", "Ars Technica", "Wired", "Techmeme"],
    }
    for cat, keywords in cats.items():
        if any(k.lower() in source.lower() for k in keywords):
            return cat
    return "Industry News"


def deduplicate(articles: List[Dict]) -> List[Dict]:
    """Remove near-duplicate titles."""
    seen, unique = set(), []
    for a in articles:
        key = a["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def fetch_all(max_age_hours: int = 12) -> List[Dict]:
    """Master fetch: RSS + NewsAPI, deduped and sorted."""
    all_articles = fetch_rss_articles(max_age_hours) + fetch_newsapi_articles(max_age_hours)
    all_articles = deduplicate(all_articles)
    # Sort: newest first (articles with known dates first)
    def sort_key(a):
        return a["published"] if a["published"] != "Unknown" else "0000"
    all_articles.sort(key=sort_key, reverse=True)
    return all_articles


if __name__ == "__main__":
    items = fetch_all(max_age_hours=24)
    print(f"Fetched {len(items)} articles")
    for item in items[:5]:
        print(f"  [{item['category']}] {item['title']} — {item['source']}")
