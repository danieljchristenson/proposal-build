# Plan 3 — Phase 5 wrap-up & next-session runway

**Date:** 2026-05-03
**Branch:** `plan-3-phase-2-generation`
**Status:** Phases 1–5 complete. 110 tests passing. Ready for Phase 6 (Riverside content migration) → first end-to-end Riverside PDF.

---

## What's on the branch

21 commits, build the full Parser → Composer → Renderer pipeline + CLI:

```
ce7603c feat(plan-3): cli.py + __main__.py — `python -m proposal_build generate` entrypoint
e8eb51e feat(plan-3): renderer/ — PDF assembly, pricing PDF, coverage report, layout pin
7ae0a20 feat(plan-3): itemized_pricing.html — 2-page master-derived pricing supplement layout
cf4baed fix(plan-3): composer cleanup from Task 13 review
e569c05 feat(plan-3): composer/ctx_builders.py + top-level compose() orchestrator
1f16858 feat(plan-3): composer/pricing.py — per-tier doc construction + partnership savings
301747c fix(plan-3): slide_plan polish from Task 11 review
f713c4b feat(plan-3): composer/slide_plan.py — auto_arrange_zones + pick_grouping
d3071f5 fix(plan-3): orchestrator polish from Task 10 review
9af2b03 feat(plan-3): parser/__init__.py — top-level build_project_model orchestrator
85944e1 feat(plan-3): parser/validate.py — CFD sniff test + zone coverage + W4/W1 warnings
665eda4 docs(plan-3): clarify why _PLACEHOLDER_RE alternation is load-bearing
21527ff feat(plan-3): parser/voice.py + parser/boilerplate.py + placeholder substitution
3e4972d docs(plan-3): add Plan 3 spec and implementation plan
ba02cf9 feat(plan-3): parser/renderings.py — filename → Path lookup with ambiguity detection
dacdb6a feat(plan-3): parser/worksheet.py — locates tables, parses 3 new columns, validates Tiers
1ff3a14 feat(plan-3): parser/brief.py — Brief.md frontmatter + sections parsing
6f0746a feat(plan-3): add 3 case study files
6360f6b feat(plan-3): add 4 voice preset drafts
f78d4dc feat(plan-3): add boilerplate library
687f765 feat(plan-3): add proposal_build package skeleton + ProjectModel dataclass
```

## What works right now

```bash
source .venv/bin/activate
python -m proposal_build generate "Projects/Downtown Riverside Metro Link"
```

Output today (smoke-tested):
- ❌ `BLOCKED — Brief: Brief not found at .../04 - Process & Notes/Project Brief.md`
- Coverage report written to `04 - Process & Notes/coverage_report.md`
- Exit code 1 (correct — gating on missing input)

The "BLOCKED on missing Brief" is the *correct* behavior. Phase 6 writes the Brief and unblocks generation.

## Recommended next-session order (fastest path to a Riverside PDF)

| Task | Time | What it does |
|---|---|---|
| **18** | ~5 min (paste) or ~30 min (tune) | Drop in the Project Brief.md from `docs/superpowers/plans/2026-05-03-plan-3-phase-2-generation.md` Task 18 step 1. |
| **17** | ~5 min | Archive the existing pre-Plan-3 PDF + PPTX so they don't get overwritten. |
| **19** | ~25 min | Run `scripts/migrate_riverside_worksheet.py` (described in Task 19 of the plan) to add the 3 new columns + 25 rows of drafted customer-facing copy. Then review/edit the customer-facing descriptions in Excel before generation. |
| **Run CLI** | ~2 min | `python -m proposal_build generate "Projects/Downtown Riverside Metro Link"` → 4 PDFs land in `03 - Scope & Pricing/`. |
| **Eyeball** | ~30 min | Open the 4 PDFs. Compare to the Plan-2-prime fixture-rendered PDFs (`tests/_output/`) and the master `Master Proposal Reference/StNicks_Proposal_v2_Master.pdf`. |
| **Iterate** | varies | Fix what's broken. Most likely culprits: customer-facing copy (edit worksheet), Investment tier card blank fields (see Task 6.5 #11), zone hero image picks (edit Brief). |

**Total:** ~90 min for a first Riverside PDF in your hand.

## What's deferred (Task 6.5 cleanup)

14 items from cumulative reviewer findings, bundled in TaskList task #24. Full description in `TaskList`. Highest impact:

- **#11** Investment slide tier cards emit empty tagline/highlights — verify visually first; may not need to fix
- **#12** `_placeholder_model()` drift safety — add a 1-line test before adding new ProjectModel fields
- **#1** Worksheet header whitespace tolerance — only matters if header text changes
- **#9, #10** New validator rules (pricing_format value validation + duplicate-coverage detection)

The other 9 items are quality polish (typed annotations, dead constants, naming). All deferrable.

**Recommended approach:** ship the Riverside PDF FIRST, then prioritize Task 6.5 fixes based on what you actually saw. Real bugs from real PDFs > speculative reviewer concerns.

## What's deferred until later sessions

- **Phase 7** (Tasks 21–22): `skill_assets/skill.md` (Claude Desktop manifest) + `AE_SOP.md` (operations manual). Not needed for direct CLI use; needed before Claude Desktop integration.
- **Phase 8** (Tasks 23–24): pytest e2e test (`test_e2e_riverside.py`) + final eyeball pass. The manual eyeball IS the e2e for this iteration; pytest version locks it for future runs.

## Transient artifacts to clean up (untracked)

The CLI smoke test wrote these — sandbox denied my `rm`:

```
Projects/Downtown Riverside Metro Link/04 - Process & Notes/coverage_report.md
Projects/Downtown Riverside Metro Link/04 - Process & Notes/runs/
```

They're not committed. Phase 6 will overwrite the report. Safe to `rm -rf` manually anytime.

## Where to look for what

- **Spec (locked decisions):** `docs/superpowers/specs/2026-05-03-plan-3-phase-2-generation-design.md`
- **Plan (per-task code):** `docs/superpowers/plans/2026-05-03-plan-3-phase-2-generation.md`
- **Phase 6 task content:** Plan §"Phase 6 — Riverside content migration" (Tasks 17–20)
- **Brief.md content for Riverside:** Plan Task 18 Step 1 (full YAML + prose, ready to paste)
- **Migration script content:** Plan Task 19 Step 1 (full Python with all 25 rows pre-filled)
- **Test status:** `pytest -v` from repo root with venv active → 110 passed
- **Branch:** `plan-3-phase-2-generation` (21 commits ahead of `main`)

## Sanity check before resuming

```bash
cd /Users/Daniel-Admin/Documents/Claude/Projects/proposal-build
git checkout plan-3-phase-2-generation
source .venv/bin/activate
pytest --tb=no -q | tail -3   # should show "110 passed"
python -m proposal_build generate "Projects/Downtown Riverside Metro Link"
# Should print: ❌ BLOCKED — Brief: Brief not found at ...
# Exit code 1. This is correct.
```

If both checks pass, you're ready for Phase 6.
