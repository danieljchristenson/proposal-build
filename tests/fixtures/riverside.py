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
