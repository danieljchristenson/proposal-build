"""Hand-built Jinja2 contexts for each of the 18 Plan 2 layouts.

Anchored on the Downtown Riverside MetroLink project where data exists.
Where Riverside doesn't yet have content (no case study selected, no
past-work library populated), values are plausible-but-fabricated and
consistent with St. Nick's voice and existing examples.

Plan 3's parsers will produce dicts of the same shape from real
Brief.md + Scope Worksheet.xlsx + rendering folders. Until then, this
file IS the data.

Filenames in *_image / *_renderings keys are paths relative to the
repo root, used by layouts as <img src="file://..."> URLs WeasyPrint
will resolve at render time.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RIVERSIDE = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"
RENDERINGS_DIR = RIVERSIDE / "02 - Renderings"
BASE_SCOPE = RENDERINGS_DIR / "Base Scope"
ENHANCEMENTS = RENDERINGS_DIR / "Enhancements"


def _path(d: Path, name: str) -> str:
    """Return a file:// URL for an absolute repo-relative rendering path.

    WeasyPrint resolves these at render time. We return file:// URLs
    rather than relative paths because the layouts live in
    skill_assets/layouts/ and renderings live elsewhere — base_url
    resolution would not span those trees.
    """
    p = d / name
    return p.as_uri()


# Common project-wide values reused by multiple fixtures.
PROJECT = {
    "client_company": "Riverside County Transportation Commission (RCTC)",
    "client_short": "RCTC",
    "decision_maker": "Jacklyn Moreno",
    "decision_maker_title": "Capital Projects Manager",
    "project_name": "Downtown Riverside MetroLink — 2026 Holiday Program",
    "project_short": "Riverside MetroLink",
    "project_year": 2026,
    "presenter_name": "Jonathan Yang",
    "presenter_email": "jonathan@st-nicks.com",
    "presenter_phone": "(562) 438-0017",
    "design_phrase": "Holiday Express",
    "voice": "civic",
}


# Each layout's fixture is appended below by its task.
# (Layouts are added in the order of the slide catalog.)


# ===== Slide 1 — Cover =====
cover_ctx = {
    **PROJECT,
    "cover_image": _path(BASE_SCOPE, "Wreaths - Station Entrance 01.png"),
    "presentation_date": "May 2026",
}


# ===== Slide 2 — Executive Summary =====
exec_summary_ctx = {
    **PROJECT,
    "tier_recommended": "Enhanced",
    "deck_length": 16,
    "investment_total": "$284,500",
    "go_live_date": "November 20, 2026",
    "season_end_date": "January 5, 2027",
    "pillars": [
        {
            "title": "Civic Pride",
            "body": "A holiday program that elevates Riverside as a destination — drawing visitors to a transit hub typically used in transit only.",
        },
        {
            "title": "Operational Discipline",
            "body": "Materials engineered for transit weather and high foot traffic; install and removal coordinated with MetroLink service hours.",
        },
        {
            "title": "Repeatable Investment",
            "body": "Decor designed for multi-season reuse; the 2026 program builds the base for 2027 and 2028 expansions.",
        },
    ],
}


# ===== Slide 3 — Our Understanding =====
understanding_ctx = {
    **PROJECT,
    "customer_goals": [
        "Establish RCTC's MetroLink station as a regional holiday destination",
        "Drive non-transit foot traffic to the downtown station and adjoining plaza",
        "Position Riverside County as a leader in civic seasonal programming",
    ],
    "success_criteria": [
        "Measurable increase in evening visitors during the program window",
        "Local press and social media coverage of the activation",
        "Zero MetroLink operational disruptions during install/strike",
    ],
    "constraints": [
        "All decor must clear MetroLink overhead catenary safety envelope",
        "Install and removal must occur outside revenue service hours",
        "Materials must withstand winter Santa Ana wind events",
    ],
    "tier_recommended": "Enhanced",
    "tier_rationale": "Balances civic visual impact with disciplined investment.",
}


# ===== Slide 4 — Creative Vision =====
creative_vision_ctx = {
    **PROJECT,
    "hero_image": _path(BASE_SCOPE, "Evening Lighting - Tree Lights Street.png"),
    "creative_direction": (
        "Holiday Express transforms the MetroLink station into the heart of "
        "Riverside's holiday season — a warm, civic-scaled invitation visible "
        "from blocks away. Wreaths and garlands frame each entrance like a "
        "ceremonial gateway; evening lighting turns the platform itself into "
        "the destination after sundown."
    ),
    "phases": [
        {"label": "Welcome", "body": "Wreaths and garlands at every station entrance — the holiday begins at the curb."},
        {"label": "Journey", "body": "Pole banners and evening lighting carry the design language down the platform."},
        {"label": "Arrival", "body": "Walk-through ornament and lit displays at the plaza — a destination, not a transfer."},
    ],
}


# ===== Slide 5a — Showcase Hero (1–3 items) =====
showcase_hero_ctx = {
    **PROJECT,
    "section_title": "Station Entrances",
    "section_subtitle": "First impressions at the curb",
    "hero_image": _path(BASE_SCOPE, "Wreaths - Station Entrance 01.png"),
    "hero_caption": "Custom-finished wreath, primary station entrance",
    "items": [
        {"name": "Custom Wreaths", "qty": 4, "note": "Each station entrance"},
        {"name": "Garland Swags", "qty": 6, "note": "Spans entrance overhang"},
        {"name": "Pole Wraps", "qty": 8, "note": "Approach from plaza"},
    ],
}


# ===== Slide 5b — Showcase 2-up (3–6 items) =====
showcase_2up_ctx = {
    **PROJECT,
    "section_title": "Platform & Plaza",
    "section_subtitle": "Where transit meets celebration",
    "tiles": [
        {
            "image": _path(BASE_SCOPE, "Garlands - Decorated Swag - Plaza Fence.png"),
            "name": "Decorated Plaza Fence Garland",
            "note": "Continuous run, plaza-side fence",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Platform Railing.png"),
            "name": "Platform Railing Lighting",
            "note": "Warm-white LED, dusk-to-2am program",
        },
    ],
}


# ===== Slide 5c — Showcase 3-up (6–10 items) =====
showcase_3up_ctx = {
    **PROJECT,
    "section_title": "Pole Decor",
    "section_subtitle": "Length-of-corridor design language",
    "tiles": [
        {
            "image": _path(BASE_SCOPE, "Pole Banner - Happy Holidays.png"),
            "name": "Happy Holidays Pole Banner",
            "note": "Both faces, weather-treated",
        },
        {
            "image": _path(BASE_SCOPE, "Pole Banner Artwork - Holiday Express 01.jpg"),
            "name": "Holiday Express Banner — A",
            "note": "Custom artwork; train-themed",
        },
        {
            "image": _path(BASE_SCOPE, "Pole Banner Artwork - Holiday Express 02.jpg"),
            "name": "Holiday Express Banner — B",
            "note": "Custom artwork; track-themed",
        },
    ],
}


# ===== Slide 5d — Showcase 4-up (overflow) =====
showcase_4up_ctx = {
    **PROJECT,
    "section_title": "Evening Program",
    "section_subtitle": "After-dark activations",
    "tiles": [
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Tree Lights Street.png"),
            "name": "Street Tree Lights",
            "note": "Warm white",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Station Awning 01.png"),
            "name": "Station Awning Lights",
            "note": "Architectural perimeter",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Platform Railing.png"),
            "name": "Platform Railing",
            "note": "Approach lighting",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Curb Edge.png"),
            "name": "Curb Edge Lighting",
            "note": "Vehicle-side warmth",
        },
    ],
}


# ===== Slide 5e — Showcase full-bleed (single hero) =====
showcase_fullbleed_ctx = {
    **PROJECT,
    "section_title": "The Walk-Through Moment",
    "hero_image": _path(ENHANCEMENTS, "Walk-Through Display - Lighted Gift Box.png"),
    "caption": (
        "A 12-foot lighted gift-box arch on the plaza — the photo "
        "moment that gets shared, that brings visitors back."
    ),
}


# ===== Slide N+1 — Scope of Work =====
scope_ctx = {
    **PROJECT,
    "inclusions": [
        "Custom-fabricated wreaths (4× station entrances)",
        "Decorated and undecorated garland swags (plaza + street fence)",
        "Pole banner program (8 poles, 2 artwork variants)",
        "Evening lighting program (platform, awning, street tree, curb edge)",
        "Walk-through ornament arch (plaza centerpiece)",
        "Install + strike per MetroLink operational windows",
        "On-site QC walkthrough with RCTC capital projects",
        "Storage between deinstall and 2027 program",
    ],
    "add_ons": [
        "Spiral LED tree at station forecourt",
        "Lighted bell display, plaza-side",
        "Lighted snowflakes on platform railing",
        "Lighted gift-box towers, plaza pair",
    ],
    "exclusions": [
        "MetroLink overhead catenary work (any modifications)",
        "Permanent electrical infrastructure",
        "After-hours security",
    ],
}


# ===== Slide N+2 — Sample of Our Work =====
sample_of_work_ctx = {
    **PROJECT,
    "tiles": [
        # 6 tiles. Riverside doesn't have a populated past_work_library yet
        # (Plan 9), so these reference plausible fixture entries by name and
        # use available rendering files as stand-in imagery.
        {"image": _path(ENHANCEMENTS, "Lighted Bell Display - Scene.png"),
         "name": "The Music Center", "location": "Los Angeles", "year": 2024},
        {"image": _path(ENHANCEMENTS, "Spiral Tree - LED Red Green.png"),
         "name": "Pier 39", "location": "San Francisco", "year": 2023},
        {"image": _path(ENHANCEMENTS, "Walk-Through Display - Lighted Gift Box.png"),
         "name": "Oregon Zoo", "location": "Portland", "year": 2024},
        {"image": _path(BASE_SCOPE, "Wreath - Brick Column Night.jpg"),
         "name": "JFK Terminal 1", "location": "New York", "year": 2023},
        {"image": _path(BASE_SCOPE, "Large Tree - Traditional Ornaments.png"),
         "name": "Sphere — Holiday Tree", "location": "Las Vegas", "year": 2024},
        {"image": _path(BASE_SCOPE, "Walk-Through Ornament - Warm White.png"),
         "name": "LED Angels Program", "location": "Long Beach", "year": 2024},
    ],
}


# ===== Slide N+3 — Case Study =====
case_study_ctx = {
    **PROJECT,
    "case_study_name": "Oregon Zoo — ZooLights",
    "case_study_image": _path(ENHANCEMENTS, "Lighted Gift Box Tower 01.png"),
    "challenge": (
        "Drive evening attendance during the slowest revenue months while "
        "maintaining the zoo's family-friendly identity and operating "
        "within a tight nonprofit budget."
    ),
    "approach": (
        "A modular lighting program designed to grow over three seasons. "
        "Year-one investment in a hero walkway and signature animal lights; "
        "years two and three add adjacent zones using compatible hardware."
    ),
    "outcome": (
        "47% increase in evening attendance during the program window. "
        "Year-three program ran with no new capital outlay. Press coverage "
        "in The Oregonian, KGW, and Travel + Leisure."
    ),
}
