"""
fetch_news.py
Pulls AI news from RSS feeds — lab blogs, newsletters, Reddit, arXiv,
Hacker News, and Papers With Code.

Key improvements over v1:
- Custom User-Agent so Reddit/HN don't silently block requests
- Wider default window (24h) with auto-fallback to 48h if thin
- AI relevance filter on general-interest sources
- More sources: xAI, Cohere, arXiv CS.CL, Papers With Code, HN, Last Week in AI
- Relevance scoring to surface the best articles first
"""

import os
import re
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")

# Custom User-Agent — Reddit and HN block the default feedparser UA
HEADERS = {"User-Agent": "ai-digest-bot/1.0 (github.com/VigneshBhaskarraj/ai-digest)"}

# ── RSS Sources ───────────────────────────────────────────────────────────────
RSS_FEEDS = {
    # Lab Blogs
    "Anthropic Blog":               "https://www.anthropic.com/rss.xml",
    "OpenAI Blog":                  "https://openai.com/blog/rss.xml",
    "Google DeepMind":              "https://deepmind.google/blog/rss.xml",
    "HuggingFace Blog":             "https://huggingface.co/blog/feed.xml",
    "Mistral AI":                   "https://mistral.ai/news/rss.xml",
    "Meta AI":                      "https://ai.meta.com/blog/feed/",
    "xAI":                          "https://x.ai/blog/rss.xml",
    "Cohere Blog":                  "https://cohere.com/blog/rss",

    # Tech News — AI-specific feeds where available
    "TechCrunch AI":                "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI":                 "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "VentureBeat AI":               "https://venturebeat.com/category/ai/feed/",
    "Wired AI":                     "https://www.wired.com/feed/tag/ai/latest/rss",
    "Ars Technica":                 "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "MIT Tech Review":              "https://www.technologyreview.com/feed/",

    # Newsletters
    "The Rundown AI":               "https://www.therundown.ai/feed",
    "Ben's Bites":                  "https://bensbites.beehiiv.com/feed",
    "Import AI":                    "https://jack-clark.net/feed/",
    "Simon Willison":               "https://simonwillison.net/atom/everything/",
    "Last Week in AI":              "https://lastweekin.ai/feed",
    "The Batch (DeepLearning.AI)":  "https://www.deeplearning.ai/the-batch/feed/",

    # Research
    "arXiv CS.AI":                  "https://rss.arxiv.org/rss/cs.AI",
    "arXiv CS.LG":                  "https://rss.arxiv.org/rss/cs.LG",
    "arXiv CS.CL":                  "https://rss.arxiv.org/rss/cs.CL",
    "Papers With Code":             "https://paperswithcode.com/latest.rss",

    # Community
    "r/LocalLLaMA":                 "https://www.reddit.com/r/LocalLLaMA/.rss",
    "r/MachineLearning":            "https://www.reddit.com/r/MachineLearning/.rss",
    "r/artificial":                 "https://www.reddit.com/r/artificial/.rss",
    "Hacker News (AI)":             "https://hnrss.org/newest?q=LLM+AI+machine+learning&count=15",
}

# Per-source article caps
SOURCE_CAPS = {
    "arXiv CS.AI": 12,
    "arXiv CS.LG": 8,
    "arXiv CS.CL": 8,
    "Papers With Code": 8,
    "r/LocalLLaMA": 10,
    "r/MachineLearning": 8,
    "r/artificial": 6,
    "Hacker News (AI)": 10,
}
DEFAULT_CAP = 8

# Sources that publish non-AI content — require keyword match
NEEDS_AI_FILTER = {
    "Ars Technica", "MIT Tech Review", "Simon Willison",
    "Hacker News (AI)", "r/artificial",
}

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "gemini", "llama", "mistral",
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "language model", "chatbot", "generative",
    "transformer", "openai", "anthropic", "deepmind", "hugging face",
    "nvidia", "gpu", "inference", "fine-tun", "agent", "embedding",
    "foundation model", "diffusion", "multimodal", "benchmark",
    "rag", "reinforcement learning", "computer vision", "nlp",
]

HIGH_SIGNAL_SOURCES = {
    "Anthropic Blog", "OpenAI Blog", "Google DeepMind",
    "HuggingFace Blog", "Mistral AI", "Meta AI", "xAI",
    "Import AI", "The Batch (DeepLearning.AI)", "TechCrunch AI",
}


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def is_ai_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def relevance_score(article: Dict) -> int:
    """Higher = more important. Used to rank within Claude's input."""
    score = 0
    if article["source"] in HIGH_SIGNAL_SOURCES:
        score += 10
    text = (article["title"] + " " + article["summary"]).lower()
    high_signal_words = ["release", "launch", "announce", "raises", "open source", "breakthrough", "beats", "surpasses", "new model"]
    score += sum(2 for w in high_signal_words if w in text)
    return score


