# FIGat7th Session Notes — Pattern Learnings for Plan 9

Running notes captured live during the FIGat7th build. After FIGat7th ships, a separate session will turn these into the formal Plan 9 spec for the new "creative menu / ROM pricing" skill capability.

## Project framing decisions (new patterns vs. existing skill)

- **First-pass concept deck, no tiers.** Existing skill assumes Essential/Enhanced/Signature. This proposal is a creative-menu introduction deck — single recommended scope, no tier comparison. `recommended_tier` was set to "essential" in the Brief as a placeholder; the builder probably needs a no-tier mode.
- **Sectioned structure with mixed alternates / always-included.** Three sections with different selection rules within each:
  - Section 1 (Overhead): single direction, no choice
  - Section 2 (Tree): single direction, no choice
  - Section 3a (Arches): four alternates, customer picks one
  - Section 3b (Standalones): four items, all included
  
  Existing schema doesn't model "alternate group" relationships. New `alternate_group` field in worksheet captures this.
- **Customer-choice menu vs. tiered recommendation.** Layout pattern needed: a "section gallery" or "alternates spread" that surfaces 4 options on one or adjacent pages, vs. existing per-zone-with-tier-badge layout.

## ROM pricing schema (locked 2026-05-08)

Per item, two presentation modes side-by-side:
- **Rental**: 1 line, low–high range, ALL-INCLUSIVE (item + install + removal + storage bundled). Never paired with separate service lines.
- **Purchase**: 2 lines:
  - One-time purchase price (low–high)
  - Annual service bundle (install + removal + storage combined as one annual fee, low–high)

Customer-facing pricing table = 3 columns: Item / Rental (annual, all-in) / Purchase (one-time + annual service).

ROM uncertainty captured as low–high ranges, not point estimates. Totals also become ranges; with alternate groups, totals are bookended by min-cheap-configuration and max-expensive-configuration.

## Workflow patterns observed

- **Multi-rendering input flow.** Daniel dropped batches of renderings mid-conversation as he iterated externally. Need a stable file-rename convention (`NN_descriptive-label.png`) so we can reference renderings unambiguously by number across turns.
- **Color-naming verification.** Eyeballing palette colors from low-light renderings is unreliable. Always cross-reference the palette board before describing. Saved as feedback memory.
- **Replace-and-supersede during the build.** Daniel iterated palette by dropping a new ornament package mid-session. Old renderings moved to Unused with original names; new renderings inherited the slot numbers. Pattern to formalize: "supersede" command that swaps one rendering for another, archiving the old.
- **First-pass framing reduces decisions.** Skipping tiers and pricing breakdown shortens dictation. Worth supporting an explicit "concept deck" mode alongside the full tiered scope.

## Open questions to resolve before Plan 9

- How does the no-tier menu mode plug into the existing composer / ctx_builders? New mode flag, or new compose path entirely?
- Should `alternate_group` drive UI on a single page (4-up gallery) or paginate (one slide per alternate)?
- ROM totals presentation: range bookends, single midpoint, or "from $X" framing?
- How does the customer-facing workbook (xlsx deliverable) handle ROM ranges? Two columns per metric (low / high)?
- Cover-slide and palette-board pre-built creative assets (FIGat7th had these) — bypass generation, treat as direct image inserts. Pattern needed.

## Session 2 — 2026-05-11 — Deck shipped

**Built four reusable layouts** (in `skill_assets/layouts/`):
- `image_fullbleed.html` — single-image edge-to-edge page for pre-designed cover/palette assets
- `section_divider.html` — dark transition page with eyebrow + 60pt section name + dimmed bg image
- `zone_4up.html` — 2×2 alternates/gallery grid with image cell + label below
- `rom_investment.html` — 3-column ROM pricing table (item / rental / purchase one-time+service)

**Built fixture**: `tests/fixtures/figat7th.py` with 13 slide ctxs + `SLIDES` list. Drives `render_proposal_pdf()` directly. Pricing data embedded as `PRICING` dict (item code → six-tuple); totals computed at module load.

**Final deck**: `Projects/Fig at 7th .../05 - Proposal Output/FIGat7th DTLA — 2026 First-Pass Concept Deck.pdf` — 13 pages, ~16 MB.

## Layout learnings for Plan 9

**WeasyPrint reality checks (vs Chrome/Safari):**
- CSS Grid with `grid-template-rows: 1fr 1fr` inside a flex parent does NOT resolve reliably. Symptoms: only first cell renders, rest collapse. **Fix**: use grid for COLUMNS only (single-row grid); for multi-row layouts, stack multiple grid containers each with explicit height (`height: 2.9in`).
- Nested `display: flex` with `min-height: 0` two layers deep can produce blank cells. **Fix**: prefer explicit pixel/inch heights over fr/percent inside content area.
- CSS `display: table` / `table-cell` works but doesn't honor `height: 100%` inside table cells when parent is flex.
- **Jinja `section.items`**: never use the key name `items` on a dict ctx — Jinja's attribute resolver picks the built-in `dict.items()` method before the key lookup. Use `rows` or another name.
- **StrictUndefined**: every variable referenced in a template MUST be present in ctx. Guard with `{% if foo is defined %}` for optional fields, or pass `""`/`None` explicitly.
- **Dark-background totals row**: a default text color of charcoal becomes invisible on a charcoal bg. Always override colors when nesting elements inside a dark section.

