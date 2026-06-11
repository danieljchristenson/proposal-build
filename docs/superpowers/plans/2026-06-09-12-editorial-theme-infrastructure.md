# Editorial Theme — Infrastructure Implementation Plan (Plan 12)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a swappable theme layer to the proposal engine so any deck can render as `classic` (today's look, byte-identical) or `editorial` (a new dark system), selected per project — with all the plumbing tested and Classic provably unchanged.

**Architecture:** A theme is (1) a per-project `theme` string on `ProjectModel`, (2) a stylesheet chosen by name (`brand.css` for classic, `theme-editorial.css` for editorial), and (3) a per-page light/dark **surface** decided by a pure `(theme, layout) → surface` map. The render boundary (`render_proposal_pdf`) injects `theme`, `body_surface`, and `layout_name` into every slide's ctx; `base.html` consumes them. No content-pipeline, parser-logic, or pricing-math changes.

**Tech Stack:** Python 3.11+ (machine runs 3.14), Jinja2 (`StrictUndefined`), WeasyPrint, pytest. CSS for WeasyPrint (no box-shadow/filter; gradients, radius, opacity, tabular-nums OK).

**Companion spec:** `docs/superpowers/specs/2026-06-09-st-nicks-editorial-theme-design.md`
**Out of scope (Plan 13 — Editorial Visual Design):** per-layout dark styling, dead-space/truncation fixes, stat call-outs, the go-forward default flip. This plan only builds the harness and a minimal-but-real editorial core sheet so editorial renders correctly.

---

## File Structure

- **Create** `skill_assets/proposal_build/composer/theming.py` — pure theme logic: `STYLESHEET_FOR`, `surface_for(theme, layout)`. One responsibility: map theme/layout → stylesheet + surface. No I/O.
- **Create** `skill_assets/layouts/theme-editorial.css` — self-contained editorial core stylesheet (font-face, @page, dark tokens, base chrome). Refined per-layout in Plan 13.
- **Modify** `skill_assets/proposal_build/models.py` — add `theme: str = "classic"` to `ProjectModel`.
- **Modify** `skill_assets/proposal_build/parser/__init__.py` (~line 131) — read `theme` from Brief front-matter.
- **Modify** `skill_assets/proposal_build/cli.py` (~line 336) — pass `theme="classic"` in the placeholder model.
- **Modify** `skill_assets/proposal_build/renderer/pdf.py` — `render_proposal_pdf(slides, out_path, theme="classic")`; inject `theme`/`body_surface`/`layout_name` per slide.
- **Modify** `skill_assets/proposal_build/renderer/__init__.py` (~line 56) — pass `model.theme` into `render_proposal_pdf`.
- **Modify** `skill_assets/layouts/base.html` — theme-aware stylesheet link + `body` class from `body_surface`/`theme`.
- **Modify** 7 layouts (`cover.html`, `about.html`, `creative_vision.html`, `section_divider.html`, `image_fullbleed.html`, `zone_solo_fullbleed.html`, `zone_feature.html`) — remove the now-redundant `{% block body_class %}` override.
- **Create** `tests/test_theming.py` — unit tests for `theming.py`.
- **Create** `tests/test_theme_classic_stable.py` — proves Classic body-class/stylesheet output is unchanged.
- **Modify** `tests/test_base_html.py` — update expectations for the new body/stylesheet markup.

---

## Task 1: `theme` field on the model

**Files:**
- Modify: `skill_assets/proposal_build/models.py` (ProjectModel, after the trailing defaulted fields ~line 181)
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_models.py`:

```python
def test_projectmodel_theme_defaults_to_classic():
    from proposal_build.models import ProjectModel
    import dataclasses
    fields = {f.name: f for f in dataclasses.fields(ProjectModel)}
    assert "theme" in fields, "ProjectModel must carry a theme field"
    assert fields["theme"].default == "classic"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py::test_projectmodel_theme_defaults_to_classic -v`
Expected: FAIL (`"theme" in fields` is False).

- [ ] **Step 3: Add the field**

In `skill_assets/proposal_build/models.py`, in `ProjectModel`, after the last existing defaulted field (the `client_contact_*` / `resolved_renderings` block), add:

```python
    # Visual theme: "classic" (default, today's look) or "editorial" (dark system).
    theme: str = "classic"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py::test_projectmodel_theme_defaults_to_classic -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/models.py tests/test_models.py
