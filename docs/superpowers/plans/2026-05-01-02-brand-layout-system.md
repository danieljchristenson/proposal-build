# Plan 2 — Brand + Layout System Implementation Plan

> ⚠️ **SUPERSEDED 2026-05-03.** This plan executed but its output (18 abstract
> layouts) was rejected. Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-layouts.md`](./2026-05-03-plan-2-prime-master-driven-layouts.md).
> Output preserved at `archive/iteration-1-abstract-layouts/`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the deployable brand + layout foundation: page geometry, embedded Roboto + Poppins fonts, `brand.css` design tokens, a Jinja2 `base.html` shell, all 18 slide layouts, and a fixture-driven test suite that proves every layout renders correctly with embedded fonts at the right page size.

**Architecture:** WeasyPrint pipeline driven by Jinja2 templates. `base.html` owns the shared `<head>` and brand.css link; 18 layouts extend it. Hand-built Riverside-shaped fixture dicts in `tests/fixtures/riverside.py` exercise each layout. `tests/conftest.py` provides a single `render_layout(name, ctx) -> Path` helper. Tests assert dimensions (13.333"×7.5"), embedded font names (Roboto + Poppins, no system fallback), and content presence in extracted PDF text. Layout-specific CSS lives inline (`<style>` block per layout); `brand.css` owns only cross-cutting tokens.

**Tech Stack:** Python 3.11+, WeasyPrint 62+, Jinja2 3.1+, PyMuPDF 1.24+ (PDF inspection), pytest 8+. Fonts: Roboto (Apache 2.0) + Poppins (OFL), both committed as binary `.ttf` files.

**Reference:** Design spec at `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md`. Parent spec at `docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md`.

---

## File Structure

**New files (skill bundle):**
- `skill_assets/fonts/Roboto-Bold.ttf`
- `skill_assets/fonts/Roboto-Regular.ttf`
- `skill_assets/fonts/Poppins-Light.ttf`
- `skill_assets/fonts/Poppins-Regular.ttf`
- `skill_assets/fonts/Poppins-Medium.ttf`
- `skill_assets/layouts/brand.css`
- `skill_assets/layouts/base.html`
- `skill_assets/layouts/cover.html`
- `skill_assets/layouts/exec_summary.html`
- `skill_assets/layouts/understanding.html`
- `skill_assets/layouts/creative_vision.html`
- `skill_assets/layouts/showcase_hero.html`
- `skill_assets/layouts/showcase_2up.html`
- `skill_assets/layouts/showcase_3up.html`
- `skill_assets/layouts/showcase_4up.html`
- `skill_assets/layouts/showcase_fullbleed.html`
- `skill_assets/layouts/scope.html`
- `skill_assets/layouts/sample_of_work.html`
- `skill_assets/layouts/case_study.html`
- `skill_assets/layouts/investment_tiered.html`
- `skill_assets/layouts/investment_single.html`
- `skill_assets/layouts/add_ons.html`
- `skill_assets/layouts/terms.html`
- `skill_assets/layouts/sign_block.html`
- `skill_assets/layouts/about.html`

**New files (tests):**
- `tests/conftest.py`
- `tests/fixtures/__init__.py`
- `tests/fixtures/riverside.py`
- `tests/test_layouts.py`

**Modified files:** none. (Plan 1's `tests/test_repo_structure.py` must keep passing on Python 3.11.)

---

## Phase A — Prerequisites

### Task 1: Install Python 3.11+ and recreate venv

**Files:**
- Modify (local environment): system Python toolchain
- Verify: `pyproject.toml` resolves; `tests/test_repo_structure.py` green on 3.11

- [ ] **Step 1: Confirm current Python version is < 3.11**

Run: `python3 --version`
Expected: `Python 3.9.x` (or anything below 3.11). If already 3.11+, skip to Step 4.

- [ ] **Step 2: Install Python 3.11+ via the python.org installer**

Pause and ask Daniel which install method he prefers. Default recommendation (no Homebrew on this machine): the official python.org installer.

1. Open https://www.python.org/downloads/macos/ in a browser.
2. Download the latest `python-3.11.x-macos11.pkg` (or `3.12`/`3.13` if Daniel prefers).
3. Run the installer.

Alternate paths if Daniel prefers them:
- `pyenv install 3.11.9 && pyenv local 3.11.9` (requires pyenv)
- Install Homebrew first, then `brew install python@3.11`

- [ ] **Step 3: Verify the install**

Run: `python3.11 --version`
Expected: `Python 3.11.x` (or whichever 3.11+ was installed).

- [ ] **Step 4: Recreate the venv at the repo root**

Run from the repo root (`/Users/Daniel-Admin/Documents/Claude/Projects/proposal-build`):

```bash
rm -rf .venv 2>/dev/null
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Expected: `Successfully installed ... weasyprint-62.x ... jinja2-3.x ... pymupdf-1.24.x ... pytest-8.x ...` (full dep tree resolves with no errors).

- [ ] **Step 5: Verify Plan 1's smoke test passes on 3.11**

Run: `pytest tests/test_repo_structure.py -v`
Expected: 5 passed. (The 5 tests are `test_top_level_layout`, `test_projects_layout`, `test_template_project_subfolders`, `test_riverside_project_has_inbox`, `test_skill_assets_subfolders`.)

- [ ] **Step 6: Verify WeasyPrint renders a trivial PDF (smoke test for system libs)**

Run:

```bash
python -c "from weasyprint import HTML; HTML(string='<h1>ok</h1>').write_pdf('/tmp/_wp_smoke.pdf'); print('OK')"
```

Expected: `OK` printed; no errors. (WeasyPrint depends on system libs like Pango/Cairo; this catches missing system deps before they fail in real tests. If this errors, follow the WeasyPrint macOS install guide at https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#macos before continuing.)

- [ ] **Step 7: Commit (no code changed; this task only modifies the local environment)**

No commit. The venv is gitignored. Move on to Task 2.

---

## Phase B — Foundation

### Task 2: Add Roboto + Poppins fonts to `skill_assets/fonts/`

**Files:**
- Create: `skill_assets/fonts/Roboto-Bold.ttf`
- Create: `skill_assets/fonts/Roboto-Regular.ttf`
- Create: `skill_assets/fonts/Poppins-Light.ttf`
- Create: `skill_assets/fonts/Poppins-Regular.ttf`
- Create: `skill_assets/fonts/Poppins-Medium.ttf`
- Test: `tests/test_fonts_present.py` (created in this task)

- [ ] **Step 1: Write the failing test**

Create `tests/test_fonts_present.py`:

```python
"""Asserts the 5 required font files exist in skill_assets/fonts/.

Per spec §3 / parent spec §3 / Plan 2 design §5, fonts MUST be embedded
in the skill bundle and never loaded from the system. This test catches
accidental deletion or wrong filename.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FONTS = REPO_ROOT / "skill_assets" / "fonts"

REQUIRED_FONTS = [
    "Roboto-Bold.ttf",
    "Roboto-Regular.ttf",
    "Poppins-Light.ttf",
    "Poppins-Regular.ttf",
    "Poppins-Medium.ttf",
]


def test_required_fonts_present():
    missing = [f for f in REQUIRED_FONTS if not (FONTS / f).is_file()]
    assert not missing, f"Missing fonts: {missing}"


def test_fonts_are_nonempty():
    for f in REQUIRED_FONTS:
        path = FONTS / f
        assert path.stat().st_size > 1000, f"{f} suspiciously small ({path.stat().st_size} bytes)"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fonts_present.py -v`
Expected: FAIL — `Missing fonts: ['Roboto-Bold.ttf', ...]`.

- [ ] **Step 3: Download font families from Google Fonts**

Open in a browser:
1. https://fonts.google.com/specimen/Roboto → "Get font" → "Download all"
2. https://fonts.google.com/specimen/Poppins → "Get font" → "Download all"

Each downloads a `.zip` containing the family.

- [ ] **Step 4: Extract the 5 specific weights to `skill_assets/fonts/`**

From the Roboto zip, locate the static (non-variable) font files. The Roboto zip from Google Fonts ships variable fonts plus a `static/` subdirectory with single-weight `.ttf` files. Copy these two files to `skill_assets/fonts/`:

- `static/Roboto-Bold.ttf` → `skill_assets/fonts/Roboto-Bold.ttf`
- `static/Roboto-Regular.ttf` → `skill_assets/fonts/Roboto-Regular.ttf`

From the Poppins zip, copy these three files (Poppins ships individual weight files at the top level):

- `Poppins-Light.ttf` → `skill_assets/fonts/Poppins-Light.ttf`
- `Poppins-Regular.ttf` → `skill_assets/fonts/Poppins-Regular.ttf`
- `Poppins-Medium.ttf` → `skill_assets/fonts/Poppins-Medium.ttf`

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_fonts_present.py -v`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/fonts/ tests/test_fonts_present.py
git commit -m "$(cat <<'EOF'
feat(plan-2): embed Roboto + Poppins fonts in skill bundle

Adds the 5 font files required by the design spec to skill_assets/fonts/.
Test asserts all 5 files exist and are non-trivial in size. Fonts are
embedded (never loaded from the system) per spec §3 — Claude's code
sandbox does not guarantee specific system fonts, so embedding prevents
silent font substitution at generation time.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Write `skill_assets/layouts/brand.css`

**Files:**
- Create: `skill_assets/layouts/brand.css`
- Test: `tests/test_brand_css.py` (created in this task)

- [ ] **Step 1: Write the failing test**

Create `tests/test_brand_css.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_brand_css.py -v`
Expected: FAIL — `brand.css` does not exist.

- [ ] **Step 3: Write `brand.css`**

Create `skill_assets/layouts/brand.css`:

```css
/* St. Nick's Proposal Builder — locked brand tokens
 *
 * This file is the single source of truth for brand colors, fonts,
 * type scale, spacing scale, and page geometry. Layouts may add
 * layout-specific styles inline but must NEVER write hex colors,
 * raw font names, or raw pixel sizes — always use the tokens here.
 *
 * See docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md
 * for design rationale.
 */

/* ===== Embedded fonts ===== */
@font-face {
  font-family: "Roboto";
  src: url("../fonts/Roboto-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
}
@font-face {
  font-family: "Roboto";
  src: url("../fonts/Roboto-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: "Poppins";
  src: url("../fonts/Poppins-Light.ttf") format("truetype");
  font-weight: 300;
  font-style: normal;
}
@font-face {
  font-family: "Poppins";
  src: url("../fonts/Poppins-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: "Poppins";
  src: url("../fonts/Poppins-Medium.ttf") format("truetype");
  font-weight: 500;
  font-style: normal;
}

/* ===== Design tokens ===== */
:root {
  /* Colors — locked by parent spec §3 */
  --color-red: #B31315;       /* Headlines, accents, CTAs ONLY — never block fill */
  --color-charcoal: #1C1C1C;  /* Body on light backgrounds */
  --color-gray: #555555;      /* Captions, secondary text */
  --color-navy: #12355B;      /* Secondary accent */
  --color-light: #ECEFF1;     /* Body on dark backgrounds; light fills */

  /* Font families */
  --font-heading: "Roboto", sans-serif;
  --font-body: "Poppins", sans-serif;

  /* Typographic scale — geometric ~1.25 minor third, base = 12pt body */
  --text-xs:   9pt;
  --text-sm:   11pt;
  --text-base: 12pt;
  --text-lg:   15pt;
  --text-xl:   19pt;
  --text-2xl:  24pt;
  --text-3xl:  30pt;

  /* Spacing scale — 4pt grid */
  --space-1: 4pt;
  --space-2: 8pt;
  --space-3: 12pt;
  --space-4: 16pt;
  --space-5: 20pt;
  --space-6: 24pt;
  --space-7: 28pt;
  --space-8: 32pt;
}

/* ===== Page geometry ===== */
@page {
  size: 13.333in 7.5in;          /* 16:9 widescreen, landscape */
  margin: var(--space-6);        /* Default margin; layouts may override */
}

/* ===== Global element rules ===== */
html, body {
  margin: 0;
  padding: 0;
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-base);
  color: var(--color-charcoal);
  line-height: 1.45;
  background: white;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--color-charcoal);
  margin: 0 0 var(--space-3) 0;
  line-height: 1.15;
  letter-spacing: -0.01em;
}

h1 { font-size: var(--text-3xl); color: var(--color-red); }
h2 { font-size: var(--text-2xl); }
h3 { font-size: var(--text-xl); }
h4 { font-size: var(--text-lg); }
h5 { font-size: var(--text-base); }
h6 { font-size: var(--text-sm); text-transform: uppercase; letter-spacing: 0.08em; }

p {
  margin: 0 0 var(--space-3) 0;
}

ul, ol {
  margin: 0 0 var(--space-3) 0;
  padding-left: var(--space-5);
}

li {
  margin: 0 0 var(--space-1) 0;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}

table {
  border-collapse: collapse;
  width: 100%;
  font-size: var(--text-sm);
}

th, td {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-light);
}

th {
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--color-charcoal);
  text-transform: uppercase;
  font-size: var(--text-xs);
  letter-spacing: 0.05em;
}

