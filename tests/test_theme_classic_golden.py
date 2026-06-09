"""Classic rendered HTML must not change while we tokenize layouts.
Captures the full rendered HTML string per slide under theme=classic and
compares to a committed snapshot. Regenerate intentionally with REGEN=1."""
import os
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from proposal_build.renderer.pdf import LAYOUTS_DIR, _enrich_ctx
from tests.test_theme_editorial_renders import _riverside_slides

SNAP = Path(__file__).parent / "_golden" / "classic_html"
_SLIDES = _riverside_slides()


def _render(layout, ctx):
    env = Environment(loader=FileSystemLoader(str(LAYOUTS_DIR)),
                      autoescape=True, undefined=StrictUndefined,
                      keep_trailing_newline=True)
    return env.get_template(f"{layout}.html").render(**_enrich_ctx(ctx, "classic", layout))


@pytest.mark.parametrize("idx", range(len(_SLIDES)))
def test_classic_html_matches_golden(idx):
    layout, ctx = _SLIDES[idx]
    html = _render(layout, ctx)
    SNAP.mkdir(parents=True, exist_ok=True)
    f = SNAP / f"{idx:02d}_{layout}.html"
    if os.environ.get("REGEN") == "1" or not f.exists():
        f.write_text(html); pytest.skip(f"wrote golden {f.name}")
    assert html == f.read_text(), f"classic HTML drifted for {layout}"
