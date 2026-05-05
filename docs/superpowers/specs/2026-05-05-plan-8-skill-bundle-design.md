# Plan 8 — Skill bundle: skill.md manifest + AE_SOP.md + inspector

**Status:** Design — pending user review.
**Date:** 2026-05-05
**Predecessor:** Plan 3 (Phase 2 generation core, shipped 2026-05-04) + plan-3-ratification + Riverside v3 polish (2026-05-05).
**Successor:** Plan 4 (per-tier itemized pricing diff-mode regeneration), Plan 5 (Phase 1 rendering ingestion), Plan 6 (Phase 0 RFP intake).

## 1. Purpose

Wrap the existing Phase 2 proposal-generation pipeline as a deployable
Claude Desktop skill bundle that Daniel, Jonathan, and Jovany can use end
to end without invoking the CLI manually. Plan 8 deliverables:

- `skill_assets/skill.md` — skill manifest Claude Desktop reads on
  description match.
- `skill_assets/AE_SOP.md` — human-facing standard operating procedure for
  AEs.
- `skill_assets/proposal_build/inspector/` — deterministic Python package
  that reports project readiness as structured findings.
- `skill_assets/proposal_build/scaffold.py` — copies `_template_project/`
  into a new `Projects/<name>/` folder.
- New `inspect` and `scaffold` CLI subcommands on `python -m
  proposal_build`.
- Tests under `tests/test_inspector.py`, `tests/test_cli_inspect.py`,
  `tests/test_scaffold.py`, `tests/test_skill_bundle.py`.

## 2. Decisions locked during brainstorming (2026-05-05)

| Question | Decision |
|---|---|
| Done bar | **Beta for sales team** — deployable to Jonathan and Jovany; SOP teaches setup; state detection thorough enough to give next-action prompts at every state |
| AE prep scope | **Phase-2 + AE-assisted prep validation** — skill detects readiness gaps and helps fix them conversationally; does not duplicate Plan 5/6 automation |
| Project storage | **Each AE clones the git repo** (option A); SOP teaches the git workflow |
| Git interface | **Claude Desktop is the git interface** — AEs never run git directly; the skill wraps `git pull`/`commit`/`push` in conversational language |
| Skill activation | **Natural-language invocation by project name** — "build proposal for Long Beach Airport"; skill resolves project under `Projects/` by name and asks if ambiguous |
| State detection scope | **Readiness check + next-action prompts** — skill turns gaps into actionable suggestions, not just a linter |
| Architecture | **`inspect` CLI subcommand outputs JSON; skill.md orchestrates and presents conversationally** |
| Project scaffolding | **In scope** — when no folder exists, skill offers to scaffold from `_template_project/` |
| Brief drafting | **Chat-driven authoring in scope** — skill walks AE through missing fields one at a time, writes answers back to Brief.md via Edit; does NOT draft from RFP (deferred to Plan 6) |

## 3. Architecture

Runtime flow when an AE invokes the skill:

```
AE in Claude Desktop: "build proposal for Long Beach Airport"
    ↓
Claude Desktop loads skill.md based on description match
    ↓
skill.md body instructs Claude to:
  1. Resolve project folder under Projects/ by name (ask if ambiguous;
     offer scaffold if none)
  2. If scaffolding: run `python -m proposal_build scaffold "<name>"`
  3. Run `python -m proposal_build inspect "Projects/<name>"`
     → JSON readiness report
  4. Parse JSON, summarize findings to AE conversationally
  5. If gaps: walk AE through fixes interactively
     - Missing Brief frontmatter field → ask AE; write answer to
       Brief.md via Edit
     - Missing required Brief prose section (Scope Includes, Creative
       Direction, Customer Goals, etc.) → ask AE for content; write
       back as a markdown section
     - Missing zone hero_image → list candidate renderings; AE picks;
       write back
     - Missing Worksheet tier columns → tell AE this is manual (Excel
       step), wait
  6. Re-run inspect after each fix batch until ready_to_generate=true
  7. Run `python -m proposal_build generate "Projects/<name>"
     --use-latest-layouts --compress`
  8. Surface output PDF paths
  9. Offer git commit + push
    ↓
proposal_build CLI (existing Plan 3 generation + new inspect/scaffold)
    ↓
PDFs land in Projects/<name>/03 - Scope & Pricing/
```

**Key design choice — JSON, not text, between Python and Claude.** The
inspector outputs structured JSON because skill.md asks Claude to *turn
that JSON into a friendly conversation*. JSON gives Claude a clean
parseable input. Pretty text would force Claude to re-format what's
already formatted.

## 4. Components

### 4.1 `skill_assets/skill.md` — skill manifest

