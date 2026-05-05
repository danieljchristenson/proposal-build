# Plan 3 — Ratification session handoff (2026-05-04)

**Status:** All 7 ratification items from `2026-05-04-riverside-v2-learnings.md`
landed on branch `plan-3-ratification`. 124 tests passing (was 110), Riverside
regenerates clean and compresses cleanly. Branch ready to merge into main.

## What landed this session

### Validator hardening (eliminates Riverside false alarms)
1. **W1 unused-rendering coverage.** `parser/__init__.py` now iterates
   `hero_images[]` and `greenery_references` into `referenced_filenames`.
   Gallery and mood-board images stop showing as "unused" in the coverage
   report. Verified on Riverside: every remaining W1 entry is a true orphan.
2. **W4 substring-match false alarm.** `parser/validate.py:check_tier_scenarios_drift`
   switched from `tier_name.value.upper() in upper` (substring) to
   `upper.lstrip().startswith(tier_name.value.upper())` (prefix match). Stops
   Signature's "SIGNATURE — Enhanced + ..." label from also matching ENHANCED.

### CLI ergonomics
3. **`--compress` flag** wired into `python -m proposal_build generate`.
   Calls ghostscript with `/ebook` profile on the customer-facing PDFs in
   `03 - Scope & Pricing/`. Run-dir copies stay uncompressed for archival.
   Riverside: 95M → 1.8M, matching the v2 manual compression.
   New module: `skill_assets/proposal_build/renderer/compress.py`. Raises
   `CompressionUnavailableError` if `gs` isn't on PATH.

### Quality gate
4. **W8 em-dash linter.** New `check_em_dashes(model)` in `parser/validate.py`
   scans every customer-facing field (frontmatter strings, Brief sections,
   scope_includes, add_ons, zone subtitles + bullets, worksheet
   `customer_facing` column, pillars/phases bodies, tier_highlights). Reports
   each em dash with field name + 80-char preview. En dashes (–) for numeric
   ranges are explicitly allowed. Riverside passes the linter cleanly,
   confirming the v2 sweep was thorough.

### Brief contract additions wired
5. **`greenery_description:` Brief override** (the docstring promised it;
   ctx_builder didn't read it). New optional field on `ProjectModel`,
   parsed in `parser/__init__.py`, consumed in
   `composer/ctx_builders.py:build_material_palette_ctx` as
   `model.greenery_description or default_copy`. Useful for single-tier
   projects where the default base→Signature progression copy doesn't fit.
6. **Template Brief documented.** `Projects/_template_project/04 - Process &
   Notes/Project Brief.md` now documents `venue_context:`, the widened
   `greenery_references:` resolver (searches `Greenery references/` →
   `Base Scope/` → `Enhancements/` in priority order), and the new
   `greenery_description:` override. Em dashes also stripped from template
   comments (consistent with the no-em-dashes rule).

### Open decisions resolved (status quo wins)
7. **Page-title size on content slides:** stays 50pt default. Scope and À La
   Carte continue to override locally to 32pt.
8. **Pole banner "custom artwork option" bullet:** stays project-level
   (AE writes per project). Documented as a "Zone Bullet Starter" in the
   template Brief so AEs see it as a reference pattern.

Both decisions saved to memory as `feedback_layout_defaults.md` so they
survive into the next session — keep the engine flexible, don't auto-inject
copy or sizing.

## Tests added

- `tests/test_parser_validate.py`: +12 tests covering W1 gallery/greenery
  coverage, W4 prefix-match, W8 em-dash linter (positive + negative cases
  including en-dash allowance).
- `tests/test_renderer_outputs.py`: +2 tests for ghostscript compression
  (size invariant + missing-gs error path).
- `tests/test_composer_slide_plan.py`: +2 tests for material palette default
  copy vs. Brief override.

Suite: **110 → 124 passing.**

## What did NOT change (still deferred from learnings doc §6)

- **Cover image still duplicates Z04 hero** on Riverside (Daniel OK with it).
- **Layout-version pin friction.** `--use-latest-layouts` is still required
  on every iteration that touches a layout file. Tabled as workflow knob.

## How to verify locally

```bash
git checkout main
git pull
source .venv/bin/activate
pytest                                                    # 124 passing
python -m proposal_build generate "Projects/Downtown Riverside Metro Link"
python -m proposal_build generate "Projects/Downtown Riverside Metro Link" --compress
```

Riverside is the regression fixture; both invocations should succeed. With
`--compress` the proposal PDF in `03 - Scope & Pricing/` should drop from
~95M to ~1.8M.

## Suggested next focus

The next real project is the natural unblock. The engine has now absorbed
every durable lesson from Riverside v2; new projects should onboard
faster (template Brief documents the new fields, em-dash linter catches
copy regressions, --compress is one flag instead of a manual step).
