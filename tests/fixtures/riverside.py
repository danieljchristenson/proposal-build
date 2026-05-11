"""Riverside MetroLink fixture — zone-heavy multi-station civic project.

Anchored on the same Riverside MetroLink project as before, but reshaped
from the old "showcase categories" model to true zone vocabulary. Each
station on the line is a zone. With 6 zones the deck would stretch out
endlessly using zone_solo only — Plan 3 will pick zone_2up / zone_3up /
zone_index based on count.

This fixture exists to prove the zone-grouped layouts work at scale.
The destination-style fixture (Pier 39, 3 zones) lives in pier_39.py.

Per the 2026-05-03 decision (memory: project_riverside_renderings_in_fixture):
this fixture wires four real renderings from the Downtown Riverside
MetroLink project folder so the eyeball pass is meaningful. Pier 39
stays image-less. Plan 3's AE workflow will replace these test-fixture
defaults with per-project AE selections.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RIVERSIDE = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"
RENDERINGS_DIR = RIVERSIDE / "02 - Renderings"
BASE_SCOPE = RENDERINGS_DIR / "Base Scope"
ENHANCEMENTS = RENDERINGS_DIR / "Enhancements"

NO_IMAGE = None

# Real renderings wired into hero_image fields (option A, 2026-05-03).
# Stored as file:// URIs so WeasyPrint resolves absolute paths regardless of
# the test conftest's base_url. Path.as_uri() percent-encodes spaces.
COVER_HERO = (BASE_SCOPE / "Wreath - Brick Column Night.jpg").as_uri()
CREATIVE_HERO = (BASE_SCOPE / "Pole Banner Artwork - Holiday Express 01.jpg").as_uri()
FLAGSHIP_HERO = (BASE_SCOPE / "Walk-Through Ornament - Warm White.png").as_uri()
CASE_STUDY_HERO = (BASE_SCOPE / "Evening Lighting - Station Awning 01.png").as_uri()


PROJECT = {
    "client_company": "Riverside County Transportation Commission (RCTC)",
    "client_short": "RCTC METROLINK",
    "project_name": "Riverside MetroLink",
    "project_short": "MetroLink",
    "project_year": 2026,
    "project_subtitle": "Six-Station Civic Holiday Program",
    "presenter_name": "Jonathan Yang",
    "presenter_title": "Account Executive",
    "presenter_org": "St. Nick's Christmas Lighting & Décor",
    "proposal_date": "May 12, 2026",
    "page_total": 14,   # +1 vs Pier 39 because this deck includes a zone_index slide
}


# Six stations along the MetroLink line — each is a zone.
ZONES = [
    {"num": "01", "name": "Downtown Riverside",   "subtitle": "The flagship station — civic centerpiece.",
     "included_elements": ["Custom-fabricated wreaths at every entrance", "Full-canopy garland across the platform overhang", "Pole banner program (8 poles)"]},
    {"num": "02", "name": "La Sierra",            "subtitle": "First park-and-ride stop — community gateway.",
     "included_elements": ["Wreaths at primary entrance", "Pole banner program (4 poles)", "Lighted accent at platform sign"]},
    {"num": "03", "name": "Pedley",               "subtitle": "Mid-line residential stop — restrained festive treatment.",
     "included_elements": ["Garland across platform railing", "Two pole banners at station entry"]},
    {"num": "04", "name": "Riverside-Hunter Park","subtitle": "University-adjacent — student-traffic focus.",
     "included_elements": ["Pole banner program (6 poles)", "Lighted gateway display at the bus interchange", "Wreaths at the eastbound entry"]},
    {"num": "05", "name": "Moreno Valley/March Field","subtitle": "Outer line — visible from the freeway.",
     "included_elements": ["Large-format pole banner program (10 poles, freeway-side)", "Lighted snowflake constellation along the platform"]},
    {"num": "06", "name": "Perris-Downtown",      "subtitle": "End of line — community arrival moment.",
     "included_elements": ["Walk-through ornament arch at the plaza", "Wreaths and garland at all entrances", "Pole banner program (4 poles)"]},
]


# ===== Slide 1 — Cover =====
cover_ctx = {
    **PROJECT,
    "page_num": 1,
    "season_label": "2026 HOLIDAY SEASON",
    "hero_image": COVER_HERO,
    "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
}


# ===== Slide 2 — Executive Summary =====
exec_summary_ctx = {
    **PROJECT,
    "page_num": 2,
    "page_title": "Executive Summary",
    "standfirst": "A six-station holiday program for the Riverside MetroLink line, at a glance.",
    "body_paragraphs": [
        "St. Nick's is proposing a coordinated holiday décor program across all six stations of the Riverside MetroLink line — a single visual identity that scales from flagship Downtown Riverside through to Perris-Downtown.",
        "Our approach builds civic pride at every stop while keeping operational discipline tight: install and removal coordinate with revenue service hours, all materials clear MetroLink overhead catenary safety envelope, and the design language repeats so every station reads as part of one program.",
    ],
    "at_a_glance": [
        ("PROJECT", "2026 Civic Holiday Program", False),
        ("STATIONS", "Six (Downtown Riverside → Perris-Downtown)", False),
        ("RECOMMENDED TIER", "Enhanced", False),
        ("INVESTMENT RANGE", "$184K — $384K", False),
        ("GO LIVE", "Fri, Nov 20, 2026", False),
        ("FABRICATION LOCK", "Aug 22, 2026", True),
        ("SIGNING DEADLINE", "Oct 30, 2026", True),
    ],
    "pillars": [
        {"title": "Civic Pride",            "body": "A holiday program that elevates Riverside as a destination, not just a transit stop."},
        {"title": "Operational Discipline", "body": "Materials engineered for transit weather; install coordinated with MetroLink service hours."},
        {"title": "Repeatable Investment",  "body": "Decor designed for multi-season reuse; 2026 builds the base for 2027 and 2028."},
    ],
}


# ===== Slide 3 — Our Understanding =====
understanding_ctx = {
    **PROJECT,
    "page_num": 3,
    "page_title": "Our Understanding",
    "standfirst": "Playback of discovery — so we're all working from the same page.",
    "panels": [
        {"title": "VENUE & CONTEXT", "body": "The MetroLink line connects six communities across Riverside County. Holiday season foot-traffic spikes at flagship Downtown Riverside; outer stations carry mostly commuter and park-and-ride traffic with civic-pride significance for local residents."},
        {"title": "GOALS FOR 2026",  "body": "Establish RCTC's MetroLink line as a regional holiday destination; drive non-transit foot traffic to Downtown Riverside in particular; position the County as a leader in civic seasonal programming."},
        {"title": "KEY CONSTRAINTS", "body": "All decor must clear MetroLink overhead catenary safety envelope. Install and removal must occur outside revenue service hours. Materials must withstand winter Santa Ana wind events."},
        {"title": "WHAT SUCCESS LOOKS LIKE", "body": "Measurable increase in evening visitors during the program window. Local press and social media coverage of the activation. Zero MetroLink operational disruptions during install/strike."},
    ],
}


# ===== Slide 4 — Creative Vision =====
creative_vision_ctx = {
    **PROJECT,
    "page_num": 4,
    "page_title": "Creative Vision",
    "standfirst": "The design direction for the 2026 MetroLink program.",
    "design_phrase": "Holiday Express.",
    "design_direction_body": "A civic-scale holiday aesthetic that turns the MetroLink line itself into the holiday gesture. Wreaths and garlands frame each station entrance like a ceremonial gateway; evening lighting turns the platforms themselves into destinations after sundown. The same design vocabulary repeats at every stop so the line reads as one program from end to end.",
    "phases": [
        {"label": "WELCOME",  "body": "Wreaths and garlands at every station entrance — the holiday begins at the curb."},
        {"label": "JOURNEY",  "body": "Pole banners and platform lighting carry the design language down the line."},
        {"label": "ARRIVAL",  "body": "Walk-through ornament and lit displays at end-of-line — a destination, not a transfer."},
    ],
    "hero_image": CREATIVE_HERO,
}


# ===== Slide 5 — Zone Index (overview of all 6 zones) =====
zone_index_ctx = {
    **PROJECT,
    "page_num": 5,
    "page_title": "The Program at a Glance",
    "standfirst": "Six stations, one design language. Here's how the program reads from end to end.",
    "zones": ZONES,
}


# ===== Slide 6 — Zone solo: Downtown Riverside (flagship, signature treatment) =====
zone_flagship_ctx = {
    **PROJECT,
    "page_num": 6,
    "zone_num": "01",
    "zone_name": "Downtown Riverside",
    "zone_subtitle": "The flagship station — civic centerpiece.",
    "included_elements": ZONES[0]["included_elements"] + [
        "Lighted walk-through arch at plaza forecourt",
        "Evening lighting program — platform + awning + curb-edge",
        "On-site QC walkthrough with RCTC Capital Projects",
    ],
    "hero_image": FLAGSHIP_HERO,
}


# ===== Slide 7 — Zones 2-up: La Sierra + Pedley =====
zone_2up_a_ctx = {
    **PROJECT,
    "page_num": 7,
    "page_title": "Program Zones",
    "standfirst": "Stations 02 and 03 — the gateway and the residential stop.",
    "zones": [ZONES[1], ZONES[2]],
}


# ===== Slide 8 — Zones 3-up: Hunter Park + Moreno Valley + Perris =====
zone_3up_ctx = {
    **PROJECT,
    "page_num": 8,
    "page_title": "Program Zones",
    "standfirst": "Stations 04, 05, and 06 — the outer line.",
    "zones": [ZONES[3], ZONES[4], ZONES[5]],
}


# ===== Slide 9 — Scope of Work =====
scope_ctx = {
    **PROJECT,
    "page_num": 9,
    "page_title": "Scope of Work",
    "standfirst": "What your investment includes, and what you can add on.",
    "includes": [
        "Custom-fabricated wreaths (every station entrance)",
        "Decorated and undecorated garland (six stations)",
        "Pole banner program (32 poles total, two artwork variants)",
        "Evening lighting program — Downtown Riverside (4 zones)",
        "Walk-through ornament arch — flagship station",
        "Install + strike per MetroLink operational windows",
        "On-site QC walkthrough with RCTC Capital Projects",
        "Storage between deinstall and 2027 program",
    ],
    "add_ons": [
        ("Spiral LED tree at flagship forecourt",      "+$8K"),
        ("Lighted bell display, plaza-side",           "+$5K"),
        ("Lighted snowflakes on platform railing (per station)", "+$2K each"),
        ("Lighted gift-box towers, plaza pair",        "+$7K"),
        ("Walk-through display refresh (existing arch)","+$3K"),
        ("Multi-year partnership (see Investment page)","Varies"),
    ],
}


# ===== Slide 10 — Case Study =====
case_study_ctx = {
    **PROJECT,
    "page_num": 10,
    "page_eyebrow": "CASE STUDY",
    "page_title": "Long Beach Transit · 2024",
    "standfirst": "A multi-station civic holiday program at scale, delivered in a single season.",
    "challenge": "Roll out a coordinated holiday décor program across 14 transit stations on a tight budget and an even tighter install window — all installs had to land within a 21-day overnight window without disrupting revenue service.",
    "approach":  "Standardized fabrication kits per station tier (flagship / standard / outpost). Pre-staged shipments at the operations yard. Crew rotated through stations on a strict overnight schedule with QC walks at sunrise.",
    "outcome":   "All 14 stations live on schedule. Zero revenue-service disruptions. Local press coverage at six of the fourteen stations. Program renewed for 2025 with three additional stations.",
    "hero_image": CASE_STUDY_HERO,
}


# ===== Slide 11 — Investment =====
investment_ctx = {
    **PROJECT,
    "page_num": 11,
    "page_title": "Investment",
    "standfirst": "Three levels of program. Pick what fits your season.",
    "tiers": [
        {
            "name": "ESSENTIAL", "rule_color": "gray", "tagline": "FLAGSHIP-ONLY PRESENCE",
            "highlights": ["Downtown Riverside only", "Core wreaths + garland", "Pole banner program (8 poles)", "Standard install + strike"],
            "price": "$184,500", "is_recommended": False,
        },
        {
            "name": "ENHANCED",  "rule_color": "red",  "tagline": "FULL LINE PROGRAM",
            "highlights": ["Everything in Essential, plus:", "All six stations covered", "Evening lighting program at flagship", "Walk-through ornament — flagship plaza", "MetroLink ops-window install"],
            "price": "$284,500", "is_recommended": True,
        },
        {
            "name": "SIGNATURE", "rule_color": "navy", "tagline": "REGIONAL DESTINATION",
            "highlights": ["Everything in Enhanced, plus:", "Spiral LED tree — flagship forecourt", "Lighted bell + gift-box towers", "Programmatic snowflake railing (all stations)", "On-site staffing during install + strike"],
            "price": "$384,500", "is_recommended": False,
        },
    ],
    "tier_count": 3,
    "partnership_discounts": [
        ("2-YEAR", "4% OFF"),
        ("3-YEAR", "6% OFF"),
        ("5-YEAR", "9% OFF"),
    ],
    "footer_note": "Pricing valid 30 days from proposal date. Fabrication must be locked by Aug 22, 2026.",
}


# ===== Slide 12 — Terms & Next Steps =====
terms_ctx = {
    **PROJECT,
    "page_num": 12,
    "page_title": "Terms & Next Steps",
    "standfirst": "The critical dates and terms for the 2026 program.",
    "critical_dates": [
        ("October 30, 2026", "Execute by this date to guarantee the install schedule."),
        ("August 22, 2026",  "All custom fabrication must be approved by this date (90 days pre-Go Live)."),
    ],
    "term_panels": [
        ("PAYMENT SCHEDULE",   "30% deposit on signing — required to lock the install schedule. 40% on fabrication start. 30% on go-live. Net-15 terms on final invoice."),
        ("INSURANCE & PERMITS","$5M Umbrella over $1M/$2M Commercial General Liability and $1M Auto; full Workers' Comp at statutory limits. Certificates issued to RCTC at signing. MetroLink coordination handled by RCTC; we provide full documentation support."),
        ("CHANGE ORDERS",      "Includes 2 creative revision rounds before Fabrication Lock (Aug 22, 2026). Scope or timeline changes after that date follow our standard change-order workflow — written approval required, priced at materials + 35%."),
        ("PROPOSAL VALIDITY",  "This proposal is valid 60 days from May 12, 2026. Materials pricing subject to market conditions thereafter. Sign by Oct 30 to lock schedule."),
    ],
    "after_approval_steps": ["Kickoff call within 48 hrs", "Creative window opens", "Renderings final by Aug 1"],
}


# ===== Slide 13 — Sign-off =====
sign_off_ctx = {
    **PROJECT,
    "page_num": 13,
    "page_title": "Let's Make It Happen",
    "standfirst": "Sign below to launch the 2026 MetroLink Holiday Program.",
    "what_youre_approving": "The 2026 Riverside MetroLink Holiday Program — six stations from Downtown Riverside through Perris-Downtown, live Nov 20, 2026 through Jan 5, 2027, at the tier and add-ons you select on the Investment page.",
    "client_party_label":   "RCTC AUTHORIZATION",
    "stnicks_party_label":  "ST. NICK'S AUTHORIZED SIGNATURE",
    "digital_signing_note": "Prefer to sign digitally? Use the Canva e-signature link in your email. Questions? Reply directly — we'll respond within 24 hours.",
}


# ===== Slide 14 — About St. Nick's =====
about_ctx = {
    **PROJECT,
    "page_num": 14,
    "page_title": "About St. Nick's",
    "standfirst": "25 years of large-scale holiday design, installation, and service.",
    "company_facts": [
        "Founded 1998 (dba St. Nick's) — T&G Global, LLC",
        "14 full-time team · 30–45 seasonal staff",
        "B-General Building Contractor #990427",
        "Certified Small Business Supplier #1626660",
        "$5M Umbrella · $1M/$2M GL · $1M Auto · Full Workers' Comp",
        "200+ commercial venues across North America",
    ],
    "team": [
        {"name": "Nicholas Adams",   "role": "Founder"},
        {"name": "Wade Francis",     "role": "Chief Financial Officer"},
        {"name": "Brenda Sheridan",  "role": "Director of Operations"},
        {"name": "Daniel Christenson","role": "Director of Sales"},
        {"name": "Stephanie Escobar","role": "Creative Director"},
        {"name": "Carlos Vasquez & Alonso Salazar", "role": "Senior Installers / Project Managers"},
    ],
    "contact_strip": "ST-NICKS.COM  ·  (562) 438-0017  ·  6861 Walker St, La Palma, CA 90623  ·  © 2026 St. Nick's Christmas Lighting & Décor",
}
