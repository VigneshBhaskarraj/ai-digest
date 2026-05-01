# ⚡ AI Digest

A self-updating AI news dashboard that runs twice daily, summarizes the latest
LLM releases, tools, research papers, and industry news using Claude API,
then delivers it as a beautiful HTML email **and** a live GitHub Pages dashboard.

**Live Dashboard → [vigneshbhaskarraj.github.io/ai-digest](https://vigneshbhaskarraj.github.io/ai-digest)**

---

## What It Does

- Pulls news from 20+ sources: lab blogs (Anthropic, OpenAI, DeepMind, HuggingFace, Mistral),
  top tech outlets (TechCrunch, The Verge, Wired, VentureBeat), newsletters (Rundown AI,
  Ben's Bites, Import AI), Reddit (r/LocalLLaMA, r/MachineLearning), arXiv CS.AI
- Summarizes with Claude (claude-sonnet-4) into structured sections
- Renders a dark-mode HTML dashboard
- Pushes the dashboard to GitHub Pages (shareable link)
- Emails the digest at **7 AM CST (Morning)** and **6 PM CST (Evening)**

---

## Sources Covered

| Category | Sources |
|---|---|
| Lab Blogs | Anthropic, OpenAI, Google DeepMind, HuggingFace, Mistral, Meta AI |
| Tech News | TechCrunch AI, The Verge, Ars Technica, VentureBeat, Wired, MIT Tech Review, Techmeme |
| Newsletters | The Rundown AI, Ben's Bites, Import AI, Simon Willison |
| Research | arXiv CS.AI, arXiv CS.LG |
| Community | r/LocalLLaMA, r/MachineLearning |
| Aggregated | NewsAPI.org (with AI/LLM keyword filters) |

---

## Setup (One Time)

### 1. Fork or clone this repo

```bash
git clone https://github.com/VigneshBhaskarraj/ai-digest.git
cd ai-digest
```

### 2. Get your API keys

| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `NEWSAPI_KEY` | [newsapi.org/register](https://newsapi.org/register) — free tier |
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASS` | [Google App Password](https://myaccount.google.com/apppasswords) — NOT your real password |

### 3. Add secrets to GitHub

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add each of these:
- `ANTHROPIC_API_KEY`
- `NEWSAPI_KEY`
- `GMAIL_USER`
- `GMAIL_APP_PASS`
- `DIGEST_RECIPIENT` (email to send to, e.g. `vignesh.bhaskarraj@gmail.com`)

### 4. Enable GitHub Pages

Go to **Settings → Pages → Source → Deploy from a branch**
Set branch to `main`, folder to `/docs`. Save.

Your dashboard will be live at:
`https://vigneshbhaskarraj.github.io/ai-digest`

### 5. Trigger your first run

Go to **Actions → AI Digest — Scheduled Run → Run workflow**
Select `morning` or `evening`. Hit Run.

Check your email and the Pages URL within ~2 minutes.

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in your secrets
cp .env.example .env
# edit .env with your keys

# Load secrets and run
export $(cat .env | xargs)
python src/main.py --session morning
python src/main.py --session evening
```

---

## Schedule

| Time | Session |
|---|---|
| 7:00 AM CST (13:00 UTC) | 🌅 Morning Edition |
| 6:00 PM CST (00:00 UTC) | 🌆 Evening Edition |

Runs via GitHub Actions — no server needed, works 24/7.

---

## Project Structure

```
ai-digest/
├── .github/workflows/digest.yml   # Scheduler + pipeline runner
├── src/
│   ├── main.py                    # Orchestrator
│   ├── fetch_news.py              # RSS + NewsAPI fetcher
│   ├── summarize.py               # Claude API summarizer
│   ├── render_html.py             # HTML dashboard renderer
│   └── send_email.py              # Gmail SMTP sender
├── docs/index.html                # Live GitHub Pages output
├── requirements.txt
├── .env.example
└── README.md
```

---

## Sharing

The GitHub Pages link (`https://vigneshbhaskarraj.github.io/ai-digest`) is public
and updates automatically twice a day. Share it with colleagues directly — no login required.

---

Built by [@VigneshBhaskarraj](https://github.com/VigneshBhaskarraj)
