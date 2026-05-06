# Plan 8 — execution resumption note (2026-05-06)

**Supersedes:** `docs/superpowers/2026-05-05-plan-8-resumption-note.md` (T1-T3 baseline).

**Purpose:** Capture exactly where Plan 8 execution paused so the next session can resume without re-reading the conversation.

## Where we are

- **Branch:** `plan-8-skill-bundle` (not pushed since the 2026-05-05 break — push before review).
- **Tests:** 150/150 passing on the branch.
- **Tasks complete:** T1-T6 fully (implementation + spec review + code-quality review + fixes).
- **Tasks in progress:** T7 implementation landed (`5b4137c`), **but spec review + code-quality review were not run** — paused before dispatching reviewers.
- **Tasks remaining:** T7 review, T8-T12 + final cross-task review + T13 (manual smoke + merge).

## Commit history this session (newest first)

```
5b4137c plan-8 t7: scaffold_project() module          # implementer DONE, unreviewed
ef0639f plan-8 t6 fix: align renderings + folder REQUIRED_SUBDIRS to canonical layout
e9673a8 plan-8 t6 fix: drop unused Path import (regressed T4 fix)
79301d5 plan-8 t6: aggregate inspect_project() with W1-W8 wrap
670496a plan-8 t5 fix: drop unused Path import + hero_images guard + plural test
83d023f plan-8 t5: inspector Renderings readiness check
3ff8291 plan-8 t4 fix: close workbook + test conventions + mirror comment
6a51a6d plan-8 t4: inspector Worksheet readiness check
```

## What landed in T4-T7

- **T4 — Worksheet inspector** (`skill_assets/proposal_build/inspector/worksheet.py` + tests). Detects missing/locked/empty worksheet, missing required columns, blank customer-facing copy per row, missing tiers per row. Fix added `wb.close()` in `try/finally`, dropped unused `Path` import, added mirror comment for column constants.
- **T5 — Renderings inspector** (`renderings.py` + tests). Detects empty renderings, files in `_inbox/`, unresolved hero_image references. Fix dropped unused `Path` import, added `isinstance(hi, str)` guard on `hero_images` plural iteration (a stringly-typed value would otherwise iterate character-by-character), added test for the plural branch, also tightened singular `hero_image` guard to `isinstance(hero, str) and hero`.
- **T6 — Aggregator `inspect_project()`** (`inspector/__init__.py` + integration tests). Orchestrates folder/brief/worksheet/renderings checks then runs the parser's W1-W8 validators. The integration test exposed three real bugs in earlier T2/T4 work which the implementer fixed inline (authorized by the plan's explicit instruction):
  - Folder canonical names: `01 - Project Background` → `01 - RFP`; removed `02 - Renderings/Greenery references` (lives at project root, not under renderings); added `02 - Renderings/Unused Renderings`.
  - Worksheet header-row search now mirrors `parser.worksheet._find_header_row` (header is not always row 0; real worksheets have a title block + pricing summary above).
  - Worksheet data-row regex now matches `parser.worksheet._LINE_NUM_RE` (`^(?:\d+|E\d+)$`).
  - Removed stale `.~lock....xlsx#` LibreOffice file that had been committed to Riverside in April and was tripping `worksheet-locked`.
  - Renderings inspector: dropped misrouted `Greenery references` from `SEARCH_SUBDIRS` (canonical layout puts greenery at project root, not under `02 - Renderings/`).
- **T7 — Scaffold module** (`scaffold.py` + tests). `scaffold_project(target, source=None)` copies `_template_project/` into a new project folder, refuses overwrite, creates intermediate parents. Implementer corrected the plan's `01 - Project Background` assertion to `01 - RFP` while writing.

## Outcomes

