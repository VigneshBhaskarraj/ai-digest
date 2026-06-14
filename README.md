# ⚡ AI Digest

A self-updating AI news intelligence platform. It reads **30+ AI sources**
twice a day, runs a cheap multi-model pass to extract cross-source signals,
then uses **Claude** to synthesize a structured briefing — and publishes it as a
dark-mode dashboard on GitHub Pages. No server. No database service. Just a cron
and an API key.

**Live dashboards:**

| Edition | Link |
|---|---|
| 🌍 **Global** — the worldwide AI briefing (morning + evening) | [vigneshbhaskarraj.github.io/ai-digest](https://vigneshbhaskarraj.github.io/ai-digest) |
| 🇮🇳 **India AI Pulse** — India funding, startups & policy | [/india.html](https://vigneshbhaskarraj.github.io/ai-digest/india.html) |
| 🌟 **Tamil Nadu Innovation** — TN deeptech, policy & ecosystem | [/tn.html](https://vigneshbhaskarraj.github.io/ai-digest/tn.html) |
| ⚡ **Lite** — fast flip-card read for mobile | [/lite.html](https://vigneshbhaskarraj.github.io/ai-digest/lite.html) |

Installable as a PWA — "Add to Home Screen" on any edition.

---

## What makes it more than a feed-summarizer

Most "AI news" tools pipe one RSS feed through a model and call it a day.
AI Digest is a **cost-aware pipeline with memory**:

```
30+ RSS sources  ──►  fetch + AI-relevance filter + relevance ranking
        │
        ▼
[ Signal extraction ]   cheap/fast model via OpenRouter reads ~35 articles and
        │               returns a structured signal graph: entities, corroborated
        │               claims (2+ sources), cross-source tensions, emerging patterns
        ▼
[ Temporal memory ]     last 14 days of headlines, surges & entities pulled from a
        │               local SQLite store and injected as context
        ▼
[ Claude synthesis ]    reasons over the dense signal graph + history instead of
        │               raw text → "connect the dots" insights, not just summaries
        ▼
[ Render + persist ]    dark-mode HTML dashboard → docs/ (GitHub Pages)
                        run stored back into memory for tomorrow
```

Why this design:

- **Cheap models do the cheap work.** A small model extracts structured facts from
  dozens of articles in seconds; Claude only pays for the expensive *reasoning*.
- **It remembers.** Because every run is persisted, the digest can say *"third
  consecutive day X has surfaced"* or *"this builds on last week's Y"* — continuity
  a stateless summarizer can't produce.
- **Cross-source corroboration.** Claims seen in 2+ sources are marked
  high-confidence; single-source claims are flagged low. Genuine disagreements are
  surfaced as "tensions" rather than averaged away.

---

## Editions & schedule

| Pipeline | Entry point | Runs | Output |
|---|---|---|---|
| Global AI Digest | `src/main.py` | Morning **and** evening | `docs/index.html` |
| India AI Pulse | `src/india_main.py` | Morning | `docs/india.html` |
| Tamil Nadu Innovation | `src/tn_main.py` | Morning | `docs/tn.html` |
| AI Digest Lite | `src/lite_main.py` | Morning | `docs/lite.html` |

| Time | Session |
|---|---|
| 7:00 AM CST (13:00 UTC) | 🌅 Morning — all four editions |
| 6:00 PM CST (00:00 UTC) | 🌆 Evening — Global refresh |

Everything runs on **GitHub Actions** — no server, works 24/7.

---

## Sources covered

| Category | Sources |
|---|---|
| Lab blogs | Anthropic, OpenAI, Google DeepMind, HuggingFace, Mistral, Meta AI, xAI, Cohere, NVIDIA, Microsoft, Databricks, Groq |
| Tech news | TechCrunch AI, The Verge AI, VentureBeat AI, Wired AI, Ars Technica, MIT Tech Review |
| Newsletters | The Rundown AI, Ben's Bites, Import AI, Simon Willison, Last Week in AI, The Batch, The Gradient, AI Snake Oil |
| Research | arXiv CS.AI · CS.LG · CS.CL, Papers With Code |
| Community | r/LocalLLaMA, r/MachineLearning, r/artificial, Hacker News (AI) |

General-interest sources are passed through an AI-relevance keyword filter so only
on-topic items make it into the digest. NewsAPI is supported as an optional extra
source but is off by default — RSS already covers the field.

---

## Setup (one time)

### 1. Fork or clone

```bash
git clone https://github.com/VigneshBhaskarraj/ai-digest.git
cd ai-digest
```

### 2. Get your API keys

| Key | Required? | Where |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** — Claude synthesis | [console.anthropic.com](https://console.anthropic.com) |
| `OPENROUTER_API_KEY` | Recommended — enables the cheap signal-extraction pass | [openrouter.ai/keys](https://openrouter.ai/keys) (free tier) |
| `NEWSAPI_KEY` | Optional — extra source, off by default | [newsapi.org/register](https://newsapi.org/register) |

If `OPENROUTER_API_KEY` is absent the pipeline still runs — it simply skips the
signal-extraction pass and sends Claude the ranked articles directly.

### 3. Add them as GitHub Actions secrets

**Settings → Secrets and variables → Actions → New repository secret** — add
`ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY` (and `NEWSAPI_KEY` if you want it).

### 4. Enable GitHub Pages

**Settings → Pages → Source → Deploy from a branch** → branch `main`, folder
`/docs`. Your dashboards go live at `https://<you>.github.io/ai-digest`.

### 5. Trigger your first run

**Actions → AI Digest — Scheduled Run → Run workflow** → pick `morning` or
`evening`. The dashboards update within ~2 minutes.

---

## Running locally

```bash
pip install -r requirements.txt

cp .env.example .env          # then fill in your keys
export $(cat .env | xargs)

python src/main.py --session morning   # Global
python src/india_main.py               # India AI Pulse
python src/tn_main.py                  # Tamil Nadu Innovation
python src/lite_main.py                # Lite
```

Output HTML lands in `docs/`. The temporal memory DB is created at
`data/digest_memory.db` (gitignored).

---

## Project structure

```
ai-digest/
├── .github/workflows/digest.yml   # Scheduler — runs all four pipelines
├── src/
│   ├── main.py / india_main.py / tn_main.py / lite_main.py   # orchestrators
│   ├── fetch_news.py              # 30+ RSS sources + relevance ranking
│   ├── fetch_papers.py            # arXiv / research fetcher
│   ├── extract_signals.py         # cheap multi-model signal-graph pass (OpenRouter)
│   ├── openrouter_client.py       # OpenRouter wrapper
│   ├── summarize*.py              # Claude synthesis prompts per edition
│   ├── memory.py                  # SQLite temporal memory store
│   ├── render_*.py                # dark-mode HTML renderers
│   └── send_email.py              # optional Gmail delivery (disabled by default)
├── docs/                          # GitHub Pages output (PWA: manifest, sw.js, icons)
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md
```

---

## Sharing

Every dashboard link is public and refreshes automatically twice a day — share it
with colleagues directly, no login required.

---

## License

MIT — see [LICENSE](LICENSE).

Built by [@VigneshBhaskarraj](https://github.com/VigneshBhaskarraj)
