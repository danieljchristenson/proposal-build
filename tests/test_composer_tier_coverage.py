"""Tests for _zone_tier_coverage helper in composer/ctx_builders.py."""
from __future__ import annotations

from proposal_build.models import LineItem, Tier, Zone
from proposal_build.composer.ctx_builders import _zone_tier_coverage


def _li(zone: str, tiers: tuple) -> LineItem:
    return LineItem(
        line_num="1", item="x", description="d", qty=1, unit="ea",
        price_per_unit=1, line_total=1, rendering_ref="r.png",
        customer_facing="c", zone=zone, tiers=tiers,
    )


def _zone(name: str) -> Zone:
    return Zone(num="01", name=name, subtitle="", flags=(), hero_image="x.png", bullets=())


class _Model:
    def __init__(self, line_items, pricing_format="tiered"):
        self.line_items = tuple(line_items)
        # tier coverage is suppressed for single-tier projects; default to
        # tiered so these multi-tier coverage cases exercise the real path.
        self.pricing_format = pricing_format


def test_zone_in_both_essential_and_enhanced():
    model = _Model([
        _li("Lobby", (Tier.ESSENTIAL, Tier.ENHANCED)),
    ])
    assert _zone_tier_coverage(model, _zone("Lobby")) == "ESSENTIAL + ENHANCED"


def test_zone_with_only_enhanced_items():
    model = _Model([
        _li("Whale", (Tier.ENHANCED,)),
        _li("Whale", (Tier.ENHANCED,)),
    ])
    assert _zone_tier_coverage(model, _zone("Whale")) == "ENHANCED ONLY"


def test_zone_with_mixed_items_unions_tier_set():
    """Most real zones: some items in both tiers, some Enhanced-only."""
    model = _Model([
        _li("Roundabout", (Tier.ESSENTIAL, Tier.ENHANCED)),
        _li("Roundabout", (Tier.ENHANCED,)),
    ])
    assert _zone_tier_coverage(model, _zone("Roundabout")) == "ESSENTIAL + ENHANCED"


def test_all_three_tiers():
    model = _Model([
        _li("Plaza", (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)),
    ])
    assert _zone_tier_coverage(model, _zone("Plaza")) == "ESSENTIAL + ENHANCED + SIGNATURE"


def test_wildcard_zone_contributes_to_every_zone():
    """Line items with zone='*' apply to every zone."""
    model = _Model([
        _li("*", (Tier.ESSENTIAL, Tier.ENHANCED)),
    ])
    assert _zone_tier_coverage(model, _zone("AnyZone")) == "ESSENTIAL + ENHANCED"


def test_zone_with_no_priced_items_returns_empty():
    """No badge for zones that have no priced line items (and no wildcard)."""
    model = _Model([
        _li("Other", (Tier.ESSENTIAL,)),
    ])
    assert _zone_tier_coverage(model, _zone("Empty")) == ""
