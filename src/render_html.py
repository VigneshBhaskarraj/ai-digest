"""
render_html.py
Builds a beautiful, shareable HTML dashboard from the structured digest JSON.
Output: docs/index.html (served by GitHub Pages)
Also returns the HTML string for email delivery.
"""

import os
from datetime import datetime, timezone
from typing import Dict


CATEGORY_ICONS = {
    "Model Releases":   "🧠",
    "Research":         "🔬",
    "Tools & Products": "🛠️",
    "Industry News":    "📰",
    "Community":        "💬",
}

CATEGORY_COLORS = {
    "Model Releases":   "#00d4ff",
    "Research":         "#a78bfa",
    "Tools & Products": "#34d399",
    "Industry News":    "#fb923c",
    "Community":        "#f472b6",
}


def render_html(digest: Dict, session_label: str = "Morning") -> str:
    """Render the full HTML dashboard string."""

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    headline = digest.get("headline", "Your AI digest is ready.")
    top_stories = digest.get("top_stories", [])
    quick_hits = digest.get("quick_hits", [])
    arxiv_picks = digest.get("arxiv_picks", [])
    community_pulse = digest.get("community_pulse", "")
    vike_note = digest.get("vike_note", "")

    # Build top stories HTML
    stories_html = ""
    for story in top_stories:
        cat = story.get("category", "Industry News")
        icon = CATEGORY_ICONS.get(cat, "📌")
        color = CATEGORY_COLORS.get(cat, "#94a3b8")
        stories_html += f"""
        <article class="story-card">
          <div class="story-meta">
            <span class="category-badge" style="background:{color}20;color:{color};border-color:{color}40">
              {icon} {cat}
            </span>
            <span class="story-source">{story.get('source','')}</span>
          </div>
          <h3 class="story-title">
            <a href="{story.get('url','#')}" target="_blank" rel="noopener">{story.get('title','')}</a>
          </h3>
          <p class="story-why">{story.get('why_it_matters','')}</p>
        </article>"""

    # Build quick hits HTML
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

    # Build arXiv HTML
    arxiv_html = ""
    if arxiv_picks:
        arxiv_html = '<div class="section-block">'
        arxiv_html += '<h2 class="section-title"><span class="section-icon">🔬</span> arXiv Picks</h2>'
        for paper in arxiv_picks:
            arxiv_html += f"""
            <div class="arxiv-card">
              <a href="{paper.get('url','#')}" target="_blank" rel="noopener" class="arxiv-title">{paper.get('title','')}</a>
              <p class="arxiv-tldr">{paper.get('tldr','')}</p>
            </div>"""
        arxiv_html += "</div>"

    session_emoji = "🌅" if session_label == "Morning" else "🌆"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Digest — {date_str}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:        #080c14;
      --surface:   #0e1420;
      --surface2:  #141a26;
      --border:    #1e2a3d;
      --text:      #e2e8f0;
      --muted:     #64748b;
      --accent:    #00d4ff;
      --accent2:   #a78bfa;
      --gold:      #fbbf24;
    }}

    body {{
      font-family: 'DM Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
    }}

    /* Subtle grid background */
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
      z-index: 0;
    }}

    .container {{
      max-width: 860px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
      position: relative;
      z-index: 1;
    }}

    /* Header */
    .header {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 2rem;
      margin-bottom: 2.5rem;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}

    .brand {{
      font-family: 'Syne', sans-serif;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--accent);
    }}

    .session-badge {{
      font-family: 'DM Mono', monospace;
      font-size: 0.7rem;
      padding: 0.25rem 0.75rem;
      border: 1px solid var(--border);
      border-radius: 2rem;
      color: var(--muted);
      background: var(--surface);
    }}

    .header-date {{
      font-family: 'DM Mono', monospace;
      font-size: 0.7rem;
      color: var(--muted);
      letter-spacing: 0.05em;
    }}

    .headline {{
      font-family: 'Syne', sans-serif;
      font-size: clamp(1.4rem, 3vw, 2rem);
      font-weight: 800;
      line-height: 1.25;
      color: var(--text);
      max-width: 700px;
    }}

    .headline span {{
      color: var(--accent);
    }}

    /* Vike Note */
    .vike-note {{
      background: linear-gradient(135deg, rgba(0,212,255,0.06), rgba(167,139,250,0.06));
      border: 1px solid rgba(0,212,255,0.2);
      border-left: 3px solid var(--accent);
      border-radius: 8px;
      padding: 1rem 1.25rem;
      margin-bottom: 2.5rem;
      font-size: 0.875rem;
      font-style: italic;
      color: #94a3b8;
    }}

    .vike-note strong {{
      font-style: normal;
      font-family: 'Syne', sans-serif;
      font-size: 0.7rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--accent);
      display: block;
      margin-bottom: 0.4rem;
    }}

    /* Section */
    .section-block {{
      margin-bottom: 2.5rem;
    }}

    .section-title {{
      font-family: 'Syne', sans-serif;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 1.25rem;
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

    /* Story Cards */
    .story-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem;
      margin-bottom: 0.875rem;
      transition: border-color 0.2s, transform 0.2s;
    }}

    .story-card:hover {{
      border-color: rgba(0,212,255,0.3);
      transform: translateY(-1px);
    }}

    .story-meta {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.625rem;
      flex-wrap: wrap;
    }}

    .category-badge {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      font-weight: 500;
      padding: 0.2rem 0.6rem;
      border-radius: 1rem;
      border: 1px solid;
      letter-spacing: 0.03em;
    }}

    .story-source {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--muted);
    }}

    .story-title a {{
      font-family: 'Syne', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      color: var(--text);
      text-decoration: none;
      display: block;
      margin-bottom: 0.5rem;
      line-height: 1.35;
    }}

    .story-title a:hover {{
      color: var(--accent);
    }}

    .story-why {{
      font-size: 0.825rem;
      color: #94a3b8;
      line-height: 1.6;
    }}

    /* Quick Hits */
    .quick-hits-grid {{
      display: flex;
      flex-direction: column;
      gap: 0.875rem;
    }}

    .quick-hit {{
      display: flex;
      gap: 0.75rem;
      align-items: flex-start;
      padding: 0.75rem 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      transition: border-color 0.2s;
    }}

    .quick-hit:hover {{
      border-color: rgba(167,139,250,0.3);
    }}

    .hit-dot {{
      color: var(--accent2);
      font-size: 0.75rem;
      margin-top: 0.25rem;
      flex-shrink: 0;
    }}

    .hit-title {{
      font-family: 'DM Sans', sans-serif;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--text);
      text-decoration: none;
    }}

    .hit-title:hover {{ color: var(--accent2); }}

    .hit-source {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--muted);
    }}

    .hit-liner {{
      font-size: 0.775rem;
      color: #64748b;
      margin-top: 0.2rem;
    }}

    /* arXiv */
    .arxiv-card {{
      padding: 0.875rem 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent2);
      border-radius: 8px;
      margin-bottom: 0.75rem;
    }}

    .arxiv-title {{
      font-family: 'DM Sans', sans-serif;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--text);
      text-decoration: none;
      display: block;
      margin-bottom: 0.4rem;
    }}

    .arxiv-title:hover {{ color: var(--accent2); }}

    .arxiv-tldr {{
      font-size: 0.775rem;
      color: #64748b;
    }}

    /* Community Pulse */
    .pulse-box {{
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem;
      font-size: 0.875rem;
      color: #94a3b8;
      line-height: 1.7;
    }}

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

    /* Refresh button */
    .refresh-btn {{
      font-family: 'Syne', sans-serif;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      background: transparent;
      color: var(--accent);
      border: 1px solid rgba(0,212,255,0.3);
      border-radius: 6px;
      padding: 0.4rem 1rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: background 0.2s, border-color 0.2s, transform 0.1s;
    }}
    .refresh-btn:hover {{
      background: rgba(0,212,255,0.08);
      border-color: var(--accent);
    }}
    .refresh-btn:active {{ transform: scale(0.97); }}
    .refresh-btn.spinning .btn-icon {{ animation: spin 0.8s linear infinite; }}
    .last-updated {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--muted);
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

    /* Fade in */
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .header        {{ animation: fadeUp 0.4s ease both; }}
    .vike-note     {{ animation: fadeUp 0.4s ease 0.1s both; }}
    .section-block {{ animation: fadeUp 0.4s ease 0.15s both; }}
  </style>
