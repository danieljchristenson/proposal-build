"""Golden test: FIGat7th deck produced by the Plan 9 pipeline must match
the locked structural shape from the May 2026 hand-authored deliverable."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures.figat7th import SLIDES
from proposal_build.renderer.pdf import render_proposal_pdf


def test_slide_count():
    assert len(SLIDES) == 12


def test_first_two_slides_are_prebuilt_creatives():
    assert SLIDES[0][0] == "image_fullbleed"
    assert SLIDES[1][0] == "image_fullbleed"


def test_last_slide_is_sign_off():
    assert SLIDES[-1][0] == "sign_off"


def test_renders_to_pdf(tmp_path):
    out = tmp_path / "figat7th-golden.pdf"
    render_proposal_pdf(SLIDES, out)
    assert out.exists()
    assert out.stat().st_size > 100_000


def test_pricing_totals_in_investment_p2():
    """Find slide 11 (investment p2) and assert the locked Program ROM Total."""
    inv_p2 = SLIDES[10]
    layout, ctx = inv_p2
    assert layout == "rom_investment"
    assert ctx["show_totals"] is True
    assert ctx["total_rental"] == "$227,150 – $234,650"
    assert ctx["total_purchase_ot"] == "$280,000 – $289,600"
    assert ctx["total_purchase_svc"] == "$117,000 – $120,900"
