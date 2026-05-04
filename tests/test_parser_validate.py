"""Tests for parser/validate.py — sniff test (W5/W6/W7) + zone coverage warnings."""
from __future__ import annotations

import pytest

from proposal_build.models import LineItem, Tier
from proposal_build.parser.validate import (
    check_cfd_sniff,
    check_zone_coverage,
)


def _li(line_num="1", item="X", description="internal", qty=1, unit="ea",
        price=100, total=100, rendering="r.png", customer_facing="OK clean text",
        zone="Zone One", tiers=(Tier.ESSENTIAL,)):
    return LineItem(
        line_num=line_num, item=item, description=description, qty=qty, unit=unit,
        price_per_unit=price, line_total=total, rendering_ref=rendering,
        customer_facing=customer_facing, zone=zone, tiers=tiers,
    )


def test_cfd_identical_to_internal_warns_w5():
    li = _li(description="The internal description.", customer_facing="The internal description.")
    warnings = check_cfd_sniff([li])
    codes = [w[0] for w in warnings]
    assert "W5" in codes


def test_cfd_jargon_dimensions_warns_w6():
    li = _li(customer_facing='14" girth garland on the perimeter.')
    warnings = check_cfd_sniff([li])
    codes = [w[0] for w in warnings]
    assert "W6" in codes


def test_cfd_jargon_units_mid_sentence_warns_w6():
    li = _li(customer_facing="Total of 1024 LF along the perimeter.")
    warnings = check_cfd_sniff([li])
    assert "W6" in [w[0] for w in warnings]


def test_cfd_too_short_warns_w7():
    li = _li(customer_facing="Three short words.")  # 3 words
    warnings = check_cfd_sniff([li])
    assert "W7" in [w[0] for w in warnings]


def test_cfd_clean_text_no_warnings():
    li = _li(customer_facing="Lighted wreaths frame every station entrance with warm-white evergreen.")
    warnings = check_cfd_sniff([li])
    assert warnings == []


def test_zone_no_priced_items_warns_w2():
    items = [_li(zone="Zone Two")]   # nothing in Zone One
    zones = ["Zone One", "Zone Two"]
    warnings = check_zone_coverage(items, zones, brief_bullets={"Zone One": ["bullet"], "Zone Two": []})
    assert "W2" in [w[0] for w in warnings]


def test_zone_bullet_count_divergence_warns_w3():
    items = [_li(zone="Zone One"), _li(line_num="2", zone="Zone One"),
             _li(line_num="3", zone="Zone One"), _li(line_num="4", zone="Zone One"),
             _li(line_num="5", zone="Zone One"), _li(line_num="6", zone="Zone One"),
             _li(line_num="7", zone="Zone One"), _li(line_num="8", zone="Zone One")]
    zones = ["Zone One"]
    warnings = check_zone_coverage(items, zones, brief_bullets={"Zone One": ["b1", "b2", "b3"]})
    # 8 priced items vs 3 bullets — divergence > 2
    assert "W3" in [w[0] for w in warnings]


def test_zone_with_wildcard_items_no_warning():
    items = [_li(zone="*")]
    zones = ["Zone One"]
    warnings = check_zone_coverage(items, zones, brief_bullets={"Zone One": ["b1"]})
    # Cross-program items count as applicable to all zones; W2 doesn't fire
    assert "W2" not in [w[0] for w in warnings]