</head>
<body>
<div class="container">

  <header class="header">
    <div class="header-top">
      <span class="brand">⚡ AI Digest</span>
      <div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap">
        <a href="india.html" style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#ff6b35;text-decoration:none;border:1px solid rgba(255,107,53,0.3);border-radius:4px;padding:0.25rem 0.6rem;">🇮🇳 India AI Pulse</a>
        <span class="session-badge">{session_emoji} {session_label} Edition</span>
        <span class="header-date">{date_str} · {time_str}</span>
      </div>
    </div>
    <h1 class="headline">{headline}</h1>
  </header>

  {"" if not vike_note else f'''<div class="vike-note"><strong>📌 Today's Focus</strong>{vike_note}</div>'''}

  <div class="section-block">
    <h2 class="section-title"><span class="section-icon">🔥</span> Top Stories</h2>
    {stories_html}
  </div>

  <div class="section-block">
    <h2 class="section-title"><span class="section-icon">⚡</span> Quick Hits</h2>
    <div class="quick-hits-grid">
      {hits_html}
    </div>
  </div>

  {arxiv_html}

  {"" if not community_pulse else f'''<div class="section-block">
    <h2 class="section-title"><span class="section-icon">💬</span> Community Pulse</h2>
    <div class="pulse-box">{community_pulse}</div>
  </div>'''}

  <footer class="footer">
    <span class="footer-brand">VigneshBhaskarraj / ai-digest</span>
    <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
      <span class="last-updated" id="last-updated">Generated {date_str} {time_str}</span>
      <button class="refresh-btn" id="refresh-btn" onclick="triggerRefresh()">
        <span class="btn-icon" id="btn-icon">↻</span> Refresh
      </button>
    </div>
  </footer>