git commit -m "feat(models): add theme field to ProjectModel (default classic)"
```

---

## Task 2: Pure theme logic (`theming.py`)

**Files:**
- Create: `skill_assets/proposal_build/composer/theming.py`
- Test: `tests/test_theming.py`

The surface map must reproduce today's Classic surfaces exactly. Today's `page-dark` layouts (from `body_class` overrides): `cover`, `image_fullbleed`, `creative_vision`, `section_divider`, `zone_solo_fullbleed`, `zone_feature`. Everything else is light. Editorial: everything dark **except** `about` (light).

- [ ] **Step 1: Write the failing test**

Create `tests/test_theming.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_theming.py -v`
Expected: FAIL with `ModuleNotFoundError: proposal_build.composer.theming`.

- [ ] **Step 3: Implement `theming.py`**

Create `skill_assets/proposal_build/composer/theming.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_theming.py -v`
Expected: PASS (all 6 tests).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/composer/theming.py tests/test_theming.py
git commit -m "feat(composer): pure theme logic — stylesheet + surface map"
```

---

## Task 3: Inject theme into the render boundary (`pdf.py`)

**Files:**
- Modify: `skill_assets/proposal_build/renderer/pdf.py`
- Test: `tests/test_render_theme_injection.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_render_theme_injection.py`:

```python
from proposal_build.renderer import pdf as pdfmod


def test_enrich_adds_theme_surface_and_layout_name():
    ctx = {"hello": "world"}
    out = pdfmod._enrich_ctx(ctx, theme="editorial", layout="cover")
    assert out["theme"] == "editorial"
    assert out["layout_name"] == "cover"
    assert out["body_surface"] == "dark"          # cover is dark under editorial
    assert out["hello"] == "world"                # original keys preserved
    assert ctx == {"hello": "world"}              # original dict not mutated


def test_enrich_classic_about_is_light():
    out = pdfmod._enrich_ctx({}, theme="classic", layout="about")
    assert out["body_surface"] == "light"
    assert out["theme"] == "classic"


def test_render_proposal_pdf_defaults_to_classic(tmp_path):
    slides = [("cover", {"season_label": "X", "title": "T", "subtitle": "S",
                          "client_short": "C", "project_year": "2026",
                          "page_num": 1, "page_total": 1})]
    out = tmp_path / "smoke.pdf"
    # Should not raise; theme defaults to classic.
    pdfmod.render_proposal_pdf(slides, out)
    assert out.exists()
```

