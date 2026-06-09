# St. Nick's Editorial — Proposal Theme System (Design Spec)

**Date:** 2026-06-09
**Status:** Approved direction; pending plan
**Author:** Daniel + Claude (brainstorming session)
**Supersedes nothing** — additive to the existing `brand.css` system.

---

## 1. Goal

Make St. Nick's proposals look materially more professional by introducing a
**dark, editorial design system** ("St. Nick's Editorial") as a **swappable
theme** that sits beside the current look ("Classic"). The engine, content
pipeline, and layout HTML stay shared; only the *skin* changes.

The bar is St. Nick's own NX Experiential deck (dark ground, red accent
hairline, bold caps headlines, oversized stat numbers, color-coded zones,
refined data viz) — matched and beaten on **warmth + personalization**, using
**only St. Nick's brand assets** (this is the St. Nick's product, not NX).

## 2. Why dark / why now (research basis)

Four parallel research streams (saved in `docs/superpowers/research/2026-06-09-*.md`)
converged:

- **Dark is the holiday-décor industry signature** — the product *is light*, so
  near-black grounds make illuminated photography perform (Blachere "Magicians
  of Light," MK Illumination, American Christmas). Light is *reserved* for
  information pages (Company Profile, pricing clarity).
- **Generic tells to kill:** ubiquitous default type, wall-of-text zones, dead
  white space, leading with process/product count instead of concept.
- **Premium tells to adopt:** named design concepts, oversized stat call-outs,
  "Your Investment" framing with value built first, landmark-client proof,
  before/after transformation, brevity (one idea per page, headline = takeaway).

## 3. Locked visual system

Verified against the brand board (`Branding Board/Branding Board Mood Board
Template.pdf`). **No gold, no serif, no decorative fonts** — the board mandates
Roboto + Poppins and "clean, modern, confident."

| Token | Value | Use |
|---|---|---|
| Ground (dark) | charcoal scale derived from brand `#1C1C1C` (e.g. `#121214` / `#1C1C1C` / `#26262A` surface steps) | page background, panels |
| Text on dark | `#ECEFF1` (brand light), never pure white | body, headlines |
| Accent (single) | brand red `#B31315` | top hairline rule, eyebrows, stat numbers, key marks |
| Secondary | brand navy `#12355B` | color-coded zone keys / data viz only |
| Muted text | brand gray `#555555` lightened for dark (e.g. `#7D7F85`) | captions, footers |
| Headlines | **Roboto Black, all-caps**, tight tracking | page titles, zone names |
| Body | **Poppins** (Light/Regular) | copy, captions |
| Numerals | `font-variant-numeric: tabular-nums lining-nums` | all prices + stats |

**Signature elements**
- **Red top hairline rule** (~4px) across every dark page.
- **Red tracked-caps eyebrow** + **Roboto Black caps headline** per page.
- **Stat call-outs** (oversized red number + tracked-caps label) replace dead
  space on otherwise sparse pages (e.g. single-image zones).
- **Named zone concepts** (e.g. "Compass North-Star"). **No three-word
  descriptor** (reads insincere — explicitly rejected).
- **Full-bleed renderings** with a gradient scrim for text legibility (no
  box-shadows — unsupported by WeasyPrint and unneeded).
- **"Your Investment" page:** oversized total, tabular numerals, committed-price
  framing, signing deadline as the close.

**Light pages (stay light, by rule):** Company Profile / About, and the
pricing-clarity pages (itemized pricing PDF already uses its own light template).

## 4. Architecture — the swappable theme layer

The seam that keeps this from muddling the system.

**Today:** `base.html` → `<link rel="stylesheet" href="brand.css">` (one file,
resolved from `LAYOUTS_DIR`); each layout sets `page-light`/`page-dark` via the
`body_class` block. No theme concept exists.

**Target:**
1. **Split CSS into core + theme.**
   - `brand.css` → keep theme-agnostic structure: `@page` geometry, `@font-face`,
     spacing scale, type scale, grid/chrome structure, utility *structure*.
   - `theme-classic.css` → the current color/treatment decisions (preserves
     today's look verbatim).
   - `theme-editorial.css` → the new dark system tokens + treatments.
2. **Select a theme per project.** Add a project-level `theme` field (Brief
   front-matter / project config), default resolved in the composer. `base.html`
   links core + the selected theme file: `<link href="{{ theme_css }}">`.
3. **Surface intent, not hardcoded body class.** Replace per-layout hardcoded
   `page-light`/`page-dark` with a per-page **surface intent** (`light` |
   `dark`) the *theme* maps to an actual background. Editorial maps most pages to
   dark and the About/pricing pages to light; Classic maps to today's choices.
   Implemented via a `theme` ctx var + a small surface-map, exact mechanism
   chosen in the plan.
4. **Shared layout fixes live in core / layout HTML** (see §6) so Classic
   benefits too.

**Rollout:** build + validate Editorial on the pilot, then make it the
**go-forward default** for new proposals. Classic remains a selectable fallback.
**No shipped deck is re-rendered or broken** — existing projects keep Classic
unless explicitly switched.

## 5. Per-slide-type treatment (Editorial)

All ~20 layouts get an Editorial treatment. Surface = dark unless noted.

- **Cover** — dark; St. Nick's logo, red eyebrow (season), Roboto Black caps
  title, full-bleed hero right with scrim. (Drop the redundant standfirst that
  repeats the title.)
- **Executive Summary** — dark; "At a Glance" panel + 3 proof cards; fill the
  mid-page dead zone (tighten grid / add a stat band).
- **Our Understanding** — dark; 4 panels, red rule, denser.
- **Creative Vision** — dark; **fix the text truncation and empty cards** (real
  bug today); concept statement + hero render + filled supporting cards.
- **Program at a Glance / Zone Index** — dark; numbered key, red zone numbers.
- **Zone solo / 2-up / feature / fullbleed** — dark; full-bleed renders, stat
  call-outs, no service-wrapper bullets (existing rule). **Kill dead space** on
  single-image zones.
- **Material / Mood Palette** — already dark and premium; align type to system.
- **Investment / ROM** — dark; "Your Investment," oversized total, tabular
  numerals, tier cards or committed-single-price per project. Pricing **table**
  uses real `<table>` markup (WeasyPrint-safe).
- **About / Company Profile** — **light** (unchanged rule).
- **Terms / Sign-off** — dark; clean.
- **Past Work / Tree Comparison / Case Study** — dark; align to system.

## 6. Shared layout fixes (theme-agnostic — Classic benefits too)

- Eliminate dead white space on single-image zone layouts (stat band /
  rebalanced grid).
- Fix Creative Vision body-copy truncation and the empty supporting cards.
- Consistent footer/eyebrow/hairline structure across layouts.

## 7. Pilot

**Riverside MetroLink** — the canonical repo fixture. Drives the existing
end-to-end tests, safest for engine work, and renders without OneDrive data.
Deliverable: full Riverside deck rendered in Editorial, reviewed end-to-end.

## 8. Scope / non-goals

**In scope (first release):** the theme layer (core/classic/editorial CSS +
theme selection + surface map), the Editorial treatment of all layouts, and the
shared layout fixes. Validated on Riverside, then promoted to default.

**Explicitly deferred (fast-follow, not this release):**
- Research-driven **content devices**: before/after transformation frames,
  guest-journey zone key-plan, dedicated Next-Steps/close page. These touch the
  content pipeline, not just the skin.
- Any serif/editorial-font evolution (rejected for now — off-brand).
- Gold/metallic accents (off-brand).

**Non-goals:** changing the content pipeline, parser, diff engine, or pricing
math; re-rendering or altering already-shipped customer decks.

## 9. Testing

- Existing `pytest` suite stays green; add tests for theme selection + surface
  mapping and that Classic output is byte-stable (no visual drift).
- Visual check: render Riverside in both themes; confirm Classic unchanged and
  Editorial matches the approved mockups.

## 10. Open questions (capture, decide in plan)

- Exact home for the `theme` field (Brief front-matter vs project config) and
  default-resolution point in the composer.
- Surface-intent mechanism (ctx var + map vs per-layout theme blocks).
- Whether `theme-classic.css` is a true extraction of current `brand.css` (zero
  visual change) or `brand.css` stays as Classic and only Editorial is added.

---

### Appendix — reference artifacts
- Mockups: `.superpowers/brainstorm/2903-1781019450/content/` (directions,
  editorial-dark, font-faceoff).
- Research briefs: `docs/superpowers/research/2026-06-09-*.md`.
- Caliber benchmark: NX Experiential Pier 39 deck (St. Nick's division).
- Current Editorial baseline to beat: Toyota Arena 2026 deck.
