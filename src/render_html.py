"""
render_html.py
Renders the AI Digest as a beige card-swipe dashboard.
Full-viewport scroll-snap cards with Playfair Display headlines.
Output: docs/index.html (served by GitHub Pages)
"""

import os
from datetime import datetime, timezone
from typing import Dict

CATEGORY_COLORS = {
    "Model Releases":   "#5C3D2E",
    "Research":         "#384840",
    "Tools & Products": "#3B4852",
    "Industry News":    "#7A4F35",
    "Community":        "#5C3A4A",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=DM+Sans:wght@400;500&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  background: #F5EFE3;
  font-family: 'DM Sans', sans-serif;
  color: #2C1810;
}

/* ── Feed ─────────────────────────────── */
.feed {
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.feed::-webkit-scrollbar { display: none; }

/* ── Cards ────────────────────────────── */
.card {
  height: 100vh;
  scroll-snap-align: start;
  scroll-snap-stop: always;
  display: flex;
  flex-direction: column;
  padding: 2.25rem 2rem 1.75rem;
  position: relative;
  border-bottom: 1px solid #E0D5C4;
}

.card-header-type { background: #F5EFE3; justify-content: center; }
.card-story-type  { background: #FAF7F0; }
.card-hits-type   { background: #F5EFE3; }
.card-arxiv-type  { background: #F0EBE0; }
.card-pulse-type  { background: #FAF7F0; }

/* ── Card Top Bar ─────────────────────── */
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: auto;
}

.category-pill {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #F5EFE3;
  border-radius: 20px;
  padding: 4px 14px;
}

.card-counter {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: #B09880;
}

/* ── Card Body ────────────────────────── */
.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1.5rem 0 1rem;
}

.card-source {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #9B7E6A;
  margin-bottom: 0.85rem;
}

.card-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.4rem, 4vw, 1.9rem);
  font-weight: 700;
  line-height: 1.2;
  color: #2C1810;
  margin-bottom: 1.1rem;
}

.card-title em {
  font-style: italic;
  color: #7A4F35;
}

.card-divider {
  width: 36px;
  height: 2px;
  background: #C4A882;
  border-radius: 2px;
  margin-bottom: 1rem;
}

.card-why {
  font-size: 14px;
  line-height: 1.75;
  color: #5C4033;
  max-width: 600px;
}

/* ── Card Bottom ──────────────────────── */
.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #E0D5C4;
}

.read-btn {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: #7A4F35;
  border: 1px solid #C4A882;
  border-radius: 20px;
  padding: 7px 18px;
  text-decoration: none;
  letter-spacing: 0.04em;
  transition: background 0.15s, color 0.15s;
}
.read-btn:hover {
  background: #5C3D2E;
  color: #F5EFE3;
  border-color: #5C3D2E;
}

.swipe-hint {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: #C4A882;
  display: flex;
  align-items: center;
  gap: 5px;
  letter-spacing: 0.05em;
}

.swipe-arrow {
  animation: bounce 1.6s ease-in-out infinite;
  display: inline-block;
  font-size: 14px;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-5px); }
}

/* ── Header Card ──────────────────────── */
.header-brand {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #9B7E6A;
  margin-bottom: 2rem;
}

.header-brand a {
  color: #7A4F35;
  text-decoration: none;
  border: 1px solid #C4A882;
  border-radius: 20px;
  padding: 4px 12px;
  margin-left: 8px;
  font-size: 9px;
}

.header-date {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: #B09880;
  margin-bottom: 1.25rem;
}

.header-session {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #F5EFE3;
  background: #5C3D2E;
  border-radius: 20px;
  padding: 4px 14px;
  display: inline-block;
  margin-bottom: 1.25rem;
}

.header-headline {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.6rem, 5vw, 2.4rem);
  font-weight: 800;
  line-height: 1.2;
  color: #2C1810;
  margin-bottom: 1.5rem;
}

