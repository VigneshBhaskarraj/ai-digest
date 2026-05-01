"""
render_india_html.py
Renders the India AI Investment & Startup digest as a dark-mode HTML dashboard.
Output: docs/india.html (served by GitHub Pages)
"""

import os
from datetime import datetime, timezone
from typing import Dict


CATEGORY_COLORS = {
    "Funding Round":         "#34d399",   # green
    "New Startup / Incubation": "#a78bfa", # purple
    "Policy & Government":   "#fb923c",   # orange
    "VC & Investment Trends": "#00d4ff",  # cyan
    "India AI News":         "#f472b6",   # pink
}

CATEGORY_ICONS = {
    "Funding Round":         "💰",
    "New Startup / Incubation": "🚀",
    "Policy & Government":   "🏛️",
    "VC & Investment Trends": "📈",
    "India AI News":         "🤖",
}


def render_india_html(digest: Dict) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    headline       = digest.get("headline", "India AI digest is ready.")
    funding_rounds = digest.get("funding_rounds", [])
    new_startups   = digest.get("new_startups", [])
    vc_trends      = digest.get("vc_trends", [])
    policy_watch   = digest.get("policy_watch", [])
    quick_hits     = digest.get("quick_hits", [])
    vike_note      = digest.get("vike_note", "")

    # ── Funding Rounds ─────────────────────────────────────────────────────────
    funding_html = ""
    for r in funding_rounds:
        funding_html += f"""
        <div class="funding-card">
          <div class="funding-header">
            <span class="startup-name">{r.get('startup', '')}</span>
            <span class="funding-amount">{r.get('amount', 'Undisclosed')}</span>
          </div>
          <div class="funding-meta">
            <span class="stage-badge">{r.get('stage', '')}</span>
            <span class="investors">🏦 {r.get('investors', '')}</span>
          </div>
          <p class="funding-focus">{r.get('focus', '')}</p>
          <a href="{r.get('url','#')}" target="_blank" rel="noopener" class="read-more">Read more →</a>
        </div>"""

    if not funding_html:
        funding_html = '<p class="empty-msg">No funding rounds reported today.</p>'

    # ── New Startups ───────────────────────────────────────────────────────────
    startups_html = ""
    for s in new_startups:
        startups_html += f"""
        <div class="startup-card">
          <div class="startup-header">
            <span class="startup-name-sm">🚀 {s.get('name', '')}</span>
            <span class="founder-tag">by {s.get('founded_by', 'Unknown')}</span>
          </div>
          <p class="startup-what">{s.get('what_it_does', '')}</p>
          <p class="startup-why">💡 {s.get('why_interesting', '')}</p>
          <a href="{s.get('url','#')}" target="_blank" rel="noopener" class="read-more">Read more →</a>
        </div>"""

    # ── VC Trends ──────────────────────────────────────────────────────────────
    trends_html = ""
    for t in vc_trends:
        trends_html += f"""
        <div class="trend-card">
          <h4 class="trend-title">📈 {t.get('trend', '')}</h4>
          <p class="trend-detail">{t.get('detail', '')}</p>
        </div>"""

    # ── Policy Watch ───────────────────────────────────────────────────────────
    policy_html = ""
    for p in policy_watch:
        policy_html += f"""
        <div class="policy-card">
          <h4 class="policy-title">🏛️ <a href="{p.get('url','#')}" target="_blank" rel="noopener">{p.get('title','')}</a></h4>
          <p class="policy-body">{p.get('body','')}</p>
          <span class="policy-source">{p.get('source','')}</span>
        </div>"""

    # ── Quick Hits ─────────────────────────────────────────────────────────────
    hits_html = ""
    for hit in quick_hits:
        hits_html += f"""
        <div class="quick-hit">
          <span class="hit-dot">▸</span>
          <div>
            <a href="{hit.get('url','#')}" target="_blank" rel="noopener" class="hit-title">{hit.get('title','')}</a>
            <span class="hit-source"> — {hit.get('source','')}</span>
            <p class="hit-liner">{hit.get('one_liner','')}</p>
          </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🇮🇳 India AI Pulse — {date_str}</title>
  <meta name="description" content="Daily digest of AI investments, startup launches, and VC trends in India.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,400;0,500;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg:       #0a0f1e;
      --surface:  #0f1629;
      --surface2: #141d35;
      --border:   #1e2d50;
      --text:     #e2e8f0;
      --muted:    #64748b;
      --accent:   #ff6b35;
      --accent2:  #34d399;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      line-height: 1.6;
      min-height: 100vh;
    }}
    .container {{
      max-width: 820px;
      margin: 0 auto;
      padding: 2.5rem 1.25rem 4rem;
    }}

    /* Header */
    .header {{ margin-bottom: 2rem; }}
    .header-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1rem;
    }}
    .brand {{
      font-family: 'Syne', sans-serif;
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
    }}
    .header-date {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--muted);
    }}
    .nav-link {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: #00d4ff;
      text-decoration: none;
      border: 1px solid rgba(0,212,255,0.3);
      border-radius: 4px;
      padding: 0.25rem 0.6rem;
    }}
    .nav-link:hover {{ background: rgba(0,212,255,0.08); }}
    .headline {{
      font-family: 'Syne', sans-serif;
      font-size: clamp(1.3rem, 3.5vw, 1.75rem);
      font-weight: 800;
      line-height: 1.25;
      color: #f1f5f9;
      margin-top: 0.5rem;
    }}

    /* Vike Note */
    .vike-note {{
      background: linear-gradient(135deg, rgba(255,107,53,0.08), rgba(255,107,53,0.03));
      border: 1px solid rgba(255,107,53,0.25);
      border-radius: 10px;
      padding: 1rem 1.25rem;
      font-size: 0.875rem;
      color: #cbd5e1;
      margin-bottom: 2rem;
      line-height: 1.7;
    }}
    .vike-note strong {{ color: var(--accent); margin-right: 0.5rem; }}

    /* Section */
    .section-block {{ margin-bottom: 2.5rem; }}
    .section-title {{
      font-family: 'Syne', sans-serif;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .section-title::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: var(--border);
    }}

    /* Funding Cards */
    .funding-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent2);
      border-radius: 10px;
      padding: 1.1rem 1.25rem;
      margin-bottom: 0.85rem;
      transition: border-color 0.2s;
    }}
    .funding-card:hover {{ border-color: var(--accent2); }}
    .funding-header {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }}
    .startup-name {{
      font-family: 'Syne', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      color: #f1f5f9;
    }}
    .funding-amount {{
      font-family: 'DM Mono', monospace;
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--accent2);
    }}
    .funding-meta {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.6rem;
      flex-wrap: wrap;
    }}
    .stage-badge {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      background: rgba(52,211,153,0.1);
      color: var(--accent2);
      border: 1px solid rgba(52,211,153,0.25);
      border-radius: 4px;
      padding: 0.15rem 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .investors {{
      font-size: 0.78rem;
      color: var(--muted);
    }}
    .funding-focus {{
      font-size: 0.85rem;
      color: #94a3b8;
      line-height: 1.6;
      margin-bottom: 0.6rem;
    }}

    /* Startup Cards */
    .startup-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 3px solid #a78bfa;
      border-radius: 10px;
      padding: 1.1rem 1.25rem;
      margin-bottom: 0.85rem;
    }}
    .startup-header {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }}
    .startup-name-sm {{
      font-family: 'Syne', sans-serif;
      font-size: 0.95rem;
      font-weight: 700;
      color: #f1f5f9;
    }}
    .founder-tag {{
      font-size: 0.72rem;
      color: var(--muted);
      font-style: italic;
    }}
    .startup-what {{
      font-size: 0.85rem;
      color: #94a3b8;
      margin-bottom: 0.4rem;
      line-height: 1.6;
    }}
    .startup-why {{
      font-size: 0.82rem;
      color: #a78bfa;
      line-height: 1.6;
      margin-bottom: 0.6rem;
    }}

    /* Trend Cards */
    .trend-card {{
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.1rem 1.25rem;
      margin-bottom: 0.85rem;
    }}
    .trend-title {{
      font-size: 0.9rem;
      font-weight: 600;
      color: #00d4ff;
      margin-bottom: 0.5rem;
    }}
    .trend-detail {{
      font-size: 0.85rem;
      color: #94a3b8;
      line-height: 1.65;
    }}

    /* Policy Cards */
    .policy-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 3px solid #fb923c;
      border-radius: 10px;
      padding: 1rem 1.25rem;
      margin-bottom: 0.85rem;
    }}
    .policy-title {{
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: 0.4rem;
    }}
    .policy-title a {{ color: #fb923c; text-decoration: none; }}
    .policy-title a:hover {{ text-decoration: underline; }}
    .policy-body {{
      font-size: 0.83rem;
      color: #94a3b8;
      line-height: 1.6;
      margin-bottom: 0.35rem;
    }}
    .policy-source {{
      font-size: 0.7rem;
      color: var(--muted);
      font-family: 'DM Mono', monospace;
    }}

    /* Quick Hits */
    .quick-hit {{
      display: flex;
      gap: 0.75rem;
      padding: 0.7rem 0;
      border-bottom: 1px solid var(--border);
    }}
    .quick-hit:last-child {{ border-bottom: none; }}
    .hit-dot {{ color: var(--accent); flex-shrink: 0; margin-top: 1px; }}
    .hit-title {{
      font-size: 0.875rem;
      color: #e2e8f0;
      font-weight: 500;
      text-decoration: none;
    }}
    .hit-title:hover {{ color: var(--accent); }}
    .hit-source {{ font-size: 0.75rem; color: var(--muted); }}
    .hit-liner {{
      font-size: 0.8rem;
      color: #64748b;
      margin-top: 0.2rem;
    }}

    /* Shared */
    .read-more {{
      font-size: 0.72rem;
      color: var(--muted);
      text-decoration: none;
      font-family: 'DM Mono', monospace;
    }}
    .read-more:hover {{ color: var(--accent); }}
    .empty-msg {{ color: var(--muted); font-size: 0.85rem; padding: 0.5rem 0; }}

    /* Footer */
    .footer {{
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .footer-brand {{
      font-family: 'Syne', sans-serif;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .footer-time {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--border);
    }}

    /* Animations */
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .header        {{ animation: fadeUp 0.4s ease both; }}
    .vike-note     {{ animation: fadeUp 0.4s ease 0.08s both; }}
    .section-block {{ animation: fadeUp 0.4s ease 0.12s both; }}
  </style>
</head>
<body>
<div class="container">

  <header class="header">
    <div class="header-top">
      <span class="brand">🇮🇳 India AI Pulse</span>
      <div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap">
        <a href="index.html" class="nav-link">⚡ Global AI Digest</a>
        <span class="header-date">{date_str} · {time_str}</span>
      </div>
    </div>
    <h1 class="headline">{headline}</h1>
  </header>

  {"" if not vike_note else f'<div class="vike-note"><strong>📌 Today\'s Signal</strong>{vike_note}</div>'}

  <div class="section-block">
    <h2 class="section-title">💰 Funding Rounds</h2>
    {funding_html}
  </div>

  {"" if not new_startups else f'''<div class="section-block">
    <h2 class="section-title">🚀 New Startups & Incubations</h2>
    {startups_html}
  </div>'''}

  {"" if not vc_trends else f'''<div class="section-block">
    <h2 class="section-title">📈 Where VCs Are Focusing</h2>
    {trends_html}
  </div>'''}

  {"" if not policy_watch else f'''<div class="section-block">
    <h2 class="section-title">🏛️ Policy Watch</h2>
    {policy_html}
  </div>'''}

  {"" if not quick_hits else f'''<div class="section-block">
    <h2 class="section-title">⚡ Quick Hits</h2>
    {hits_html}
  </div>'''}

  <footer class="footer">
    <span class="footer-brand">VigneshBhaskarraj / ai-digest · India AI Pulse</span>
    <span class="footer-time">Generated {date_str} {time_str}</span>
  </footer>

</div>
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
        "funding_rounds": [{
            "startup": "Sarvam AI",
            "amount": "$41M (₹340 Cr)",
            "stage": "Series B",
            "investors": "Peak XV Partners",
            "focus": "Building India-specific LLMs across 22 languages, targeting govt and enterprise.",
            "url": "https://inc42.com",
            "source": "Inc42",
        }],
        "new_startups": [],
        "vc_trends": [{
            "trend": "Vernacular AI getting serious capital",
            "detail": "Multiple VCs are placing bets on language-specific models for Tier 2/3 India markets. The thesis: English-first LLMs miss 800M non-English speakers.",
        }],
        "policy_watch": [],
        "quick_hits": [],
        "vike_note": "If you're building in AI for India, vernacular + voice is where the moat is — not another ChatGPT wrapper.",
    }
    html = render_india_html(dummy)
    save_india_dashboard(html, "/tmp/test_india.html")
    print(f"Test India HTML written, size: {len(html)} bytes")
