# Plan 3 — S4 polish session handoff (2026-05-04 EOD)

**Status:** Riverside MetroLink proposal ships customer-ready. Branch `plan-3-phase-2-generation`. 110 tests passing. Final compressed PDF (~1 MB after ghostscript /ebook) sent to Jonathan Yang for review.

## What landed this session (commits since 2026-05-03 wrap-up)

In rough order:

1. `S1 bug sweep` — pricing PDF multi-page fix, exec-summary "STATIONS" → "ZONES" label, payment terms 50/50, Brief signing_deadline +45 day policy, perimeter overflow fix
2. `Pricing PDFs on 8.5x11 portrait` — supplements use US Letter; deck stays 16:9
3. `S2 multi-image zone support` — new zone_solo_gallery layout with hero_images list, gallery_fit ('cover'|'contain'), gallery_orientation ('stacked'|'horizontal'), gallery_emphasis ('equal'|'feature_first'); hero_fit option for single-hero zones
4. `Investment tier cards` — TIER + price as header line ('ESSENTIAL  $88,906'), tagline, divider, highlights bullets, ALL-IN footnote. Multi-year partnership banner removed → footer line. tier_highlights map in Brief frontmatter drives card content.
5. `Scope of Work` — Brief sections Scope Includes + Add-Ons added to BULLET_SECTIONS (root cause of "no spacing" was bullets parsing as one paragraph)
6. `Greenery Mood Board` — new dedicated slide (material_palette.html). Inserted after Creative Vision when greenery_references is non-empty. 3 composite shots + descriptive copy.
7. `Customer contact` — client_contact_name/title/email/phone in Brief; Cover gets "PREPARED FOR" block; Sign-off pre-fills printed name + title + contact row.
8. `St. Nick's logo` — embedded in every page header via _LOGO_PATH constant, available globally through _project_base ctx. Logo files: skill_assets/Branding/ST NICKS LOGO.png + LOGO 2.png.
9. `Copy refresh — Size→Item→Details format` — all 25 worksheet customer-facing descriptions + all Brief zone bullets + Scope Includes + Add-Ons + tier_highlights rewritten.
10. `Service-wrapper bullets pruned` from Z01/Z02/Z03/Z08 — Z06 Stair Tower kept its bullets (Daniel exception).
11. `Renderings refreshed` — `Large Tree - Traditional with Topper.jpg` (new, replaces no-topper) + `Spiral Tree - LED Red Green.png` (revised). Old archived to Unused Renderings/.
12. `Date updates` — proposal_date 2026-05-04 (today), signing_deadline 2026-06-18 (today + 45d), fabrication_lock 2026-07-31. Exec summary FAB LOCK row dropped; GO LIVE shows "November 2026" only.
13. `Cover image swap` — Large Tree with Topper now on cover (also in Z04 — duplication noted; Daniel OK with it for now).

## Where things stand

- **Riverside is shipped.** Compressed PDF at `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal - compressed.pdf`. Sent to Jonathan; awaiting his feedback.
- Tests: 110 pass.
- Coverage report W1 warnings reduced (more renderings now used by galleries + greenery refs); W4 false alarm still present (validator does substring match — "ENHANCED" inside Signature label trips the check).

## Known deferred items (Task 6.5 cleanup candidates for next session)

- **W4 validator false alarm** — `parser/validate.py:check_tier_scenarios_drift` does substring match for tier-name-in-label; Signature's label "SIGNATURE — Enhanced + ..." trips the Enhanced match. Fix: prefix-match instead of substring.
- **Investment slide cover-image duplication** — Large Tree with Topper used as both cover AND Z04 Plaza Centerpiece hero. Daniel OK with it but worth flagging if next iteration finds a different cover.
- **Case study slide skipped** — Daniel will pick City of Paramount or Long Beach Airport later. case_study: skip in current Brief.
- **Itemized pricing page count** — Essential 4pp / Enhanced 4pp / Signature 4pp on 8.5×11. Could tighten to 2-3pp by trimming margins or shrinking line item font, if desired.
- **PDF compression** — currently a manual `gs` post-step. Could auto-wire into the generate CLI as an optional flag (`--compress`).
- **Logo dark/light variants** — `ST NICKS LOGO.png` works on light pages; on the dark Creative Vision slide it may need the LOGO 2 variant or a CSS filter. Not yet tested.
- **Greenery references default** — currently 3 hand-picked filenames in Brief; could auto-discover all images from `Greenery references/` folder if Brief is silent.

## Jonathan's feedback (priority backlog for next session)

Captured 2026-05-04 EOD. Cover logo already applied; everything else queued.

### Already done at session end
- ✅ **Cover logo** — added prominent 0.9in St. Nick's logo to top of cover left panel above the rule + season label.

