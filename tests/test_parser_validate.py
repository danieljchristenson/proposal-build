"""Tests for parser/validate.py — sniff test (W5/W6/W7) + zone coverage warnings."""
from __future__ import annotations

import pytest

from proposal_build.models import LineItem, Tier
from proposal_build.parser.validate import (
    check_cfd_sniff,
    check_em_dashes,
    check_tier_scenarios_drift,
    check_unused_renderings,
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


def test_w1_gallery_images_count_as_referenced():
    eligible = {"hero.png": "/p/hero.png", "g1.png": "/p/g1.png", "g2.png": "/p/g2.png"}
    # Gallery + hero filenames both must be in referenced_filenames after the fix
    referenced = ["hero.png", "g1.png", "g2.png"]
    warnings = check_unused_renderings(eligible, referenced)
    assert warnings == []


def test_w1_unreferenced_file_still_warns():
    eligible = {"used.png": "/p/used.png", "orphan.png": "/p/orphan.png"}
    warnings = check_unused_renderings(eligible, ["used.png"])
    codes = [w[0] for w in warnings]
    assert "W1" in codes
    assert any("orphan.png" in w[1] for w in warnings)


def test_w1_greenery_references_count_as_referenced():
    eligible = {"swag.png": "/p/swag.png"}
    # greenery_references may live in Base Scope/ or Greenery references/;
    # the parser should add the raw filename either way.
    warnings = check_unused_renderings(eligible, ["swag.png"])
    assert warnings == []


def test_w4_signature_label_does_not_collide_with_enhanced_substring():
    """Signature scenarios labeled 'SIGNATURE — Enhanced + ...' must not
    match the ENHANCED tier via substring; prefix-match required."""
    per_line_sums = {Tier.ENHANCED: 100_000, Tier.SIGNATURE: 200_000}
    scenarios = (("SIGNATURE — Enhanced + Bell Display", 200_000),)
    warnings = check_tier_scenarios_drift(per_line_sums, scenarios)
    # Should match SIGNATURE → 200K (no drift), not ENHANCED → 200K (100% drift).
    assert all("Enhanced" not in w[1].split(" per-line")[0] for w in warnings)


def test_w4_prefix_match_clean_when_totals_align():
    per_line_sums = {Tier.ESSENTIAL: 50_000, Tier.ENHANCED: 100_000, Tier.SIGNATURE: 200_000}
    scenarios = (
        ("ESSENTIAL — Base Scope", 50_000),
        ("ENHANCED — Base + Greenery", 100_000),
        ("SIGNATURE — Enhanced + Add-Ons", 200_000),
    )
    warnings = check_tier_scenarios_drift(per_line_sums, scenarios)
    assert warnings == []


def _model(**overrides):
    """Minimal ProjectModel for em-dash tests."""
    from proposal_build.models import ProjectModel
    base = dict(
        client_company="Acme", client_short="Acme", project_name="X", project_short="X",
        project_year=2026, project_subtitle="", proposal_type="Holiday Proposal",
        presenter_name="P", presenter_title="", presenter_email="", presenter_phone="",
        proposal_date="", go_live="", season_end="", fabrication_lock="", signing_deadline="",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="", pricing_format="tiered",
        cover_image="", creative_vision_hero="", case_study="skip", case_study_hero="",
        zones=(), line_items=(), creative_direction="", customer_goals=(),
        customer_constraints=(), success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(), term_panels={},
        after_approval_steps=(), company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )
    base.update(overrides)
    return ProjectModel(**base)


def test_w8_em_dash_in_design_phrase_warns():
    model = _model(design_phrase="A festive—elevated direction")
    warnings = check_em_dashes(model)
    assert any(w[0] == "W8" and "design_phrase" in w[1] for w in warnings)


def test_w8_em_dash_in_zone_bullet_warns():
    from proposal_build.models import Zone
    z = Zone(num="01", name="Plaza", subtitle="", flags=(), hero_image="",
             bullets=("Anchored — weather-rated for the season",))
    model = _model(zones=(z,))
    warnings = check_em_dashes(model)
    assert any(w[0] == "W8" and "Plaza" in w[1] and "bullet" in w[1] for w in warnings)


def test_w8_em_dash_in_worksheet_customer_facing_warns():
    li = LineItem(line_num="1", item="X", description="d", qty=1, unit="ea",
                  price_per_unit=100, line_total=100, rendering_ref="r.png",
                  customer_facing="14 inch garland — perimeter run",
                  zone="Plaza", tiers=(Tier.ESSENTIAL,))
    model = _model(line_items=(li,))
    warnings = check_em_dashes(model)
    assert any(w[0] == "W8" and "Row #1" in w[1] for w in warnings)


def test_w8_clean_copy_no_warning():
    model = _model(
        design_phrase="Festive, elevated.",
        creative_direction="A clean direction. No dashes here.",
        scope_includes=("Lighting on the canopy.", "Wreaths between columns."),
    )
    assert check_em_dashes(model) == []


def test_w8_en_dash_allowed():
    """En dashes (–) for numeric ranges are fine; only em dashes (—) trip W8."""
    model = _model(project_subtitle="$88K – $200K range across three tiers")
    assert check_em_dashes(model) == []
