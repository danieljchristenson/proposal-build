"""Unit tests for menu-mode ctx builders."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.composer.menu_ctx_builders import (
    build_image_fullbleed_ctx,
    build_menu_creative_vision_ctx,
    build_menu_zone_solo_ctx,
    build_menu_zone_2up_gallery_ctx,
    build_menu_rom_investment_ctx,
    build_menu_sign_off_ctx,
    set_resolved_project_dir,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


@pytest.fixture(scope="module", autouse=True)
def _set_dir():
    # MenuProjectModel is frozen; the project dir for image URI resolution
    # is communicated via module-level state in menu_ctx_builders.
    set_resolved_project_dir(FIGAT7TH)
    yield
    set_resolved_project_dir(None)


@pytest.fixture(scope="module")
def model():
    return parse_project(FIGAT7TH)


def test_image_fullbleed_cover(model):
    ctx = build_image_fullbleed_ctx(model, page_num=1, page_total=12, kind="cover")
    assert ctx["page_num"] == 1
    assert ctx["page_total"] == 12
    assert ctx["hero_image"].endswith("01_cover-slide-cityscape.png")


def test_image_fullbleed_palette(model):
    ctx = build_image_fullbleed_ctx(model, page_num=2, page_total=12, kind="palette")
    assert ctx["hero_image"].endswith("02_palette-board-mood.png")


def test_creative_vision_passes_phases_and_hero(model):
    ctx = build_menu_creative_vision_ctx(model, page_num=3, page_total=12)
    assert ctx["design_phrase"].startswith("Modern Magic")
    assert ctx["hero_fit"] == "contain"
    assert len(ctx["phases"]) == 3


def test_zone_solo_for_single_item_section(model):
    """Section 1 (canopy) renders as zone_solo with section header inlined."""
    section = next(s for s in model.sections if s.key == "1")
    ctx = build_menu_zone_solo_ctx(model, section, page_num=4, page_total=12)
    assert ctx["section_label"] == "Section One"
    assert ctx["section_name"] == "Main Entrance Overhead"
    assert ctx["zone_name"] == "Mixed Ornament Canopy"
    assert ctx["hero_image"].endswith("20_overhead-mixed-canopy.png")


def test_zone_2up_gallery_for_arch_alternates(model):
    """Section 3a, slide A: first two arches with section header + alt banner."""
    section = next(s for s in model.sections if s.key == "3a")
    ctx = build_menu_zone_2up_gallery_ctx(
        model, section, items=section.items[:2],
        page_num=6, page_total=12, is_first_slide_of_section=True,
        alternate_banner="Customer Choice — Pick One",
    )
    assert ctx["section_label"] == "Section Three"
    assert ctx["section_name"] == "Plaza Photo-Ops"
    assert ctx["alternate_banner"] == "Customer Choice — Pick One"
    assert len(ctx["cells"]) == 2
    # Option A is the first item in the Brief order (which is rendering 33)
    assert ctx["cells"][0]["eyebrow"] == "OPTION A"


def test_rom_investment_totals(model):
    """ROM totals math: rental, purchase OT, purchase service — verified
    against the FIGat7th values locked in session memory."""
    ctx = build_menu_rom_investment_ctx(
        model, page_num=10, page_total=12, page_part=1,
    )
    # When page_part=1, totals are not shown (continuation slide carries them).
    assert ctx["show_totals"] is False
    ctx2 = build_menu_rom_investment_ctx(
        model, page_num=11, page_total=12, page_part=2,
    )
    assert ctx2["show_totals"] is True
    assert ctx2["total_rental"] == "$231,527 – $239,652"
    assert ctx2["total_purchase_ot"] == "$299,601 – $309,201"
    assert ctx2["total_purchase_svc"] == "$107,001 – $112,401"


def test_sign_off_uses_dm_contact(model):
    ctx = build_menu_sign_off_ctx(model, page_num=12, page_total=12)
    assert ctx["client_contact_name"] == "Alexandra Castro"
    assert ctx["client_contact_email"] == "acastro@athenapm.com"


def test_build_tree_comparison_ctx_produces_three_cards_with_recommended_flag():
    """Builder maps loaded entries → cards with rule-color alternation + recommended flag."""
    from pathlib import Path
    from proposal_build.composer import _load_tree_entries
    from proposal_build.composer.menu_ctx_builders import build_tree_comparison_ctx
    from proposal_build.models import MenuProjectModel

    fixture_lib = Path(__file__).resolve().parent / "fixtures" / "tree_library"
    entries = _load_tree_entries(
        ["fixture_tree_a", "fixture_tree_b", "fixture_tree_c"],
        library_dir=fixture_lib,
    )
    model = MenuProjectModel(
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
    ctx = build_tree_comparison_ctx(
        model, page_num=11, page_total=12,
        tree_entries=entries, recommended_id="fixture_tree_b",
    )

    # Header copy
    assert ctx["page_num"] == 11
    assert ctx["page_total"] == 12
    assert ctx["page_eyebrow"] == "Alternate Tree Options"
    assert ctx["page_title"] == "Three scale options"
    assert "Three commercial frame trees" in ctx["standfirst"]

    # Cards
    assert len(ctx["cards"]) == 3
    assert [c["height_eyebrow"] for c in ctx["cards"]] == ["30 FT", "40 FT", "50 FT"]
    assert [c["is_recommended"] for c in ctx["cards"]] == [False, True, False]
    # Rule-color alternation: gray / red / navy across the three cards
    assert [c["rule_color"] for c in ctx["cards"]] == ["gray", "red", "navy"]
    # Image URI is propagated
    assert ctx["cards"][0]["image"].endswith("fixture_tree_a.jpg")
    # Bullets propagated verbatim
    assert ctx["cards"][0]["bullets"][0].startswith("18,700")
    # Price sublabel constant on every card
    assert ctx["cards"][0]["price_sublabel"] == "PURCHASE · FULLY DECORATED"
