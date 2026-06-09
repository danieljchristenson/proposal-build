# Editorial Visual Design — Implementation Plan (Plan 13)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax. **This is a large, visual plan — execute in phase order; do not skip the render-review checkpoints.**

**Goal:** Make the `editorial` theme look finished across every slide — proper dark surfaces, a white logo, true-black headlines, fixed text overlaps/truncation, no dead space — then make it the go-forward default. Classic stays byte-identical throughout.

**Architecture:** The per-layout color decisions are currently hardcoded in each template's inline `<style>` (and some came from `brand.css`, which editorial doesn't load). We **tokenize** those decisions into CSS custom properties scoped by `body.page-light` / `body.page-dark` inside each theme stylesheet. Classic sets tokens to today's exact values (byte-stable); editorial sets a dark palette. Shared layout templates reference tokens, so they adapt per theme automatically. Plus two asset tasks (white logo, Roboto-Black) and a per-layout polish/bugfix pass.

**Tech Stack:** Jinja2 + WeasyPrint, Python 3.11+ (machine 3.14), pytest, Pillow (for the logo asset — already a transitive dep of WeasyPrint; verify). CSS custom properties + `body.page-dark`/`.page-light` scoping (WeasyPrint-supported).

**Builds on:** Plan 12 (theme infrastructure) on branch `feat/editorial-theme`. Spec: `docs/superpowers/specs/2026-06-09-st-nicks-editorial-theme-design.md`.

**Out of scope:** `itemized_pricing.html` / `itemized_pricing_rom.html` (separate letter-format pricing PDFs — stay light, not themed); any pricing-math change; new content devices (before/after frames, guest-journey key-plan, Next-Steps page — a later plan).

---

## Token contract (the spine — referenced by every layout task)

Semantic tokens, set per `(theme × surface)`. Classic values reproduce TODAY's hardcoded colors exactly (byte-stable). Editorial-dark introduces the new palette.

| Token | Purpose | Classic light | Classic dark | Editorial dark |
|---|---|---|---|---|
| `--ink` | primary text | `#1C1C1C` | `#ECEFF1` | `#ECEFF1` |
| `--ink-muted` | captions/gray | `#555555` | `rgba(236,239,241,.7)` | `#9A9CA1` |
| `--surface-card` | panels/cards | `#F2F2F2` | `#2a2a2a` | `#26262A` |
| `--surface-card-2` | nested/darker panel | `#0d0d0d` | `#0d0d0d` | `#121214` |
| `--surface-hero` | image placeholder bg | `#2A2A2A` | `#2a2a2a` | `#1F1F22` |
| `--surface-strip` | dark accent strips (partnership/workflow) | `#1C1C1C` | `#1C1C1C` | `#0E0E10` |
| `--surface-recommended` | recommended tier card | `#FFF8F8` | `#FFF8F8` | `#241A1A` |
| `--rule` | dividers/borders | `#E0E0E0` | `rgba(236,239,241,.18)` | `rgba(236,239,241,.14)` |
| `--placeholder-ink` | image fallback text | `rgba(28,28,28,.4)` | `rgba(236,239,241,.4)` | `rgba(236,239,241,.4)` |
| `--accent` | brand red | `#B31315` | `#B31315` | `#B31315` |
| `--accent-2` | brand navy | `#12355B` | `#12355B` | `#3D6FB5` |

> These are starting values; the dark ones get tuned at the render-review checkpoints in Phase 3. The classic columns must NOT change.

---

## Phase 1 — Foundations (assets + tokens + stability net)

### Task 1: Classic golden-render stability net (do FIRST)

Plan 12's guard only checks the `<body>` tag. Tokenizing touches inline color CSS, so we need a stronger net that proves classic *rendered HTML* is unchanged before we refactor.

**Files:**
- Create: `tests/test_theme_classic_golden.py`

- [ ] **Step 1: Write a golden test that snapshots classic rendered HTML for every Riverside slide**

