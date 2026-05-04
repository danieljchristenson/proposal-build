"""Render N (layout, ctx) tuples → 1 multi-page proposal PDF."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML


LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def render_proposal_pdf(slides: list, out_path: Path) -> Path:
    """slides: list of SlidePlanItem-like (layout_name, ctx) tuples.

    Renders each slide as a single HTML page with @page breaks between them,
    then writes a single PDF. Returns the output path.
    """
    env = Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    # Render each slide individually, then concatenate via WeasyPrint's render_pages mechanism.
    # WeasyPrint can take multiple HTML(string=...).render() outputs and combine pages.
    pages = []
    for layout, ctx in slides:
        template = env.get_template(f"{layout}.html")
        html_str = template.render(**ctx)
        doc = HTML(string=html_str, base_url=str(LAYOUTS_DIR)).render()
        pages.extend(doc.pages)

    # Use the first doc's metadata; merge all pages
    if not pages:
        raise ValueError("No slides to render")

    # Reuse the first doc's metadata; replace pages list
    first_doc = HTML(string="<html><body></body></html>").render()
    first_doc.pages = pages
    out_path.parent.mkdir(parents=True, exist_ok=True)
    first_doc.write_pdf(target=str(out_path))
    return out_path
