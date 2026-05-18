"""
render_lite_html.py — v3
Full-screen swipe-card AI Digest Lite.

UX:
- One card fills the entire viewport
- Swipe up (or scroll) → next card  (CSS scroll-snap)
- Tap anywhere → flip card to see implications
- Back panel shows strategic implications + economics & business section
- Light/dark mode toggle in header
- Topic-relevant image on each card front
- Two tabs at top: 🌍 Global | 🇮🇳 India

Published to docs/lite.html on GitHub Pages.
"""

import os
from datetime import datetime, timezone
from typing import Dict


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _impact_cls(impact: str) -> str:
    return {"high": "i-high", "medium": "i-med", "low": "i-low"}.get(
        impact.lower(), "i-low"
    )

def _cat_icon(cat: str) -> str:
    cat = cat.lower()
    if "model"     in cat: return "🧠"
    if "funding"   in cat: return "💰"
    if "policy"    in cat: return "📋"
    if "research"  in cat: return "🔬"
    if "product"   in cat: return "🚀"
    if "open"      in cat: return "🔓"
    if "industry"  in cat: return "🏭"
    if "workforce" in cat: return "👥"
    return "📡"

def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _card(story: dict, idx: int, total: int, section: str) -> str:
    cid        = f"{section}-{idx}"
    title      = _esc(story.get("title", ""))
    summary    = _esc(story.get("summary", ""))
    impl       = _esc(story.get("implication", ""))
    econ_impl  = _esc(story.get("econ_implication", ""))
    source     = _esc(story.get("source", ""))
    url        = _esc(story.get("url", "#"))
    category   = story.get("category", "News")
    impact     = story.get("impact", "medium")
    date       = _esc(story.get("date", ""))
    img_url    = _esc(story.get("image", "").strip())
    icon       = _cat_icon(category)
    imp_cls    = _impact_cls(impact)
    imp_lbl    = impact.upper()
    counter    = f"{idx + 1} / {total}"
    is_last    = (idx == total - 1)

    swipe_hint = "" if is_last else "<p class='swipe-hint'>&#x2191; swipe up for next</p>"
    date_html  = f"<span class='card-date'>{date}</span>" if date else ""

    img_block = ""
    if img_url:
        img_block = f"""          <div class="card-img-wrap">
            <img src="{img_url}" class="card-img" alt="" loading="lazy" onerror="this.parentElement.style.display='none'">
            <div class="img-overlay"></div>
          </div>"""

    content_cls = "card-content" if img_url else "card-content no-img"

    econ_block = ""
    if econ_impl:
        econ_block = f"""          <div class="econ-section">
            <div class="econ-hdr">&#x1F4C8; Economics &amp; Business</div>
            <p class="econ-text">{econ_impl}</p>
          </div>"""

    return f"""  <div class="card-wrap">
    <div class="flip-card" id="fc-{cid}" onclick="flip('{cid}')">
      <div class="flip-inner">

        <!-- FRONT -->
        <div class="flip-front">
{img_block}
          <div class="{content_cls}">
            <div class="meta-row">
              <span class="cat-pill">{icon} {_esc(category)}</span>
              <span class="impact-badge {imp_cls}">{imp_lbl}</span>
              {date_html}
            </div>
            <h2 class="card-title">{title}</h2>
            <p class="card-summary">{summary}</p>
            <div class="card-foot">
              <div class="foot-row">
                <span class="card-source">{source}</span>
                <span class="card-counter">{counter}</span>
              </div>
              <p class="tap-hint">Tap to see implications &#x21A9;</p>
              {swipe_hint}
            </div>
          </div>
        </div>

        <!-- BACK -->
        <div class="flip-back">
          <div class="back-hdr">
            <span class="back-label">&#x26A1; Business Implications</span>
            <span class="back-sub">&#x2190; tap to go back</span>
          </div>
          <div class="impl-section">
            <p class="impl-text">{impl}</p>
          </div>
{econ_block}
          <div class="back-foot">
            <a href="{url}" target="_blank" rel="noopener"
               onclick="event.stopPropagation()" class="read-link">Read full story &#x2197;</a>
            <span class="back-counter">{counter}</span>
          </div>
        </div>

      </div>
    </div>
  </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Main renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_lite_html(digest: Dict) -> str:
    now            = datetime.now(timezone.utc)
    date_str       = now.strftime("%b %d, %Y")
    time_str       = now.strftime("%H:%M UTC")
    global_stories = digest.get("global", [])
    india_stories  = digest.get("india",  [])
    g_headline     = _esc(digest.get("global_headline", ""))
    i_headline     = _esc(digest.get("india_headline",  ""))
    g_count        = len(global_stories)
    i_count        = len(india_stories)

    global_cards = "\n".join(
        _card(s, i, g_count, "g") for i, s in enumerate(global_stories)
    )
    india_cards = "\n".join(
        _card(s, i, i_count, "i") for i, s in enumerate(india_stories)
    )

    g_intro = f"""  <div class="card-wrap intro-wrap">
    <div class="intro-card">
      <div class="intro-label">&#x1F30D; Global AI &middot; {date_str}</div>
      <p class="intro-headline">{g_headline}</p>
      <p class="intro-hint">&#x2191; Swipe up to start &nbsp;&middot;&nbsp; Tap cards to flip</p>
    </div>
  </div>""" if g_headline else ""

    i_intro = f"""  <div class="card-wrap intro-wrap">
    <div class="intro-card">
      <div class="intro-label">&#x1F1EE;&#x1F1F3; India AI &middot; {date_str}</div>
      <p class="intro-headline">{i_headline}</p>
      <p class="intro-hint">&#x2191; Swipe up to start &nbsp;&middot;&nbsp; Tap cards to flip</p>
    </div>
  </div>""" if i_headline else ""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>&#x26A1; AI Digest Lite &middot; {date_str}</title>
  <meta name="description" content="AI business briefing for leaders &mdash; one card at a time. Swipe up, tap to flip.">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x26A1;</text></svg>">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --hdr:    56px;
      --accent: #818CF8;
      --acc2:   #6366F1;
      --bg:           #080D1A;
      --text:         #F1F5F9;
      --title:        #F8FAFC;
      --hdr-bg:       rgba(8,13,26,0.96);
      --hdr-border:   rgba(255,255,255,0.07);
      --tab-bg:       rgba(255,255,255,0.05);
      --tab-border:   rgba(255,255,255,0.1);
      --tab-text:     rgba(255,255,255,0.4);
      --front-bg:     linear-gradient(155deg,#0F172A 0%,#1A2035 65%,#0F172A 100%);
      --back-bg:      linear-gradient(155deg,#1A1040 0%,#0E0928 65%,#170E3E 100%);
      --pill-bg:      rgba(255,255,255,0.05);
      --pill-border:  rgba(255,255,255,0.08);
      --pill-text:    rgba(255,255,255,0.38);
      --summary:      rgba(255,255,255,.55);
      --source:       rgba(255,255,255,.26);
      --counter:      rgba(255,255,255,.16);
      --time-text:    rgba(255,255,255,0.22);
      --swipe:        rgba(255,255,255,.16);
      --inner-border: rgba(255,255,255,.08);
      --back-border:  rgba(255,255,255,.06);
      --back-sub:     rgba(255,255,255,.2);
      --impl:         rgba(255,255,255,.82);
      --econ-bg:      rgba(255,255,255,.04);
      --econ-border:  rgba(255,255,255,.12);
      --econ-lbl:     rgba(129,140,248,.85);
      --intro-hint:   rgba(255,255,255,0.22);
      --date-text:    rgba(255,255,255,.24);
      --toggle-bg:    rgba(255,255,255,.08);
      --toggle-border: rgba(255,255,255,.14);
      --img-overlay:  linear-gradient(to bottom,rgba(0,0,0,0) 0%,rgba(0,0,0,0.6) 100%);
    }}

    html[data-theme="light"] {{
      --bg:           #F0F4FF;
      --text:         #1E293B;
      --title:        #0F172A;
      --hdr-bg:       rgba(240,244,255,0.97);
      --hdr-border:   rgba(0,0,0,0.09);
      --tab-bg:       rgba(0,0,0,0.05);
      --tab-border:   rgba(0,0,0,0.1);
      --tab-text:     rgba(0,0,0,0.45);
      --front-bg:     linear-gradient(155deg,#FFFFFF 0%,#EEF2FF 65%,#FFFFFF 100%);
      --back-bg:      linear-gradient(155deg,#EDE9FE 0%,#DDD6FE 65%,#EDE9FE 100%);
      --pill-bg:      rgba(0,0,0,0.05);
      --pill-border:  rgba(0,0,0,0.1);
      --pill-text:    rgba(0,0,0,0.5);
      --summary:      rgba(15,23,42,.65);
      --source:       rgba(15,23,42,.45);
      --counter:      rgba(15,23,42,.3);
      --time-text:    rgba(0,0,0,0.38);
      --swipe:        rgba(0,0,0,.28);
      --inner-border: rgba(0,0,0,.1);
      --back-border:  rgba(0,0,0,.08);
      --back-sub:     rgba(0,0,0,.32);
      --impl:         rgba(15,23,42,.88);
      --econ-bg:      rgba(99,102,241,.07);
      --econ-border:  rgba(99,102,241,.22);
      --econ-lbl:     rgba(79,70,229,.85);
      --intro-hint:   rgba(0,0,0,.38);
      --date-text:    rgba(0,0,0,.35);
      --toggle-bg:    rgba(0,0,0,.06);
      --toggle-border: rgba(0,0,0,.13);
      --img-overlay:  linear-gradient(to bottom,rgba(255,255,255,0) 0%,rgba(240,244,255,0.45) 100%);
    }}

    html, body {{
      height: 100%; overflow: hidden;
      background: var(--bg);
      font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
      color: var(--text);
      -webkit-font-smoothing: antialiased;
      transition: background .3s, color .3s;
    }}

    /* ── Header ── */
    header {{
      position: fixed; top: 0; left: 0; right: 0;
      height: var(--hdr);
      background: var(--hdr-bg);
      backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--hdr-border);
      z-index: 200;
      display: flex; align-items: center;
      padding: 0 10px; gap: 8px;
    }}
    .logo {{
      font-size: 14px; font-weight: 800;
      color: var(--text); letter-spacing: -.2px; flex-shrink: 0;
    }}
    .logo span {{ color: var(--accent); }}
    .tabs {{ display: flex; gap: 6px; flex: 1; justify-content: center; }}
    .tab-btn {{
      background: var(--tab-bg);
      border: 1px solid var(--tab-border);
      border-radius: 20px; padding: 5px 13px;
      color: var(--tab-text);
      font-size: 12px; font-weight: 700; cursor: pointer;
      transition: background .2s, color .2s, border-color .2s;
      -webkit-tap-highlight-color: transparent;
    }}
    .tab-btn.active {{ background: var(--acc2); border-color: var(--acc2); color: #fff; }}
    .hdr-time {{
      font-size: 9px; color: var(--time-text);
      text-align: right; line-height: 1.5; flex-shrink: 0;
    }}
    .theme-toggle {{
      background: var(--toggle-bg);
      border: 1px solid var(--toggle-border);
      border-radius: 50%; width: 30px; height: 30px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; font-size: 15px; flex-shrink: 0;
      -webkit-tap-highlight-color: transparent;
      transition: background .2s;
    }}

    /* ── Deck ── */
    .deck {{
      position: fixed; top: var(--hdr); left: 0; right: 0; bottom: 0;
      overflow-y: scroll; scroll-snap-type: y mandatory;
      -webkit-overflow-scrolling: touch; scrollbar-width: none;
    }}
    .deck::-webkit-scrollbar {{ display: none; }}
    .deck.hidden {{ visibility: hidden; pointer-events: none; }}

    /* ── Card wrapper ── */
    .card-wrap {{
      height: calc(100dvh - var(--hdr));
      height: calc(100vh  - var(--hdr));
      scroll-snap-align: start; scroll-snap-stop: always;
      display: flex;
    }}

    /* ── Intro screen ── */
    .intro-wrap {{ align-items: center; justify-content: center; }}
    .intro-card {{ text-align: center; padding: 40px 28px; max-width: 500px; }}
    .intro-label {{
      font-size: 11px; font-weight: 700; color: var(--accent);
      letter-spacing: .08em; text-transform: uppercase; margin-bottom: 18px;
    }}
    .intro-headline {{
      font-size: clamp(18px, 3.8vw, 26px); font-weight: 800; line-height: 1.4;
      color: var(--title); margin-bottom: 28px;
    }}
    .intro-hint {{ font-size: 11px; color: var(--intro-hint); }}

    /* ── Flip card ── */
    .flip-card {{
      width: 100%; height: 100%;
      perspective: 1400px; cursor: pointer;
      -webkit-tap-highlight-color: transparent;
    }}
    .flip-inner {{
      width: 100%; height: 100%; position: relative;
      transform-style: preserve-3d;
      transition: transform .52s cubic-bezier(.4,0,.2,1);
    }}
    .flip-card.flipped .flip-inner {{ transform: rotateY(180deg); }}

    /* ── Front ── */
    .flip-front {{
      position: absolute; width: 100%; height: 100%;
      backface-visibility: hidden; -webkit-backface-visibility: hidden;
      display: flex; flex-direction: column;
      background: var(--front-bg); overflow: hidden;
    }}

    /* ── Card image ── */
    .card-img-wrap {{
      position: relative; width: 100%; height: 150px;
      flex-shrink: 0; overflow: hidden;
    }}
    .card-img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .img-overlay {{ position: absolute; inset: 0; background: var(--img-overlay); }}

    .card-content {{
      display: flex; flex-direction: column; flex: 1;
      padding: 16px 22px 14px; overflow: hidden;
    }}
    .card-content.no-img {{ padding-top: 26px; }}

    .meta-row {{
      display: flex; align-items: center;
      gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
    }}
    .cat-pill {{
      font-size: 10px; font-weight: 700;
      color: var(--pill-text); background: var(--pill-bg);
      border: 1px solid var(--pill-border);
      border-radius: 6px; padding: 3px 9px; letter-spacing: .03em;
    }}
    .impact-badge {{
      font-size: 9px; font-weight: 900;
      border-radius: 5px; padding: 3px 8px; letter-spacing: .06em;
    }}
    .i-high {{ background: rgba(248,113,113,.14); color: #F87171; border: 1px solid rgba(248,113,113,.22); }}
    .i-med  {{ background: rgba(251,191,36,.12);  color: #FBBF24; border: 1px solid rgba(251,191,36,.2);   }}
    .i-low  {{ background: rgba(148,163,184,.09); color: #94A3B8; border: 1px solid rgba(148,163,184,.16); }}
    html[data-theme="light"] .i-high {{ background: rgba(220,38,38,.1);  color: #DC2626; border-color: rgba(220,38,38,.2);  }}
    html[data-theme="light"] .i-med  {{ background: rgba(180,83,9,.09);  color: #B45309; border-color: rgba(180,83,9,.18);  }}
    html[data-theme="light"] .i-low  {{ background: rgba(71,85,105,.08); color: #475569; border-color: rgba(71,85,105,.15); }}

    .card-date {{ margin-left: auto; font-size: 10px; color: var(--date-text); font-weight: 500; }}

    .card-title {{
      font-size: clamp(19px, 4.2vw, 27px);
      font-weight: 800; line-height: 1.27; color: var(--title);
      letter-spacing: -.4px; margin-bottom: 10px;
      overflow: hidden; display: -webkit-box;
      -webkit-line-clamp: 4; -webkit-box-orient: vertical;
    }}
    .card-summary {{
      font-size: 13px; line-height: 1.68; color: var(--summary);
      overflow: hidden; display: -webkit-box;
      -webkit-line-clamp: 2; -webkit-box-orient: vertical;
      flex: 1;
    }}
    .card-foot {{ margin-top: auto; padding-top: 12px; }}
    .foot-row {{
      display: flex; justify-content: space-between;
      align-items: center; margin-bottom: 9px;
    }}
    .card-source {{
      font-size: 10px; font-weight: 700; color: var(--source);
      text-transform: uppercase; letter-spacing: .06em;
    }}
    .card-counter {{ font-size: 10px; color: var(--counter); }}
    .tap-hint {{
      text-align: center; font-size: 11px;
      color: var(--accent); font-weight: 600;
      margin-bottom: 6px; opacity: .85;
    }}
    .swipe-hint {{ text-align: center; font-size: 10px; color: var(--swipe); }}

    /* ── Back ── */
    .flip-back {{
      position: absolute; width: 100%; height: 100%;
      backface-visibility: hidden; -webkit-backface-visibility: hidden;
      transform: rotateY(180deg);
      display: flex; flex-direction: column;
      padding: 20px 22px 16px;
      background: var(--back-bg); overflow: hidden;
    }}
    .back-hdr {{
      display: flex; align-items: center; justify-content: space-between;
      padding-bottom: 11px;
      border-bottom: 1px solid var(--inner-border);
      margin-bottom: 12px; flex-shrink: 0;
    }}
    .back-label {{ font-size: 12px; font-weight: 800; color: var(--accent); letter-spacing: .02em; }}
    .back-sub   {{ font-size: 10px; color: var(--back-sub); }}

    /* strategic implications */
    .impl-section {{ flex: 1; overflow: hidden; margin-bottom: 10px; }}
    .impl-text {{
      font-size: clamp(13px, 2.1vw, 15px);
      line-height: 1.72; color: var(--impl);
      overflow: hidden; display: -webkit-box;
      -webkit-line-clamp: 6; -webkit-box-orient: vertical;
    }}

    /* economics & business section */
    .econ-section {{
      background: var(--econ-bg); border: 1px solid var(--econ-border);
      border-radius: 10px; padding: 11px 13px;
      flex-shrink: 0; margin-bottom: 10px;
    }}
    .econ-hdr {{
      font-size: 10px; font-weight: 800; color: var(--econ-lbl);
      letter-spacing: .06em; text-transform: uppercase; margin-bottom: 6px;
    }}
    .econ-text {{
      font-size: clamp(12px, 1.9vw, 13px);
      line-height: 1.62; color: var(--impl);
      overflow: hidden; display: -webkit-box;
      -webkit-line-clamp: 4; -webkit-box-orient: vertical;
    }}

    .back-foot {{
      padding-top: 12px; flex-shrink: 0;
      display: flex; justify-content: space-between; align-items: center;
      border-top: 1px solid var(--back-border);
    }}
    .read-link {{
      font-size: 12px; font-weight: 700;
      color: var(--accent); text-decoration: none; padding: 6px 0;
    }}
    .read-link:hover {{ text-decoration: underline; }}
    .back-counter {{ font-size: 10px; color: var(--counter); }}

    /* ── Desktop: constrain width ── */
    @media (min-width: 768px) {{
      .card-wrap {{ justify-content: center; }}
      .flip-card {{ max-width: 580px; }}
      .intro-wrap {{ justify-content: center; }}
      .card-img-wrap {{ height: 180px; }}
    }}

    /* ── Notch / safe-area ── */
    @supports (padding: env(safe-area-inset-bottom)) {{
      .card-foot, .back-foot {{
        padding-bottom: calc(8px + env(safe-area-inset-bottom));
      }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo">&#x26A1; AI <span>Lite</span></div>
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('global',this)">&#x1F30D; Global <small style="opacity:.55">({g_count})</small></button>
      <button class="tab-btn"        onclick="switchTab('india',this)" >&#x1F1EE;&#x1F1F3; India <small style="opacity:.55">({i_count})</small></button>
    </div>
    <div class="hdr-time">{date_str}<br>{time_str}</div>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme" aria-label="Toggle light/dark mode">&#x2600;&#xFE0F;</button>
  </header>

  <div class="deck" id="deck-global">
{g_intro}
{global_cards}
  </div>

  <div class="deck hidden" id="deck-india">
{i_intro}
{india_cards}
  </div>

  <script>
    function flip(id) {{
      var c = document.getElementById('fc-' + id);
      if (c) c.classList.toggle('flipped');
    }}
    function switchTab(tab, btn) {{
      document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.remove('active'); }});
      btn.classList.add('active');
      var g = document.getElementById('deck-global');
      var i = document.getElementById('deck-india');
      if (tab === 'global') {{
        g.classList.remove('hidden'); i.classList.add('hidden');
        g.scrollTo({{top:0,behavior:'instant'}});
      }} else {{
        i.classList.remove('hidden'); g.classList.add('hidden');
        i.scrollTo({{top:0,behavior:'instant'}});
      }}
    }}
    function toggleTheme() {{
      var html = document.documentElement;
      var btn  = document.querySelector('.theme-toggle');
      if (html.getAttribute('data-theme') === 'dark') {{
        html.setAttribute('data-theme', 'light');
        btn.innerHTML = '&#x1F319;';
      }} else {{
        html.setAttribute('data-theme', 'dark');
        btn.innerHTML = '&#x2600;&#xFE0F;';
      }}
    }}
  </script>

</body>
</html>"""


def save_lite_dashboard(html: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = len(html.encode()) // 1024
    print(f"[Lite] Saved {size_kb}KB → {path}")