/* Utility: caption text */
.caption {
  font-size: var(--text-xs);
  color: var(--color-gray);
  font-weight: 300;
}

/* Utility: small uppercase label */
.label {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-gray);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_brand_css.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/layouts/brand.css tests/test_brand_css.py
git commit -m "$(cat <<'EOF'
feat(plan-2): write brand.css with design tokens

Locks colors, fonts (@font-face for all 5 weights), type scale, spacing
scale, page geometry (13.333" × 7.5"), and global element rules.
No reusable component classes (deferred per design §4). Test asserts
the locked tokens are present so accidental edits surface immediately.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Write `skill_assets/layouts/base.html`

**Files:**
- Create: `skill_assets/layouts/base.html`
- Test: `tests/test_base_html.py` (created in this task)

- [ ] **Step 1: Write the failing test**

Create `tests/test_base_html.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_base_html.py -v`
Expected: FAIL — `base.html` does not exist.

- [ ] **Step 3: Write `base.html`**

Create `skill_assets/layouts/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}St. Nick's Proposal{% endblock %}</title>
  {% block layout_version %}{% endblock %}
  <link rel="stylesheet" href="brand.css">
  {% block extra_head %}{% endblock %}
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_base_html.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/layouts/base.html tests/test_base_html.py
git commit -m "$(cat <<'EOF'
feat(plan-2): add Jinja2 base.html template

Single source of <head> for all 18 layouts. Exposes blocks: title,
layout_version (per parent spec §7), extra_head (escape hatch), and
content. Layouts extend this and have no head boilerplate of their own.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Write `tests/conftest.py` with `render_layout` helper

**Files:**
- Create: `tests/conftest.py`

This is infrastructure that later tasks consume; it has no failing-test step. Verification is "later layout tests can render."

- [ ] **Step 1: Write `tests/conftest.py`**

Create `tests/conftest.py`:

```python
"""Test fixtures and helpers shared across the layout test suite.

Plan 2 deliberately keeps rendering glue inside tests/ — Plan 3 will
write the production render pipeline at skill_assets/generate.py.
This helper exists only to drive the layout tests.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

REPO_ROOT = Path(__file__).resolve().parent.parent
LAYOUTS_DIR = REPO_ROOT / "skill_assets" / "layouts"
OUTPUT_DIR = REPO_ROOT / "tests" / "_output"


@pytest.fixture(scope="session")
def jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )


@pytest.fixture(scope="session")
def render_layout(jinja_env: Environment):
    """Render a single layout HTML file to PDF and return the path.

    Args:
        layout_name: filename stem under skill_assets/layouts/, e.g. "cover".
        ctx: Python dict passed to Jinja2 as the rendering context.

    Returns:
        Path to the rendered PDF file in tests/_output/{layout_name}.pdf.

    Side effects:
        Writes the PDF; creates tests/_output/ if missing.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _render(layout_name: str, ctx: dict[str, Any]) -> Path:
        template = jinja_env.get_template(f"{layout_name}.html")
        html_string = template.render(**ctx)
        out = OUTPUT_DIR / f"{layout_name}.pdf"
        # base_url tells WeasyPrint how to resolve <link href="brand.css">
        # and brand.css's relative ../fonts/ urls.
        HTML(string=html_string, base_url=str(LAYOUTS_DIR)).write_pdf(
            target=str(out)
        )
        return out

    return _render
```

- [ ] **Step 2: Smoke-test the helper renders a trivial layout**

Create a temporary trivial layout to verify the helper plumbing works end-to-end. From the repo root:

```bash
cat > /tmp/_smoke_layout.html <<'EOF'
{% extends "base.html" %}
{% block content %}
<h1>{{ project_name }}</h1>
<p>{{ tagline }}</p>
{% endblock %}
EOF
cp /tmp/_smoke_layout.html skill_assets/layouts/_smoke.html

python -c "
import sys
sys.path.insert(0, 'tests')
from conftest import LAYOUTS_DIR, OUTPUT_DIR
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML
env = Environment(loader=FileSystemLoader(str(LAYOUTS_DIR)), autoescape=True, undefined=StrictUndefined)
t = env.get_template('_smoke.html')
html = t.render(project_name='Smoke', tagline='OK')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HTML(string=html, base_url=str(LAYOUTS_DIR)).write_pdf(str(OUTPUT_DIR / '_smoke.pdf'))
print('Smoke OK:', (OUTPUT_DIR / '_smoke.pdf').stat().st_size, 'bytes')
"

rm skill_assets/layouts/_smoke.html
rm -f tests/_output/_smoke.pdf
```

Expected: `Smoke OK: <some-number> bytes` printed; no errors. The number should be > 5000 bytes (a real PDF with embedded fonts).

If this fails: fix `conftest.py` (or `brand.css` / `base.html`) before continuing — the layout tasks will fail in confusing ways otherwise.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "$(cat <<'EOF'
feat(plan-2): add render_layout test helper

tests/conftest.py exposes a render_layout(layout_name, ctx) -> Path
fixture that loads the named Jinja2 template from skill_assets/layouts/,
renders with the given ctx, pipes through WeasyPrint, and returns the
output path. Used by the parametrized layout tests in test_layouts.py.

StrictUndefined is on so missing ctx keys raise instead of silently
rendering empty strings — catches fixture/layout drift early.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Scaffold `tests/fixtures/riverside.py`

**Files:**
- Create: `tests/fixtures/__init__.py`
- Create: `tests/fixtures/riverside.py`

This task creates the empty fixture module. Each of the 18 layout tasks will append its fixture to `riverside.py`.

- [ ] **Step 1: Create `tests/fixtures/__init__.py`**

```bash
touch tests/fixtures/__init__.py
```

- [ ] **Step 2: Write `tests/fixtures/riverside.py`**

Create `tests/fixtures/riverside.py`:

```python
"""Hand-built Jinja2 contexts for each of the 18 Plan 2 layouts.

Anchored on the Downtown Riverside MetroLink project where data exists.
Where Riverside doesn't yet have content (no case study selected, no
past-work library populated), values are plausible-but-fabricated and
consistent with St. Nick's voice and existing examples.

Plan 3's parsers will produce dicts of the same shape from real
Brief.md + Scope Worksheet.xlsx + rendering folders. Until then, this
file IS the data.

Filenames in *_image / *_renderings keys are paths relative to the
repo root, used by layouts as <img src="file://..."> URLs WeasyPrint
will resolve at render time.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RIVERSIDE = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"
RENDERINGS_DIR = RIVERSIDE / "02 - Renderings"
BASE_SCOPE = RENDERINGS_DIR / "Base Scope"
ENHANCEMENTS = RENDERINGS_DIR / "Enhancements"


def _path(d: Path, name: str) -> str:
    """Return a file:// URL for an absolute repo-relative rendering path.

    WeasyPrint resolves these at render time. We return file:// URLs
    rather than relative paths because the layouts live in
    skill_assets/layouts/ and renderings live elsewhere — base_url
    resolution would not span those trees.
    """
    p = d / name
    return p.as_uri()


# Common project-wide values reused by multiple fixtures.
PROJECT = {
    "client_company": "Riverside County Transportation Commission (RCTC)",
    "client_short": "RCTC",
    "decision_maker": "Jacklyn Moreno",
    "decision_maker_title": "Capital Projects Manager",
    "project_name": "Downtown Riverside MetroLink — 2026 Holiday Program",
    "project_short": "Riverside MetroLink",
    "project_year": 2026,
    "presenter_name": "Jonathan Yang",
    "presenter_email": "jonathan@st-nicks.com",
    "presenter_phone": "(562) 438-0017",
    "design_phrase": "Holiday Express",
    "voice": "civic",
}


# Each layout's fixture is appended below by its task.
# (Layouts are added in the order of the slide catalog.)
```

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/__init__.py tests/fixtures/riverside.py
git commit -m "$(cat <<'EOF'
feat(plan-2): scaffold tests/fixtures/riverside.py

Empty module with shared PROJECT dict and rendering-path helper.
Subsequent tasks append a per-layout ctx dict to this file.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Scaffold `tests/test_layouts.py` with assertion helpers

**Files:**
- Create: `tests/test_layouts.py`

This task creates the parametrized test infrastructure with an empty parametrize list. Each layout task will append one entry. The full test suite passes only when all 18 layouts are built and added.

- [ ] **Step 1: Write `tests/test_layouts.py`**

Create `tests/test_layouts.py`:

```python
"""Parametrized layout tests — one entry per layout in skill_assets/layouts/.

