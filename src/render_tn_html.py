"""
render_tn_html.py
Renders the Tamil Nadu Innovation Digest as a card-swipe dashboard.
CSS is kept pixel-consistent with render_india_html.py and render_html.py.
Sections: Signal of the Week, Policy, Startup Spotlight, Research,
          Club Radar, District Pulse, Sector Opportunities, Quick Hits,
          Leaders Voices, Footer.
Output: docs/tn.html (GitHub Pages)
"""

import os
from datetime import datetime, timezone
from typing import Dict
from tn_ecosystem_data import get_startups_by_cluster

# ─────────────────────────────────────────────────────────────────────────────
# Shared CSS — identical palette to India + Global pages
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; }
body { background: #F8FAFC; font-family: 'Inter', sans-serif; color: #0F172A; }

/* ── Nav ─────────────────────────────────────────────────────────────────── */
.nav-tab-bar {
  position: fixed; top: 14px; left: 50%; transform: translateX(-50%);
  z-index: 200; background: #6366F1; border-radius: 999px; padding: 5px 6px;
  display: flex; gap: 2px; box-shadow: 0 4px 24px rgba(99,102,241,0.35);
}
.nav-tab {
  font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.04em;
  padding: 6px 18px; border-radius: 999px; border: none; cursor: pointer;
  background: transparent; color: rgba(255,255,255,0.7); text-decoration: none;
  transition: background 0.18s, color 0.18s; white-space: nowrap;
}
.nav-tab.active, .nav-tab:hover { background: #fff; color: #4338CA; }

/* ── Feed ──────────────────────────────────────────────────────────────────── */
.feed {
  height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory;
  -webkit-overflow-scrolling: touch; scrollbar-width: none;
}
.feed::-webkit-scrollbar { display: none; }

/* ── Card base ─────────────────────────────────────────────────────────────── */
.card {
  height: 100vh; scroll-snap-align: start; scroll-snap-stop: always;
  display: flex; flex-direction: column;
  padding: 72px 2rem 2rem;
  border-bottom: 1px solid #E2E8F0; overflow: hidden;
}
.card-header-type  { background: #0F172A; }
.card-signal-type  { background: #1E1B4B; }
.card-policy-type  { background: #FFFFFF; }
.card-startup-type { background: #F8FAFC; }
.card-research-type { background: #F1F5F9; }
.card-club-type    { background: #FFFFFF; }
.card-district-type { background: #F8FAFC; }
.card-sector-type  { background: #F1F5F9; }
.card-pulse-type   { background: #FFFFFF; }
.card-hits-type    { background: #F8FAFC; }
.card-leaders-type { background: #FAFAFA; }

/* ── Card Top ──────────────────────────────────────────────────────────────── */
.card-top {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1.25rem; flex-shrink: 0;
}
.category-pill {
  font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.08em;
  text-transform: uppercase; color: #fff; border-radius: 999px; padding: 4px 14px;
}
.card-counter { font-family: 'DM Mono', monospace; font-size: 11px; color: #94A3B8; }

/* ── Card Body ─────────────────────────────────────────────────────────────── */
.card-body { display: flex; flex-direction: column; flex-shrink: 0; }
.card-body-scroll { display: flex; flex-direction: column; flex: 1; overflow-y: auto; min-height: 0; }

/* ── Card Bottom ───────────────────────────────────────────────────────────── */
.card-bottom {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E2E8F0; flex-shrink: 0;
}

/* ── Buttons & hints ───────────────────────────────────────────────────────── */
.read-btn {
  font-family: 'DM Mono', monospace; font-size: 11px; color: #6366F1;
  border: 1.5px solid #6366F1; border-radius: 999px; padding: 8px 20px;
  text-decoration: none; letter-spacing: 0.04em;
  transition: background 0.15s, color 0.15s; white-space: nowrap; display: inline-block;
}
.read-btn:hover { background: #6366F1; color: #fff; }
.read-btn-sm {
  font-family: 'DM Mono', monospace; font-size: 9px; color: #6366F1;
  border: 1px solid #6366F1; border-radius: 999px; padding: 3px 10px;
  text-decoration: none; transition: background 0.15s, color 0.15s; display: inline-block;
}
.read-btn-sm:hover { background: #6366F1; color: #fff; }

.start-btn {
  font-family: 'DM Mono', monospace; font-size: 11px; background: #6366F1;
  color: #fff; border: none; border-radius: 999px; padding: 10px 26px;
  cursor: pointer; letter-spacing: 0.06em; text-transform: uppercase;
  transition: background 0.15s;
}
.start-btn:hover { background: #4F46E5; }

.swipe-hint {
  font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8;
  display: flex; align-items: center; gap: 5px;
}
.swipe-arrow { animation: bounce 1.6s ease-in-out infinite; display: inline-block; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

/* ── Card divider ──────────────────────────────────────────────────────────── */
.card-divider { width: 36px; height: 2px; background: #6366F1; border-radius: 2px; margin-bottom: 1rem; flex-shrink: 0; }

/* ── Header card ───────────────────────────────────────────────────────────── */
.header-date { font-family: 'DM Mono', monospace; font-size: 10px; color: #64748B; margin-bottom: 1rem; letter-spacing: 0.06em; }
.header-session {
  font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.12em;
  text-transform: uppercase; color: #A5B4FC; background: rgba(99,102,241,0.2);
  border: 1px solid rgba(165,180,252,0.3); border-radius: 999px; padding: 4px 14px;
  display: inline-block; margin-bottom: 1.5rem;
}
.header-headline {
  font-family: 'Playfair Display', serif; font-size: clamp(1.7rem, 5vw, 2.6rem);
  font-weight: 800; line-height: 1.2; color: #F8FAFC; margin-bottom: 1.5rem;
}
.header-note {
  font-size: 13px; line-height: 1.75; color: #94A3B8;
  border-left: 3px solid #6366F1; padding-left: 1rem; max-width: 540px;
}
.header-note strong {
  color: #A5B4FC; font-size: 10px; font-family: 'DM Mono', monospace;
  letter-spacing: 0.08em; text-transform: uppercase; display: block; margin-bottom: 0.4rem;
}

/* ── Signal of the Week card (dark, like Global Surge) ─────────────────────── */
.signal-label {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.2em;
  text-transform: uppercase; color: #A5B4FC; margin-bottom: 1.25rem;
}
.signal-theme {
  font-family: 'Playfair Display', serif; font-size: clamp(1.8rem, 5.5vw, 2.8rem);
  font-weight: 800; font-style: italic; color: #F8FAFC; line-height: 1.1; margin-bottom: 1.25rem;
}
.signal-why { font-size: 14px; line-height: 1.8; color: #A5B4FC; max-width: 560px; margin-bottom: 1.5rem; }
.signal-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.signal-tag {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.06em;
  color: #C7D2FE; background: #312E81; border-radius: 999px; padding: 4px 12px;
}

/* ── Generic item block (policy, research, club, district) ──────────────────── */
.item-block { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; }
.item-block:last-child { border-bottom: none; margin-bottom: 0; }
.item-title {
  font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700;
  color: #0F172A; line-height: 1.35; margin-bottom: 0.5rem;
}
.item-body { font-size: 13px; line-height: 1.7; color: #475569; margin-bottom: 0.5rem; }
.item-note { font-size: 13px; line-height: 1.65; color: #0F172A; font-weight: 500; border-left: 2px solid #6366F1; padding-left: 0.65rem; margin-bottom: 0.4rem; }
.item-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 0.4rem; }

/* ── Badges ────────────────────────────────────────────────────────────────── */
.impact-badge { font-family: 'DM Mono', monospace; font-size: 9px; border-radius: 999px; padding: 2px 9px; }
.impact-high   { background: #DCFCE7; color: #15803D; }
.impact-medium { background: #FEF9C3; color: #A16207; }
.impact-low    { background: #F1F5F9; color: #64748B; }
.sector-badge  { font-family: 'DM Mono', monospace; font-size: 9px; background: #EEF2FF; color: #4338CA; border-radius: 999px; padding: 2px 9px; }
.location-badge { font-family: 'DM Mono', monospace; font-size: 9px; background: #F0FDF4; color: #15803D; border-radius: 999px; padding: 2px 9px; }
.org-badge     { font-family: 'DM Mono', monospace; font-size: 9px; background: #FFF7ED; color: #C2410C; border-radius: 999px; padding: 2px 9px; }
.district-badge { font-family: 'DM Mono', monospace; font-size: 9px; background: #F5F3FF; color: #6D28D9; border-radius: 999px; padding: 2px 9px; }
.source-tag   { font-family: 'DM Mono', monospace; font-size: 9px; color: #94A3B8; letter-spacing: 0.04em; }

/* ── Startup spotlight ────────────────────────────────────────────────────── */
.startup-name-lg {
  font-family: 'Playfair Display', serif; font-size: clamp(1.4rem, 4vw, 1.9rem);
  font-weight: 800; color: #0F172A; line-height: 1.15; margin-bottom: 0.4rem;
}
.startup-what { font-size: 14px; line-height: 1.7; color: #475569; margin-bottom: 0.6rem; }
.startup-why  { font-size: 13px; line-height: 1.65; color: #64748B; border-left: 2px solid #6366F1; padding-left: 0.75rem; font-style: italic; }

/* ── Sector opportunity ────────────────────────────────────────────────────── */
.sector-item { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; }
.sector-item:last-child { border-bottom: none; }
.sector-name { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #0F172A; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 8px; }
.sector-signal { font-family: 'DM Mono', monospace; font-size: 9px; background: #FEF3C7; color: #92400E; border-radius: 999px; padding: 2px 9px; }
.sector-body  { font-size: 13px; line-height: 1.7; color: #475569; }

/* ── District pulse ────────────────────────────────────────────────────────── */
.district-item { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; }
.district-item:last-child { border-bottom: none; }
.district-header { display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }
.district-city { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #0F172A; }
.district-signal { font-size: 13px; line-height: 1.65; color: #475569; margin-bottom: 0.4rem; }
.district-opp { font-size: 12px; line-height: 1.6; color: #64748B; border-left: 2px solid #A5B4FC; padding-left: 0.65rem; }

/* ── Quick Hits ────────────────────────────────────────────────────────────── */
.hits-list { list-style: none; }
.hit-item { padding: 0.85rem 0; border-bottom: 1px solid #E2E8F0; display: flex; gap: 0.75rem; align-items: flex-start; }
.hit-item:last-child { border-bottom: none; }
.hit-dot { color: #6366F1; font-size: 12px; flex-shrink: 0; margin-top: 3px; }
.hit-title { font-size: 13px; font-weight: 500; color: #0F172A; text-decoration: none; line-height: 1.45; }
.hit-title:hover { color: #6366F1; }
.hit-source { font-size: 10px; color: #94A3B8; font-family: 'DM Mono', monospace; margin-left: 4px; }
.hit-liner { font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5; }

/* ── Pulse text ────────────────────────────────────────────────────────────── */
.pulse-text {
  font-family: 'Playfair Display', serif; font-size: clamp(1.2rem, 3.5vw, 1.6rem);
  font-style: italic; font-weight: 700; line-height: 1.6; color: #0F172A;
}

/* ── Leaders ───────────────────────────────────────────────────────────────── */
.leader-item { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; display: flex; gap: 1rem; align-items: flex-start; }
.leader-item:last-child { border-bottom: none; }
.leader-avatar {
  width: 40px; height: 40px; border-radius: 50%; background: #EEF2FF; border: 2px solid #6366F1;
  display: flex; align-items: center; justify-content: center;
  font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; color: #4338CA; flex-shrink: 0;
}
.leader-content { flex: 1; min-width: 0; }
.leader-name { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #0F172A; margin-bottom: 1px; }
.leader-role { font-family: 'DM Mono', monospace; font-size: 9px; color: #94A3B8; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.leader-insight { font-size: 13px; line-height: 1.65; color: #334155; margin-bottom: 0.3rem; }
.leader-context { font-size: 11px; color: #94A3B8; line-height: 1.5; }
.leader-link { font-family: 'DM Mono', monospace; font-size: 9px; color: #6366F1; text-decoration: none; margin-top: 0.35rem; display: inline-block; }
.leader-link:hover { text-decoration: underline; }

/* ── Startup Pulse (news-driven funded startups) ──────────────────────────── */
.card-pulse-startups-type { background: #FFFFFF; }
.funded-item { padding: 0.9rem 0; border-bottom: 1px solid #E2E8F0; }
.funded-item:last-child { border-bottom: none; }
.funded-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-bottom: 0.35rem; }
.funded-name { font-family: 'Playfair Display', serif; font-size: 1rem; font-weight: 700; color: #0F172A; line-height: 1.2; }
.funded-badges { display: flex; flex-direction: column; gap: 3px; align-items: flex-end; flex-shrink: 0; }
.funded-what { font-size: 12px; line-height: 1.6; color: #475569; margin-bottom: 0.3rem; }
.funded-news { font-size: 11px; line-height: 1.55; color: #0F172A; font-weight: 500; border-left: 2px solid #059669; padding-left: 0.5rem; margin-bottom: 0.3rem; }
.funding-tag { font-family: 'DM Mono', monospace; font-size: 9px; background: #F0FDF4; color: #15803D; border-radius: 999px; padding: 2px 9px; font-weight: 500; }
.stage-tag { font-family: 'DM Mono', monospace; font-size: 9px; background: #EEF2FF; color: #4338CA; border-radius: 999px; padding: 2px 9px; }
.incubator-tag { font-family: 'DM Mono', monospace; font-size: 9px; background: #FFF7ED; color: #C2410C; border-radius: 999px; padding: 2px 9px; }

/* ── Startup Ecosystem Directory ───────────────────────────────────────────── */
.card-ecosystem-type { background: #F8FAFC; }
.eco-cluster { margin-bottom: 1.25rem; }
.eco-cluster:last-child { margin-bottom: 0; }
.eco-cluster-title {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.12em;
  text-transform: uppercase; color: #6366F1; margin-bottom: 0.6rem;
  padding-bottom: 0.4rem; border-bottom: 1px solid #E2E8F0;
}
.eco-item { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; padding: 0.55rem 0; border-bottom: 1px solid #F1F5F9; }
.eco-item:last-child { border-bottom: none; }
.eco-name { font-size: 13px; font-weight: 600; color: #0F172A; line-height: 1.3; }
.eco-location { font-family: 'DM Mono', monospace; font-size: 9px; color: #94A3B8; }
.eco-right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; flex-shrink: 0; }
.eco-stage { font-family: 'DM Mono', monospace; font-size: 9px; background: #EEF2FF; color: #4338CA; border-radius: 999px; padding: 2px 8px; }
.eco-funding { font-family: 'DM Mono', monospace; font-size: 9px; color: #15803D; font-weight: 500; }

/* ── Progress Rail ─────────────────────────────────────────────────────────── */
.progress-rail { position: fixed; right: 14px; top: 50%; transform: translateY(-50%); width: 3px; height: 80px; background: #E2E8F0; border-radius: 3px; z-index: 100; }
.progress-fill { width: 100%; background: #6366F1; border-radius: 3px; height: 10%; transition: height 0.3s ease; }

/* ── Footer ────────────────────────────────────────────────────────────────── */
.footer-card { height: 100vh; scroll-snap-align: start; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2rem; background: #1E1B4B; }
.footer-brand-lg { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.75rem; }
.footer-sub { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #A5B4FC; margin-bottom: 2rem; }
.footer-restart { font-family: 'DM Mono', monospace; font-size: 11px; color: #F8FAFC; border: 1px solid rgba(165,180,252,0.4); border-radius: 999px; padding: 8px 24px; cursor: pointer; background: transparent; letter-spacing: 0.06em; }
.footer-restart:hover { background: rgba(165,180,252,0.1); }
"""


def render_tn_html(digest: Dict) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    headline            = digest.get("headline", "Tamil Nadu Innovation digest is ready.")
    signal_of_week      = digest.get("signal_of_the_week")
    policy_incentives   = digest.get("policy_incentives", [])
    startup_spotlight   = digest.get("startup_spotlight", [])
    funded_startups     = digest.get("funded_startups", [])
    research_innovation = digest.get("research_innovation", [])
    club_radar          = digest.get("club_radar", [])
    district_pulse      = digest.get("district_pulse", [])
    sector_opps         = digest.get("sector_opportunities", [])
    quick_hits          = digest.get("quick_hits", [])
    leaders_voices      = digest.get("leaders_voices", [])
    vike_note           = digest.get("vike_note", "")

    # Static ecosystem data — always show
    ecosystem_clusters  = get_startups_by_cluster()

    total_cards = (
        1
        + (1 if signal_of_week else 0)
        + (1 if policy_incentives else 0)
        + (1 if startup_spotlight else 0)
        + (1 if funded_startups else 0)         # news-driven funded startups
        + (1 if research_innovation else 0)
        + (1 if club_radar else 0)
        + (1 if district_pulse else 0)
        + (1 if sector_opps else 0)
        + (1 if ecosystem_clusters else 0)      # always shown (static directory)
        + (1 if quick_hits else 0)
        + (1 if leaders_voices else 0)
        + 1   # footer
    )

    cards_html = ""
    card_index = 0

    # ── Header Card ──────────────────────────────────────────────────────────
    vike_block = ""
    if vike_note:
        vike_block = f'<div class="header-note"><strong>This week\'s signal</strong>{vike_note}</div>'

    cards_html += f"""
    <section class="card card-header-type" data-index="0">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.25rem">
        <span style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:0.16em;text-transform:uppercase;color:#64748B">🌟 TN Innovation</span>
        <span class="card-counter">1 / {total_cards}</span>
      </div>
      <div class="card-body">
        <div class="header-date">{date_str} · {time_str} · 7-day digest</div>
        <div class="header-session">🌟 Tamil Nadu Innovation</div>
        <h1 class="header-headline">{headline}</h1>
        {vike_block}
      </div>
      <div class="card-bottom">
        <button class="start-btn" onclick="document.querySelector('.feed').scrollBy({{top:window.innerHeight,behavior:'smooth'}})">Explore TN ↓</button>
        <span class="swipe-hint"><span class="swipe-arrow">↑</span> swipe</span>
      </div>
    </section>"""
    card_index = 1

    # ── Signal of the Week Card (dark) ───────────────────────────────────────
    if signal_of_week:
        card_index += 1
        signals = signal_of_week.get("signals", [])
        tags_html = "".join(f'<span class="signal-tag">{s}</span>' for s in signals[:4])
        cards_html += f"""
    <section class="card card-signal-type" data-index="{card_index - 1}">
      <div class="card-top" style="border-bottom:1px solid rgba(165,180,252,0.15);padding-bottom:0.75rem;margin-bottom:0">
        <span class="signal-label">🌟 Signal of the Week</span>
        <span class="card-counter" style="color:#6366F1">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body" style="padding-top:2rem">
        <div class="signal-theme">{signal_of_week.get('theme','')}</div>
        <p class="signal-why">{signal_of_week.get('why_it_matters','')}</p>
        <div class="signal-tags">{tags_html}</div>
      </div>
      <div class="card-bottom" style="border-top:1px solid rgba(165,180,252,0.15)">
        <span class="swipe-hint" style="color:#A5B4FC"><span class="swipe-arrow">↑</span> swipe up</span>
      </div>
    </section>"""

    # ── Policy & Incentives Card ──────────────────────────────────────────────
    if policy_incentives:
        card_index += 1
        items_html = ""
        for item in policy_incentives:
            impact = item.get("impact_level", "medium")
            url = item.get("url", "#")
            link = f'<a href="{url}" target="_blank" rel="noopener" class="read-btn-sm">Read →</a>' if url and url != "#" else ""
            items_html += f"""
        <div class="item-block">
          <div class="item-title">{item.get('title','')}</div>
          <p class="item-body">{item.get('body','')}</p>
          <div class="item-meta">
            <span class="impact-badge impact-{impact}">Impact: {impact.upper()}</span>
            <span class="source-tag">{item.get('source','')}</span>
            {link}
          </div>
        </div>"""

        cards_html += f"""
    <section class="card card-policy-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#4338CA">🏛 Policy &amp; Incentives</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── Startup Spotlight Card ─────────────────────────────────────────────────
    if startup_spotlight:
        card_index += 1
        items_html = ""
        for s in startup_spotlight:
            url     = s.get("url", "#")
            link    = f'<a href="{url}" target="_blank" rel="noopener" class="read-btn-sm">Read →</a>' if url and url != "#" else ""
            funding = s.get("funding", "Not disclosed")
            stage   = s.get("stage", "")
            loc     = s.get("location", "")
            items_html += f"""
        <div class="item-block">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:0.4rem">
            <div class="startup-name-lg">{s.get('name','')}</div>
            <div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end;flex-shrink:0">
              <span class="sector-badge">{s.get('sector','')}</span>
              {"" if not loc else f'<span class="location-badge">{loc}</span>'}
            </div>
          </div>
          <p class="startup-what">{s.get('what_it_does','')}</p>
          <p class="startup-why">{s.get('why_notable','')}</p>
          <div class="item-meta" style="margin-top:0.6rem">
            {"" if not stage else f'<span class="impact-badge impact-medium">{stage}</span>'}
            <span class="source-tag">💰 {funding}</span>
            {link}
          </div>
        </div>"""

        cards_html += f"""
    <section class="card card-startup-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#7C3AED">🚀 Startup Spotlight</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── Funded & Incubated Startups Card (news-driven) ────────────────────────
    if funded_startups:
        card_index += 1
        items_html = ""
        for s in funded_startups:
            url      = s.get("url", "#")
            link     = f'<a href="{url}" target="_blank" rel="noopener" class="read-btn-sm">Read →</a>' if url and url != "#" else ""
            inc      = s.get("incubator")
            inc_tag  = f'<span class="incubator-tag">{inc}</span>' if inc else ""
            news     = s.get("recent_news", "")
            news_block = f'<p class="funded-news">📌 {news}</p>' if news else ""
            items_html += f"""
        <div class="funded-item">
          <div class="funded-header">
            <div>
              <div class="funded-name">{s.get('name','')}</div>
              <div class="eco-location">{s.get('location','')}</div>
            </div>
            <div class="funded-badges">
              <span class="stage-tag">{s.get('stage','')}</span>
              <span class="funding-tag">{s.get('funding','')}</span>
              {inc_tag}
            </div>
          </div>
          <p class="funded-what">{s.get('what_it_does','')}</p>
          {news_block}
          <div class="item-meta">
            <span class="sector-badge">{s.get('sector','')}</span>
            {link}
          </div>
        </div>"""

        cards_html += f"""
    <section class="card card-pulse-startups-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#059669">💰 Startup Pulse</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── Research & Innovation Card ─────────────────────────────────────────────
    if research_innovation:
        card_index += 1
        items_html = ""
        for r in research_innovation:
            url  = r.get("url", "#")
            link = f'<a href="{url}" target="_blank" rel="noopener" class="read-btn-sm">Read →</a>' if url and url != "#" else ""
            items_html += f"""
        <div class="item-block">
          <div class="item-meta" style="margin-bottom:0.5rem">
            <span class="org-badge">{r.get('institution','')}</span>
            <span class="source-tag">{r.get('source','')}</span>
          </div>
          <div class="item-title">{r.get('title','')}</div>
          <p class="item-body">{r.get('description','')}</p>
          {link}
        </div>"""

        cards_html += f"""
    <section class="card card-research-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#0F766E">🔬 Research &amp; Innovation</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── Club Radar Card ────────────────────────────────────────────────────────
    if club_radar:
        card_index += 1
        items_html = ""
        for c in club_radar:
            url  = c.get("url") or ""
            link = f'<a href="{url}" target="_blank" rel="noopener" class="read-btn-sm">Details →</a>' if url and url != "#" else ""
            items_html += f"""
        <div class="item-block">
          <div class="item-meta" style="margin-bottom:0.5rem">
            <span class="org-badge">{c.get('org','')}</span>
          </div>
          <div class="item-title" style="font-size:0.95rem">{c.get('activity','')}</div>
          <p class="item-note">{c.get('why_follow','')}</p>
          {link}
        </div>"""

        cards_html += f"""
    <section class="card card-club-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#C2410C">🤝 Club Radar</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── District Pulse Card ────────────────────────────────────────────────────
    if district_pulse:
        card_index += 1
        items_html = ""
        for d in district_pulse:
            items_html += f"""
        <div class="district-item">
          <div class="district-header">
            <span class="district-city">{d.get('district','')}</span>
            <span class="district-badge">{d.get('sector_focus','')}</span>
          </div>
          <p class="district-signal">{d.get('signal','')}</p>
          <p class="district-opp">{d.get('opportunity','')}</p>
        </div>"""

        cards_html += f"""
    <section class="card card-district-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#6D28D9">📍 District Pulse</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── Sector Opportunities Card ──────────────────────────────────────────────
    if sector_opps:
        card_index += 1
        items_html = ""
        for opp in sector_opps:
            signals  = opp.get("signals", [])
            tag_html = "".join(f'<span class="sector-signal">{s}</span>' for s in signals[:3])
            items_html += f"""
        <div class="sector-item">
          <div class="sector-name">{opp.get('sector','')} {tag_html}</div>
          <p class="sector-body">{opp.get('opportunity','')}</p>
        </div>"""

        cards_html += f"""
    <section class="card card-sector-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#B45309">📈 Sector Opportunities</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{items_html}</div>
    </section>"""

    # ── TN Startup Ecosystem Directory (static curated) ───────────────────────
    if ecosystem_clusters:
        card_index += 1
        clusters_html = ""
        for cluster_name, startups in ecosystem_clusters.items():
            items_html = ""
            for s in startups:
                inc_tag = f'<span class="incubator-tag" style="font-size:8px">{s["incubator"]}</span>' if s.get("incubator") else ""
                url = s.get("url") or ""
                name_el = f'<a href="{url}" target="_blank" rel="noopener" style="color:#0F172A;text-decoration:none">{s["name"]}</a>' if url else s["name"]
                items_html += f"""
          <div class="eco-item">
            <div>
              <div class="eco-name">{name_el}</div>
              <div class="eco-location">{s['location']} {inc_tag}</div>
            </div>
            <div class="eco-right">
              <span class="eco-stage">{s['stage']}</span>
              <span class="eco-funding">{s['funding']}</span>
            </div>
          </div>"""

            clusters_html += f"""
        <div class="eco-cluster">
          <div class="eco-cluster-title">{cluster_name}</div>
          {items_html}
        </div>"""

        cards_html += f"""
    <section class="card card-ecosystem-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#1D4ED8">🗺 TN Startup Ecosystem</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:9px;color:#94A3B8;margin-bottom:0.75rem;flex-shrink:0">
        {sum(len(v) for v in ecosystem_clusters.values())} notable startups · curated from StartupTN, IITM Pravartak, Inc42, Tracxn
      </div>
      <div class="card-body-scroll">{clusters_html}</div>
    </section>"""

    # ── Quick Hits Card ────────────────────────────────────────────────────────
    if quick_hits:
        card_index += 1
        hits_items = ""
        for hit in quick_hits:
            hits_items += f"""
          <li class="hit-item">
            <span class="hit-dot">▸</span>
            <div>
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

    # ── Leaders Voices Card ────────────────────────────────────────────────────
    if leaders_voices:
        card_index += 1
        leaders_html = ""
        for lv in leaders_voices:
            name     = lv.get("name", "")
            url      = lv.get("url") or ""
            initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
            link_html = f'<a href="{url}" target="_blank" rel="noopener" class="leader-link">Read more →</a>' if url else ""
            leaders_html += f"""
        <div class="leader-item">
          <div class="leader-avatar">{initials}</div>
          <div class="leader-content">
            <div class="leader-name">{name}</div>
            <div class="leader-role">{lv.get('role','')}</div>
            <p class="leader-insight">{lv.get('insight','')}</p>
            <p class="leader-context">{lv.get('context','')}</p>
            {link_html}
          </div>
        </div>"""

        cards_html += f"""
    <section class="card card-leaders-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#4338CA">Leaders&apos; Voices</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">{leaders_html}</div>
    </section>"""

    # ── Footer ─────────────────────────────────────────────────────────────────
    cards_html += f"""
    <section class="footer-card" data-index="{card_index}">
      <div class="footer-brand-lg">🌟 TN Innovation</div>
      <div class="footer-sub">7-day digest · {date_str} · {time_str}</div>
      <button class="footer-restart" onclick="document.querySelector('.feed').scrollTo({{top:0,behavior:'smooth'}})">↑ Back to top</button>
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🌟 TN Innovation Digest · {date_str}</title>
  <meta name="description" content="Weekly Tamil Nadu innovation digest — policies, startups, research, district signals, and club radar.">
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#6366F1">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="TN Innovation">
  <link rel="apple-touch-icon" href="icon-192.png">
  <style>{CSS}</style>
</head>
<body>

<nav class="nav-tab-bar">
  <a class="nav-tab" href="index.html">⚡ Global</a>
  <a class="nav-tab" href="india.html">🇮🇳 India</a>
  <a class="nav-tab active" href="tn.html">🌟 Tamil Nadu</a>
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

  if ('serviceWorker' in navigator) {{
    navigator.serviceWorker.register('/ai-digest/sw.js').catch(() => {{}});
  }}
</script>
</body>
</html>"""

    return html


def save_tn_dashboard(html: str, output_path: str = "docs/tn.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Render] TN Innovation dashboard saved → {output_path}")


if __name__ == "__main__":
    from summarize_tn import _empty_digest
    html = render_tn_html(_empty_digest())
    save_tn_dashboard(html, "/tmp/test_tn.html")
    print(f"Test TN HTML written ({len(html):,} bytes)")