### Cross-cutting copy / tone
1. **Punctuation pass** — needs review throughout. Specific issue: "Design Direction Holiday Express." reads weirdly because design_phrase ends with a period. Decide: drop the period from `design_phrase` in Brief OR strip trailing punctuation in templates that pair it with a label.
2. **Remove em dashes (—) globally** — "looks very AI." Hard rule going forward. We've used em dashes pervasively in zone bullets, customer-facing descriptions, taglines, etc. Replace with: en dashes (–) for spans, commas, periods, parens, or restructure. **Worksheet 25 customer-facing rows + Brief everywhere + tier_highlights + tagline copy all need a sweep.**
3. **More festive, less corporate tone** — overall stylistic direction. Consider: warmer accent colors, more decorative typography or flourish elements, holiday-themed icons or visual flourishes between sections. Currently the deck reads very business-formal. (Open-ended note for design exploration; no specific change yet.)

### Slide-by-slide

4. **Pole Banner Program (Z01)** — add a note that **custom designs are optional** ("we can custom design any pole banner"). Standing line that should appear on every pole banner zone slide across projects.
5. **Station Entrance Wreaths (Z03)** — image is too zoomed out. Make larger or more focused on the wreath as the focal point.
6. **Plaza Centerpiece (Z04)** — likely fine, but check after title-shrink change (#11 below).
7. **Perimeter & Driveway Garlands (Z05)** — currently 3 images (decorated swag plaza fence + pathway + fence). Switch to **2 images: fence rendering on the LEFT + building eave example on the RIGHT**. Make them larger. Need to add a building-eave rendering — none currently exists in the renderings folder (we have garland-on-fence shots but no eave-installed shot). May require a new rendering OR repurposing one.
8. **Walk-Through Photo Moments (Z07)** — the Lighted Gift Box arch rendering "looks weird." Replace with a better shot or restructure.
9. **City of Riverside Bell Display** — deserves its OWN slide. Full-bleed treatment. Pull out of Z08 Signature Add-Ons gallery.
10. **Gift Box Tower** — also deserves its own slide. Pull out of Z08.
   - With #9 + #10, Z08 Signature Add-Ons becomes Snowflakes-only (or merge into something else / drop the Z08 slide).

### Layout / structural

11. **Smaller, more tucked-away titles across all zone slides** — "they're not really that important other than just for placeholders." Frees vertical space for larger images. Apply to zone_solo + zone_solo_gallery layouts: drop zone-name font from 28pt → maybe 18-20pt, smaller subtitle, less margin.
12. **Slide order: Scope of Work AFTER Investment** — currently `... → scope → case_study → investment → terms → ...`. Swap to `... → investment → scope → terms → ...`. Single line change in `composer/__init__.py:48-62`.
13. **NEW: Full-page À-La-Carte Add-Ons table** — clean tabular layout listing every Enhancement with description and price. Currently Add-Ons live as bullets on the Scope of Work slide; this becomes its own dedicated slide. Likely sits near Investment/Scope. Probably a new layout (e.g., `a_la_carte.html`) + ctx_builder + slide-plan insertion.

### Implementation order I'd suggest

1. Em-dash sweep (worksheet + Brief — global find-replace, mechanical) — clean the foundation before drawing on it
2. Punctuation pass on `design_phrase` and similar (small)
3. Slide-order swap (Scope of Work after Investment) — one-liner
4. Smaller titles across zone layouts — quick CSS tweak, big visual impact
5. Bell Display + Gift Box Tower as own slides — extract from Z08 (new layout? Or zone_solo_fullbleed with hero?)
6. À-La-Carte table slide — new layout + slide-plan insertion
7. Z05 Garlands — new building-eave rendering + 2-image layout
8. Z03 Wreaths zoom + Z07 Gift Box rendering swap
9. Pole Banner "custom designs" note (small Brief tweak per project, or template-level boilerplate)
10. Festive tone exploration (open-ended; defer until others are done)

## Pickup commands

```bash
cd /Users/Daniel-Admin/Documents/Claude/Projects/proposal-build
git checkout plan-3-phase-2-generation
source .venv/bin/activate
pytest --tb=no -q | tail -3   # should show "110 passed"

# Regenerate Riverside
.venv/bin/python -m proposal_build generate "Projects/Downtown Riverside Metro Link"

# Compress for delivery
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile="Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal - compressed.pdf" \
   "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal.pdf"
```

## Memory entries to consult next session

Loaded automatically via MEMORY.md but worth knowing:
- `feedback_copy_format.md` — Size→Item→Details mandate
- `feedback_eyeball_specifics.md` — ask before guessing on visual fixes
- `feedback_redundant_service_bullets.md` — service wrapper is implied, don't bullet it
- `reference_riverside_metrolink.md` — RCTC project facts
- `reference_proposal_architecture.md` — pipeline, Brief contract, ctx guards, paging gotcha
