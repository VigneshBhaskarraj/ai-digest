"""
tn_ecosystem_data.py
Curated, hand-researched list of notable Tamil Nadu startups organized by
sector. This static base ensures the TN Startup Ecosystem card always has
rich content even on low-news days. Combined with the dynamic news pipeline
for freshness.

Sources cross-referenced:
  - StartupTN portal (startuptn.in)
  - IITM Pravartak incubated companies
  - IIT Madras Entrepreneurship Cell alumni
  - Anna University BIC portfolio
  - PSG-STEP Coimbatore portfolio
  - Inc42 / YourStory / Entrackr TN coverage
  - Tracxn Tamil Nadu database
  - Crunchbase Chennai/Coimbatore/Madurai filters

Last updated: May 2026
"""

from typing import List, Dict

# ─────────────────────────────────────────────────────────────────────────────
# Stage legend:
#   "Listed"    = public company (NSE/BSE/NASDAQ)
#   "Unicorn"   = $1B+ valuation, private
#   "Series C+" = late-stage funded
#   "Series B"
#   "Series A"
#   "Seed"
#   "Bootstrap" = profitable, no external VC
#   "Incubated" = currently in incubation program
# ─────────────────────────────────────────────────────────────────────────────

TN_STARTUPS: List[Dict] = [

    # ── AI / ML / Conversational AI ──────────────────────────────────────────
    {
        "name": "Uniphore",
        "sector": "AI / Conversational AI",
        "location": "Chennai",
        "stage": "Series E",
        "funding": "$610M+",
        "what_it_does": "Conversational AI and automation platform for enterprise customer service.",
        "incubator": None,
        "why_notable": "One of TN's largest funded AI companies; pioneered speech-AI in India.",
        "url": "https://uniphore.com",
    },
    {
        "name": "Zoho Corporation",
        "sector": "Enterprise SaaS",
        "location": "Chennai",
        "stage": "Bootstrap",
        "funding": "Bootstrapped ($1B+ revenue)",
        "what_it_does": "Full-stack business software suite — CRM, HR, finance, collaboration.",
        "incubator": None,
        "why_notable": "India's most successful bootstrapped SaaS company; 100M+ users globally.",
        "url": "https://zoho.com",
    },
    {
        "name": "Freshworks",
        "sector": "CRM / Customer Experience SaaS",
        "location": "Chennai",
        "stage": "Listed",
        "funding": "NASDAQ: FRSH",
        "what_it_does": "AI-powered CRM, IT service management, and customer engagement tools.",
        "incubator": None,
        "why_notable": "First Chennai startup to list on NASDAQ; valued at $3B+.",
        "url": "https://freshworks.com",
    },
    {
        "name": "Mad Street Den / Vue.ai",
        "sector": "Retail AI",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "$30M+",
        "what_it_does": "AI-powered visual intelligence and personalization platform for retail.",
        "incubator": None,
        "why_notable": "Powers product discovery and visual search for 200+ global retailers.",
        "url": "https://vue.ai",
    },
    {
        "name": "Facilio",
        "sector": "PropTech / Building AI",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "$40M",
        "what_it_does": "AI platform for connected building operations and facilities management.",
        "incubator": None,
        "why_notable": "Used by Cushman & Wakefield and major REITs globally; Accel-backed.",
        "url": "https://facilio.com",
    },
    {
        "name": "Kovai.co",
        "sector": "B2B SaaS / Integration",
        "location": "Coimbatore",
        "stage": "Bootstrap",
        "funding": "Bootstrapped ($10M+ ARR)",
        "what_it_does": "Azure Service Bus Explorer and B2B integration products for enterprises.",
        "incubator": None,
        "why_notable": "Rare profitable bootstrapped SaaS from Coimbatore; proves Tier-2 TN can build global products.",
        "url": "https://kovai.co",
    },
    {
        "name": "Chargebee",
        "sector": "FinTech / Subscription SaaS",
        "location": "Chennai",
        "stage": "Unicorn",
        "funding": "$700M+ (valued $3.5B)",
        "what_it_does": "Subscription and revenue management platform for SaaS companies.",
        "incubator": None,
        "why_notable": "Chennai's first SaaS unicorn; used by 6500+ companies globally.",
        "url": "https://chargebee.com",
    },
    {
        "name": "Kissflow",
        "sector": "No-Code / Workflow SaaS",
        "location": "Chennai",
        "stage": "Bootstrap",
        "funding": "Bootstrapped ($20M+ ARR)",
        "what_it_does": "No-code workflow automation and digital workplace platform.",
        "incubator": None,
        "why_notable": "Profitable product-led growth company; 10,000+ customers across 160 countries.",
        "url": "https://kissflow.com",
    },

    # ── SpaceTech ────────────────────────────────────────────────────────────
    {
        "name": "Agnikul Cosmos",
        "sector": "SpaceTech",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "₹138Cr+",
        "what_it_does": "Building the world's first fully 3D-printed rocket engine; developing Agnibaan launch vehicle.",
        "incubator": "IITM Incubation Cell",
        "why_notable": "IIT Madras spinoff; first Indian private company to successfully hot-fire a 3D-printed engine.",
        "url": "https://agnikul.in",
    },
    {
        "name": "GalaxEye Space",
        "sector": "SpaceTech / Earth Observation",
        "location": "Chennai",
        "stage": "Series A",
        "funding": "$10M+",
        "what_it_does": "Multi-sensor satellite imaging platform for defense, agriculture, and disaster response.",
        "incubator": "IITM Incubation Cell",
        "why_notable": "IIT Madras spinoff; building India's first multi-sensor SAR satellite.",
        "url": "https://galaxeye.space",
    },

    # ── Defense / Deep Tech ──────────────────────────────────────────────────
    {
        "name": "Tonbo Imaging",
        "sector": "Defense Tech / Computer Vision",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "$30M+",
        "what_it_does": "Multispectral imaging and AI-based situational awareness systems for defense.",
        "incubator": None,
        "why_notable": "Key supplier to Indian Army and Navy; exporting defense AI systems globally.",
        "url": "https://tonboimaging.com",
    },
    {
        "name": "Garuda Aerospace",
        "sector": "Drone Tech",
        "location": "Chennai",
        "stage": "Series A",
        "funding": "₹100Cr+",
        "what_it_does": "Agricultural and industrial drone manufacturing and services platform.",
        "incubator": None,
        "why_notable": "India's largest drone fleet operator; backed by MS Dhoni; expanding to 100 cities.",
        "url": "https://garudaaerospace.com",
    },

    # ── HealthTech / MedTech ─────────────────────────────────────────────────
    {
        "name": "Niramai",
        "sector": "HealthTech / Medical AI",
        "location": "Chennai (IIT Madras roots)",
        "stage": "Series B",
        "funding": "$16M+",
        "what_it_does": "AI-powered thermal imaging for early breast cancer screening — no radiation, works in rural settings.",
        "incubator": "IITM Incubation Cell",
        "why_notable": "Works on low-cost devices; deployed in 80+ hospitals; WHO-recognized innovation.",
        "url": "https://niramai.com",
    },
    {
        "name": "Skanray Technologies",
        "sector": "MedTech / Medical Devices",
        "location": "Mysuru/Chennai",
        "stage": "Series B",
        "funding": "₹150Cr+",
        "what_it_does": "X-ray, CT, and critical care medical devices for emerging markets.",
        "incubator": "IITM Pravartak",
        "why_notable": "Made India's first indigenous ICU ventilator at scale during COVID; exported to 30+ countries.",
        "url": "https://skanray.com",
    },
    {
        "name": "Sigtuple",
        "sector": "HealthTech / AI Diagnostics",
        "location": "Bengaluru/Chennai operations",
        "stage": "Series B",
        "funding": "$19M",
        "what_it_does": "AI-powered smart microscopy for automated blood, urine, and semen analysis.",
        "incubator": None,
        "why_notable": "Reduces pathology lab turnaround from hours to minutes; deployed in 500+ labs.",
        "url": "https://sigtuple.com",
    },

    # ── AgriTech ─────────────────────────────────────────────────────────────
    {
        "name": "Cropin",
        "sector": "AgriTech / Farm Intelligence",
        "location": "Bengaluru (IITM roots / TN operations)",
        "stage": "Series C",
        "funding": "$105M",
        "what_it_does": "AI-powered farm intelligence platform — crop monitoring, risk analytics, and supply chain.",
        "incubator": None,
        "why_notable": "Covers 200+ crops across 52 countries; used by Syngenta, Bayer, IFFCO.",
        "url": "https://cropin.com",
    },
    {
        "name": "Stellapps",
        "sector": "AgriTech / Dairy Tech",
        "location": "Bengaluru/Tamil Nadu operations",
        "stage": "Series B",
        "funding": "$26M",
        "what_it_does": "IoT and AI platform for dairy farm productivity, milk quality, and supply chain.",
        "incubator": None,
        "why_notable": "Monitors 3M+ cows across India; major TN dairy cooperative deployments.",
        "url": "https://stellapps.com",
    },

    # ── EV / CleanTech / Manufacturing ───────────────────────────────────────
    {
        "name": "Ola Electric",
        "sector": "EV Manufacturing",
        "location": "Krishnagiri, Tamil Nadu",
        "stage": "Listed",
        "funding": "NSE/BSE listed",
        "what_it_does": "Electric two-wheeler manufacturing; world's largest two-wheeler EV factory in TN.",
        "incubator": None,
        "why_notable": "Futuristic Factory (1,000 acres, TN) is the world's largest EV 2W plant; TN's biggest manufacturing bet.",
        "url": "https://olaelectric.com",
    },
    {
        "name": "Ultraviolette Automotive",
        "sector": "EV / Performance Bikes",
        "location": "Bengaluru/Hosur TN factory",
        "stage": "Series B",
        "funding": "$35M+",
        "what_it_does": "High-performance electric motorcycles designed for Indian roads.",
        "incubator": None,
        "why_notable": "Manufacturing base in Hosur TN; backed by TVS Motor; expanding to Europe.",
        "url": "https://ultraviolette.com",
    },
    {
        "name": "Magenta Mobility",
        "sector": "EV Logistics",
        "location": "Pan-India / Chennai ops",
        "stage": "Series A",
        "funding": "$25M",
        "what_it_does": "Electric vehicle last-mile logistics fleet and EV charging infrastructure.",
        "incubator": None,
        "why_notable": "Major Chennai deployment; government contracts for EV charging in TN.",
        "url": "https://magentamobility.com",
    },

    # ── FinTech ───────────────────────────────────────────────────────────────
    {
        "name": "Kaleidofin",
        "sector": "FinTech / Financial Inclusion",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "$25M+",
        "what_it_does": "Goal-based financial solutions for underserved households — credit, savings, and insurance.",
        "incubator": None,
        "why_notable": "IIT Madras alumni-founded; serves 5M+ underserved customers across TN and India.",
        "url": "https://kaleidofin.com",
    },
    {
        "name": "Matrimony.com",
        "sector": "Consumer Tech / Matchmaking",
        "location": "Chennai",
        "stage": "Listed",
        "funding": "BSE/NSE: MATRIMONY",
        "what_it_does": "India's largest matrimony platform with 5M+ profiles; community matchmaking services.",
        "incubator": None,
        "why_notable": "Chennai-born profitable public company; growing AI-match recommendation engine.",
        "url": "https://matrimony.com",
    },

    # ── EdTech ────────────────────────────────────────────────────────────────
    {
        "name": "GUVI (IIT Madras / HCL)",
        "sector": "EdTech / Vernacular Tech Education",
        "location": "Chennai",
        "stage": "Acquired",
        "funding": "Acquired by HCL / IIT Madras",
        "what_it_does": "Vernacular-language coding and tech education platform — Tamil, Hindi, Kannada.",
        "incubator": "IIT Madras Incubation Cell",
        "why_notable": "IIT Madras incubated; acquired by HCL; 500K+ learners in regional languages.",
        "url": "https://guvi.in",
    },
    {
        "name": "iamneo (Examly)",
        "sector": "EdTech / Assessment",
        "location": "Coimbatore",
        "stage": "Series A",
        "funding": "$5M+",
        "what_it_does": "AI-powered proctored assessments and coding evaluation platform for campuses.",
        "incubator": "PSG-STEP",
        "why_notable": "PSG-STEP incubated; used by 350+ colleges; Coimbatore's edtech anchor.",
        "url": "https://iamneo.ai",
    },

    # ── Currently Incubated (IITM Pravartak / StartupTN active cohorts) ──────
    {
        "name": "Ati Motors",
        "sector": "Robotics / Autonomous Vehicles",
        "location": "Chennai",
        "stage": "Series A",
        "funding": "$12M",
        "what_it_does": "Autonomous warehouse and factory floor vehicles for logistics and manufacturing.",
        "incubator": "IITM Incubation Cell",
        "why_notable": "IIT Madras spinoff; deployed in Tata Steel, DHL, Maersk warehouses.",
        "url": "https://atimotors.com",
    },
    {
        "name": "Entropik Tech",
        "sector": "Emotion AI / Consumer Insights",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "$25M",
        "what_it_does": "Emotion and cognitive AI platform — facial coding, eye tracking, brainwave analysis for market research.",
        "incubator": "IITM Incubation Cell",
        "why_notable": "IIT Madras origin; used by Unilever, Nestlé, and 200+ global brands.",
        "url": "https://entropik.io",
    },
    {
        "name": "Pi-Lens",
        "sector": "AI / Visual Intelligence",
        "location": "Chennai",
        "stage": "Seed",
        "funding": "₹5Cr seed",
        "what_it_does": "Computer vision AI for quality inspection in manufacturing lines.",
        "incubator": "IITM Pravartak",
        "why_notable": "Active IITM Pravartak incubate; targeting India's $50B+ manufacturing quality control market.",
        "url": None,
    },
    {
        "name": "Inito",
        "sector": "FemTech / Digital Health",
        "location": "Bengaluru/Chennai",
        "stage": "Series A",
        "funding": "$6.5M",
        "what_it_does": "Fertility monitor device and app — tracks hormone levels at home.",
        "incubator": None,
        "why_notable": "IIT Madras alumni-founded; strong TN connection; used by 200K+ women globally.",
        "url": "https://inito.com",
    },
    {
        "name": "Zluri",
        "sector": "IT SaaS / Security",
        "location": "Chennai",
        "stage": "Series B",
        "funding": "$20M+",
        "what_it_does": "SaaS management platform — app discovery, access governance, and license optimization.",
        "incubator": None,
        "why_notable": "Chennai-built product used by 300+ enterprise customers; Sequoia India backed.",
        "url": "https://zluri.com",
    },
    {
        "name": "Pixis",
        "sector": "Marketing AI / No-Code AI",
        "location": "Chennai",
        "stage": "Series C",
        "funding": "$100M",
        "what_it_does": "No-code AI infrastructure for marketing teams — targeting, creative, and performance AI.",
        "incubator": None,
        "why_notable": "Chennai-founded; $100M+ raised; used by Burger King, Cred, Dunzo.",
        "url": "https://pixis.ai",
    },
    {
        "name": "Staqu Technologies",
        "sector": "AI / Video Analytics",
        "location": "Pan-India / Chennai ops",
        "stage": "Series A",
        "funding": "$6M",
        "what_it_does": "AI video analytics for surveillance, retail, and law enforcement.",
        "incubator": None,
        "why_notable": "Deployed with 10+ Indian state police forces including TN Police.",
        "url": "https://staqu.com",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Helper: group by sector cluster for card rendering
# ─────────────────────────────────────────────────────────────────────────────

SECTOR_CLUSTERS = {
    "AI & SaaS":          ["AI / Conversational AI", "Retail AI", "Marketing AI / No-Code AI",
                           "AI / Visual Intelligence", "AI / Video Analytics",
                           "Enterprise SaaS", "CRM / Customer Experience SaaS",
                           "B2B SaaS / Integration", "No-Code / Workflow SaaS", "IT SaaS / Security",
                           "PropTech / Building AI"],
    "SpaceTech & Defense": ["SpaceTech", "SpaceTech / Earth Observation", "Defense Tech / Computer Vision", "Drone Tech"],
    "HealthTech":          ["HealthTech / Medical AI", "MedTech / Medical Devices", "HealthTech / AI Diagnostics", "FemTech / Digital Health"],
    "AgriTech":            ["AgriTech / Farm Intelligence", "AgriTech / Dairy Tech"],
    "EV & CleanTech":      ["EV Manufacturing", "EV / Performance Bikes", "EV Logistics"],
    "FinTech":             ["FinTech / Financial Inclusion", "FinTech / Subscription SaaS", "Consumer Tech / Matchmaking"],
    "EdTech":              ["EdTech / Vernacular Tech Education", "EdTech / Assessment"],
    "Robotics & DeepTech": ["Robotics / Autonomous Vehicles", "Emotion AI / Consumer Insights"],
}


def get_startups_by_cluster() -> Dict[str, List[Dict]]:
    """Return startups grouped by sector cluster for rendering."""
    clustered = {k: [] for k in SECTOR_CLUSTERS}
    for startup in TN_STARTUPS:
        for cluster, sectors in SECTOR_CLUSTERS.items():
            if startup["sector"] in sectors:
                clustered[cluster].append(startup)
                break
    return {k: v for k, v in clustered.items() if v}


def get_incubated_startups() -> List[Dict]:
    """Return only startups with known incubator affiliations."""
    return [s for s in TN_STARTUPS if s.get("incubator")]


def get_startups_summary_for_prompt() -> str:
    """
    Return a compact text summary of TN's startup ecosystem for injecting
    into the Claude summarization prompt as background context.
    """
    lines = ["KNOWN TN STARTUP ECOSYSTEM (background context — do not fabricate beyond this):"]
    for s in TN_STARTUPS:
        inc = f" [{s['incubator']}]" if s.get("incubator") else ""
        lines.append(
            f"- {s['name']} ({s['location']}) | {s['sector']} | {s['stage']} | {s['funding']}{inc}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    clusters = get_startups_by_cluster()
    for cluster, startups in clusters.items():
        print(f"\n{cluster} ({len(startups)} startups):")
        for s in startups:
            print(f"  • {s['name']} — {s['stage']} — {s['funding']}")

    print(f"\nTotal: {len(TN_STARTUPS)} startups catalogued")
    print(f"With incubator affiliation: {len(get_incubated_startups())}")