## Iteration after first-pass review (added 2026-05-11)

Three rounds of visual feedback from Daniel surfaced these durable lessons:

1. **`object-fit: cover` crops renderings — never default to it for menu galleries.** AE cares about every rendering being fully visible. Switched to `object-fit: contain` across the deck (creative_vision, zone_4up, zone_2up_gallery). Added `hero_fit` opt-in flag to creative_vision so existing tiered-fixture decks (Riverside, Pier 39) keep their cover-fit behavior — gallery decks pass `hero_fit='contain'`.
2. **Dark image-cell backgrounds look like ugly "wings" against a light page.** When `contain` produces letterbox bars, the bar color reads as dead space, not negative space. Setting `.cell-image { background: white }` makes the bars vanish into the page and the rendering reads as a discrete framed picture. **Rule**: image cells should match the page background, not the page chrome.
3. **2×2 image grids in a 13.33×7.5 landscape page can't show a rendering meaningfully — split to 2-up.** With ~12in × 6.1in content area, 2×2 cells max out at ~5.9in × 2.4in (2.5:1 aspect). Landscape renderings (1.5:1) leave ~50% empty space per cell; portrait renderings leave even more. Splitting each section into two 2-up slides gives each rendering ~5.9in × 4.5in (1.3:1 aspect) — nearly 2.5x more visible area. **Rule**: gallery decks default to 2-up across multiple slides, not 4-up on one slide. 4-up is for thumbnail/index uses only.

## Layout patterns for Plan 9 to formalize

- **Image-only slide layout** — bypass templating for pre-designed creative assets (cover, palette/mood board). Almost every multi-rendering proposal will have these.
- **Section divider** — group multi-section decks. Reusable for any sectioned proposal.
- **N-up gallery** — 2×2 with optional "Customer Choice — Pick One" / "All Included" banner. Generalize beyond 4 cells with N-up auto-arrangement (consider 2up, 3up, 4up, 6up presets).
- **ROM pricing table** — 3-column (item / rental / purchase). The "alternate-group" handling (visual ALT tag + min/max bookend totals) is unique to creative-menu proposals — formalize as `alternate_group` field at the worksheet schema level so totals can be computed automatically.
- **Multi-page investment** — line-item tables routinely overflow at >8–10 items. Build automatic page-fragmentation into the layout: render N rows per page, last page gets the totals row + footnote.

## Open layout debt

- `slide-07` (zone_solo for tree): The 7-bullet element list extends past the image's vertical center. Visually fine but could benefit from a `zone_solo_long` variant that drops the image to half-height when bullet count > 5.
- Investment p1 has dead vertical space below Section 3a (the 4-arch list ends ~2/3 down the page). Could backfill with subtotal rows or a "continued on next page" pointer.
- The `feature-bell-lantern` → `feature-ornament-bench` mislabel from session 1 made it through to a rendered slide; the fixture's customer-facing description is the bench version. Pattern: AE should QC rendering labels at intake before pricing/copy lock to avoid this trickle-through.

## Session 1 — 2026-05-08 (paused mid-build)

**Completed:**
- Brief locked (status: ready, all phase-1 fields populated, Creative Direction + Customer Goals + 3 Showcase Sections written)
- 27 renderings curated and renamed (12 Base Scope, 15 Unused, 1 design comp). Multi-pass replacement workflow because Daniel iterated palette mid-session.
- ROM pricing schema designed (rental all-inclusive single-line vs purchase one-time + service-bundle two-line)
- Pricing dictation captured for all 11 line items; customer-facing copy refined per format rules
- Item 42 misnamed in original rename pass — corrected from "feature-bell-lantern" to "feature-ornament-bench" after Daniel clarified the actual concept

**Open for next session:**
- Build 12-page deck PDF per agreed structure (see project memory `RESUME-NEXT-SESSION` block)
- Optional: customer-facing workbook xlsx and itemized pricing PDF (Riverside-style deliverable set)
- Plan 9 spec drafting (separate session after FIGat7th ships)

**Patterns to capture for Plan 9:**
- "Replace-and-supersede" rendering workflow (numeric slot inheritance, old → Unused with descriptive renamed file)
- Tree subdivision into hero + enhancement package as separate priced line items
- Item 42 rename revealed: rendering filenames need verification with the AE before committing — eyeball-only labels can mislabel concepts
- Pricing dictation produces a mix of point estimates and ranges; worksheet schema needs to support both gracefully (low=high for points)
- Lift equipment / per-unit overhead pricing (canopy's $5K lift fee under purchase mode) doesn't cleanly fit "service = install+removal+storage" — schema may need a per-item-overhead category for equipment-rental-style line items

