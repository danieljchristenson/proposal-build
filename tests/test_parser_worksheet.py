"""Tests for parser/worksheet.py — Scope Worksheet.xlsx parsing."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.models import Tier
from proposal_build.parser.worksheet import (
    parse_worksheet,
    WorksheetParseError,
)

FIXTURES = Path(__file__).parent / "fixtures" / "worksheets"


def test_minimal_valid_parses():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    assert len(result.line_items) == 3
    base = [li for li in result.line_items if not li.is_enhancement]
    enh = [li for li in result.line_items if li.is_enhancement]
    assert len(base) == 2
    assert len(enh) == 1
    assert base[0].item == "Wreath"
    assert base[0].qty == 4
    assert base[0].line_total == 400
    assert base[0].customer_facing == "Lighted wreaths at the entrance."
    assert base[0].zone == "Zone One"
    assert base[0].tiers == (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)
    assert enh[0].line_num == "E1"


def test_zone_wildcard_preserved():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    garland = next(li for li in result.line_items if li.item == "Garland")
    assert garland.zone == "*"


def test_substitution_via_tier_membership():
    result = parse_worksheet(FIXTURES / "with_substitution.xlsx")
    traditional = next(li for li in result.line_items if li.item == "Traditional Tree")
    spiral = next(li for li in result.line_items if li.item == "Spiral LED Tree")
    assert Tier.ESSENTIAL in traditional.tiers
    assert Tier.SIGNATURE not in traditional.tiers
    assert Tier.SIGNATURE in spiral.tiers
    assert Tier.ESSENTIAL not in spiral.tiers


def test_per_tier_sums():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    sums = result.tier_sums_per_line()
    # Base = 400 + 2500 = 2900; Enhancement E1 = 12*295 = 3540
    assert sums[Tier.ESSENTIAL] == 2900
    assert sums[Tier.ENHANCED] == 2900 + 3540
    assert sums[Tier.SIGNATURE] == 2900 + 3540


def test_substitution_tier_sums():
    result = parse_worksheet(FIXTURES / "with_substitution.xlsx")
    sums = result.tier_sums_per_line()
    assert sums[Tier.ESSENTIAL] == 18000
    assert sums[Tier.ENHANCED] == 18000
    assert sums[Tier.SIGNATURE] == 22000


def test_missing_tiers_column_raises():
    with pytest.raises(WorksheetParseError) as exc:
        parse_worksheet(FIXTURES / "missing_tiers_column.xlsx")
    assert "tiers" in str(exc.value).lower()


def test_scenarios_block_parsed():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    assert result.scenarios is not None
    # We don't validate contents here — that's W4 in validate.py
    assert len(result.scenarios) == 3
