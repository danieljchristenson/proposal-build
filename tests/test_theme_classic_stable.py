"""Classic theme must reproduce the pre-theme body-class + stylesheet exactly."""
import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from proposal_build.renderer.pdf import LAYOUTS_DIR, _enrich_ctx
from proposal_build.composer.theming import surface_for

# (layout, expected_surface) for the classic theme — the locked truth table.
EXPECT = [
    ("cover", "dark"), ("creative_vision", "dark"), ("section_divider", "dark"),
    ("image_fullbleed", "dark"), ("zone_solo_fullbleed", "dark"),
    ("zone_feature", "dark"), ("about", "light"), ("exec_summary", "light"),
    ("understanding", "light"), ("scope", "light"), ("zone_solo", "light"),
    ("zone_2up", "light"), ("zone_index", "light"), ("investment", "light"),
    ("terms", "light"), ("sign_off", "light"),
]


@pytest.mark.parametrize("layout,surface", EXPECT)
def test_classic_surface_locked(layout, surface):
    assert surface_for("classic", layout) == surface


def test_classic_body_markup_unchanged():
    env = Environment(loader=FileSystemLoader(str(LAYOUTS_DIR)),
                      autoescape=True, undefined=StrictUndefined)
    # Minimal ctx is fine: we only inspect the <body> tag the base emits.
    for layout, surface in EXPECT:
        # render base.html directly via a tiny child to avoid per-layout ctx needs
        tmpl = env.from_string(
            '{% extends "base.html" %}{% block content %}x{% endblock %}'
        )
        ctx = _enrich_ctx(
            {"project_year": "2026", "client_short": "C",
             "page_num": 1, "page_total": 1},
            theme="classic", layout=layout,
        )
        html = tmpl.render(**ctx)
        assert f'class="page-{surface} theme-classic"' in html, layout
        assert 'href="brand.css"' in html, layout
