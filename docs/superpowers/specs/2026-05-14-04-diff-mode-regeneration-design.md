# Diff-Mode Regeneration — `last_run.json` + `dependency_map.yaml`

**Date:** 2026-05-14
**Status:** Approved, ready for plan
**Author:** Daniel + Claude (brainstorming session)
**Slot:** Plan 4 (original master spec §7)

---

## 1. Goal

After the first successful generation of a proposal, every subsequent
`python -m proposal_build generate` run produces two artifacts the AE
needs but doesn't have today:

1. **A change report** that tells Daniel exactly which Brief fields,
   Worksheet cells, and renderings changed since the previous run, and
   which slides those changes affect.
2. **An auto-drafted `change_summary.md`** suitable for pasting into a
   revision email to the customer.

Plus a safety net:

3. **Revision history snapshots** in `04 - Process & Notes/revisions/v<n>/`
   so prior versions of the deck, itemized pricing, and workbook are
   always recoverable.

The whole feature is an informational + archival layer around the
existing renderer. The renderer itself is not modified.

---

## 2. Driver pains (from brainstorming)

Daniel identified two real pains, and we explicitly de-prioritized
others that the original master spec coupled with this work:

- ✅ **Drift confidence:** after tweaking Brief field X, Daniel wants
  certainty about which slides are byte-equivalent vs. modified — so
  no cosmetic drift sneaks into a revision the customer sees.
- ✅ **Change summary:** when sending revision N to the customer,
  Daniel wants a clean one-paragraph "here's what's different" he can
  paste into Outlook.
- ❌ **Speed:** full regen runs in ~30-45 sec for a 13-slide deck.
  Acceptable. No slice-rendering in V1.
- ❌ **Layout version locking:** speculative without revision rounds
  actually hitting yet. Snapshot doesn't even track layout hashes in
  V1 — if needed later, clean Plan 4.x addition.
- ❌ **Approval state per slide:** speculative.
- ❌ **Dry-run preview:** `--diff-only` flag covers the use case
  without a separate "preview" mode.

---

## 3. Scope

**In scope**

- New file `skill_assets/dependency_map.yaml` — slide-by-slide
  declaration of which Brief paths, Worksheet patterns, and rendering
  globs each layout consumes. One entry per layout + entries for the
  itemized pricing PDF and customer workbook.
- New per-project file `04 - Process & Notes/last_run.json` — hashes
  of all inputs + outputs, slide list rendered, revision counter,
  timestamp. Created on first run; updated on each subsequent run.
- New per-project folder `04 - Process & Notes/revisions/v<n>/` —
  archived copies of deck PDF, itemized PDF, workbook xlsx,
  `last_run.json`, `change_summary.md` at each revision.
- Change-report terminal output during regen.
- New per-project file `05 - Output/change_summary.md` — customer-email-
  ready summary, regenerated each run.
- Two new CLI flags: `--no-snapshot`, `--diff-only`.
- Inspector / generator integration: the differ runs after composer,
  before render; snapshotter runs after a successful render.
- `human_label:` field per Brief path in `dependency_map.yaml` so
  change reports use plain-English labels, not JSON paths.
- `04 - Process & Notes/revisions/` added to root `.gitignore`.

**Out of scope (V1, deferred to later plans if pain materializes)**

- Slice rendering — regen always rebuilds the full deck.
- Layout version locking, layout hash tracking, `--use-latest-layouts`
  flag. The differ does not compare layout file contents.
- Approval state per slide / per-revision sign-off.
- Auto-generation of email Subject / recipient — only the body is
  produced.
- PDF page extraction or PDF caching libraries (pypdf, etc.).
- Retroactive snapshotting of Riverside / Sheraton / FIGat7th's
  already-shipped outputs — they get a fresh `v1/` on next regen.

---

## 4. Architecture

### 4.1 Components

```
inputs            differ                outputs
                                       ┌─────────────────────┐
Brief.md      ───>                ────>│ 05 - Output/        │
Worksheet.xlsx├──> hash_inputs() ─┬──> │   deck.pdf          │
renderings/   ┘                   │    │   itemized.pdf      │
                                  │    │   workbook.xlsx     │
last_run.json─> read_snapshot()──>┴──> │   change_summary.md │
dependency_   ┘                        │                     │
  map.yaml      diff_against_snapshot()│ 04 - Process &      │
                  ▼                    │   Notes/            │
              change_report (text)     │   last_run.json     │
              affected_slides (set)    │   revisions/v<n>/   │
                  │                    └─────────────────────┘
                  ▼
              render_proposal_pdf()  ←─ unchanged
                  │
                  ▼
              snapshot_outputs()
              copy_to_revisions()
              write_change_summary()
```

The differ is a pre-render step. Affected-slide set is informational —
the renderer still renders all slides. (Slice rendering deferred.)

