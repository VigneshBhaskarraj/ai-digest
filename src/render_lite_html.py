"""
render_lite_html.py
Renders AI Digest Lite — a two-column flip-card page covering Global + India news.
Published to docs/lite.html on GitHub Pages.

Design:
- Two columns: Global (left) | India (right), stack on mobile
- Flip card on click: front = headline + 2-line summary, back = real-world implication
- Clean, modern — distinct from the swipe-card main digest
- Impact badges: HIGH (red) / MED (amber) / LOW (slate)
- Category pill on each card
"""

import os
from datetime import datetime, timezone
from typing import Dict


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _impact_class(impact: str) -> str:
    return {"high": "impact-high", "medium": "impact-med", "low": "impact-low"}.get(
        impact.lower(), "impact-low"
    )

def _category_icon(cat: str) -> str:
    cat = cat.lower()
    if "model"    in cat: return "🧠"
    if "funding"  in cat: return "💰"
    if "policy"   in cat: return "📋"
    if "research" in cat: return "🔬"
    if "product"  in cat: return "🚀"
    if "open"     in cat: return "🔓"
    if "industry" in cat: return "🏭"
    return "📡"

def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def _card(story: dict, idx: int, section: str) -> str:
    card_id   = f"{section}-{idx}"
    title     = _esc(story.get("title", ""))
    summary   = _esc(story.get("summary", ""))
    impl      = _esc(story.get("implication", ""))
    source    = _esc(story.get("source", ""))
    url       = _esc(story.get("url", "#"))
    category  = story.get("category", "News")
    impact    = story.get("impact", "medium")
    cat_icon  = _category_icon(category)
    imp_cls   = _impact_class(impact)
    imp_label = impact.upper()

    return f"""
    <div class="flip-card" id="card-{card_id}" onclick="flip('{card_id}')">
      <div class="flip-inner">

        <!-- FRONT -->
        <div class="flip-front">
          <div class="card-meta">
            <span class="cat-pill">{cat_icon} {_esc(category)}</span>
            <span class="impact-badge {imp_cls}">{imp_label}</span>
          </div>
          <h3 class="card-title">{title}</h3>
          <p class="card-summary">{summary}</p>
          <div class="card-footer">
            <span class="card-source">{source}</span>
            <span class="flip-hint">Tap for implications →</span>
          </div>
        </div>

        <!-- BACK -->
        <div class="flip-back">
          <div class="back-header">
            <span class="back-label">⚡ Real-world implications</span>
            <span class="flip-hint-back">← tap to flip back</span>
          </div>
          <p class="impl-text">{impl}</p>
          <div class="card-footer">
            <a href="{url}" target="_blank" rel="noopener" onclick="event.stopPropagation()"
               class="read-link">Read full story ↗</a>
          </div>
        </div>

      </div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Main renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_lite_html(digest: Dict) -> str:
    now       = datetime.now(timezone.utc)
    date_str  = now.strftime("%A, %B %d %Y")
    time_str  = now.strftime("%H:%M UTC")

    global_headline = _esc(digest.get("global_headline", "Today's global AI signals"))
    india_headline  = _esc(digest.get("india_headline",  "Today's India AI signals"))
    global_stories  = digest.get("global", [])
    india_stories   = digest.get("india",  [])

    # Build card HTML for each column
    global_cards = "\n".join(_card(s, i, "g") for i, s in enumerate(global_stories))
    india_cards  = "\n".join(_card(s, i, "i") for i, s in enumerate(india_stories))

    global_count = len(global_stories)
    india_count  = len(india_stories)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AI Digest Lite — {date_str}</title>
  <meta name="description" content="A curated 15-minute AI briefing — Global and India signals, with real-world implications."/>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"/>

  <style>
    /* ── Reset & base ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:        #F0F4FF;
      --surface:   #FFFFFF;
      --border:    #E2E8F0;
      --accent:    #6366F1;
      --accent2:   #0EA5E9;
      --text:      #0F172A;
      --muted:     #64748B;
      --light:     #94A3B8;
      --high:      #EF4444;
      --med:       #F59E0B;
      --low:       #94A3B8;
      --flip-dur:  0.55s;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
      min-height: 100vh;
      padding-bottom: 48px;
    }}

    /* ── Header ── */
    .site-header {{
      background: #0F172A;
      padding: 20px 24px 18px;
      text-align: center;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 2px 12px rgba(0,0,0,.25);
    }}
    .site-header h1 {{
      font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px;
    }}
    .site-header h1 span {{ color: #818CF8; }}
    .header-sub {{
      font-size: 12px; color: #94A3B8; margin-top: 4px;
      display: flex; gap: 16px; justify-content: center; align-items: center; flex-wrap: wrap;
    }}
    .header-badge {{
      background: #1E293B; border: 1px solid #334155;
      border-radius: 20px; padding: 2px 10px;
      font-size: 11px; font-weight: 600; color: #A5B4FC;
    }}

    /* ── Columns layout ── */
    .columns {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
      max-width: 1400px;
      margin: 0 auto;
    }}
    .column {{
      padding: 20px 16px;
      border-right: 1px solid var(--border);
    }}
    .column:last-child {{ border-right: none; }}

    /* Column header */
    .col-header {{
      margin-bottom: 14px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--border);
    }}
    .col-title {{
      font-size: 16px; font-weight: 800; color: var(--text);
      display: flex; align-items: center; gap: 8px;
    }}
    .col-count {{
      font-size: 11px; background: var(--accent); color: white;
      border-radius: 10px; padding: 1px 8px; font-weight: 700;
    }}
    .col-headline {{
      font-size: 12px; color: var(--muted); margin-top: 5px; line-height: 1.5;
      font-style: italic;
    }}

    /* ── Flip card ── */
    .flip-card {{
      perspective: 1200px;
      margin-bottom: 12px;
      cursor: pointer;
      border-radius: 12px;
    }}
    .flip-inner {{
      position: relative;
      width: 100%;
      transition: transform var(--flip-dur) cubic-bezier(.4,0,.2,1);
      transform-style: preserve-3d;
    }}
    .flip-card.flipped .flip-inner {{
      transform: rotateY(180deg);
    }}
    .flip-front,
    .flip-back {{
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: 12px;
      padding: 14px 16px;
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }}
    .flip-back {{
      position: absolute;
      top: 0; left: 0; right: 0;
      transform: rotateY(180deg);
      min-height: 100%;
      border-color: #C7D2FE;
      background: #FAFAFF;
    }}
    /* Make flip-card height match the taller side */
    .flip-card {{ min-height: 0; }}
    .flip-inner {{ min-height: inherit; }}

    /* Card meta row */
    .card-meta {{
      display: flex; align-items: center; gap: 6px; margin-bottom: 8px; flex-wrap: wrap;
    }}
    .cat-pill {{
      font-size: 10px; font-weight: 600; color: var(--muted);
      background: #F1F5F9; border-radius: 6px; padding: 2px 7px;
    }}
    .impact-badge {{
      font-size: 9.5px; font-weight: 800; border-radius: 6px; padding: 2px 7px;
      letter-spacing: .04em;
    }}
    .impact-high {{ background: #FEE2E2; color: #991B1B; }}
    .impact-med  {{ background: #FEF3C7; color: #92400E; }}
    .impact-low  {{ background: #F1F5F9; color: #64748B; }}

    /* Card text */
    .card-title {{
      font-size: 13.5px; font-weight: 700; color: var(--text);
      line-height: 1.4; margin-bottom: 7px;
      display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    }}
    .card-summary {{
      font-size: 12px; color: #374151; line-height: 1.6;
      display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
    }}
    .card-footer {{
      margin-top: 10px;
      display: flex; justify-content: space-between; align-items: center;
    }}
    .card-source {{ font-size: 10.5px; color: var(--light); font-weight: 600; }}
    .flip-hint   {{ font-size: 10px; color: var(--accent); font-weight: 600; }}

    /* Back side */
    .back-header {{
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 10px;
    }}
    .back-label  {{ font-size: 11px; font-weight: 800; color: var(--accent); }}
    .flip-hint-back {{ font-size: 10px; color: var(--light); }}
    .impl-text {{
      font-size: 12.5px; color: #1E293B; line-height: 1.7;
    }}
    .read-link {{
      font-size: 11px; font-weight: 700; color: var(--accent);
      text-decoration: none;
    }}
    .read-link:hover {{ text-decoration: underline; }}

    /* ── Mobile ── */
    @media (max-width: 767px) {{
      .columns {{ grid-template-columns: 1fr; }}
      .column {{ border-right: none; border-bottom: 2px solid var(--border); }}
      .column:last-child {{ border-bottom: none; }}
      .site-header h1 {{ font-size: 18px; }}
    }}

    /* ── Footer ── */
    .site-footer {{
      text-align: center; font-size: 11px; color: var(--light);
      padding: 24px 16px 0; border-top: 1px solid var(--border);
      max-width: 1400px; margin: 20px auto 0;
    }}
    .site-footer a {{ color: var(--accent); text-decoration: none; }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="site-header">
    <h1>⚡ AI Digest <span>Lite</span></h1>
    <div class="header-sub">
      <span>{date_str} · Updated {time_str}</span>
      <span class="header-badge">15-min read</span>
      <span class="header-badge">🌍 Global + 🇮🇳 India</span>
      <span class="header-badge">Tap cards to see implications</span>
    </div>
  </header>

  <!-- Two-column layout -->
  <div class="columns">

    <!-- Global column -->
    <div class="column">
      <div class="col-header">
        <div class="col-title">
          🌍 Global AI
          <span class="col-count">{global_count}</span>
        </div>
        <div class="col-headline">{global_headline}</div>
      </div>
      {global_cards}
    </div>

    <!-- India column -->
    <div class="column">
      <div class="col-header">
        <div class="col-title">
          🇮🇳 India AI
          <span class="col-count">{india_count}</span>
        </div>
        <div class="col-headline">{india_headline}</div>
      </div>
      {india_cards}
    </div>

  </div>

  <footer class="site-footer">
    <p>AI Digest Lite · Curated by Claude · <a href="index.html">Full Global Digest</a> · <a href="india.html">India Pulse</a> · <a href="tn.html">TN Innovation</a></p>
    <p style="margin-top:4px">Updated daily at 7AM CST · Powered by Anthropic Claude</p>
  </footer>

  <script>
    function flip(id) {{
      const card = document.getElementById('card-' + id);
      card.classList.toggle('flipped');
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
