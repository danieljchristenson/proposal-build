"""Asserts brand.css declares the locked design tokens and font faces."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAND_CSS = REPO_ROOT / "skill_assets" / "layouts" / "brand.css"


def test_brand_css_exists():
    assert BRAND_CSS.is_file()


def test_color_tokens_present():
    css = BRAND_CSS.read_text()
    assert "--color-red: #B31315" in css
    assert "--color-charcoal: #1C1C1C" in css
    assert "--color-gray: #555555" in css
    assert "--color-navy: #12355B" in css
    assert "--color-light: #ECEFF1" in css


def test_font_face_declarations_present():
    css = BRAND_CSS.read_text()
    # Each of the 5 weights must have an @font-face that loads from ../fonts/
    for weight_file in [
        "Roboto-Bold.ttf",
        "Roboto-Regular.ttf",
        "Poppins-Light.ttf",
        "Poppins-Regular.ttf",
        "Poppins-Medium.ttf",
    ]:
        assert f"../fonts/{weight_file}" in css, f"Missing @font-face url for {weight_file}"


def test_page_geometry_locked():
    css = BRAND_CSS.read_text()
    # 16:9 widescreen, landscape — the only allowed page size
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
