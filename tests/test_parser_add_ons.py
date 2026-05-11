"""Tests for _fill_add_ons in parser/__init__.py.

Regression coverage for the twinkle truncation bug (2026-05-06): a Brief
add-on line like 'Description: $17,324 (qualifier)' lost the parenthetical
in the rendered à-la-carte page because the legacy rsplit-on-colon parser
captured everything after the colon into the nowrap'd price column.
"""
from __future__ import annotations

from types import SimpleNamespace

from proposal_build.parser import _fill_add_ons


def _brief(lines: list[str]):
    """Minimal stub matching what _fill_add_ons consumes from BriefData."""
    return SimpleNamespace(sections={"Add-Ons": lines})


def test_simple_line_parses_clean():
    out = _fill_add_ons(_brief(["Lobby tree: $7,345"]), {})
    assert out == (("Lobby tree", "$7,345"),)


def test_trailing_parenthetical_stays_in_description():
    """The bug we hit: '(net of snowflake removal)' was landing in the
    price column. With the regex parser it folds back into description."""
    out = _fill_add_ons(_brief([
        "Porte-cochère twinkle canopy upgrade: $17,324 (net of snowflake removal)",
    ]), {})
    assert len(out) == 1
    desc, price = out[0]
    assert price == "$17,324"
    assert "net of snowflake removal" in desc
    assert "(net of snowflake removal)" not in price


def test_qualifier_before_price_left_alone():
    """'Description (qualifier): $price' — qualifier sits before the colon
    so the description naturally keeps it. No special handling needed."""
    out = _fill_add_ons(_brief([
        "Sheraton-branded gift-tag accent (Enhanced add-on): $535",
    ]), {})
    assert out == (("Sheraton-branded gift-tag accent (Enhanced add-on)", "$535"),)


def test_multiple_lines():
    out = _fill_add_ons(_brief([
        "First add-on: $1,000",
        "Second add-on with comma, in description: $2,500 (Enhanced upgrade)",
        "Third add-on: $250",
    ]), {})
    assert len(out) == 3
    assert out[0] == ("First add-on", "$1,000")
    assert out[1][1] == "$2,500"
    assert "Enhanced upgrade" in out[1][0]
    assert out[2] == ("Third add-on", "$250")


def test_empty_section_returns_empty_tuple():
    assert _fill_add_ons(_brief([]), {}) == ()
    assert _fill_add_ons(SimpleNamespace(sections={}), {}) == ()


def test_dollar_with_decimal_cents_parsed():
    out = _fill_add_ons(_brief(["Tax-exempt accessory: $499.99"]), {})
    assert out == (("Tax-exempt accessory", "$499.99"),)


def test_legacy_no_dollar_falls_back_to_colon_split():
    """A line without a $ pattern should still parse — gracefully fall back
    to the original colon-split behavior rather than dropping the line."""
    out = _fill_add_ons(_brief(["Custom quote item: TBD per consultation"]), {})
    assert out == (("Custom quote item", "TBD per consultation"),)
