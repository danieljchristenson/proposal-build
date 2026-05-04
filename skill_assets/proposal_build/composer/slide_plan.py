"""Composer — zone-block slide arrangement.

Implements the auto-arrange algorithm from spec §6 and the pick_grouping table.
"""
from __future__ import annotations

from typing import Sequence

from proposal_build.models import Zone


class SlidePlanError(Exception):
    pass


def auto_arrange_zones(zones: Sequence[Zone]) -> list[tuple[str, dict]]:
    """Return [(layout_name, ctx), ...] for the zone block.

    Honors per-zone layout_override. Validates ≤1 signature flag.
    """
    sigs = [z for z in zones if z.is_signature]
    if len(sigs) > 1:
        names = ", ".join(z.name for z in sigs)
        raise SlidePlanError(f"At most one zone may carry the 'signature' flag; found: {names}")

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
