"""Render N (layout, ctx) tuples → 1 multi-page proposal PDF."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

from proposal_build.composer.theming import surface_for, stylesheet_for

LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def _enrich_ctx(ctx: dict, theme: str, layout: str) -> dict:
    """Return a copy of ctx with theme chrome variables added (non-mutating)."""
    return {
        **ctx,
        "theme": theme,
        "layout_name": layout,
        "body_surface": surface_for(theme, layout),
        "theme_stylesheet": stylesheet_for(theme),
    }


def render_proposal_pdf(slides: list, out_path: Path, theme: str = "classic") -> Path:
    """slides: list of (layout_name, ctx) tuples. Renders one PDF in `theme`."""
    env = Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    pages = []
    for layout, ctx in slides:
        template = env.get_template(f"{layout}.html")
        html_str = template.render(**_enrich_ctx(ctx, theme, layout))
        doc = HTML(string=html_str, base_url=str(LAYOUTS_DIR)).render()
        pages.extend(doc.pages)

    if not pages:
        raise ValueError("No slides to render")

    first_doc = HTML(string="<html><body></body></html>").render()
    first_doc.pages = pages
    out_path.parent.mkdir(parents=True, exist_ok=True)
    first_doc.write_pdf(target=str(out_path))
    return out_path
