"""FIGat7th DTLA fixture — first-pass creative-menu proposal.

This fixture exercises the new no-tier creative-menu pattern:
- Three sections (Overhead, Tree, Plaza Photo-Ops), each with section-divider entry.
- ROM pricing: rental (annual all-in) vs purchase (one-time + service) side-by-side.
- Customer-choice alternates: 4 plaza arches presented as a 2×2 menu, customer picks one.
- Pre-built creative assets (cover slide and palette/mood board) are full-bleed PNG
  inserts rather than templated layouts.

The fixture format and ROM pricing schema introduced here will be formalized
into Plan 9 of the skill build after FIGat7th ships.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
RENDERINGS_DIR = PROJECT_DIR / "02 - Renderings" / "Base Scope"


def _img(name: str) -> str:
    return (RENDERINGS_DIR / name).as_uri()


# Renderings (locked 2026-05-08)
COVER_PREBUILT = _img("01_cover-slide-cityscape.png")
PALETTE_PREBUILT = _img("02_palette-board-mood.png")
TREE_HERO = _img("10_tree-A-studio-blackbg.png")
CANOPY_HERO = _img("20_overhead-mixed-canopy.png")
ARCH_30 = _img("30_arch-letters-happy-holidays.png")
ARCH_31 = _img("31_arch-bauble.png")
ARCH_32 = _img("32_arch-wreath.png")
ARCH_33 = _img("33_arch-bauble-vertical.png")
PHOTO_40 = _img("40_photo-op-bow-frame.png")
PHOTO_41 = _img("41_photo-op-ornament-globe.png")
PHOTO_42 = _img("42_feature-ornament-bench.png")
PHOTO_43 = _img("43_gift-box-trio.png")


PROJECT = {
    "client_company": "FIGat7th",
    "client_short": "FIGat7th DTLA",
    "project_name": "FIGat7th DTLA — 2026 Holiday Program",
    "project_short": "FIGat7th DTLA",
    "project_year": 2026,
    "project_subtitle": "First-Pass Creative Menu",
    "presenter_name": "Daniel Christenson",
    "presenter_title": "Director of Sales",
    "presenter_org": "St. Nick's Christmas Lighting & Décor",
    "proposal_date": "May 9, 2026",
    "page_total": 12,
}


# ===== Slide 1 — Cover (pre-built) =====
slide_01_cover = ("image_fullbleed", {
    **PROJECT,
    "page_num": 1,
    "page_title": "Cover",
    "hero_image": COVER_PREBUILT,
    "alt_text": "FIGat7th DTLA — 2026 Holiday Décor Proposal",
})


# ===== Slide 2 — Palette / Mood (pre-built) =====
slide_02_palette = ("image_fullbleed", {
    **PROJECT,
    "page_num": 2,
    "page_title": "Selected Ornament Palette",
    "hero_image": PALETTE_PREBUILT,
    "alt_text": "FIGat7th palette: Champagne Gold, Soft Antique Gold, Sapphire Teal, Jewel Teal, Ivory White Light",
})


# ===== Slide 3 — Creative Vision =====
slide_03_creative = ("creative_vision", {
    **PROJECT,
    "page_num": 3,
    "page_title": "Creative Vision",
    "standfirst": "The design direction for FIGat7th's 2026 holiday program.",
    "design_phrase": "Modern Magic.",
    "design_direction_body": (
        "FIGat7th becomes Downtown LA's most photographed holiday destination, "
        "where a modern landmark turns into a glowing photo op after dark. "
        "The energy is upscale, festive, and dressed up for the camera, built "
        "for FIGat7th's nightlife audience rather than the traditional "
        "family-in-PJs crowd. Sapphire teal, jewel teal, and champagne gold "
        "carry the property's signature color story through every moment."
    ),
    "phases": [
        {"label": "ARRIVE",  "body": "An ornament canopy turns the FIGat7th courtyard ceiling into a winter night sky."},
        {"label": "GATHER",  "body": "The centerpiece tree anchors the plaza as the moment every shopper poses with."},
        {"label": "EXPLORE", "body": "A menu of arches, frames, and selfie moments scattered through the plaza."},
    ],
    "hero_image": TREE_HERO,
    "hero_fit": "contain",
})


# ===== Slide 4 — Canopy (leads Section 1) =====
slide_04_canopy = ("zone_solo", {
    **PROJECT,
    "page_num": 4,
    "section_label": "Section One",
    "section_name": "Main Entrance Overhead",
    "zone_num": "01",
    "zone_name": "Mixed Ornament Canopy",
    "zone_subtitle": "16 oversized 6-foot overhead ornaments forming a layered courtyard canopy.",
    "included_elements": [
        "Tinsel-wrapped sapphire and jewel-teal 3-foot spheres",
        "See-through 3-foot baubles filled with the FIGat7th ornament package",
        "Cool-white LED starburst sparklers throughout",
        "Warm-white and cool-white LED lighting on metal frames",
        "Suspended from existing ceiling structure (lift equipment included)",
    ],
    "hero_image": CANOPY_HERO,
})


# ===== Slide 5 — Tree (leads Section 2) =====
slide_05_tree = ("zone_solo", {
    **PROJECT,
    "page_num": 5,
    "section_label": "Section Two",
    "section_name": "The FIGat7th Tree",
    "zone_num": "02",
    "zone_name": "FIGat7th Holiday Tree",
    "zone_subtitle": "56-foot commercial holiday tree (50-foot tree with a 6-foot LED topper) fully decorated in the FIGat7th ornament package.",
    "included_elements": [
        "50-foot commercial PVC tree on engineered base",
        "6-foot LED topper for a total height of 56 feet",
        "Champagne gold, sapphire teal, jewel teal, and ivory white ornament package",
        "24-inch cool-white and gold LED sparkler accents",
        "Around-the-tree enhancement package: 12-foot custom 'FIGat7th Happy Holidays' photo-op arch",
        "Pair of lit 6-foot and 7.5-foot reindeer flanking the base",
        "3-foot, 4-foot, and 6-foot illuminated gift boxes anchoring the plaza base",
    ],
    "hero_image": TREE_HERO,
    "hero_fit": "contain",
})


# ===== Slide 6 — Plaza Arches A (leads Section 3 — Plaza Photo-Ops) =====
# Daniel's preferred order: D, C, A, B (was rendering 33, 32, 30, 31).
# Position labels stay sequential (A, B, C, D) for customer reading flow.
slide_06_arches_a = ("zone_2up_gallery", {
    **PROJECT,
    "page_num": 6,
    "section_label": "Section Three",
    "section_name": "Plaza Photo-Ops",
    "page_title": "Plaza Arches",
    "standfirst": "Four walk-through arch directions for the H&M plaza entrance. Each can stand alone as the moment. Options A and B follow; Options C and D on the next page.",
    "alternate_banner": "Customer Choice — Pick One",
    "cells": [
        {
            "eyebrow": "OPTION A",
            "name": "Custom Ornament Arch",
            "hero_image": ARCH_33,
        },
        {
            "eyebrow": "OPTION B",
            "name": "Wreath Arch — Cursive Neon",
            "hero_image": ARCH_32,
        },
    ],
})


# ===== Slide 7 — Plaza Arches B (Options C + D) =====
slide_07_arches_b = ("zone_2up_gallery", {
    **PROJECT,
    "page_num": 7,
    "page_title": "Plaza Arches (continued)",
    "standfirst": "Options C and D — the final two arch directions for customer choice.",
    "alternate_banner": "Customer Choice — Pick One",
    "cells": [
        {
            "eyebrow": "OPTION C",
            "name": "Letter Arch — \"Happy Holidays\"",
            "hero_image": ARCH_30,
        },
        {
            "eyebrow": "OPTION D",
            "name": "Bauble Arch — Gold",
            "hero_image": ARCH_31,
        },
    ],
})


# ===== Slide 8 — Plaza Moments A (Moments 01 + 02) =====
slide_08_moments_a = ("zone_2up_gallery", {
    **PROJECT,
    "page_num": 8,
    "page_title": "Plaza Moments",
    "standfirst": "Four standalone photo-ops scattered through the plaza. Moments 01 and 02 below; Moments 03 and 04 on the next page.",
    "alternate_banner": "All Four Included",
    "cells": [
        {
            "eyebrow": "MOMENT 01",
            "name": "Picture-Frame Selfie",
            "hero_image": PHOTO_40,
        },
        {
            "eyebrow": "MOMENT 02",
            "name": "Walk-In Ornament Globe",
            "hero_image": PHOTO_41,
        },
    ],
})


# ===== Slide 9 — Plaza Moments B (Moments 03 + 04) =====
slide_09_moments_b = ("zone_2up_gallery", {
    **PROJECT,
    "page_num": 9,
    "page_title": "Plaza Moments (continued)",
    "standfirst": "Moments 03 and 04 round out the standalone plaza photo-op program.",
    "alternate_banner": "All Four Included",
    "cells": [
        {
            "eyebrow": "MOMENT 03",
            "name": "Custom Ornament Bench",
            "hero_image": PHOTO_42,
        },
        {
            "eyebrow": "MOMENT 04",
            "name": "Gift Box Trio",
            "hero_image": PHOTO_43,
        },
    ],
})


# ===== Slide 11 — ROM Investment =====
def _fmt_money(n: int) -> str:
    return f"${n:,}"


def _fmt_range(low: int, high: int) -> str:
    if low == high:
        return _fmt_money(low)
    return f"{_fmt_money(low)} – {_fmt_money(high)}"


# Pricing data — sourced from FIGat7th DTLA - Scope Worksheet.xlsx (locked 2026-05-08)
PRICING = {
    # code: (rental_low, rental_high, po_low, po_high, ps_low, ps_high)
    "20":     (22400, 22400, 19200, 19200, 18600, 18600),
    "10":     (150000, 150000, 200000, 200000, 80000, 80000),
    "10-enh": (15000, 15000, 12000, 12000, 5900, 5900),
    "30":     (9500, 9500, 9000, 9000, 2000, 2000),
    "31":     (9000, 9000, 8900, 8900, 2000, 2000),
    "32":     (8500, 8500, 9500, 9500, 2200, 2200),
    "33":     (14000, 14000, 16500, 16500, 2900, 2900),
    "40":     (9500, 9500, 12000, 12000, 2500, 2500),
    "41":     (10250, 10250, 12500, 12500, 2500, 2500),
    "42":     (7500, 7500, 9400, 9400, 1500, 1500),
    "43":     (4000, 6000, 6000, 8000, 4000, 7000),
}


def _row(code: str, name: str, desc: str, *, is_alternate: bool = False) -> dict:
    rl, rh, pol, poh, psl, psh = PRICING[code]
    return {
        "name": name,
        "description": desc,
        "is_alternate": is_alternate,
        "rental_price": _fmt_range(rl, rh),
        "purchase_ot_price": _fmt_range(pol, poh),
        "purchase_svc_price": _fmt_range(psl, psh),
    }


# Totals: alternates resolve via cheapest-pick (low) vs most-expensive-pick (high).
# Section 3a is mutually exclusive → take min/max across the four arches.
_arch_codes = ("30", "31", "32", "33")
_non_alt_codes = ("20", "10", "10-enh", "40", "41", "42", "43")

_total_rental_low = sum(PRICING[c][0] for c in _non_alt_codes) + min(PRICING[c][0] for c in _arch_codes)
_total_rental_high = sum(PRICING[c][1] for c in _non_alt_codes) + max(PRICING[c][1] for c in _arch_codes)
_total_po_low = sum(PRICING[c][2] for c in _non_alt_codes) + min(PRICING[c][2] for c in _arch_codes)
_total_po_high = sum(PRICING[c][3] for c in _non_alt_codes) + max(PRICING[c][3] for c in _arch_codes)
_total_ps_low = sum(PRICING[c][4] for c in _non_alt_codes) + min(PRICING[c][4] for c in _arch_codes)
_total_ps_high = sum(PRICING[c][5] for c in _non_alt_codes) + max(PRICING[c][5] for c in _arch_codes)


# Investment table split across two pages (11 line items + section headers
# + totals don't fit on one page even with maximally tight typography).
slide_10_investment_a = ("rom_investment", {
    **PROJECT,
    "page_num": 10,
    "page_title": "Investment",
    "standfirst": "Rough order of magnitude pricing — Sections 1, 2, and 3a (continued on next page).",
    "sections": [
        {
            "label": "Section 1 — Main Entrance Overhead",
            "rows": [
                _row("20", "Mixed Ornament Canopy", ""),
            ],
        },
        {
            "label": "Section 2 — Holiday Tree + Photo Op",
            "rows": [
                _row("10", "FIGat7th Holiday Tree", ""),
                _row("10-enh", "Tree Enhancement Package", ""),
            ],
        },
        {
            "label": "Section 3a — Plaza Arches (customer picks one)",
            "rows": [
                _row("33", "Custom Ornament Arch", "", is_alternate=True),
                _row("32", "Wreath Arch — Cursive Neon", "", is_alternate=True),
                _row("30", "Letter Arch — \"Happy Holidays\"", "", is_alternate=True),
                _row("31", "Bauble Arch — Gold", "", is_alternate=True),
            ],
        },
    ],
    "total_rental": "",
    "total_purchase_ot": "",
    "total_purchase_svc": "",
    "show_totals": False,
    "footnote": "",
})

slide_11_investment_b = ("rom_investment", {
    **PROJECT,
    "page_num": 11,
    "page_title": "Investment (continued)",
    "standfirst": "Section 3b plus program total. Customer can mix and match rental and purchase per item.",
    "sections": [
        {
            "label": "Section 3b — Plaza Photo-Ops (all included)",
            "rows": [
                _row("40", "Picture-Frame Selfie", ""),
                _row("41", "Walk-In Ornament Globe", ""),
                _row("42", "Custom Ornament Bench", ""),
                _row("43", "Gift Box Trio", ""),
            ],
        },
    ],
    "total_rental":      _fmt_range(_total_rental_low, _total_rental_high),
    "total_purchase_ot": _fmt_range(_total_po_low, _total_po_high),
    "total_purchase_svc": _fmt_range(_total_ps_low, _total_ps_high),
    "show_totals": True,
    "footnote": (
        "<strong>Rental</strong> is an annual all-inclusive fee covering item, install, removal, and storage. "
        "<strong>Purchase</strong> is a one-time price plus a separate annual service fee for install, removal, and storage. "
        "Plaza arches are mutually exclusive — Program ROM Total is bookended by the cheapest-pick (low) and most-expensive-pick (high) configurations. "
        "All figures are rough order of magnitude for first-pass scoping; final numbers will follow site walk and scope refinement."
    ),
})


# ===== Slide 12 — Sign-off / Next Steps =====
slide_12_signoff = ("sign_off", {
    **PROJECT,
    "page_num": 12,
    "page_title": "Let's Make It Happen",
    "standfirst": "Next steps to lock the FIGat7th 2026 program.",
    "what_youre_approving": (
        "This first-pass creative menu and rough-order-of-magnitude pricing as the basis for site walk and final scope refinement. "
        "Approval here authorizes St. Nick's to schedule the on-site walk-through with Athena Property Management and prepare a finalized scope and committed pricing for execution."
    ),
    "client_party_label": "FIGat7th — Athena Property Management",
    "client_contact_name": "Alexandra Castro",
    "client_contact_title": "Property Manager, Athena Property Management",
    "client_contact_email": "acastro@athenapm.com",
    "client_contact_phone": "",
    "stnicks_party_label": "St. Nick's Christmas Lighting & Décor",
    "digital_signing_note": "This proposal may be approved digitally — a countersigned PDF is sufficient to proceed.",
})


# ===== Master deck list =====
SLIDES = [
    slide_01_cover,
    slide_02_palette,
    slide_03_creative,
    slide_04_canopy,        # Section 1 header inlined
    slide_05_tree,          # Section 2 header inlined
    slide_06_arches_a,      # Section 3 header inlined
    slide_07_arches_b,
    slide_08_moments_a,
    slide_09_moments_b,
    slide_10_investment_a,
    slide_11_investment_b,
    slide_12_signoff,
]
