"""Pure theme logic: theme name -> stylesheet + per-layout light/dark surface.

No I/O, no side effects. The single source of truth for which pages are dark
under each theme. `classic` must reproduce today's hardcoded body_class
choices exactly so existing decks are byte-stable.
"""
from __future__ import annotations

# Layouts that render dark under the classic theme (mirrors the old
# `{% block body_class %}page-dark{% endblock %}` overrides).
_CLASSIC_DARK = frozenset({
    "cover",
    "image_fullbleed",
    "creative_vision",
    "section_divider",
    "zone_solo_fullbleed",
    "zone_feature",
})

# Under editorial, every page is dark except these (information pages).
_EDITORIAL_LIGHT = frozenset({"about"})

_STYLESHEETS = {
    "classic": "brand.css",
    "editorial": "theme-editorial.css",
}


def stylesheet_for(theme: str) -> str:
    """Filename of the stylesheet base.html should link (resolved vs LAYOUTS_DIR)."""
    return _STYLESHEETS.get(theme, _STYLESHEETS["classic"])


def surface_for(theme: str, layout: str) -> str:
    """Return "dark" or "light" for a (theme, layout) pair."""
    if theme == "editorial":
        return "light" if layout in _EDITORIAL_LIGHT else "dark"
    # classic and any unknown theme fall back to classic surfaces
    return "dark" if layout in _CLASSIC_DARK else "light"