YAML frontmatter (required by Claude Desktop's skill format):

```yaml
---
name: proposal-builder
description: Generate St. Nick's customer proposals (proposal deck + per-tier itemized pricing PDFs) from a project's Brief, Worksheet, and renderings. Use when the user asks to "build a proposal for X", "generate a proposal", "create the X holiday proposal", or similar.
allowed-tools: Bash, Read, Write, Edit
---
```

Body: ~150–300 lines of instructions to Claude covering each numbered
step in §3. Body sections:

- `## Step 1 — Resolve the project` — find folder under `Projects/`,
  fuzzy-match, ask AE if ambiguous, offer scaffold if missing.
- `## Step 2 — Scaffold (if needed)` — run `scaffold` subcommand.
- `## Step 3 — Inspect` — run `inspect`, parse JSON, summarize findings.
- `## Step 4 — Resolve blockers conversationally` — for each Finding,
  the matching prompt pattern (Brief field → ask AE → Edit; Brief
  prose section → ask AE → Edit; hero_image → list candidates → ask
  → Edit; manual step → tell AE and wait).
- `## Step 5 — Generate` — run `generate --use-latest-layouts
  --compress`.
- `## Step 6 — Surface output + git` — show PDF paths, offer commit/
  push.
- `## Common errors and friendly translations` — translation table for
  YAML parse / font / image-not-found / formula-cache errors.
- `## Beta safety rail` — instruction to Claude: stop auto-iteration
  after 2 failed attempts on the same fix; surface the situation to the
  AE with full output.

### 4.2 `skill_assets/AE_SOP.md` — human-facing SOP

Single Markdown file with three top-level sections:

- **Setup (one-time):** install Claude Desktop, configure shell access,
  install the skill bundle into Claude Desktop's skills folder, clone
  the repo, run a smoke test on Riverside.
- **Daily workflow:** start a new project (skill scaffolds), fill Brief
  via chat, drop renderings into `02 - Renderings/Base Scope/`, fill
  Worksheet manually in Excel, run the skill, review output, commit/push.
- **Reference:** what each Brief frontmatter field means, common error
  messages and fixes, FAQ ("why do I have to fill the Worksheet
  manually?"), who to ping for help.

Tone: warm, concrete, uses screenshots where they help. Audience is
sales-team AEs, not developers.

### 4.3 `skill_assets/proposal_build/inspector/` — readiness package

```
inspector/
  __init__.py        # exports inspect_project(project_path) -> InspectionReport
  report.py          # @dataclass InspectionReport, Finding
  folder.py          # detects missing project folder, missing subdirs
  brief.py           # missing required frontmatter, empty required sections,
                     #   em-dash regressions (W8 wrap), missing hero_image per zone
  worksheet.py       # missing .xlsx, no tier columns, blank customer-facing copy
  renderings.py      # empty renderings dir, files unsorted in _inbox/, broken
                     #   hero_image references
```

Each module exposes `def check(project_path: Path) -> list[Finding]`.
`inspect_project` calls all four and aggregates.

`Finding` schema:
```python
@dataclass(frozen=True)
class Finding:
    severity: Literal["blocker", "warning", "info", "error"]
    category: Literal["folder", "brief", "worksheet", "renderings"]
    issue: str           # short kebab-case identifier ("missing-field",
                         # "no-hero-image", "files-in-inbox", etc.)
    detail: str          # human-readable specifics
    fix: str | None      # next action ("Reply with the client company name.")
    field: str | None    # Brief field name when applicable
    zone: str | None     # zone name when applicable
```

`InspectionReport` schema:
```python
@dataclass(frozen=True)
class InspectionReport:
    project_path: Path
    ready_to_generate: bool        # True iff no blockers + no errors
    findings: tuple[Finding, ...]
    summary: str                   # one-line headline ("Ready to generate" /
                                   # "8 blockers, 4 warnings")
```

The W1-W8 validators from `parser/validate.py` are *wrapped*, not duplicated.
Each W-rule that fires becomes a Finding with the matching category +
severity.

### 4.4 `cli.py inspect` subcommand

```bash
python -m proposal_build inspect "Projects/<name>" [--format=json|human]
```

- Default `--format=json` for skill use.
- `--format=human` for debug / SOP examples.
- Exit codes: `0` = ready, `1` = has blockers (normal "AE has work to
  do"), `2` = inspector failed (Python error, IO error).

### 4.5 `cli.py scaffold` subcommand

```bash
python -m proposal_build scaffold "<project-name>" [--from=_template_project]
```

- Copies `Projects/_template_project/` to `Projects/<project-name>/`.
- Refuses to overwrite an existing folder (exits 1 with clear error).
- Default `--from=_template_project`; `--from` lets future plans point
  at a different starter.

### 4.6 Inspector resilience

Design rule: `inspect_project()` never crashes on an in-progress
project. Each `check()` is wrapped in try/except; exceptions become
`Finding(severity="error", ...)`. Examples: Worksheet open in Excel
(file lock), corrupt Brief YAML, missing template file.

## 5. Data flow walkthrough

A concrete trace of Jonathan starting the Long Beach Airport project
from scratch.

| Turn | Actor | Action |
|---|---|---|
| 1 | Jonathan | "build proposal for Long Beach Airport" |
| 2 | Claude | Loads skill.md (description match). Lists `Projects/`. No "Long Beach Airport" folder. Asks: "Want me to scaffold from `_template_project/`?" |
| 3 | Jonathan | "yes" |
| 4 | Claude | Runs `python -m proposal_build scaffold "Long Beach Airport"`. Confirms folder created. |
| 5 | Claude | Runs `python -m proposal_build inspect "Projects/Long Beach Airport"`. Gets JSON: ~25 missing Brief fields, no zones defined, no renderings, blank Worksheet. Summarizes in plain English: "Brief is empty, no renderings yet, Worksheet not filled. Let's start with the Brief — what's the client company?" |
| 6..N | Jonathan + Claude | Brief walk-through, one field at a time. Claude uses Edit to write each value into `04 - Process & Notes/Project Brief.md`. |
| N+1 | Claude | Re-inspects. Brief blockers gone. Tells Jonathan: drop renderings into `02 - Renderings/Base Scope/`, fill the Worksheet in Excel, ping when ready. |
| N+2 | Jonathan | Drops 18 renderings, fills Worksheet, replies "ready". |
| N+3 | Claude | Re-inspects. Renderings present, Worksheet filled, but zones missing `hero_image`. For each zone, lists candidate filenames (matched by keywords), asks Jonathan to pick. Writes `hero_image:` values back to Brief. |
| N+4 | Claude | Re-inspects. `ready_to_generate: true`. Runs `python -m proposal_build generate "Projects/Long Beach Airport" --use-latest-layouts --compress`. Surfaces output paths. |
| N+5 | Claude | Offers git commit + push. Jonathan: yes. Claude runs `git add ... && git commit -m "..." && git push`. |

**Short-flow variant — regenerate after edit:**

| Turn | Actor | Action |
|---|---|---|
| 1 | AE | "regenerate Long Beach Airport with latest copy" |
| 2 | Claude | `git pull`, runs inspect (clean), runs generate, pushes new PDFs. |

## 6. Error handling

Errors come from four layers; each is handled differently.

### 6.1 AE-input errors (ambiguous or unknown project name)

- Multiple matches → list candidates, ask AE which one.
- Zero matches → list closest names by string similarity, ask "did you
  mean…", offer scaffold of a new folder under the original spelling.

### 6.2 Inspector internal errors

`inspect_project()` catches every exception and emits
`Finding(severity="error", category=..., issue="check-failed",
detail=str(exc))`. The CLI exits 2 (vs 0 ready / 1 blockers). Skill
body tells Claude: on exit-2, surface stderr summary and ask AE if they
want full output.

### 6.3 Generator errors

The skill body has a translation table for common patterns:

| Generator error | Friendly translation | Auto-fix? |
|---|---|---|
| YAML parse error | "Syntax issue in the Brief on line N." | Claude reads, fixes if obvious, re-runs |
| WeasyPrint font missing | "Renderer can't find a font — setup issue." | No; refer to SOP setup-troubleshooting |
| Image not found (W1) | "Brief references `Foo.png` but it's not in the renderings folder." | Asks AE: update reference or add file? |
| Worksheet formula cache stale | "Tier totals look stale; let me re-cache." | Runs migrate script |
| Unknown / unrecognized | Stops auto-flow; surfaces output; asks AE to ping Daniel. | No |

### 6.4 Git errors

- **Remote has changes:** "Remote has commits I don't have. Want me to
  pull first?"
- **Uncommitted local changes:** "You have uncommitted edits — should I
  stash, commit, or discard?"
- **Permission denied / no push access:** "Git rejected the push. Could
  be auth — check Claude Desktop's GitHub credentials, or send me the
  error and I'll dig in."

### 6.5 Beta safety rail

After 2 failed attempts at the same fix, the skill stops auto-iterating
and surfaces the situation to the AE: "I've tried twice and the same
error came back. Here's what I see — send this to Daniel if you'd like
a hand." Prevents infinite loops or compounding mistakes.

## 7. Testing

### 7.1 Inspector unit tests — `tests/test_inspector.py`

One test class per module (`folder`, `brief`, `worksheet`,
`renderings`). Each detection rule has a positive test (issue present,
finding returned with correct severity/category/issue) and a negative
(issue absent, no finding). W1-W8 wrappers get a "wrapper passes
through validator output" test, no need to retest underlying validators.

### 7.2 CLI integration tests — `tests/test_cli_inspect.py`

- `inspect "Projects/_template_project"` → exit 1 (blockers expected),
  JSON valid, finding count > 20.
- `inspect "Projects/Downtown Riverside Metro Link"` → exit 0,
  `ready_to_generate: true`, only info-severity findings.
- `--format=human` returns non-JSON readable text.
- Inspector resilience: corrupt Brief YAML → exit 1 with
  `severity="error"` finding, not a crash.

### 7.3 Scaffold tests — `tests/test_scaffold.py`

- `scaffold_project(tmp_path / "Test Project")` creates the full
  template tree.
- Refuses to overwrite an existing folder (raises `FileExistsError`).
- Created folder is byte-identical to `_template_project/` minus
  `.gitkeep` markers.

### 7.4 Skill bundle smoke test — `tests/test_skill_bundle.py`

- `skill_assets/skill.md` exists, parses as valid frontmatter + body.
- Required frontmatter fields present: `name`, `description`.
  Description includes activation phrases ("build proposal", "generate
  proposal").
- `skill_assets/AE_SOP.md` exists, non-empty, has expected H2 sections
  (Setup, Daily workflow, Reference).

### 7.5 Existing suite stays green

The current 124 tests must keep passing. Plan 8 adds tests, doesn't
break them.

### 7.6 Manual end-to-end test (not automated)

Done first by Daniel, then by Jonathan/Jovany. Plan-8 implementation
plan will include an "AE smoke test" checklist:

1. Install skill in Claude Desktop.
2. Run on Riverside (existing project, regen-only flow). Expect: no
   walk-through, just inspect → generate → commit prompt.
3. Scaffold a throwaway test project. Expect: folder created, Brief
   walk-through, manual prompts for renderings/Worksheet, hero_image
   walk-through, generation, commit prompt.
4. Note any friction. Refine SOP from the session before handing the
   skill to Jonathan/Jovany.

### 7.7 Coverage target

Every Finding type emitted by the inspector has an explicit unit test.
Every CLI exit code path tested. Skill bundle structure tested.
End-to-end path tested via the existing Riverside generation flow + an
explicit `inspect → generate` test on the Riverside fixture.

## 8. Out of scope (deferred to future plans)

- **RFP intake / Brief auto-draft from RFP** → Plan 6.
- **Renderings auto-sort from `_inbox/`** → Plan 5.
- **Worksheet auto-fill from RFP** → Plan 6.
- **Diff-mode regeneration** (regenerate only what changed) → Plan 4.
- **Canva CSV output** → Plan 7 (blocked on Abigail's master Canva
  field names).

These all surface in `inspect` as warnings or info-level findings (e.g.,
"14 files in `_inbox/` — please sort manually; Plan 5 will automate
this") so the AE knows what's still manual.

## 9. Acceptance criteria

Plan 8 is "done" when:

1. `python -m proposal_build inspect "Projects/Downtown Riverside Metro
   Link"` exits 0 with `ready_to_generate: true` and only info-severity
   findings.
2. `python -m proposal_build inspect "Projects/_template_project"`
   exits 1 with > 20 findings naming missing Brief fields and zones.
3. `python -m proposal_build scaffold "Test Project"` creates a folder
   matching `_template_project/` exactly.
4. `skill_assets/skill.md` and `skill_assets/AE_SOP.md` exist with the
   expected structure (validated by `tests/test_skill_bundle.py`).
5. Existing 124 tests pass; every Finding-issue type emitted by the
   inspector has at least one explicit unit test covering it.
6. Daniel completes the manual smoke test on Riverside (regen-only
   flow) without manual CLI invocation.
7. Daniel completes the manual smoke test on a scaffolded throwaway
   project (full new-project flow) and any friction points are
   captured in the SOP.

## 10. Open questions / decisions deferred to writing-plans

These are smaller calls that don't need design-level resolution but
will come up during implementation:

- Exact `Finding.issue` kebab-case names (canonical taxonomy — derive
  during implementation; revise tests if needed).
- `inspector/brief.py` field-presence rules vs the Brief schema source
  of truth (probably reuse `parser/__init__.py` field requirements;
  decide during implementation).
- Whether `scaffold` subcommand should also run `inspect` immediately
  after creating the folder, or leave that to the skill body (probably
  leave to skill body for separation of concerns).
- SOP's screenshot strategy (PNG embeds vs ASCII-art mocks) — decide
  during writing.

## 11. Spec self-review notes

- No "TBD" placeholders.
- §2 decisions consistent with §3 architecture.
- Scope tight enough for one implementation plan (~6-8 steps in
  writing-plans).
- Acceptance criteria measurable.
- §10 deferred items are appropriately small for plan-level decisions.
