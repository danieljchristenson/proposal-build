# Plan 2 — Brand + Layout System: Design

> ⚠️ **SUPERSEDED 2026-05-03.** Decision 6 ("master is informal directional
> reference only") was wrong. Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-design.md`](./2026-05-03-plan-2-prime-master-driven-design.md).
> Implementation moved to `archive/iteration-1-abstract-layouts/`.

**Status:** Approved 2026-05-01 (brainstorming session, Daniel + Claude)
**Parent spec:** `docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md`
**Predecessor:** Plan 1 — Repo restructure + skill scaffolding (complete)
**Successor:** Plan 3 — Phase 2 generation core (parsers + slide assembly)

This document captures the design decisions for Plan 2. The executable plan
itself lives at `docs/superpowers/plans/2026-05-01-02-brand-layout-system.md`
(written next, by `superpowers:writing-plans`).

---

## 1. Goal

Ship the deployable brand + layout foundation of the skill: page geometry,
embedded fonts, `brand.css` design tokens, a Jinja2 templating shell, all 18
slide layouts, and a fixture-driven test suite that proves every layout
renders correctly with embedded fonts at the right page size.

After Plan 2: the visual system exists and is verified end-to-end against
real-shaped fixture data. After Plan 3 (next): real Brief/Worksheet data
flows through it.

## 2. Design decisions (locked)

These were the six decisions made during the 2026-05-01 brainstorming session.

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Page geometry | 16:9 widescreen, 13.333" × 7.5" landscape | Matches existing `StNicks_Proposal_v2_Master.pptx`. PDF and Canva backup remain visually interchangeable. Customers view on screens, not paper. |
| 2 | Plan 2 scope | All 18 layouts + foundation, validated against hand-built Riverside fixture data | Avoids both extremes: blind layout work (uncovered until Plan 3) and stubbed pipeline (real layout problems pushed to Plan 3). |
| 3 | Test strategy | Render + structural assertions (dimensions, font embedding, content presence) — not pixel diffs | Catches the silent failures the spec calls out (font fallback, dimension drift). Snapshot diffs are too brittle for layouts still iterating. |
| 4 | `brand.css` scope | Tokens — colors, fonts, type scale, spacing scale, global element rules. No reusable component classes. | Enforces visual rhythm consistency. Component classes are premature abstraction in V1 (most candidates appear in only one layout). |
| 5 | Templating | Jinja2 + `base.html` extends pattern | Plan 3 needs a real template engine for data injection; using Jinja2 now means Plan 2 layouts don't get rewritten in Plan 3. Single `<head>` definition. |
| 6 | Visual reference | Fresh modern redesign from spec; master .pptx is informal directional reference only | User wants a fresh look. No PNG-extraction task in Plan 2. |

## 3. Visual direction

Modern, restrained, image-led. Specific guardrails:

- Generous whitespace; hero imagery does the heavy lifting.
- Accent red (`--color-red`) used only on headlines and CTAs — never as block fill.
- Tight, geometric type scale (~1.25 minor third).
- No decorative elements that aren't load-bearing.
- Each layout's eyeball-pass approval verifies these qualities.

The master .pptx may be opened for directional reference (brand feel) but
must not be used as a layout template.

## 4. Brand system (`skill_assets/layouts/brand.css`)

CSS variable design tokens, layered:

**Colors** (locked by parent spec §3):
- `--color-red: #B31315` — headlines, accents, CTAs only
- `--color-charcoal: #1C1C1C` — body on light backgrounds
- `--color-gray: #555555` — captions, secondary text
- `--color-navy: #12355B` — secondary accent
- `--color-light: #ECEFF1` — body on dark backgrounds, light fills

**Fonts** — `@font-face` declarations loading from `../fonts/` (never the
system, per parent spec §3):
- `--font-heading: "Roboto", sans-serif`
- `--font-body: "Poppins", sans-serif`

**Typographic scale** — geometric (~1.25 minor third):
- `--text-xs`, `--text-sm`, `--text-base`, `--text-lg`, `--text-xl`, `--text-2xl`, `--text-3xl`

**Spacing scale** — 4pt grid:
- `--space-1` (4pt) through `--space-8` (32pt)

**Global element rules** — `h1`–`h6`, `p`, `ul`, `li`, `img`, `table`
get base styles so layouts inherit consistent rhythm.

**Page geometry** — default `@page { size: 13.333in 7.5in; margin: var(--space-6); }`.
Per-layout margin overrides allowed (e.g., `cover` and `showcase_fullbleed` use `0`).

No reusable component classes in Plan 2 (deferred to Plan 3+ if patterns emerge).

## 5. Fonts

Sourced from Google Fonts. Licenses permit redistribution:
- Roboto — Apache License 2.0
- Poppins — SIL Open Font License (OFL)

Files committed as binaries to `skill_assets/fonts/`:

| File | Weight | Purpose |
|------|--------|---------|
| `Roboto-Bold.ttf` | 700 | Headings, key statements |
| `Roboto-Regular.ttf` | 400 | Subheadings |
| `Poppins-Light.ttf` | 300 | Captions, descriptions |
| `Poppins-Regular.ttf` | 400 | Long-form body |
| `Poppins-Medium.ttf` | 500 | Body emphasis |

## 6. Templating shell (`skill_assets/layouts/base.html`)

Jinja2 base template. Owns:
- `<!DOCTYPE html>`
- `<html lang="en">` and `<head>` with `<meta charset>`, title slot
- `<link rel="stylesheet" href="brand.css">`
- A `{% block layout_version %}{% endblock %}` slot in `<head>` for the
  per-layout version comment
- `{% block content %}{% endblock %}` slot in `<body>`

Every layout file begins with `{% extends "base.html" %}`, fills the
`layout_version` block with its own version comment (per parent spec §7),
and fills `content` with its body. Layout files have no `<head>`
boilerplate and no direct `<link>` to `brand.css`.

## 7. Layout files (18, all in `skill_assets/layouts/`)

| # | File | Slide | Notes |
|---|------|-------|-------|
| 1 | `cover.html` | Cover | hero image full-bleed; project + client + date |
| 2 | `exec_summary.html` | Executive Summary | at-a-glance grid + 3 pillars |
| 3 | `understanding.html` | Our Understanding | 4-box (goals/criteria/constraints/tier); constraints box hidden if "none" |
| 4 | `creative_vision.html` | Creative Vision | hero image + 3-phase narrative |
| 5 | `showcase_hero.html` | Showcase (1–3 items) | hero rendering + sidebar item list |
| 6 | `showcase_2up.html` | Showcase (3–6 items) | 2-up grid |
| 7 | `showcase_3up.html` | Showcase (6–10 items) | 3-up grid |
| 8 | `showcase_4up.html` | Showcase (overflow) | 4-up grid |
| 9 | `showcase_fullbleed.html` | Showcase (single hero) | edge-to-edge rendering |
| 10 | `scope.html` | Scope of Work | 2-column inclusions + add-ons |
| 11 | `sample_of_work.html` | Sample of Our Work | 6-tile grid |
| 12 | `case_study.html` | Case Study | challenge / approach / outcome |
| 13 | `investment_tiered.html` | Investment | 3-tier price columns |
| 14 | `investment_single.html` | Investment | 1-tier alt |
| 15 | `add_ons.html` | Add-Ons | line-item table with prices |
| 16 | `terms.html` | Terms & Next Steps | dates + payment + insurance + change orders + validity |
| 17 | `sign_block.html` | Sign Block | signature lines |
| 18 | `about.html` | About St. Nick's | company + team |

Each layout fills the base template's `layout_version` block with its own
version comment, e.g.:

```jinja
{% block layout_version %}<!-- layout-version: 2026-05-01 -->{% endblock %}
```

Per parent spec §7 — exposes which layout version rendered each slide so
the Coverage Report can record it on subsequent runs.

## 8. Fixture data (`tests/fixtures/riverside.py`)

Hand-built Python dicts shaped as Plan 3's eventual parsers will produce
them. Anchored on the Downtown Riverside MetroLink project where data
exists: real client name (RCTC), real rendering filenames from
`Projects/Downtown Riverside Metro Link/02 - Renderings/`, plausible
scope items and pricing. Where Riverside doesn't yet have content for a
given layout (e.g., no case study selected, no past-work library
populated), fixtures use plausible-but-fabricated values consistent with
St. Nick's voice and existing examples.

One importable fixture per layout — e.g., `cover_ctx`, `exec_summary_ctx`,
`showcase_3up_ctx`. Tests parametrize over the (layout_name, fixture) pairs.

Fixtures are *not* a parsing exercise — they are hand-authored to model
the eventual data shape. Plan 3 will derive its parsers' output schemas
from these.

## 9. Render pipeline (test-only, `tests/conftest.py`)

Single helper:

```python
def render_layout(layout_name: str, ctx: dict) -> Path:
    """Render a single layout to PDF; return path to the rendered file.

    - Loads Jinja2 environment rooted at skill_assets/layouts/
    - Renders {layout_name} with ctx
    - Pipes the resulting HTML through WeasyPrint
    - Writes to tests/_output/{layout_name}.pdf
    - Returns the Path
    """
```

Plan 2 deliberately does *not* commit to a production rendering architecture.
Plan 3 owns `skill_assets/generate.py` and may or may not extract logic from
this test helper.

## 10. Tests (`tests/test_layouts.py`)

One parametrized test runs all 18 layouts. For each `(layout_name, ctx)` pair:

- Call `render_layout(layout_name, ctx)`.
- Assert PDF page count == 1.
- Assert page dimensions match 13.333" × 7.5" within 1pt tolerance.
- Assert embedded fonts include both `"Roboto"` and `"Poppins"`
  (catches the silent system-font-fallback failure mode).
- Assert expected text strings from the fixture appear in extracted PDF
  text (catches blank-page and missing-content failures).

Plus one cross-cutting test asserts that all 18 PDFs exist in
`tests/_output/` after the suite runs, so the manual eyeball-pass can
proceed reliably.

The existing Plan 1 smoke test (`tests/test_repo_structure.py`) must
continue to pass.

## 11. Prerequisites (Plan 2 task #1)

System Python is 3.9.6 (Xcode-bundled); `pyproject.toml` requires `>=3.11`.
Plan 2 task #1 installs Python 3.11+ via one of:

- Homebrew: `brew install python@3.11` (preferred if Homebrew is or
  becomes available)
- Official installer from python.org (fallback)
- pyenv (if user prefers managed versions)

Then: recreate venv, `pip install -e ".[dev]"`, confirm Plan 1's smoke
test passes on 3.11. Without this, no rendering work can run.

## 12. Out of scope (deferred to Plans 3+)

- `Project Brief.md` / Scope Worksheet (.xlsx) parsers
- Real data injection from project files (Plan 2 uses fixture dicts only)
- `skill_assets/generate.py` CLI / production render pipeline
- Canva CSV emission
- Diff-mode regeneration, `last_run.json`, `dependency_map.yaml`
- Per-tier itemized pricing PDFs
- Phase 0 (RFP intake) and Phase 1 (rendering ingestion) logic
- Any reusable component CSS classes in `brand.css`

## 13. Done checklist

- [ ] Python 3.11+ installed; venv recreated; `pip install -e ".[dev]"` succeeds.
- [ ] Plan 1's `tests/test_repo_structure.py` green on 3.11.
- [ ] 5 font files in `skill_assets/fonts/` (Roboto Bold/Regular, Poppins Light/Regular/Medium).
- [ ] `skill_assets/layouts/brand.css` written: variables + `@font-face` + type scale + spacing scale + global rules + `@page`.
- [ ] `skill_assets/layouts/base.html` written.
- [ ] 18 layout files written, each `{% extends "base.html" %}` with version comment.
- [ ] `tests/fixtures/riverside.py` with one ctx dict per layout.
- [ ] `tests/conftest.py` `render_layout` helper.
- [ ] `tests/test_layouts.py` — 18 parametrized tests passing.
- [ ] All 18 PDFs in `tests/_output/`; manual eyeball-pass complete and approved.
- [ ] Work committed as a logical sequence of small commits.
