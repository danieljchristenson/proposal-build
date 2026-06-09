"""Asserts base.html exposes the documented Jinja2 contract for Plan 2-prime.

Task 4 update: body_class block removed; body surface now comes from
body_surface (injected by _enrich_ctx). Tests that previously checked
raw template source for body_class now verify rendered HTML.
"""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from proposal_build.renderer.pdf import _enrich_ctx

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_HTML = REPO_ROOT / "skill_assets" / "layouts" / "base.html"
LAYOUTS_DIR = REPO_ROOT / "skill_assets" / "layouts"

# Minimal ctx sufficient for base.html to render without UndefinedError.
_BASE_CTX = {
    "project_year": "2026",
    "client_short": "TEST",
    "page_num": 1,
    "page_total": 1,
}


def _make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )


def test_base_html_exists():
    assert BASE_HTML.is_file()


def test_links_theme_stylesheet_classic():
    """Under classic theme, base.html emits href="brand.css"."""
    env = _make_env()
    tmpl = env.get_template("base.html")
    html = tmpl.render(**_enrich_ctx(_BASE_CTX, theme="classic", layout="about"))
    assert 'href="brand.css"' in html


def test_links_theme_stylesheet_editorial():
    """Under editorial theme, base.html emits href="theme-editorial.css"."""
    env = _make_env()
    tmpl = env.get_template("base.html")
    html = tmpl.render(**_enrich_ctx(_BASE_CTX, theme="editorial", layout="about"))
    assert 'href="theme-editorial.css"' in html


def test_exposes_required_blocks():
    body = BASE_HTML.read_text()
    for block in [
        "{% block layout_version %}",
        "{% block title %}",
        "{% block extra_head %}",
        "{% block content %}",
        "{% block footer %}",
    ]:
        assert block in body, f"Missing block: {block}"


def test_chrome_present():
    """Persistent header (brand mark) and footer (project + page number)."""
    body = BASE_HTML.read_text()
    assert "page-header" in body
    assert "ST. NICK'S" in body
    assert "page-footer" in body


def test_has_charset_meta():
    body = BASE_HTML.read_text()
    assert 'charset="utf-8"' in body.lower() or 'charset="UTF-8"' in body


def test_body_surface_light_classic_about():
    """Classic about renders page-light."""
    env = _make_env()
    tmpl = env.get_template("base.html")
    html = tmpl.render(**_enrich_ctx(_BASE_CTX, theme="classic", layout="about"))
    assert 'class="page-light theme-classic"' in html


def test_body_surface_dark_classic_cover():
    """Classic cover renders page-dark."""
    env = _make_env()
    tmpl = env.get_template("base.html")
    html = tmpl.render(**_enrich_ctx(_BASE_CTX, theme="classic", layout="cover"))
    assert 'class="page-dark theme-classic"' in html


def test_body_surface_dark_editorial_cover():
    """Editorial cover also renders page-dark (editorial keeps cover dark)."""
    env = _make_env()
    tmpl = env.get_template("base.html")
    html = tmpl.render(**_enrich_ctx(_BASE_CTX, theme="editorial", layout="cover"))
    assert 'class="page-dark theme-editorial"' in html
    assert 'href="theme-editorial.css"' in html


def test_data_layout_attribute_present():
    """data-layout attribute carries the layout name for CSS targeting."""
    env = _make_env()
    tmpl = env.get_template("base.html")
    html = tmpl.render(**_enrich_ctx(_BASE_CTX, theme="classic", layout="about"))
    assert 'data-layout="about"' in html
