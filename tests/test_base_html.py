"""Asserts base.html exposes the documented Jinja2 contract."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_HTML = REPO_ROOT / "skill_assets" / "layouts" / "base.html"


def test_base_html_exists():
    assert BASE_HTML.is_file()


def test_links_brand_css():
    body = BASE_HTML.read_text()
    assert 'href="brand.css"' in body


def test_exposes_layout_version_block():
    body = BASE_HTML.read_text()
    assert "{% block layout_version %}" in body
    assert "{% endblock %}" in body


def test_exposes_content_block():
    body = BASE_HTML.read_text()
    assert "{% block content %}" in body


def test_exposes_title_block():
    """Layouts may set page title for accessibility / debugging."""
    body = BASE_HTML.read_text()
    assert "{% block title %}" in body


def test_has_charset_meta():
    body = BASE_HTML.read_text()
    assert 'charset="utf-8"' in body.lower() or 'charset="UTF-8"' in body
