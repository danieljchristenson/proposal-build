"""Composer — zone-block slide arrangement.

Implements the auto-arrange algorithm from spec §6 and the pick_grouping table.
"""
from __future__ import annotations

from typing import Sequence

from proposal_build.models import Zone


class SlidePlanError(Exception):
    pass


# Layouts a single zone can be rendered with. Grouping layouts (zone_2up,
# zone_3up, zone_index) require multiple zones and aren't valid as a per-zone
# override.
_VALID_SOLO_OVERRIDES = ("zone_solo", "zone_solo_fullbleed")


def auto_arrange_zones(zones: Sequence[Zone]) -> list[tuple[str, dict]]:
    """Return [(layout_name, ctx), ...] for the zone block.

    Honors per-zone layout_override. Validates ≤1 signature flag.

    Behavior note: when N≥4, soloed zones (flagships, signature, and
    layout-override solos) are emitted at the front of the zone block
    immediately after the zone_index slide. The grouped zones follow in
    declared order. AEs who want strict declared order should use the
    Brief-level slide_plan: override (handled outside this function).
    """
    sigs = [z for z in zones if z.is_signature]
    if len(sigs) > 1:
        names = ", ".join(z.name for z in sigs)
        raise SlidePlanError(f"At most one zone may carry the 'signature' flag; found: {names}")

    # Validate per-zone layout_override values up front so a typo surfaces here
    # rather than as a Jinja KeyError deep in the renderer.
    for z in zones:
        if z.layout_override and z.layout_override not in _VALID_SOLO_OVERRIDES:
            raise SlidePlanError(
                f"Zone {z.num} ({z.name!r}): layout_override must be one of "
                f"{list(_VALID_SOLO_OVERRIDES)}, got {z.layout_override!r}. "
                f"Grouping layouts (zone_2up, zone_3up, zone_index) cannot be "
                f"set per-zone — use the Brief slide_plan: override instead."
            )

    if not zones:
        return []

    # Per-zone layout_override short-circuits everything for that zone
    # We build the plan respecting overrides where present.
    n = len(zones)

    if n <= 3:
        # All zones get solos; signature gets fullbleed
        return [_solo_or_fullbleed(z) for z in zones]

    # n >= 4: index slide + flagships + signature first, rest grouped
    plan: list[tuple[str, dict]] = []
    plan.append(("zone_index", {"zones": list(zones)}))

    soloed_set = set()
    for z in zones:
        if z.is_flagship or z.is_signature or z.layout_override in ("zone_solo", "zone_solo_fullbleed"):
            plan.append(_solo_or_fullbleed(z))
            soloed_set.add(z.num)

    grouped = [z for z in zones if z.num not in soloed_set]
    for chunk_size in pick_grouping(len(grouped)):
        chunk = grouped[:chunk_size]
        grouped = grouped[chunk_size:]
        if chunk_size == 1:
            plan.append(_solo_or_fullbleed(chunk[0]))
        else:
            plan.append((f"zone_{chunk_size}up", {"zones": chunk}))

    return plan


def _solo_or_fullbleed(z: Zone) -> tuple[str, dict]:
    if z.layout_override:
        return (z.layout_override, {"zone": z})
    layout = "zone_solo_fullbleed" if z.is_signature else "zone_solo"
    return (layout, {"zone": z})


def pick_grouping(n: int) -> list[int]:
    """Chunk sizes that sum to n. Smaller-first; avoid orphan 1s by pairing 2,2."""
    if n == 0:
        return []
    if n <= 3:
        return [n]
    rem = n % 3
    if rem == 0:
        return [3] * (n // 3)
    if rem == 2:
        return [2] + [3] * ((n - 2) // 3)
    # rem == 1: replace one 3 with [2, 2] to avoid an orphan 1
    threes = (n - 4) // 3
    return [2, 2] + [3] * threes