For each (layout_name, ctx, expected_text) tuple, the test:
- renders the layout to PDF via the render_layout fixture,
- asserts the PDF has 1 page at 13.333" × 7.5" (within 1pt),
- asserts both Roboto and Poppins are listed as embedded fonts
  (catches the silent system-font-fallback failure mode),
- asserts every string in expected_text appears in the extracted
  PDF text (catches blank-page and missing-content failures).

Each layout task in Plan 2 appends to LAYOUT_CASES below.
"""
from __future__ import annotations

from pathlib import Path

import fitz  # pymupdf
import pytest

# Page dimensions in PDF points (1pt = 1/72in).
EXPECTED_WIDTH_PT = 13.333 * 72   # 959.976 pt
EXPECTED_HEIGHT_PT = 7.5 * 72     # 540.000 pt
DIMENSION_TOLERANCE_PT = 1.0


def _font_names(doc: fitz.Document) -> list[str]:
    """Collect basefont names across all pages.

    pymupdf's get_fonts() returns tuples; index 3 is the basefont name,
    e.g. 'ABCDEF+Roboto-Bold' (subsetted) or 'Roboto-Bold' (full).
    """
    names: list[str] = []
    for page in doc:
        for entry in page.get_fonts():
            names.append(entry[3])
    return names


def _assert_font_family_present(doc: fitz.Document, family: str) -> None:
    names = _font_names(doc)
    assert any(family in n for n in names), (
        f"No embedded font with '{family}' in its name. "
        f"Got: {names}. WeasyPrint may have fallen back to a system font — "
        f"check brand.css @font-face urls and font file presence."
    )


def _assert_dimensions(doc: fitz.Document) -> None:
    rect = doc[0].rect
    assert abs(rect.width - EXPECTED_WIDTH_PT) <= DIMENSION_TOLERANCE_PT, (
        f"PDF width {rect.width:.2f}pt — expected {EXPECTED_WIDTH_PT:.2f}pt"
    )
    assert abs(rect.height - EXPECTED_HEIGHT_PT) <= DIMENSION_TOLERANCE_PT, (
        f"PDF height {rect.height:.2f}pt — expected {EXPECTED_HEIGHT_PT:.2f}pt"
    )


def _assert_text_present(doc: fitz.Document, expected: list[str]) -> None:
    text = "\n".join(page.get_text() for page in doc)
    for fragment in expected:
        assert fragment in text, (
            f"Expected fragment {fragment!r} not found in extracted PDF text."
        )


# (layout_name, fixture_attribute_name, list_of_text_fragments_that_must_appear)
# Each Plan 2 layout task appends one entry here.
LAYOUT_CASES: list[tuple[str, str, list[str]]] = [
    # appended per task
]


@pytest.mark.parametrize("layout_name,ctx_attr,expected_text", LAYOUT_CASES)
def test_layout_renders(layout_name, ctx_attr, expected_text, render_layout):
    # pytest adds tests/ to sys.path because there's no tests/__init__.py
    # (Plan 1's pattern), so 'fixtures' is importable as a top-level package.
    from fixtures import riverside
    ctx = getattr(riverside, ctx_attr)
    pdf_path: Path = render_layout(layout_name, ctx)

    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 5000, "PDF suspiciously small"

    with fitz.open(pdf_path) as doc:
        assert doc.page_count == 1, f"Expected 1 page, got {doc.page_count}"
        _assert_dimensions(doc)
        _assert_font_family_present(doc, "Roboto")
        _assert_font_family_present(doc, "Poppins")
        _assert_text_present(doc, expected_text)


def test_all_eighteen_layouts_rendered():
    """After the suite runs, all 18 PDFs must exist for the eyeball pass.

    Skipped if LAYOUT_CASES is incomplete (Plan 2 in progress).
    """
    if len(LAYOUT_CASES) < 18:
        pytest.skip(f"Plan 2 in progress: {len(LAYOUT_CASES)}/18 layouts present.")

    output_dir = Path(__file__).resolve().parent / "_output"
    expected_pdfs = {f"{name}.pdf" for name, _, _ in LAYOUT_CASES}
    actual_pdfs = {p.name for p in output_dir.glob("*.pdf")}
    missing = expected_pdfs - actual_pdfs
    assert not missing, f"Missing rendered PDFs: {missing}"
```

- [ ] **Step 2: Run the test to confirm it skips cleanly**

Run: `pytest tests/test_layouts.py -v`
Expected:
- `test_layout_renders` does not appear (parametrize list empty).
- `test_all_eighteen_layouts_rendered` SKIPPED with reason "Plan 2 in progress: 0/18 layouts present."

- [ ] **Step 3: Commit**

```bash
git add tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2): scaffold parametrized layout test suite

tests/test_layouts.py defines the test contract for every layout —
renders to PDF, asserts dimensions (13.333"×7.5"), asserts both Roboto
and Poppins are embedded (catches silent system-font fallback), and
asserts content presence. LAYOUT_CASES is empty — each subsequent task
appends one entry. test_all_eighteen_layouts_rendered skips until all
18 are present, gating the manual eyeball pass.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — Layouts (TDD per layout)

> **Pattern for every layout task in this phase:**
> 1. Append fixture dict to `tests/fixtures/riverside.py`.
> 2. Append `(layout_name, ctx_attr, expected_text)` tuple to `LAYOUT_CASES` in `tests/test_layouts.py`.
> 3. Run `pytest tests/test_layouts.py::test_layout_renders -v` — confirm new test fails (template not found).
> 4. Write the layout HTML file under `skill_assets/layouts/`.
> 5. Run the test again — confirm it passes.
> 6. Commit the three files together.

### Task 8: `cover.html`

**Files:**
- Modify: `tests/fixtures/riverside.py` (append `cover_ctx`)
- Modify: `tests/test_layouts.py` (append to `LAYOUT_CASES`)
- Create: `skill_assets/layouts/cover.html`

- [ ] **Step 1: Append fixture to `tests/fixtures/riverside.py`**

Append at the end of the file:

```python


# ===== Slide 1 — Cover =====
cover_ctx = {
    **PROJECT,
    "cover_image": _path(BASE_SCOPE, "Wreaths - Station Entrance 01.png"),
    "presentation_date": "May 2026",
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES` in `tests/test_layouts.py`**

Find `LAYOUT_CASES: list[tuple[str, str, list[str]]] = [` and add the entry inside the list:

```python
LAYOUT_CASES: list[tuple[str, str, list[str]]] = [
    ("cover", "cover_ctx", [
        "Downtown Riverside MetroLink",
        "Riverside County Transportation Commission",
        "Holiday Express",
    ]),
]
```

- [ ] **Step 3: Run the test to confirm it fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v`
Expected: 1 FAILED — `TemplateNotFound: cover.html`.

- [ ] **Step 4: Create `skill_assets/layouts/cover.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ project_name }} — Cover{% endblock %}
{% block extra_head %}
<style>
  @page { margin: 0; }
  body { width: 13.333in; height: 7.5in; }
  .cover {
    position: relative;
    width: 13.333in;
    height: 7.5in;
    overflow: hidden;
  }
  .cover-hero {
    position: absolute;
    top: 0; right: 0; bottom: 0; left: 0;
    background-image: url("{{ cover_image }}");
    background-size: cover;
    background-position: center;
  }
  .cover-scrim {
    position: absolute;
    top: 0; right: 0; bottom: 0; left: 0;
    background: linear-gradient(
      90deg,
      rgba(0,0,0,0.65) 0%,
      rgba(0,0,0,0.35) 45%,
      rgba(0,0,0,0.0) 75%
    );
  }
  .cover-text {
    position: absolute;
    left: var(--space-8);
    bottom: var(--space-8);
    right: 50%;
    color: var(--color-light);
  }
  .cover-eyebrow {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--color-light);
    margin-bottom: var(--space-3);
    opacity: 0.85;
  }
  .cover-title {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 44pt;
    line-height: 1.05;
    color: var(--color-light);
    margin: 0 0 var(--space-4) 0;
    letter-spacing: -0.02em;
  }
  .cover-design-phrase {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-2xl);
    color: var(--color-red);
    margin: 0 0 var(--space-5) 0;
  }
  .cover-meta {
    font-family: var(--font-body);
    font-weight: 300;
    font-size: var(--text-sm);
    color: var(--color-light);
    line-height: 1.6;
  }
  .cover-meta strong {
    font-weight: 500;
  }
</style>
{% endblock %}
{% block content %}
<div class="cover">
  <div class="cover-hero"></div>
  <div class="cover-scrim"></div>
  <div class="cover-text">
    <div class="cover-eyebrow">Holiday Program Proposal · {{ project_year }}</div>
    <h1 class="cover-title">{{ project_name }}</h1>
    <div class="cover-design-phrase">"{{ design_phrase }}"</div>
    <div class="cover-meta">
      Prepared for <strong>{{ client_company }}</strong><br>
      {{ decision_maker }}, {{ decision_maker_title }}<br>
      <br>
      Presented by <strong>{{ presenter_name }}</strong>, St. Nick's<br>
      {{ presentation_date }}
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run the test to confirm it passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v`
Expected: 1 PASSED.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/cover.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2): add cover.html layout

Full-bleed hero with project image, scrim, project name in white,
design phrase in brand red, client + presenter metadata. Per design §3:
hero imagery does the heavy lifting; red used only for accent
(design phrase), never as block fill.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: `exec_summary.html`

**Files:**
- Modify: `tests/fixtures/riverside.py` (append `exec_summary_ctx`)
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/exec_summary.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 2 — Executive Summary =====
exec_summary_ctx = {
    **PROJECT,
    "tier_recommended": "Enhanced",
    "deck_length": 16,
    "investment_total": "$284,500",
    "go_live_date": "November 20, 2026",
    "season_end_date": "January 5, 2027",
    "pillars": [
        {
            "title": "Civic Pride",
            "body": "A holiday program that elevates Riverside as a destination — drawing visitors to a transit hub typically used in transit only.",
        },
        {
            "title": "Operational Discipline",
            "body": "Materials engineered for transit weather and high foot traffic; install and removal coordinated with MetroLink service hours.",
        },
        {
            "title": "Repeatable Investment",
            "body": "Decor designed for multi-season reuse; the 2026 program builds the base for 2027 and 2028 expansions.",
        },
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("exec_summary", "exec_summary_ctx", [
        "Civic Pride",
        "Operational Discipline",
        "Repeatable Investment",
        "Enhanced",
        "$284,500",
    ]),
```

- [ ] **Step 3: Run test → fails with TemplateNotFound**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k exec_summary`

- [ ] **Step 4: Write `skill_assets/layouts/exec_summary.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ project_name }} — Executive Summary{% endblock %}
{% block extra_head %}
<style>
  .es-page {
    display: flex;
    flex-direction: column;
    height: 6.7in;
    gap: var(--space-6);
  }
  .es-header h1 {
    font-size: var(--text-2xl);
    color: var(--color-charcoal);
    margin: 0 0 var(--space-1) 0;
  }
  .es-header .es-eyebrow {
    color: var(--color-red);
  }
  .es-glance {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
    border-top: 2px solid var(--color-red);
    border-bottom: 1px solid var(--color-light);
    padding: var(--space-4) 0;
  }
  .es-glance-cell .label {
    margin-bottom: var(--space-1);
  }
  .es-glance-cell .value {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-xl);
    color: var(--color-charcoal);
  }
  .es-pillars {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-5);
    flex: 1;
  }
  .es-pillar {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  .es-pillar-num {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-3xl);
    color: var(--color-red);
    line-height: 1;
  }
  .es-pillar h3 {
    font-size: var(--text-lg);
    margin: 0;
  }
  .es-pillar p {
    font-size: var(--text-sm);
    color: var(--color-charcoal);
    margin: 0;
  }
</style>
{% endblock %}
{% block content %}
<div class="es-page">
  <div class="es-header">
    <div class="label es-eyebrow">Executive Summary</div>
    <h1>{{ project_short }} — {{ project_year }} Holiday Program</h1>
  </div>

  <div class="es-glance">
    <div class="es-glance-cell">
      <div class="label">Recommended Tier</div>
      <div class="value">{{ tier_recommended }}</div>
    </div>
    <div class="es-glance-cell">
      <div class="label">Investment</div>
      <div class="value">{{ investment_total }}</div>
    </div>
    <div class="es-glance-cell">
      <div class="label">Go Live</div>
      <div class="value">{{ go_live_date }}</div>
    </div>
    <div class="es-glance-cell">
      <div class="label">Season End</div>
      <div class="value">{{ season_end_date }}</div>
    </div>
  </div>

  <div class="es-pillars">
    {% for pillar in pillars %}
    <div class="es-pillar">
      <div class="es-pillar-num">{{ "%02d"|format(loop.index) }}</div>
      <h3>{{ pillar.title }}</h3>
      <p>{{ pillar.body }}</p>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run the test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k exec_summary`
Expected: 1 PASSED.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/exec_summary.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add exec_summary.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: `understanding.html`

**Files:**
- Modify: `tests/fixtures/riverside.py`
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/understanding.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 3 — Our Understanding =====
understanding_ctx = {
    **PROJECT,
    "customer_goals": [
        "Establish RCTC's MetroLink station as a regional holiday destination",
        "Drive non-transit foot traffic to the downtown station and adjoining plaza",
        "Position Riverside County as a leader in civic seasonal programming",
    ],
    "success_criteria": [
        "Measurable increase in evening visitors during the program window",
        "Local press and social media coverage of the activation",
        "Zero MetroLink operational disruptions during install/strike",
    ],
    "constraints": [
        "All decor must clear MetroLink overhead catenary safety envelope",
        "Install and removal must occur outside revenue service hours",
        "Materials must withstand winter Santa Ana wind events",
    ],
    "tier_recommended": "Enhanced",
    "tier_rationale": "Balances civic visual impact with disciplined investment.",
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("understanding", "understanding_ctx", [
        "regional holiday destination",
        "MetroLink overhead catenary",
        "Enhanced",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k understanding`

- [ ] **Step 4: Write `skill_assets/layouts/understanding.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ project_name }} — Our Understanding{% endblock %}
{% block extra_head %}
<style>
  .un-page { display: flex; flex-direction: column; gap: var(--space-5); height: 6.7in; }
  .un-header h1 { font-size: var(--text-2xl); margin: 0 0 var(--space-1) 0; color: var(--color-charcoal); }
  .un-header .label { color: var(--color-red); }
  .un-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: var(--space-4);
    flex: 1;
  }
  .un-box {
    border-top: 3px solid var(--color-navy);
    padding: var(--space-3) 0 0 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  .un-box.tier { border-top-color: var(--color-red); }
  .un-box h3 {
    font-size: var(--text-base);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0;
    color: var(--color-charcoal);
  }
  .un-box ul {
    margin: 0;
    padding-left: var(--space-4);
    font-size: var(--text-sm);
    color: var(--color-charcoal);
  }
  .un-box li { margin-bottom: var(--space-1); }
  .un-tier-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-2xl);
    color: var(--color-red);
    margin: var(--space-1) 0 var(--space-2) 0;
  }
  .un-tier-rationale {
    font-size: var(--text-sm);
    color: var(--color-charcoal);
  }
</style>
{% endblock %}
{% block content %}
<div class="un-page">
  <div class="un-header">
    <div class="label">Our Understanding</div>
    <h1>What success looks like for {{ client_short }}</h1>
  </div>

  <div class="un-grid">
    <div class="un-box">
      <h3>Customer Goals</h3>
      <ul>{% for g in customer_goals %}<li>{{ g }}</li>{% endfor %}</ul>
    </div>

    <div class="un-box">
      <h3>Success Criteria</h3>
      <ul>{% for s in success_criteria %}<li>{{ s }}</li>{% endfor %}</ul>
    </div>

    {% if constraints %}
    <div class="un-box">
      <h3>Constraints</h3>
      <ul>{% for c in constraints %}<li>{{ c }}</li>{% endfor %}</ul>
    </div>
    {% endif %}

    <div class="un-box tier">
      <h3>Recommended Tier</h3>
      <div class="un-tier-name">{{ tier_recommended }}</div>
      <div class="un-tier-rationale">{{ tier_rationale }}</div>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k understanding`
Expected: 1 PASSED.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/understanding.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add understanding.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 11: `creative_vision.html`

**Files:**
- Modify: `tests/fixtures/riverside.py`
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/creative_vision.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 4 — Creative Vision =====
creative_vision_ctx = {
    **PROJECT,
    "hero_image": _path(BASE_SCOPE, "Evening Lighting - Tree Lights Street.png"),
    "creative_direction": (
        "Holiday Express transforms the MetroLink station into the heart of "
        "Riverside's holiday season — a warm, civic-scaled invitation visible "
        "from blocks away. Wreaths and garlands frame each entrance like a "
        "ceremonial gateway; evening lighting turns the platform itself into "
        "the destination after sundown."
    ),
    "phases": [
        {"label": "Welcome", "body": "Wreaths and garlands at every station entrance — the holiday begins at the curb."},
        {"label": "Journey", "body": "Pole banners and evening lighting carry the design language down the platform."},
        {"label": "Arrival", "body": "Walk-through ornament and lit displays at the plaza — a destination, not a transfer."},
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("creative_vision", "creative_vision_ctx", [
        "Holiday Express transforms",
        "Welcome",
        "Journey",
        "Arrival",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k creative_vision`

- [ ] **Step 4: Write `skill_assets/layouts/creative_vision.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ project_name }} — Creative Vision{% endblock %}
{% block extra_head %}
<style>
  @page { margin: 0; }
  body { width: 13.333in; height: 7.5in; }
  .cv-page {
    display: grid;
    grid-template-columns: 7in 6.333in;
    height: 7.5in;
  }
  .cv-hero {
    background-image: url("{{ hero_image }}");
    background-size: cover;
    background-position: center;
  }
  .cv-text {
    padding: var(--space-7) var(--space-6);
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
  }
  .cv-text .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .cv-text h1 {
    font-size: var(--text-2xl);
    color: var(--color-charcoal);
    margin: 0 0 var(--space-3) 0;
  }
  .cv-direction {
    font-size: var(--text-sm);
    color: var(--color-charcoal);
    line-height: 1.55;
  }
  .cv-phases {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    margin-top: var(--space-2);
  }
  .cv-phase {
    display: grid;
    grid-template-columns: 1.4in 1fr;
    align-items: baseline;
    gap: var(--space-3);
    padding-bottom: var(--space-3);
    border-bottom: 1px solid var(--color-light);
  }
  .cv-phase:last-child { border-bottom: 0; padding-bottom: 0; }
  .cv-phase-label {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-red);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .cv-phase-body {
    font-size: var(--text-sm);
    color: var(--color-charcoal);
  }
</style>
{% endblock %}
{% block content %}
<div class="cv-page">
  <div class="cv-hero"></div>
  <div class="cv-text">
    <div>
      <div class="label">Creative Vision</div>
      <h1>"{{ design_phrase }}"</h1>
    </div>
    <div class="cv-direction">{{ creative_direction }}</div>
    <div class="cv-phases">
      {% for phase in phases %}
      <div class="cv-phase">
        <div class="cv-phase-label">{{ phase.label }}</div>
        <div class="cv-phase-body">{{ phase.body }}</div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k creative_vision`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/creative_vision.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add creative_vision.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 12: `showcase_hero.html`

**Files:**
- Modify: `tests/fixtures/riverside.py`
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/showcase_hero.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 5a — Showcase Hero (1–3 items) =====
showcase_hero_ctx = {
    **PROJECT,
    "section_title": "Station Entrances",
    "section_subtitle": "First impressions at the curb",
    "hero_image": _path(BASE_SCOPE, "Wreaths - Station Entrance 01.png"),
    "hero_caption": "Custom-finished wreath, primary station entrance",
    "items": [
        {"name": "Custom Wreaths", "qty": 4, "note": "Each station entrance"},
        {"name": "Garland Swags", "qty": 6, "note": "Spans entrance overhang"},
        {"name": "Pole Wraps", "qty": 8, "note": "Approach from plaza"},
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("showcase_hero", "showcase_hero_ctx", [
        "Station Entrances",
        "Custom Wreaths",
        "Pole Wraps",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_hero`

- [ ] **Step 4: Write `skill_assets/layouts/showcase_hero.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ section_title }}{% endblock %}
{% block extra_head %}
<style>
  .sh-page {
    display: grid;
    grid-template-columns: 8in 5in;
    height: 6.7in;
    gap: var(--space-6);
  }
  .sh-hero {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  .sh-hero-image {
    flex: 1;
    background-image: url("{{ hero_image }}");
    background-size: cover;
    background-position: center;
    border-radius: 4pt;
  }
  .sh-hero-caption { color: var(--color-gray); font-size: var(--text-xs); }
  .sh-side {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    gap: var(--space-4);
  }
  .sh-side .label { color: var(--color-red); }
  .sh-side h1 {
    font-size: var(--text-2xl);
    color: var(--color-charcoal);
    margin: 0 0 var(--space-1) 0;
  }
  .sh-side .sh-subtitle {
    font-size: var(--text-base);
    color: var(--color-gray);
    font-weight: 300;
    margin-bottom: var(--space-4);
  }
  .sh-items {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    border-top: 2px solid var(--color-red);
    padding-top: var(--space-4);
  }
  .sh-item {
    display: grid;
    grid-template-columns: 0.5in 1fr;
    gap: var(--space-3);
    align-items: baseline;
  }
  .sh-item-qty {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-xl);
    color: var(--color-red);
    text-align: right;
  }
  .sh-item-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-charcoal);
  }
  .sh-item-note {
    font-size: var(--text-xs);
    color: var(--color-gray);
  }
</style>
{% endblock %}
{% block content %}
<div class="sh-page">
  <div class="sh-hero">
    <div class="sh-hero-image"></div>
    <div class="sh-hero-caption">{{ hero_caption }}</div>
  </div>

  <div class="sh-side">
    <div>
      <div class="label">Showcase</div>
      <h1>{{ section_title }}</h1>
      <div class="sh-subtitle">{{ section_subtitle }}</div>
    </div>

    <div class="sh-items">
      {% for item in items %}
      <div class="sh-item">
        <div class="sh-item-qty">{{ item.qty }}</div>
        <div>
          <div class="sh-item-name">{{ item.name }}</div>
          <div class="sh-item-note">{{ item.note }}</div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_hero`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/showcase_hero.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add showcase_hero.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 13: `showcase_2up.html`

**Files:**
- Modify: `tests/fixtures/riverside.py`
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/showcase_2up.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 5b — Showcase 2-up (3–6 items) =====
showcase_2up_ctx = {
    **PROJECT,
    "section_title": "Platform & Plaza",
    "section_subtitle": "Where transit meets celebration",
    "tiles": [
        {
            "image": _path(BASE_SCOPE, "Garlands - Decorated Swag - Plaza Fence.png"),
            "name": "Decorated Plaza Fence Garland",
            "note": "Continuous run, plaza-side fence",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Platform Railing.png"),
            "name": "Platform Railing Lighting",
            "note": "Warm-white LED, dusk-to-2am program",
        },
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("showcase_2up", "showcase_2up_ctx", [
        "Platform & Plaza",
        "Decorated Plaza Fence Garland",
        "Platform Railing Lighting",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_2up`

- [ ] **Step 4: Write `skill_assets/layouts/showcase_2up.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ section_title }}{% endblock %}
{% block extra_head %}
<style>
  .sg-page {
    display: flex;
    flex-direction: column;
    height: 6.7in;
    gap: var(--space-4);
  }
  .sg-header { display: flex; align-items: baseline; justify-content: space-between; }
  .sg-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .sg-subtitle { color: var(--color-gray); font-size: var(--text-sm); font-weight: 300; }
  .sg-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-5);
    flex: 1;
  }
  .sg-tile {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  .sg-image {
    flex: 1;
    background-size: cover;
    background-position: center;
    border-radius: 4pt;
  }
  .sg-tile-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-charcoal);
  }
  .sg-tile-note {
    font-size: var(--text-xs);
    color: var(--color-gray);
  }
  .sg-eyebrow { color: var(--color-red); }
</style>
{% endblock %}
{% block content %}
<div class="sg-page">
  <div class="sg-header">
    <div>
      <div class="label sg-eyebrow">Showcase</div>
      <h1>{{ section_title }}</h1>
    </div>
    <div class="sg-subtitle">{{ section_subtitle }}</div>
  </div>

  <div class="sg-grid">
    {% for tile in tiles %}
    <div class="sg-tile">
      <div class="sg-image" style="background-image: url('{{ tile.image }}');"></div>
      <div class="sg-tile-name">{{ tile.name }}</div>
      <div class="sg-tile-note">{{ tile.note }}</div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_2up`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/showcase_2up.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add showcase_2up.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 14: `showcase_3up.html`

Same structure as `showcase_2up.html` with `repeat(3, 1fr)`.

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 5c — Showcase 3-up (6–10 items) =====
showcase_3up_ctx = {
    **PROJECT,
    "section_title": "Pole Decor",
    "section_subtitle": "Length-of-corridor design language",
    "tiles": [
        {
            "image": _path(BASE_SCOPE, "Pole Banner - Happy Holidays.png"),
            "name": "Happy Holidays Pole Banner",
            "note": "Both faces, weather-treated",
        },
        {
            "image": _path(BASE_SCOPE, "Pole Banner Artwork - Holiday Express 01.jpg"),
            "name": "Holiday Express Banner — A",
            "note": "Custom artwork; train-themed",
        },
        {
            "image": _path(BASE_SCOPE, "Pole Banner Artwork - Holiday Express 02.jpg"),
            "name": "Holiday Express Banner — B",
            "note": "Custom artwork; track-themed",
        },
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("showcase_3up", "showcase_3up_ctx", [
        "Pole Decor",
        "Happy Holidays Pole Banner",
        "Holiday Express Banner",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_3up`

- [ ] **Step 4: Write `skill_assets/layouts/showcase_3up.html`**

Identical to `showcase_2up.html` except change `grid-template-columns: repeat(2, 1fr)` to `repeat(3, 1fr)` and reduce gap to `var(--space-4)`. Full file:

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ section_title }}{% endblock %}
{% block extra_head %}
<style>
  .sg-page {
    display: flex;
    flex-direction: column;
    height: 6.7in;
    gap: var(--space-4);
  }
  .sg-header { display: flex; align-items: baseline; justify-content: space-between; }
  .sg-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .sg-subtitle { color: var(--color-gray); font-size: var(--text-sm); font-weight: 300; }
  .sg-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
    flex: 1;
  }
  .sg-tile { display: flex; flex-direction: column; gap: var(--space-2); }
  .sg-image { flex: 1; background-size: cover; background-position: center; border-radius: 4pt; }
  .sg-tile-name { font-family: var(--font-heading); font-weight: 700; font-size: var(--text-sm); color: var(--color-charcoal); }
  .sg-tile-note { font-size: var(--text-xs); color: var(--color-gray); }
  .sg-eyebrow { color: var(--color-red); }
</style>
{% endblock %}
{% block content %}
<div class="sg-page">
  <div class="sg-header">
    <div>
      <div class="label sg-eyebrow">Showcase</div>
      <h1>{{ section_title }}</h1>
    </div>
    <div class="sg-subtitle">{{ section_subtitle }}</div>
  </div>

  <div class="sg-grid">
    {% for tile in tiles %}
    <div class="sg-tile">
      <div class="sg-image" style="background-image: url('{{ tile.image }}');"></div>
      <div class="sg-tile-name">{{ tile.name }}</div>
      <div class="sg-tile-note">{{ tile.note }}</div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_3up`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/showcase_3up.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add showcase_3up.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 15: `showcase_4up.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 5d — Showcase 4-up (overflow) =====
showcase_4up_ctx = {
    **PROJECT,
    "section_title": "Evening Program",
    "section_subtitle": "After-dark activations",
    "tiles": [
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Tree Lights Street.png"),
            "name": "Street Tree Lights",
            "note": "Warm white",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Station Awning 01.png"),
            "name": "Station Awning Lights",
            "note": "Architectural perimeter",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Platform Railing.png"),
            "name": "Platform Railing",
            "note": "Approach lighting",
        },
        {
            "image": _path(BASE_SCOPE, "Evening Lighting - Curb Edge.png"),
            "name": "Curb Edge Lighting",
            "note": "Vehicle-side warmth",
        },
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("showcase_4up", "showcase_4up_ctx", [
        "Evening Program",
        "Street Tree Lights",
        "Curb Edge Lighting",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_4up`

- [ ] **Step 4: Write `skill_assets/layouts/showcase_4up.html`**

Identical to `showcase_3up.html` except `grid-template-columns: repeat(4, 1fr)` and `--text-xs` for the tile name (smaller cells = smaller type). Full file:

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ section_title }}{% endblock %}
{% block extra_head %}
<style>
  .sg-page { display: flex; flex-direction: column; height: 6.7in; gap: var(--space-4); }
  .sg-header { display: flex; align-items: baseline; justify-content: space-between; }
  .sg-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .sg-subtitle { color: var(--color-gray); font-size: var(--text-sm); font-weight: 300; }
  .sg-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); flex: 1; }
  .sg-tile { display: flex; flex-direction: column; gap: var(--space-1); }
  .sg-image { flex: 1; background-size: cover; background-position: center; border-radius: 4pt; }
  .sg-tile-name { font-family: var(--font-heading); font-weight: 700; font-size: var(--text-xs); color: var(--color-charcoal); text-transform: uppercase; letter-spacing: 0.04em; }
  .sg-tile-note { font-size: var(--text-xs); color: var(--color-gray); font-weight: 300; }
  .sg-eyebrow { color: var(--color-red); }
</style>
{% endblock %}
{% block content %}
<div class="sg-page">
  <div class="sg-header">
    <div>
      <div class="label sg-eyebrow">Showcase</div>
      <h1>{{ section_title }}</h1>
    </div>
    <div class="sg-subtitle">{{ section_subtitle }}</div>
  </div>

  <div class="sg-grid">
    {% for tile in tiles %}
    <div class="sg-tile">
      <div class="sg-image" style="background-image: url('{{ tile.image }}');"></div>
      <div class="sg-tile-name">{{ tile.name }}</div>
      <div class="sg-tile-note">{{ tile.note }}</div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_4up`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/showcase_4up.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add showcase_4up.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 16: `showcase_fullbleed.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide 5e — Showcase full-bleed (single hero) =====
showcase_fullbleed_ctx = {
    **PROJECT,
    "section_title": "The Walk-Through Moment",
    "hero_image": _path(ENHANCEMENTS, "Walk-Through Display - Lighted Gift Box.png"),
    "caption": (
        "A 12-foot lighted gift-box arch on the plaza — the photo "
        "moment that gets shared, that brings visitors back."
    ),
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("showcase_fullbleed", "showcase_fullbleed_ctx", [
        "The Walk-Through Moment",
        "12-foot lighted gift-box arch",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_fullbleed`

- [ ] **Step 4: Write `skill_assets/layouts/showcase_fullbleed.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}{{ section_title }}{% endblock %}
{% block extra_head %}
<style>
  @page { margin: 0; }
  body { width: 13.333in; height: 7.5in; }
  .sf-page {
    position: relative;
    width: 13.333in;
    height: 7.5in;
    overflow: hidden;
  }
  .sf-image {
    position: absolute;
    top: 0; right: 0; bottom: 0; left: 0;
    background-image: url("{{ hero_image }}");
    background-size: cover;
    background-position: center;
  }
  .sf-text {
    position: absolute;
    left: var(--space-8);
    bottom: var(--space-8);
    right: var(--space-8);
    color: var(--color-light);
    text-shadow: 0 2pt 12pt rgba(0,0,0,0.6);
  }
  .sf-text .label { color: var(--color-light); opacity: 0.85; margin-bottom: var(--space-2); }
  .sf-text h1 {
    font-size: var(--text-3xl);
    color: var(--color-light);
    margin: 0 0 var(--space-3) 0;
  }
  .sf-text p {
    font-size: var(--text-base);
    color: var(--color-light);
    max-width: 7in;
    margin: 0;
  }
</style>
{% endblock %}
{% block content %}
<div class="sf-page">
  <div class="sf-image"></div>
  <div class="sf-text">
    <div class="label">Showcase</div>
    <h1>{{ section_title }}</h1>
    <p>{{ caption }}</p>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k showcase_fullbleed`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/showcase_fullbleed.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add showcase_fullbleed.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 17: `scope.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+1 — Scope of Work =====
scope_ctx = {
    **PROJECT,
    "inclusions": [
        "Custom-fabricated wreaths (4× station entrances)",
        "Decorated and undecorated garland swags (plaza + street fence)",
        "Pole banner program (8 poles, 2 artwork variants)",
        "Evening lighting program (platform, awning, street tree, curb edge)",
        "Walk-through ornament arch (plaza centerpiece)",
        "Install + strike per MetroLink operational windows",
        "On-site QC walkthrough with RCTC capital projects",
        "Storage between deinstall and 2027 program",
    ],
    "add_ons": [
        "Spiral LED tree at station forecourt",
        "Lighted bell display, plaza-side",
        "Lighted snowflakes on platform railing",
        "Lighted gift-box towers, plaza pair",
    ],
    "exclusions": [
        "MetroLink overhead catenary work (any modifications)",
        "Permanent electrical infrastructure",
        "After-hours security",
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("scope", "scope_ctx", [
        "Scope of Work",
        "Custom-fabricated wreaths",
        "MetroLink overhead catenary",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k "scope and not exec"`

- [ ] **Step 4: Write `skill_assets/layouts/scope.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Scope of Work{% endblock %}
{% block extra_head %}
<style>
  .sc-page { display: flex; flex-direction: column; gap: var(--space-5); height: 6.7in; }
  .sc-header h1 { font-size: var(--text-2xl); margin: 0 0 var(--space-1) 0; color: var(--color-charcoal); }
  .sc-header .label { color: var(--color-red); }
  .sc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-6);
    flex: 1;
  }
  .sc-col h3 {
    font-size: var(--text-base);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 var(--space-3) 0;
    color: var(--color-charcoal);
    padding-bottom: var(--space-2);
    border-bottom: 2px solid var(--color-red);
  }
  .sc-col.add-ons h3 { border-bottom-color: var(--color-navy); }
  .sc-col.exclusions h3 { border-bottom-color: var(--color-gray); }
  .sc-col ul {
    margin: 0;
    padding-left: var(--space-4);
    font-size: var(--text-sm);
  }
  .sc-col li { margin-bottom: var(--space-2); }
  .sc-stacked {
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
  }
</style>
{% endblock %}
{% block content %}
<div class="sc-page">
  <div class="sc-header">
    <div class="label">Scope of Work</div>
    <h1>What's included</h1>
  </div>

  <div class="sc-grid">
    <div class="sc-col">
      <h3>Inclusions</h3>
      <ul>{% for x in inclusions %}<li>{{ x }}</li>{% endfor %}</ul>
    </div>

    <div class="sc-stacked">
      <div class="sc-col add-ons">
        <h3>Optional Add-Ons</h3>
        <ul>{% for x in add_ons %}<li>{{ x }}</li>{% endfor %}</ul>
      </div>
      <div class="sc-col exclusions">
        <h3>Exclusions</h3>
        <ul>{% for x in exclusions %}<li>{{ x }}</li>{% endfor %}</ul>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k "scope and not exec"`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/scope.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add scope.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 18: `sample_of_work.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+2 — Sample of Our Work =====
sample_of_work_ctx = {
    **PROJECT,
    "tiles": [
        # 6 tiles. Riverside doesn't have a populated past_work_library yet
        # (Plan 9), so these reference plausible fixture entries by name and
        # use available rendering files as stand-in imagery.
        {"image": _path(ENHANCEMENTS, "Lighted Bell Display - Scene.png"),
         "name": "The Music Center", "location": "Los Angeles", "year": 2024},
        {"image": _path(ENHANCEMENTS, "Spiral Tree - LED Red Green.png"),
         "name": "Pier 39", "location": "San Francisco", "year": 2023},
        {"image": _path(ENHANCEMENTS, "Walk-Through Display - Lighted Gift Box.png"),
         "name": "Oregon Zoo", "location": "Portland", "year": 2024},
        {"image": _path(BASE_SCOPE, "Wreath - Brick Column Night.jpg"),
         "name": "JFK Terminal 1", "location": "New York", "year": 2023},
        {"image": _path(BASE_SCOPE, "Large Tree - Traditional Ornaments.png"),
         "name": "Sphere — Holiday Tree", "location": "Las Vegas", "year": 2024},
        {"image": _path(BASE_SCOPE, "Walk-Through Ornament - Warm White.png"),
         "name": "LED Angels Program", "location": "Long Beach", "year": 2024},
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("sample_of_work", "sample_of_work_ctx", [
        "Sample of Our Work",
        "Pier 39",
        "Oregon Zoo",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k sample_of_work`

- [ ] **Step 4: Write `skill_assets/layouts/sample_of_work.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Sample of Our Work{% endblock %}
{% block extra_head %}
<style>
  .sw-page { display: flex; flex-direction: column; gap: var(--space-4); height: 6.7in; }
  .sw-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .sw-header .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .sw-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: var(--space-3);
    flex: 1;
  }
  .sw-tile {
    position: relative;
    overflow: hidden;
    border-radius: 4pt;
    background-size: cover;
    background-position: center;
  }
  .sw-tile-overlay {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    padding: var(--space-3);
    background: linear-gradient(0deg, rgba(0,0,0,0.7), rgba(0,0,0,0));
    color: var(--color-light);
  }
  .sw-tile-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-light);
  }
  .sw-tile-meta {
    font-size: var(--text-xs);
    color: var(--color-light);
    opacity: 0.85;
  }
</style>
{% endblock %}
{% block content %}
<div class="sw-page">
  <div class="sw-header">
    <div class="label">Sample of Our Work</div>
    <h1>Recent installations</h1>
  </div>

  <div class="sw-grid">
    {% for tile in tiles %}
    <div class="sw-tile" style="background-image: url('{{ tile.image }}');">
      <div class="sw-tile-overlay">
        <div class="sw-tile-name">{{ tile.name }}</div>
        <div class="sw-tile-meta">{{ tile.location }} · {{ tile.year }}</div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k sample_of_work`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/sample_of_work.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add sample_of_work.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 19: `case_study.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+3 — Case Study =====
case_study_ctx = {
    **PROJECT,
    "case_study_name": "Oregon Zoo — ZooLights",
    "case_study_image": _path(ENHANCEMENTS, "Lighted Gift Box Tower 01.png"),
    "challenge": (
        "Drive evening attendance during the slowest revenue months while "
        "maintaining the zoo's family-friendly identity and operating "
        "within a tight nonprofit budget."
    ),
    "approach": (
        "A modular lighting program designed to grow over three seasons. "
        "Year-one investment in a hero walkway and signature animal lights; "
        "years two and three add adjacent zones using compatible hardware."
    ),
    "outcome": (
        "47% increase in evening attendance during the program window. "
        "Year-three program ran with no new capital outlay. Press coverage "
        "in The Oregonian, KGW, and Travel + Leisure."
    ),
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("case_study", "case_study_ctx", [
        "Oregon Zoo",
        "47% increase in evening attendance",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k case_study`

- [ ] **Step 4: Write `skill_assets/layouts/case_study.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Case Study — {{ case_study_name }}{% endblock %}
{% block extra_head %}
<style>
  .cs-page {
    display: grid;
    grid-template-columns: 5in 1fr;
    gap: var(--space-6);
    height: 6.7in;
  }
  .cs-image {
    background-image: url("{{ case_study_image }}");
    background-size: cover;
    background-position: center;
    border-radius: 4pt;
  }
  .cs-text { display: flex; flex-direction: column; gap: var(--space-4); }
  .cs-text .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .cs-text h1 {
    font-size: var(--text-2xl);
    color: var(--color-charcoal);
    margin: 0 0 var(--space-3) 0;
  }
  .cs-act {
    border-left: 3px solid var(--color-red);
    padding-left: var(--space-4);
  }
  .cs-act h3 {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-red);
    margin: 0 0 var(--space-1) 0;
  }
  .cs-act p {
    font-size: var(--text-sm);
    color: var(--color-charcoal);
    margin: 0;
  }
</style>
{% endblock %}
{% block content %}
<div class="cs-page">
  <div class="cs-image"></div>
  <div class="cs-text">
    <div>
      <div class="label">Case Study</div>
      <h1>{{ case_study_name }}</h1>
    </div>
    <div class="cs-act">
      <h3>Challenge</h3>
      <p>{{ challenge }}</p>
    </div>
    <div class="cs-act">
      <h3>Approach</h3>
      <p>{{ approach }}</p>
    </div>
    <div class="cs-act">
      <h3>Outcome</h3>
      <p>{{ outcome }}</p>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k case_study`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/case_study.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add case_study.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 20: `investment_tiered.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+4a — Investment (3-tier) =====
investment_tiered_ctx = {
    **PROJECT,
    "tiers": [
        {
            "name": "Essential",
            "tagline": "The disciplined civic baseline",
            "price": "$184,500",
            "highlights": [
                "Custom wreaths at every entrance",
                "Garland program — plaza fence",
                "Pole banner program — 8 poles",
                "Standard install + strike",
            ],
        },
        {
            "name": "Enhanced",
            "tagline": "Recommended — civic moment, full evening program",
            "price": "$284,500",
            "is_recommended": True,
            "highlights": [
                "Everything in Essential",
                "Full evening lighting program",
                "Walk-through ornament — plaza centerpiece",
                "Coordinated install per MetroLink ops windows",
            ],
        },
        {
            "name": "Signature",
            "tagline": "A regional destination",
            "price": "$384,500",
            "highlights": [
                "Everything in Enhanced",
                "Spiral LED tree — station forecourt",
                "Lighted bell + gift-box towers",
                "Programmatic snowflake railing",
                "On-site staffing during install + strike",
            ],
        },
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("investment_tiered", "investment_tiered_ctx", [
        "Essential",
        "Enhanced",
        "Signature",
        "$184,500",
        "$284,500",
        "$384,500",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k investment_tiered`

- [ ] **Step 4: Write `skill_assets/layouts/investment_tiered.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Investment{% endblock %}
{% block extra_head %}
<style>
  .it-page { display: flex; flex-direction: column; gap: var(--space-5); height: 6.7in; }
  .it-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .it-header .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .it-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
    flex: 1;
  }
  .it-tier {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-5) var(--space-4);
    border: 1px solid var(--color-light);
    border-radius: 4pt;
    background: white;
  }
  .it-tier.recommended {
    border: 2px solid var(--color-red);
    background: #FFF8F8;
  }
  .it-tier .it-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-xl);
    color: var(--color-charcoal);
    margin: 0;
  }
  .it-tier.recommended .it-name { color: var(--color-red); }
  .it-tier .it-tagline {
    font-size: var(--text-xs);
    color: var(--color-gray);
    font-weight: 300;
    min-height: 2.4em;
  }
  .it-tier .it-price {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-3xl);
    color: var(--color-charcoal);
    margin: var(--space-2) 0;
  }
  .it-tier.recommended .it-price { color: var(--color-red); }
  .it-tier ul {
    margin: 0;
    padding-left: var(--space-4);
    font-size: var(--text-sm);
  }
  .it-tier li { margin-bottom: var(--space-1); }
  .it-recommend-flag {
    align-self: flex-start;
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--color-light);
    background: var(--color-red);
    padding: 4pt 10pt;
    border-radius: 2pt;
  }
</style>
{% endblock %}
{% block content %}
<div class="it-page">
  <div class="it-header">
    <div class="label">Investment</div>
    <h1>Three program tiers — pick the one that fits the moment</h1>
  </div>

  <div class="it-grid">
    {% for tier in tiers %}
    <div class="it-tier {% if tier.is_recommended %}recommended{% endif %}">
      {% if tier.is_recommended %}<span class="it-recommend-flag">Recommended</span>{% endif %}
      <div class="it-name">{{ tier.name }}</div>
      <div class="it-tagline">{{ tier.tagline }}</div>
      <div class="it-price">{{ tier.price }}</div>
      <ul>{% for h in tier.highlights %}<li>{{ h }}</li>{% endfor %}</ul>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k investment_tiered`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/investment_tiered.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add investment_tiered.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 21: `investment_single.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+4b — Investment (single tier) =====
investment_single_ctx = {
    **PROJECT,
    "price": "$284,500",
    "tier_name": "Enhanced",
    "highlights": [
        "Custom wreaths — every station entrance",
        "Garland program — plaza + street fence",
        "Pole banner program — 8 poles, 2 artwork variants",
        "Full evening lighting program — 4 zones",
        "Walk-through ornament — plaza centerpiece",
        "Install + strike per MetroLink ops windows",
        "Storage between deinstall and 2027 program",
    ],
    "totals_breakdown": [
        ("Materials", "$148,200"),
        ("Fabrication", "$52,800"),
        ("Install + strike", "$58,500"),
        ("PM + QC", "$25,000"),
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("investment_single", "investment_single_ctx", [
        "$284,500",
        "Materials",
        "Install + strike",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k investment_single`

- [ ] **Step 4: Write `skill_assets/layouts/investment_single.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Investment{% endblock %}
{% block extra_head %}
<style>
  .is-page { display: grid; grid-template-columns: 6in 1fr; gap: var(--space-6); height: 6.7in; }
  .is-left { display: flex; flex-direction: column; gap: var(--space-4); }
  .is-left .label { color: var(--color-red); }
  .is-left h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .is-tier-block {
    border-top: 3px solid var(--color-red);
    padding-top: var(--space-4);
  }
  .is-tier-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-lg);
    color: var(--color-red);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: var(--space-2);
  }
  .is-price {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 48pt;
    color: var(--color-charcoal);
    line-height: 1;
    margin-bottom: var(--space-3);
  }
  .is-highlights ul { margin: 0; padding-left: var(--space-4); font-size: var(--text-sm); }
  .is-highlights li { margin-bottom: var(--space-1); }
  .is-right { display: flex; flex-direction: column; justify-content: flex-end; gap: var(--space-3); }
  .is-breakdown table { width: 100%; }
  .is-breakdown th, .is-breakdown td { padding: var(--space-2) 0; }
  .is-breakdown td:last-child { text-align: right; font-family: var(--font-heading); font-weight: 700; }
  .is-breakdown caption {
    text-align: left;
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--color-gray);
    margin-bottom: var(--space-2);
  }
</style>
{% endblock %}
{% block content %}
<div class="is-page">
  <div class="is-left">
    <div>
      <div class="label">Investment</div>
      <h1>One program. One number.</h1>
    </div>

    <div class="is-tier-block">
      <div class="is-tier-name">{{ tier_name }} Program</div>
      <div class="is-price">{{ price }}</div>
      <div class="is-highlights">
        <ul>{% for h in highlights %}<li>{{ h }}</li>{% endfor %}</ul>
      </div>
    </div>
  </div>

  <div class="is-right">
    <div class="is-breakdown">
      <table>
        <caption>Cost Breakdown</caption>
        <tbody>
          {% for label, amount in totals_breakdown %}
          <tr><td>{{ label }}</td><td>{{ amount }}</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k investment_single`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/investment_single.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add investment_single.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 22: `add_ons.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+5 — Add-Ons =====
add_ons_ctx = {
    **PROJECT,
    "items": [
        {"id": "E1", "name": "Spiral LED Tree", "location": "Station forecourt",
         "qty": 1, "unit": "ea", "price_each": "$8,500", "total": "$8,500"},
        {"id": "E2", "name": "Lighted Bell Display", "location": "Plaza-side",
         "qty": 4, "unit": "ea", "price_each": "$1,250", "total": "$5,000"},
        {"id": "E3", "name": "Lighted Snowflakes — Railing",
         "location": "Platform north railing", "qty": 12, "unit": "ea",
         "price_each": "$185", "total": "$2,220"},
        {"id": "E4", "name": "Lighted Gift-Box Tower",
         "location": "Plaza, both sides", "qty": 2, "unit": "ea",
         "price_each": "$3,400", "total": "$6,800"},
        {"id": "E5", "name": "Walk-Through Display Refresh",
         "location": "Existing arch", "qty": 1, "unit": "LS",
         "price_each": "$3,200", "total": "$3,200"},
    ],
    "subtotal": "$25,720",
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("add_ons", "add_ons_ctx", [
        "Add-Ons",
        "Spiral LED Tree",
        "$25,720",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k add_ons`

- [ ] **Step 4: Write `skill_assets/layouts/add_ons.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Optional Add-Ons{% endblock %}
{% block extra_head %}
<style>
  .ao-page { display: flex; flex-direction: column; gap: var(--space-4); height: 6.7in; }
  .ao-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .ao-header .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .ao-table { font-size: var(--text-sm); }
  .ao-table th, .ao-table td { padding: var(--space-2) var(--space-3); }
  .ao-table td:nth-child(1) { width: 0.5in; color: var(--color-gray); font-family: var(--font-heading); }
  .ao-table td:nth-child(4),
  .ao-table td:nth-child(5),
  .ao-table td:nth-child(6) { text-align: right; }
  .ao-table tfoot td {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    border-top: 2px solid var(--color-red);
    border-bottom: 0;
    padding-top: var(--space-3);
  }
  .ao-name { font-weight: 500; }
  .ao-loc { color: var(--color-gray); font-size: var(--text-xs); }
</style>
{% endblock %}
{% block content %}
<div class="ao-page">
  <div class="ao-header">
    <div class="label">Optional Add-Ons</div>
    <h1>Beyond the recommended program</h1>
  </div>

  <table class="ao-table">
    <thead>
      <tr>
        <th>#</th>
        <th>Item</th>
        <th>Location</th>
        <th>Qty</th>
        <th>Each</th>
        <th>Total</th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td>{{ item.id }}</td>
        <td>
          <div class="ao-name">{{ item.name }}</div>
        </td>
        <td>
          <div class="ao-loc">{{ item.location }}</div>
        </td>
        <td>{{ item.qty }} {{ item.unit }}</td>
        <td>{{ item.price_each }}</td>
        <td>{{ item.total }}</td>
      </tr>
      {% endfor %}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="5" style="text-align: right;">Add-On Subtotal</td>
        <td style="text-align: right;">{{ subtotal }}</td>
      </tr>
    </tfoot>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k add_ons`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/add_ons.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add add_ons.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 23: `terms.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+6 — Terms & Next Steps =====
terms_ctx = {
    **PROJECT,
    "key_dates": [
        ("Signing deadline", "October 30, 2026"),
        ("Fabrication lock", "August 22, 2026"),
        ("Install begins", "November 10, 2026"),
        ("Go live", "November 20, 2026"),
        ("Season end", "January 5, 2027"),
        ("Strike complete", "January 15, 2027"),
    ],
    "payment_schedule": [
        ("On signing", "30%"),
        ("On fabrication start", "40%"),
        ("On go-live", "30%"),
    ],
    "insurance_summary": (
        "St. Nick's carries $5M general liability and $2M auto. "
        "Certificates issued to RCTC at signing."
    ),
    "change_orders_summary": (
        "Scope or timeline changes after fabrication lock follow our "
        "standard change-order workflow — written approval required, "
        "priced at materials + 35%."
    ),
    "validity_days": 60,
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("terms", "terms_ctx", [
        "Terms & Next Steps",
        "Signing deadline",
        "On fabrication start",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k "terms and not template"`

- [ ] **Step 4: Write `skill_assets/layouts/terms.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Terms & Next Steps{% endblock %}
{% block extra_head %}
<style>
  .tm-page { display: flex; flex-direction: column; gap: var(--space-4); height: 6.7in; }
  .tm-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .tm-header .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .tm-grid {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    grid-template-rows: auto auto;
    gap: var(--space-5);
    flex: 1;
  }
  .tm-block h3 {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-red);
    margin: 0 0 var(--space-2) 0;
  }
  .tm-list { font-size: var(--text-sm); }
  .tm-list .row {
    display: grid;
    grid-template-columns: 1fr auto;
    padding: var(--space-1) 0;
    border-bottom: 1px solid var(--color-light);
  }
  .tm-list .row:last-child { border-bottom: 0; }
  .tm-list .row .v {
    font-family: var(--font-heading);
    font-weight: 700;
  }
  .tm-prose { font-size: var(--text-sm); color: var(--color-charcoal); }
  .tm-validity {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-red);
  }
</style>
{% endblock %}
{% block content %}
<div class="tm-page">
  <div class="tm-header">
    <div class="label">Terms & Next Steps</div>
    <h1>How we get from here to the curb</h1>
  </div>

  <div class="tm-grid">
    <div class="tm-block">
      <h3>Key Dates</h3>
      <div class="tm-list">
        {% for label, value in key_dates %}
        <div class="row"><div>{{ label }}</div><div class="v">{{ value }}</div></div>
        {% endfor %}
      </div>
    </div>

    <div class="tm-block">
      <h3>Payment Schedule</h3>
      <div class="tm-list">
        {% for label, value in payment_schedule %}
        <div class="row"><div>{{ label }}</div><div class="v">{{ value }}</div></div>
        {% endfor %}
      </div>
    </div>

    <div class="tm-block">
      <h3>Insurance</h3>
      <p class="tm-prose">{{ insurance_summary }}</p>
    </div>

    <div class="tm-block">
      <h3>Change Orders</h3>
      <p class="tm-prose">{{ change_orders_summary }}</p>
      <p class="tm-prose"><span class="tm-validity">Proposal valid for {{ validity_days }} days.</span></p>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k "terms and not template"`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/terms.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add terms.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 24: `sign_block.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+7 — Sign Block =====
sign_block_ctx = {
    **PROJECT,
    "client_signer_name": "Jacklyn Moreno",
    "client_signer_title": "Capital Projects Manager",
    "client_signer_org": "Riverside County Transportation Commission",
    "stnicks_signer_name": "Daniel Christenson",
    "stnicks_signer_title": "Director of Sales",
    "stnicks_signer_org": "St. Nick's Holiday Decor",
    "instructions": (
        "Sign and return to your St. Nick's representative. We'll countersign "
        "and return a fully executed copy along with your project kickoff packet."
    ),
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("sign_block", "sign_block_ctx", [
        "Jacklyn Moreno",
        "Daniel Christenson",
        "Sign and return",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k sign_block`

- [ ] **Step 4: Write `skill_assets/layouts/sign_block.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}Acceptance{% endblock %}
{% block extra_head %}
<style>
  .sb-page { display: flex; flex-direction: column; gap: var(--space-6); height: 6.7in; }
  .sb-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .sb-header .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .sb-instructions { font-size: var(--text-sm); color: var(--color-gray); max-width: 9in; }
  .sb-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-7);
    margin-top: var(--space-4);
  }
  .sb-party h3 {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-red);
    margin: 0 0 var(--space-4) 0;
  }
  .sb-line {
    border-bottom: 1px solid var(--color-charcoal);
    height: 0.45in;
    margin-bottom: var(--space-1);
  }
  .sb-row { display: grid; grid-template-columns: 1fr 1.5in; gap: var(--space-4); margin-bottom: var(--space-4); }
  .sb-caption { font-size: var(--text-xs); color: var(--color-gray); text-transform: uppercase; letter-spacing: 0.06em; }
  .sb-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-charcoal);
    margin-top: var(--space-3);
  }
  .sb-title-line { font-size: var(--text-sm); color: var(--color-gray); }
</style>
{% endblock %}
{% block content %}
<div class="sb-page">
  <div class="sb-header">
    <div class="label">Acceptance</div>
    <h1>Authorization to proceed</h1>
  </div>

  <div class="sb-instructions">{{ instructions }}</div>

  <div class="sb-grid">
    <div class="sb-party">
      <h3>Client</h3>
      <div class="sb-row">
        <div>
          <div class="sb-line"></div>
          <div class="sb-caption">Signature</div>
        </div>
        <div>
          <div class="sb-line"></div>
          <div class="sb-caption">Date</div>
        </div>
      </div>
      <div class="sb-name">{{ client_signer_name }}</div>
      <div class="sb-title-line">{{ client_signer_title }}, {{ client_signer_org }}</div>
    </div>

    <div class="sb-party">
      <h3>St. Nick's</h3>
      <div class="sb-row">
        <div>
          <div class="sb-line"></div>
          <div class="sb-caption">Signature</div>
        </div>
        <div>
          <div class="sb-line"></div>
          <div class="sb-caption">Date</div>
        </div>
      </div>
      <div class="sb-name">{{ stnicks_signer_name }}</div>
      <div class="sb-title-line">{{ stnicks_signer_title }}, {{ stnicks_signer_org }}</div>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k sign_block`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/sign_block.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add sign_block.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 25: `about.html`

- [ ] **Step 1: Append fixture**

```python


# ===== Slide N+8 — About St. Nick's =====
about_ctx = {
    **PROJECT,
    "company_blurb": (
        "St. Nick's is a holiday decor design and fabrication studio "
        "serving civic, retail, and hospitality clients across North America "
        "since 2008. We design programs that scale across years, fabricate "
        "in-house, and run our own install crews."
    ),
    "stats": [
        {"value": "17", "label": "Years in business"},
        {"value": "120+", "label": "Annual programs"},
        {"value": "32 states", "label": "Active geography"},
        {"value": "100%", "label": "In-house fabrication"},
    ],
    "team": [
        {"name": "Daniel Christenson", "title": "Director of Sales", "email": "daniel@st-nicks.com"},
        {"name": "Jonathan Yang", "title": "Account Executive", "email": "jonathan@st-nicks.com"},
        {"name": "Stephanie Escobar", "title": "Past Work Curator", "email": "stephanie@st-nicks.com"},
        {"name": "Abigail Lacson", "title": "Brand & Design", "email": "abigail@st-nicks.com"},
    ],
}
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

```python
    ("about", "about_ctx", [
        "St. Nick's",
        "120+",
        "Daniel Christenson",
    ]),
```

- [ ] **Step 3: Run test → fails**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k about`

- [ ] **Step 4: Write `skill_assets/layouts/about.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
{% block title %}About St. Nick's{% endblock %}
{% block extra_head %}
<style>
  .ab-page { display: flex; flex-direction: column; gap: var(--space-5); height: 6.7in; }
  .ab-header h1 { font-size: var(--text-2xl); margin: 0; color: var(--color-charcoal); }
  .ab-header .label { color: var(--color-red); margin-bottom: var(--space-1); }
  .ab-blurb { font-size: var(--text-base); color: var(--color-charcoal); max-width: 11in; }
  .ab-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-5);
    border-top: 2px solid var(--color-red);
    border-bottom: 1px solid var(--color-light);
    padding: var(--space-4) 0;
  }
  .ab-stat-value {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-3xl);
    color: var(--color-red);
    line-height: 1;
  }
  .ab-stat-label {
    font-size: var(--text-xs);
    color: var(--color-gray);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: var(--space-1);
  }
  .ab-team h3 {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-red);
    margin: 0 0 var(--space-3) 0;
  }
  .ab-team-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
    font-size: var(--text-sm);
  }
  .ab-member-name {
    font-family: var(--font-heading);
    font-weight: 700;
    color: var(--color-charcoal);
  }
  .ab-member-title { color: var(--color-gray); }
  .ab-member-email { color: var(--color-charcoal); font-size: var(--text-xs); }
</style>
{% endblock %}
{% block content %}
<div class="ab-page">
  <div class="ab-header">
    <div class="label">About St. Nick's</div>
    <h1>Who we are</h1>
  </div>

  <div class="ab-blurb">{{ company_blurb }}</div>

  <div class="ab-stats">
    {% for stat in stats %}
    <div>
      <div class="ab-stat-value">{{ stat.value }}</div>
      <div class="ab-stat-label">{{ stat.label }}</div>
    </div>
    {% endfor %}
  </div>

  <div class="ab-team">
    <h3>Your Team</h3>
    <div class="ab-team-grid">
      {% for m in team %}
      <div>
        <div class="ab-member-name">{{ m.name }}</div>
        <div class="ab-member-title">{{ m.title }}</div>
        <div class="ab-member-email">{{ m.email }}</div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test → passes**

Run: `pytest tests/test_layouts.py::test_layout_renders -v -k about`

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/about.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "feat(plan-2): add about.html layout

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase D — Verification

### Task 26: Run the full suite and the all-eighteen gate

**Files:** none modified — only verification.

- [ ] **Step 1: Run the entire test suite**

Run: `pytest -v`
Expected:
- `tests/test_repo_structure.py` — 5 passed
- `tests/test_fonts_present.py` — 2 passed
- `tests/test_brand_css.py` — 6 passed
- `tests/test_base_html.py` — 6 passed
- `tests/test_layouts.py::test_layout_renders` — 18 passed (one per layout)
- `tests/test_layouts.py::test_all_eighteen_layouts_rendered` — 1 passed (no longer skipped; gate satisfied)

If any layout test fails, stop and fix it before continuing. The eyeball pass is meaningless if structural assertions don't hold.

- [ ] **Step 2: Confirm all 18 PDFs are in `tests/_output/`**

Run: `ls -1 tests/_output/`
Expected: 18 `.pdf` files matching the 18 layout names.

### Task 27: Manual eyeball pass on all 18 PDFs

**Files:** none modified — this is human review.

- [ ] **Step 1: Open each PDF in macOS Preview (or browser)**

```bash
open tests/_output/*.pdf
```

- [ ] **Step 2: Eyeball each layout against the design guardrails (design spec §3)**

For each PDF, verify:
- Page dimensions look like a 16:9 deck slide.
- Hero imagery (where present) does the heavy lifting; no decorative elements without purpose.
- Red accent is used only for headlines / CTAs / brand-emphasis text — never block fill.
- Whitespace is generous; nothing feels cramped.
- Typography rhythm is consistent across layouts (headings same family/weight; body same family/weight; captions consistent).
- Roboto and Poppins are clearly used (not Times/Helvetica/system fallbacks).

If a layout is structurally correct but visually off (cropping, spacing, weight), note it. Visual refinements are a follow-up commit; the structural test still passes.

- [ ] **Step 3: Make any visual refinements**

For any layout flagged in step 2, refine the inline `<style>` block in that layout file. Re-run `pytest tests/test_layouts.py::test_layout_renders -v -k <layout_name>` to confirm the structural test still passes after the visual change. Eyeball-pass each refinement.

Commit each refinement separately:

```bash
git add skill_assets/layouts/<file>.html
git commit -m "fix(plan-2): polish <layout> visual treatment

<one-line description of the change, e.g. tighten exec_summary pillar
spacing; fix cover scrim falloff>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: Final commit — Plan 2 complete**

Once all 18 are eyeball-approved:

```bash
git log --oneline | head -30
```

Confirm the commit history reads as a coherent sequence of small commits (Plan 2 prereq → fonts → brand.css → base.html → conftest → fixtures scaffold → test scaffold → 18 layout commits → any visual polish commits).

No final all-in-one commit needed — Plan 2's deliverables are already in main.

- [ ] **Step 5: Update project memory (optional)**

If Plan 2's outcome materially changed the project state (e.g., visual decisions worth remembering, deferred items, follow-ups for Plan 3), update `~/.claude/projects/.../memory/project_proposal_builder.md` accordingly.

---

## Plan 2 — Done

After Task 27:
- 18 layout PDFs render reliably from hand-built fixtures.
- Brand system (colors, fonts, type scale, spacing scale, page geometry) is locked in `brand.css` and exercised by tests.
- Structural assertions catch silent font fallback and dimension drift on every render.
- Plan 3 can start: Brief.md + Worksheet.xlsx parsers can produce dicts of the same shape as the riverside fixtures, and existing layouts will render them with no further work.
