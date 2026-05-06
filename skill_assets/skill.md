---
name: proposal-builder
description: Generate St. Nick's customer proposals (proposal deck + per-tier itemized pricing PDFs) from a project's Brief, Worksheet, and renderings. Use when the user asks to "build a proposal for X", "generate a proposal", "create the X holiday proposal", "make pricing PDFs for X", or any phrase referring to building a proposal for a project under Projects/.
allowed-tools: Bash, Read, Write, Edit
---

# Proposal Builder

When the user asks you to build, generate, or create a proposal for a St.
Nick's project, follow this flow exactly. The user is a sales-team AE
(usually Daniel, Jonathan, or Jovany), not a developer — keep your
language conversational, never show raw stack traces or JSON, and never
make destructive changes without confirmation.

## Step 1 — Resolve the project

Look under `Projects/` (relative to the repo root) for a folder whose
name matches the project the user named (case-insensitive substring
match is fine). If exactly one matches, proceed. If multiple match, ask
the user which one. If none match, say so and offer to scaffold a new
folder via Step 2.

## Step 2 — Scaffold (if no folder exists)

Ask the user: *"I don't see a folder for `<name>`. Want me to scaffold
one from the template?"* If yes:

```bash
python -m proposal_build scaffold "<name>"
```

Then proceed to Step 3.

## Step 3 — Inspect

Run:

```bash
python -m proposal_build inspect "Projects/<name>"
```

Parse the JSON `stdout`. The report has `ready_to_generate: bool`, a
`summary` string, and a `findings` array. Each finding has
`severity` (`blocker`, `warning`, `info`, `error`), `category`, `issue`,
`detail`, optional `fix`, optional `field`, optional `zone`.

If `ready_to_generate` is `true` and no findings have severity `error`,
skip to Step 5.

## Step 4 — Resolve blockers conversationally

Group findings by category. Walk the user through one category at a
time, never dumping all findings at once. For each finding:

- **`brief / missing-field`** — ask the user the field's value (e.g.,
  *"What's the client company?"*). Use the `Edit` tool to write the
  answer into `Projects/<name>/04 - Process & Notes/Project Brief.md`
  under the matching frontmatter key.
- **`brief / missing-section`** — ask the user for the prose content
  (e.g., *"What's the Creative Direction paragraph for this project?"*).
  Use `Edit` to add a `## <section>` heading + body.
- **`brief / no-zones-defined`** — ask the user how many zones and
  their names; build the `zones:` list in frontmatter.
- **`brief / no-hero-image`** (warning) — list candidate renderings
  under `Projects/<name>/02 - Renderings/Base Scope/` whose filenames
  hint at the zone (substring match). Ask the user to pick. Write the
  `hero_image:` value to the zone via `Edit`.
- **`worksheet / missing-customer-facing-column`** /
  **`missing-tiers-column`** / **`blank-customer-facing`** /
  **`no-tiers-on-line`** — these are manual Excel steps. Tell the user
  which lines need fixing and wait for them to reply when done. Do
  NOT try to edit `.xlsx` via shell.
- **`worksheet / worksheet-locked`** — tell the user the file appears
  open in Excel; ask them to close it and reply when ready.
- **`renderings / no-renderings-present`** /
  **`files-in-inbox`** — tell the user the manual action (drop into
  `Base Scope/` etc., or move from `_inbox/` to subfolders). Wait for
  reply.
- **`renderings / hero-image-unresolved`** — the Brief references a
  filename that doesn't exist. Ask: *"Should I update the reference,
  or are you adding the file?"*
- **`validator / W*`** — wrapped W1-W8 validators from the parser.
  Translate the message into plain English using the table below.

After fixing a batch of findings, re-run `inspect` and continue from
Step 3 with the new report. Do not loop more than 5 times — if the
same finding persists after 2 attempted fixes, hit the safety rail
(see "Beta safety rail" below).

## Step 5 — Generate

Run:

```bash
python -m proposal_build generate "Projects/<name>" --use-latest-layouts --compress
```

If the command exits 0, surface the output PDFs to the user with
their full paths. If non-zero, parse stderr against the
"Common errors and friendly translations" table below.

## Step 6 — Surface output and offer git

Tell the user the PDF paths under
`Projects/<name>/03 - Scope & Pricing/`. Then ask:
*"Want me to commit and push the project folder to the team repo?"*

If yes, run:

```bash
git -C <repo-root> add "Projects/<name>"
git -C <repo-root> commit -m "<name>: <short summary of changes>"
git -C <repo-root> push
```

If `git push` is rejected, see the git error translations.

## Common errors and friendly translations

| Error pattern in stderr | Friendly translation | Auto-fix? |
|---|---|---|
| `yaml.scanner.ScannerError`, `yaml.parser.ParserError` | "There's a syntax issue in the Brief — let me look." | Read the Brief, find the line, fix the YAML, re-run. |
| `cannot load library 'libgobject` | "The proposal renderer can't find a font/library — usually a setup issue. Check the SOP setup-troubleshooting section." | No. |
| `referenced rendering not found` (W1) | "Brief references `<file>` but it's not in the renderings folder." | Ask: update reference or add file? |
| `formula cache is stale` / `tier totals don't match` | "The Worksheet's tier totals look stale — let me re-cache." | Run `python skill_assets/proposal_build/scripts/migrate_riverside_worksheet.py "Projects/<name>"` (or generic equivalent) and re-run generate. |
| Anything else / unrecognized | Don't auto-fix. Surface a brief summary, ask the user to send the output to Daniel. | No. |

## Git error translations

- `! [rejected]` (remote has changes) → *"Remote has commits I don't have. Want me to pull first?"*
- `Changes not staged` (uncommitted local edits during pull) → *"You have uncommitted edits — should I stash, commit, or discard?"*
- `Permission denied`, `403`, auth errors → *"Git rejected the push — could be auth. Check Claude Desktop's GitHub credentials. If that doesn't help, send me the error."*

## Beta safety rail

After 2 failed attempts at the same fix (same `issue` reappears in
`inspect` output), STOP auto-iterating. Tell the user:

*"I've tried twice and the same error came back. Here's what I see —
send this to Daniel if you'd like a hand."*

…and surface the relevant `inspect` JSON or the generator stderr.
Don't make further attempts in this session unless the user explicitly
asks again.

## What this skill does NOT do (yet)

- Draft the Brief from an RFP. (Plan 6 / Phase 0.)
- Auto-sort renderings from `_inbox/`. (Plan 5 / Phase 1.)
- Auto-fill the Worksheet. (Plan 6 / Phase 0.)
- Diff-mode regeneration (regenerate only what changed). (Plan 4.)

When you encounter an `inspect` finding that says "this is manual; Plan
N will automate", just tell the user it's manual right now.
