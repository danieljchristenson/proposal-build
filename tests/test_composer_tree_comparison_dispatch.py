"""Tests for composer wiring of the tree_comparison slide (menu mode).

Mirrors test_composer_past_work_dispatch.py — synthesizes a menu-mode model
in-memory (no Brief / Worksheet round-trip) so the test isolates dispatch
ordering. The render path is exercised by Task 11's layout render test.
"""
from __future__ import annotations

from pathlib import Path

import pytest


def _menu_model(**overrides):
    """Minimal menu model with all required scalar fields populated."""
    from proposal_build.models import MenuProjectModel
    defaults = dict(
        client_company="FIGat7th", client_short="FIG",
        project_name="FIGat7th 2026", project_short="FIG", project_year=2026,
        project_subtitle="",
        presenter_name="P", presenter_title="T", presenter_org="O",
        proposal_date="May 12, 2026",
        client_contact_name="A", client_contact_title="B",
        client_contact_email="a@b.com", client_contact_phone="555",
        design_phrase="phrase", voice="destination",
        creative_direction="", customer_goals=(), creative_phases=(),
        prebuilt_cover_image="cover.png", prebuilt_palette_image="",
        creative_vision_hero="hero.png",
        sections=(), what_youre_approving="",
    )
    defaults.update(overrides)
    return MenuProjectModel(**defaults)


def _swap_tree_library_to_fixture(monkeypatch):
    fixture_lib = Path(__file__).resolve().parent / "fixtures" / "tree_library"
    from proposal_build import composer
    monkeypatch.setattr(composer, "TREE_LIBRARY_DIR", fixture_lib)


def test_menu_composer_emits_tree_comparison_when_field_present(monkeypatch):
    """tree_comparison populated → slide between rom_investment and sign_off_menu."""
    _swap_tree_library_to_fixture(monkeypatch)
    from proposal_build.composer.menu_compose import compose_menu

    model = _menu_model(
        tree_comparison={
            "trees": ["fixture_tree_a", "fixture_tree_b", "fixture_tree_c"],
            "recommended": "fixture_tree_b",
        },
    )

    project_dir = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
    )
    slides, _ = compose_menu(model, project_dir=project_dir)
    layouts = [s.layout_name for s in slides]

    assert "tree_comparison" in layouts, (
        f"Expected tree_comparison in slide deck; got: {layouts}"
    )
    tc_idx = layouts.index("tree_comparison")
    # rom_investment appears twice (p1, p2); ensure tree_comparison follows the LAST one
    rom_idxs = [i for i, l in enumerate(layouts) if l == "rom_investment"]
    assert rom_idxs, "Expected rom_investment slides in deck"
    assert tc_idx > rom_idxs[-1], "tree_comparison must come after rom_investment p2"
    sign_off_idx = layouts.index("sign_off")
    assert tc_idx < sign_off_idx, "tree_comparison must come before sign_off"


def test_menu_composer_skips_tree_comparison_when_field_absent(monkeypatch):
    """Empty tree_comparison → no slide emitted, deck assembles as before."""
    _swap_tree_library_to_fixture(monkeypatch)
    from proposal_build.composer.menu_compose import compose_menu

    model = _menu_model()  # tree_comparison defaults to {}
    project_dir = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
    )
    slides, _ = compose_menu(model, project_dir=project_dir)
    layouts = [s.layout_name for s in slides]
    assert "tree_comparison" not in layouts