def fetch_rss_articles(max_age_hours: int = 24) -> List[Dict]:
    """Fetch articles from all RSS feeds published within max_age_hours."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    for source, url in RSS_FEEDS.items():
        cap = SOURCE_CAPS.get(source, DEFAULT_CAP)
        try:
            # Pass custom headers via feedparser's request_headers
            feed = feedparser.parse(url, request_headers=HEADERS)
            count = 0
            for entry in feed.entries:
                if count >= cap:
                    break

                # Parse published date
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                if published and published < cutoff:
                    continue

                title   = entry.get("title", "Untitled")[:200]
                summary = strip_html(
                    entry.get("summary", "") or entry.get("description", "")
                )[:500]

                # For general sources, filter out non-AI articles
                if source in NEEDS_AI_FILTER and not is_ai_relevant(title, summary):
                    continue

                articles.append({
                    "title":     title,
                    "url":       entry.get("link", ""),
                    "summary":   summary,
                    "source":    source,
                    "published": published.strftime("%Y-%m-%d %H:%M UTC") if published else "Unknown",
                    "category":  categorize(source),
                })
                count += 1

        except Exception as e:
            print(f"[RSS] Failed {source}: {e}")

    return articles


def fetch_newsapi_articles(max_age_hours: int = 24) -> List[Dict]:
    """Fetch AI news from NewsAPI.org (only if key is set)."""
    if not NEWSAPI_KEY:
        return []

    NEWSAPI_QUERIES = [
        "LLM release", "AI model launch",
        "GPT OR Claude OR Gemini OR Llama",
        "AI agent tool", "artificial intelligence funding",
    ]

    articles = []
    from_time = (datetime.utcnow() - timedelta(hours=max_age_hours)).strftime("%Y-%m-%dT%H:%M:%S")

    for query in NEWSAPI_QUERIES[:3]:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q":        query,
                    "from":     from_time,
                    "sortBy":   "publishedAt",
                    "language": "en",
                    "pageSize": 5,
                    "apiKey":   NEWSAPI_KEY,
                },
                timeout=10,
                headers=HEADERS,
            )
            data = resp.json()
            for a in data.get("articles", []):
                articles.append({
                    "title":     a.get("title", "")[:200],
                    "url":       a.get("url", ""),
                    "summary":   (a.get("description") or "")[:500],
                    "source":    a.get("source", {}).get("name", "NewsAPI"),
                    "published": a.get("publishedAt", "")[:16].replace("T", " ") + " UTC",
                    "category":  "Industry News",
                })
        except Exception as e:
            print(f"[NewsAPI] Failed '{query}': {e}")

    return articles


def categorize(source: str) -> str:
    cats = {
        "Model Releases":   ["HuggingFace", "Anthropic", "OpenAI", "DeepMind", "Mistral", "Meta AI", "xAI", "Cohere"],
        "Research":         ["arXiv", "Import AI", "MIT Tech Review", "Papers With Code", "The Batch"],
        "Tools & Products": ["Ben's Bites", "The Rundown", "Simon Willison", "VentureBeat", "Last Week"],
        "Community":        ["r/LocalLLaMA", "r/MachineLearning", "r/artificial", "Hacker News"],
        "Industry News":    ["TechCrunch", "The Verge", "Ars Technica", "Wired"],
    }
    for cat, keywords in cats.items():
        if any(k.lower() in source.lower() for k in keywords):
            return cat
    return "Industry News"


def deduplicate(articles: List[Dict]) -> List[Dict]:
    seen, unique = set(), []
    for a in articles:
        key = a["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def fetch_all(max_age_hours: int = 24) -> List[Dict]:
    """Master fetch: RSS + NewsAPI, deduped and sorted by relevance."""
    articles = fetch_rss_articles(max_age_hours) + fetch_newsapi_articles(max_age_hours)
    articles = deduplicate(articles)

    # Auto-fallback: if too few articles, widen the window
    if len(articles) < 15:
        print(f"[Fetch] Only {len(articles)} articles in {max_age_hours}h — widening to 48h")
        articles = fetch_rss_articles(48) + fetch_newsapi_articles(48)
        articles = deduplicate(articles)

    # Sort by relevance score first, then recency
    articles.sort(key=lambda a: (
        relevance_score(a),
        a["published"] if a["published"] != "Unknown" else "0000"
    ), reverse=True)

    print(f"[Fetch] {len(articles)} articles ready ({max_age_hours}h window)")
    return articles


if __name__ == "__main__":
    items = fetch_all(max_age_hours=24)
    print(f"\nFetched {len(items)} articles")
    for item in items[:10]:
        print(f"  [{item['category']}] {item['title'][:70]} — {item['source']}")
