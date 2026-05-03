# Plan 2-prime — Master-Driven Layout System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Plan 2 layout system using the master pptx as literal reference. Ship 15 master-derived layouts, brand-compliant fonts/colors, two test fixtures (destination + zone-heavy), with the prior 18 layouts archived.

**Architecture:** Same WeasyPrint + Jinja2 + brand.css foundation as Plan 2. The persistent St. Nick's header + footer + page background are baked into `base.html` so layouts inherit chrome consistently. Layouts come in two background modes (`page-light` / `page-dark`); layout files toggle modes via a `body_class` Jinja block. Each layout extends `base.html` and only writes its unique body composition + layout-specific styles.

**Tech Stack:** Python 3.11+, Jinja2, WeasyPrint 68.x, pymupdf 1.24+, pytest 8+, fontsource CDN for fonts, the master PDF + PNG renders at `Master Proposal Reference/` as the visual source of truth.

---

## File Structure

**Visual reference (existing, don't modify):**
- `Master Proposal Reference/StNicks_Proposal_v2_Master.pdf` — the master deck
- `Master Proposal Reference/master-pages/page-NN.png` — per-page renders for visual diff

**Foundation (modified by Tasks 1–8):**
- `archive/iteration-1-abstract-layouts/` (new) — Plan 2's 18 HTML files + 18 PDFs + README
- `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md` — banner added
- `docs/superpowers/plans/2026-05-01-02-brand-layout-system.md` — banner added
- `docs/superpowers/specs/2026-05-03-typographic-fallback-layouts-design.md` — banner added
- `docs/superpowers/plans/2026-05-03-02b-typographic-fallback-layouts.md` — banner added
- `skill_assets/fonts/Poppins-Black.ttf` (new)
- `skill_assets/layouts/brand.css` — Poppins-Black @font-face, new tokens, page-chrome CSS
- `skill_assets/layouts/base.html` — replaced with chrome-aware version
- `tests/test_fonts_present.py` — Poppins-Black added
- `tests/test_brand_css.py` — new tokens asserted
- `tests/fixtures/pier_39.py` (new) — destination, 3 zones
- `tests/fixtures/riverside.py` — reshaped to multi-station zones
- `tests/test_layouts.py` — `LAYOUT_CASES` reset, generalized gate test stays

**Layouts (built by Tasks 9–23):**
- `skill_assets/layouts/cover.html`
- `skill_assets/layouts/exec_summary.html`
- `skill_assets/layouts/understanding.html`
- `skill_assets/layouts/creative_vision.html`
- `skill_assets/layouts/zone_solo.html`
- `skill_assets/layouts/zone_solo_fullbleed.html`
- `skill_assets/layouts/zone_2up.html`
- `skill_assets/layouts/zone_3up.html`
- `skill_assets/layouts/zone_index.html`
- `skill_assets/layouts/scope.html`
- `skill_assets/layouts/case_study.html`
- `skill_assets/layouts/investment.html`
- `skill_assets/layouts/terms.html`
- `skill_assets/layouts/sign_off.html`
- `skill_assets/layouts/about.html`

---

## Phase A — Cleanup + Foundation

### Task 1: Archive Plan 2's iteration-1 work

**Files:**
- Create: `archive/iteration-1-abstract-layouts/` directory
- Move: 18 HTML files from `skill_assets/layouts/` to `archive/iteration-1-abstract-layouts/`
- Copy: 18 PDFs from `tests/_output/` to `archive/iteration-1-abstract-layouts/`
- Create: `archive/iteration-1-abstract-layouts/README.md`

- [ ] **Step 1: Create the archive folder**

```bash
mkdir -p archive/iteration-1-abstract-layouts
```

- [ ] **Step 2: Move the 18 HTML files into archive (preserves git history of the move)**

```bash
git mv skill_assets/layouts/cover.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/exec_summary.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/understanding.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/creative_vision.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/showcase_hero.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/showcase_2up.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/showcase_3up.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/showcase_4up.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/showcase_fullbleed.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/scope.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/sample_of_work.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/case_study.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/investment_tiered.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/investment_single.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/add_ons.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/terms.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/sign_block.html archive/iteration-1-abstract-layouts/
git mv skill_assets/layouts/about.html archive/iteration-1-abstract-layouts/
```

After this, `skill_assets/layouts/` contains only `base.html` and `brand.css`.

- [ ] **Step 3: Copy the 18 PDFs from tests/_output/ to archive (these aren't in git but are visual reference)**

```bash
cp tests/_output/cover.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/exec_summary.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/understanding.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/creative_vision.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/showcase_hero.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/showcase_2up.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/showcase_3up.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/showcase_4up.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/showcase_fullbleed.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/scope.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/sample_of_work.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/case_study.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/investment_tiered.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/investment_single.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/add_ons.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/terms.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/sign_block.pdf archive/iteration-1-abstract-layouts/
cp tests/_output/about.pdf archive/iteration-1-abstract-layouts/
```

- [ ] **Step 4: Write `archive/iteration-1-abstract-layouts/README.md`**

```markdown
# Plan 2 Iteration 1 — Abstract-Driven Layouts (archived)

**Status:** Superseded 2026-05-03 by Plan 2-prime (master-driven layouts).

This directory contains the 18 layouts shipped by Plan 2 (May 1–2, 2026) along
with their rendered PDFs. They are kept here for reference: side-by-side visual
comparison with the master deck and Plan 2-prime's output, and as a worked
example of what *not* to ship.

## Why archived

The original Plan 2 spec (decision 6) called the master pptx an "informal
directional reference only" and produced a fresh modern redesign. The output was
technically clean but bland and structurally wrong:

- Abstract layouts (`showcase_2up`, `showcase_3up`) instead of zone-driven slides
  customers can map to physical parts of their property.
- St. Nick's branding hidden — only on the cover and About page, not as
  persistent header/footer.
- Pricing reserved — tier numbers and add-on costs were set small or absent.
- Tone was civic-procurement reserved, not the confident sales tone of the
  master.

Daniel rejected the output on 2026-05-03. Plan 2-prime uses the master pptx as
the literal reference instead.

## What's here

- `*.html` — the 18 Jinja2 layouts (page chrome + design tokens via `brand.css`)
- `*.pdf` — rendered output as of the final Plan 2 commit. Eyeball these
  alongside the new layouts to see the gap.

## Original specs + plans

- Spec: `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md`
- Plan: `docs/superpowers/plans/2026-05-01-02-brand-layout-system.md`
- Replacement spec: `docs/superpowers/specs/2026-05-03-plan-2-prime-master-driven-design.md`
- Replacement plan: `docs/superpowers/plans/2026-05-03-plan-2-prime-master-driven-layouts.md`

A typographic-fallback addendum (cover_typographic.html, showcase_typographic.html)
was scoped on 2026-05-03 morning but never executed; its spec/plan are also
marked superseded.
```

- [ ] **Step 5: Commit the archive**

```bash
git add archive/iteration-1-abstract-layouts/
git commit -m "$(cat <<'EOF'
chore(plan-2-prime): archive iteration-1 abstract-driven layouts

Moves 18 HTML layouts + 18 rendered PDFs from skill_assets/layouts/ and
tests/_output/ to archive/iteration-1-abstract-layouts/ with a README
explaining what this is and why it was superseded.

skill_assets/layouts/ now contains only base.html and brand.css; the new
master-driven layouts will land on top in subsequent commits.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Mark superseded specs and plans with status banners

**Files:**
- Modify: `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md` (banner at top)
- Modify: `docs/superpowers/plans/2026-05-01-02-brand-layout-system.md` (banner at top)
- Modify: `docs/superpowers/specs/2026-05-03-typographic-fallback-layouts-design.md` (banner at top)
- Modify: `docs/superpowers/plans/2026-05-03-02b-typographic-fallback-layouts.md` (banner at top)

- [ ] **Step 1: Add banner to the original Plan 2 spec**

Insert at the top of `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md`, immediately after the `# Plan 2 — Brand + Layout System: Design` H1:

```markdown
> ⚠️ **SUPERSEDED 2026-05-03.** Decision 6 ("master is informal directional
> reference only") was wrong. Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-design.md`](./2026-05-03-plan-2-prime-master-driven-design.md).
> Implementation moved to `archive/iteration-1-abstract-layouts/`.

```

- [ ] **Step 2: Add banner to the original Plan 2 plan**

Insert at the top of `docs/superpowers/plans/2026-05-01-02-brand-layout-system.md`, immediately after the `# Plan 2 — Brand + Layout System Implementation Plan` H1:

```markdown
> ⚠️ **SUPERSEDED 2026-05-03.** This plan executed but its output (18 abstract
> layouts) was rejected. Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-layouts.md`](./2026-05-03-plan-2-prime-master-driven-layouts.md).
> Output preserved at `archive/iteration-1-abstract-layouts/`.

```

- [ ] **Step 3: Add banner to the typographic-fallback spec**

Insert at the top of `docs/superpowers/specs/2026-05-03-typographic-fallback-layouts-design.md`, immediately after the `# Typographic Fallback Layouts — Design` H1:

```markdown
> ⚠️ **SUPERSEDED 2026-05-03 (same day).** Off-brand: the Branding Board rules
> out decorative/script fonts, but this addendum added Playfair Display.
> Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-design.md`](./2026-05-03-plan-2-prime-master-driven-design.md).
> Never executed.

```

- [ ] **Step 4: Add banner to the typographic-fallback plan**

Insert at the top of `docs/superpowers/plans/2026-05-03-02b-typographic-fallback-layouts.md`, immediately after the `# Plan 2 Addendum — Typographic Fallback Layouts Implementation Plan` H1:

```markdown
> ⚠️ **SUPERSEDED 2026-05-03 (same day, never executed).** Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-layouts.md`](./2026-05-03-plan-2-prime-master-driven-layouts.md).

