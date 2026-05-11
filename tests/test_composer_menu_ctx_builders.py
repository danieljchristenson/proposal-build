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
    set_resolved_project_dir(Path("."))


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
    assert ctx2["total_rental"] == "$227,150 – $234,650"
    assert ctx2["total_purchase_ot"] == "$280,000 – $289,600"
    assert ctx2["total_purchase_svc"] == "$117,000 – $120,900"


def test_sign_off_uses_dm_contact(model):
    ctx = build_menu_sign_off_ctx(model, page_num=12, page_total=12)
    assert ctx["client_contact_name"] == "Alexandra Castro"
    assert ctx["client_contact_email"] == "acastro@athenapm.com"
