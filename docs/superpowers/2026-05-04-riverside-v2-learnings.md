# Riverside v2 polish — learnings to ratify into the full project

**Date:** 2026-05-04
**Context:** This was the second pass on the Riverside MetroLink proposal,
driven by 13 items of feedback from Jonathan Yang plus a live revision pass
from Daniel. The proposal shipped as `FINAL Riverside MetroLink - 2026
Holiday Proposal.pdf` (1.8 MB compressed). Below are the durable rules and
architectural decisions that should fold into the design spec, the
template_project Brief, and the next round of plans.

---

## 1. Copy / tone conventions (durable)

These belong in the AE-facing Brief docs and in any "polish" prompt the
voice presets ship with.

- **No em dashes (—) anywhere customer-facing.** Replace with comma, period,
  colon, parentheses, or restructure with a preposition ("with", "in", "on").
  En dashes (–) are fine for numeric spans (`$88K – $200K`). Verified
  globally across Brief, worksheet column K, boilerplate, voice presets,
  case studies, runtime ctx_builders, and the Investment range. Em dashes
  read as AI-generated.
- **Customer-facing format: Size → Item → Color/Material/Details.**
  Already a memory rule; reaffirmed across all 24 worksheet rows + Brief
  zone bullets in this pass.
- **Don't list service-wrapper bullets** (annual install / removal / storage)
  on zone slides. Implied; redundant. Already a memory rule; reaffirmed.
