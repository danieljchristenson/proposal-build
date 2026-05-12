"""One-shot: render the Abigail/Jose handoff brief to PDF.

Usage:
    source .venv/bin/activate
    python3 scripts/render_handoff_pdf.py
"""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML, CSS

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "instructions" / "2026-05-12-past-work-library-handoff.md"
OUT = ROOT / "docs" / "instructions" / "2026-05-12-past-work-library-handoff.pdf"

CSS_TEXT = """
@page {
    size: Letter;
    margin: 0.75in 0.85in 0.85in 0.85in;
    @bottom-right {
        content: "Past Work Library — page " counter(page) " of " counter(pages);
        font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
        font-size: 9pt;
        color: #777;
    }
}

body {
    font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #1A1A1A;
}

h1 {
    font-size: 22pt;
    font-weight: 800;
    color: #1A1A1A;
    border-bottom: 2pt solid #B5121B;
    padding-bottom: 6pt;
    margin: 0 0 4pt 0;
}

h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #1A1A1A;
    margin: 22pt 0 6pt 0;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #1A1A1A;
    margin: 14pt 0 4pt 0;
}

p {
    margin: 0 0 8pt 0;
}

strong {
    color: #1A1A1A;
}

ul, ol {
    margin: 0 0 10pt 0;
    padding-left: 22pt;
}

li {
    margin-bottom: 3pt;
}

code {
    font-family: "SF Mono", Menlo, Consolas, monospace;
    font-size: 9.5pt;
    background: #F2F2EE;
    padding: 1pt 4pt;
    border-radius: 2pt;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0 12pt 0;
    font-size: 10pt;
}

th, td {
    border: 0.5pt solid #D0D0CB;
    padding: 6pt 9pt;
    text-align: left;
    vertical-align: top;
}

th {
    background: #F2F2EE;
    font-weight: 700;
    color: #1A1A1A;
}

hr {
    border: none;
    border-top: 0.5pt solid #D0D0CB;
    margin: 18pt 0;
}

.meta {
    color: #777;
    font-size: 10pt;
    margin-bottom: 18pt;
}

/* Render the [ ] checklists as boxed items */
li input[type="checkbox"] {
    margin-right: 6pt;
}
"""


def main() -> None:
    md_text = SRC.read_text()

    # Markdown → HTML. Use extensions for tables and checklists.
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )

    # Convert GFM-style "[ ]" / "[x]" task lists to checkbox HTML, since the
    # core markdown library doesn't ship that conversion by default.
    html_body = (
        html_body
        .replace("<li>[ ] ", '<li><input type="checkbox" disabled> ')
        .replace("<li>[x] ", '<li><input type="checkbox" disabled checked> ')
    )

    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"></head>
<body>
{html_body}
</body></html>"""

    HTML(string=html_doc).write_pdf(
        str(OUT),
        stylesheets=[CSS(string=CSS_TEXT)],
    )
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