### 4.2 Data files

**`skill_assets/dependency_map.yaml`** (skill-bundled, project-agnostic):

```yaml
schema_version: 1

# Per-slide layout entries. Each lists the inputs the layout consumes.
slides:
  cover:
    brief:
      - path: client_name
        human_label: "Client name"
      - path: project_name
        human_label: "Project name"
      - path: cover_image
        human_label: "Cover image"
    worksheet: []
    renderings:
      - glob: "Base Scope/01_*"

  tree_comparison:
    brief:
      - path: tree_comparison.trees
        human_label: "Tree comparison — sizes shown"
      - path: tree_comparison.recommended
        human_label: "Tree comparison — recommended size"
    worksheet: []
    follow:
      - resolve_from: tree_comparison.trees
        to_assets:
          - "tree_library/{id}.md"
          - "tree_library/{id}.jpg"

  rom_investment:
    brief:
      - path: sections
        human_label: "Section / scope structure"
    worksheet:
      - pattern: "row.*.rental_low"
        human_label: "Annual rental low"
      - pattern: "row.*.rental_high"
        human_label: "Annual rental high"
      - pattern: "row.*.purchase_ot_low"
        human_label: "One-time purchase low"
      # ... etc for each ROM column

  # ... one entry per layout

# Standalone (non-deck) outputs:
itemized_pricing_pdf:
  brief:
    - path: client_name
      human_label: "Client name"
    - path: sections
      human_label: "Section / scope structure"
  worksheet:
    - pattern: "row.*"
      human_label: "Pricing line items"

customer_workbook_xlsx:
  brief:
    - path: client_name
      human_label: "Client name"
  worksheet:
    - pattern: "row.*"
      human_label: "Worksheet line items"
```

**`04 - Process & Notes/last_run.json`** (per-project, written after
each successful run):

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-14T18:42:00Z",
  "revision": 2,
  "brief": {
    "design_phrase": "sha256:abc...",
    "creative_phases.0.body": "sha256:def...",
    "tree_comparison.recommended": "sha256:..."
  },
  "worksheet": {
    "row.20.rental_high": "sha256:...",
    "row.30.customer_facing_description": "sha256:..."
  },
  "renderings": {
    "Base Scope/20_overhead-mixed-canopy.png": "sha256:..."
  },
  "slides_rendered": [
    {"layout": "cover", "page": 1},
    {"layout": "tree_comparison", "page": 12}
  ],
  "outputs": {
    "deck_pdf": "sha256:...",
    "itemized_pdf": "sha256:...",
    "workbook_xlsx": "sha256:..."
  }
}
```

Notes:
- All hashes are sha256, encoded as hex with a `sha256:` prefix for
  forward compatibility if the algorithm is ever upgraded.
- Brief is flattened to JSON-path strings (`creative_phases.0.body`).
  Diffing happens at field level. Item codes containing hyphens
  (`10-enh`) stay as-is — the path is `row.10-enh.rental_high`.
- Worksheet is hashed per-cell, keyed by `row.<item_code>.<column_name>`.
- Renderings hashed by file content, keyed by path relative to
  `02 - Renderings/`.
- `slides_rendered` records what was actually composed for this run
  (so tree-less projects don't get phantom tree-comparison entries).
- Layout hashes are **not** stored in V1 (see §3 out-of-scope).
- Each output is hashed for tamper detection.

### 4.3 Dependency resolution

For each entry in `dependency_map.yaml`, the dep-map resolver expands
patterns and `follow:` chains against the current Brief and Worksheet
to produce a flat dependency set per slide.

- **Static brief paths** (`tree_comparison.recommended`) map 1:1.
- **Glob worksheet patterns** (`row.*.rental_high`) expand against
  the current Worksheet's row inventory.
- **Rendering globs** (`Base Scope/01_*`) expand against the project's
  `02 - Renderings/` tree.
- **`follow:` chains** read the resolved Brief value and substitute
  `{id}` placeholders. Example: `tree_comparison.trees: [tree_30,
  tree_50]` produces `tree_library/tree_30.md`,
  `tree_library/tree_30.jpg`, `tree_library/tree_50.md`,
  `tree_library/tree_50.jpg`.

Resolved sets are computed per-run (no caching). This keeps the
resolver stateless and handles changes in `tree_comparison.trees`
between revisions cleanly.

---

## 5. CLI behavior

### 5.1 First run (no `last_run.json`)

```
$ python -m proposal_build generate
[inspector] 0 blockers, 0 warnings
[composer]  13 slides composed
[renderer]  deck.pdf (1.8 MB) -> 05 - Output/
            itemized.pdf, workbook.xlsx -> 03 - Scope & Pricing/
