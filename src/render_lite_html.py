"""
render_lite_html.py — v2
Full-screen swipe-card AI Digest Lite.

UX:
- One card fills the entire viewport
- Swipe up (or scroll) → next card  (CSS scroll-snap)
- Tap anywhere → flip card to see business implications
- Two tabs at top: 🌍 Global | 🇮🇳 India
- Dark premium design, mobile-first, works on desktop too

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
    cid      = f"{section}-{idx}"
    title    = _esc(story.get("title", ""))
    summary  = _esc(story.get("summary", ""))
    impl     = _esc(story.get("implication", ""))
    source   = _esc(story.get("source", ""))
    url      = _esc(story.get("url", "#"))
    category = story.get("category", "News")
    impact   = story.get("impact", "medium")
    date     = _esc(story.get("date", ""))
    icon     = _cat_icon(category)
    imp_cls  = _impact_cls(impact)
    imp_lbl  = impact.upper()
    counter  = f"{idx + 1} / {total}"
    is_last  = (idx == total - 1)

    swipe_hint = "" if is_last else "<p class='swipe-hint'>&#x2191; swipe up for next</p>"
    date_html  = f"<span class='card-date'>{date}</span>" if date else ""

    return f"""  <div class="card-wrap">
    <div class="flip-card" id="fc-{cid}" onclick="flip('{cid}')">
      <div class="flip-inner">

        <!-- FRONT -->
        <div class="flip-front">
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
            <p class="tap-hint">Tap to see business implications &#x21A9;</p>
            {swipe_hint}
          </div>
        </div>

        <!-- BACK -->
        <div class="flip-back">
          <div class="back-hdr">
            <span class="back-label">&#x26A1; Business Implications</span>
            <span class="back-sub">&#x2190; tap to go back</span>
          </div>
          <p class="impl-text">{impl}</p>
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

    # Intro screens (shown before the news cards)
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
<html lang="en">
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
    }}

    html, body {{
      height: 100%;
      overflow: hidden;
      background: #080D1A;
      font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
      color: #F1F5F9;
      -webkit-font-smoothing: antialiased;
    }}

    /* ── Header ── */
    header {{
      position: fixed;
      top: 0; left: 0; right: 0;
      height: var(--hdr);
      background: rgba(8,13,26,0.96);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(255,255,255,0.07);
      z-index: 200;
      display: flex;
      align-items: center;
      padding: 0 16px;
      gap: 12px;
    }}
    .logo {{
      font-size: 14px; font-weight: 800;
      color: #F1F5F9; letter-spacing: -.2px;
      flex-shrink: 0;
    }}
    .logo span {{ color: var(--accent); }}

    .tabs {{
      display: flex; gap: 6px;
      flex: 1; justify-content: center;
    }}
    .tab-btn {{
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 5px 16px;
      color: rgba(255,255,255,0.4);
      font-size: 12px; font-weight: 700;
      cursor: pointer;
      transition: background .2s, color .2s, border-color .2s;
      -webkit-tap-highlight-color: transparent;
    }}
    .tab-btn.active {{
      background: var(--acc2);
      border-color: var(--acc2);
      color: #fff;
    }}
    .hdr-time {{
      font-size: 9px; color: rgba(255,255,255,0.22);
      text-align: right; line-height: 1.5;
      flex-shrink: 0;
    }}

    /* ── Deck ── */
    .deck {{
      position: fixed;
      top: var(--hdr); left: 0; right: 0; bottom: 0;
      overflow-y: scroll;
      scroll-snap-type: y mandatory;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }}
    .deck::-webkit-scrollbar {{ display: none; }}
    .deck.hidden {{ visibility: hidden; pointer-events: none; }}

    /* ── Card wrapper — full viewport height ── */
    .card-wrap {{
      height: calc(100dvh - var(--hdr));
      height: calc(100vh  - var(--hdr));
      scroll-snap-align: start;
      scroll-snap-stop: always;
      display: flex;
    }}

    /* ── Intro screen ── */
    .intro-wrap {{ align-items: center; justify-content: center; }}
    .intro-card {{
      text-align: center;
      padding: 40px 28px;
      max-width: 500px;
    }}
    .intro-label {{
      font-size: 11px; font-weight: 700;
      color: var(--accent);
      letter-spacing: .08em; text-transform: uppercase;
      margin-bottom: 18px;
    }}
    .intro-headline {{
      font-size: clamp(18px, 3.8vw, 26px);
      font-weight: 800; line-height: 1.4;
      color: #F1F5F9; margin-bottom: 28px;
    }}
    .intro-hint {{
      font-size: 11px; color: rgba(255,255,255,0.22);
    }}

    /* ── Flip card ── */
    .flip-card {{
      width: 100%; height: 100%;
      perspective: 1400px;
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
    }}
    .flip-inner {{
      width: 100%; height: 100%;
      position: relative;
      transform-style: preserve-3d;
      transition: transform .52s cubic-bezier(.4,0,.2,1);
    }}
    .flip-card.flipped .flip-inner {{ transform: rotateY(180deg); }}

    /* ── Front ── */
    .flip-front {{
      position: absolute; width: 100%; height: 100%;
      backface-visibility: hidden; -webkit-backface-visibility: hidden;
      display: flex; flex-direction: column;
      padding: 28px 24px 20px;
      background: linear-gradient(155deg, #0F172A 0%, #1A2035 65%, #0F172A 100%);
      overflow: hidden;
    }}
    .meta-row {{
      display: flex; align-items: center;
      gap: 8px; margin-bottom: 20px; flex-wrap: wrap;
    }}
    .cat-pill {{
      font-size: 10px; font-weight: 700;
      color: rgba(255,255,255,0.38);
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 6px; padding: 3px 9px;
      letter-spacing: .03em;
    }}
    .impact-badge {{
      font-size: 9px; font-weight: 900;
      border-radius: 5px; padding: 3px 8px;
      letter-spacing: .06em;
    }}
    .i-high {{ background: rgba(248,113,113,.14); color: #F87171; border: 1px solid rgba(248,113,113,.22); }}
    .i-med  {{ background: rgba(251,191,36,.12);  color: #FBBF24; border: 1px solid rgba(251,191,36,.2);   }}
    .i-low  {{ background: rgba(148,163,184,.09); color: #94A3B8; border: 1px solid rgba(148,163,184,.16); }}
    .card-date {{
      margin-left: auto;
      font-size: 10px; color: rgba(255,255,255,.24); font-weight: 500;
    }}
    .card-title {{
      font-size: clamp(21px, 4.5vw, 30px);
      font-weight: 800; line-height: 1.27;
      color: #F8FAFC; letter-spacing: -.4px;
      margin-bottom: 16px;
      flex: 1; overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 5; -webkit-box-orient: vertical;
    }}
    .card-summary {{
      font-size: 14px; line-height: 1.72;
      color: rgba(255,255,255,.55);
      overflow: hidden; display: -webkit-box;
      -webkit-line-clamp: 3; -webkit-box-orient: vertical;
    }}
    .card-foot {{ margin-top: auto; padding-top: 18px; }}
    .foot-row {{
      display: flex; justify-content: space-between;
      align-items: center; margin-bottom: 11px;
    }}
    .card-source {{
      font-size: 10px; font-weight: 700;
      color: rgba(255,255,255,.26);
      text-transform: uppercase; letter-spacing: .06em;
    }}
    .card-counter {{ font-size: 10px; color: rgba(255,255,255,.16); }}
    .tap-hint {{
      text-align: center; font-size: 11px;
      color: var(--accent); font-weight: 600;
      margin-bottom: 7px; opacity: .85;
    }}
    .swipe-hint {{
      text-align: center; font-size: 10px;
      color: rgba(255,255,255,.16);
    }}

    /* ── Back ── */
    .flip-back {{
      position: absolute; width: 100%; height: 100%;
      backface-visibility: hidden; -webkit-backface-visibility: hidden;
      transform: rotateY(180deg);
      display: flex; flex-direction: column;
      padding: 28px 24px 20px;
      background: linear-gradient(155deg, #1A1040 0%, #0E0928 65%, #170E3E 100%);
      overflow: hidden;
    }}
    .back-hdr {{
      display: flex; align-items: center;
      justify-content: space-between;
      padding-bottom: 14px;
      border-bottom: 1px solid rgba(255,255,255,.08);
      margin-bottom: 18px; flex-shrink: 0;
    }}
    .back-label {{
      font-size: 12px; font-weight: 800;
      color: var(--accent); letter-spacing: .02em;
    }}
    .back-sub {{ font-size: 10px; color: rgba(255,255,255,.2); }}
    .impl-text {{
      font-size: clamp(14px, 2.3vw, 16px);
      line-height: 1.78; color: rgba(255,255,255,.82);
      flex: 1; overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 11; -webkit-box-orient: vertical;
    }}
    .back-foot {{
      margin-top: auto; padding-top: 16px;
      display: flex; justify-content: space-between; align-items: center;
      border-top: 1px solid rgba(255,255,255,.06);
    }}
    .read-link {{
      font-size: 12px; font-weight: 700;
      color: var(--accent); text-decoration: none; padding: 6px 0;
    }}
    .read-link:hover {{ text-decoration: underline; }}
    .back-counter {{ font-size: 10px; color: rgba(255,255,255,.16); }}

    /* ── Desktop: constrain width ── */
    @media (min-width: 768px) {{
      .card-wrap {{ justify-content: center; }}
      .flip-card {{ max-width: 580px; }}
      .intro-wrap {{ justify-content: center; }}
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
  </script>

</body>
</html>"""


def save_lite_dashboard(html: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = len(html.encode()) // 1024
    print(f"[Lite] Saved {size_kb}KB → {path}")
