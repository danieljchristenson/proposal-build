# Plan 2 Addendum — Typographic Fallback Layouts Implementation Plan

> ⚠️ **SUPERSEDED 2026-05-03 (same day, never executed).** Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-layouts.md`](./2026-05-03-plan-2-prime-master-driven-layouts.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship two typographic alternates (`cover_typographic.html` and `showcase_typographic.html`) so the AE can lead a proposal without a hero photo. Adds Playfair Display to the bundle.

**Architecture:** Two new Jinja2 layouts under `skill_assets/layouts/`, sharing the existing `base.html` and brand tokens. New CSS variable `--font-display` plus 2 `@font-face` blocks for Playfair Display in `brand.css`. The fixtures alias existing `cover_ctx` / `showcase_fullbleed_ctx` so the AE workflow can swap layouts without re-shaping data. The existing all-eighteen gate test is generalized to count whatever's in `LAYOUT_CASES`.

**Tech Stack:** Python 3.11+, Jinja2, WeasyPrint 68.x, pymupdf 1.24+, pytest 8+, fontsource CDN for font sourcing.

---

## File Structure

**Added:**
- `skill_assets/fonts/Playfair-Display-Bold.ttf` — display headline, weight 700
- `skill_assets/fonts/Playfair-Display-Italic.ttf` — italic accents/wordmark, weight 400
- `skill_assets/layouts/cover_typographic.html` — no-photo cover variant
- `skill_assets/layouts/showcase_typographic.html` — no-photo section divider variant

**Modified:**
- `skill_assets/layouts/brand.css` — append 2 `@font-face` blocks; add `--font-display` token
- `tests/test_fonts_present.py` — assert Playfair fonts are present + non-empty
- `tests/test_brand_css.py` — assert Playfair `@font-face` urls + `--font-display` token
- `tests/fixtures/riverside.py` — alias `cover_typographic_ctx = cover_ctx` and `showcase_typographic_ctx = showcase_fullbleed_ctx`
- `tests/test_layouts.py` — append 2 entries to `LAYOUT_CASES`; generalize+rename `test_all_eighteen_layouts_rendered` → `test_all_layouts_rendered`; conditionally assert Playfair embedding for typographic layouts (and skip Roboto for them, since they don't use Roboto)

---

## Phase A — Foundation

### Task 1: Embed Playfair Display fonts in `skill_assets/fonts/`

**Files:**
- Create: `skill_assets/fonts/Playfair-Display-Bold.ttf`
- Create: `skill_assets/fonts/Playfair-Display-Italic.ttf`
- Modify: `tests/test_fonts_present.py` (extend `REQUIRED_FONTS` list)

- [ ] **Step 1: Extend the failing test**

Edit `tests/test_fonts_present.py` to add the two new files to `REQUIRED_FONTS`:

```python
"""Asserts the required font files exist in skill_assets/fonts/.

Per parent spec §3 / Plan 2 design §5 + addendum §5, fonts MUST be
embedded in the skill bundle and never loaded from the system. This
test catches accidental deletion or wrong filename.
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
    "Playfair-Display-Bold.ttf",
    "Playfair-Display-Italic.ttf",
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

Run: `.venv/bin/pytest tests/test_fonts_present.py -v`
Expected: FAIL — `test_required_fonts_present` reports missing `Playfair-Display-Bold.ttf` and `Playfair-Display-Italic.ttf`.

- [ ] **Step 3: Download the Playfair Display fonts from fontsource CDN**

Same source as Plan 2's Roboto/Poppins (verified to ship valid static TTFs with correct family names and weight metadata):

```bash
curl -sSfL -o skill_assets/fonts/Playfair-Display-Bold.ttf \
  "https://cdn.jsdelivr.net/fontsource/fonts/playfair-display@latest/latin-700-normal.ttf"

curl -sSfL -o skill_assets/fonts/Playfair-Display-Italic.ttf \
  "https://cdn.jsdelivr.net/fontsource/fonts/playfair-display@latest/latin-400-italic.ttf"
```

- [ ] **Step 4: Verify the files are valid TTFs**

```bash
ls -la skill_assets/fonts/Playfair-Display-*.ttf
file skill_assets/fonts/Playfair-Display-Bold.ttf
file skill_assets/fonts/Playfair-Display-Italic.ttf
```

Expected:
- Both files exist with size > 30 KB (fontsource ships ~50–100 KB latin subsets)
- `file` reports `TrueType Font data`

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_fonts_present.py -v`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/fonts/Playfair-Display-Bold.ttf skill_assets/fonts/Playfair-Display-Italic.ttf tests/test_fonts_present.py
git commit -m "$(cat <<'EOF'
feat(plan-2-addendum): embed Playfair Display fonts in skill bundle

Adds 2 .ttf files to skill_assets/fonts/ (Playfair Display Bold + Italic)
plus extends test_fonts_present.py to cover them. Sourced from fontsource
CDN — same source as Plan 2's Roboto/Poppins, valid TTFs with correct
family + weight metadata.

Used by the typographic fallback layouts (cover_typographic.html and
showcase_typographic.html, added in subsequent tasks).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Add Playfair `@font-face` + `--font-display` token to `brand.css`

**Files:**
- Modify: `skill_assets/layouts/brand.css` (append 2 `@font-face` blocks; add `--font-display` token)
- Modify: `tests/test_brand_css.py` (assert new font urls + token)

- [ ] **Step 1: Extend the failing tests**

Edit `tests/test_brand_css.py`. Replace `test_font_face_declarations_present` with the extended list, and add a new test for `--font-display`:

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
    # All embedded font weights must have an @font-face that loads from ../fonts/
    for weight_file in [
        "Roboto-Bold.ttf",
        "Roboto-Regular.ttf",
        "Poppins-Light.ttf",
        "Poppins-Regular.ttf",
        "Poppins-Medium.ttf",
        "Playfair-Display-Bold.ttf",
        "Playfair-Display-Italic.ttf",
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


def test_font_display_token_present():
    css = BRAND_CSS.read_text()
    assert "--font-display:" in css
    assert "Playfair Display" in css
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_brand_css.py -v`
Expected: 2 FAIL — `test_font_face_declarations_present` (missing Playfair urls) and `test_font_display_token_present` (token not declared).

- [ ] **Step 3: Update `brand.css`**

In `skill_assets/layouts/brand.css`, after the existing 5 `@font-face` blocks (last one is Poppins-Medium), append two new blocks. Then in the `:root` block, add the `--font-display` token after the existing `--font-body` line.

The exact diff:

```css
/* After the Poppins-Medium @font-face block (around line 42 of current file): */
@font-face {
  font-family: "Playfair Display";
  src: url("../fonts/Playfair-Display-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
}
@font-face {
  font-family: "Playfair Display";
  src: url("../fonts/Playfair-Display-Italic.ttf") format("truetype");
  font-weight: 400;
  font-style: italic;
}
```

And in `:root`, immediately after the existing `--font-body` line, add:

```css
  --font-display: "Playfair Display", serif;
```

The full Font families block in `:root` should now read:

```css
  /* Font families */
  --font-heading: "Roboto", sans-serif;
  --font-body: "Poppins", sans-serif;
  --font-display: "Playfair Display", serif;
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_brand_css.py -v`
Expected: 7 passed.

Also run the whole suite to confirm no regressions:
Run: `.venv/bin/pytest -v`
Expected: 39 passed (38 baseline + the new `test_font_display_token_present`). The existing 18 layouts continue to render correctly — adding 2 new fonts to brand.css doesn't break them because they don't reference Playfair.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/layouts/brand.css tests/test_brand_css.py
git commit -m "$(cat <<'EOF'
feat(plan-2-addendum): add Playfair Display @font-face + --font-display token

Two new @font-face blocks in brand.css (Bold 700 normal, Italic 400)
load Playfair-Display-Bold.ttf and Playfair-Display-Italic.ttf from
skill_assets/fonts/. New token --font-display: "Playfair Display", serif
joins the existing --font-heading and --font-body tokens.

Used by the typographic fallback layouts (added next). Existing 18
layouts are unaffected — they don't reference --font-display.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Generalize the all-layouts gate test

**Files:**
- Modify: `tests/test_layouts.py` (rename + generalize the all-N gate test; conditionally assert Playfair for typographic layouts)

- [ ] **Step 1: Rewrite the gate test and adjust the parametrized renderer**

Edit `tests/test_layouts.py`. Two changes — both at the bottom of the file:

**Change 1** — In `test_layout_renders`, replace the two unconditional Roboto/Poppins assertions with a conditional that handles typographic layouts (which use Playfair + Poppins, NOT Roboto):

Replace lines (the two `_assert_font_family_present` calls inside `with fitz.open(pdf_path) as doc:`):

```python
        _assert_font_family_present(doc, "Roboto")
        _assert_font_family_present(doc, "Poppins")
```

With:

```python
        # Typographic fallback layouts use Playfair Display + Poppins
        # and intentionally do NOT use Roboto. Photo layouts use Roboto + Poppins.
        if "typographic" in layout_name:
            _assert_font_family_present(doc, "Playfair")
            _assert_font_family_present(doc, "Poppins")
        else:
            _assert_font_family_present(doc, "Roboto")
            _assert_font_family_present(doc, "Poppins")
```

**Change 2** — Replace the `test_all_eighteen_layouts_rendered` function entirely with the generalized version:

```python
def test_all_layouts_rendered():
    """After the suite runs, every PDF named in LAYOUT_CASES must exist.

    Skipped if LAYOUT_CASES is empty (planning state).
    """
    if not LAYOUT_CASES:
        pytest.skip("LAYOUT_CASES is empty.")

    output_dir = Path(__file__).resolve().parent / "_output"
    expected_pdfs = {f"{name}.pdf" for name, _, _ in LAYOUT_CASES}
    actual_pdfs = {p.name for p in output_dir.glob("*.pdf")}
    missing = expected_pdfs - actual_pdfs
    assert not missing, f"Missing rendered PDFs: {missing}"
```

- [ ] **Step 2: Run the suite to verify nothing regressed**

Run: `.venv/bin/pytest tests/test_layouts.py -v`
Expected: 19 tests pass (18 layouts × `test_layout_renders` + 1 new `test_all_layouts_rendered`).

The conditional doesn't affect any of the existing 18 layouts because none of their names contain "typographic" — they all hit the `else` branch and continue asserting Roboto + Poppins.

Also run the whole suite:
Run: `.venv/bin/pytest -v`
Expected: 39 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/test_layouts.py
git commit -m "$(cat <<'EOF'
refactor(plan-2-addendum): generalize the all-layouts gate test

Renames test_all_eighteen_layouts_rendered to test_all_layouts_rendered
and removes the hardcoded count gate; future additions to LAYOUT_CASES
extend coverage without touching this test.

Also conditionally asserts Playfair Display embedding for typographic
layouts (which use Playfair + Poppins, not Roboto + Poppins). The
existing 18 layouts hit the unchanged else branch.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — Layouts (TDD per layout)

> **Pattern for both layout tasks:**
> 1. Append fixture alias to `tests/fixtures/riverside.py`.
> 2. Append `(layout_name, ctx_attr, expected_text)` tuple to `LAYOUT_CASES` in `tests/test_layouts.py`.
> 3. Run `pytest tests/test_layouts.py::test_layout_renders -v -k <layout>` — confirm new test fails (template not found).
> 4. Write the layout HTML file under `skill_assets/layouts/`.
> 5. Run the test again — confirm it passes.
> 6. Commit the three files together.

### Task 4: `cover_typographic.html`

**Files:**
- Modify: `tests/fixtures/riverside.py` (append `cover_typographic_ctx` alias)
- Modify: `tests/test_layouts.py` (append to `LAYOUT_CASES`)
- Create: `skill_assets/layouts/cover_typographic.html`

- [ ] **Step 1: Append fixture alias**

Append at the end of `tests/fixtures/riverside.py`:

```python


# ===== Slide 1b — Cover (typographic fallback) =====
# Same data as cover_ctx; only the layout file changes. Aliased rather
# than copied so any future shared edit lands in both at once. Plan 3's
# AE workflow picks cover.html vs cover_typographic.html per project.
cover_typographic_ctx = cover_ctx
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

Find `LAYOUT_CASES: list[tuple[str, str, list[str]]] = [` in `tests/test_layouts.py` and add the entry inside the list, after the existing `("about", ...)` entry:

```python
    ("cover_typographic", "cover_typographic_ctx", [
        "Downtown Riverside MetroLink",
        "Riverside County Transportation Commission",
        "Holiday Express",
        "St. Nick's",                       # wordmark presence
    ]),
```

- [ ] **Step 3: Run test to confirm it fails**

Run: `.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k cover_typographic`
Expected: 1 FAIL — `TemplateNotFound: 'cover_typographic.html' not found`.

- [ ] **Step 4: Create `skill_assets/layouts/cover_typographic.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-03 -->{% endblock %}
{% block title %}{{ project_name }} — Cover{% endblock %}
{% block extra_head %}
<style>
  @page { margin: 0; }
  body { width: 13.333in; height: 7.5in; }
  .ct-page {
    position: relative;
    width: 13.333in;
    height: 7.5in;
    padding: var(--space-7) var(--space-8);
    box-sizing: border-box;
    background: white;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  /* St. Nick's wordmark — top-right */
  .ct-mark {
    position: absolute;
    top: var(--space-7);
    right: var(--space-8);
    text-align: right;
  }
  .ct-mark .ct-mark-name {
    font-family: var(--font-display);
    font-style: italic;
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-red);
    line-height: 1;
  }
  .ct-mark .ct-mark-tag {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 7pt;
    letter-spacing: 0.18em;
    color: var(--color-gray);
    margin-top: var(--space-1);
  }

  /* Top section — issue numeral, headline, rule, design phrase */
  .ct-num {
    font-family: var(--font-display);
    font-style: italic;
    font-weight: 400;
    font-size: var(--text-sm);
    color: var(--color-gray);
    margin-bottom: var(--space-3);
  }
  .ct-h {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: var(--text-3xl);
    line-height: 1.0;
    letter-spacing: -0.018em;
    color: var(--color-charcoal);
    margin: 0;
    max-width: 9in;
  }
  .ct-rule {
    width: 32pt;
    height: 1pt;
    background: var(--color-red);
    margin: var(--space-3) 0 var(--space-2) 0;
  }
  .ct-design-phrase {
    font-family: var(--font-display);
    font-style: italic;
    font-weight: 400;
    font-size: var(--text-lg);
    color: var(--color-red);
  }

  /* Bottom — two-column metadata */
  .ct-bottom {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-7);
    align-items: end;
  }
  .ct-meta-label {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 7pt;
    letter-spacing: 0.18em;
    color: var(--color-gray);
    margin-bottom: var(--space-2);
  }
  .ct-meta-name {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: var(--text-base);
    color: var(--color-charcoal);
    margin-bottom: var(--space-1);
  }
  .ct-meta-line {
    font-family: var(--font-body);
    font-weight: 300;
    font-size: var(--text-sm);
    color: var(--color-charcoal);
    line-height: 1.5;
  }
</style>
{% endblock %}
{% block content %}
<div class="ct-page">
  <div class="ct-mark">
    <div class="ct-mark-name">St. Nick's</div>
    <div class="ct-mark-tag">HOLIDAY DECOR</div>
  </div>

  <div>
    <div class="ct-num">№ {{ project_year }} — A Holiday Program</div>
    <h1 class="ct-h">{{ project_name }}</h1>
    <div class="ct-rule"></div>
    <div class="ct-design-phrase">"{{ design_phrase }}"</div>
  </div>

  <div class="ct-bottom">
    <div>
      <div class="ct-meta-label">PREPARED FOR</div>
      <div class="ct-meta-name">{{ client_company }}</div>
      <div class="ct-meta-line">{{ decision_maker }}, {{ decision_maker_title }}</div>
    </div>
    <div>
      <div class="ct-meta-label">PRESENTED BY</div>
      <div class="ct-meta-name">{{ presenter_name }}</div>
      <div class="ct-meta-line">St. Nick's · {{ presentation_date }}</div>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test to confirm it passes**

Run: `.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k cover_typographic`
Expected: 1 PASSED.

Also run the whole suite to confirm no regressions:
Run: `.venv/bin/pytest -v`
Expected: 40 passed.

The `_output/cover_typographic.pdf` file should be > 5000 bytes (text-heavy layout with embedded Playfair + Poppins subsets — expect ~15–25 KB).

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/cover_typographic.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2-addendum): add cover_typographic.html layout

No-photo cover variant. Same data fields as cover.html — the AE swaps
the layout file when there's no strong hero photo for the project.

Editorial direction inside the existing brand palette: Playfair Display
Bold for the headline, italic numerals + design phrase, thin red rule
(1pt × 32pt). St. Nick's wordmark sits top-right (italic Playfair red
+ tracked-caps "HOLIDAY DECOR" tagline). Bottom-row metadata splits
client and presenter into two columns.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: `showcase_typographic.html`

**Files:**
- Modify: `tests/fixtures/riverside.py` (append `showcase_typographic_ctx` alias)
- Modify: `tests/test_layouts.py` (append to `LAYOUT_CASES`)
- Create: `skill_assets/layouts/showcase_typographic.html`

- [ ] **Step 1: Append fixture alias**

Append at the end of `tests/fixtures/riverside.py`:

```python


# ===== Slide 5f — Showcase (typographic fallback for fullbleed) =====
# Same data as showcase_fullbleed_ctx; only the layout file changes.
# Aliased so a single edit covers both layouts. Plan 3's AE workflow
# picks showcase_fullbleed.html vs showcase_typographic.html per section.
showcase_typographic_ctx = showcase_fullbleed_ctx
```

- [ ] **Step 2: Append to `LAYOUT_CASES`**

Find `LAYOUT_CASES: list[tuple[str, str, list[str]]] = [` and add the entry after the `("cover_typographic", ...)` entry from Task 4:

```python
    ("showcase_typographic", "showcase_typographic_ctx", [
        "Walk-Through Moment",                  # the section_title
        "12-foot lighted gift-box arch",        # the caption
        "St. Nick's",                           # wordmark presence
    ]),
```

- [ ] **Step 3: Run test to confirm it fails**

Run: `.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k showcase_typographic`
Expected: 1 FAIL — `TemplateNotFound: 'showcase_typographic.html' not found`.

- [ ] **Step 4: Create `skill_assets/layouts/showcase_typographic.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-03 -->{% endblock %}
{% block title %}{{ section_title }}{% endblock %}
{% block extra_head %}
<style>
  @page { margin: 0; }
  body { width: 13.333in; height: 7.5in; }
  .st-page {
    position: relative;
    width: 13.333in;
    height: 7.5in;
    padding: var(--space-8) var(--space-8);
    box-sizing: border-box;
    background: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  /* St. Nick's wordmark — top-right (same treatment as cover_typographic) */
  .st-mark {
    position: absolute;
    top: var(--space-7);
    right: var(--space-8);
    text-align: right;
  }
  .st-mark .st-mark-name {
    font-family: var(--font-display);
    font-style: italic;
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-red);
    line-height: 1;
  }
  .st-mark .st-mark-tag {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 7pt;
    letter-spacing: 0.18em;
    color: var(--color-gray);
    margin-top: var(--space-1);
  }

  /* Eyebrow */
  .st-eyebrow {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 9pt;
    letter-spacing: 0.32em;
    color: var(--color-gray);
    margin-bottom: var(--space-5);
  }

  /* Hero section title — runs bigger than --text-3xl by design (see spec §4) */
  .st-h {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 36pt;
    line-height: 0.95;
    letter-spacing: -0.02em;
    color: var(--color-charcoal);
    margin: 0;
    max-width: 11in;
  }

  /* Rule */
  .st-rule {
    width: 50pt;
    height: 1pt;
    background: var(--color-red);
    margin: var(--space-4) 0;
  }

  /* Italic standfirst caption */
  .st-caption {
    font-family: var(--font-display);
    font-style: italic;
    font-weight: 400;
    font-size: var(--text-lg);
    line-height: 1.4;
    color: var(--color-gray);
    max-width: 9in;
  }

  /* Bottom-right pacing ornament */
  .st-ornament {
    position: absolute;
    bottom: var(--space-7);
    right: var(--space-8);
    font-family: var(--font-display);
    font-size: 18pt;
    color: var(--color-red);
    opacity: 0.4;
    line-height: 1;
  }
</style>
{% endblock %}
{% block content %}
<div class="st-page">
  <div class="st-mark">
    <div class="st-mark-name">St. Nick's</div>
    <div class="st-mark-tag">HOLIDAY DECOR</div>
  </div>

  <div class="st-eyebrow">SHOWCASE</div>
  <h1 class="st-h">{{ section_title }}</h1>
  <div class="st-rule"></div>
  <div class="st-caption">{{ caption }}</div>

  <div class="st-ornament">✦</div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run test to confirm it passes**

Run: `.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k showcase_typographic`
Expected: 1 PASSED.

Run the whole suite:
Run: `.venv/bin/pytest -v`
Expected: 41 passed.

The `_output/showcase_typographic.pdf` file should be > 5000 bytes — text-only layout, expect ~12–20 KB.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/showcase_typographic.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2-addendum): add showcase_typographic.html layout

No-photo section-divider variant. Same data fields as
showcase_fullbleed.html. The AE swaps the layout when no strong hero
exists for the section.

Section title runs at 36pt (literal, exceeds --text-3xl on purpose —
see addendum design §4). Same St. Nick's wordmark as
cover_typographic. Bottom-right ✦ ornament at 0.4 opacity acts as a
quiet section-end pacing device.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — Verification

### Task 6: Run the full suite + manual eyeball pass

**Files:** none modified — verification only.

- [ ] **Step 1: Run the full pytest suite**

Run: `.venv/bin/pytest -v`
Expected:
- 41 passed (38 from Plan 2 baseline + `test_font_display_token_present` from Task 2 + 2 new layout cases), 0 skipped, 0 failed.
- `test_all_layouts_rendered` passes (no skip — `LAYOUT_CASES` is non-empty and all 20 PDFs exist on disk).
- For `cover_typographic` and `showcase_typographic`, the embedded fonts include `Playfair` and `Poppins` (NOT Roboto). For all 18 photo layouts, embedded fonts include `Roboto` and `Poppins` (Playfair is absent — WeasyPrint subsets to only used fonts). The conditional in `test_layout_renders` enforces this distinction.

- [ ] **Step 2: List the 20 rendered PDFs**

```bash
ls -la tests/_output/*.pdf | wc -l
ls tests/_output/*.pdf
```

Expected: 20 files; both `cover_typographic.pdf` and `showcase_typographic.pdf` are present.

- [ ] **Step 3: Manual eyeball pass on the two new PDFs**

Open `tests/_output/cover_typographic.pdf` and `tests/_output/showcase_typographic.pdf` in Preview (macOS) or any PDF viewer.

For `cover_typographic.pdf`, confirm visually:
- White background, no photo.
- St. Nick's wordmark sits top-right — italic red "St. Nick's", smaller tracked-caps "HOLIDAY DECOR" gray below.
- Issue-style numeral above headline (`№ 2026 — A Holiday Program`), small italic gray.
- Project name "Downtown Riverside MetroLink — 2026 Holiday Program" set in big Playfair Bold.
- Thin red horizontal rule under the headline.
- Design phrase `"Holiday Express"` in italic red below the rule.
- Bottom-left: client block ("PREPARED FOR" → RCTC → Jacklyn Moreno).
- Bottom-right: presenter block ("PRESENTED BY" → Jonathan Yang → St. Nick's · May 2026).

For `showcase_typographic.pdf`, confirm visually:
- White background, no photo.
- Same St. Nick's wordmark top-right.
- "SHOWCASE" eyebrow set in tracked-out caps gray.
- Section title "The Walk-Through Moment" in 36pt Playfair Bold.
- Thin red rule below the title.
- Caption ("A 12-foot lighted gift-box arch on the plaza...") in italic Playfair gray.
- Small `✦` glyph in faint red sitting bottom-right.

If anything looks wrong, note the layout name and what's off. Common things to watch for:
- Wordmark is missing or system-font (font-fallback issue → check brand.css `@font-face` urls).
- Headline is in Roboto rather than Playfair (font reference issue → check `--font-display` token in `:root`).
- Page is more than one page (CSS height/overflow issue — apply Plan 2's gap→margin fix if needed; see commit `90ddea0` for the pattern).

- [ ] **Step 4: No commit**

This task changes nothing in the tree. The full-suite green and visual confirmation are the deliverable.

---

## Plan 2 Addendum — Done

After all 6 tasks land:
- 2 new layouts shipped (`cover_typographic.html`, `showcase_typographic.html`).
- 2 new font files in the bundle (Playfair Display Bold + Italic).
- `brand.css` exposes `--font-display` token + Playfair `@font-face` blocks.
- `LAYOUT_CASES` has 20 entries; all 20 PDFs render in CI.
- `test_all_layouts_rendered` is now count-agnostic.
- Per-layout font assertion handles photo layouts (Roboto + Poppins) vs typographic layouts (Playfair + Poppins) correctly.

Plan 3 (AE workflow + parsers) picks up next, with the project memory note about AE-driven layout-variant selection now extending from "cover image choice" to "cover layout choice and showcase-divider layout choice."