```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md \
        docs/superpowers/plans/2026-05-01-02-brand-layout-system.md \
        docs/superpowers/specs/2026-05-03-typographic-fallback-layouts-design.md \
        docs/superpowers/plans/2026-05-03-02b-typographic-fallback-layouts.md
git commit -m "$(cat <<'EOF'
docs(plan-2-prime): mark superseded specs and plans with status banners

Banners on the four superseded documents (original Plan 2 spec + plan,
typographic-fallback spec + plan) point at the Plan 2-prime replacements
and explain the why. Documents themselves remain unchanged for history.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Embed Poppins-Black font in `skill_assets/fonts/`

**Files:**
- Create: `skill_assets/fonts/Poppins-Black.ttf`
- Modify: `tests/test_fonts_present.py` — add Poppins-Black to `REQUIRED_FONTS`

- [ ] **Step 1: Extend the failing test**

Edit `tests/test_fonts_present.py`. Replace the contents with:

```python
"""Asserts the required font files exist in skill_assets/fonts/.

Per parent spec §3 / Plan 2-prime design §6, fonts MUST be embedded in the
skill bundle and never loaded from the system. This test catches accidental
deletion or wrong filename.
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
    "Poppins-Black.ttf",
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

```bash
.venv/bin/pytest tests/test_fonts_present.py -v
```

Expected: FAIL — `test_required_fonts_present` reports missing `Poppins-Black.ttf`.

- [ ] **Step 3: Download Poppins-Black from fontsource CDN (same source as the other Poppins weights)**

```bash
curl -sSfL -o skill_assets/fonts/Poppins-Black.ttf \
  "https://cdn.jsdelivr.net/fontsource/fonts/poppins@latest/latin-900-normal.ttf"
```

- [ ] **Step 4: Verify file is a valid TTF**

```bash
ls -la skill_assets/fonts/Poppins-Black.ttf
file skill_assets/fonts/Poppins-Black.ttf
```

Expected: file exists, size > 30 KB, `file` reports `TrueType Font data`.

- [ ] **Step 5: Run test to verify it passes**

```bash
.venv/bin/pytest tests/test_fonts_present.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/fonts/Poppins-Black.ttf tests/test_fonts_present.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): embed Poppins-Black font in skill bundle

Adds Poppins-Black.ttf (weight 900) to skill_assets/fonts/, extending
the existing Poppins family (Light/Regular/Medium). Used for the heavy
display headlines in the master-driven layouts (page-title hero ~50pt,
zone names ~80pt on the cover).

Sourced from fontsource CDN — same source as Plan 2's other weights.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Add new brand.css tokens, Poppins-Black @font-face, and page-chrome CSS

**Files:**
- Modify: `skill_assets/layouts/brand.css`
- Modify: `tests/test_brand_css.py`

- [ ] **Step 1: Extend the failing tests**

Edit `tests/test_brand_css.py`. Replace the entire contents with:

```python
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
```

- [ ] **Step 2: Run tests to verify the new ones fail**

```bash
.venv/bin/pytest tests/test_brand_css.py -v
```

Expected: 4 FAIL (`test_panel_and_green_tokens_present`, `test_font_family_tokens_present` for `--font-display`, `test_font_face_declarations_present` for Poppins-Black, `test_page_chrome_classes_present`).

- [ ] **Step 3: Update `skill_assets/layouts/brand.css`**

Replace the entire contents of `skill_assets/layouts/brand.css` with:

```css
/* St. Nick's Proposal Builder — locked brand tokens
 *
 * Single source of truth for brand colors, fonts, type scale, spacing
 * scale, page geometry, and persistent page chrome. Layouts may add
 * layout-specific styles inline but must NEVER write hex colors,
 * raw font names, or raw pixel sizes — always use the tokens here.
 *
 * See docs/superpowers/specs/2026-05-03-plan-2-prime-master-driven-design.md
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
@font-face {
  font-family: "Poppins";
  src: url("../fonts/Poppins-Black.ttf") format("truetype");
  font-weight: 900;
  font-style: normal;
}

/* ===== Design tokens ===== */
:root {
  /* Brand colors — verbatim from the Branding Board */
  --color-red: #B31315;       /* Headlines, accents, CTAs, eyebrows */
  --color-charcoal: #1C1C1C;  /* Body on light backgrounds; dark page bg */
  --color-gray: #555555;      /* Captions, secondary text, footer */
  --color-navy: #12355B;      /* Secondary accent; tier rule on Investment */
  --color-light: #ECEFF1;     /* Body on dark backgrounds; light fills */

  /* Plan 2-prime additions for card surfaces */
  --color-panel: #F2F2F2;     /* Card / panel background — distinct from --color-light */
  --color-green: #1B7A3F;     /* Scope page "YOUR PROGRAM INCLUDES" header — only used there */

  /* Font families */
  --font-heading: "Roboto", sans-serif;     /* Subheadings, key statements, labels */
  --font-body: "Poppins", sans-serif;       /* Body, long-form, captions */
  --font-display: "Poppins", sans-serif;    /* Heavy display headlines (use weight 900) */

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
  size: 13.333in 7.5in;
  margin: 0;
}

/* ===== Page chrome — persistent header, footer, body background ===== */
html, body {
  margin: 0;
  padding: 0;
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-base);
  line-height: 1.45;
  width: 13.333in;
  height: 7.5in;
}

body.page-light {
  background: white;
  color: var(--color-charcoal);
}

body.page-dark {
  background: var(--color-charcoal);
  color: var(--color-light);
}

.page-header {
  position: absolute;
  top: var(--space-4);
  left: var(--space-6);
}
.page-header .brand-name {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 11pt;
  letter-spacing: 0.06em;
  line-height: 1.0;
}
.page-header .brand-tag {
  font-family: var(--font-body);
  font-weight: 400;
  font-size: 7pt;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-top: 4pt;
  opacity: 0.85;
}
body.page-light .page-header { color: var(--color-charcoal); }
body.page-dark  .page-header { color: var(--color-light); }

.page-footer {
  position: absolute;
  bottom: var(--space-4);
  left: var(--space-6);
  right: var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 8pt;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
body.page-light .page-footer { color: var(--color-gray); }
body.page-dark  .page-footer { color: var(--color-light); opacity: 0.65; }

.page-content {
  position: absolute;
  top: var(--space-8);
  left: var(--space-6);
  right: var(--space-6);
  bottom: var(--space-8);
  /* Layouts add their own padding/grid inside .page-content. */
}

/* ===== Global element rules ===== */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: 700;
  margin: 0 0 var(--space-3) 0;
  line-height: 1.15;
  letter-spacing: -0.01em;
}

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

/* Utility: small uppercase label (Roboto Bold caps, brand red) */
.label {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-red);
}

/* Utility: section eyebrow, slightly tighter than .label, used for "ZONE 01", "CASE STUDY" */
.eyebrow {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 10pt;
  text-transform: uppercase;
  letter-spacing: 0.10em;
  color: var(--color-red);
}

/* Utility: page-title hero (Poppins Black at 50pt) */
.page-title {
  font-family: var(--font-display);
  font-weight: 900;
  font-size: 50pt;
  line-height: 1.0;
  letter-spacing: -0.02em;
  margin: 0;
}

/* Utility: italic standfirst beneath the page title */
.standfirst {
  font-family: var(--font-body);
  font-weight: 300;
  font-style: italic;
  font-size: 16pt;
  line-height: 1.35;
  margin: var(--space-2) 0 0 0;
}
body.page-light .page-title { color: var(--color-charcoal); }
body.page-dark  .page-title { color: var(--color-light); }
body.page-light .standfirst { color: var(--color-gray); }
body.page-dark  .standfirst { color: var(--color-light); opacity: 0.7; }

/* Card pattern — used by Understanding, Scope, Terms, Sign-off */
.card {
  background: var(--color-panel);
  border-radius: 4pt;
  padding: var(--space-4);
  box-shadow: 0 1pt 3pt rgba(0, 0, 0, 0.08);
}
.card.red-rule { border-left: 3pt solid var(--color-red); }
.card.has-header { padding: 0; overflow: hidden; }
.card .card-header {
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: var(--text-sm);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-light);
}
.card.has-header.green .card-header { background: var(--color-green); }
.card.has-header.red   .card-header { background: var(--color-red); }
.card .card-body {
  padding: var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--color-charcoal);
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_brand_css.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/layouts/brand.css tests/test_brand_css.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): rewrite brand.css with chrome + new tokens

Major changes vs Plan 2's brand.css:
- Adds Poppins-Black @font-face (weight 900).
- Adds tokens: --color-panel (#F2F2F2 card bg), --color-green (#1B7A3F
  Scope-only), --font-display (= Poppins, intent-signaling).
- Removes default @page margin (was var(--space-6)) since layouts now
  control their own internal padding via .page-content.
- Adds page-chrome CSS: body.page-light / body.page-dark backgrounds,
  .page-header (top-left brand mark), .page-footer (project crumb +
  page number), .page-content (positioned interior).
- Adds utility classes: .eyebrow, .page-title, .standfirst, .card
  (with header/red-rule variants).

Existing 5 brand colors, type scale, spacing scale, page geometry
(13.333in × 7.5in) all unchanged.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Rewrite `base.html` to include persistent chrome

**Files:**
- Modify: `skill_assets/layouts/base.html` (full rewrite)
- Modify: `tests/test_base_html.py`

- [ ] **Step 1: Extend the failing tests**

Replace the contents of `tests/test_base_html.py` with:

```python
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
```

- [ ] **Step 2: Run tests to verify failures**

```bash
.venv/bin/pytest tests/test_base_html.py -v
```

Expected: at least 3 fail (block list, chrome, default body class).

- [ ] **Step 3: Replace `skill_assets/layouts/base.html`**

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
<body class="{% block body_class %}page-light{% endblock %}">

  <header class="page-header">
    <div class="brand-name">ST. NICK'S</div>
    <div class="brand-tag">CHRISTMAS LIGHTING &amp; DÉCOR</div>
  </header>

  <div class="page-content">
    {% block content %}{% endblock %}
  </div>

  {% block footer %}
  <footer class="page-footer">
    <div class="footer-crumb">ST. NICK'S &nbsp;·&nbsp; {{ project_year }} HOLIDAY PROPOSAL &nbsp;·&nbsp; {{ client_short }}</div>
    <div class="footer-page-num">{{ page_num }} / {{ page_total }}</div>
  </footer>
  {% endblock %}

</body>
</html>
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_base_html.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/layouts/base.html tests/test_base_html.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): rewrite base.html with persistent chrome

Adds the persistent St. Nick's brand mark (top-left) and project-crumb
+ page-number footer that appear on every master slide. Layouts now
extend base.html and inherit chrome automatically:
- Default body class is page-light (white bg). Dark-bg layouts
  (cover, creative_vision, zone_solo_fullbleed, about) override
  {% block body_class %}page-dark{% endblock %}.
- Layouts that should not show the footer (cover, dark feature pages
  per master) override {% block footer %}{% endblock %} as empty.

Footer reads project_year, client_short, page_num, page_total from ctx
(StrictUndefined enforces presence in test fixtures).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Build `tests/fixtures/pier_39.py` — destination-style fixture (3 zones)

**Files:**
- Create: `tests/fixtures/pier_39.py`

- [ ] **Step 1: Write the fixture file**

Create `tests/fixtures/pier_39.py`:

```python
"""Pier 39 fixture — destination-style proposal with 3 zones.

Content matches Master Proposal Reference/StNicks_Proposal_v2_Master.pdf
verbatim, since the master is built around this project. Drives the
"destination path" through the layout system: zone_solo for non-signature
zones, zone_solo_fullbleed for the signature zone.

Plan 3 will produce dicts of the same shape from real Brief.md +
Scope Worksheet.xlsx + rendering folders. Until then this file IS the
data. Each per-layout ctx dict is a dict that gets passed to Jinja2 as
the rendering context. Common project-wide values are assembled into
PROJECT and merged via {**PROJECT, ...}.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# No real Pier 39 renderings are in the test fixtures yet — when the
# Plan 3 AE workflow lands, real images will replace these placeholders.
# For now hero_image fields are None; layouts must render a placeholder
# when no image is supplied (tested via dark grey rectangle).
NO_IMAGE = None


PROJECT = {
    "client_company": "Pier 39",
    "client_short": "PIER 39 SAN FRANCISCO",
    "project_name": "Pier 39",
    "project_short": "Pier 39",
    "project_year": 2026,
    "project_subtitle": "San Francisco",
    "presenter_name": "Daniel Christenson",
    "presenter_title": "Director of Sales",
    "presenter_org": "St. Nick's Christmas Lighting & Décor",
    "proposal_date": "October 15, 2026",
    "page_total": 13,
}


# ===== Slide 1 — Cover =====
cover_ctx = {
    **PROJECT,
    "page_num": 1,
    "season_label": "2026 HOLIDAY SEASON",
    "hero_image": NO_IMAGE,
    "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
}


# ===== Slide 2 — Executive Summary =====
exec_summary_ctx = {
    **PROJECT,
    "page_num": 2,
    "page_title": "Executive Summary",
    "standfirst": "Our 2026 holiday program for Pier 39, at a glance.",
    "body_paragraphs": [
        "St. Nick's is proposing a destination-scale holiday program for Pier 39 — a designed, fabricated, installed, and serviced lighting and décor experience across three of the property's highest-traffic guest zones.",
        "Our approach builds a signature visual identity for Pier 39's 2026 holiday season, driving guest dwell time, social shareability, and differentiation from neighboring attractions along the Embarcadero.",
    ],
    "at_a_glance": [
        ("PROJECT", "2026 Holiday Program", False),
        ("ZONES", "Embarcadero · Promenade · Bay Terrace", False),
        ("RECOMMENDED TIER", "Enhanced", False),
        ("INVESTMENT RANGE", "$225K — $485K", False),
        ("GO LIVE", "Fri, Nov 20, 2026", False),
        ("FABRICATION LOCK", "Aug 22, 2026", True),
        ("SIGNING DEADLINE", "Nov 14, 2026", True),
    ],
    "pillars": [
        {"title": "Turnkey Delivery",   "body": "Concept through teardown — one partner, zero seams."},
        {"title": "Destination Scale",  "body": "Built for venues hosting millions of guests per season."},
        {"title": "25 Years at It",     "body": "From Pier 39 to Disney Parks, we've done this before."},
    ],
}