</div>

<script>
  function triggerRefresh() {{
    const btn  = document.getElementById('refresh-btn');
    const icon = document.getElementById('btn-icon');
    const info = document.getElementById('last-updated');

    btn.classList.add('spinning');
    btn.disabled = true;
    info.textContent = 'Refreshing...';

    // GitHub Actions manual trigger via repository_dispatch would need a PAT.
    // For now: hard-reload the page after a short delay to pick up any new deploy.
    setTimeout(() => {{
      window.location.reload(true);
    }}, 1800);
  }}

  // Show how long ago the page was generated
  (function() {{
    const generated = new Date('{date_str} {time_str}'.replace(' UTC','') + 'Z');
    const now       = new Date();
    const diffMin   = Math.round((now - generated) / 60000);
    const el        = document.getElementById('last-updated');
    if (!isNaN(diffMin) && el) {{
      if (diffMin < 1)       el.textContent = 'Just updated';
      else if (diffMin < 60) el.textContent = `Updated ${{diffMin}}m ago`;
      else                   el.textContent = `Updated ${{Math.round(diffMin/60)}}h ago`;
    }}
  }})();
</script>

</body>
</html>"""

    return html


def save_dashboard(html: str, output_path: str = "docs/index.html"):
    """Write the HTML to the docs/ folder for GitHub Pages."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Render] Dashboard saved → {output_path}")


if __name__ == "__main__":
    # Smoke test with dummy digest
    dummy = {
        "headline": "Anthropic ships Claude 4 with native tool use and 200K context",
        "top_stories": [
            {
                "title": "Claude 4 Released with Extended Thinking Mode",
                "source": "Anthropic Blog",
                "url": "https://anthropic.com",
                "why_it_matters": "Extended thinking lets Claude reason step by step over long contexts before responding. For builders, this means better agentic reliability on complex multi-step tasks.",
                "category": "Model Releases",
            }
        ],
        "quick_hits": [
            {"title": "Mistral releases Le Chat Pro", "source": "Mistral AI", "url": "#", "one_liner": "New paid tier with faster inference and priority access."},
        ],
        "arxiv_picks": [],
        "community_pulse": "r/LocalLLaMA is buzzing about running Claude 4 variants locally via Ollama.",
        "vike_note": "The Claude 4 tool-use improvements are directly relevant to the Ask Agent POC you're building — worth testing the new API parameters this week.",
    }
    html = render_html(dummy, "Morning")
    save_dashboard(html, "/tmp/test_dashboard.html")
    print(f"Test HTML written, size: {len(html)} bytes")
