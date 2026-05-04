"""Composer — per-tier itemized pricing doc construction."""
from __future__ import annotations

from proposal_build.models import ItemizedPricingDoc, Tier


def build_itemized_pricing_docs(model) -> list[ItemizedPricingDoc]:
    """Returns 1 or 3 ItemizedPricingDoc instances depending on pricing_format."""
    if model.pricing_format == "single":
        tiers_to_emit = [model.recommended_tier]
    else:
        tiers_to_emit = [Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE]

    docs = []
    for tier in tiers_to_emit:
        in_tier = [li for li in model.line_items if tier in li.tiers]
        base = tuple(li for li in in_tier if not li.is_enhancement)
        enh = tuple(li for li in in_tier if li.is_enhancement)
        total = sum(li.line_total for li in in_tier)
        docs.append(ItemizedPricingDoc(
            tier=tier, project=model,
            base_scope_lines=base, enhancement_lines=enh,
            tier_total=total,
        ))
    return docs


def compute_partnership_savings(tier_total: float, discounts: tuple,
                                discount_pcts: dict) -> list[dict]:
    """Given (label, percent_str) tuples + a {label: float} map of percentages,
    return [{term, discount_label, savings, year_1_price}, ...]."""
    rows = []
    for term, label in discounts:
        pct = discount_pcts.get(term, 0)
        savings = -tier_total * pct
        year_1 = tier_total + savings
        rows.append({
            "term": term,
            "discount_label": label,
            "savings": savings,
            "year_1_price": year_1,
        })
    return rows
