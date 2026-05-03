"""Asserts base.html exposes the documented Jinja2 contract for Plan 2-prime."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_HTML = REPO_ROOT / "skill_assets" / "layouts" / "base.html"


def test_base_html_exists():
    assert BASE_HTML.is_file()


def test_links_brand_css():
    body = BASE_HTML.read_text()
    assert 'href="brand.css"' in body


def test_exposes_required_blocks():
    body = BASE_HTML.read_text()
    for block in [
        "{% block layout_version %}",
        "{% block title %}",
        "{% block extra_head %}",
        "{% block body_class %}",
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


def test_default_body_class_is_page_light():
    """Most pages are light bg; layouts opt into dark via {% block body_class %}page-dark{% endblock %}."""
    body = BASE_HTML.read_text()
    assert "{% block body_class %}page-light{% endblock %}" in body