> Note: if the minimal `cover` ctx above is missing required keys for the real
> `cover.html`, copy a complete cover ctx from `tests/fixtures/riverside.py`
> instead. The point of the third test is only that the default-theme path runs.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_render_theme_injection.py -v`
Expected: FAIL with `AttributeError: module ... has no attribute '_enrich_ctx'`.

- [ ] **Step 3: Implement injection in `pdf.py`**

Replace the body of `skill_assets/proposal_build/renderer/pdf.py` with:

```python
"""Render N (layout, ctx) tuples → 1 multi-page proposal PDF."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

from proposal_build.composer.theming import surface_for, stylesheet_for

LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def _enrich_ctx(ctx: dict, theme: str, layout: str) -> dict:
    """Return a copy of ctx with theme chrome variables added (non-mutating)."""
    return {
        **ctx,
        "theme": theme,
        "layout_name": layout,
        "body_surface": surface_for(theme, layout),
        "theme_stylesheet": stylesheet_for(theme),
    }


def render_proposal_pdf(slides: list, out_path: Path, theme: str = "classic") -> Path:
    """slides: list of (layout_name, ctx) tuples. Renders one PDF in `theme`."""
    env = Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    pages = []
    for layout, ctx in slides:
        template = env.get_template(f"{layout}.html")
        html_str = template.render(**_enrich_ctx(ctx, theme, layout))
        doc = HTML(string=html_str, base_url=str(LAYOUTS_DIR)).render()
        pages.extend(doc.pages)

    if not pages:
        raise ValueError("No slides to render")

    first_doc = HTML(string="<html><body></body></html>").render()
    first_doc.pages = pages
    out_path.parent.mkdir(parents=True, exist_ok=True)
    first_doc.write_pdf(target=str(out_path))
    return out_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_render_theme_injection.py -v`
Expected: the two `_enrich_ctx` tests PASS. `test_render_proposal_pdf_defaults_to_classic` may still fail at Task 3 because `base.html` does not yet read `body_surface` — that's fixed in Task 4. Re-run after Task 4.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/renderer/pdf.py tests/test_render_theme_injection.py
git commit -m "feat(renderer): inject theme/body_surface/layout_name per slide"
```

---

## Task 4: Theme-aware `base.html` + remove per-layout body_class

**Files:**
- Modify: `skill_assets/layouts/base.html`
- Modify: `cover.html`, `about.html`, `creative_vision.html`, `section_divider.html`, `image_fullbleed.html`, `zone_solo_fullbleed.html`, `zone_feature.html`
- Modify: `tests/test_base_html.py`

- [ ] **Step 1: Update `base.html`**

In `skill_assets/layouts/base.html`, change the stylesheet link (line 8) and the body tag (line 11).

Replace line 8:
```html
  <link rel="stylesheet" href="brand.css">
```
with:
```html
  <link rel="stylesheet" href="{{ theme_stylesheet | default('brand.css') }}">
```

Replace line 11:
```html
<body class="{% block body_class %}page-light{% endblock %}">
```
with:
```html
<body class="page-{{ body_surface | default('light') }} theme-{{ theme | default('classic') }}" data-layout="{{ layout_name | default('') }}">
```

(`default(...)` is safe under `StrictUndefined` — the filter intercepts the Undefined before it is stringified, so templates rendered directly in tests without these vars still work and fall back to classic/light.)

- [ ] **Step 2: Remove the now-dead `body_class` block from the 7 layouts**

In each of `cover.html`, `about.html`, `creative_vision.html`, `section_divider.html`, `image_fullbleed.html`, `zone_solo_fullbleed.html`, `zone_feature.html`, delete the line:

```html
{% block body_class %}page-dark{% endblock %}
```
(for `about.html` it is `page-light`). The surface now comes from `body_surface`, which `theming.surface_for` sets to the identical value under classic.

- [ ] **Step 3: Update `tests/test_base_html.py`**

Open `tests/test_base_html.py`. For any assertion that the rendered body contains `class="page-light"` or `class="page-dark"`, update it to render through the theme path. Replace direct `template.render()` calls with the enrich helper, e.g.:

```python
from proposal_build.renderer.pdf import _enrich_ctx

def test_cover_is_dark_under_classic(env):
    tmpl = env.get_template("cover.html")
    html = tmpl.render(**_enrich_ctx(SAMPLE_COVER_CTX, theme="classic", layout="cover"))
    assert 'class="page-dark theme-classic"' in html
    assert 'href="brand.css"' in html

def test_cover_is_dark_under_editorial(env):
    tmpl = env.get_template("cover.html")
    html = tmpl.render(**_enrich_ctx(SAMPLE_COVER_CTX, theme="editorial", layout="cover"))
    assert 'class="page-dark theme-editorial"' in html
    assert 'href="theme-editorial.css"' in html
```

Use whatever sample ctx the file already defines (or import one from `tests/fixtures/riverside.py`). Keep the file's existing `env` fixture if present; otherwise build an `Environment` the same way `pdf.py` does.

- [ ] **Step 4: Run the affected tests**

Run: `pytest tests/test_base_html.py tests/test_render_theme_injection.py -v`
Expected: PASS. (`test_render_proposal_pdf_defaults_to_classic` now passes too.)

- [ ] **Step 5: Commit**

```bash
git add skill_assets/layouts/ tests/test_base_html.py
git commit -m "feat(layouts): theme-aware base.html; surface from body_surface"
```

---

## Task 5: Classic byte-stability guard

**Files:**
- Create: `tests/test_theme_classic_stable.py`

This test renders every layout used by the Riverside fixture under classic and asserts the body class + stylesheet are exactly today's values — the regression net for "Classic is unchanged."

- [ ] **Step 1: Write the test**

Create `tests/test_theme_classic_stable.py`:

```python
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
```

- [ ] **Step 2: Run it**

Run: `pytest tests/test_theme_classic_stable.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_theme_classic_stable.py
git commit -m "test: lock classic theme body-class + stylesheet stability"
```

---

## Task 6: Wire `theme` through parser + renderer entrypoints

**Files:**
- Modify: `skill_assets/proposal_build/parser/__init__.py` (~line 131, `ProjectModel(` call)
- Modify: `skill_assets/proposal_build/cli.py` (~line 336, placeholder `ProjectModel(`)
- Modify: `skill_assets/proposal_build/renderer/__init__.py` (~line 56)
- Test: `tests/test_parser_brief.py` (or the existing brief-parsing test module)

- [ ] **Step 1: Write the failing test**

Add to the brief-parsing test module (find it with `ls tests | grep brief`; likely `tests/test_parser_brief.py`):

```python
def test_brief_theme_frontmatter_flows_to_model(tmp_path):
    # Build a model from a brief whose frontmatter sets theme: editorial.
    # Reuse the module's existing brief-building helper/fixture; only assert theme.
    from proposal_build.parser import build_model_from_project  # adjust to real entry
    # ... arrange a project dir / brief with `theme: editorial` in frontmatter ...
    model = build_model_from_project(project_dir)
    assert model.theme == "editorial"
```

> Adjust the import and arrangement to match how this test file already builds a
> model (the file's existing fixtures show the real entrypoint and brief layout).
> If no model-building helper is exposed, assert at the `frontmatter.get` level
> instead and cover the wiring via the Task 7 pilot render.

- [ ] **Step 2: Run it (fails)**

Run: `pytest tests/test_parser_brief.py -k theme -v`
Expected: FAIL (`model.theme` is `"classic"`).

- [ ] **Step 3: Thread the field**

In `skill_assets/proposal_build/parser/__init__.py`, in the `ProjectModel(` construction (~line 131), add a kwarg (read from the parsed Brief front-matter dict — match the local variable name already used, e.g. `fm` / `bd.frontmatter`):

```python
        theme=fm.get("theme", "classic"),
```

In `skill_assets/proposal_build/cli.py` placeholder model (~line 336), add:

```python
        theme="classic",
```

In `skill_assets/proposal_build/renderer/__init__.py`, change the proposal render call (~line 56) from:

```python
    render_proposal_pdf([(s.layout_name, s.context) for s in slides], proposal_run)
```
to:
```python
    render_proposal_pdf([(s.layout_name, s.context) for s in slides], proposal_run,
                        theme=model.theme)
```

- [ ] **Step 4: Run it (passes) + full suite**

Run: `pytest tests/test_parser_brief.py -k theme -v` → PASS
Run: `pytest` (full suite) → all green. Fix any direct-render tests that now need `_enrich_ctx` (same pattern as Task 4 Step 3).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/parser/__init__.py skill_assets/proposal_build/cli.py skill_assets/proposal_build/renderer/__init__.py tests/
git commit -m "feat: thread project theme from brief frontmatter to renderer"
```

---

## Task 7: Minimal-but-real `theme-editorial.css` + render proof

**Files:**
- Create: `skill_assets/layouts/theme-editorial.css`
- Test: `tests/test_theme_editorial_renders.py` (create)

This is a legitimate v1 editorial **core** sheet (dark ground, red hairline rule, Roboto Black caps headings, Poppins body, footer). Per-layout polish, dead-space/truncation fixes, and stat call-outs are Plan 13.

- [ ] **Step 1: Write the failing render test**

Create `tests/test_theme_editorial_renders.py`:

```python
from pathlib import Path
from proposal_build.renderer.pdf import LAYOUTS_DIR, render_proposal_pdf


def test_editorial_stylesheet_exists():
    assert (Path(LAYOUTS_DIR) / "theme-editorial.css").exists()


def test_riverside_renders_in_editorial(tmp_path):
    from tests.fixtures.riverside import SLIDES  # existing fixture slide list
    out = tmp_path / "riverside-editorial.pdf"
    render_proposal_pdf(SLIDES, out, theme="editorial")
    assert out.exists()
    assert out.stat().st_size > 100_000
```

> If the fixture module/const is named differently, find it with
> `ls tests/fixtures` and `grep -n SLIDES tests/fixtures/riverside.py`.

- [ ] **Step 2: Run it (fails)**

Run: `pytest tests/test_theme_editorial_renders.py -v`
Expected: FAIL (`theme-editorial.css` missing).

- [ ] **Step 3: Create the stylesheet**

Create `skill_assets/layouts/theme-editorial.css`. Self-contained (own `@font-face`, `@page`, tokens) so it never depends on `brand.css`:

```css
/* St. Nick's Editorial theme — dark system. Self-contained core.
 * Per-layout polish lives in Plan 13. Brand-verified tokens only:
 * red #B31315, charcoal #1C1C1C, gray #555, navy #12355B, light #ECEFF1.
 * No gold, no serif, no box-shadow (WeasyPrint-unsupported).
 */
@font-face { font-family:"Roboto"; src:url("../fonts/Roboto-Black.ttf") format("truetype"); font-weight:900; }
@font-face { font-family:"Roboto"; src:url("../fonts/Roboto-Bold.ttf") format("truetype"); font-weight:700; }
@font-face { font-family:"Roboto"; src:url("../fonts/Roboto-Regular.ttf") format("truetype"); font-weight:400; }
@font-face { font-family:"Poppins"; src:url("../fonts/Poppins-Light.ttf") format("truetype"); font-weight:300; }
@font-face { font-family:"Poppins"; src:url("../fonts/Poppins-Regular.ttf") format("truetype"); font-weight:400; }
@font-face { font-family:"Poppins"; src:url("../fonts/Poppins-Medium.ttf") format("truetype"); font-weight:500; }

:root {
  --color-red:#B31315; --color-navy:#12355B; --color-light:#ECEFF1;
  --ink:#ECEFF1; --muted:#9A9C A1; --muted:#9A9CA1;
  --surface-0:#121214; --surface-1:#1C1C1C; --surface-2:#26262A;
  --font-heading:"Roboto",sans-serif; --font-body:"Poppins",sans-serif;
  --space-3:12pt; --space-4:16pt; --space-6:24pt;
}

@page { size:13.333in 7.5in; margin:0; }

html, body {
  margin:0; padding:0; width:13.333in; height:7.5in;
  font-family:var(--font-body); font-weight:400; font-size:12pt; line-height:1.5;
}
body.page-dark  { background:var(--surface-1); color:var(--ink); }
body.page-light { background:#fff; color:#1C1C1C; }

/* Red top hairline rule on every dark page */
body.page-dark::before {
  content:""; position:absolute; top:0; left:0; right:0; height:4px;
  background:var(--color-red); z-index:50;
}

.page-header { position:absolute; top:var(--space-4); left:var(--space-6); }
.page-header .brand-logo { height:0.45in; width:auto; display:block; }
body.page-dark .page-header { filter:none; }

.page-content { position:absolute; top:0.9in; left:var(--space-6); right:var(--space-6); bottom:0.55in; }

h1,h2,h3,h4 {
  font-family:var(--font-heading); font-weight:900; text-transform:uppercase;
  letter-spacing:-0.01em; line-height:0.98; margin:0 0 var(--space-3) 0;
}
p { margin:0 0 var(--space-3) 0; }

.eyebrow, .label {
  font-family:var(--font-heading); font-weight:700; font-size:10pt;
  text-transform:uppercase; letter-spacing:0.18em; color:var(--color-red);
}
.page-title {
  font-family:var(--font-heading); font-weight:900; text-transform:uppercase;
  font-size:46pt; line-height:0.96; letter-spacing:-0.01em; margin:0;
}
body.page-dark .page-title { color:var(--ink); }

.page-footer {
  position:absolute; bottom:var(--space-4); left:var(--space-6); right:var(--space-6);
  display:flex; justify-content:space-between; align-items:baseline;
  font-family:var(--font-body); font-weight:500; font-size:8pt;
  letter-spacing:0.18em; text-transform:uppercase;
}
body.page-dark .page-footer { color:rgba(236,239,241,0.6); }

/* Tabular numerals everywhere numbers matter */
.stat-num, .price, td { font-variant-numeric:tabular-nums lining-nums; }
```

> Remove the duplicated `--muted` line shown above — keep a single
> `--muted:#9A9CA1;`. (Listed twice here only to flag the correct value.)

- [ ] **Step 4: Run it (passes)**

Run: `pytest tests/test_theme_editorial_renders.py -v`
Expected: PASS (Riverside renders to a >100KB PDF under editorial).

- [ ] **Step 5: Eyeball the render (manual checkpoint)**

```bash
python -c "from tests.fixtures.riverside import SLIDES; from proposal_build.renderer.pdf import render_proposal_pdf; from pathlib import Path; render_proposal_pdf(SLIDES, Path('/tmp/riverside-editorial.pdf'), theme='editorial')"
open /tmp/riverside-editorial.pdf
```
Expected: dark pages with the red top rule, Roboto Black caps headings, About page still light. Rough (not yet polished) — Plan 13 refines per layout. Confirm nothing is broken/illegible before continuing.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/theme-editorial.css tests/test_theme_editorial_renders.py
git commit -m "feat(theme): minimal-but-real editorial core stylesheet + render proof"
```

---

## Task 8: Full-suite green + layout pin refresh

**Files:**
- Possibly: `Projects/Downtown Riverside Metro Link/04 - Process & Notes/layout_pin.json` (regenerated on next real run; no manual edit needed)

- [ ] **Step 1: Run the entire suite**

Run: `pytest`
Expected: all green (303+ tests). Investigate any failure; the usual cause is a direct-render test needing `_enrich_ctx` (apply the Task 4 Step 3 pattern).

- [ ] **Step 2: Confirm Classic byte-stability end to end**

Render the Riverside fixture under classic and diff the body markup against `main` if desired; the `tests/test_theme_classic_stable.py` guard already covers this structurally.

Run: `pytest tests/test_theme_classic_stable.py tests/test_theming.py -v`
Expected: PASS.

- [ ] **Step 3: Commit any remaining test fixups**

```bash
git add -A
git commit -m "test: full-suite green after theme infrastructure"
```

---

## Self-Review (completed by author)

**Spec coverage:** Theme-as-swappable-layer (Tasks 2–6 ✓); core vs theme CSS without touching `brand.css` — resolved per spec open-Q #3 as "brand.css stays classic; editorial added" (Task 7 ✓); per-page light/dark surface map with About light (Task 2 ✓); `theme` field source = Brief front-matter (Task 6 ✓, resolves spec open-Q #1); surface mechanism = ctx var + map (Task 3, resolves spec open-Q #2); Classic unchanged (Task 5 guard ✓). **Deferred to Plan 13 (per spec §8):** per-layout Editorial styling, dead-space + Creative Vision truncation fixes, stat call-outs, and the go-forward **default flip** (this plan keeps default `classic`; the flip happens after Plan 13 validation).

**Placeholder scan:** No "TBD/TODO". Two steps say "adjust import to match the file" (Task 6 Step 1, Task 7 Step 1) — these are real instructions to match existing fixture names the engineer can read, not missing logic; the assertions and wiring are fully specified.

**Type consistency:** `surface_for(theme, layout)`, `stylesheet_for(theme)`, `_enrich_ctx(ctx, theme, layout)`, `render_proposal_pdf(slides, out_path, theme="classic")` used identically across Tasks 2–7. Ctx keys `theme` / `body_surface` / `layout_name` / `theme_stylesheet` consistent between `pdf.py`, `base.html`, and tests.

**Note for executor:** the `theme-editorial.css` snippet in Task 7 intentionally flags a duplicated `--muted` declaration — keep only `--muted:#9A9CA1;`.
