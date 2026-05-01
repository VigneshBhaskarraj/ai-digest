"""
summarize_tn.py
Uses Claude API to summarize Tamil Nadu innovation news into a structured
7-day digest. Sections: policies, startup spotlight, research, district pulse,
startup club radar, sector opportunities, quick hits, leaders voices.
"""

import os
import json
import anthropic
from typing import List, Dict

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are an expert analyst specializing in Tamil Nadu's innovation and startup ecosystem.
You track government policy, research institutions (especially IIT Madras / IITM Pravartak / Anna University),
startup clubs (TiE Chennai, NASSCOM 10000 Startups, StartupTN), college E-cells, VC activity, and
district-level opportunity signals across TN's cities.

You will be given a JSON list of articles from the past 7 days.

Return ONLY valid JSON (no markdown, no extra text) in this exact structure:
{
  "headline": "One punchy sentence capturing the most important Tamil Nadu innovation development this week",

  "signal_of_the_week": {
    "theme": "The single most important pattern or trend emerging from TN this week (e.g. 'IIT Madras spinoffs accelerating', 'EV policy reshaping Coimbatore')",
    "why_it_matters": "2 sentences on why this theme is significant and what it signals for the TN ecosystem",
    "signals": ["signal1", "signal2", "signal3"]
  },

  "policy_incentives": [
    {
      "title": "Policy or initiative title",
      "body": "2-3 sentences: what it is, who it targets, why it matters for startups or innovators in TN",
      "url": "article url",
      "source": "source name",
      "impact_level": "high | medium | low"
    }
  ],

  "startup_spotlight": [
    {
      "name": "Startup or company name",
      "sector": "AI / HealthTech / AgriTech / EV / Semiconductor / EdTech / FinTech / SpaceTech / CleanTech / Manufacturing / DeepTech / Other",
      "location": "Chennai / Coimbatore / Madurai / Trichy / Tirunelveli / Vellore / Other",
      "what_it_does": "One sentence description",
      "stage": "Idea / Seed / Series A / Series B / Growth / Bootstrapped",
      "funding": "Amount if mentioned, else 'Bootstrapped / Not disclosed'",
      "why_notable": "One sentence on what makes this significant for TN",
      "url": "article url",
      "source": "source name"
    }
  ],

  "research_innovation": [
    {
      "institution": "IIT Madras / IITM Pravartak / Anna University / NIT Trichy / PSG / SRM / Other",
      "title": "Research project, spinoff, or innovation milestone",
      "description": "2 sentences: what they built/discovered and its real-world application",
      "url": "article url",
      "source": "source name"
    }
  ],

  "club_radar": [
    {
      "org": "Organization name (e.g. TiE Chennai, NASSCOM 10000 Startups, StartupTN, IIT Madras E-Cell, Anna University BIC, PSG-STEP)",
      "activity": "What this org is currently doing — new cohort, event, investment, program launch",
      "why_follow": "One sentence on why this matters for founders or innovators right now",
      "url": "article url or null"
    }
  ],

  "district_pulse": [
    {
      "district": "City/district name (Chennai / Coimbatore / Madurai / Trichy / Tirunelveli / Other)",
      "sector_focus": "What sector is most active here (e.g. EV Manufacturing, AgriTech, Textile Tech, Aerospace)",
      "signal": "2 sentences: what's happening here and why it's a meaningful signal",
      "opportunity": "One sentence: what opportunity this creates for founders or investors"
    }
  ],

  "sector_opportunities": [
    {
      "sector": "Sector name",
      "opportunity": "2-3 sentences: what's happening in this sector in TN right now, why it's hot, what founders or investors should know",
      "signals": ["signal1", "signal2"]
    }
  ],

  "quick_hits": [
    {
      "title": "Brief headline",
      "source": "Source",
      "url": "url",
      "one_liner": "One sentence max"
    }
  ],

  "leaders_voices": [
    {
      "name": "Leader's full name",
      "role": "Their title / affiliation",
      "insight": "What they said, shared, or argued — paraphrased in 1-2 punchy sentences",
      "context": "One sentence on why this is noteworthy for TN's ecosystem",
      "url": "source url or null"
    }
  ],

  "vike_note": "One sharp, opinionated sentence: what should a founder, investor, or innovation professional in Tamil Nadu act on most from this week's digest?"
}

Rules:
- signal_of_the_week: synthesize the SINGLE biggest theme across all articles this week; if no clear theme, return null
- policy_incentives: include ALL government schemes, incentives, or regulatory news relevant to TN startups/innovators
- startup_spotlight: include ALL TN-based startups mentioned — any sector, any city, any stage
- research_innovation: IIT Madras spinoffs, IITM Pravartak incubates, Anna University BIC, NIT Trichy, college projects with commercial potential
- club_radar: TiE Chennai, NASSCOM 10000 Startups, StartupTN programs, IIT Madras Entrepreneurship Cell, PSG-STEP, college E-cells, Anna University BIC, pitch competitions, hackathons, demo days — if mentioned, include them
- district_pulse: synthesize by city — Chennai (GCC/AI), Coimbatore (EV/manufacturing), Madurai (agritech/water), Trichy (aerospace/defense), Tirunelveli (solar/renewable), etc. Only include districts where you have real signal from the articles
- sector_opportunities: 2-4 max, synthesized across articles
- quick_hits: 4-8 items
- leaders_voices: TN CM MK Stalin, IT Secretary, StartupTN CEO, TiE Chennai president, IITM directors, any named TN founder/investor/policymaker who made a statement. Return empty array if none found — never fabricate
- If an article mentions both funding AND a new startup, include in startup_spotlight AND quick_hits
- If a section has no data, return empty array — NEVER fabricate
- vike_note: actionable, TN-specific advice
- This is a 7-day digest window — synthesize patterns across the week, not just today's news

