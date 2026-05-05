"""Parametrized layout tests — one entry per layout-render in skill_assets/layouts/.

Each LAYOUT_CASES tuple is (out_name, layout_name, fixture_module, ctx_attr,
expected_text):
- out_name: the PDF filename stem written to tests/_output/
- layout_name: the .html template under skill_assets/layouts/
- fixture_module: "pier_39" or "riverside" — which fixture module supplies ctx
- ctx_attr: name of the ctx dict on that module
- expected_text: substrings that must appear in the rendered PDF text

The same layout may be rendered multiple times with different ctxs (e.g.
zone_solo with zone_01 and zone_02 fixtures). out_name disambiguates.

Per Plan 2-prime: every PDF embeds Roboto + Poppins; no other families.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import fitz  # pymupdf
import pytest

EXPECTED_WIDTH_PT = 13.333 * 72   # 959.976 pt
EXPECTED_HEIGHT_PT = 7.5 * 72     # 540.000 pt
DIMENSION_TOLERANCE_PT = 1.0


def _font_names(doc: fitz.Document) -> list[str]:
    names: list[str] = []
    for page in doc:
        for entry in page.get_fonts():
            names.append(entry[3])
    return names


def _assert_font_family_present(doc: fitz.Document, family: str) -> None:
    names = _font_names(doc)
    assert any(family in n for n in names), (
        f"No embedded font with '{family}' in its name. Got: {names}. "
        f"WeasyPrint may have fallen back to a system font — check brand.css "
        f"@font-face urls and font file presence."
    )


def _assert_dimensions(doc: fitz.Document) -> None:
    rect = doc[0].rect
    assert abs(rect.width - EXPECTED_WIDTH_PT) <= DIMENSION_TOLERANCE_PT, (
        f"PDF width {rect.width:.2f}pt — expected {EXPECTED_WIDTH_PT:.2f}pt"
    )
    assert abs(rect.height - EXPECTED_HEIGHT_PT) <= DIMENSION_TOLERANCE_PT, (
        f"PDF height {rect.height:.2f}pt — expected {EXPECTED_HEIGHT_PT:.2f}pt"
    )


def _assert_text_present(doc: fitz.Document, expected: list[str]) -> None:
    raw = " ".join(page.get_text() for page in doc)
    text = " ".join(raw.split()).casefold()
    for fragment in expected:
        assert fragment.casefold() in text, (
            f"Expected fragment {fragment!r} not found in extracted PDF text."
        )


# (out_name, layout_name, fixture_module, ctx_attr, expected_text)
# Each Plan 2-prime layout task appends one or more entries here.
LAYOUT_CASES: list[tuple[str, str, str, str, list[str]]] = [
    ("cover_pier39",    "cover", "pier_39",   "cover_ctx", [
        "Pier 39", "San Francisco", "holiday season", "St. Nick's",
    ]),
    ("cover_riverside", "cover", "riverside", "cover_ctx", [
        "Riverside MetroLink", "Six-Station", "holiday season", "St. Nick's",
    ]),
    ("exec_summary_pier39",    "exec_summary", "pier_39",   "exec_summary_ctx",
        ["Executive Summary", "destination-scale", "Turnkey Delivery", "FABRICATION LOCK", "Aug 22, 2026"]),
    ("exec_summary_riverside", "exec_summary", "riverside", "exec_summary_ctx",
        ["Executive Summary", "Six-Station", "Civic Pride", "FABRICATION LOCK", "Aug 22, 2026"]),
    ("understanding_pier39",    "understanding", "pier_39",   "understanding_ctx",
        ["Our Understanding", "Pier 39 is San Francisco's", "VENUE & CONTEXT", "GOALS FOR 2026", "KEY CONSTRAINTS"]),
    ("understanding_riverside", "understanding", "riverside", "understanding_ctx",
        ["Our Understanding", "MetroLink line connects", "VENUE & CONTEXT", "GOALS FOR 2026", "KEY CONSTRAINTS"]),
    ("creative_vision_pier39",    "creative_vision", "pier_39",   "creative_vision_ctx",
        ["Creative Vision", "Bayside Twilight", "ARRIVE", "EXPLORE", "CELEBRATE"]),
    ("creative_vision_riverside", "creative_vision", "riverside", "creative_vision_ctx",
        ["Creative Vision", "Holiday Express", "WELCOME", "JOURNEY", "ARRIVAL"]),
    ("zone_solo_pier39_z01",     "zone_solo", "pier_39",   "zone_01_ctx",
        ["ZONE 01", "Embarcadero Arrival", "28' illuminated entry arch", "Dusk-to-dawn programming"]),
    ("zone_solo_pier39_z02",     "zone_solo", "pier_39",   "zone_02_ctx",
        ["ZONE 02", "Pier Promenade", "Suspended starlight canopy", "Hot cocoa concierge"]),
    ("zone_solo_riverside_flag", "zone_solo", "riverside", "zone_flagship_ctx",
        ["ZONE 01", "Downtown Riverside", "Custom-fabricated wreaths", "Evening lighting program"]),
    ("zone_solo_fullbleed_pier39_z03", "zone_solo_fullbleed", "pier_39", "zone_03_ctx",
        ["ZONE 03", "Bay Terrace", "40' walkthrough signature tree", "synchronized music"]),
    ("zone_2up_riverside", "zone_2up", "riverside", "zone_2up_a_ctx",
        ["Program Zones", "ZONE 02", "La Sierra", "ZONE 03", "Pedley"]),
    ("zone_3up_riverside", "zone_3up", "riverside", "zone_3up_ctx",
        ["Program Zones", "ZONE 04", "Hunter Park", "ZONE 05", "Moreno Valley", "ZONE 06", "Perris"]),
    ("zone_index_riverside", "zone_index", "riverside", "zone_index_ctx",
        ["The Program at a Glance", "Six stations", "Downtown Riverside", "La Sierra", "Pedley", "Hunter Park", "Moreno Valley", "Perris"]),
    ("scope_pier39",    "scope", "pier_39",   "scope_ctx",
        ["Scope of Work", "YOUR PROGRAM INCLUDES"]),
    ("scope_riverside", "scope", "riverside", "scope_ctx",
        ["Scope of Work", "YOUR PROGRAM INCLUDES", "Custom-fabricated wreaths"]),
    ("case_study_pier39",    "case_study", "pier_39",   "case_study_ctx",
        ["CASE STUDY", "Oregon Zoo", "ZooLights 2025", "31% YoY increase"]),
    ("case_study_riverside", "case_study", "riverside", "case_study_ctx",
        ["CASE STUDY", "Long Beach Transit", "14 transit stations", "Zero revenue-service disruptions"]),
    ("investment_pier39",    "investment", "pier_39",   "investment_ctx",
        ["Investment", "Three levels", "ESSENTIAL", "ENHANCED", "SIGNATURE", "$225,000", "$345,000", "$485,000", "RECOMMENDED", "MULTI-YEAR PARTNERSHIP", "9% OFF"]),
    ("investment_riverside", "investment", "riverside", "investment_ctx",
        ["Investment", "ESSENTIAL", "ENHANCED", "SIGNATURE", "$184,500", "$284,500", "$384,500", "RECOMMENDED", "MULTI-YEAR PARTNERSHIP"]),
    ("terms_pier39",    "terms", "pier_39",   "terms_ctx",
        ["Terms & Next Steps", "November 14, 2026", "August 22, 2026", "PAYMENT SCHEDULE", "INSURANCE & PERMITS", "AFTER APPROVAL"]),
    ("terms_riverside", "terms", "riverside", "terms_ctx",
        ["Terms & Next Steps", "October 30, 2026", "August 22, 2026", "PAYMENT SCHEDULE", "INSURANCE & PERMITS", "AFTER APPROVAL"]),
    ("sign_off_pier39",    "sign_off", "pier_39",   "sign_off_ctx",
        ["Let's Make It Happen", "WHAT YOU'RE APPROVING", "CLIENT AUTHORIZATION", "Canva e-signature"]),
    ("sign_off_riverside", "sign_off", "riverside", "sign_off_ctx",
        ["Let's Make It Happen", "WHAT YOU'RE APPROVING", "RCTC AUTHORIZATION", "Canva e-signature"]),
    ("about_pier39",    "about", "pier_39",   "about_ctx",
        ["About St. Nick's", "Founded 1998", "Daniel Christenson", "Director of Sales", "ST-NICKS.COM"]),
    ("about_riverside", "about", "riverside", "about_ctx",
        ["About St. Nick's", "Founded 1998", "Daniel Christenson", "Director of Sales", "ST-NICKS.COM"]),
]


@pytest.mark.parametrize("out_name,layout_name,fixture_module,ctx_attr,expected_text", LAYOUT_CASES)
def test_layout_renders(out_name, layout_name, fixture_module, ctx_attr, expected_text, render_layout):
    fixtures = importlib.import_module(f"fixtures.{fixture_module}")
    ctx = getattr(fixtures, ctx_attr)
    pdf_path: Path = render_layout(layout_name, ctx, out_name=out_name)

    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 5000, "PDF suspiciously small"

    with fitz.open(pdf_path) as doc:
        assert doc.page_count == 1, f"Expected 1 page, got {doc.page_count}"
        _assert_dimensions(doc)
        _assert_font_family_present(doc, "Roboto")
        _assert_font_family_present(doc, "Poppins")
        _assert_text_present(doc, expected_text)


def test_all_layouts_rendered():
    """After the suite runs, every PDF named in LAYOUT_CASES must exist on disk."""
    if not LAYOUT_CASES:
        pytest.skip("LAYOUT_CASES is empty.")

    output_dir = Path(__file__).resolve().parent / "_output"
    expected_pdfs = {f"{out}.pdf" for out, _, _, _, _ in LAYOUT_CASES}
    actual_pdfs = {p.name for p in output_dir.glob("*.pdf")}
    missing = expected_pdfs - actual_pdfs
    assert not missing, f"Missing rendered PDFs: {missing}"
