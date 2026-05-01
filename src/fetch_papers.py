"""
fetch_papers.py
Fetches the latest AI research papers from arXiv, Hugging Face Daily Papers,
and Papers With Code. Returns structured data for the whitepaper section.
"""

import re
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict

HEADERS = {"User-Agent": "ai-digest-bot/1.0 (github.com/VigneshBhaskarraj/ai-digest)"}

# arXiv categories to pull from
ARXIV_FEEDS = {
    "arXiv CS.AI": "https://rss.arxiv.org/rss/cs.AI",
    "arXiv CS.LG": "https://rss.arxiv.org/rss/cs.LG",
    "arXiv CS.CL": "https://rss.arxiv.org/rss/cs.CL",
}

# Hugging Face Daily Papers API
HF_PAPERS_URL = "https://huggingface.co/api/daily_papers"

# Papers with Code latest
PWC_FEED = "https://paperswithcode.com/latest.rss"

# High-signal keywords for paper relevance
PAPER_KEYWORDS = [
    "llm", "large language model", "language model", "transformer",
    "agent", "reasoning", "chain-of-thought", "rlhf", "instruction tuning",
    "fine-tuning", "prompt", "alignment", "safety", "hallucination",
    "retrieval", "rag", "multimodal", "vision language", "diffusion",
    "benchmark", "evaluation", "efficient", "quantization", "inference",
    "attention", "context window", "long context", "code generation",
    "tool use", "function calling", "agentic", "foundation model",
]


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def is_relevant_paper(title: str, abstract: str) -> bool:
    text = (title + " " + abstract).lower()
    return any(kw in text for kw in PAPER_KEYWORDS)


def fetch_arxiv_papers(max_age_hours: int = 48, cap_per_feed: int = 10) -> List[Dict]:
    papers = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    for source, url in ARXIV_FEEDS.items():
        try:
            feed = feedparser.parse(url, request_headers=HEADERS)
            count = 0
            for entry in feed.entries:
                if count >= cap_per_feed:
                    break

                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

                title = entry.get("title", "").replace("\n", " ").strip()
                abstract = strip_html(entry.get("summary", ""))[:800]

                if not is_relevant_paper(title, abstract):
                    continue

                # Extract arXiv ID for the URL
                link = entry.get("link", "")
                arxiv_id = ""
                if "arxiv.org/abs/" in link:
                    arxiv_id = link.split("arxiv.org/abs/")[-1].strip()

                papers.append({
                    "title": title,
                    "url": link,
                    "abstract": abstract,
                    "authors": "",
                    "source": source,
                    "arxiv_id": arxiv_id,
                    "published": published.strftime("%Y-%m-%d") if published else "Unknown",
                    "tags": [source.replace("arXiv ", "")],
                })
                count += 1

        except Exception as e:
            print(f"[Papers] Failed {source}: {e}")

    return papers


def fetch_hf_daily_papers() -> List[Dict]:
    """Fetch Hugging Face Daily Papers — curated by the HF community."""
    papers = []
    try:
        resp = requests.get(HF_PAPERS_URL, headers=HEADERS, timeout=10)
        data = resp.json()

        for item in data[:15]:
            paper = item.get("paper", {})
            title = paper.get("title", "").strip()
            abstract = paper.get("summary", "")[:800]
            arxiv_id = paper.get("id", "")
            url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""

            authors_raw = paper.get("authors", [])
            if authors_raw:
                author_names = [a.get("name", "") for a in authors_raw[:3]]
                authors_str = ", ".join(author_names)
                if len(paper.get("authors", [])) > 3:
                    authors_str += " et al."
            else:
                authors_str = ""

            published_str = paper.get("publishedAt", "")[:10]

            papers.append({
                "title": title,
                "url": url,
                "abstract": abstract,
                "authors": authors_str,
                "source": "HF Daily Papers",
                "arxiv_id": arxiv_id,
                "published": published_str or "Unknown",
                "tags": ["HF Pick"],
                "upvotes": item.get("numComments", 0),
            })

    except Exception as e:
        print(f"[Papers] Failed HF Daily Papers: {e}")

    return papers


def fetch_pwc_papers(cap: int = 8) -> List[Dict]:
    """Fetch trending papers from Papers With Code."""
    papers = []
    try:
        feed = feedparser.parse(PWC_FEED, request_headers=HEADERS)
        for entry in feed.entries[:cap]:
            title = entry.get("title", "").strip()
            abstract = strip_html(entry.get("summary", ""))[:800]
            link = entry.get("link", "")

            if not is_relevant_paper(title, abstract):
                continue

            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            papers.append({
                "title": title,
                "url": link,
                "abstract": abstract,
                "authors": "",
                "source": "Papers With Code",
                "arxiv_id": "",
                "published": published.strftime("%Y-%m-%d") if published else "Unknown",
                "tags": ["PWC"],
            })
    except Exception as e:
        print(f"[Papers] Failed Papers With Code: {e}")

    return papers


def deduplicate_papers(papers: List[Dict]) -> List[Dict]:
    seen, unique = set(), []
    for p in papers:
        key = p["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def fetch_all_papers(max_age_hours: int = 48) -> List[Dict]:
    """Master fetch: arXiv + HF Daily Papers + Papers With Code, deduped."""
    # HF Daily Papers first (highest quality curation)
    papers = fetch_hf_daily_papers()
    papers += fetch_arxiv_papers(max_age_hours)
    papers += fetch_pwc_papers()

    papers = deduplicate_papers(papers)

    # Sort: HF picks first, then by recency
    def sort_key(p):
        hf_boost = 10 if p["source"] == "HF Daily Papers" else 0
        date_str = p["published"] if p["published"] != "Unknown" else "0000-00-00"
        return (hf_boost, date_str)

    papers.sort(key=sort_key, reverse=True)

    print(f"[Papers] {len(papers)} papers ready")
    return papers[:30]  # Cap total at 30


if __name__ == "__main__":
    items = fetch_all_papers()
    print(f"\nFetched {len(items)} papers")
    for p in items[:10]:
        print(f"  [{p['source']}] {p['title'][:70]}")
        print(f"    {p['published']} | {p['url']}")
