"""Tests for composer/slide_plan.py — auto-arrange + pick_grouping + override."""
from __future__ import annotations

import pytest

from proposal_build.models import Zone
from proposal_build.composer.slide_plan import (
    auto_arrange_zones,
    pick_grouping,
    SlidePlanError,
)


def _z(num: str, name: str, *flags: str) -> Zone:
    return Zone(num=num, name=name, subtitle=f"{name} subtitle.",
                flags=tuple(flags), hero_image=f"{name}.jpg",
                bullets=("Bullet A", "Bullet B"))


def test_auto_arrange_n1_signature_only():
    zones = [_z("01", "Solo", "signature")]
    plan = auto_arrange_zones(zones)
    assert [layout for layout, _ in plan] == ["zone_solo_fullbleed"]


def test_auto_arrange_n1_no_signature():
    """Without a signature flag, single zone gets zone_solo (not fullbleed)."""
    zones = [_z("01", "Solo")]
    plan = auto_arrange_zones(zones)
    assert [layout for layout, _ in plan] == ["zone_solo"]


def test_auto_arrange_n2_solo_plus_fullbleed():
    zones = [_z("01", "A"), _z("02", "B", "signature")]
    plan = auto_arrange_zones(zones)
    assert [layout for layout, _ in plan] == ["zone_solo", "zone_solo_fullbleed"]


def test_auto_arrange_n3_pier_39_pattern():
    zones = [_z("01", "Embarcadero"), _z("02", "Promenade"), _z("03", "Bay Terrace", "signature")]
    plan = auto_arrange_zones(zones)
    layouts = [layout for layout, _ in plan]
    assert layouts == ["zone_solo", "zone_solo", "zone_solo_fullbleed"]


def test_auto_arrange_n6_riverside_pattern():
    zones = [
        _z("01", "Downtown Riverside", "flagship"),
        _z("02", "La Sierra"), _z("03", "Pedley"),
        _z("04", "Hunter Park"), _z("05", "Moreno Valley"), _z("06", "Perris"),
    ]
    plan = auto_arrange_zones(zones)
    layouts = [layout for layout, _ in plan]
    assert layouts == ["zone_index", "zone_solo", "zone_2up", "zone_3up"]
    # Verify which zones are in the 2up vs 3up
    twoup_ctx = plan[2][1]
    threeup_ctx = plan[3][1]
    assert [z.name for z in twoup_ctx["zones"]] == ["La Sierra", "Pedley"]
    assert [z.name for z in threeup_ctx["zones"]] == ["Hunter Park", "Moreno Valley", "Perris"]


def test_two_signatures_raises():
    zones = [_z("01", "A", "signature"), _z("02", "B", "signature")]
    with pytest.raises(SlidePlanError):
        auto_arrange_zones(zones)


@pytest.mark.parametrize("n,expected", [
    (0, []),
    (1, [1]),
    (2, [2]),
    (3, [3]),
    (4, [2, 2]),
    (5, [2, 3]),
    (6, [3, 3]),
    (7, [2, 2, 3]),
    (8, [2, 3, 3]),
    (9, [3, 3, 3]),
    (10, [2, 2, 3, 3]),
])
def test_pick_grouping_table(n, expected):
    assert pick_grouping(n) == expected


def test_zone_layout_override_used():
    """Brief-level per-zone layout: override skips auto-pick for that zone."""
    zones = [_z("01", "A")]
    # Override: force fullbleed even though no signature flag
    z = zones[0].__class__(num="01", name="A", subtitle="", flags=(),
                          hero_image="a.jpg", bullets=(),
                          layout_override="zone_solo_fullbleed")
    plan = auto_arrange_zones([z])
    assert [layout for layout, _ in plan] == ["zone_solo_fullbleed"]