[snapshot]  first run -- wrote last_run.json (revision 1)
[snapshot]  copied outputs to 04 - Process & Notes/revisions/v1/
[summary]   wrote change_summary.md (initial revision)
```

No diff to compute. `change_summary.md` for v1 has the text "Initial
revision — no prior version to compare against."

### 5.2 Subsequent run

```
$ python -m proposal_build generate
[inspector] 0 blockers, 0 warnings
[diff] CHANGES SINCE LAST RUN (rev 1, 2026-05-13):
       Brief:
         - Creative direction: "Modern Magic" -> "Modern Magic - Holiday"
         - Tree comparison - recommended size: tree_50 -> tree_40
       Worksheet:
         - Letter Arch (row 30) annual rental high: $24,500 -> $26,000
       Renderings: no changes

       Affected slides (4 of 13): cover, tree_comparison,
                                  rom_investment p1, rom_investment p2
       Itemized pricing PDF: affected
       Workbook: affected

[composer]  13 slides composed
[renderer]  deck.pdf (1.8 MB) -> 05 - Output/
[snapshot]  wrote last_run.json (revision 2)
[snapshot]  copied outputs to 04 - Process & Notes/revisions/v2/
[summary]   wrote change_summary.md (paste into customer email)
```

Full deck still renders. Affected-slide list is informational.

### 5.3 Flags

- `--no-snapshot` — skip `last_run.json` write and skip
  `revisions/v<n>/` copy. Skip `change_summary.md` write. Use for
  test-driven renders that shouldn't pollute project state.
- `--diff-only` — run inspector + composer + differ + write
  `change_summary.md` + print report. **Skip render and snapshot.**
  Use when AE wants to know what would change without rebuilding.
  Requires `last_run.json` to exist; otherwise prints "no prior run to
  diff against" and exits cleanly without writing anything (see §8).

Both flags off by default.

---

## 6. `change_summary.md` format

Written to `05 - Output/change_summary.md`. Overwritten each run.

```markdown
# FIGat7th DTLA - Revision 2 Change Summary

**Generated:** 2026-05-14
**Previous revision:** v1 (2026-05-13)

> Copy the section below into your customer email body.

---

## Changes since revision 1

- **Creative direction:** Refined design phrase to "Modern Magic - Holiday."
- **Tree size:** Recommended tree changed from 50 ft to 40 ft.
- **Pricing:** Letter Arch (item 30) annual rental high adjusted from
  $24,500 to $26,000.

## What's the same

Cover, palette board, canopy, tree feature, plaza arches, plaza moments,
sign-off - all unchanged from revision 1.

---

*Internal: affected slides this round: cover, tree_comparison,
rom_investment p1, rom_investment p2. Itemized PDF and workbook
regenerated.*
```

Notes:
- Bullets are auto-generated from `human_label:` mappings + before/after
  values. Brief-path changes and Worksheet-cell changes both produce
  bullets.
- If a changed Brief path has no `human_label:` defined in
  `dependency_map.yaml`, the bullet falls back to the bare JSON path
  (`tree_comparison.recommended: tree_50 -> tree_40`) and the terminal
  logs a warning so the dep-map can be filled in next pass.
- Rendering-only changes get a generic line ("Updated rendering: ...").
- Layout changes are not surfaced (V1 doesn't track them).
- "What's the same" is auto-derived from slide list minus affected
  slides — names taken from a friendly-label table or `section.name`
  values in the Brief.
- The "Internal:" footer is for Daniel's reference and is below a
  separator so he can trim it before pasting.
- Tone: matches Daniel's customer-facing voice (no em dashes; festive
  but not corporate per memory feedback).

---

## 7. Revision history snapshots

After each successful render:

```
04 - Process & Notes/revisions/
+- v1/
   +- deck.pdf
   +- itemized.pdf
   +- workbook.xlsx
   +- last_run.json     (snapshot at time of v1)
   +- change_summary.md (for v1: "Initial revision")
+- v2/
   +- deck.pdf
   +- itemized.pdf
   +- workbook.xlsx
   +- last_run.json
   +- change_summary.md
