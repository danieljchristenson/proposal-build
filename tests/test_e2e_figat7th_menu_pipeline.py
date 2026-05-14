"""End-to-end test: parse FIGat7th project → compose → render PDF.

This is the regression test that proves the menu pipeline produces the
13-slide FIGat7th deck (Plan 9 base + Plan 11 tree_comparison).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.composer import compose
from proposal_build.renderer.pdf import render_proposal_pdf


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def test_figat7th_renders_to_pdf(tmp_path):
    model = parse_project(FIGAT7TH)
    slides, _pricing_docs = compose(model)
    assert len(slides) == 13

    out = tmp_path / "figat7th-deck.pdf"
    render_proposal_pdf([(s.layout_name, s.context) for s in slides], out)
    assert out.exists()
    assert out.stat().st_size > 100_000  # multi-page PDF is at least 100 KB
