"""Asserts brand.css declares the locked design tokens, font faces, and page chrome."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAND_CSS = REPO_ROOT / "skill_assets" / "layouts" / "brand.css"


def test_brand_css_exists():
    assert BRAND_CSS.is_file()


def test_brand_color_tokens_present():
    """The 5 brand colors from the Branding Board, verbatim."""
    css = BRAND_CSS.read_text()
    assert "--color-red: #B31315" in css
    assert "--color-charcoal: #1C1C1C" in css
    assert "--color-gray: #555555" in css
    assert "--color-navy: #12355B" in css
    assert "--color-light: #ECEFF1" in css


def test_panel_and_green_tokens_present():
    """Plan 2-prime additions for card backgrounds and the Scope page green header."""
    css = BRAND_CSS.read_text()
    assert "--color-panel: #F2F2F2" in css
    assert "--color-green: #1B7A3F" in css


def test_font_face_declarations_present():
    css = BRAND_CSS.read_text()
    for weight_file in [
        "Roboto-Bold.ttf",
        "Roboto-Regular.ttf",
        "Poppins-Light.ttf",
        "Poppins-Regular.ttf",
        "Poppins-Medium.ttf",
        "Poppins-Black.ttf",
    ]:
        assert f"../fonts/{weight_file}" in css, f"Missing @font-face url for {weight_file}"


def test_font_family_tokens_present():
    css = BRAND_CSS.read_text()
    assert "--font-heading:" in css and "Roboto" in css
    assert "--font-body:" in css and "Poppins" in css
    assert "--font-display:" in css


def test_page_geometry_locked():
    css = BRAND_CSS.read_text()
    assert "13.333in 7.5in" in css


def test_typographic_scale_tokens():
    css = BRAND_CSS.read_text()
    for token in ["--text-xs", "--text-sm", "--text-base",
                  "--text-lg", "--text-xl", "--text-2xl", "--text-3xl"]:
        assert token in css


def test_spacing_scale_tokens():
    css = BRAND_CSS.read_text()
    for n in range(1, 9):
        assert f"--space-{n}" in css


def test_page_chrome_classes_present():
    """Plan 2-prime adds .page-light / .page-dark body classes that flip the
    page background and brand-mark + footer colors. base.html sets one of
    these on <body>."""
    css = BRAND_CSS.read_text()
    assert "body.page-light" in css
    assert "body.page-dark" in css
    assert ".page-header" in css
    assert ".page-footer" in css