```

- `<n>` matches the `revision` counter in `last_run.json`.
- Top-level `04 - Process & Notes/last_run.json` always reflects the
  latest run. The copies inside `v<n>/` are immutable historical
  records.
- The folder is **gitignored at repo root** (pattern:
  `04 - Process & Notes/revisions/`) so revision binaries don't
  pollute git diffs.

**No-changes case:** if a regen runs but no inputs changed, outputs
get rebuilt (because user explicitly asked) but the revision counter
does not increment, no new `v<n>/` is created, and `change_summary.md`
is overwritten with a one-line note ("nothing changed since rev N").
Snapshot's `generated_at` updates; everything else stays.

---

## 8. Edge cases

| Case | Behavior |
|---|---|
| First run, no `last_run.json` | Skip diff, write snapshot, copy outputs to `revisions/v1/`. Terminal reports "first run." `change_summary.md` says "initial revision." |
| `last_run.json` exists but `revisions/` missing | Start fresh at `v<recorded+1>` with a warning. Hashes can't reconstruct prior binary outputs. |
| Schema version mismatch on `last_run.json` | Refuse the run, print upgrade instructions, exit non-zero. Future Plan 4.x ships a migrator. Never auto-rewrite. |
| Malformed / corrupt `last_run.json` | Back up to `last_run.json.broken-<timestamp>`, warn, treat as first run. |
| `revisions/v<n>/` already exists for the same revision number | Overwrite. (Re-running in the same session with the same inputs is idempotent.) |
| Brief field exists in project but has no `dependency_map.yaml` entry | Log warning, ignore for affected-slide derivation. Surfaces map staleness as new layouts ship. |
| `dependency_map.yaml` references Brief path that doesn't exist in this project | Silent skip. Layout that consumes it isn't rendered, so it doesn't matter. |
| Output file missing on disk (AE manually deleted) | Hash check flags mismatch; render recreates the file. |
| Worksheet row deleted between runs | Reported as "row 33 (Bauble Vertical Arch) removed." Any slide that listed row 33 is affected. |
| Rendering moved Base Scope <-> Unused between runs | Reported as "rendering 31_arch-bauble.png moved Base Scope -> Unused." Same effect as a delete from Base Scope. |
| Brief.voice flipped between runs | `voice` is in slide brief deps; falls out as a normal Brief change. No special handling. |
| `--diff-only` and no `last_run.json` exists | Print "no prior run to diff against," exit cleanly without writing anything. |

---

## 9. Testing approach

Target: ~25-30 new tests, bringing 251 -> ~280. No flaky integration
runs — fixture project is a tiny synthetic one, not Riverside / Sheraton
/ FIGat7th.

1. **`tests/test_diff_hasher.py`** — same Brief object hashes to same
   value across invocations; field reorder doesn't change hash;
   nested-list mutation only affects that path's hash.
2. **`tests/test_diff_differ.py`** — hand-crafted before/after snapshots
   produce expected change-report dicts. Covers add, remove, modify
   for Brief paths, Worksheet cells, and rendering files.
3. **`tests/test_diff_dep_map.py`** — given a dep_map + Brief, resolver
   returns expected dependency paths. Covers static paths, globs, and
   `follow:` chains.
4. **`tests/test_diff_change_summary.py`** — change-report dict
   produces expected `change_summary.md` text. Covers human_label
   substitution, no-changes case, mixed-change case.
5. **`tests/test_diff_integration.py`** — small synthetic fixture
   project, run pipeline twice with a Brief tweak between runs.
   Assert: `last_run.json` matches expected hashes, `change_summary.md`
   contains expected lines, `revisions/v2/` exists with all 4 files.
6. **`tests/test_diff_cli.py`** — `--no-snapshot` doesn't write JSON;
   `--diff-only` writes summary but no outputs; both flags off does
   the full flow.
7. **`tests/test_diff_schema_version.py`** — load synthetic v0
   `last_run.json`, assert refuse + non-zero exit.
8. **Real-project smoke (not asserted, manual verification):** run
   `python -m proposal_build generate` against FIGat7th post-merge;
   verify `last_run.json` and `revisions/v1/` appear; verify nothing
   crashes.

---

## 10. Open questions

None. All design decisions locked in §2-§9 from brainstorming.

---

## 11. What this unblocks

- Confidence: Daniel can ship revision 2 to a customer knowing exactly
  which slides moved.
- Customer summary: paste-ready text drops a recurring 5-minute write-
  up task per revision.
- Recovery: every prior revision is two clicks away in Finder.
- Plan 5+ groundwork: `last_run.json` snapshot shape is also useful
  for the rendering-ingestion CLI (knowing which renderings were last
  "in scope") and for the Phase 0 RFP intake (cross-referencing
  changes against the source RFP).

---

## 12. Implementation order (rough)

(Detailed sequencing belongs in the implementation plan, not the spec.
This is just for sizing.)

1. `dependency_map.yaml` authoring + schema validation
2. Hasher (`diff/hasher.py`)
3. Differ (`diff/differ.py`)
4. Dep-map resolver (`diff/dep_map.py`)
5. Snapshot writer / reader (`diff/snapshot.py`)
6. Change-summary writer (`diff/summary.py`)
7. CLI integration in `proposal_build/__main__.py` (flags, plumbing)
8. Revision folder copier
9. Gitignore update
10. AE_SOP section documenting the new files + flags

Rough size: ~600-800 lines of new code, ~25-30 new tests.