```python
"""Classic rendered HTML must not change while we tokenize layouts.
Captures the full rendered HTML string per slide under theme=classic and
compares to a committed snapshot. Regenerate intentionally with REGEN=1."""
import os
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import tests.fixtures.riverside as rv
from proposal_build.renderer.pdf import LAYOUTS_DIR, _enrich_ctx

SNAP = Path(__file__).parent / "_golden" / "classic_html"

def _slides():
    # Reuse the same (layout, ctx) tuples the editorial render test assembles.
    from tests.test_theme_editorial_renders import _riverside_slides
    return _riverside_slides()

def _render(layout, ctx):
    env = Environment(loader=FileSystemLoader(str(LAYOUTS_DIR)),
                      autoescape=True, undefined=StrictUndefined,
                      keep_trailing_newline=True)
    return env.get_template(f"{layout}.html").render(**_enrich_ctx(ctx, "classic", layout))

@pytest.mark.parametrize("idx", range(len(_slides())))
def test_classic_html_matches_golden(idx):
    layout, ctx = _slides()[idx]
    html = _render(layout, ctx)
    SNAP.mkdir(parents=True, exist_ok=True)
    f = SNAP / f"{idx:02d}_{layout}.html"
    if os.environ.get("REGEN") == "1" or not f.exists():
        f.write_text(html); pytest.skip(f"wrote golden {f.name}")
    assert html == f.read_text(), f"classic HTML drifted for {layout}"
```

- [ ] **Step 2: Refactor the editorial render test to expose `_riverside_slides()`**

In `tests/test_theme_editorial_renders.py`, extract the inline slide-assembly into a module-level `def _riverside_slides() -> list[tuple[str,dict]]:` returning the same list it already builds, and have the existing test call it. (So both tests share one slide list.)

- [ ] **Step 3: Generate the goldens and commit them**

Run: `REGEN=1 python -m pytest tests/test_theme_classic_golden.py -q` (writes snapshots, skips).
Then `python -m pytest tests/test_theme_classic_golden.py -q` → all PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_theme_classic_golden.py tests/test_theme_editorial_renders.py tests/_golden/
git commit -m "test: golden snapshot of classic rendered HTML (tokenization safety net)"
```

### Task 2: White logo asset + theme-aware logo wiring

**Files:**
- Create: `skill_assets/Branding/ST NICKS LOGO WHITE.png` (generated)
- Create: `scripts/make_white_logo.py`
- Modify: `skill_assets/proposal_build/composer/ctx_builders.py` (`_project_base`, `_LOGO_PATH`)
- Modify: `skill_assets/proposal_build/renderer/pdf.py` (`_enrich_ctx`)
- Modify: `skill_assets/layouts/base.html`, `cover.html`, `about.html`
- Test: `tests/test_logo_assets.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
from PIL import Image
from proposal_build.renderer.pdf import _enrich_ctx

BRANDING = Path("skill_assets/Branding")

