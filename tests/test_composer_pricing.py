"""Tests for composer/pricing.py — per-tier itemized pricing doc construction."""
from __future__ import annotations

import pytest

from proposal_build.models import LineItem, ItemizedPricingDoc, Tier
from proposal_build.composer.pricing import (
    build_itemized_pricing_docs,
    compute_partnership_savings,
)


def _li(line_num, item, qty, price, tiers):
    return LineItem(
        line_num=line_num, item=item, description="internal",
        qty=qty, unit="ea", price_per_unit=price, line_total=qty * price,
        rendering_ref="r.png", customer_facing=f"Customer {item}",
        zone="*", tiers=tiers,
    )


# Minimal model stub — only needs the fields pricing reads
class _Model:
    def __init__(self, line_items, pricing_format="tiered",
                 recommended_tier=Tier.ENHANCED, partnership_discounts=()):
        self.line_items = line_items
        self.pricing_format = pricing_format
        self.recommended_tier = recommended_tier
        self.partnership_discounts = partnership_discounts


def test_tiered_format_produces_three_docs():
    items = [
        _li("1", "Wreath", 4, 100, (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)),
        _li("E1", "Snowflakes", 12, 295, (Tier.ENHANCED, Tier.SIGNATURE)),
    ]
    model = _Model(items, "tiered")
    docs = build_itemized_pricing_docs(model)
    assert len(docs) == 3
    by_tier = {d.tier: d for d in docs}
    assert Tier.ESSENTIAL in by_tier
    assert by_tier[Tier.ESSENTIAL].tier_total == 400        # only Wreath
    assert by_tier[Tier.ENHANCED].tier_total == 400 + 3540
    assert by_tier[Tier.SIGNATURE].tier_total == 400 + 3540


def test_single_format_produces_one_doc_for_recommended():
    items = [_li("1", "Wreath", 4, 100, (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE))]
    model = _Model(items, "single", recommended_tier=Tier.SIGNATURE)
    docs = build_itemized_pricing_docs(model)
    assert len(docs) == 1
    assert docs[0].tier == Tier.SIGNATURE


def test_per_tier_filters_split_base_vs_enhancements():
    items = [
        _li("1", "Wreath", 1, 100, (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)),
        _li("E1", "Snowflakes", 1, 200, (Tier.ENHANCED, Tier.SIGNATURE)),
    ]
    model = _Model(items, "tiered")
    docs = {d.tier: d for d in build_itemized_pricing_docs(model)}
    assert len(docs[Tier.ESSENTIAL].base_scope_lines) == 1
    assert len(docs[Tier.ESSENTIAL].enhancement_lines) == 0
    assert len(docs[Tier.ENHANCED].enhancement_lines) == 1


def test_substitution_excludes_replaced_item():
    """Substitution scenario: Traditional in Essential+Enhanced; Spiral in Signature.
    Signature tier shows Spiral but NOT Traditional."""
    items = [
        _li("1", "Traditional Tree", 1, 18000, (Tier.ESSENTIAL, Tier.ENHANCED)),
        _li("E1", "Spiral LED", 1, 22000, (Tier.SIGNATURE,)),
    ]
    model = _Model(items, "tiered")
    docs = {d.tier: d for d in build_itemized_pricing_docs(model)}
    sig_items = [li for li in docs[Tier.SIGNATURE].base_scope_lines + docs[Tier.SIGNATURE].enhancement_lines]
    sig_names = [li.item for li in sig_items]
    assert "Spiral LED" in sig_names
    assert "Traditional Tree" not in sig_names


def test_partnership_savings_computation():
    discounts = (("2-YEAR", "4% OFF"), ("3-YEAR", "6% OFF"), ("5-YEAR", "9% OFF"))
    rows = compute_partnership_savings(tier_total=345000, discounts=discounts,
                                       discount_pcts={"2-YEAR": 0.04, "3-YEAR": 0.06, "5-YEAR": 0.09})
    by_term = {r["term"]: r for r in rows}
    assert by_term["2-YEAR"]["savings"] == -13800
    assert by_term["2-YEAR"]["year_1_price"] == 331200
    assert by_term["3-YEAR"]["savings"] == -20700
    assert by_term["5-YEAR"]["year_1_price"] == 313950
