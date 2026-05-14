"""FIGat7th DTLA fixture — Plan 9 data-driven shim.

After Plan 9 the fixture no longer hand-authors slide ctxs; it loads the
project from disk via the same pipeline production uses. Kept for the
test_layouts.py snapshot suite (if any) and for ad-hoc rendering checks.
"""
from __future__ import annotations

from pathlib import Path

from proposal_build.parser import parse_project
from proposal_build.composer import compose


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def load_slides() -> list:
    """Returns [(layout_name, ctx), ...] for renderer.pdf.render_proposal_pdf."""
    model = parse_project(PROJECT_DIR)
    slides, _ = compose(model)
    return [(s.layout_name, s.context) for s in slides]


SLIDES = load_slides()
