"""
render_india_html.py
Renders the India AI Pulse digest as a beige card-swipe dashboard.
Focused on funding rounds, new startups, VC trends, and policy.
Output: docs/india.html (served by GitHub Pages)
"""

import os
from datetime import datetime, timezone
from typing import Dict

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; }

body { background: #F8FAFC; font-family: 'Inter', sans-serif; color: #0F172A; }

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

.feed {
  height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory;
  -webkit-overflow-scrolling: touch; scrollbar-width: none;
}
.feed::-webkit-scrollbar { display: none; }

.card {
  height: 100vh; scroll-snap-align: start; scroll-snap-stop: always;
  display: flex; flex-direction: column;
  padding: 72px 2rem 2rem;
  border-bottom: 1px solid #E2E8F0; overflow: hidden;
}

.card-header-type  { background: #0F172A; }
.card-funding-type { background: #FFFFFF; }
.card-startup-type { background: #F8FAFC; }
.card-trend-type   { background: #F1F5F9; }
.card-policy-type  { background: #FFFFFF; }
.card-hits-type    { background: #F8FAFC; }

.card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; flex-shrink: 0; }

.category-pill {
  font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.08em;
  text-transform: uppercase; color: #fff; border-radius: 999px; padding: 4px 14px;
}

.card-counter { font-family: 'DM Mono', monospace; font-size: 11px; color: #94A3B8; }

.card-body { display: flex; flex-direction: column; flex-shrink: 0; }

.card-bottom {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 1.5rem; padding-top: 1rem;
  border-top: 1px solid #E2E8F0; flex-shrink: 0;
}
.card-header-type .card-bottom { border-top-color: rgba(255,255,255,0.1); }

.read-btn {
  font-family: 'DM Mono', monospace; font-size: 11px; color: #6366F1;
  border: 1.5px solid #6366F1; border-radius: 999px; padding: 8px 20px;
  text-decoration: none; letter-spacing: 0.04em; transition: background 0.15s, color 0.15s;
}
.read-btn:hover { background: #6366F1; color: #fff; }

.swipe-hint { font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8; display: flex; align-items: center; gap: 5px; }
.swipe-arrow { animation: bounce 1.6s ease-in-out infinite; display: inline-block; }
@keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

.card-divider { width: 36px; height: 2px; background: #6366F1; border-radius: 2px; margin-bottom: 1rem; }

/* Header */
.header-date { font-family: 'DM Mono', monospace; font-size: 10px; color: #64748B; margin-bottom: 1rem; letter-spacing: 0.06em; }
.header-headline { font-family: 'Playfair Display', serif; font-size: clamp(1.5rem, 4.5vw, 2.3rem); font-weight: 800; line-height: 1.2; color: #F8FAFC; margin-bottom: 1.5rem; }
.header-note { font-size: 13px; line-height: 1.75; color: #94A3B8; border-left: 3px solid #6366F1; padding-left: 1rem; max-width: 540px; }
.header-note strong { color: #A5B4FC; font-size: 10px; font-family: 'DM Mono', monospace; letter-spacing: 0.08em; text-transform: uppercase; display: block; margin-bottom: 0.4rem; }
.start-btn { font-family: 'DM Mono', monospace; font-size: 11px; background: #6366F1; color: #fff; border: none; border-radius: 999px; padding: 10px 26px; cursor: pointer; letter-spacing: 0.06em; text-transform: uppercase; }
.start-btn:hover { background: #4F46E5; }

/* Funding */
.startup-name-lg { font-family: 'Playfair Display', serif; font-size: clamp(1.5rem, 4vw, 2rem); font-weight: 800; color: #0F172A; line-height: 1.1; margin-bottom: 0.4rem; }
.funding-amount-lg { font-family: 'DM Mono', monospace; font-size: clamp(2rem, 7vw, 3rem); font-weight: 500; color: #059669; line-height: 1; margin-bottom: 0.75rem; }
.funding-meta-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.meta-chip { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; background: #EEF2FF; color: #4338CA; border-radius: 999px; padding: 4px 12px; }
.funding-focus { font-size: 13.5px; line-height: 1.7; color: #475569; }

/* Startup */
.startup-name-md { font-family: 'Playfair Display', serif; font-size: clamp(1.3rem, 3.5vw, 1.75rem); font-weight: 700; color: #0F172A; margin-bottom: 0.3rem; }
.founder-line { font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 1rem; }
.startup-what { font-size: 14px; line-height: 1.7; color: #475569; margin-bottom: 0.6rem; }
.startup-why { font-size: 13px; line-height: 1.65; color: #64748B; border-left: 2px solid #6366F1; padding-left: 0.75rem; font-style: italic; }

/* Trends */
.trend-item { margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #E2E8F0; }
.trend-item:last-child { border-bottom: none; margin-bottom: 0; }
.trend-title { font-family: 'Playfair Display', serif; font-size: 1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem; }
.trend-detail { font-size: 13px; color: #475569; line-height: 1.7; }

/* Policy */
.policy-title-lg { font-family: 'Playfair Display', serif; font-size: clamp(1.1rem, 3vw, 1.4rem); font-weight: 700; color: #0F172A; margin-bottom: 0.75rem; line-height: 1.3; text-decoration: none; display: block; }
.policy-title-lg:hover { color: #6366F1; }
.policy-body { font-size: 14px; line-height: 1.75; color: #475569; }
.policy-source { font-family: 'DM Mono', monospace; font-size: 10px; color: #94A3B8; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 0.75rem; display: block; }

/* Quick hits */
.hits-list { list-style: none; }
.hit-item { padding: 0.85rem 0; border-bottom: 1px solid #E2E8F0; display: flex; gap: 0.75rem; align-items: flex-start; }
.hit-item:last-child { border-bottom: none; }
.hit-dot { color: #6366F1; font-size: 12px; flex-shrink: 0; margin-top: 3px; }
.hit-title { font-size: 13px; font-weight: 500; color: #0F172A; text-decoration: none; line-height: 1.4; }
.hit-title:hover { color: #6366F1; }
.hit-source { font-size: 10px; color: #94A3B8; font-family: 'DM Mono', monospace; margin-left: 4px; }
.hit-liner { font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5; }

/* card-body-scroll */
.card-body-scroll { display: flex; flex-direction: column; flex: 1; overflow-y: auto; min-height: 0; }

/* Leaders Voices */
.card-leaders-type { background: #FAFAFA; }
.leader-item { padding: 1rem 0; border-bottom: 1px solid #E2E8F0; display: flex; gap: 1rem; align-items: flex-start; }
.leader-item:last-child { border-bottom: none; }
.leader-avatar { width: 40px; height: 40px; border-radius: 50%; background: #EEF2FF; border: 2px solid #6366F1; display: flex; align-items: center; justify-content: center; font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; color: #4338CA; flex-shrink: 0; }
.leader-content { flex: 1; min-width: 0; }
.leader-name { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #0F172A; margin-bottom: 1px; }
.leader-role { font-family: 'DM Mono', monospace; font-size: 9px; color: #94A3B8; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.leader-insight { font-size: 13px; line-height: 1.65; color: #334155; margin-bottom: 0.3rem; }
.leader-context { font-size: 11px; color: #94A3B8; line-height: 1.5; }
.leader-link { font-family: 'DM Mono', monospace; font-size: 9px; color: #6366F1; text-decoration: none; margin-top: 0.35rem; display: inline-block; }
.leader-link:hover { text-decoration: underline; }

/* Progress rail */
.progress-rail { position: fixed; right: 14px; top: 50%; transform: translateY(-50%); width: 3px; height: 80px; background: #E2E8F0; border-radius: 3px; z-index: 100; }
.progress-fill { width: 100%; background: #6366F1; border-radius: 3px; height: 10%; transition: height 0.3s ease; }

/* Footer */
.footer-card { height: 100vh; scroll-snap-align: start; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2rem; background: #1E1B4B; }
.footer-brand-lg { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.75rem; }
.footer-sub { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #A5B4FC; margin-bottom: 2rem; }
.footer-restart { font-family: 'DM Mono', monospace; font-size: 11px; color: #F8FAFC; border: 1px solid rgba(165,180,252,0.4); border-radius: 999px; padding: 8px 24px; cursor: pointer; background: transparent; letter-spacing: 0.06em; }
.footer-restart:hover { background: rgba(165,180,252,0.1); }
"""


def render_india_html(digest: Dict) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    headline        = digest.get("headline", "India AI Pulse is ready.")
    funding_rounds  = digest.get("funding_rounds", [])
    new_startups    = digest.get("new_startups", [])
    vc_trends       = digest.get("vc_trends", [])
    policy_watch    = digest.get("policy_watch", [])
    quick_hits      = digest.get("quick_hits", [])
    leaders_voices  = digest.get("leaders_voices", [])
    vike_note       = digest.get("vike_note", "")

    total_cards = (
        1
        + len(funding_rounds)
        + (1 if new_startups else 0)
        + (1 if vc_trends else 0)
        + (1 if policy_watch else 0)
        + (1 if quick_hits else 0)
        + (1 if leaders_voices else 0)
        + 1   # footer
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
        <span style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:0.16em;text-transform:uppercase;color:#64748B">🇮🇳 India AI Pulse</span>
        <span class="card-counter">1 / {total_cards}</span>
      </div>
      <div class="card-body" style="padding-bottom:80px">
        <div class="header-date">{date_str} · {time_str}</div>
        <h1 class="header-headline">{headline}</h1>
        {vike_block}
      </div>
      <div class="card-bottom">
        <button class="start-btn" onclick="document.querySelector('.feed').scrollBy({{top:window.innerHeight,behavior:'smooth'}})">Read today's pulse ↓</button>
        <span class="swipe-hint" style="color:#475569"><span class="swipe-arrow">↑</span> swipe up</span>
      </div>
    </section>"""
    card_index = 1

    # ── Funding Round Cards ───────────────────────────────────────────────────
    for r in funding_rounds:
        card_index += 1
        stage_chip    = f'<span class="meta-chip">{r.get("stage","")}</span>' if r.get("stage") else ""
        investor_chip = f'<span class="meta-chip">🏦 {r.get("investors","")}</span>' if r.get("investors") else ""

        cards_html += f"""
    <section class="card card-funding-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#059669">Funding</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body">
        <div class="startup-name-lg">{r.get("startup","")}</div>
        <div class="funding-amount-lg">{r.get("amount","Undisclosed")}</div>
        <div class="funding-meta-row">{stage_chip}{investor_chip}</div>
        <div class="card-divider"></div>
        <p class="funding-focus">{r.get("focus","")}</p>
      </div>
      <div class="card-bottom">
        <a href="{r.get('url','#')}" target="_blank" rel="noopener" class="read-btn">Read full story →</a>
      </div>
    </section>"""

    # ── New Startups Card ─────────────────────────────────────────────────────
    if new_startups:
        card_index += 1
        startups_inner = ""
        for s in new_startups:
            startups_inner += f"""
        <div style="margin-bottom:1.5rem;padding-bottom:1.5rem;border-bottom:1px solid #E2E8F0">
          <div class="startup-name-md">{s.get("name","")}</div>
          <div class="founder-line">by {s.get("founded_by","Unknown")}</div>
          <p class="startup-what">{s.get("what_it_does","")}</p>
          <p class="startup-why">{s.get("why_interesting","")}</p>
          <a href="{s.get('url','#')}" target="_blank" rel="noopener" class="read-btn" style="display:inline-block;margin-top:0.75rem">Read more →</a>
        </div>"""

        cards_html += f"""
    <section class="card card-startup-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#7C3AED">New Startups</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">
        {startups_inner}
      </div>
    </section>"""

    # ── VC Trends Card ────────────────────────────────────────────────────────
    if vc_trends:
        card_index += 1
        trends_inner = ""
        for t in vc_trends:
            trends_inner += f"""
        <div class="trend-item">
          <div class="trend-title">{t.get("trend","")}</div>
          <p class="trend-detail">{t.get("detail","")}</p>
        </div>"""

        cards_html += f"""
    <section class="card card-trend-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#5C3D2E">VC Trends</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">
        {trends_inner}
      </div>
    </section>"""

    # ── Policy Watch Cards ────────────────────────────────────────────────────
    if policy_watch:
        card_index += 1
        policy_inner = ""
        for p in policy_watch:
            policy_inner += f"""
        <div style="margin-bottom:1.5rem;padding-bottom:1.5rem;border-bottom:1px solid #E2E8F0">
          <a href="{p.get('url','#')}" target="_blank" rel="noopener" class="policy-title-lg">{p.get("title","")}</a>
          <p class="policy-body">{p.get("body","")}</p>
          <span class="policy-source">{p.get("source","")}</span>
        </div>"""

        cards_html += f"""
    <section class="card card-policy-type" data-index="{card_index - 1}">
      <div class="card-top">
        <span class="category-pill" style="background:#3B4852">Policy Watch</span>
        <span class="card-counter">{card_index} / {total_cards}</span>
      </div>
      <div class="card-body-scroll">
        {policy_inner}
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

    # ── Footer Card ───────────────────────────────────────────────────────────
    cards_html += f"""
    <section class="footer-card" data-index="{card_index}">
      <div class="footer-brand-lg">🇮🇳 India AI Pulse</div>
      <div class="footer-sub">Generated {date_str} · {time_str}</div>
      <button class="footer-restart" onclick="document.querySelector('.feed').scrollTo({{top:0,behavior:'smooth'}})">↑ Back to top</button>
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🇮🇳 India AI Pulse · {date_str}</title>
  <meta name="description" content="Daily digest of AI investments, startups, and VC trends in India.">
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#6366F1">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="India AI Pulse">
  <link rel="apple-touch-icon" href="icon-192.png">
  <style>{CSS}</style>
</head>
<body>

<nav class="nav-tab-bar">
  <a class="nav-tab" href="index.html">⚡ Global</a>
  <a class="nav-tab active" href="india.html">🇮🇳 India</a>
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


def save_india_dashboard(html: str, output_path: str = "docs/india.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Render] India dashboard saved → {output_path}")


if __name__ == "__main__":
    dummy = {
        "headline": "Sarvam AI raises $41M Series B; Peak XV doubles down on India LLMs",
        "funding_rounds": [{"startup": "Sarvam AI", "amount": "$41M", "stage": "Series B", "investors": "Peak XV Partners", "focus": "India-specific LLMs across 22 languages.", "url": "#", "source": "Inc42"}],
        "new_startups": [],
        "vc_trends": [{"trend": "Vernacular AI getting serious capital", "detail": "VCs are betting on language-specific models for Tier 2/3 India."}],
        "policy_watch": [],
        "quick_hits": [],
        "vike_note": "Vernacular + voice is where the India AI moat is — not another ChatGPT wrapper.",
    }
    html = render_india_html(dummy)
    save_india_dashboard(html, "/tmp/test_india.html")
    print(f"Test India HTML written ({len(html):,} bytes)")