# ===== Slide 3 — Our Understanding =====
understanding_ctx = {
    **PROJECT,
    "page_num": 3,
    "page_title": "Our Understanding",
    "standfirst": "Playback of discovery — so we're all working from the same page.",
    "panels": [
        {"title": "VENUE & CONTEXT", "body": "Pier 39 is San Francisco's iconic waterfront destination — 45 acres of retail, dining, and entertainment hosting 10M+ annual guests. Holiday season drives peak family traffic from Thanksgiving through New Year's."},
        {"title": "GOALS FOR 2026",  "body": "Amplify the arrival experience, extend guest dwell time through the holiday window, and create shareable photo moments that reinforce Pier 39's position as Northern California's premier holiday destination."},
        {"title": "KEY CONSTRAINTS", "body": "Phased install during overnight windows to avoid retail disruption. Zero impact to the sea lion habitat at K-Dock. All-weather durability required. Full removal and storage complete by January 15, 2027."},
        {"title": "WHAT SUCCESS LOOKS LIKE", "body": "A signature holiday identity photographed and shared 10x the volume of 2025. Measurable dwell-time lift. A program built for multi-year refresh and extension into Pier 39's broader marketing narrative."},
    ],
}


# ===== Slide 4 — Creative Vision =====
creative_vision_ctx = {
    **PROJECT,
    "page_num": 4,
    "page_title": "Creative Vision",
    "standfirst": "The design direction for Pier 39's 2026 holiday program.",
    "design_phrase": "Bayside Twilight.",
    "design_direction_body": "A cinematic holiday aesthetic that honors Pier 39's waterfront character — warm whites and brushed gold set against the Bay at twilight, oversized architectural lighting, and seasonal storytelling that unfolds as guests move through the property.",
    "phases": [
        {"label": "ARRIVE",   "body": "Warm, cinematic welcome."},
        {"label": "EXPLORE",  "body": "Discoverable moments along the Promenade."},
        {"label": "CELEBRATE","body": "A landmark scene at the Bay Terrace."},
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 5 — Zone 01: Embarcadero Arrival (zone_solo) =====
zone_01_ctx = {
    **PROJECT,
    "page_num": 5,
    "zone_num": "01",
    "zone_name": "Embarcadero Arrival",
    "zone_subtitle": "First impression. The threshold between the city and Pier 39.",
    "included_elements": [
        "28' illuminated entry arch",
        "Pair of 14' flanking classic trees",
        "Custom 'Welcome to Pier 39' marquee",
        "Warm-white garland across arch beams",
        "Brushed-gold ribbon accents",
        "Dusk-to-dawn programming",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 6 — Zone 02: Pier Promenade (zone_solo) =====
zone_02_ctx = {
    **PROJECT,
    "page_num": 6,
    "zone_num": "02",
    "zone_name": "Pier Promenade",
    "zone_subtitle": "A layered, discoverable journey through the heart of the Pier.",
    "included_elements": [
        "220 linear feet of illuminated tree wrap",
        "Four 8' oversized ornament installations",
        "Suspended starlight canopy over Central Plaza",
        "Two custom photo moments (K-Dock + fountain)",
        "Themed garland across retail storefronts",
        "Hot cocoa concierge station (Fri–Sun)",
        "Curated wreath package on Pier architecture",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 7 — Zone 03: Bay Terrace (zone_solo_fullbleed, signature) =====
zone_03_ctx = {
    **PROJECT,
    "page_num": 7,
    "zone_num": "03",
    "zone_name": "Bay Terrace",
    "zone_subtitle": "The signature moment. The destination within the destination.",
    "included_elements": [
        "40' walkthrough signature tree",
        "Illuminated Bay view photo frame",
        "Suspended snowflake constellation",
        "Custom \"Happy Holidays, Pier 39\" marquee",
        "Gold-accented architectural pier lighting",
        "Nightly synchronized music + light show",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 8 — Scope of Work =====
scope_ctx = {
    **PROJECT,
    "page_num": 8,
    "page_title": "Scope of Work",
    "standfirst": "What your investment includes, and what you can add on.",
    "includes": [
        "Creative design + client-approved renderings",
        "All materials, décor, and lighting elements",
        "Installation labor (3-week phased window)",
        "Testing, commissioning, and launch night support",
        "Daily programming (dusk-to-dawn schedule)",
        "Weekly on-site maintenance visits (Nov 20 – Jan 5)",
        "24/7 season on-call response (4-hour SLA)",
        "Complete post-season teardown and removal",
        "Storage of reusable elements at our facility",
    ],
    "add_ons": [
        ("Extended programming (Halloween kickoff)", "+$12K"),
        ("Maintenance upgrade (2x weekly visits)",   "+$9K"),
        ("Custom photo-op signage package",          "+$14K"),
        ("Scheduled mid-season creative refresh",    "+$18K"),
        ("Synchronized music + full light show",     "+$24K"),
        ("On-site producer (peak Fri/Sat nights)",   "+$16K"),
        ("Priority 2-hour SLA upgrade",              "+$8K"),
        ("Extended installation (add-week)",         "+$22K"),
        ("Multi-year partnership (see Investment page)", "Varies"),
    ],
}


# ===== Slide 9 — Case Study =====
case_study_ctx = {
    **PROJECT,
    "page_num": 9,
    "page_eyebrow": "CASE STUDY",
    "page_title": "Oregon Zoo · ZooLights 2025",
    "standfirst": "Transforming Portland's family destination into a signature winter experience.",
    "challenge": "Deliver a full property-wide holiday transformation across 64 acres of active zoological habitats, with zero disruption to animal welfare protocols and overnight install windows aligned to keeper schedules.",
    "approach":  "Phased 18-night install coordinated with animal care teams. Custom low-impact lighting specifications. A signature 45-ft illuminated central tree, themed habitat lighting, and an interactive Light Walk that shifted weekly.",
    "outcome":   "31% YoY increase in ZooLights attendance. 4.2M+ social impressions. Partnership renewed through 2028. Feature coverage in The Oregonian, KGW, and Travel + Leisure.",
    "hero_image": NO_IMAGE,
}


# ===== Slide 10 — Investment =====
investment_ctx = {
    **PROJECT,
    "page_num": 10,
    "page_title": "Investment",
    "standfirst": "Three levels of program. Pick what fits your season.",
    "tiers": [
        {
            "name": "ESSENTIAL",
            "rule_color": "gray",
            "tagline": "CORE HOLIDAY PRESENCE",
            "highlights": [
                "Zone 01 (Embarcadero) only",
                "Core lighting + décor",
                "Weekly maintenance",
                "Dusk-to-dawn programming",
            ],
            "price": "$225,000",
            "is_recommended": False,
        },
        {
            "name": "ENHANCED",
            "rule_color": "red",
            "tagline": "FULL GUEST EXPERIENCE",
            "highlights": [
                "Everything in Essential, plus:",
                "Zones 02 + 03",
                "Custom photo moments",
                "Suspended starlight canopy",
                "24/7 on-call response",
            ],
            "price": "$345,000",
            "is_recommended": True,
        },
        {
            "name": "SIGNATURE",
            "rule_color": "navy",
            "tagline": "DESTINATION EXPERIENCE",
            "highlights": [
                "Everything in Enhanced, plus:",
                "40' signature tree + marquee",
                "Synchronized music + light show",
                "Mid-season creative refresh",
                "On-site producer, priority SLA",
            ],
            "price": "$485,000",
            "is_recommended": False,
        },
    ],
    "partnership_discounts": [
        ("2-YEAR", "4% OFF"),
        ("3-YEAR", "6% OFF"),
        ("5-YEAR", "9% OFF"),
    ],
    "footer_note": "Pricing valid 30 days from proposal date. Fabrication must be locked by Aug 22, 2026.",
}


# ===== Slide 11 — Terms & Next Steps =====
terms_ctx = {
    **PROJECT,
    "page_num": 11,
    "page_title": "Terms & Next Steps",
    "standfirst": "The critical dates and terms for the 2026 program.",
    "critical_dates": [
        ("November 14, 2026", "Execute by this date to guarantee the install schedule."),
        ("August 22, 2026",   "All custom fabrication must be approved by this date (90 days pre-Go Live)."),
    ],
    "term_panels": [
        ("PAYMENT SCHEDULE",   "50% deposit upon contract execution — required to lock the install schedule. 50% balance due upon completion of post-season teardown (Jan 15, 2027). Net-15 terms on final invoice."),
        ("INSURANCE & PERMITS","$5M Umbrella over $1M/$2M Commercial General Liability and $1M Auto; full Workers' Comp at statutory limits. Certificates available upon request. Municipal permits handled by Pier 39; we provide full documentation support."),
        ("CHANGE ORDERS",      "Includes 2 creative revision rounds before Fabrication Lock (Aug 22, 2026). Changes after that date require a written change order: 30% of the value of any item removed from scope, plus full value of any item added."),
        ("PROPOSAL VALIDITY",  "This proposal is valid 30 days from October 15, 2026. Materials pricing subject to market conditions thereafter. Sign by Nov 14 to lock schedule."),
    ],
    "after_approval_steps": ["Kickoff call within 48 hrs", "Creative window opens", "Renderings final by Aug 1"],
}


# ===== Slide 12 — Sign-off =====
sign_off_ctx = {
    **PROJECT,
    "page_num": 12,
    "page_title": "Let's Make It Happen",
    "standfirst": "Sign below to launch Pier 39's 2026 holiday program.",
    "what_youre_approving": "The 2026 Pier 39 holiday program — three zones (Embarcadero Arrival, Pier Promenade, Bay Terrace), live Nov 20, 2026 through Jan 5, 2027, at the tier and add-ons you select on the Investment page.",
    "client_party_label":   "CLIENT AUTHORIZATION",
    "stnicks_party_label":  "ST. NICK'S AUTHORIZED SIGNATURE",
    "digital_signing_note": "Prefer to sign digitally? Use the Canva e-signature link in your email. Questions? Reply directly — we'll respond within 24 hours.",
}


# ===== Slide 13 — About St. Nick's =====
about_ctx = {
    **PROJECT,
    "page_num": 13,
    "page_title": "About St. Nick's",
    "standfirst": "25 years of large-scale holiday design, installation, and service.",
    "company_facts": [
        "Founded 1998 (dba St. Nick's) — T&G Global, LLC",
        "14 full-time team · 30–45 seasonal staff",
        "B-General Building Contractor #990427",
        "Certified Small Business Supplier #1626660",
        "$5M Umbrella · $1M/$2M GL · $1M Auto · Full Workers' Comp",
        "200+ commercial venues across North America",
    ],
    "team": [
        {"name": "Nicholas Adams",   "role": "Founder"},
        {"name": "Wade Francis",     "role": "Chief Financial Officer"},
        {"name": "Brenda Sheridan",  "role": "Director of Operations"},
        {"name": "Daniel Christenson","role": "Director of Sales"},
        {"name": "Stephanie Escobar","role": "Creative Director"},
        {"name": "Carlos Vasquez & Alonso Salazar", "role": "Senior Installers / Project Managers"},
    ],
    "contact_strip": "ST-NICKS.COM  ·  (562) 438-0017  ·  6861 Walker St, La Palma, CA 90623  ·  © 2026 St. Nick's Christmas Lighting & Décor",
}
```

- [ ] **Step 2: Verify the fixture imports cleanly**

```bash
.venv/bin/python -c "from tests.fixtures import pier_39; print(pier_39.PROJECT['client_short']); print(len([k for k in dir(pier_39) if k.endswith('_ctx')]), 'ctx dicts')"
```

Expected: prints `PIER 39 SAN FRANCISCO` and `13 ctx dicts`.

- [ ] **Step 3: Run the whole suite to confirm no regression**

```bash
.venv/bin/pytest -v
```

Expected: passing tests from Tasks 1–5; no test references the new fixture yet so no new tests run.

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/pier_39.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): add Pier 39 destination-style test fixture

13 per-layout ctx dicts (cover through about) plus zone_01/02/03_ctx
for the 3 destination zones. Content mirrors the master pptx
verbatim so the rendered output can be eyeballed against the master
PNG renders in Master Proposal Reference/master-pages/.

This is the "destination path" fixture (3 zones, master pattern).
The "zone-heavy path" fixture (Riverside, 5+ stations) lands next.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Reshape `tests/fixtures/riverside.py` — multi-station zone-heavy fixture

**Files:**
- Modify: `tests/fixtures/riverside.py` (full rewrite — old fixture content gets overwritten)

- [ ] **Step 1: Replace `tests/fixtures/riverside.py` entirely**

```python
"""Riverside MetroLink fixture — zone-heavy multi-station civic project.

Anchored on the same Riverside MetroLink project as before, but reshaped
from the old "showcase categories" model to true zone vocabulary. Each
station on the line is a zone. With 6 zones the deck would stretch out
endlessly using zone_solo only — Plan 3 will pick zone_2up / zone_3up /
zone_index based on count.

This fixture exists to prove the zone-grouped layouts work at scale.
The destination-style fixture (Pier 39, 3 zones) lives in pier_39.py.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RIVERSIDE = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"
RENDERINGS_DIR = RIVERSIDE / "02 - Renderings"
BASE_SCOPE = RENDERINGS_DIR / "Base Scope"
ENHANCEMENTS = RENDERINGS_DIR / "Enhancements"

NO_IMAGE = None


PROJECT = {
    "client_company": "Riverside County Transportation Commission (RCTC)",
    "client_short": "RCTC METROLINK",
    "project_name": "Riverside MetroLink",
    "project_short": "MetroLink",
    "project_year": 2026,
    "project_subtitle": "Six-Station Civic Holiday Program",
    "presenter_name": "Jonathan Yang",
    "presenter_title": "Account Executive",
    "presenter_org": "St. Nick's Christmas Lighting & Décor",
    "proposal_date": "May 12, 2026",
    "page_total": 14,   # +1 vs Pier 39 because this deck includes a zone_index slide
}


# Six stations along the MetroLink line — each is a zone.
ZONES = [
    {"num": "01", "name": "Downtown Riverside",   "subtitle": "The flagship station — civic centerpiece.",
     "included_elements": ["Custom-fabricated wreaths at every entrance", "Full-canopy garland across the platform overhang", "Pole banner program (8 poles)"]},
    {"num": "02", "name": "La Sierra",            "subtitle": "First park-and-ride stop — community gateway.",
     "included_elements": ["Wreaths at primary entrance", "Pole banner program (4 poles)", "Lighted accent at platform sign"]},
    {"num": "03", "name": "Pedley",               "subtitle": "Mid-line residential stop — restrained festive treatment.",
     "included_elements": ["Garland across platform railing", "Two pole banners at station entry"]},
    {"num": "04", "name": "Riverside-Hunter Park","subtitle": "University-adjacent — student-traffic focus.",
     "included_elements": ["Pole banner program (6 poles)", "Lighted gateway display at the bus interchange", "Wreaths at the eastbound entry"]},
    {"num": "05", "name": "Moreno Valley/March Field","subtitle": "Outer line — visible from the freeway.",
     "included_elements": ["Large-format pole banner program (10 poles, freeway-side)", "Lighted snowflake constellation along the platform"]},
    {"num": "06", "name": "Perris-Downtown",      "subtitle": "End of line — community arrival moment.",
     "included_elements": ["Walk-through ornament arch at the plaza", "Wreaths and garland at all entrances", "Pole banner program (4 poles)"]},
]


# ===== Slide 1 — Cover =====
cover_ctx = {
    **PROJECT,
    "page_num": 1,
    "season_label": "2026 HOLIDAY SEASON",
    "hero_image": NO_IMAGE,
    "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
}


# ===== Slide 2 — Executive Summary =====
exec_summary_ctx = {
    **PROJECT,
    "page_num": 2,
    "page_title": "Executive Summary",
    "standfirst": "A six-station holiday program for the Riverside MetroLink line, at a glance.",
    "body_paragraphs": [
        "St. Nick's is proposing a coordinated holiday décor program across all six stations of the Riverside MetroLink line — a single visual identity that scales from flagship Downtown Riverside through to Perris-Downtown.",
        "Our approach builds civic pride at every stop while keeping operational discipline tight: install and removal coordinate with revenue service hours, all materials clear MetroLink overhead catenary safety envelope, and the design language repeats so every station reads as part of one program.",
    ],
    "at_a_glance": [
        ("PROJECT", "2026 Civic Holiday Program", False),
        ("STATIONS", "Six (Downtown Riverside → Perris-Downtown)", False),
        ("RECOMMENDED TIER", "Enhanced", False),
        ("INVESTMENT RANGE", "$184K — $384K", False),
        ("GO LIVE", "Fri, Nov 20, 2026", False),
        ("FABRICATION LOCK", "Aug 22, 2026", True),
        ("SIGNING DEADLINE", "Oct 30, 2026", True),
    ],
    "pillars": [
        {"title": "Civic Pride",            "body": "A holiday program that elevates Riverside as a destination, not just a transit stop."},
        {"title": "Operational Discipline", "body": "Materials engineered for transit weather; install coordinated with MetroLink service hours."},
        {"title": "Repeatable Investment",  "body": "Decor designed for multi-season reuse; 2026 builds the base for 2027 and 2028."},
    ],
}


# ===== Slide 3 — Our Understanding =====
understanding_ctx = {
    **PROJECT,
    "page_num": 3,
    "page_title": "Our Understanding",
    "standfirst": "Playback of discovery — so we're all working from the same page.",
    "panels": [
        {"title": "VENUE & CONTEXT", "body": "The MetroLink line connects six communities across Riverside County. Holiday season foot-traffic spikes at flagship Downtown Riverside; outer stations carry mostly commuter and park-and-ride traffic with civic-pride significance for local residents."},
        {"title": "GOALS FOR 2026",  "body": "Establish RCTC's MetroLink line as a regional holiday destination; drive non-transit foot traffic to Downtown Riverside in particular; position the County as a leader in civic seasonal programming."},
        {"title": "KEY CONSTRAINTS", "body": "All decor must clear MetroLink overhead catenary safety envelope. Install and removal must occur outside revenue service hours. Materials must withstand winter Santa Ana wind events."},
        {"title": "WHAT SUCCESS LOOKS LIKE", "body": "Measurable increase in evening visitors during the program window. Local press and social media coverage of the activation. Zero MetroLink operational disruptions during install/strike."},
    ],
}


# ===== Slide 4 — Creative Vision =====
creative_vision_ctx = {
    **PROJECT,
    "page_num": 4,
    "page_title": "Creative Vision",
    "standfirst": "The design direction for the 2026 MetroLink program.",
    "design_phrase": "Holiday Express.",
    "design_direction_body": "A civic-scale holiday aesthetic that turns the MetroLink line itself into the holiday gesture. Wreaths and garlands frame each station entrance like a ceremonial gateway; evening lighting turns the platforms themselves into destinations after sundown. The same design vocabulary repeats at every stop so the line reads as one program from end to end.",
    "phases": [
        {"label": "WELCOME",  "body": "Wreaths and garlands at every station entrance — the holiday begins at the curb."},
        {"label": "JOURNEY",  "body": "Pole banners and platform lighting carry the design language down the line."},
        {"label": "ARRIVAL",  "body": "Walk-through ornament and lit displays at end-of-line — a destination, not a transfer."},
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 5 — Zone Index (overview of all 6 zones) =====
zone_index_ctx = {
    **PROJECT,
    "page_num": 5,
    "page_title": "The Program at a Glance",
    "standfirst": "Six stations, one design language. Here's how the program reads from end to end.",
    "zones": ZONES,
}


# ===== Slide 6 — Zone solo: Downtown Riverside (flagship, signature treatment) =====
zone_flagship_ctx = {
    **PROJECT,
    "page_num": 6,
    "zone_num": "01",
    "zone_name": "Downtown Riverside",
    "zone_subtitle": "The flagship station — civic centerpiece.",
    "included_elements": ZONES[0]["included_elements"] + [
        "Lighted walk-through arch at plaza forecourt",
        "Evening lighting program — platform + awning + curb-edge",
        "On-site QC walkthrough with RCTC Capital Projects",
    ],
    "hero_image": NO_IMAGE,
}


# ===== Slide 7 — Zones 2-up: La Sierra + Pedley =====
zone_2up_a_ctx = {
    **PROJECT,
    "page_num": 7,
    "page_title": "Program Zones",
    "standfirst": "Stations 02 and 03 — the gateway and the residential stop.",
    "zones": [ZONES[1], ZONES[2]],
}


# ===== Slide 8 — Zones 3-up: Hunter Park + Moreno Valley + Perris =====
zone_3up_ctx = {
    **PROJECT,
    "page_num": 8,
    "page_title": "Program Zones",
    "standfirst": "Stations 04, 05, and 06 — the outer line.",
    "zones": [ZONES[3], ZONES[4], ZONES[5]],
}


# ===== Slide 9 — Scope of Work =====
scope_ctx = {
    **PROJECT,
    "page_num": 9,
    "page_title": "Scope of Work",
    "standfirst": "What your investment includes, and what you can add on.",
    "includes": [
        "Custom-fabricated wreaths (every station entrance)",
        "Decorated and undecorated garland (six stations)",
        "Pole banner program (32 poles total, two artwork variants)",
        "Evening lighting program — Downtown Riverside (4 zones)",
        "Walk-through ornament arch — flagship station",
        "Install + strike per MetroLink operational windows",
        "On-site QC walkthrough with RCTC Capital Projects",
        "Storage between deinstall and 2027 program",
    ],
    "add_ons": [
        ("Spiral LED tree at flagship forecourt",      "+$8K"),
        ("Lighted bell display, plaza-side",           "+$5K"),
        ("Lighted snowflakes on platform railing (per station)", "+$2K each"),
        ("Lighted gift-box towers, plaza pair",        "+$7K"),
        ("Walk-through display refresh (existing arch)","+$3K"),
        ("Multi-year partnership (see Investment page)","Varies"),
    ],
}


# ===== Slide 10 — Case Study =====
case_study_ctx = {
    **PROJECT,
    "page_num": 10,
    "page_eyebrow": "CASE STUDY",
    "page_title": "Long Beach Transit · 2024",
    "standfirst": "A multi-station civic holiday program at scale, delivered in a single season.",
    "challenge": "Roll out a coordinated holiday décor program across 14 transit stations on a tight budget and an even tighter install window — all installs had to land within a 21-day overnight window without disrupting revenue service.",
    "approach":  "Standardized fabrication kits per station tier (flagship / standard / outpost). Pre-staged shipments at the operations yard. Crew rotated through stations on a strict overnight schedule with QC walks at sunrise.",
    "outcome":   "All 14 stations live on schedule. Zero revenue-service disruptions. Local press coverage at six of the fourteen stations. Program renewed for 2025 with three additional stations.",
    "hero_image": NO_IMAGE,
}


# ===== Slide 11 — Investment =====
investment_ctx = {
    **PROJECT,
    "page_num": 11,
    "page_title": "Investment",
    "standfirst": "Three levels of program. Pick what fits your season.",
    "tiers": [
        {
            "name": "ESSENTIAL", "rule_color": "gray", "tagline": "FLAGSHIP-ONLY PRESENCE",
            "highlights": ["Downtown Riverside only", "Core wreaths + garland", "Pole banner program (8 poles)", "Standard install + strike"],
            "price": "$184,500", "is_recommended": False,
        },
        {
            "name": "ENHANCED",  "rule_color": "red",  "tagline": "FULL LINE PROGRAM",
            "highlights": ["Everything in Essential, plus:", "All six stations covered", "Evening lighting program at flagship", "Walk-through ornament — flagship plaza", "MetroLink ops-window install"],
            "price": "$284,500", "is_recommended": True,
        },
        {
            "name": "SIGNATURE", "rule_color": "navy", "tagline": "REGIONAL DESTINATION",
            "highlights": ["Everything in Enhanced, plus:", "Spiral LED tree — flagship forecourt", "Lighted bell + gift-box towers", "Programmatic snowflake railing (all stations)", "On-site staffing during install + strike"],
            "price": "$384,500", "is_recommended": False,
        },
    ],
    "partnership_discounts": [
        ("2-YEAR", "4% OFF"),
        ("3-YEAR", "6% OFF"),
        ("5-YEAR", "9% OFF"),
    ],
    "footer_note": "Pricing valid 30 days from proposal date. Fabrication must be locked by Aug 22, 2026.",
}


# ===== Slide 12 — Terms & Next Steps =====
terms_ctx = {
    **PROJECT,
    "page_num": 12,
    "page_title": "Terms & Next Steps",
    "standfirst": "The critical dates and terms for the 2026 program.",
    "critical_dates": [
        ("October 30, 2026", "Execute by this date to guarantee the install schedule."),
        ("August 22, 2026",  "All custom fabrication must be approved by this date (90 days pre-Go Live)."),
    ],
    "term_panels": [
        ("PAYMENT SCHEDULE",   "30% deposit on signing — required to lock the install schedule. 40% on fabrication start. 30% on go-live. Net-15 terms on final invoice."),
        ("INSURANCE & PERMITS","$5M Umbrella over $1M/$2M Commercial General Liability and $1M Auto; full Workers' Comp at statutory limits. Certificates issued to RCTC at signing. MetroLink coordination handled by RCTC; we provide full documentation support."),
        ("CHANGE ORDERS",      "Includes 2 creative revision rounds before Fabrication Lock (Aug 22, 2026). Scope or timeline changes after that date follow our standard change-order workflow — written approval required, priced at materials + 35%."),
        ("PROPOSAL VALIDITY",  "This proposal is valid 60 days from May 12, 2026. Materials pricing subject to market conditions thereafter. Sign by Oct 30 to lock schedule."),
    ],
    "after_approval_steps": ["Kickoff call within 48 hrs", "Creative window opens", "Renderings final by Aug 1"],
}


# ===== Slide 13 — Sign-off =====
sign_off_ctx = {
    **PROJECT,
    "page_num": 13,
    "page_title": "Let's Make It Happen",
    "standfirst": "Sign below to launch the 2026 MetroLink Holiday Program.",
    "what_youre_approving": "The 2026 Riverside MetroLink Holiday Program — six stations from Downtown Riverside through Perris-Downtown, live Nov 20, 2026 through Jan 5, 2027, at the tier and add-ons you select on the Investment page.",
    "client_party_label":   "RCTC AUTHORIZATION",
    "stnicks_party_label":  "ST. NICK'S AUTHORIZED SIGNATURE",
    "digital_signing_note": "Prefer to sign digitally? Use the Canva e-signature link in your email. Questions? Reply directly — we'll respond within 24 hours.",
}


# ===== Slide 14 — About St. Nick's =====
about_ctx = {
    **PROJECT,
    "page_num": 14,
    "page_title": "About St. Nick's",
    "standfirst": "25 years of large-scale holiday design, installation, and service.",
    "company_facts": [
        "Founded 1998 (dba St. Nick's) — T&G Global, LLC",
        "14 full-time team · 30–45 seasonal staff",
        "B-General Building Contractor #990427",
        "Certified Small Business Supplier #1626660",
        "$5M Umbrella · $1M/$2M GL · $1M Auto · Full Workers' Comp",
        "200+ commercial venues across North America",
    ],
    "team": [
        {"name": "Nicholas Adams",   "role": "Founder"},
        {"name": "Wade Francis",     "role": "Chief Financial Officer"},
        {"name": "Brenda Sheridan",  "role": "Director of Operations"},
        {"name": "Daniel Christenson","role": "Director of Sales"},
        {"name": "Stephanie Escobar","role": "Creative Director"},
        {"name": "Carlos Vasquez & Alonso Salazar", "role": "Senior Installers / Project Managers"},
    ],
    "contact_strip": "ST-NICKS.COM  ·  (562) 438-0017  ·  6861 Walker St, La Palma, CA 90623  ·  © 2026 St. Nick's Christmas Lighting & Décor",
}
```

- [ ] **Step 2: Verify the fixture imports cleanly**

```bash
.venv/bin/python -c "from tests.fixtures import riverside; print(riverside.PROJECT['client_short']); print(len(riverside.ZONES), 'zones')"
```

Expected: prints `RCTC METROLINK` and `6 zones`.

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/riverside.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): reshape Riverside fixture as zone-heavy multi-station

Six MetroLink stations as 6 named zones. Drives the zone-grouped
layouts: zone_index (slide 5 overview), zone_solo for the flagship,
zone_2up + zone_3up for the outer stations. Provides the second
fixture (with pier_39.py) needed by Plan 2-prime to exercise both
"destination path" (3 zones, master pattern) and "zone-heavy path"
(6+ zones).

The previous abstract-categories shape (showcase_*) is gone —
those layouts moved to archive in Task 1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Reset `tests/test_layouts.py` LAYOUT_CASES; conftest.py update

**Files:**
- Modify: `tests/test_layouts.py`
- Modify: `tests/conftest.py` — extend `render_layout` to accept fixture-module argument so tests can pull from either `pier_39` or `riverside`

- [ ] **Step 1: Update `tests/conftest.py`**

Replace the contents with:

```python
"""Test fixtures and helpers shared across the layout test suite.

Plan 2-prime keeps rendering glue inside tests/ — Plan 3 will write the
production render pipeline at skill_assets/generate.py. This helper
exists only to drive the layout tests.
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
    """Render a layout HTML file to PDF. Returns the PDF path.

    Args:
        layout_name: filename stem under skill_assets/layouts/, e.g. "cover".
        ctx: Python dict passed to Jinja2 as the rendering context.
        out_name: optional output filename stem. Defaults to layout_name.
            Use this when the same layout is rendered twice with different
            ctxs (e.g. zone_solo for two zones from the same fixture).

    Returns:
        Path to the rendered PDF file in tests/_output/{out_name}.pdf.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _render(layout_name: str, ctx: dict[str, Any], out_name: str | None = None) -> Path:
        template = jinja_env.get_template(f"{layout_name}.html")
        html_string = template.render(**ctx)
        out = OUTPUT_DIR / f"{out_name or layout_name}.pdf"
        HTML(string=html_string, base_url=str(LAYOUTS_DIR)).write_pdf(target=str(out))
        return out

    return _render
```

- [ ] **Step 2: Replace `tests/test_layouts.py`**

```python
"""Parametrized layout tests — one entry per layout-render in skill_assets/layouts/.

Each LAYOUT_CASES tuple is (out_name, layout_name, fixture_module, ctx_attr,
expected_text):
- out_name: the PDF filename stem written to tests/_output/
- layout_name: the .html template under skill_assets/layouts/
- fixture_module: "pier_39" or "riverside" — which fixture module supplies ctx
- ctx_attr: name of the ctx dict on that module
- expected_text: substrings that must appear in the rendered PDF text

The same layout may be rendered multiple times with different ctxs (e.g.
zone_solo with zone_01 and zone_02 fixtures). out_name disambiguates.

Per Plan 2-prime: every PDF embeds Roboto + Poppins; no other families.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import fitz  # pymupdf
import pytest

EXPECTED_WIDTH_PT = 13.333 * 72   # 959.976 pt
EXPECTED_HEIGHT_PT = 7.5 * 72     # 540.000 pt
DIMENSION_TOLERANCE_PT = 1.0


def _font_names(doc: fitz.Document) -> list[str]:
    names: list[str] = []
    for page in doc:
        for entry in page.get_fonts():
            names.append(entry[3])
    return names


def _assert_font_family_present(doc: fitz.Document, family: str) -> None:
    names = _font_names(doc)
    assert any(family in n for n in names), (
        f"No embedded font with '{family}' in its name. Got: {names}. "
        f"WeasyPrint may have fallen back to a system font — check brand.css "
        f"@font-face urls and font file presence."
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
    raw = " ".join(page.get_text() for page in doc)
    text = " ".join(raw.split()).casefold()
    for fragment in expected:
        assert fragment.casefold() in text, (
            f"Expected fragment {fragment!r} not found in extracted PDF text."
        )


# (out_name, layout_name, fixture_module, ctx_attr, expected_text)
# Each Plan 2-prime layout task appends one or more entries here.
LAYOUT_CASES: list[tuple[str, str, str, str, list[str]]] = [
    # appended per task
]


@pytest.mark.parametrize("out_name,layout_name,fixture_module,ctx_attr,expected_text", LAYOUT_CASES)
def test_layout_renders(out_name, layout_name, fixture_module, ctx_attr, expected_text, render_layout):
    fixtures = importlib.import_module(f"fixtures.{fixture_module}")
    ctx = getattr(fixtures, ctx_attr)
    pdf_path: Path = render_layout(layout_name, ctx, out_name=out_name)

    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 5000, "PDF suspiciously small"

    with fitz.open(pdf_path) as doc:
        assert doc.page_count == 1, f"Expected 1 page, got {doc.page_count}"
        _assert_dimensions(doc)
        _assert_font_family_present(doc, "Roboto")
        _assert_font_family_present(doc, "Poppins")
        _assert_text_present(doc, expected_text)


def test_all_layouts_rendered():
    """After the suite runs, every PDF named in LAYOUT_CASES must exist on disk."""
    if not LAYOUT_CASES:
        pytest.skip("LAYOUT_CASES is empty.")

    output_dir = Path(__file__).resolve().parent / "_output"
    expected_pdfs = {f"{out}.pdf" for out, _, _, _, _ in LAYOUT_CASES}
    actual_pdfs = {p.name for p in output_dir.glob("*.pdf")}
    missing = expected_pdfs - actual_pdfs
    assert not missing, f"Missing rendered PDFs: {missing}"
```

- [ ] **Step 3: Run the suite to confirm baseline**

```bash
.venv/bin/pytest -v
```

Expected: all foundation tests (Tasks 1–7) pass; `test_layout_renders` does not parametrize (LAYOUT_CASES is empty); `test_all_layouts_rendered` skips with reason "LAYOUT_CASES is empty."

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): reset layout test harness for master-driven layouts

Generalises the layout test contract:
- LAYOUT_CASES is now a 5-tuple (out_name, layout_name, fixture_module,
  ctx_attr, expected_text) — supports rendering the same layout file
  multiple times with different ctxs (e.g. zone_solo for each zone),
  output disambiguated by out_name.
- conftest.py render_layout fixture takes optional out_name kwarg.
- LAYOUT_CASES is empty; tasks 9-23 each append entries.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — Layouts (TDD per layout)

> **Pattern for every layout task in this phase:**
> 1. Append `LAYOUT_CASES` entry/entries to `tests/test_layouts.py`.
> 2. Run `pytest tests/test_layouts.py::test_layout_renders -v -k <out_name>` — confirm new test fails (template not found).
> 3. Look at the master page render at `Master Proposal Reference/master-pages/page-NN.png` for the visual reference.
> 4. Write the layout HTML file under `skill_assets/layouts/`.
> 5. Run the test again — confirm it passes.
> 6. Render the PDF and eyeball it against the master page. Iterate on the layout HTML until the visual matches.
> 7. Commit when satisfied.

**Implementer note:** every layout in this phase extends `base.html`. Layouts that should NOT show the standard footer must override `{% block footer %}{% endblock %}` (empty). Layouts on a dark background must override `{% block body_class %}page-dark{% endblock %}`. Layout-specific styles go in `{% block extra_head %}<style>...</style>{% endblock %}`.

**Two layouts (Tasks 9–10) are written in full HTML below to lock the chrome integration patterns. Tasks 11–23 specify structure, ctx fields, master-page reference, and design constraints; the implementer writes the CSS using the worked examples plus the master PNG as guides.**

---

### Task 9: `cover.html` (FULLY SPECIFIED — locks the dark-feature chrome pattern)

**Files:**
- Modify: `tests/test_layouts.py` (append 2 LAYOUT_CASES — one for each fixture)
- Create: `skill_assets/layouts/cover.html`

**Master reference:** `Master Proposal Reference/master-pages/page-01.png`

- [ ] **Step 1: Append LAYOUT_CASES entries**

Add inside the `LAYOUT_CASES = [` list:

```python
    ("cover_pier39",    "cover", "pier_39",   "cover_ctx", [
        "Pier 39", "San Francisco", "2026 HOLIDAY SEASON", "St. Nick's",
    ]),
    ("cover_riverside", "cover", "riverside", "cover_ctx", [
        "Riverside MetroLink", "Six-Station", "2026 HOLIDAY SEASON", "St. Nick's",
    ]),
```

- [ ] **Step 2: Verify both tests fail with TemplateNotFound**

```bash
.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k cover
```

Expected: 2 FAIL — `TemplateNotFound: 'cover.html'`.

- [ ] **Step 3: Create `skill_assets/layouts/cover.html`**

```html
{% extends "base.html" %}
{% block body_class %}page-dark{% endblock %}
{% block footer %}{% endblock %}
{% block layout_version %}<!-- layout-version: 2026-05-03 -->{% endblock %}
{% block title %}{{ project_name }} — Cover{% endblock %}
{% block extra_head %}
<style>
  /* Cover-only chrome adjustments. The master cover splits the page into
     a left text panel and a right hero-image panel, both on charcoal but
     the right slightly lifted with a subtle gradient. */
  body.page-dark .page-content {
    /* Override the default content positioning — cover uses full bleed. */
    top: 0; left: 0; right: 0; bottom: 0;
    padding: 0;
  }

  .cover-grid {
    display: grid;
    grid-template-columns: 5in 1fr;
    height: 7.5in;
  }

  .cover-left {
    background: var(--color-charcoal);
    padding: 1.0in 0.55in 0.55in 0.55in;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    color: var(--color-light);
  }

  .cover-right {
    background: #2a2a2a;  /* Subtle lift from the left charcoal. */
    position: relative;
    overflow: hidden;
  }
  .cover-right .hero-placeholder {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-family: var(--font-body);
    font-style: italic;
    color: rgba(236, 239, 241, 0.4);
    font-size: var(--text-sm);
  }

  .cover-rule {
    width: 0.4in;
    height: 2pt;
    background: var(--color-red);
    margin-bottom: var(--space-3);
  }
  .cover-season {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 11pt;
    letter-spacing: 0.15em;
    color: var(--color-red);
    margin-bottom: var(--space-3);
  }
  .cover-project {
    font-family: var(--font-display);
    font-weight: 900;
    font-size: 80pt;
    line-height: 0.9;
    letter-spacing: -0.03em;
    color: var(--color-light);
    margin: 0 0 var(--space-3) 0;
  }
  .cover-subtitle {
    font-family: var(--font-body);
    font-weight: 300;
    font-size: 18pt;
    color: var(--color-light);
    opacity: 0.75;
    margin: 0;
  }

  .cover-prep-block {
    font-family: var(--font-body);
    font-size: 9pt;
    line-height: 1.5;
    color: var(--color-light);
    opacity: 0.85;
  }
  .cover-prep-label {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.18em;
    color: var(--color-light);
    opacity: 0.6;
    margin-bottom: var(--space-1);
  }
  .cover-prep-name {
    font-weight: 600;
    color: var(--color-light);
    opacity: 1.0;
  }
</style>
{% endblock %}
{% block content %}
<div class="cover-grid">
  <div class="cover-left">
    <div>
      <div class="cover-rule"></div>
      <div class="cover-season">{{ season_label }}</div>
      <h1 class="cover-project">{{ project_name }}</h1>
      <div class="cover-subtitle">{{ project_subtitle }}</div>
    </div>

    <div class="cover-prep-block">
      <div class="cover-prep-label">PREPARED BY</div>
      <div class="cover-prep-name">{{ prepared_by_org }}</div>
      <div>Proposal Date: {{ proposal_date }}</div>
    </div>
  </div>

  <div class="cover-right">
    <div class="hero-placeholder">[ {{ project_name }} hero image — Plan 3 supplies real photo ]</div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Verify both tests pass**

```bash
.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k cover
```

Expected: 2 PASSED.

- [ ] **Step 5: Eyeball both rendered PDFs against `master-pages/page-01.png`**

Open `tests/_output/cover_pier39.pdf` and `tests/_output/cover_riverside.pdf`. Confirm visually:
- Left panel (~5") in solid charcoal with text content; right panel (~8.3") slightly lifted with hero-image placeholder.
- Top-left ST. NICK'S brand mark (white).
- Small red rule above "2026 HOLIDAY SEASON" (red).
- Big "Pier 39" / "Riverside MetroLink" headline in Poppins Black ~80pt.
- Subtitle ("San Francisco" / "Six-Station Civic Holiday Program") in light gray below.
- Bottom-left "PREPARED BY" block.
- No footer (layout overrides {% block footer %}).

If any of these fail, iterate on the CSS until they match the master.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/cover.html tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): add cover.html — dark feature page

Master-derived cover: 5"+8.3" two-column dark page. Left panel holds
project name in Poppins Black 80pt, season eyebrow in red, prepared-by
metadata at the bottom. Right panel reserves the hero-image area
(Plan 3 will inject real photo references).

Locks the dark-feature chrome pattern: extends base.html with
page-dark body class and empty {% block footer %} override.
Subsequent dark-feature layouts (creative_vision, zone_solo_fullbleed,
about) follow the same pattern.

Tested against pier_39 and riverside fixtures.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: `exec_summary.html` (FULLY SPECIFIED — locks the light-page-with-side-panel chrome pattern)

**Files:**
- Modify: `tests/test_layouts.py` (append 2 LAYOUT_CASES)
- Create: `skill_assets/layouts/exec_summary.html`

**Master reference:** `Master Proposal Reference/master-pages/page-02.png`

- [ ] **Step 1: Append LAYOUT_CASES entries**

```python
    ("exec_summary_pier39",    "exec_summary", "pier_39",   "exec_summary_ctx",
        ["Executive Summary", "destination-scale", "Turnkey Delivery", "FABRICATION LOCK", "Aug 22, 2026"]),
    ("exec_summary_riverside", "exec_summary", "riverside", "exec_summary_ctx",
        ["Executive Summary", "Six-Station", "Civic Pride", "FABRICATION LOCK", "Aug 22, 2026"]),
```

- [ ] **Step 2: Verify the new tests fail**

```bash
.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k exec_summary
```

Expected: 2 FAIL with `TemplateNotFound`.

- [ ] **Step 3: Create `skill_assets/layouts/exec_summary.html`**

```html
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-03 -->{% endblock %}
{% block title %}{{ project_short }} — {{ page_title }}{% endblock %}
{% block extra_head %}
<style>
  .es-grid {
    display: grid;
    grid-template-columns: 1fr 4.5in;
    grid-template-rows: auto 1fr auto;
    column-gap: var(--space-7);
    height: 100%;
  }
  .es-title-area    { grid-column: 1; grid-row: 1; }
  .es-body-area     { grid-column: 1; grid-row: 2; padding-top: var(--space-4); }
  .es-pillars       { grid-column: 1 / -1; grid-row: 3; padding-top: var(--space-5); }
  .es-glance        { grid-column: 2; grid-row: 1 / 3; align-self: start; }

  .es-body-area p {
    font-family: var(--font-body);
    font-size: var(--text-sm);
    line-height: 1.55;
    color: var(--color-charcoal);
    margin-bottom: var(--space-3);
  }

  .es-glance {
    background: var(--color-panel);
    border-radius: 4pt;
    padding: var(--space-5) var(--space-5);
    box-shadow: 0 1pt 3pt rgba(0, 0, 0, 0.08);
  }
  .es-glance-header {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-sm);
    color: var(--color-red);
    margin-bottom: var(--space-3);
    letter-spacing: 0.06em;
  }
  .es-glance-row {
    margin-bottom: var(--space-3);
  }
  .es-glance-label {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.10em;
    color: var(--color-gray);
    margin-bottom: 2pt;
  }
  .es-glance-label.deadline { color: var(--color-red); }
  .es-glance-value {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-sm);
    color: var(--color-charcoal);
  }

  .es-pillars-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
  }
  .es-pillar {
    background: var(--color-panel);
    border-radius: 4pt;
    padding: var(--space-4);
    box-shadow: 0 1pt 3pt rgba(0, 0, 0, 0.08);
  }
  .es-pillar-title {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-charcoal);
    margin-bottom: var(--space-2);
  }
  .es-pillar-body {
    font-family: var(--font-body);
    font-size: var(--text-sm);
    line-height: 1.5;
    color: var(--color-charcoal);
  }
</style>
{% endblock %}
{% block content %}
<div class="es-grid">

  <div class="es-title-area">
    <h1 class="page-title">{{ page_title }}</h1>
    <div class="standfirst">{{ standfirst }}</div>
  </div>

  <div class="es-body-area">
    {% for p in body_paragraphs %}<p>{{ p }}</p>{% endfor %}
  </div>

  <aside class="es-glance">
    <div class="es-glance-header">AT A GLANCE</div>
    {% for label, value, is_deadline in at_a_glance %}
    <div class="es-glance-row">
      <div class="es-glance-label{% if is_deadline %} deadline{% endif %}">{{ label }}</div>
      <div class="es-glance-value">{{ value }}</div>
    </div>
    {% endfor %}
  </aside>

  <div class="es-pillars">
    <div class="es-pillars-grid">
      {% for pillar in pillars %}
      <div class="es-pillar">
        <div class="es-pillar-title">{{ pillar.title }}</div>
        <div class="es-pillar-body">{{ pillar.body }}</div>
      </div>
      {% endfor %}
    </div>
  </div>

</div>
{% endblock %}
```

- [ ] **Step 4: Verify tests pass**

```bash
.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k exec_summary
```

Expected: 2 PASSED.

- [ ] **Step 5: Eyeball against `master-pages/page-02.png`**

Confirm: page title in Poppins Black ~50pt charcoal, italic gray standfirst, body left, AT A GLANCE side panel right with FABRICATION LOCK + SIGNING DEADLINE labels in brand red, 3 pillar cards across the bottom. Footer present (St. Nick's · 2026 HOLIDAY PROPOSAL · client_short on left, "2 / 13" on right).

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/exec_summary.html tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-2-prime): add exec_summary.html — light page with side panel

Master-derived layout: page title + standfirst + body left, AT A GLANCE
sidebar right, 3 pillar cards across the bottom. Brand-red labels for
FABRICATION LOCK and SIGNING DEADLINE (driven by the third tuple field
in at_a_glance ctx). Cards use --color-panel and the standard subtle
shadow.

Locks the light-page-with-side-panel chrome pattern. Subsequent layouts
(understanding, scope, terms) follow the same pattern with different
body grids.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: `understanding.html` — light page with 4-card grid

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/understanding.html`

**Master reference:** `Master Proposal Reference/master-pages/page-03.png`

**Implementer guidance:** This layout follows the light-page chrome from `exec_summary.html` (page title + standfirst + footer). Body is a 2×2 grid of cards. Each card uses the `.card.red-rule` pattern (already in brand.css): light-gray background with a 3pt brand-red left edge accent. Card title is in brand red caps (use the `.label` utility class for size and tracking). Card body is Poppins Regular at `var(--text-sm)`.

**ctx fields used:** `page_title`, `standfirst`, `panels` (list of `{title, body}` dicts), plus the chrome fields `project_year`, `client_short`, `page_num`, `page_total`.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("understanding_pier39",    "understanding", "pier_39",   "understanding_ctx",
        ["Our Understanding", "Pier 39 is San Francisco's", "VENUE & CONTEXT", "GOALS FOR 2026", "KEY CONSTRAINTS"]),
    ("understanding_riverside", "understanding", "riverside", "understanding_ctx",
        ["Our Understanding", "MetroLink line connects", "VENUE & CONTEXT", "GOALS FOR 2026", "KEY CONSTRAINTS"]),
```

- [ ] **Step 2: Confirm tests fail (TemplateNotFound)**

```bash
.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k understanding
```

- [ ] **Step 3: Write `skill_assets/layouts/understanding.html`**

Layout structure (Jinja, with the implementer to write the precise CSS based on the master page):
1. `{% extends "base.html" %}` — inherits page-light bg, header, footer.
2. `{% block extra_head %}` containing `<style>` for: `.un-grid` (2x2 grid using `display:grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: var(--space-4);`), `.un-card` (card with red left rule), `.un-card-title` (brand red caps), `.un-card-body` (Poppins Regular text-sm).
3. `{% block content %}` with: page title (`<h1 class="page-title">`) + standfirst (`<div class="standfirst">`) at top, then `.un-grid` containing 4 cards, one per `panels` entry.

The implementer can read `exec_summary.html` for chrome integration and the master PNG for visual proportions. Reference the existing `.card.red-rule` styles in brand.css if they fit; otherwise add card styles inline.

- [ ] **Step 4: Confirm tests pass**

```bash
.venv/bin/pytest tests/test_layouts.py::test_layout_renders -v -k understanding
```

Expected: 2 PASSED.

- [ ] **Step 5: Eyeball against `master-pages/page-03.png`**

- [ ] **Step 6: Commit**

```bash
git add skill_assets/layouts/understanding.html tests/test_layouts.py
git commit -m "feat(plan-2-prime): add understanding.html — 2x2 red-rule cards

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 12: `creative_vision.html` — dark feature page

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/creative_vision.html`

**Master reference:** `Master Proposal Reference/master-pages/page-04.png`

**Implementer guidance:** Dark page (extend base with `{% block body_class %}page-dark{% endblock %}`). Footer hidden (`{% block footer %}{% endblock %}`). Same body content pattern as `exec_summary.html` but inverted colors (white text on charcoal). Layout: page title + standfirst at top, then a 2-column body — left column has `DESIGN DIRECTION` red eyebrow + design phrase as a hero ("Bayside Twilight." in Poppins Black ~36pt) + design_direction_body paragraph; right column has the hero-image placeholder. Below the 2-column body, a 3-card phase strip (`ARRIVE / EXPLORE / CELEBRATE`) — each card is darker than the page bg, has a thin red top rule, label in white sans-serif, body in opacity 0.7 white.

**ctx fields used:** `page_title`, `standfirst`, `design_phrase`, `design_direction_body`, `phases` (list of `{label, body}`), `hero_image`. Footer is suppressed so chrome ctx fields not needed.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("creative_vision_pier39",    "creative_vision", "pier_39",   "creative_vision_ctx",
        ["Creative Vision", "Bayside Twilight", "ARRIVE", "EXPLORE", "CELEBRATE"]),
    ("creative_vision_riverside", "creative_vision", "riverside", "creative_vision_ctx",
        ["Creative Vision", "Holiday Express", "WELCOME", "JOURNEY", "ARRIVAL"]),
```

- [ ] **Step 2-6:** Follow the same pattern as Task 11 (run failing test, write layout, run passing test, eyeball, commit). Use cover.html for dark-page chrome reference and exec_summary.html for the page-title + standfirst + grid pattern.

Commit message: `feat(plan-2-prime): add creative_vision.html — dark feature page with 3 phases`

---

### Task 13: `zone_solo.html` — single zone, light bg, image right + bullet list left

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/zone_solo.html`

**Master reference:** `Master Proposal Reference/master-pages/page-05.png` (also page-06, same pattern with different ctx).

**Implementer guidance:** Light page, footer present. Top: `ZONE 0N` red eyebrow (use `.eyebrow` utility class) + zone name in Poppins Black ~50pt + zone_subtitle as italic gray standfirst. Body: 2-column grid — left column has `INCLUDED ELEMENTS` red caps label + bulleted list of `included_elements` items in red bullets + charcoal text; right column has hero image placeholder (`#1C1C1C`-ish dark rectangle with placeholder text inside it).

**ctx fields used:** `zone_num`, `zone_name`, `zone_subtitle`, `included_elements` (list of strings), `hero_image`, plus the chrome fields.

- [ ] **Step 1: Append LAYOUT_CASES** (rendered twice from pier_39 — one per non-signature zone — plus once from riverside as the flagship)

```python
    ("zone_solo_pier39_z01",     "zone_solo", "pier_39",   "zone_01_ctx",
        ["ZONE 01", "Embarcadero Arrival", "28' illuminated entry arch", "Dusk-to-dawn programming"]),
    ("zone_solo_pier39_z02",     "zone_solo", "pier_39",   "zone_02_ctx",
        ["ZONE 02", "Pier Promenade", "Suspended starlight canopy", "Hot cocoa concierge"]),
    ("zone_solo_riverside_flag", "zone_solo", "riverside", "zone_flagship_ctx",
        ["ZONE 01", "Downtown Riverside", "Custom-fabricated wreaths", "Evening lighting program"]),
```

- [ ] **Steps 2-6:** Standard pattern. Reference exec_summary.html for chrome.

Commit message: `feat(plan-2-prime): add zone_solo.html — single zone with image+bullets`

---

### Task 14: `zone_solo_fullbleed.html` — signature zone, dark bg, full-bleed image top + text panel bottom

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/zone_solo_fullbleed.html`

**Master reference:** `Master Proposal Reference/master-pages/page-07.png`

**Implementer guidance:** Dark page (`page-dark`), footer hidden. Page splits horizontally: top ~65% is hero image area (full-bleed, dark placeholder); bottom ~35% is a darker text panel. Text panel contents: `ZONE 0N` red eyebrow, zone name in Poppins Black ~36pt white, italic standfirst beneath, then a 2-column bulleted list of included_elements (split roughly in half). Top-right shows the page number small in light gray (footer is hidden but page number still present — the master keeps `7 / 13` visible on the dark page in the bottom right; check the PNG).

**ctx fields used:** Same as zone_solo. Plus `page_num`, `page_total` for the small page number.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("zone_solo_fullbleed_pier39_z03", "zone_solo_fullbleed", "pier_39", "zone_03_ctx",
        ["ZONE 03", "Bay Terrace", "40' walkthrough signature tree", "synchronized music"]),
```

- [ ] **Steps 2-6:** Standard pattern. Reference cover.html for dark-page chrome.

Commit message: `feat(plan-2-prime): add zone_solo_fullbleed.html — signature zone fullbleed`

---

### Task 15: `zone_2up.html` — two zones share a slide

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/zone_2up.html`

**Master reference:** No exact master page (zone_2up is a Plan 2-prime addition for zone-heavy decks). Use `master-pages/page-05.png` as the per-zone treatment reference, but split the page in half and show each zone's `ZONE 0N + name + standfirst + bullets` in its own column. Page title at top: `Program Zones` (from `page_title` ctx field).

**Implementer guidance:** Light page, footer present. Top: page title (small — this is a content page not a feature page, so use `<h1 class="page-title">` but at maybe ~36pt, not the full 50pt). Body: 2-column grid, each column gets one zone's stack (eyebrow + name + subtitle + bulleted included_elements). No hero images — this is a text-only page since fitting two zone images on one page reads cluttered.

**ctx fields used:** `page_title`, `standfirst`, `zones` (list of 2 zone dicts, each with `num/name/subtitle/included_elements`).

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("zone_2up_riverside", "zone_2up", "riverside", "zone_2up_a_ctx",
        ["Program Zones", "ZONE 02", "La Sierra", "ZONE 03", "Pedley"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add zone_2up.html — 2 zones per slide`

---

### Task 16: `zone_3up.html` — three zones share a slide

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/zone_3up.html`

**Implementer guidance:** Same as zone_2up but 3 columns. Tighter typography (zone names at maybe `var(--text-xl)` instead of `var(--text-2xl)`). Bullet lists may need to be limited to top 3-4 items per zone to fit cleanly.

**ctx fields used:** Same as zone_2up but `zones` has 3 entries.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("zone_3up_riverside", "zone_3up", "riverside", "zone_3up_ctx",
        ["Program Zones", "ZONE 04", "Hunter Park", "ZONE 05", "Moreno Valley", "ZONE 06", "Perris"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add zone_3up.html — 3 zones per slide`

---

### Task 17: `zone_index.html` — overview of all zones

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/zone_index.html`

**Implementer guidance:** Light page, footer present. Page title (e.g. `The Program at a Glance`) + standfirst at top. Body: a vertical list of all zones, each row showing `ZONE 0N` (red eyebrow, fixed-width column) + zone name (Poppins Bold) + zone subtitle (gray italic). Compact — designed to fit 5-8 zones on one page. No bullet lists per zone (those go on the per-zone pages).

**ctx fields used:** `page_title`, `standfirst`, `zones` (list of all zones).

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("zone_index_riverside", "zone_index", "riverside", "zone_index_ctx",
        ["The Program at a Glance", "Six stations", "Downtown Riverside", "La Sierra", "Pedley", "Hunter Park", "Moreno Valley", "Perris"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add zone_index.html — all-zones overview`

---

### Task 18: `scope.html` — light page, two cards (green + red headers)

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/scope.html`

**Master reference:** `Master Proposal Reference/master-pages/page-08.png`

**Implementer guidance:** Light page, footer present. Top: page title + standfirst. Body: 2-column card grid using the `.card.has-header` pattern (already in brand.css). Left card has `.green` modifier showing `YOUR PROGRAM INCLUDES` in white on green; bullet list of `includes`. Right card has `.red` modifier showing `OPTIONAL ADD-ONS` in white on brand red; each item is a 2-column row (item description left, price right). Use the existing `.card`, `.card.has-header`, `.green`, `.red`, `.card-header`, `.card-body` classes from brand.css.

**ctx fields used:** `page_title`, `standfirst`, `includes` (list of strings), `add_ons` (list of `(description, price)` tuples).

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("scope_pier39",    "scope", "pier_39",   "scope_ctx",
        ["Scope of Work", "YOUR PROGRAM INCLUDES", "OPTIONAL ADD-ONS", "+$24K", "Synchronized music"]),
    ("scope_riverside", "scope", "riverside", "scope_ctx",
        ["Scope of Work", "YOUR PROGRAM INCLUDES", "OPTIONAL ADD-ONS", "Custom-fabricated wreaths"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add scope.html — green-includes + red-addons cards`

---

### Task 19: `case_study.html` — light page, image left + 3-section narrative right

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/case_study.html`

**Master reference:** `Master Proposal Reference/master-pages/page-09.png`

**Implementer guidance:** Light page, footer present. Page-eyebrow `CASE STUDY` (red) above the page title. Body: 2-column grid, left column has hero image placeholder (~5" wide), right column has three stacked sections (`THE CHALLENGE`, `OUR APPROACH`, `THE OUTCOME`) — each with red caps label + body paragraph.

**ctx fields used:** `page_eyebrow`, `page_title`, `standfirst`, `challenge`, `approach`, `outcome`, `hero_image`.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("case_study_pier39",    "case_study", "pier_39",   "case_study_ctx",
        ["CASE STUDY", "Oregon Zoo", "ZooLights 2025", "31% YoY increase"]),
    ("case_study_riverside", "case_study", "riverside", "case_study_ctx",
        ["CASE STUDY", "Long Beach Transit", "14 transit stations", "Zero revenue-service disruptions"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add case_study.html — image left + Challenge/Approach/Outcome`

---

### Task 20: `investment.html` — 3 tier cards + dark partnership panel

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/investment.html`

**Master reference:** `Master Proposal Reference/master-pages/page-10.png`

**Implementer guidance:** Light page, footer present. Top: page title + standfirst. Body: 3 tier cards in a row, each with a top rule (gray for first, red for recommended, navy for last). The recommended card has a `★ RECOMMENDED ★` red banner above and a slightly tinted bg (`#FFF8F8`). Each card: tier name (Poppins Black ~24pt), tagline (red caps), thin gray rule, bulleted highlights, big price (Poppins Black ~32pt), `ALL-IN · TAX EXCLUDED` footnote. Below the cards: a dark partnership panel (`background: var(--color-charcoal)`, white text) showing `MULTI-YEAR PARTNERSHIP / Lock in rates and save:` left + 3 discount columns right (`2-YEAR 4% OFF`, `3-YEAR 6% OFF`, `5-YEAR 9% OFF`). At the very bottom: small footer note in gray.

**ctx fields used:** `page_title`, `standfirst`, `tiers` (list of `{name, rule_color, tagline, highlights, price, is_recommended}`), `partnership_discounts` (list of `(label, off)`), `footer_note`.

**Implementer note:** Watch for the WeasyPrint flex-in-grid bug from Plan 2 (commit `90ddea0`): if a tier card is a flex container inside a grid cell with `gap`, WeasyPrint may miscalculate intrinsic height and produce multi-page output. Use `margin-bottom` on children rather than `gap` on the flex parent if this happens.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("investment_pier39",    "investment", "pier_39",   "investment_ctx",
        ["Investment", "Three levels", "ESSENTIAL", "ENHANCED", "SIGNATURE", "$225,000", "$345,000", "$485,000", "RECOMMENDED", "MULTI-YEAR PARTNERSHIP", "9% OFF"]),
    ("investment_riverside", "investment", "riverside", "investment_ctx",
        ["Investment", "ESSENTIAL", "ENHANCED", "SIGNATURE", "$184,500", "$284,500", "$384,500", "RECOMMENDED", "MULTI-YEAR PARTNERSHIP"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add investment.html — 3 tiers + partnership discounts`

---

### Task 21: `terms.html` — light page, red date banner + 4 cards + dark workflow strip

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/terms.html`

**Master reference:** `Master Proposal Reference/master-pages/page-11.png`

**Implementer guidance:** Light page, footer present. Top: page title + standfirst. Then a full-width brand-red banner showing 2 critical_dates side-by-side: each with a date (white, Poppins Black ~24pt) + description (white, Poppins Regular). Below the banner: 2×2 card grid (Payment Schedule, Insurance & Permits, Change Orders, Proposal Validity) — each card is a `.card` with no header bar but a brand-red caps title at top + body text. At the bottom of the page (above the footer): a dark workflow strip showing `AFTER APPROVAL → ` + 3 steps separated by `·`.

**ctx fields used:** `page_title`, `standfirst`, `critical_dates` (list of 2 `(date, description)` tuples), `term_panels` (list of 4 `(title, body)` tuples), `after_approval_steps` (list of strings).

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("terms_pier39",    "terms", "pier_39",   "terms_ctx",
        ["Terms & Next Steps", "November 14, 2026", "August 22, 2026", "PAYMENT SCHEDULE", "INSURANCE & PERMITS", "AFTER APPROVAL"]),
    ("terms_riverside", "terms", "riverside", "terms_ctx",
        ["Terms & Next Steps", "October 30, 2026", "August 22, 2026", "PAYMENT SCHEDULE", "INSURANCE & PERMITS", "AFTER APPROVAL"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add terms.html — red date banner + 2x2 cards + workflow strip`

---

### Task 22: `sign_off.html` — light page, what-you're-approving + 2 signature blocks

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/sign_off.html`

**Master reference:** `Master Proposal Reference/master-pages/page-12.png`

**Implementer guidance:** Light page, footer present. Top: page title (`Let's Make It Happen`) + standfirst. Then a `.card` with `WHAT YOU'RE APPROVING` red caps label + `what_youre_approving` body. Below that: a 2-column grid with two signature blocks. Each block: red caps label (`CLIENT AUTHORIZATION` / `ST. NICK'S AUTHORIZED SIGNATURE`), then 4 rows: SIGNATURE (with empty bottom-bordered line), PRINTED NAME (line), TITLE (line), DATE (line). Bottom: italic gray `digital_signing_note`.

**ctx fields used:** `page_title`, `standfirst`, `what_youre_approving`, `client_party_label`, `stnicks_party_label`, `digital_signing_note`.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("sign_off_pier39",    "sign_off", "pier_39",   "sign_off_ctx",
        ["Let's Make It Happen", "WHAT YOU'RE APPROVING", "CLIENT AUTHORIZATION", "Canva e-signature"]),
    ("sign_off_riverside", "sign_off", "riverside", "sign_off_ctx",
        ["Let's Make It Happen", "WHAT YOU'RE APPROVING", "RCTC AUTHORIZATION", "Canva e-signature"]),
```

- [ ] **Steps 2-6:** Standard pattern.

Commit message: `feat(plan-2-prime): add sign_off.html — approval recap + 2 signature blocks`

---

### Task 23: `about.html` — dark feature page, 2-column body + red contact strip

**Files:**
- Modify: `tests/test_layouts.py`
- Create: `skill_assets/layouts/about.html`

**Master reference:** `Master Proposal Reference/master-pages/page-13.png`

**Implementer guidance:** Dark page (`page-dark`). Special: this layout DOES show the standard footer (master keeps page count visible). However, it OVERRIDES the footer to also include a brand-red contact strip across the full bottom. So: `{% block footer %}` is overridden, but rendered with custom content (red strip + standard crumb).

Body: page title + standfirst at top. Below: 2-column grid — left column has `THE COMPANY` red caps label + bulleted `company_facts` list; right column has `YOUR TEAM` red caps label + team list (each row: name in Poppins Bold white + role in light gray below).

Bottom of page (overriding footer): a full-width brand-red strip with the `contact_strip` text (white, tracked caps).

**ctx fields used:** `page_title`, `standfirst`, `company_facts`, `team` (list of `{name, role}`), `contact_strip`.

- [ ] **Step 1: Append LAYOUT_CASES**

```python
    ("about_pier39",    "about", "pier_39",   "about_ctx",
        ["About St. Nick's", "Founded 1998", "Daniel Christenson", "Director of Sales", "ST-NICKS.COM"]),
    ("about_riverside", "about", "riverside", "about_ctx",
        ["About St. Nick's", "Founded 1998", "Daniel Christenson", "Director of Sales", "ST-NICKS.COM"]),
```

- [ ] **Steps 2-6:** Standard pattern. Reference cover.html for dark-page chrome.

Commit message: `feat(plan-2-prime): add about.html — dark page with team + red contact strip`

---

## Phase C — Verification

### Task 24: Full-suite verification + manual eyeball pass

**Files:** none modified — verification only.

- [ ] **Step 1: Run the full pytest suite**

```bash
.venv/bin/pytest -v
```

Expected:
- All foundation tests pass (Tasks 1–8): test_repo_structure, test_fonts_present (now 7 fonts), test_brand_css (9 tests), test_base_html (6 tests).
- All `test_layout_renders` parametrized cases pass — count depends on how many fixtures use each layout. Total LAYOUT_CASES entries: cover ×2, exec_summary ×2, understanding ×2, creative_vision ×2, zone_solo ×3, zone_solo_fullbleed ×1, zone_2up ×1, zone_3up ×1, zone_index ×1, scope ×2, case_study ×2, investment ×2, terms ×2, sign_off ×2, about ×2 = **27 layout cases**.
- `test_all_layouts_rendered` passes — every PDF named in LAYOUT_CASES exists on disk.

Total expected: ~50 passed, 0 skipped, 0 failed.

- [ ] **Step 2: List the rendered PDFs**

```bash
ls tests/_output/*.pdf | wc -l
ls tests/_output/*.pdf
```

Expected: 27 PDFs.

- [ ] **Step 3: Manual eyeball pass — 13 master pages × all relevant rendered PDFs**

For each pair of (master page, rendered PDF), open both and compare:

| Master page | Rendered PDFs to compare |
|---|---|
| page-01.png | cover_pier39.pdf, cover_riverside.pdf |
| page-02.png | exec_summary_pier39.pdf, exec_summary_riverside.pdf |
| page-03.png | understanding_pier39.pdf, understanding_riverside.pdf |
| page-04.png | creative_vision_pier39.pdf, creative_vision_riverside.pdf |
| page-05.png | zone_solo_pier39_z01.pdf, zone_solo_pier39_z02.pdf, zone_solo_riverside_flag.pdf |
| page-07.png | zone_solo_fullbleed_pier39_z03.pdf |
| (no master) | zone_2up_riverside.pdf, zone_3up_riverside.pdf, zone_index_riverside.pdf |
| page-08.png | scope_pier39.pdf, scope_riverside.pdf |
| page-09.png | case_study_pier39.pdf, case_study_riverside.pdf |
| page-10.png | investment_pier39.pdf, investment_riverside.pdf |
| page-11.png | terms_pier39.pdf, terms_riverside.pdf |
| page-12.png | sign_off_pier39.pdf, sign_off_riverside.pdf |
| page-13.png | about_pier39.pdf, about_riverside.pdf |

Acceptance criteria for each:
- Visual structure matches the master (positions, proportions, hierarchy).
- Type sizes feel comparable to the master (within ~10%).
- Brand colors are correct (`#B31315` red, `#1C1C1C` charcoal, `#1B7A3F` green only on Scope, `#12355B` navy only on Investment Signature tier rule, no other colors except `#F2F2F2` panel and white).
- Persistent header (top-left ST. NICK'S brand mark) and footer (project crumb + page number) present except where suppressed (cover, creative_vision, zone_solo_fullbleed have NO standard footer; about has the red contact strip in place of the footer).

If any layout differs noticeably from the master, note the layout name and what's off, then iterate on the layout HTML and re-run the test for that case.

- [ ] **Step 4: Confirm no regressions in foundation**

```bash
.venv/bin/pytest tests/test_brand_css.py tests/test_fonts_present.py tests/test_base_html.py tests/test_repo_structure.py -v
```

Expected: all pass.

- [ ] **Step 5: No commit**

This task changes nothing in the tree. The full-suite green and visual confirmation are the deliverable. After this task lands, Plan 2-prime is shipped.

---

## Plan 2-prime — Done

After all 24 tasks land:
- 18 archived layouts + their PDFs sit at `archive/iteration-1-abstract-layouts/` with explanatory README.
- 4 superseded specs/plans carry status banners pointing at the new docs.
- 15 master-driven layouts live in `skill_assets/layouts/`, all extending the new chrome-aware `base.html`.
- `brand.css` carries Poppins-Black + new tokens + page chrome CSS.
- 27 LAYOUT_CASES entries render against 2 fixtures (Pier 39 destination + Riverside zone-heavy).
- The full pytest suite passes; manual eyeball confirms each rendered PDF visually matches its master-page reference.

Plan 3 picks up next: parsers (Brief.md + Scope Worksheet.xlsx + rendering folders), AE workflow (selecting cover image, zone images, layout variants based on zone count), and the production render pipeline at `skill_assets/generate.py`.
