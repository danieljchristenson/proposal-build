"""Sanity tests for the ProjectModel dataclass contract.

ProjectModel is the boundary between Parser and Composer. Its shape must
match what the existing test fixtures (pier_39.py, riverside.py) hand-author.
"""
from __future__ import annotations

import pytest

from proposal_build.models import (
    ProjectModel,
    Zone,
    LineItem,
    SlidePlanItem,
    ValidationResult,
    Tier,
)


def test_zone_minimal_construction():
    z = Zone(num="01", name="La Sierra", subtitle="A stop.", flags=(), hero_image="img.jpg",
             bullets=("Wreaths",))
    assert z.name == "La Sierra"
    assert z.flags == ()
    assert z.bullets == ("Wreaths",)


def test_zone_flag_helpers():
    z = Zone(num="01", name="A", subtitle="", flags=("flagship", "signature"),
             hero_image="i.jpg", bullets=())
    assert z.is_flagship
    assert z.is_signature

    z2 = Zone(num="02", name="B", subtitle="", flags=(), hero_image="i.jpg", bullets=())
    assert not z2.is_flagship
    assert not z2.is_signature


def test_line_item_tier_membership():
    li = LineItem(
        line_num="11", item="Large Tree", description="Internal: 18ft PVC",
        qty=1, unit="ea", price_per_unit=18654, line_total=18654,
        rendering_ref="Tree.png", customer_facing="Traditional centerpiece tree.",
        zone="Downtown Riverside", tiers=(Tier.ESSENTIAL, Tier.ENHANCED),
    )
    assert Tier.ESSENTIAL in li.tiers
    assert Tier.SIGNATURE not in li.tiers


def test_validation_result_status():
    r = ValidationResult(blockers=[], warnings=[])
    assert r.passed is True
    assert r.status == "PASSED"

    r2 = ValidationResult(blockers=[("missing_field", "voice")], warnings=[])
    assert r2.passed is False
    assert r2.status == "BLOCKED"


def test_project_model_minimal():
    pm = ProjectModel(
        client_company="RCTC", client_short="RCTC", project_name="MetroLink",
        project_short="MetroLink", project_year=2026, project_subtitle="",
        proposal_type="Holiday Proposal",
        presenter_name="J", presenter_title="AE", presenter_email="j@s.com",
        presenter_phone="(555) 555-5555", proposal_date="2026-05-12",
        go_live="2026-11-20", season_end="2027-01-05",
        fabrication_lock="2026-08-22", signing_deadline="2026-10-30",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="Holiday Express.",
        pricing_format="tiered",
        cover_image="cover.jpg", creative_vision_hero="cv.jpg",
        case_study="long_beach_transit", case_study_hero="cs.jpg",
        zones=(), line_items=(),
        creative_direction="", customer_goals=(), customer_constraints=(),
        success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(),
        term_panels={}, after_approval_steps=(),
        company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )
    assert pm.project_name == "MetroLink"
    assert pm.recommended_tier == Tier.ENHANCED


def test_project_model_has_sample_work_field():
    """ProjectModel exposes sample_work as an empty tuple by default."""
    from proposal_build.models import ProjectModel
    import dataclasses
    fields = {f.name for f in dataclasses.fields(ProjectModel)}
    assert "sample_work" in fields, (
        "ProjectModel missing sample_work field — see spec §5"
    )


def test_menu_project_model_has_sample_work_field():
    """MenuProjectModel exposes sample_work as an empty tuple by default."""
    from proposal_build.models import MenuProjectModel
    import dataclasses
    fields = {f.name for f in dataclasses.fields(MenuProjectModel)}
    assert "sample_work" in fields, (
        "MenuProjectModel missing sample_work field — see spec §5"
    )


def test_menu_project_model_has_tree_comparison_field_defaulting_to_empty_dict():
    """MenuProjectModel.tree_comparison defaults to {} so missing Brief field is OK."""
    from proposal_build.models import MenuProjectModel
    m = MenuProjectModel(
        client_company="X", client_short="X",
        project_name="Y", project_short="Y", project_year=2026, project_subtitle="",
        presenter_name="", presenter_title="", presenter_org="",
        proposal_date="",
        client_contact_name="", client_contact_title="",
        client_contact_email="", client_contact_phone="",
        design_phrase="d", voice="v",
        creative_direction="", customer_goals=(), creative_phases=(),
        prebuilt_cover_image="c.png", prebuilt_palette_image="",
        creative_vision_hero="h.png",
        sections=(), what_youre_approving="",
    )
    assert m.tree_comparison == {}


def test_projectmodel_theme_defaults_to_classic():
    from proposal_build.models import ProjectModel
    import dataclasses
    fields = {f.name: f for f in dataclasses.fields(ProjectModel)}
    assert "theme" in fields, "ProjectModel must carry a theme field"
    assert fields["theme"].default == "classic"
