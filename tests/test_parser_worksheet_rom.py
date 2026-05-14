"""Tests for the ROM (Rough Order of Magnitude) worksheet parser
used by the creative-menu proposal mode."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser.worksheet_rom import (
    parse_rom_worksheet, ROMWorksheetParseError, ROMWorksheetData,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH_WORKSHEET = (
    REPO_ROOT
    / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
    / "03 - Scope & Pricing" / "FIGat7th DTLA - Scope Worksheet.xlsx"
)


def test_parse_figat7th_worksheet_yields_eleven_items():
    """The locked FIGat7th worksheet has 11 priced items."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    assert isinstance(data, ROMWorksheetData)
    assert len(data.line_items) == 11


def test_parse_figat7th_canopy_pricing():
    """Item 20 (canopy) prices should round-trip exactly from the worksheet."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    canopy = next(it for it in data.line_items if it.code == "20")
    assert canopy.name == "Mixed Ornament Canopy"
    assert canopy.rental_low == 21197 and canopy.rental_high == 21197
    assert canopy.purchase_ot_low == 19197 and canopy.purchase_ot_high == 19197
    assert canopy.purchase_svc_low == 17097 and canopy.purchase_svc_high == 18597


def test_parse_figat7th_arch_alternates_have_group():
    """Items 30, 31, 32, 33 share alternate_group='arch_alternates'."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    by_code = {it.code: it for it in data.line_items}
    for code in ("30", "31", "32", "33"):
        assert by_code[code].alternate_group, (
            f"Item {code} should carry an alternate_group flag in the worksheet"
        )
        assert by_code[code].alternate_group == by_code["30"].alternate_group


def test_parse_figat7th_gift_box_trio_is_range():
    """Item 43 (Gift Box Trio) is the only true range in the locked sheet."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    trio = next(it for it in data.line_items if it.code == "43")
    assert trio.rental_low == 3997 and trio.rental_high == 5997
    assert trio.is_point_estimate is False


def test_parse_missing_file_raises():
    with pytest.raises(ROMWorksheetParseError):
        parse_rom_worksheet(Path("/nonexistent/path.xlsx"))


def test_parse_worksheet_section_grouping():
    """line_items are emitted with the section column populated, matching
    the section divider rows in the worksheet."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    sections_seen = {it.section for it in data.line_items}
    # Canonical four buckets from the locked sheet:
    assert sections_seen == {"Overhead", "Tree", "Arches", "Standalones"}
