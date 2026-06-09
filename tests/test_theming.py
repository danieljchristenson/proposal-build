from proposal_build.composer.theming import surface_for, stylesheet_for

CLASSIC_DARK = {
    "cover", "image_fullbleed", "creative_vision",
    "section_divider", "zone_solo_fullbleed", "zone_feature",
}

def test_stylesheet_for_classic_is_brand_css():
    assert stylesheet_for("classic") == "brand.css"

def test_stylesheet_for_editorial():
    assert stylesheet_for("editorial") == "theme-editorial.css"

def test_unknown_theme_falls_back_to_classic_stylesheet():
    assert stylesheet_for("nope") == "brand.css"

def test_classic_surfaces_match_today():
    for layout in CLASSIC_DARK:
        assert surface_for("classic", layout) == "dark", layout
    for layout in ["about", "exec_summary", "scope", "zone_solo", "investment", "terms"]:
        assert surface_for("classic", layout) == "light", layout

def test_editorial_surfaces_are_dark_except_about():
    assert surface_for("editorial", "about") == "light"
    for layout in ["cover", "exec_summary", "zone_solo", "investment", "terms", "scope"]:
        assert surface_for("editorial", layout) == "dark", layout

def test_unknown_theme_uses_classic_surfaces():
    assert surface_for("nope", "cover") == "dark"
    assert surface_for("nope", "about") == "light"