.header-note {
  font-size: 13px;
  line-height: 1.75;
  color: #5C4033;
  border-left: 3px solid #C4A882;
  padding-left: 1rem;
  max-width: 540px;
}

.header-note strong {
  color: #7A4F35;
  font-size: 10px;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  display: block;
  margin-bottom: 0.4rem;
}

.start-btn {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  background: #5C3D2E;
  color: #F5EFE3;
  border: none;
  border-radius: 20px;
  padding: 10px 24px;
  cursor: pointer;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ── Quick Hits Card ──────────────────── */
.hits-list { list-style: none; }
.hit-item {
  padding: 0.85rem 0;
  border-bottom: 1px solid #E0D5C4;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}
.hit-item:last-child { border-bottom: none; }
.hit-dot { color: #C4A882; font-size: 14px; flex-shrink: 0; margin-top: 1px; }
.hit-content {}
.hit-title {
  font-size: 13px;
  font-weight: 500;
  color: #2C1810;
  text-decoration: none;
  line-height: 1.4;
}
.hit-title:hover { color: #7A4F35; }
.hit-source { font-size: 10px; color: #9B7E6A; font-family: 'DM Mono', monospace; margin-left: 4px; }
.hit-liner { font-size: 12px; color: #9B7E6A; margin-top: 3px; line-height: 1.5; }

/* ── arXiv Card ───────────────────────── */
.arxiv-item { margin-bottom: 1.25rem; padding-bottom: 1.25rem; border-bottom: 1px solid #E0D5C4; }
.arxiv-item:last-child { border-bottom: none; margin-bottom: 0; }
.arxiv-title {
  font-family: 'Playfair Display', serif;
  font-size: 1rem;
  font-weight: 700;
  color: #2C1810;
  margin-bottom: 0.4rem;
  text-decoration: none;
  display: block;
  line-height: 1.35;
}
.arxiv-title:hover { color: #7A4F35; }
.arxiv-tldr { font-size: 13px; color: #5C4033; line-height: 1.65; }

/* ── Pulse Card ───────────────────────── */
.pulse-text {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.1rem, 3vw, 1.4rem);
  font-style: italic;
  font-weight: 700;
  line-height: 1.6;
  color: #2C1810;
}

/* ── Filter Bar ──────────────────────── */
.filter-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 200;
  background: rgba(245,239,227,0.95);
  backdrop-filter: blur(8px);
  border-top: 1px solid #E0D5C4;
  padding: 0.6rem 1.25rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.filter-row {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  scrollbar-width: none;
  align-items: center;
}
.filter-row::-webkit-scrollbar { display: none; }
.filter-label {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #B09880;
  white-space: nowrap;
  flex-shrink: 0;
  width: 52px;
}
.filter-chip {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.04em;
  color: #7A4F35;
  background: #EDE4D6;
  border: 1px solid #D4C4B0;
  border-radius: 20px;
  padding: 4px 12px;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
  user-select: none;
}
.filter-chip:hover { background: #D4C4B0; }
.filter-chip.active {
  background: #5C3D2E;
  color: #F5EFE3;
  border-color: #5C3D2E;
}

/* push cards up so filter bar doesn't overlap last card */
.feed { padding-bottom: 0; }
.card { padding-bottom: 5.5rem; }
.footer-card { padding-bottom: 2rem; }

/* ── Fixed Progress Bar ───────────────── */
.progress-rail {
  position: fixed;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 80px;
  background: #E0D5C4;
  border-radius: 3px;
  z-index: 100;
}
.progress-fill {
  width: 100%;
  background: #5C3D2E;
  border-radius: 3px;
  height: 10%;
  transition: height 0.3s ease;
}

/* ── Footer Card ──────────────────────── */
.footer-card {
  height: 100vh;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  background: #5C3D2E;
}
.footer-brand-lg {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 800;
  color: #F5EFE3;
  margin-bottom: 0.75rem;
}
.footer-sub {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #C4A882;
  margin-bottom: 2rem;
}
.footer-restart {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: #F5EFE3;
  border: 1px solid rgba(245,239,227,0.35);
  border-radius: 20px;
  padding: 8px 22px;
  cursor: pointer;
  background: transparent;
  letter-spacing: 0.06em;
}
.footer-restart:hover { background: rgba(245,239,227,0.1); }
"""


def _pill(cat: str) -> str:
    color = CATEGORY_COLORS.get(cat, "#7A4F35")
    return f'<span class="category-pill" style="background:{color}">{cat}</span>'


def render_html(digest: Dict, session_label: str = "Morning") -> str:
    now = datetime.now(timezone.utc)
    date_str  = now.strftime("%A, %B %d, %Y")
    time_str  = now.strftime("%H:%M UTC")
    session_emoji = "🌅" if session_label == "Morning" else "🌆"

    headline       = digest.get("headline", "Your AI digest is ready.")
    top_stories    = digest.get("top_stories", [])
    quick_hits     = digest.get("quick_hits", [])
    arxiv_picks    = digest.get("arxiv_picks", [])
    community_pulse = digest.get("community_pulse", "")
    vike_note      = digest.get("vike_note", "")

    # Count total cards for the counter
    total_cards = (
        1                            # header
        + len(top_stories)
        + (1 if quick_hits else 0)
        + (1 if arxiv_picks else 0)
        + (1 if community_pulse else 0)
        + 1                          # footer
    )

    cards_html = ""
    card_index = 0

    # ── Header Card ───────────────────────────────────────────────────────────
    vike_block = ""
    if vike_note:
        vike_block = f'<div class="header-note"><strong>Today\'s signal</strong>{vike_note}</div>'

    cards_html += f"""
    <section class="card card-header-type" data-index="0">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:auto">
        <span class="header-brand">⚡ AI Digest <a href="india.html">🇮🇳 India Pulse</a></span>
        <span class="card-counter">1 / {total_cards}</span>
      </div>
      <div class="card-body" style="justify-content:flex-start;padding-top:2rem">
        <div class="header-date">{date_str} · {time_str}</div>
        <div class="header-session">{session_emoji} {session_label} Edition</div>
        <h1 class="header-headline">{headline}</h1>
        {vike_block}
      </div>
      <div class="card-bottom">
        <button class="start-btn" onclick="document.querySelector('.feed').scrollBy({{top:window.innerHeight,behavior:'smooth'}})">Read today's digest ↓</button>
        <span class="swipe-hint"><span class="swipe-arrow">↑</span> swipe up</span>
      </div>
    </section>"""
    card_index = 1

    # ── Top Story Cards ───────────────────────────────────────────────────────
    for story in top_stories:
        cat   = story.get("category", "Industry News")
        pill  = _pill(cat)
        src   = story.get("source", "")
        title = story.get("title", "")
        why   = story.get("why_it_matters", "")
        url   = story.get("url", "#")
        card_index += 1

        cards_html += f"""
    <section class="card card-story-type" data-index="{card_index - 1}">
      <div class="card-top">
        {pill}
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body">
        <div class="card-source">{src}</div>
        <h2 class="card-title">{title}</h2>
        <div class="card-divider"></div>
        <p class="card-why">{why}</p>
      </div>
      <div class="card-bottom">
        <a href="{url}" target="_blank" rel="noopener" class="read-btn">Read full story →</a>
      </div>
    </section>"""

    # ── Quick Hits Card ───────────────────────────────────────────────────────
    if quick_hits:
        card_index += 1
        hits_items = ""
        for hit in quick_hits:
            hits_items += f"""
          <li class="hit-item">
            <span class="hit-dot">▸</span>
            <div class="hit-content">
              <a href="{hit.get('url','#')}" target="_blank" rel="noopener" class="hit-title">{hit.get('title','')}</a>
              <span class="hit-source">— {hit.get('source','')}</span>
              <p class="hit-liner">{hit.get('one_liner','')}</p>
            </div>
          </li>"""

        cards_html += f"""
    <section class="card card-hits-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#5C3A4A">Quick Hits</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body" style="overflow-y:auto">
        <ul class="hits-list">{hits_items}</ul>
      </div>
    </section>"""

    # ── arXiv Card ────────────────────────────────────────────────────────────
    if arxiv_picks:
        card_index += 1
        arxiv_items = ""
        for paper in arxiv_picks:
            arxiv_items += f"""
          <div class="arxiv-item">
            <a href="{paper.get('url','#')}" target="_blank" rel="noopener" class="arxiv-title">{paper.get('title','')}</a>
            <p class="arxiv-tldr">{paper.get('tldr','')}</p>
          </div>"""

        cards_html += f"""
    <section class="card card-arxiv-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#384840">Research Picks</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body" style="overflow-y:auto">
        {arxiv_items}
      </div>
    </section>"""

    # ── Community Pulse Card ──────────────────────────────────────────────────
    if community_pulse:
        card_index += 1
        cards_html += f"""
    <section class="card card-pulse-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#5C3A4A">Community Pulse</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body">
        <p class="pulse-text">"{community_pulse}"</p>
      </div>
    </section>"""

    # ── Footer Card ───────────────────────────────────────────────────────────
    cards_html += f"""
    <section class="footer-card" data-index="{card_index}">
      <div class="footer-brand-lg">⚡ AI Digest</div>
      <div class="footer-sub">Generated {date_str} · {time_str}</div>
      <button class="footer-restart" onclick="document.querySelector('.feed').scrollTo({{top:0,behavior:'smooth'}})">↑ Back to top</button>
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚡ AI Digest — {session_label} Edition · {date_str}</title>
  <meta name="description" content="Daily AI news digest — top stories, quick hits, and research picks.">
  <style>{CSS}</style>
</head>
<body>

<div class="progress-rail"><div class="progress-fill" id="progress-fill"></div></div>

<div class="feed" id="feed">
  {cards_html}
</div>

<div class="filter-bar" id="filter-bar">
  <div class="filter-row">
    <span class="filter-label">Leaders</span>
    <span class="filter-chip" data-filter="karpathy">Karpathy</span>
    <span class="filter-chip" data-filter="sam altman">Sam Altman</span>
    <span class="filter-chip" data-filter="demis">Demis</span>
    <span class="filter-chip" data-filter="yann lecun">LeCun</span>
    <span class="filter-chip" data-filter="ilya">Ilya</span>
    <span class="filter-chip" data-filter="greg brockman">Brockman</span>
  </div>
  <div class="filter-row">
    <span class="filter-label">Company</span>
    <span class="filter-chip" data-filter="anthropic">Anthropic</span>
    <span class="filter-chip" data-filter="openai">OpenAI</span>
    <span class="filter-chip" data-filter="google">Google</span>
    <span class="filter-chip" data-filter="meta">Meta</span>
    <span class="filter-chip" data-filter="mistral">Mistral</span>
    <span class="filter-chip" data-filter="huggingface">HuggingFace</span>
    <span class="filter-chip" data-filter="nvidia">Nvidia</span>
  </div>
  <div class="filter-row">
    <span class="filter-label">Topic</span>
    <span class="filter-chip" data-filter="agent">Agents</span>
    <span class="filter-chip" data-filter="model">Models</span>
    <span class="filter-chip" data-filter="research">Research</span>
    <span class="filter-chip" data-filter="vision">Vision</span>
    <span class="filter-chip" data-filter="robotics">Robotics</span>
    <span class="filter-chip" data-filter="open source">Open Source</span>
    <span class="filter-chip" data-filter="safety">Safety</span>
  </div>
</div>

<script>
  const feed    = document.getElementById('feed');
  const fill    = document.getElementById('progress-fill');
  const allCards = Array.from(document.querySelectorAll('[data-index]'));
  let visibleCards = allCards;

  function updateProgress() {{
    const idx = visibleCards.findIndex(c => {{
      const r = c.getBoundingClientRect();
      return r.top >= -10 && r.top < window.innerHeight / 2;
    }});
    const cur = idx >= 0 ? idx : 0;
    fill.style.height = ((cur + 1) / visibleCards.length * 100) + '%';
  }}

  feed.addEventListener('scroll', updateProgress, {{ passive: true }});

  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {{
      feed.scrollBy({{ top: window.innerHeight, behavior: 'smooth' }});
    }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
      feed.scrollBy({{ top: -window.innerHeight, behavior: 'smooth' }});
    }}
  }});

  // ── Filtering ─────────────────────────────────────────────────────────────
  let activeFilter = null;

  document.querySelectorAll('.filter-chip').forEach(chip => {{
    chip.addEventListener('click', () => {{
      const keyword = chip.dataset.filter;

      if (activeFilter === keyword) {{
        // Deactivate filter — show all
        activeFilter = null;
        chip.classList.remove('active');
        allCards.forEach(c => c.style.display = '');
        visibleCards = allCards;
        feed.scrollTo({{ top: 0, behavior: 'smooth' }});
        return;
      }}

      // Deactivate previous chip
      document.querySelectorAll('.filter-chip.active').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeFilter = keyword;

      // Show/hide cards based on text content match
      visibleCards = [];
      allCards.forEach(c => {{
        const text = c.innerText.toLowerCase();
        const isHeader = c.dataset.index === '0';
        const isFooter = !c.classList.contains('card');
        const matches = isHeader || isFooter || text.includes(keyword);
        c.style.display = matches ? '' : 'none';
        if (matches) visibleCards.push(c);
      }});

      // Scroll to first matching story card
      const firstStory = visibleCards.find(c => c.dataset.index !== '0');
      if (firstStory) firstStory.scrollIntoView({{ behavior: 'smooth' }});

      updateProgress();
    }});
  }});
</script>
</body>
</html>"""

    return html


def save_dashboard(html: str, output_path: str = "docs/index.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Render] Dashboard saved → {output_path}")


if __name__ == "__main__":
    dummy = {
        "headline": "Anthropic ships Claude 4 with native tool use and 200K context window",
        "top_stories": [
            {
                "title": "Claude 4 Released with Extended Thinking Mode",
                "source": "Anthropic Blog",
                "url": "https://anthropic.com",
                "why_it_matters": "Extended thinking lets Claude reason step-by-step. For builders this means better agentic reliability on complex multi-step tasks.",
                "category": "Model Releases",
            },
            {
                "title": "OpenAI launches GPT-5 with multimodal reasoning",
                "source": "OpenAI Blog",
                "url": "https://openai.com",
                "why_it_matters": "GPT-5 adds native vision and audio reasoning in a single model call — no longer requires separate pipelines.",
                "category": "Model Releases",
            },
        ],
        "quick_hits": [
            {"title": "Mistral releases Le Chat Pro", "source": "Mistral AI", "url": "#", "one_liner": "New paid tier with faster inference and priority access."},
            {"title": "Meta open-sources Llama 4", "source": "Meta AI", "url": "#", "one_liner": "70B and 405B variants available for commercial use."},
        ],
        "arxiv_picks": [
            {"title": "Mixture-of-Agents Outperforms GPT-4 on Most Benchmarks", "url": "#", "tldr": "Combining outputs from 6 smaller LLMs beats a single large model at 40% lower cost."},
        ],
        "community_pulse": "r/LocalLLaMA is buzzing about running Claude 4 variants locally via Ollama. The quantized 70B model fits in 48GB VRAM.",
        "vike_note": "Claude 4 tool-use improvements are directly relevant to the Ask Agent POC you're building — test the new API parameters this week.",
    }
    html = render_html(dummy, "Morning")
    save_dashboard(html, "/tmp/test_dashboard.html")
    print(f"Test HTML written ({len(html):,} bytes)")
