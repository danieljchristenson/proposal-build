"""Editorial theme must render BOTH proposal types (standard + menu-mode).

Riverside exercises the standard deck; FIGat7th exercises menu-mode with the
pricing/comparison layouts (rom_investment, tree_comparison, zone galleries).
This guards against a layout being unstyled/unreadable under editorial.
"""
from pathlib import Path

from proposal_build.renderer.pdf import render_proposal_pdf
from tests.fixtures.figat7th import SLIDES as FIGAT7TH_SLIDES
from tests.test_theme_editorial_renders import _riverside_slides


def test_figat7th_menu_deck_renders_in_editorial(tmp_path):
    out = tmp_path / "figat7th-editorial.pdf"
    render_proposal_pdf(FIGAT7TH_SLIDES, out, theme="editorial")
    assert out.exists()
    assert out.stat().st_size > 100_000


def test_figat7th_covers_menu_pricing_layouts():
    # Sanity: the fixture really exercises the menu/pricing layouts we styled.
    used = {layout for layout, _ in FIGAT7TH_SLIDES}
    for layout in ("rom_investment", "tree_comparison", "zone_2up_gallery"):
        assert layout in used, f"{layout} not in figat7th fixture"


def test_both_proposal_types_render_in_editorial(tmp_path):
    for name, slides in (("riverside", _riverside_slides()),
                         ("figat7th", FIGAT7TH_SLIDES)):
        out = tmp_path / f"{name}-ed.pdf"
        render_proposal_pdf(slides, out, theme="editorial")
        assert out.exists() and out.stat().st_size > 100_000, name
