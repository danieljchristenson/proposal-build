# Typographic Fallback Layouts — Design

> ⚠️ **SUPERSEDED 2026-05-03 (same day).** Off-brand: the Branding Board rules
> out decorative/script fonts, but this addendum added Playfair Display.
> Replaced by:
> [`2026-05-03-plan-2-prime-master-driven-design.md`](./2026-05-03-plan-2-prime-master-driven-design.md).
> Never executed.

**Status:** Approved 2026-05-03 (brainstorming session, Daniel + Claude)
**Parent spec:** `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md`
**Predecessor:** Plan 2 — Brand + Layout System (complete; 18 layouts shipped)
**Successor:** Plan 3 — Phase 2 generation core (parsers + AE workflow)

This document captures the design for two new layouts that extend Plan 2's
output, intended to ship as a Plan 2 addendum (the executable plan will live
at `docs/superpowers/plans/2026-05-03-02b-typographic-fallback-layouts.md`).

---

## 1. Goal

Add two photo-free alternates for the cover and the section-divider slides
so Account Executives have a way to lead a proposal when the available
imagery is weak, missing, or wrong-tone for the specific project.

The current `cover.html` and `showcase_fullbleed.html` both depend on a
single hero photo doing 100% of the visual work. When the photo is bad,
the whole slide is bad. The fallbacks remove that single point of failure
by producing a strong slide on typography alone.

## 2. Design decisions (locked)

These were the decisions made during the 2026-05-03 brainstorming session.

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Scope | Cover + showcase_fullbleed only — not all hero-driven layouts | These are the two slides where weak imagery actually breaks the slide. `creative_vision`, `showcase_hero`, and `case_study` have body text + secondary content that carry weight when the photo softens; the cover and the fullbleed don't. |
| 2 | Aesthetic | Editorial / magazine-style typographic | Daniel chose this direction over "festive warm" and "cinematic luxury" in the brainstorming. Reads as a deliberate design choice, not a missing-asset placeholder. |
| 3 | Palette | Existing brand — white, charcoal, gray, red. Same tokens as the photo cover. | Keeps the typographic and photo versions of each slide as siblings, not strangers. The deck reads as one proposal even when the AE mixes layouts. |
| 4 | Photos in fallback | None | The premise is "no good photo available." Adding a small photo defeats the purpose — a small mediocre photo trusts less than no photo. |
| 5 | St. Nick's brand mark | Required, top-right, restrained. Typographic wordmark until a real logo file lands. | Daniel asked for St. Nick's branding to be "subtle" but visible on the cover. Top-right is the convention; small italic Playfair "St. Nick's" + tracked-caps "HOLIDAY DECOR" tagline reads as letterhead-style without selling. |
| 6 | Selection mechanism | AE picks per-project during the build (Plan 3 work) | Out of scope for this addendum. Connects to existing project memory: "AE chooses cover/hero images, system never picks defaults." Same principle, applied to layout-variant selection. |

## 3. Visual language

Editorial typographic. Specific guardrails:

- Same brand palette as the photo cover (`--color-red`, `--color-charcoal`,
  `--color-gray`, white as background) — no new colors introduced.
- Display headlines in a serif (Playfair Display) — distinct from the
  existing layouts' Roboto sans-serif headings.
- Italic accents (design phrase, issue numerals) in the same display serif.
- Thin red rule (1pt, 32–50pt wide) under the headline. Functional accent,
  not decoration.
- Issue-style numerals (`№ 26`, `Section IV`) give the deck a magazine
  cadence — these are editorial flourishes, not data.
- St. Nick's wordmark fixed top-right at small scale.

The typographic layouts and the photo layouts must coexist in the same
deck without visual whiplash. Same brand colors, same spacing grid, same
brand mark placement principles. Only the lead changes.

## 4. Layouts

### `cover_typographic.html`

Replaces `cover.html` when no strong hero photo is available.

**Structure:**
- Top-right: St. Nick's wordmark (italic Playfair red + tracked-caps
  "HOLIDAY DECOR" tagline in gray).
- Top section: issue-style numeral (`№ 26 — A Holiday Program`),
  project name as the hero (display Playfair Bold at `var(--text-3xl)` = 30pt, charcoal),
  thin red rule, design phrase as italic accent (`"Holiday Express"`).
- Bottom section: two-column metadata block.
  - Left: "Prepared for" → client company → decision maker + title.
  - Right: "Presented by" → presenter name → "St. Nick's · {date}".