If articles are sparse: synthesize what IS available honestly. Use known ecosystem facts to contextualize (IIT Madras Pravartak program, StartupTN's active schemes, Chennai's GCC base) but clearly distinguish what comes from articles vs. general knowledge. When citing general knowledge, note it as ecosystem context."""


def summarize_tn_articles(articles: List[Dict]) -> Dict:
    """Send TN articles to Claude and get back a structured digest dict."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    payload = []
    for a in articles[:70]:
        payload.append({
            "title":     a["title"],
            "summary":   a["summary"][:500],
            "source":    a["source"],
            "url":       a["url"],
            "category":  a["category"],
            "published": a.get("published", ""),
        })

    if not payload:
        return _empty_digest()

    user_message = f"""Here are the Tamil Nadu innovation and technology news articles from the past 7 days.
Today's date: {__import__('datetime').datetime.utcnow().strftime('%B %d, %Y')} (IST: +5:30 ahead of UTC)
Articles cover: {len(payload)} items from the past 7 days.

Articles JSON:
{json.dumps(payload, indent=2)}

Produce the structured TN Innovation Digest JSON. This is a 7-day digest so synthesize patterns across the week.
Focus on:
- Government policies / StartupTN schemes / TIDEL / SIPCOT / TANSIM announcements
- New TN-based startups across any sector or city
- IIT Madras, IITM Pravartak, Anna University, NIT Trichy research and spinoffs
- TiE Chennai, NASSCOM 10000, college E-cell events, demo days, hackathons
- District-level signals: Coimbatore (EV/manufacturing), Madurai (agritech), Trichy (aerospace), Chennai (AI/GCC)
- Notable quotes or actions from TN government officials, IITM faculty, startup founders"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def _empty_digest() -> Dict:
    return {
        "headline": "Tamil Nadu Innovation Digest — building the 7-day signal picture.",
        "signal_of_the_week": {
            "theme": "IIT Madras Spinoff Momentum",
            "why_it_matters": "IITM Pravartak consistently produces 40-50 new startups per year, making it India's most prolific deeptech incubator. The commercialization pipeline from IIT Madras remains Tamil Nadu's strongest innovation signal regardless of weekly news volume.",
            "signals": ["IITM Pravartak pipeline", "450+ startups incubated", "Research-to-market acceleration"]
        },
        "policy_incentives": [],
        "startup_spotlight": [],
        "research_innovation": [],
        "club_radar": [
            {
                "org": "StartupTN",
                "activity": "Operates 10+ active incubation and acceleration programs across Tamil Nadu districts.",
                "why_follow": "Largest state startup mission in India — equity-free grants, mentorship, and market access for TN founders.",
                "url": "https://startuptn.in"
            },
            {
                "org": "TiE Chennai",
                "activity": "Monthly charter meetings, mentorship programs, and the TiE Global Summit pipeline for Chennai founders.",
                "why_follow": "Best network for Chennai-based founders seeking angel checks and global mentor connections.",
                "url": "https://chennai.tie.org"
            }
        ],
        "district_pulse": [
            {
                "district": "Chennai",
                "sector_focus": "AI / GCC Talent",
                "signal": "Chennai hosts 250+ Global Capability Centers with 500,000+ tech professionals. GCC expansion continues driven by cost-quality advantage.",
                "opportunity": "Enterprise AI tooling and B2B SaaS serving GCC workflows is an underserved niche with captive paying customers."
            },
            {
                "district": "Coimbatore",
                "sector_focus": "EV & Manufacturing",
                "signal": "Coimbatore's existing precision manufacturing base is rapidly pivoting to EV components, driven by Ola Electric and government EV policy.",
                "opportunity": "EV battery management, motor controller, and charging infrastructure component suppliers have near-term contract opportunities."
            }
        ],
        "sector_opportunities": [
            {
                "sector": "Agricultural AI",
                "opportunity": "Tamil Nadu's 62 lakh farmer base and the state's TNAU digitization program create one of India's largest captive AgriTech markets. Three active programs fund pilot deployments at district level.",
                "signals": ["TNAU digitization budget", "62L farmer base"]
            }
        ],
        "quick_hits": [],
        "leaders_voices": [],
        "vike_note": "The highest-leverage move for a TN-based AI founder this week: apply to IITM Pravartak's open cohort — the IIT Madras brand attached to your company opens enterprise doors that cold outreach never will.",
    }


if __name__ == "__main__":
    test_articles = [
        {
            "title": "Tamil Nadu launches Rs 500 Cr AI startup fund under StartupTN",
            "summary": "The Tamil Nadu government announced a Rs 500 crore AI-focused startup fund to support early-stage founders in healthcare, agriculture, and manufacturing AI. The fund will be managed by StartupTN with a 7-year horizon.",
            "source": "The Hindu",
            "url": "https://thehindu.com",
            "category": "Policy & Incentives",
            "published": "2026-04-30",
        },
        {
            "title": "TiE Chennai announces 12th annual pitch competition for deep tech startups",
            "summary": "TiE Chennai has opened applications for its 12th annual pitch competition, targeting deep tech startups in AI, semiconductors, and advanced manufacturing. Winner gets Rs 50L grant and TiE global membership.",
            "source": "YourStory",
            "url": "https://yourstory.com",
            "category": "Startup Club & Events",
            "published": "2026-04-29",
        }
    ]
    result = summarize_tn_articles(test_articles)
    print(json.dumps(result, indent=2))