- **Trailing periods on title-style phrases read awkwardly** when the phrase
  pairs with an eyebrow label. `design_phrase: "Holiday Express."` showed
  in the Creative Vision slide as "Design Direction / Holiday Express." —
  the period felt off. **Fix:** strip the trailing period at the source
  (Brief frontmatter), since the value is title-style, not a sentence.
  Standfirst lines with the same pattern (e.g. "The design direction for
  the 2026 program.") were also de-periodicized.
- **Tone target: festive but elevated, not corporate.** Open exploration
  deferred to a future pass.

## 2. Layout / visual decisions

- **Zone titles should be small.** `zone_solo` zone-name dropped 50pt → 22pt;
  `zone_solo_gallery` 28pt → 20pt; subtitles 16pt → 11pt and 12pt → 10pt
  respectively; title-area margin tightened. Frees ~30–40pt of vertical
  space per zone slide for the imagery, which is what carries the message.
- **Page-titles on content slides (Scope, À La Carte) should NOT use the
  default 50pt hero size.** Locally overridden to 32pt + 12pt standfirst
  on those slides because the cards/tables underneath looked "awkwardly
  low" otherwise. Worth considering whether 50pt should be reserved for
  cover/exec only and 32pt should be the default for body slides.
- **Feature-zone slides need a true full-bleed treatment with a SUBTLE
  text overlay.** The previous `zone_solo_fullbleed` layout (image 65% +
  dark text panel 35%) was rejected as "terrible" for hero-product zones
  like Bell Display and Gift Box Tower. New `zone_feature` layout: 100%
  full-bleed image, small text block in **top-left** corner (away from
  centered subjects), diagonal gradient scrim only in that corner so the
  rest of the image stays clean. Eyebrow + zone name + subtitle + 2–3
  bullets, all white-on-image with text-shadow for legibility.
- **Gallery images at different aspect ratios need `gallery_fit: "cover"`
  to share the same height.** The previous `contain` default left short
  images letterboxed and visually inferior. The layout now honors the
  `gallery_fit` field per zone (cover vs contain). Used on Z07 to make
  the walkthrough ornament and the lighted gift box arch share equal
  width and height.
- **Add-Ons belong on their own slide, not as a side-column on Scope.**
  New `a_la_carte` layout: full-width table with Enhancement description
  + price columns. Scope slide is now Includes-only and reads cleaner.
- **Feature additions deserve their own slide, not a 3-up gallery.**
  Bell Display and Gift Box Tower were extracted from the old Z08
  Signature Add-Ons gallery; each got its own `zone_feature` page.
  Z08 became Snowflakes-only (single image, `zone_solo`).
- **Garlands need to show BOTH undecorated and decorated states** so the
  tier story is legible. Solved by adding the undecorated swag rendering
  to the Greenery Mood Board (4-up) and revising the mood-board copy to
  call out the base→Signature progression.

## 3. Information architecture

- **Slide order: Investment BEFORE Scope.** The previous order
  (Scope → Investment) buried the price; flipping reads more naturally
  ("here's what it costs at three tiers, then here's what each tier
  includes"). Single-line composer change.
- **Final deck order (Riverside, 21 slides):**
  Cover → Exec Summary → Understanding → Creative Vision → Greenery Mood
  Board → Z01–Z10 zones → Investment → Scope → À La Carte → Terms →
  Sign Off → About.
- **À La Carte slide is conditional**: only inserted when `model.add_ons`
  is non-empty (composer guards on `if model.add_ons:`).
- **Pole banner zones get a standing "custom artwork option" line.**
  Riverside got it as a Brief bullet; if it should appear on every pole
  banner zone across all projects, the durable place is a layout-level
  conditional or a default Brief bullet in `_template_project`.

## 4. Brief contract additions

Two new optional Brief fields landed this session — both should be
documented in `_template_project/Project Brief.md`:

- **`venue_context:` (string, optional).** Replaces the auto-generated
  "X is a Y-zone program covering …" one-liner on the Understanding
  slide. Used for richer venue descriptions: scale, attendance, foot
  traffic, atmosphere. Falls back to the auto-generated string when
  empty, so existing projects don't break.
- **`greenery_references:` resolver widened.** Previously resolved
  only inside `Greenery references/`. Now also searches
  `02 - Renderings/Base Scope/` and `02 - Renderings/Enhancements/`,
  in priority order. AE can pull project renderings into the mood
  board without duplicating files.

## 5. Code / architecture improvements made this session

Concrete diffs ready for the next plan to formalize:

- New layout: `skill_assets/layouts/zone_feature.html` — full-bleed
  feature treatment, text top-left with subtle scrim.
- New layout: `skill_assets/layouts/a_la_carte.html` — full-page
  Enhancement table.
- Modified `zone_solo_gallery.html` to honor `gallery_fit: cover`
  (was hardcoded to `contain`).
- Modified `zone_solo.html` and `zone_solo_gallery.html` to drop title
  font sizes.
- Modified `scope.html` to be single-column (Includes only) with
  shrunken title-area; bumped layout-version to `2026-05-04-r3`.
- Composer: `zone_feature` and `a_la_carte` registered in
  `_resolve_zone_block` and `_build_ctx`. Slide order swapped so
  Investment precedes Scope.
- Parser: `_resolve_greenery_refs` extended; new `venue_context` model
  field plumbed through.
- Customer-facing standfirsts and runtime f-strings cleaned of em
  dashes (Understanding venue line, exec summary body, sign-off
  digital signing note, greenery default copy).

## 6. Known gaps / deferred work

These didn't block Riverside v2 shipping but should be addressed before
the next project ships:

- **W1 unused-rendering false-alarm.** `parser/__init__.py:56-73` only
  collects `referenced_filenames` from `hero_image`, `cover_image`,
  `creative_vision_hero`, `case_study_hero` — NOT from `hero_images[]`
  (galleries) or `greenery_references`. So gallery and mood-board images
  appear as "unused" in coverage reports even when actively shown. Fix:
  iterate `hero_images` and `greenery_references` into the referenced
  set. Trivial change; meaningful coverage-report quality bump.
- **W4 substring-match false alarm.** `parser/validate.py:check_tier_scenarios_drift`
  uses `tier_name in label.upper()`. Signature's label
  `"SIGNATURE — Enhanced + …"` matches "ENHANCED" because of the
  substring. Switch to prefix-match.
- **PDF compression should be a CLI flag.** The `gs … /ebook` step is
  currently a manual post-step. Wire `--compress` into the generate
  command so the FINAL deliverable is one command.
- **Greenery default copy is project-generic.** It now mentions tier
  progression, which works for projects that have one — but for
  single-tier projects, the copy doesn't apply. Either add a
  `greenery_description:` Brief override (the docstring already
  promises this; it's just not wired) or branch the default on
  `pricing_format`.
- **Cover image still duplicates Z04 hero.** Large Tree with Topper
  appears on the cover AND in the Plaza Centerpiece gallery. Fine for
  Riverside; flag if next project has more rendering variety.
- **Layout-version pin drift requires `--use-latest-layouts` on every
  iteration that touches a layout file.** Frictionful during a
  fast-iteration session. Consider auto-bumping the pin when
  `--use-latest-layouts` is invoked, or making it the default during
  active development with an explicit `--lock-layouts` opt-in for
  reproducibility runs.

## 7. Workflow patterns that worked

- **"Show me the diff before committing if anything feels ambiguous"**
  is a useful instruction. The em-dash sweep on the worksheet's 24
  customer-facing rows used a Python script that printed every
  before/after pair before saving.
- **Backup before mutating an .xlsx** (`prebackup.xlsx` companion file)
  caught one stale-lock scenario this session.
- **Eyeball checkpoints after meaningful change clusters** (em-dash
  sweep, layout structure changes, new slides) kept the iteration loop
  tight. Trying to land all 13 items before showing Daniel anything
  would have wasted cycles.
- **Ask before guessing on visual fixes** (`feedback_eyeball_specifics`
  memory) — confirmed multiple times this session: the Z03 wreath
  zoom and Z07 gift box "weird" issues were mostly resolved by Daniel
  re-rendering the source images, not by code changes.

---

## Suggested next-plan ratifications

In rough priority order for the next planning session:

1. Update `_template_project/Project Brief.md` to document
   `venue_context:` and the widened `greenery_references:` resolver.
2. Add an em-dash linter pass to `parser/validate.py` (W-level
   warning when any customer-facing string contains `—`).
3. Fix the W1 unused-rendering and W4 substring-match validators.
4. Wire `--compress` into `proposal_build generate`.
5. Decide whether 32pt should be the default page-title size for
   content slides, vs. an opt-in override.
6. Decide whether the pole banner "custom artwork option" should be
   layout-level or stay project-level.
7. Wire `greenery_description:` Brief override (the override the
   docstring already mentions).
