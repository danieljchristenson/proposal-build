"""Tests for menu-mode slide list assembly."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.composer.menu_compose import compose_menu


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


@pytest.fixture(scope="module")
def slides():
    model = parse_project(FIGAT7TH)
    slides_, _docs = compose_menu(model)
    return slides_


def test_figat7th_compose_yields_thirteen_slides(slides):
    assert len(slides) == 13


def test_figat7th_slide_layouts_in_order(slides):
    expected = [
        "image_fullbleed",   # 1 cover
        "image_fullbleed",   # 2 palette
        "creative_vision",   # 3
        "zone_solo",         # 4 canopy (Section 1 lead)
        "zone_solo",         # 5 tree (Section 2 lead)
        "zone_2up_gallery",  # 6 arches A (Section 3 lead)
        "zone_2up_gallery",  # 7 arches B (continuation)
        "zone_2up_gallery",  # 8 moments A
        "zone_2up_gallery",  # 9 moments B
        "rom_investment",    # 10 investment p1
        "rom_investment",    # 11 investment p2
        "tree_comparison",   # 12 tree size comparison
        "sign_off",          # 13
    ]
    actual = [s.layout_name for s in slides]
    assert actual == expected


def test_page_numbers_continuous(slides):
    nums = [s.context["page_num"] for s in slides]
    assert nums == list(range(1, len(slides) + 1))
    assert all(s.context["page_total"] == len(slides) for s in slides)


def test_arches_first_slide_has_section_header(slides):
    arches_a = slides[5]
    assert arches_a.context["section_label"] == "Section Three"
    assert arches_a.context["section_name"] == "Plaza Photo-Ops"


def test_arches_continuation_slide_has_no_section_header(slides):
    arches_b = slides[6]
    assert "section_label" not in arches_b.context


def test_moments_slide_has_no_alt_banner(slides):
    """Section slides used to carry 'Customer Choice — Pick One' / 'All Four Included'
    banners; both were dropped because sections are menus (customer picks any subset)."""
    moments_a = slides[7]
    assert moments_a.context["alternate_banner"] == ""