- Riverside fixture inspects as **`Ready to generate (21 warning(s))`** — 11×W6 (internal-marker hints) + 10×W1 (unused renderings). Matches the ratified state.
- Template fixture reports 12 blockers (well above the test's `>= 5` floor).
- Inspector subsystem is feature-complete; CLI integration (T8/T9) is the next layer.

## Recurring patterns — apply automatically in T8-T12

The reviewer keeps catching the same handful of issues. The implementer prompt should pre-fix these inline so spec/quality reviews are clean:

1. **`from __future__ import annotations` on every new `.py` file.** This is non-negotiable. The plan's test snippets often omit it — add it as line 2 (after the docstring).

2. **Dead `Path` import in test files.** Under `from __future__ import annotations`, `Path` only as an annotation does NOT require the import. The import is needed ONLY when `Path()` is constructed at runtime (`Path(__file__).resolve()...`) or used as a value (`isinstance(x, Path)`). The fix subagent has had to drop this import THREE times across T4/T5/T6 — bake the rule into every implementer prompt.

3. **Unused `import pytest`.** Only keep when calling `pytest.X` directly (`pytest.skip`, `pytest.raises`, `pytest.fixture`).

4. **Modern union `str | None`, NOT `Optional[str]`.** (Already consistent, but watch for it.)

5. **Avoid `field` as loop variable name.** Shadows `Finding.field`. Use `field_name` or similar.

6. **Mirror "source of truth" lists with a comment.** When the inspector duplicates a constant or path from the parser, add `# Mirrors parser.X. Keep in sync.` (precedent: `inspector/brief.py:11`, `inspector/worksheet.py:13`).

7. **Resource hygiene.** `openpyxl.load_workbook(read_only=True)` MUST `wb.close()` in a `finally` block (caught on T4). `frontmatter.load` opens/closes internally — no try/finally needed.

8. **Plan errata — canonical project layout.** The plan was written before the layout was nailed down. The actual `_template_project/` has: `01 - RFP`, `02 - Renderings/{Base Scope, Enhancements, Unused Renderings, _inbox}`, `03 - Scope & Pricing`, `04 - Process & Notes`. Riverside also has `Greenery references/` and `Downtown Riverside MetroLink/` and `RFP/` at project root. Whenever the plan text contradicts on-disk truth, prefer disk. Specifically watch `01 - Project Background` (wrong) → use `01 - RFP`.

## Deferred bugs to address in T7+ tasks

These were identified during reviews but explicitly deferred:

- **`brief.py` doesn't detect unsupported sections.** If an AE writes `## Pillars` in their Brief, `brief.check()` returns no findings, the parser's `_fill_pillars` raises `ProjectLoadError("Brief 'Pillars' section is not supported in V1...")`, and the aggregator's `except ProjectLoadError: return []` swallows it silently. The AE sees a clean report, then generation fails at runtime. Fix in `brief.py` by adding an unsupported-sections check. (Surfaced in T6 code-quality review.)

- **`.gitignore` has `~$*.xlsx` (Microsoft Office) but not `.~lock.*#` (LibreOffice / macOS).** Adding `.~lock.*#` would prevent the stale-lock recurrence that broke T6. Hygiene only — not blocking. Could land as part of T12 cleanup.

## Subagent-driven-development workflow recap

Each task is dispatched as: implementer → spec compliance reviewer → code-quality reviewer → fix subagent (if issues) → re-review → mark complete. Use `general-purpose` agents for implementer/spec reviewer; use `feature-dev:code-reviewer` for the code-quality stage.

The TodoWrite list has all remaining tasks tracked. Confirm with `TaskList` before starting.

## How to resume in the next session

Open a fresh Claude Code session in `/Users/Daniel-Admin/Documents/Claude/Projects/proposal-build/`. Then:

1. Confirm branch and baseline:
   ```bash
   git checkout plan-8-skill-bundle
   git log --oneline -1     # expect 5b4137c (or this resumption-note commit if pushed after)
   source .venv/bin/activate && pytest -q 2>&1 | tail -3   # expect 150 passed
   ```

2. Tell Claude: *"Resume Plan 8. Read this resumption note (`docs/superpowers/2026-05-06-plan-8-resumption-note.md`) and the implementation plan (`docs/superpowers/plans/2026-05-05-plan-8-skill-bundle.md`). Invoke `superpowers:subagent-driven-development`, dispatch the spec compliance reviewer for T7 (scaffold module, commit `5b4137c`), then continue the dispatch-implementer-then-review pattern through T12."*

3. After T12, dispatch a final `feature-dev:code-reviewer` agent across the full T1-T12 diff (`git diff main..plan-8-skill-bundle`) before merging.

4. T13 is the manual smoke test in Claude Desktop — Daniel runs it; controller handles the merge once smoke passes.

## Tasks remaining (per TodoWrite)

- **T7 review** — Scaffold module already implemented at `5b4137c`; spec compliance + code-quality reviews not yet dispatched. Start here.
- **T8** — CLI `inspect` subcommand (modify `cli.py` + tests). Plan §Task 8.
- **T9** — CLI `scaffold` subcommand (modify `cli.py` + tests). Plan §Task 9.
- **T10** — `skill.md` manifest. Plan §Task 10.
- **T11** — `AE_SOP.md`. Plan §Task 11.
- **T12** — Skill bundle smoke test (`tests/test_skill_bundle.py`). Plan §Task 12.
- **Final cross-task code review** — `feature-dev:code-reviewer` over `git diff main..plan-8-skill-bundle`.
- **T13** — Manual smoke test (Daniel) + merge to main (controller).

## Untracked files on disk (intentionally not committed)

Same set as 2026-05-05; carried over:

- `Master Proposal Reference/StNicks_Proposal_v2_Master.pdf`
- `Projects/Downtown Riverside Metro Link/02 - Renderings/Base Scope/Wreath - Brick Column with Garlands copy.png`
- `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - Scope Worksheet - prebackup.xlsx`
- `skill_assets/Branding/about_hero_strip.jpg` (leftover from v3 polish; layout no longer references it)

Leave them untracked.
