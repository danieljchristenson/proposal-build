"""ROM pricing math: per-section row formatting + totals with menu-style alternate-group handling.

Items sharing an `alternate_group` value are treated as a customer-pick-any-subset
menu (not mutually exclusive). For each money axis, the group contributes:
  - low  = min(item.low for item in group)   — cheapest single pick
  - high = sum(item.high for item in group)  — customer takes the whole menu

This replaces the original "bookended min/max" math (which assumed pick-exactly-one)
because in practice the customer can pick zero, one, or several items per section.
"""
from __future__ import annotations

from typing import Iterable

from proposal_build.models import Section, ROMLineItem


def format_money(n: int) -> str:
    return f"${n:,}"


def format_money_range(low: int, high: int) -> str:
    if low == high:
        return format_money(low)
    return f"{format_money(low)} – {format_money(high)}"


def compute_rom_totals(sections: Iterable[Section]) -> dict:
    """Sum across all sections. Within each alternate_group, treat the items
    as a customer-pick-any-subset menu: low = cheapest single, high = sum of
    all. See module docstring for rationale."""
    rental_low = rental_high = 0
    po_low = po_high = 0
    psv_low = psv_high = 0

    # Bucket alternates by group
    groups: dict[str, list[ROMLineItem]] = {}
    non_alts: list[ROMLineItem] = []
    for section in sections:
        for it in section.items:
            if it.is_alternate:
                groups.setdefault(it.alternate_group, []).append(it)
            else:
                non_alts.append(it)

    for it in non_alts:
        rental_low += it.rental_low
        rental_high += it.rental_high
        po_low += it.purchase_ot_low
        po_high += it.purchase_ot_high
        psv_low += it.purchase_svc_low
        psv_high += it.purchase_svc_high

    for items in groups.values():
        rental_low += min(it.rental_low for it in items)
        rental_high += sum(it.rental_high for it in items)
        po_low += min(it.purchase_ot_low for it in items)
        po_high += sum(it.purchase_ot_high for it in items)
        psv_low += min(it.purchase_svc_low for it in items)
        psv_high += sum(it.purchase_svc_high for it in items)

    return {
        "rental_low": rental_low, "rental_high": rental_high,
        "purchase_ot_low": po_low, "purchase_ot_high": po_high,
        "purchase_svc_low": psv_low, "purchase_svc_high": psv_high,
    }


def rows_for_sections(sections, keys):
    """Re-export for ctx_builders import surface symmetry; thin pass-through used in early prototypes."""
    return [s for s in sections if s.key in keys]
