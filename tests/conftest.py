"""Test fixtures and helpers shared across the layout test suite.

Plan 2-prime keeps rendering glue inside tests/ — Plan 3 will write the
production render pipeline at skill_assets/generate.py. This helper
exists only to drive the layout tests.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

REPO_ROOT = Path(__file__).resolve().parent.parent
LAYOUTS_DIR = REPO_ROOT / "skill_assets" / "layouts"
OUTPUT_DIR = REPO_ROOT / "tests" / "_output"


@pytest.fixture(scope="session")
def jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )


@pytest.fixture(scope="session")
def render_layout(jinja_env: Environment):
    """Render a layout HTML file to PDF. Returns the PDF path.

    Args:
        layout_name: filename stem under skill_assets/layouts/, e.g. "cover".
        ctx: Python dict passed to Jinja2 as the rendering context.
        out_name: optional output filename stem. Defaults to layout_name.
            Use this when the same layout is rendered twice with different
            ctxs (e.g. zone_solo for two zones from the same fixture).

    Returns:
        Path to the rendered PDF file in tests/_output/{out_name}.pdf.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _render(layout_name: str, ctx: dict[str, Any], out_name: str | None = None) -> Path:
        template = jinja_env.get_template(f"{layout_name}.html")
        html_string = template.render(**ctx)
        out = OUTPUT_DIR / f"{out_name or layout_name}.pdf"
        HTML(string=html_string, base_url=str(LAYOUTS_DIR)).write_pdf(target=str(out))
        return out

    return _render
