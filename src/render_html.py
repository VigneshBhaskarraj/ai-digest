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
    "Model Releases":   "#4338CA",
    "Research":         "#0F766E",
    "Tools & Products": "#1D4ED8",
    "Industry News":    "#6366F1",
    "Community":        "#7C3AED",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body { height: 100%; overflow: hidden; }

body {
  background: #F8FAFC;
  font-family: 'Inter', sans-serif;
  color: #0F172A;
}

/* ── Floating Nav Tab ─────────────────── */
.nav-tab-bar {
  position: fixed;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  background: #6366F1;
  border-radius: 999px;
  padding: 5px 6px;
  display: flex;
  gap: 2px;
  box-shadow: 0 4px 24px rgba(99,102,241,0.35);
}
.nav-tab {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  padding: 6px 18px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  background: transparent;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  transition: background 0.18s, color 0.18s;
  white-space: nowrap;
}
.nav-tab.active, .nav-tab:hover {
  background: #fff;
  color: #4338CA;
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
  padding: 72px 2rem 2rem;
  border-bottom: 1px solid #E2E8F0;
  overflow: hidden;
}

.card-header-type { background: #0F172A; }
.card-story-type  { background: #FFFFFF; }
.card-hits-type   { background: #F8FAFC; }
.card-arxiv-type  { background: #F1F5F9; }
.card-pulse-type  { background: #FFFFFF; }

/* ── Card Top Bar ─────────────────────── */
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  flex-shrink: 0;
}

.category-pill {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #fff;
  border-radius: 999px;
  padding: 4px 14px;
}

.card-counter {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: #94A3B8;
}

/* ── Card Body ────────────────────────── */
.card-body {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

/* scrollable variant for list cards */
.card-body-scroll {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.card-source {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #94A3B8;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.card-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.35rem, 4vw, 1.85rem);
  font-weight: 700;
  line-height: 1.25;
  color: #0F172A;
  margin-bottom: 1rem;
  /* clamp to 3 lines so button never pushed off */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-divider {
  width: 36px;
  height: 2px;
  background: #6366F1;
  border-radius: 2px;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.card-why {
  font-size: 14px;
  line-height: 1.75;
  color: #475569;
  /* clamp to 5 lines so button always visible */
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Card Bottom — inline just after content ── */
.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #E2E8F0;
  flex-shrink: 0;
}

.card-header-type .card-bottom { border-top-color: rgba(255,255,255,0.1); }
.card-surge-type .card-bottom  { border-top-color: rgba(165,180,252,0.2); }

.read-btn {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: #6366F1;
  border: 1.5px solid #6366F1;
  border-radius: 999px;
  padding: 8px 20px;
  text-decoration: none;
  letter-spacing: 0.04em;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.read-btn:hover { background: #6366F1; color: #fff; }

.swipe-hint {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: #94A3B8;
  display: flex;
  align-items: center;
  gap: 5px;
}

.swipe-arrow {
  animation: bounce 1.6s ease-in-out infinite;
  display: inline-block;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-4px); }
}

/* ── Header Card ──────────────────────── */
.header-date {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: #64748B;
  margin-bottom: 1rem;
  letter-spacing: 0.06em;
}

.header-session {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #A5B4FC;
  background: rgba(99,102,241,0.2);
  border: 1px solid rgba(165,180,252,0.3);
  border-radius: 999px;
  padding: 4px 14px;
  display: inline-block;
  margin-bottom: 1.5rem;
}

.header-headline {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.7rem, 5vw, 2.6rem);
  font-weight: 800;
  line-height: 1.2;
  color: #F8FAFC;
  margin-bottom: 1.5rem;
}

.header-note {
  font-size: 13px;
  line-height: 1.75;
  color: #94A3B8;
  border-left: 3px solid #6366F1;
  padding-left: 1rem;
  max-width: 540px;
}

.header-note strong {
  color: #A5B4FC;
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
  background: #6366F1;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 10px 26px;
  cursor: pointer;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: background 0.15s;
}
.start-btn:hover { background: #4F46E5; }

/* ── Quick Hits Card ──────────────────── */
.hits-list { list-style: none; }
.hit-item {
  padding: 0.85rem 0;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}
.hit-item:last-child { border-bottom: none; }
.hit-dot { color: #6366F1; font-size: 12px; flex-shrink: 0; margin-top: 3px; }
.hit-title {
  font-size: 13px;
  font-weight: 500;
  color: #0F172A;
  text-decoration: none;
  line-height: 1.45;
}
.hit-title:hover { color: #6366F1; }
.hit-source { font-size: 10px; color: #94A3B8; font-family: 'DM Mono', monospace; margin-left: 4px; }
.hit-liner { font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5; }

/* ── arXiv Card ───────────────────────── */
.arxiv-item { margin-bottom: 1.25rem; padding-bottom: 1.25rem; border-bottom: 1px solid #E2E8F0; }
.arxiv-item:last-child { border-bottom: none; margin-bottom: 0; }
.arxiv-title {
  font-family: 'Playfair Display', serif;
  font-size: 1rem;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 0.4rem;
  text-decoration: none;
  display: block;
  line-height: 1.35;
}
.arxiv-title:hover { color: #6366F1; }
.arxiv-tldr { font-size: 13px; color: #475569; line-height: 1.65; }

/* ── Pulse Card ───────────────────────── */
.pulse-text {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.2rem, 3.5vw, 1.6rem);
  font-style: italic;
  font-weight: 700;
  line-height: 1.6;
  color: #0F172A;
}

/* ── Signal Surge Card ────────────────── */
.card-surge-type { background: #1E1B4B; }
.surge-label {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #A5B4FC;
  margin-bottom: 1.25rem;
}
.surge-topic {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 6vw, 3.2rem);
  font-weight: 800;
  font-style: italic;
  color: #F8FAFC;
  line-height: 1.1;
  margin-bottom: 1.25rem;
}
.surge-why {
  font-size: 14px;
  line-height: 1.8;
  color: #A5B4FC;
  max-width: 560px;
  margin-bottom: 1.5rem;
}
.surge-sources { display: flex; flex-wrap: wrap; gap: 8px; }
.surge-source-tag {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.06em;
  color: #C7D2FE;
  background: #312E81;
  border-radius: 999px;
  padding: 4px 12px;
}

/* ── Credibility Badge ────────────────── */
.cred-badge {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.04em;
  border-radius: 999px;
  padding: 2px 9px;
  vertical-align: middle;
}
.cred-high     { background: #DCFCE7; color: #15803D; }
.cred-medium   { background: #FEF9C3; color: #A16207; }
.cred-community{ background: #EEF2FF; color: #4338CA; }

/* ── Whitepaper Cards ─────────────────── */
.card-paper-type { background: #F1F5F9; }
.paper-item {
  margin-bottom: 0.75rem;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.paper-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0.9rem 1rem;
  cursor: pointer;
  gap: 1rem;
}
.paper-header:hover { background: #F8FAFC; }
.paper-title-wrap { flex: 1; }
.paper-title {
  font-family: 'Playfair Display', serif;
  font-size: 0.92rem;
  font-weight: 700;
  color: #0F172A;
  line-height: 1.3;
  margin-bottom: 0.3rem;
}
.paper-meta {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  color: #94A3B8;
  letter-spacing: 0.04em;
}
.paper-toggle {
  font-size: 16px;
  color: #6366F1;
  flex-shrink: 0;
  margin-top: 1px;
  transition: transform 0.2s;
  line-height: 1;
}
.paper-toggle.open { transform: rotate(90deg); }
.paper-body { display: none; padding: 0 1rem 1rem; border-top: 1px solid #E2E8F0; }
.paper-body.open { display: block; }
.paper-abstract { font-size: 12px; line-height: 1.7; color: #475569; margin-top: 0.75rem; margin-bottom: 0.75rem; }
.paper-read-btn {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: #6366F1;
  border: 1px solid #6366F1;
  border-radius: 999px;
  padding: 5px 14px;
  text-decoration: none;
}
.paper-read-btn:hover { background: #6366F1; color: #fff; }
.paper-source-tag {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  background: #EEF2FF;
  color: #4338CA;
  border-radius: 999px;
  padding: 2px 9px;
}

/* ── Leaders Voices Card ──────────────── */
.card-leaders-type { background: #FAFAFA; }
.leader-item {
  padding: 1rem 0;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}
.leader-item:last-child { border-bottom: none; }
.leader-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #EEF2FF;
  border: 2px solid #6366F1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'DM Mono', monospace;
  font-size: 13px;
  font-weight: 500;
  color: #4338CA;
  flex-shrink: 0;
}
.leader-content { flex: 1; min-width: 0; }
.leader-name {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 1px;
}
.leader-role {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  color: #94A3B8;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}
.leader-insight {
  font-size: 13px;
  line-height: 1.65;
  color: #334155;
  margin-bottom: 0.3rem;
}
.leader-context {
  font-size: 11px;
  color: #94A3B8;
  line-height: 1.5;
}
.leader-link {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  color: #6366F1;
  text-decoration: none;
  letter-spacing: 0.04em;
  margin-top: 0.35rem;
  display: inline-block;
}
.leader-link:hover { text-decoration: underline; }

/* ── Progress Rail ────────────────────── */
.progress-rail {
  position: fixed;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 80px;
  background: #E2E8F0;
  border-radius: 3px;
  z-index: 100;
}
.progress-fill {
  width: 100%;
  background: #6366F1;
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
  background: #1E1B4B;
}
.footer-brand-lg {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 800;
  color: #F8FAFC;
  margin-bottom: 0.75rem;
}
.footer-sub {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #A5B4FC;
  margin-bottom: 2rem;
}
.footer-restart {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: #F8FAFC;
  border: 1px solid rgba(165,180,252,0.4);
  border-radius: 999px;
  padding: 8px 24px;
  cursor: pointer;
  background: transparent;
  letter-spacing: 0.06em;
}
.footer-restart:hover { background: rgba(165,180,252,0.1); }
"""


def _pill(cat: str) -> str:
    color = CATEGORY_COLORS.get(cat, "#7A4F35")
    return f'<span class="category-pill" style="background:{color}">{cat}</span>'


def _cred_badge(credibility: str) -> str:
    mapping = {
        "high":      ("cred-high",      "✓ Lab / Research"),
        "medium":    ("cred-medium",    "◎ Tech Press"),
        "community": ("cred-community", "⬡ Community"),
    }
    cls, label = mapping.get(credibility, ("cred-medium", "◎ Tech Press"))
    return f'<span class="cred-badge {cls}">{label}</span>'


def render_html(digest: Dict, session_label: str = "Morning", papers: list = None) -> str:
    now = datetime.now(timezone.utc)
    date_str  = now.strftime("%A, %B %d, %Y")
    time_str  = now.strftime("%H:%M UTC")
    session_emoji = "🌅" if session_label == "Morning" else "🌆"

    headline        = digest.get("headline", "Your AI digest is ready.")
    signal_surge    = digest.get("signal_surge")
    top_stories     = digest.get("top_stories", [])
    quick_hits      = digest.get("quick_hits", [])
    arxiv_picks     = digest.get("arxiv_picks", [])
    community_pulse = digest.get("community_pulse", "")
    leaders_voices  = digest.get("leaders_voices", [])
    vike_note       = digest.get("vike_note", "")
    papers          = papers or []

    # Chunk papers into cards of 3 each
    paper_chunks = [papers[i:i+3] for i in range(0, min(len(papers), 9), 3)]

    # Count total cards for the counter
    total_cards = (
        1                                   # header
        + (1 if signal_surge else 0)        # signal surge
        + len(top_stories)
        + (1 if quick_hits else 0)
        + (1 if arxiv_picks else 0)
        + (1 if community_pulse else 0)
        + (1 if leaders_voices else 0)      # leaders card
        + len(paper_chunks)                 # whitepaper cards
        + 1                                 # footer
    )

    cards_html = ""
    card_index = 0

    # ── Header Card ───────────────────────────────────────────────────────────
    vike_block = ""
    if vike_note:
        vike_block = f'<div class="header-note"><strong>Today\'s signal</strong>{vike_note}</div>'

    cards_html += f"""
    <section class="card card-header-type" data-index="0">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.25rem">
        <span style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:0.16em;text-transform:uppercase;color:#64748B">⚡ AI Digest</span>
        <span class="card-counter">1 / {total_cards}</span>
      </div>
      <div class="card-body">
        <div class="header-date">{date_str} · {time_str}</div>
        <div class="header-session">{session_emoji} {session_label} Edition</div>
        <h1 class="header-headline">{headline}</h1>
        {vike_block}
      </div>
      <div class="card-bottom">
        <button class="start-btn" onclick="document.querySelector('.feed').scrollBy({{top:window.innerHeight,behavior:'smooth'}})">Read today's digest ↓</button>
        <span class="swipe-hint"><span class="swipe-arrow">↑</span> swipe</span>
      </div>
    </section>"""
    card_index = 1

    # ── Signal Surge Card ─────────────────────────────────────────────────────
    if signal_surge:
        card_index += 1
        surge_topic   = signal_surge.get("topic", "")
        surge_why     = signal_surge.get("why_surging", "")
        surge_count   = signal_surge.get("sources_count", 0)
        surge_srcs    = signal_surge.get("sources", [])
        surge_tags_html = "".join(
            f'<span class="surge-source-tag">{s}</span>' for s in surge_srcs[:6]
        )
        cards_html += f"""
    <section class="card card-surge-type" data-index="{card_index - 1}">
      <div class="card-top" style="border-bottom:1px solid rgba(196,168,130,0.2);padding-bottom:0.75rem;margin-bottom:auto">
        <span class="surge-label">⚡ Signal Surge — trending across {surge_count} sources</span>
        <span class="card-counter" style="color:#9B7E6A">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body" style="justify-content:flex-start;padding-top:2rem">
        <div class="surge-label" style="margin-bottom:0.75rem">What everyone&apos;s watching</div>
        <div class="surge-topic">{surge_topic}</div>
        <p class="surge-why">{surge_why}</p>
        <div class="surge-sources">{surge_tags_html}</div>
      </div>
      <div class="card-bottom" style="border-top:1px solid rgba(196,168,130,0.2)">
        <span class="swipe-hint" style="color:#9B7E6A"><span class="swipe-arrow">↑</span> swipe up</span>
      </div>
    </section>"""

    # ── Top Story Cards ───────────────────────────────────────────────────────
    for story in top_stories:
        cat         = story.get("category", "Industry News")
        pill        = _pill(cat)
        src         = story.get("source", "")
        title       = story.get("title", "")
        why         = story.get("why_it_matters", "")
        url         = story.get("url", "#")
        credibility = story.get("credibility", "medium")
        badge       = _cred_badge(credibility)
        card_index += 1

        cards_html += f"""
    <section class="card card-story-type" data-index="{card_index - 1}">
      <div class="card-top">
        {pill}
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body">
        <div class="card-source">{src}{badge}</div>
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
      <div class="card-body-scroll">
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
        <span class="category-pill" style="background:#0F766E">Research Picks</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">
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

    # ── Leaders Voices Card ───────────────────────────────────────────────────
    if leaders_voices:
        card_index += 1
        leaders_html = ""
        for lv in leaders_voices:
            name    = lv.get("name", "")
            role    = lv.get("role", "")
            insight = lv.get("insight", "")
            context = lv.get("context", "")
            url     = lv.get("url") or ""
            initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
            link_html = f'<a href="{url}" target="_blank" rel="noopener" class="leader-link">Read more →</a>' if url else ""
            leaders_html += f"""
        <div class="leader-item">
          <div class="leader-avatar">{initials}</div>
          <div class="leader-content">
            <div class="leader-name">{name}</div>
            <div class="leader-role">{role}</div>
            <p class="leader-insight">{insight}</p>
            <p class="leader-context">{context}</p>
            {link_html}
          </div>
        </div>"""

        cards_html += f"""
    <section class="card card-leaders-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#4338CA">Leaders&apos; Voices</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">
        {leaders_html}
      </div>
    </section>"""

    # ── Whitepaper Cards ──────────────────────────────────────────────────────
    for chunk_idx, chunk in enumerate(paper_chunks):
        card_index += 1
        chunk_label = f"Whitepapers · {chunk_idx + 1} of {len(paper_chunks)}"
        papers_html = ""
        for p_idx, p in enumerate(chunk):
            card_id   = f"paper-{card_index}-{p_idx}"
            src_tag   = f'<span class="paper-source-tag">{p.get("source","")}</span>'
            pub_date  = p.get("published", "")
            authors   = p.get("authors", "")
            meta_parts = [src_tag]
            if pub_date and pub_date != "Unknown":
                meta_parts.append(pub_date)
            if authors:
                meta_parts.append(authors)
            meta_html = " · ".join(str(x) for x in meta_parts)
            abstract  = p.get("abstract", "")[:500]
            purl      = p.get("url", "#")
            ptitle    = p.get("title", "")
            papers_html += f"""
        <div class="paper-item">
          <div class="paper-header" onclick="togglePaper('{card_id}')">
            <div class="paper-title-wrap">
              <div class="paper-title">{ptitle}</div>
              <div class="paper-meta">{meta_html}</div>
            </div>
            <span class="paper-toggle" id="toggle-{card_id}">›</span>
          </div>
          <div class="paper-body" id="body-{card_id}">
            <p class="paper-abstract">{abstract}</p>
            <a href="{purl}" target="_blank" rel="noopener" class="paper-read-btn">Read paper →</a>
          </div>
        </div>"""

        cards_html += f"""
    <section class="card card-paper-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#0F766E">📄 {chunk_label}</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">
        {papers_html}
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
  <meta name="description" content="Daily AI news digest — top stories, quick hits, research picks, and whitepapers.">
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#6366F1">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="AI Digest">
  <link rel="apple-touch-icon" href="icon-192.png">
  <style>{CSS}
/* ── PWA install banner ── */
#pwa-banner {{
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: #1E1B4B; color: #fff; border-radius: 999px;
  padding: 10px 20px 10px 16px; display: none; align-items: center; gap: 10px;
  box-shadow: 0 8px 32px rgba(99,102,241,0.45); z-index: 300;
  font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.04em;
  white-space: nowrap; cursor: pointer; border: none;
}}
#pwa-banner.show {{ display: flex; }}
#pwa-banner .pwa-icon {{ font-size: 16px; }}
#pwa-banner .pwa-dismiss {{
  margin-left: 6px; color: rgba(255,255,255,0.4); cursor: pointer;
  font-size: 14px; line-height: 1; padding: 0 4px;
}}
</style>
</head>
<body>

<button id="pwa-banner" aria-label="Install AI Digest app">
  <span class="pwa-icon">⬇</span> Add to Home Screen
  <span class="pwa-dismiss" id="pwa-dismiss" aria-label="Dismiss">✕</span>
</button>

<nav class="nav-tab-bar">
  <a class="nav-tab active" href="index.html">⚡ Global</a>
  <a class="nav-tab" href="india.html">🇮🇳 India</a>
</nav>

<div class="progress-rail"><div class="progress-fill" id="progress-fill"></div></div>

<div class="feed" id="feed">
  {cards_html}
</div>

<script>
  const feed  = document.getElementById('feed');
  const fill  = document.getElementById('progress-fill');
  const cards = document.querySelectorAll('[data-index]');
  const total = cards.length;

  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {{
        const idx = parseInt(entry.target.dataset.index, 10);
        fill.style.height = ((idx + 1) / total * 100) + '%';
      }}
    }});
  }}, {{ threshold: 0.5 }});

  cards.forEach(c => observer.observe(c));

  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {{
      feed.scrollBy({{ top: window.innerHeight, behavior: 'smooth' }});
    }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
      feed.scrollBy({{ top: -window.innerHeight, behavior: 'smooth' }});
    }}
  }});

  // ── Whitepaper expand/collapse ────────────────────────────────────────────
  function togglePaper(id) {{
    const body   = document.getElementById('body-' + id);
    const toggle = document.getElementById('toggle-' + id);
    const isOpen = body.classList.contains('open');
    body.classList.toggle('open', !isOpen);
    toggle.classList.toggle('open', !isOpen);
  }}

  // ── Service Worker ────────────────────────────────────────────────────────
  if ('serviceWorker' in navigator) {{
    navigator.serviceWorker.register('/ai-digest/sw.js')
      .catch(() => {{}});
  }}

  // ── PWA Install Banner ────────────────────────────────────────────────────
  let deferredPrompt = null;
  const banner = document.getElementById('pwa-banner');

  window.addEventListener('beforeinstallprompt', e => {{
    e.preventDefault();
    deferredPrompt = e;
    banner.classList.add('show');
  }});

  document.getElementById('pwa-install-btn').addEventListener('click', async () => {{
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const {{ outcome }} = await deferredPrompt.userChoice;
    deferredPrompt = null;
    banner.classList.remove('show');
  }});

  document.getElementById('pwa-dismiss').addEventListener('click', e => {{
    e.stopPropagation();
    banner.classList.remove('show');
  }});

  window.addEventListener('appinstalled', () => {{
    banner.classList.remove('show');
    deferredPrompt = null;
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
