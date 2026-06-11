"""Task 7: editorial theme — stylesheet existence + full Riverside render proof."""
from pathlib import Path

from proposal_build.renderer.pdf import LAYOUTS_DIR, render_proposal_pdf


def _riverside_slides():
    """Return the full Riverside deck as a list of (layout_name, ctx) tuples.

    Shared by test_riverside_renders_in_editorial and the classic golden
    snapshot tests so both suites exercise the identical slide assembly.
    """
    from tests.fixtures import riverside as rv

    return [
        ("cover",           rv.cover_ctx),
        ("exec_summary",    rv.exec_summary_ctx),
        ("understanding",   rv.understanding_ctx),
        ("creative_vision", rv.creative_vision_ctx),
        ("zone_index",      rv.zone_index_ctx),
        ("zone_solo",       rv.zone_flagship_ctx),
        ("zone_2up",        rv.zone_2up_a_ctx),
        ("zone_3up",        rv.zone_3up_ctx),
        ("scope",           rv.scope_ctx),
        ("case_study",      rv.case_study_ctx),
        ("investment",      rv.investment_ctx),
        ("terms",           rv.terms_ctx),
        ("sign_off",        rv.sign_off_ctx),
        ("about",           rv.about_ctx),
    ]


def test_editorial_stylesheet_exists():
    assert (Path(LAYOUTS_DIR) / "theme-editorial.css").exists()


def test_riverside_renders_in_editorial(tmp_path):
    slides = _riverside_slides()
    out = tmp_path / "riverside-editorial.pdf"
    render_proposal_pdf(slides, out, theme="editorial")
    assert out.exists()
    assert out.stat().st_size > 100_000
