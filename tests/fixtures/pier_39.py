"""Pier 39 fixture — destination-style proposal with 3 zones.

Content matches Master Proposal Reference/StNicks_Proposal_v2_Master.pdf
verbatim, since the master is built around this project. Drives the
"destination path" through the layout system: zone_solo for non-signature
zones, zone_solo_fullbleed for the signature zone.

Plan 3 will produce dicts of the same shape from real Brief.md +
Scope Worksheet.xlsx + rendering folders. Until then this file IS the
data. Each per-layout ctx dict is a dict that gets passed to Jinja2 as
the rendering context. Common project-wide values are assembled into
PROJECT and merged via {**PROJECT, ...}.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# No real Pier 39 renderings are in the test fixtures yet — when the
# Plan 3 AE workflow lands, real images will replace these placeholders.
# For now hero_image fields are None; layouts must render a placeholder
# when no image is supplied (tested via dark grey rectangle).
NO_IMAGE = None


PROJECT = {
    "client_company": "Pier 39",
    "client_short": "PIER 39 SAN FRANCISCO",
    "project_name": "Pier 39",
    "project_short": "Pier 39",
    "project_year": 2026,
    "project_subtitle": "San Francisco",
    "presenter_name": "Daniel Christenson",
    "presenter_title": "Director of Sales",
    "presenter_org": "St. Nick's Christmas Lighting & Décor",
    "proposal_date": "October 15, 2026",
    "page_total": 13,
}


# ===== Slide 1 — Cover =====
cover_ctx = {
    **PROJECT,
    "page_num": 1,
    "season_label": "2026 HOLIDAY SEASON",
    "hero_image": NO_IMAGE,
    "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
}


# ===== Slide 2 — Executive Summary =====
exec_summary_ctx = {
    **PROJECT,
    "page_num": 2,
    "page_title": "Executive Summary",
    "standfirst": "Our 2026 holiday program for Pier 39, at a glance.",
    "body_paragraphs": [
        "St. Nick's is proposing a destination-scale holiday program for Pier 39 — a designed, fabricated, installed, and serviced lighting and décor experience across three of the property's highest-traffic guest zones.",
        "Our approach builds a signature visual identity for Pier 39's 2026 holiday season, driving guest dwell time, social shareability, and differentiation from neighboring attractions along the Embarcadero.",
    ],
    "at_a_glance": [
        ("PROJECT", "2026 Holiday Program", False),
        ("ZONES", "Embarcadero · Promenade · Bay Terrace", False),
        ("RECOMMENDED TIER", "Enhanced", False),
        ("INVESTMENT RANGE", "$225K — $485K", False),
        ("GO LIVE", "Fri, Nov 20, 2026", False),
        ("FABRICATION LOCK", "Aug 22, 2026", True),
        ("SIGNING DEADLINE", "Nov 14, 2026", True),
    ],
    "pillars": [
        {"title": "Turnkey Delivery",   "body": "Concept through teardown — one partner, zero seams."},
        {"title": "Destination Scale",  "body": "Built for venues hosting millions of guests per season."},
        {"title": "25 Years at It",     "body": "From Pier 39 to Disney Parks, we've done this before."},
    ],
}


# ===== Slide 3 — Our Understanding =====
understanding_ctx = {
    **PROJECT,
    "page_num": 3,
    "page_title": "Our Understanding",
    "standfirst": "Playback of discovery — so we're all working from the same page.",
    "panels": [
        {"title": "VENUE & CONTEXT", "body": "Pier 39 is San Francisco's iconic waterfront destination — 45 acres of retail, dining, and entertainment hosting 10M+ annual guests. Holiday season drives peak family traffic from Thanksgiving through New Year's."},
        {"title": "GOALS FOR 2026",  "body": "Amplify the arrival experience, extend guest dwell time through the holiday window, and create shareable photo moments that reinforce Pier 39's position as Northern California's premier holiday destination."},
        {"title": "KEY CONSTRAINTS", "body": "Phased install during overnight windows to avoid retail disruption. Zero impact to the sea lion habitat at K-Dock. All-weather durability required. Full removal and storage complete by January 15, 2027."},
        {"title": "WHAT SUCCESS LOOKS LIKE", "body": "A signature holiday identity photographed and shared 10x the volume of 2025. Measurable dwell-time lift. A program built for multi-year refresh and extension into Pier 39's broader marketing narrative."},
    ],
}


# ===== Slide 4 — Creative Vision =====
creative_vision_ctx = {
    **PROJECT,
    "page_num": 4,
    "page_title": "Creative Vision",
    "standfirst": "The design direction for Pier 39's 2026 holiday program.",
    "design_phrase": "Bayside Twilight.",
    "design_direction_body": "A cinematic holiday aesthetic that honors Pier 39's waterfront character — warm whites and brushed gold set against the Bay at twilight, oversized architectural lighting, and seasonal storytelling that unfolds as guests move through the property.",
    "phases": [
        {"label": "ARRIVE",   "body": "Warm, cinematic welcome."},
        {"label": "EXPLORE",  "body": "Discoverable moments along the Promenade."},
        {"label": "CELEBRATE","body": "A landmark scene at the Bay Terrace."},
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 5 — Zone 01: Embarcadero Arrival (zone_solo) =====
zone_01_ctx = {
    **PROJECT,
    "page_num": 5,
    "zone_num": "01",
    "zone_name": "Embarcadero Arrival",
    "zone_subtitle": "First impression. The threshold between the city and Pier 39.",
    "included_elements": [
        "28' illuminated entry arch",
        "Pair of 14' flanking classic trees",
        "Custom 'Welcome to Pier 39' marquee",
        "Warm-white garland across arch beams",
        "Brushed-gold ribbon accents",
        "Dusk-to-dawn programming",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 6 — Zone 02: Pier Promenade (zone_solo) =====
zone_02_ctx = {
    **PROJECT,
    "page_num": 6,
    "zone_num": "02",
    "zone_name": "Pier Promenade",
    "zone_subtitle": "A layered, discoverable journey through the heart of the Pier.",
    "included_elements": [
        "220 linear feet of illuminated tree wrap",
        "Four 8' oversized ornament installations",
        "Suspended starlight canopy over Central Plaza",
        "Two custom photo moments (K-Dock + fountain)",
        "Themed garland across retail storefronts",
        "Hot cocoa concierge station (Fri–Sun)",
        "Curated wreath package on Pier architecture",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 7 — Zone 03: Bay Terrace (zone_solo_fullbleed, signature) =====
zone_03_ctx = {
    **PROJECT,
    "page_num": 7,
    "zone_num": "03",
    "zone_name": "Bay Terrace",
    "zone_subtitle": "The signature moment. The destination within the destination.",
    "included_elements": [
        "40' walkthrough signature tree",
        "Illuminated Bay view photo frame",
        "Suspended snowflake constellation",
        "Custom \"Happy Holidays, Pier 39\" marquee",
        "Gold-accented architectural pier lighting",
        "Nightly synchronized music + light show",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 8 — Scope of Work =====
scope_ctx = {
    **PROJECT,
    "page_num": 8,
    "page_title": "Scope of Work",
    "standfirst": "What your investment includes, and what you can add on.",
    "includes": [
        "Creative design + client-approved renderings",
        "All materials, décor, and lighting elements",
        "Installation labor (3-week phased window)",
        "Testing, commissioning, and launch night support",
        "Daily programming (dusk-to-dawn schedule)",
        "Weekly on-site maintenance visits (Nov 20 – Jan 5)",
        "24/7 season on-call response (4-hour SLA)",
        "Complete post-season teardown and removal",
        "Storage of reusable elements at our facility",
    ],
    "add_ons": [
        ("Extended programming (Halloween kickoff)", "+$12K"),
        ("Maintenance upgrade (2x weekly visits)",   "+$9K"),
        ("Custom photo-op signage package",          "+$14K"),
        ("Scheduled mid-season creative refresh",    "+$18K"),
        ("Synchronized music + full light show",     "+$24K"),
        ("On-site producer (peak Fri/Sat nights)",   "+$16K"),
        ("Priority 2-hour SLA upgrade",              "+$8K"),
        ("Extended installation (add-week)",         "+$22K"),
        ("Multi-year partnership (see Investment page)", "Varies"),
    ],
}


# ===== Slide 9 — Case Study =====
case_study_ctx = {
    **PROJECT,
    "page_num": 9,
    "page_eyebrow": "CASE STUDY",
    "page_title": "Oregon Zoo · ZooLights 2025",
    "standfirst": "Transforming Portland's family destination into a signature winter experience.",
    "challenge": "Deliver a full property-wide holiday transformation across 64 acres of active zoological habitats, with zero disruption to animal welfare protocols and overnight install windows aligned to keeper schedules.",
    "approach":  "Phased 18-night install coordinated with animal care teams. Custom low-impact lighting specifications. A signature 45-ft illuminated central tree, themed habitat lighting, and an interactive Light Walk that shifted weekly.",
    "outcome":   "31% YoY increase in ZooLights attendance. 4.2M+ social impressions. Partnership renewed through 2028. Feature coverage in The Oregonian, KGW, and Travel + Leisure.",
    "hero_image": NO_IMAGE,
}


# ===== Slide 10 — Investment =====
investment_ctx = {
    **PROJECT,
    "page_num": 10,
    "page_title": "Investment",
    "standfirst": "Three levels of program. Pick what fits your season.",
    "tiers": [
        {
            "name": "ESSENTIAL",
            "rule_color": "gray",
            "tagline": "CORE HOLIDAY PRESENCE",
            "highlights": [
                "Zone 01 (Embarcadero) only",
                "Core lighting + décor",
                "Weekly maintenance",
                "Dusk-to-dawn programming",
            ],
            "price": "$225,000",
            "is_recommended": False,
        },
        {
            "name": "ENHANCED",
            "rule_color": "red",
            "tagline": "FULL GUEST EXPERIENCE",
            "highlights": [
                "Everything in Essential, plus:",
                "Zones 02 + 03",
                "Custom photo moments",
                "Suspended starlight canopy",
                "24/7 on-call response",
            ],
            "price": "$345,000",
            "is_recommended": True,
        },
        {
            "name": "SIGNATURE",
            "rule_color": "navy",
            "tagline": "DESTINATION EXPERIENCE",
            "highlights": [
                "Everything in Enhanced, plus:",
                "40' signature tree + marquee",
                "Synchronized music + light show",
                "Mid-season creative refresh",
                "On-site producer, priority SLA",
            ],
            "price": "$485,000",
            "is_recommended": False,
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


# ===== Slide 11 — Terms & Next Steps =====
terms_ctx = {
    **PROJECT,
    "page_num": 11,
    "page_title": "Terms & Next Steps",
    "standfirst": "The critical dates and terms for the 2026 program.",
    "critical_dates": [
        ("November 14, 2026", "Execute by this date to guarantee the install schedule."),
        ("August 22, 2026",   "All custom fabrication must be approved by this date (90 days pre-Go Live)."),
    ],
    "term_panels": [
        ("PAYMENT SCHEDULE",   "50% deposit upon contract execution — required to lock the install schedule. 50% balance due upon completion of post-season teardown (Jan 15, 2027). Net-15 terms on final invoice."),
        ("INSURANCE & PERMITS","$5M Umbrella over $1M/$2M Commercial General Liability and $1M Auto; full Workers' Comp at statutory limits. Certificates available upon request. Municipal permits handled by Pier 39; we provide full documentation support."),
        ("CHANGE ORDERS",      "Includes 2 creative revision rounds before Fabrication Lock (Aug 22, 2026). Changes after that date require a written change order: 30% of the value of any item removed from scope, plus full value of any item added."),
        ("PROPOSAL VALIDITY",  "This proposal is valid 30 days from October 15, 2026. Materials pricing subject to market conditions thereafter. Sign by Nov 14 to lock schedule."),
    ],
    "after_approval_steps": ["Kickoff call within 48 hrs", "Creative window opens", "Renderings final by Aug 1"],
}


# ===== Slide 12 — Sign-off =====
sign_off_ctx = {
    **PROJECT,
    "page_num": 12,
    "page_title": "Let's Make It Happen",
    "standfirst": "Sign below to launch Pier 39's 2026 holiday program.",
    "what_youre_approving": "The 2026 Pier 39 holiday program — three zones (Embarcadero Arrival, Pier Promenade, Bay Terrace), live Nov 20, 2026 through Jan 5, 2027, at the tier and add-ons you select on the Investment page.",
    "client_party_label":   "CLIENT AUTHORIZATION",
    "stnicks_party_label":  "ST. NICK'S AUTHORIZED SIGNATURE",
    "digital_signing_note": "Prefer to sign digitally? Use the Canva e-signature link in your email. Questions? Reply directly — we'll respond within 24 hours.",
}


# ===== Slide 13 — About St. Nick's =====
about_ctx = {
    **PROJECT,
    "page_num": 13,
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


# ── Tree Comparison fixture (Plan 11) ──
# Synthetic 3-card ctx for the tree_comparison layout render test. Images
# come from tests/fixtures/tree_library/ so the rendered card shows a real
# (1x1 JPEG) photo asset.
_TREE_LIBRARY_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "tree_library"

tree_comparison_ctx = {
    **PROJECT,
    "page_num": 11,
    "page_total": 12,
    "page_eyebrow": "Alternate Tree Options",
    "page_title": "Three scale options",
    "standfirst": (
        "Three commercial frame trees, side by side. Each replaces the "
        "program tree in Section 2; the surrounding enhancement package "
        "carries over to whichever tree you pick."
    ),
    "cards": [
        {
            "rule_color": "gray",
            "image": (_TREE_LIBRARY_FIXTURE_DIR / "fixture_tree_a.jpg").as_uri(),
            "height_eyebrow": "30 FT",
            "name": "Sample Tree A — 30 ft",
            "tagline": "Compact landmark presence.",
            "bullets": [
                "18,700 warm-white LED lights",
                "3,740 ornaments · 20 per branch fully decorated",
                "15 ft canopy diameter at base",
                "5 ft illuminated tree top · welded steel mast",
            ],
            "price_display": "$60,153",
            "price_sublabel": "PURCHASE · FULLY DECORATED",
            "is_recommended": False,
        },
        {
            "rule_color": "red",
            "image": (_TREE_LIBRARY_FIXTURE_DIR / "fixture_tree_b.jpg").as_uri(),
            "height_eyebrow": "40 FT",
            "name": "Sample Tree B — 40 ft",
            "tagline": "Confident centerpiece scale.",
            "bullets": [
                "38,200 warm-white LED lights",
                "7,640 ornaments · 20 per branch fully decorated",
                "20 ft canopy diameter at base",
                "5 ft illuminated tree top · welded steel mast",
            ],
            "price_display": "$131,778",
            "price_sublabel": "PURCHASE · FULLY DECORATED",
            "is_recommended": True,
        },
        {
            "rule_color": "navy",
            "image": (_TREE_LIBRARY_FIXTURE_DIR / "fixture_tree_c.jpg").as_uri(),
            "height_eyebrow": "50 FT",
            "name": "Sample Tree C — 50 ft",
            "tagline": "Hero-scale flagship statement.",
            "bullets": [
                "65,200 warm-white LED lights",
                "13,040 ornaments · 20 per branch fully decorated",
                "25 ft canopy diameter at base",
                "5 ft illuminated tree top · welded steel mast",
            ],
            "price_display": "$244,991",
            "price_sublabel": "PURCHASE · FULLY DECORATED",
            "is_recommended": False,
        },
    ],
}
