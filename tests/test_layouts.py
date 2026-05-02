"""Parametrized layout tests — one entry per layout in skill_assets/layouts/.

For each (layout_name, ctx, expected_text) tuple, the test:
- renders the layout to PDF via the render_layout fixture,
- asserts the PDF has 1 page at 13.333" × 7.5" (within 1pt),
- asserts both Roboto and Poppins are listed as embedded fonts
  (catches the silent system-font-fallback failure mode),
- asserts every string in expected_text appears in the extracted
  PDF text (catches blank-page and missing-content failures).

Each layout task in Plan 2 appends to LAYOUT_CASES below.
"""
from __future__ import annotations

from pathlib import Path

import fitz  # pymupdf
import pytest

# Page dimensions in PDF points (1pt = 1/72in).
EXPECTED_WIDTH_PT = 13.333 * 72   # 959.976 pt
EXPECTED_HEIGHT_PT = 7.5 * 72     # 540.000 pt
DIMENSION_TOLERANCE_PT = 1.0


def _font_names(doc: fitz.Document) -> list[str]:
    """Collect basefont names across all pages.

    pymupdf's get_fonts() returns tuples; index 3 is the basefont name,
    e.g. 'ABCDEF+Roboto-Bold' (subsetted) or 'Roboto-Bold' (full).
    """
    names: list[str] = []
    for page in doc:
        for entry in page.get_fonts():
            names.append(entry[3])
    return names


def _assert_font_family_present(doc: fitz.Document, family: str) -> None:
    names = _font_names(doc)
    assert any(family in n for n in names), (
        f"No embedded font with '{family}' in its name. "
        f"Got: {names}. WeasyPrint may have fallen back to a system font — "
        f"check brand.css @font-face urls and font file presence."
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
    # Normalise line-breaks introduced by PyMuPDF's text extraction (it inserts
    # \n wherever the renderer wrapped a line, so multi-word fragments that span
    # a wrap point would never match a verbatim substring check).  Collapsing to
    # a single space mirrors what a reader sees and keeps assertions readable.
    #
    # Case-folding: WeasyPrint applies CSS `text-transform: uppercase` by
    # rewriting the rendered glyphs to uppercase characters, so PyMuPDF's
    # text extraction returns e.g. "WELCOME" even when the source content
    # is "Welcome". The fragments are content assertions, not styling
    # assertions — case is the layout's job, presence is the test's job.
    raw = " ".join(page.get_text() for page in doc)
    text = " ".join(raw.split()).casefold()
    for fragment in expected:
        assert fragment.casefold() in text, (
            f"Expected fragment {fragment!r} not found in extracted PDF text."
        )


# (layout_name, fixture_attribute_name, list_of_text_fragments_that_must_appear)
# Each Plan 2 layout task appends one entry here.
LAYOUT_CASES: list[tuple[str, str, list[str]]] = [
    ("cover", "cover_ctx", [
        "Downtown Riverside MetroLink",
        "Riverside County Transportation Commission",
        "Holiday Express",
    ]),
    ("exec_summary", "exec_summary_ctx", [
        "Civic Pride",
        "Operational Discipline",
        "Repeatable Investment",
        "Enhanced",
        "$284,500",
    ]),
    ("understanding", "understanding_ctx", [
        "regional holiday destination",
        "MetroLink overhead catenary",
        "Enhanced",
    ]),
    ("creative_vision", "creative_vision_ctx", [
        "Holiday Express transforms",
        "Welcome",
        "Journey",
        "Arrival",
    ]),
    ("showcase_hero", "showcase_hero_ctx", [
        "Station Entrances",
        "Custom Wreaths",
        "Pole Wraps",
    ]),
    ("showcase_2up", "showcase_2up_ctx", [
        "Platform & Plaza",
        "Decorated Plaza Fence Garland",
        "Platform Railing Lighting",
    ]),
    ("showcase_3up", "showcase_3up_ctx", [
        "Pole Decor",
        "Happy Holidays Pole Banner",
        "Holiday Express Banner",
    ]),
    ("showcase_4up", "showcase_4up_ctx", [
        "Evening Program",
        "Street Tree Lights",
        "Curb Edge Lighting",
    ]),
    ("showcase_fullbleed", "showcase_fullbleed_ctx", [
        "The Walk-Through Moment",
        "12-foot lighted gift-box arch",
    ]),
    ("scope", "scope_ctx", [
        "Scope of Work",
        "Custom-fabricated wreaths",
        "MetroLink overhead catenary",
    ]),
    ("sample_of_work", "sample_of_work_ctx", [
        "Sample of Our Work",
        "Pier 39",
        "Oregon Zoo",
    ]),
]


@pytest.mark.parametrize("layout_name,ctx_attr,expected_text", LAYOUT_CASES)
def test_layout_renders(layout_name, ctx_attr, expected_text, render_layout):
    # pytest adds tests/ to sys.path because there's no tests/__init__.py
    # (Plan 1's pattern), so 'fixtures' is importable as a top-level package.
    from fixtures import riverside
    ctx = getattr(riverside, ctx_attr)
    pdf_path: Path = render_layout(layout_name, ctx)

    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 5000, "PDF suspiciously small"

    with fitz.open(pdf_path) as doc:
        assert doc.page_count == 1, f"Expected 1 page, got {doc.page_count}"
        _assert_dimensions(doc)
        _assert_font_family_present(doc, "Roboto")
        _assert_font_family_present(doc, "Poppins")
        _assert_text_present(doc, expected_text)


def test_all_eighteen_layouts_rendered():
    """After the suite runs, all 18 PDFs must exist for the eyeball pass.

    Skipped if LAYOUT_CASES is incomplete (Plan 2 in progress).
    """
    if len(LAYOUT_CASES) < 18:
        pytest.skip(f"Plan 2 in progress: {len(LAYOUT_CASES)}/18 layouts present.")

    output_dir = Path(__file__).resolve().parent / "_output"
    expected_pdfs = {f"{name}.pdf" for name, _, _ in LAYOUT_CASES}
    actual_pdfs = {p.name for p in output_dir.glob("*.pdf")}
    missing = expected_pdfs - actual_pdfs
    assert not missing, f"Missing rendered PDFs: {missing}"