def test_white_logo_exists_and_has_alpha():
    p = BRANDING / "ST NICKS LOGO WHITE.png"
    assert p.is_file()
    im = Image.open(p).convert("RGBA")
    # opaque pixels should be near-white
    px = [im.getpixel((x, y)) for x in range(0, im.width, max(1, im.width//20))
          for y in range(0, im.height, max(1, im.height//20))]
    opaque = [p for p in px if p[3] > 200]
    assert opaque, "logo has no opaque pixels"
    assert all(c > 200 for p in opaque for c in p[:3]), "opaque pixels are not white"

def test_enrich_selects_white_logo_on_dark():
    out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/white.png"},
                      theme="editorial", layout="cover")
    assert out["header_logo"] == "/x/white.png"
    out2 = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/white.png"},
                       theme="editorial", layout="about")  # about is light
    assert out2["header_logo"] == "/x/black.png"
```

- [ ] **Step 2: Run → fails. Step 3: Create the generator + asset**

Create `scripts/make_white_logo.py`:

```python
"""Recolor the black St. Nick's logo to white, preserving alpha."""
from pathlib import Path
from PIL import Image

src = Path("skill_assets/Branding/ST NICKS LOGO.png")
dst = Path("skill_assets/Branding/ST NICKS LOGO WHITE.png")
im = Image.open(src).convert("RGBA")
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        px[x, y] = (244, 234, 222, a)  # ivory #F4EADE, keep original alpha
im.save(dst)
print("wrote", dst)
```

Run: `python scripts/make_white_logo.py`. Open the PNG to confirm it's a clean white wordmark on transparency. (If the source logo's antialiased edges look harsh, that's acceptable; tune later.)

- [ ] **Step 4: Wire it**

In `ctx_builders.py`: add `_LOGO_PATH_DARK` (the white png) next to `_LOGO_PATH`, and in `_project_base` add `"logo_path_dark": _LOGO_PATH_DARK`.

In `pdf.py` `_enrich_ctx`, after computing `body_surface`, add:
```python
        "header_logo": (ctx.get("logo_path_dark") if surface == "dark" and ctx.get("logo_path_dark")
                        else ctx.get("logo_path")),
```
(where `surface = surface_for(theme, layout)` — reuse the value already computed.)

In `base.html`, change the logo `<img src="{{ logo_path }}">` to use `{{ header_logo | default(logo_path) }}`. In `cover.html` (`.cover-logo`) and `about.html` (`.ab-logo-bottom`), likewise prefer `header_logo` when defined, falling back to `logo_path`. (Read each file; they reference `logo_path` directly — swap to `{{ header_logo | default(logo_path) }}`.)

- [ ] **Step 5: Run tests + classic golden (must still pass — classic uses black logo on its light pages; on classic dark `cover`, `header_logo` now resolves to the white logo, which is a *deliberate* improvement — REGEN the golden for the cover slide only and eyeball it).**

```bash
python -m pytest tests/test_logo_assets.py -v
REGEN=1 python -m pytest tests/test_theme_classic_golden.py -q   # cover HTML legitimately changes (white logo on dark)
python -m pytest tests/test_theme_classic_golden.py -q
```
Open a classic render of the cover to confirm the white logo reads well on the dark cover. If you prefer to keep classic's cover EXACTLY as-is (black logo in a white chip), instead gate `header_logo` on `theme == "editorial"` in `_enrich_ctx` so classic is untouched. **Decision for the executor: prefer gating on `theme == "editorial"` to keep classic 100% byte-stable.** Update the test accordingly (classic cover → black logo).

- [ ] **Step 6: Commit**

```bash
git add scripts/make_white_logo.py "skill_assets/Branding/ST NICKS LOGO WHITE.png" skill_assets/proposal_build/composer/ctx_builders.py skill_assets/proposal_build/renderer/pdf.py skill_assets/layouts/ tests/test_logo_assets.py
git commit -m "feat(theme): white logo asset + dark-surface logo wiring (editorial)"
```

### Task 3: Embed Roboto-Black for true weight-900 headlines

**Files:**
- Add: `skill_assets/fonts/Roboto-Black.ttf`
- Modify: `skill_assets/layouts/theme-editorial.css`
- Test: `tests/test_fonts_present.py` (extend)

- [ ] **Step 1:** Obtain `Roboto-Black.ttf` (Apache-2.0, redistributable) from the Google Fonts repo and place it in `skill_assets/fonts/`. Verify it loads: `python -c "from fontTools.ttLib import TTFont; TTFont('skill_assets/fonts/Roboto-Black.ttf')"`.
  - **Fallback if no network:** use the existing `Poppins-Black.ttf` for editorial headlines instead — point the weight-900 `@font-face` at `Poppins-Black.ttf` and set `--font-heading` accordingly. Note the deviation in the CSS comment and STOP to flag it for review.
- [ ] **Step 2:** Extend `tests/test_fonts_present.py` to assert `Roboto-Black.ttf` (or the chosen fallback) exists in `skill_assets/fonts/`.
- [ ] **Step 3:** In `theme-editorial.css`, change the `font-weight:900` `@font-face` `src` from `Roboto-Bold.ttf` to `Roboto-Black.ttf` and remove the fallback comment.
- [ ] **Step 4:** Render Riverside editorial; confirm headlines are visibly heavier (true Black). `python -m pytest tests/test_fonts_present.py tests/test_theme_editorial_renders.py -v`.
- [ ] **Step 5:** Commit: `git add skill_assets/fonts/Roboto-Black.ttf skill_assets/layouts/theme-editorial.css tests/test_fonts_present.py && git commit -m "feat(theme): embed Roboto-Black for true weight-900 editorial headlines"`

### Task 4: Define the token contract in both stylesheets

**Files:**
- Modify: `skill_assets/layouts/brand.css` (classic) — add token declarations scoped to `body.page-light` / `body.page-dark` using TODAY's exact values (table above, classic columns).
- Modify: `skill_assets/layouts/theme-editorial.css` (editorial) — add the same token names scoped to `body.page-dark` (editorial column) and `body.page-light` (classic-light values, for the About page).
- Test: extend `tests/test_brand_css.py` + `tests/test_theme_classic_golden.py` stays green (no layout references the tokens yet, so rendered HTML is unchanged).

- [ ] **Step 1:** Add to `brand.css`:
```css
body.page-light {
  --ink:#1C1C1C; --ink-muted:#555555; --surface-card:#F2F2F2; --surface-card-2:#0d0d0d;
  --surface-hero:#2A2A2A; --surface-strip:#1C1C1C; --surface-recommended:#FFF8F8;
  --rule:#E0E0E0; --placeholder-ink:rgba(28,28,28,.4); --accent:#B31315; --accent-2:#12355B;
}
body.page-dark {
  --ink:#ECEFF1; --ink-muted:rgba(236,239,241,.7); --surface-card:#2a2a2a; --surface-card-2:#0d0d0d;
  --surface-hero:#2a2a2a; --surface-strip:#1C1C1C; --surface-recommended:#FFF8F8;
  --rule:rgba(236,239,241,.18); --placeholder-ink:rgba(236,239,241,.4); --accent:#B31315; --accent-2:#12355B;
}
```
- [ ] **Step 2:** Add to `theme-editorial.css`:
```css
body.page-dark {
  --surface-card:#26262A; --surface-card-2:#121214; --surface-hero:#1F1F22;
  --surface-strip:#0E0E10; --surface-recommended:#241A1A;
  --rule:rgba(236,239,241,.14); --placeholder-ink:rgba(236,239,241,.4); --accent-2:#3D6FB5;
  /* --ink / --ink-muted / --accent already set by the core body.page-dark rule */
}
body.page-light {  /* About page */
  --ink:#1C1C1C; --ink-muted:#555555; --surface-card:#F2F2F2; --surface-hero:#2A2A2A;
  --rule:#E0E0E0; --placeholder-ink:rgba(28,28,28,.4); --accent:#B31315; --accent-2:#12355B;
}
```
- [ ] **Step 3:** `python -m pytest tests/test_theme_classic_golden.py tests/test_brand_css.py -q` → still green (tokens defined but unused = no HTML change).
- [ ] **Step 4:** Commit: `git commit -am "feat(theme): define shared color token contract in both stylesheets"`

---

## Phase 2 — Tokenize the layouts (per-layout sweep)

For each layout, edit its inline `<style>` block: replace hardcoded colors with the token names from the contract. Because classic tokens equal the old values, **the classic golden test must stay green after every task** (run it each time). Editorial then renders correctly because editorial sets dark token values.

General rule per file: `#F2F2F2`/light panel → `var(--surface-card)`; `#2a2a2a`/`#2A2A2A` → `var(--surface-hero)` or `var(--surface-card)` per context; `#0d0d0d` → `var(--surface-card-2)`; `#1C1C1C` strips → `var(--surface-strip)`; `#FFF8F8` → `var(--surface-recommended)`; gray text `#555`/`rgba(...)` → `var(--ink-muted)`; divider grays (`#E0E0E0`/`#D8D8D8`/`#F5F5F5`) → `var(--rule)`; placeholder text → `var(--placeholder-ink)`; charcoal body text → `var(--ink)`; `#B31315` may stay literal or → `var(--accent)`.

Each task below = one commit. After each: `python -m pytest tests/test_theme_classic_golden.py tests/test_layouts.py -q` (green), then render Riverside+Toyota editorial and eyeball the touched slides.

- [ ] **Task 5 — Dark-native layouts** (already dark for classic; just point colors at tokens so editorial palette applies): `cover.html`, `creative_vision.html`, `zone_feature.html`, `zone_solo_fullbleed.html`, `section_divider.html`, `image_fullbleed.html`. Replace inline `#2a2a2a`/`#0d0d0d`/semi-transparent whites with `--surface-*`/`--ink*`/`--rule`. **Remove the `box-shadow` on `zone_feature.html`'s `.zfe-text` panel** (WeasyPrint-unsupported; use a 1px `--rule` border or `--surface-card` fill instead).
- [ ] **Task 6 — Zone content layouts**: `zone_index.html`, `zone_solo.html`, `zone_2up.html`, `zone_3up.html`, `zone_4up.html`, `zone_2up_gallery.html`, `zone_solo_gallery.html`. Tokenize dividers (`.z*-zone-rule`, list rules), placeholders (`.z*-placeholder` — fix the light-on-light bug via `--placeholder-ink`), and image-cell backgrounds. For `zone_4up`/`zone_2up_gallery` white image cells: keep image framing readable on dark — set cell bg to `var(--surface-card)` so renderings sit on a panel, not raw white.
- [ ] **Task 7 — Summary/understanding/scope**: `exec_summary.html`, `understanding.html`, `scope.html`. Tokenize the `.es-glance`/`.es-pillar`/`.un-card` panels to `var(--surface-card)` with `var(--rule)` borders and `var(--ink)` text, so they read as real cards on dark (today they go transparent because `.card` came from brand.css). For `scope.html`'s `.card.has-header.green`: define an editorial treatment (keep the green header — it's semantic — on a `var(--surface-card)` body).
- [ ] **Task 8 — Investment/pricing-in-deck**: `investment.html`, `rom_investment.html`, `a_la_carte.html`, `tree_comparison.html`. Tokenize tier cards, the `.inv-partnership`/dark strips (`--surface-strip`), recommended cards (`--surface-recommended`), table header/row backgrounds, and the green/navy rules. Ensure the big total reads in `--ink` or `--accent` on dark. Tables: header → `--surface-strip`, alt rows → `--surface-card`.
- [ ] **Task 9 — Closing pages**: `terms.html`, `sign_off.html`. Tokenize cards, the dark workflow/date strips, and the signature-line color (`--rule`). Keep the red date banner literal red (semantic).
- [ ] **Task 10 — Proof/menu pages**: `material_palette.html`, `case_study.html`, `sample_of_work.html`. Tokenize placeholders and image/scrim backgrounds; the `sample_of_work` dark scrim already works on any bg.
- [ ] **Task 11 — About (light) audit**: confirm `about.html` still renders correctly on its forced-light surface under editorial (logo bottom-right uses the BLACK logo on light — `logo_path`, not `header_logo`). No token changes expected; just verify and snapshot.

> If any layout needs a structural change (not just color) to look right on dark, keep it minimal and note it; deep restructures belong in Phase 3.

---

## Phase 3 — Bug fixes + polish (render-review gated)

Each task: implement, render Riverside **and** Toyota editorial, and STOP for a human review checkpoint (the controller/Daniel eyeballs the page) before marking complete. Tune values against the render.

- [ ] **Task 12 — Creative Vision truncation + empty cards** (shared classic+editorial fix): the `.cv-mid` 65% max-height clips `.cv-direction-body`; the phase cards can render empty. Fix overflow (let body text fit or scale; ensure phase cards always have content or collapse gracefully). Re-snapshot classic golden (this is an intentional shared improvement — REGEN + eyeball classic too).
- [ ] **Task 13 — Exec Summary standfirst/body overlap**: `.es-title-area` standfirst overlaps `.es-body-area` on the dark render. Fix the flex spacing so the standfirst and body never collide. Verify on both Riverside and Toyota (different copy lengths).
- [ ] **Task 14 — Cover stray crumb + polish**: remove/fix the stray top-right element on the cover; confirm the white logo, red rule, season eyebrow, title, and prepared-by block all sit cleanly. Verify hero image fills the right panel.
- [ ] **Task 15 — Kill dead space on single-image zones**: `zone_solo` with one image leaves a large empty lower-left. Rebalance (larger image / better grid) so the page reads full. (Optional, additive: an editorial `.stat` call-out component — oversized `--accent` number + tracked-caps label — for zones that carry a quantity; only render when a `stat` is present in ctx, default off. Do NOT add new required ctx fields.)
- [ ] **Task 16 — Full editorial pass review**: render the complete Riverside and Toyota editorial decks; review every page; fix remaining fit-and-finish (spacing, eyebrow tracking, footer contrast, page-number legibility on full-bleed pages). Checkpoint with Daniel.

---

## Phase 4 — Flip default + final validation

- [ ] **Task 17 — Flip the default theme classic→editorial**: change the default in the parser (`fm.get("theme", "editorial")`) and the `cli.py` placeholder and `render_proposal_pdf(theme="editorial")` default and `ProjectModel.theme = "editorial"`. Update Plan-12 tests that assumed `classic` default (e.g. the `theme_defaults_to_classic_when_absent` test → now `editorial`; the model default test). **Projects can pin `theme: classic` in their Brief front-matter to opt out.**
- [ ] **Task 18 — Regenerate + review the pilot**: render the full Riverside deck under the new default; confirm it matches the approved direction end-to-end. Save a fresh `EDITORIAL THEME PREVIEW.pdf`. Final Daniel checkpoint.
- [ ] **Task 19 — Full suite green**: `python -m pytest -q` → only the known pre-existing `test_ae_sop_exists_and_has_required_sections` fails. Classic still selectable and byte-stable (`theme: classic` pin → golden test). Commit and run the finishing-a-development-branch flow.

---

## Self-Review (author)

**Spec coverage:** dark per-layout styling (Phase 2 ✓); light reserved for About + pricing PDFs (Task 11, out-of-scope pricing ✓); white logo (Task 2 ✓); Roboto-Black (Task 3 ✓); dead-space + truncation fixes (Tasks 12,15 ✓); go-forward default flip (Task 17 ✓); classic byte-stable (Task 1 golden net, run every task ✓).

**Placeholder scan:** Token values and find→replace rules are concrete (contract table). Per-layout tasks name exact files + exact class/color targets from the structural inventory; visual *tuning* is explicitly deferred to render-review checkpoints (not a placeholder — the change and verification are specified). The Roboto-Black acquisition has a defined fallback.

**Type/name consistency:** token names identical across the contract table, brand.css, theme-editorial.css, and the layout tasks. `header_logo` / `logo_path_dark` consistent across ctx_builders, `_enrich_ctx`, base.html, cover.html, about.html.

**Scope check:** Large but coherent (one theme, one branch). If executing incrementally, Phases 1–2 (foundations + tokenization) are a natural first merge-able milestone; Phases 3–4 (polish + flip) a second. Each task is independently committable and keeps classic green.

**Risk:** the classic golden test is the critical guard — it MUST be run after every Phase-2 task. Tokenization that changes a classic value (vs. just naming it) would drift classic and fail the golden; that's the intended tripwire.