**Same context fields as `cover.html`** — no new ctx keys required.
This is intentional: the AE swaps the layout file, not the data.

### `showcase_typographic.html`

Replaces `showcase_fullbleed.html` when no hero photo for the section.

**Structure:**
- Top-right: St. Nick's wordmark (same treatment as cover).
- Eyebrow: section-style label (`Showcase · Section IV`).
- Hero: section title in display Playfair Bold at 36pt (literal — exceeds the
  `--text-3xl` token at 30pt; this is intentional, the section divider runs
  bigger than the cover headline because it carries less metadata around it),
  thin red rule, italic standfirst caption beneath.
- Bottom-right ornament: small `✦` glyph in red at ~18pt, opacity 0.4 —
  editorial pacing device, signals to the reader that the next section begins.

**Same context fields as `showcase_fullbleed.html`** — same swap-the-layout-not-the-data principle.

## 5. Font additions

The existing bundle has Roboto (Bold, Regular) + Poppins (Light, Regular,
Medium). The typographic layouts add **Playfair Display**:

- `Playfair-Display-Bold.ttf` — weight 700, used for headlines (display H1
  on both layouts).
- `Playfair-Display-Italic.ttf` — italic 400, used for design-phrase accents,
  issue-style numerals, the `St. Nick's` wordmark, and the standfirst caption.

Files placed under `skill_assets/fonts/`. Embedded via `@font-face` in
`brand.css` (the same file that loads Roboto and Poppins). License: SIL
Open Font License (same as Plan 2 fonts).

A new token `--font-display: "Playfair Display", serif;` is added to the
`:root` in `brand.css`. The existing `--font-heading` (Roboto) and
`--font-body` (Poppins) are unchanged.

## 6. Test approach

Two new entries in `LAYOUT_CASES` (in `tests/test_layouts.py`):

```python
("cover_typographic", "cover_typographic_ctx", [
    "Downtown Riverside MetroLink",
    "Holiday Express",
    "St. Nick's",                       # wordmark presence
]),
("showcase_typographic", "showcase_typographic_ctx", [
    "Walk-Through Moment",              # the section_title
    "12-foot lighted gift-box arch",    # the caption
    "St. Nick's",                       # wordmark presence
]),
```

Two new context dicts in `tests/fixtures/riverside.py`. They reuse the
existing `cover_ctx` and `showcase_fullbleed_ctx` fields verbatim —
the data is the same; only the layout file changes.

After this addendum: 20 layouts total, 20 LAYOUT_CASES entries. The
existing `test_all_eighteen_layouts_rendered` is generalized and renamed
to `test_all_layouts_rendered` — it asserts that every PDF named in
`LAYOUT_CASES` exists on disk after the suite runs, with no hard-coded
count. Future additions to the layout catalogue extend `LAYOUT_CASES`
without touching this test.

A new test asserts Playfair Display is embedded in the typographic PDFs
(catches the silent system-font fallback, same pattern as the existing
Roboto/Poppins assertions).

## 7. Out of scope (deferred)

- **AE selection UX.** Picking `cover.html` vs `cover_typographic.html`
  per project belongs in Plan 3's AE workflow. Until then, both files
  exist; the rendering pipeline picks based on a fixture choice.
- **Real St. Nick's logo file.** The typographic wordmark stands in.
  When a real SVG/PNG logo lands in `Branding Board/`, swap the markup
  for an `<img>` reference in both layouts.
- **Logo-on-photo cover.** Was discussed and deferred. Not part of this
  addendum.
- **Brand-coherence sweep across the other 16 layouts.** They stay as
  shipped in Plan 2. The typographic style is fallback-only, not a
  parallel design system.

## 8. Files added / modified

**Added:**
- `skill_assets/fonts/Playfair-Display-Bold.ttf`
- `skill_assets/fonts/Playfair-Display-Italic.ttf`
- `skill_assets/layouts/cover_typographic.html`
- `skill_assets/layouts/showcase_typographic.html`

**Modified:**
- `skill_assets/layouts/brand.css` — add 3 `@font-face` blocks + `--font-display` token.
- `tests/fixtures/riverside.py` — append `cover_typographic_ctx`, `showcase_typographic_ctx`.
- `tests/test_layouts.py` — append 2 entries to `LAYOUT_CASES`; rename or generalize the all-N gate test.
- `tests/test_fonts_present.py` — assert Playfair Display files are present.
