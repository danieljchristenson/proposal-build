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

## CRITICAL — read before doing anything

This skill is an **orchestrator**, not a designer. The `proposal_build`
Python module owns ALL visual output: colors, fonts, layouts, logo
placement, page chrome, pagination. Your job is to fill the Brief,
run the bash commands below, and surface results — nothing else.

**You MUST:**
- Run `python -m proposal_build inspect` (Step 3) before claiming the
  project is ready.
- Run `python -m proposal_build generate` (Step 5) to produce the deck
  and pricing PDFs. The renderer is the only sanctioned visual output.
- Show every bash command in a fenced block before executing it.

**You MUST NOT:**
- Design slides yourself, in any form. Not as HTML, not as CSS, not
  as Markdown, not as Python that calls a slide library.
- Call `python-pptx`, `pptx`, `reportlab`, `weasyprint`, `pillow`,
  or any other rendering library directly. The skill's renderer wraps
  WeasyPrint with the locked brand stylesheet — never bypass it.
- Produce `.pptx`, `.key`, `.pages`, or loose slide images. The
  deliverables are PDFs from `python -m proposal_build generate`.
  Nothing else.
- Improvise a palette, typography, or layout based on the customer's
  brand (e.g. navy/gold for a Sheraton property, dark green for civic
  agencies). The proposal is a **St. Nick's** deliverable. The
  renderer enforces St. Nick's brand on every page regardless of
  customer.

**If you cannot run the bash commands** (Bash tool denied, module not
importable, Pango/Cairo missing, repo not accessible, etc.), STOP.
Report the exact error to the user verbatim. Do NOT improvise a
substitute. Do NOT export slides as JPGs and assemble them. The user
will fix the environment and retry.

If you find yourself thinking *"this customer has a different aesthetic,
let me match theirs"* or *"the renderer is broken, I'll just build the
deck myself"* — stop. That's the renderer's decision, not yours, and
the answer is no. Surface the problem to the user.

## Brand reference (context only — never design from this)

The renderer applies these automatically. They're listed here so you
can answer the AE's questions about output, never as a spec to design
custom slides from:

- **Brand red** — `#B31315`. Used for headlines, eyebrows, accents,
  date callouts, the recommended-tier ribbon, footer crumb dividers.
- **Charcoal** — `#1C1C1C`. Body text on light pages; full-bleed dark
  page background.
- **Light** — `#ECEFF1`. Body text on dark pages.
- **Panel** — `#F2F2F2`. Card backgrounds.
- **Headings** — Roboto, weights 400/700/900.
- **Body** — Poppins, weights 300/400/600.
- **Logo** — `ST NICKS LOGO.png`, top-left of every standard page;
  large bottom-right on the about/Company Profile page; prominent on
  the cover. Intentionally absent on full-bleed feature slides
  (zone_feature, zone_solo_fullbleed).

The locked source-of-truth stylesheet is `skill_assets/layouts/brand.css`.
If a question requires more detail than the bullets above, read that
file — never invent a value.

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

If `ready_to_generate` is `true` and there are zero `warning`-severity
findings, skip to Step 5. If `ready_to_generate` is `true` but warnings
remain, walk the user through them in Step 4 first — warnings include
`brief / no-hero-image` (the AE must pick a hero image, never
auto-defaulted) and `renderings / no-renderings-present`. After the
warnings are addressed (or the user explicitly says "ship anyway"),
proceed to Step 5.

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
- **Any finding not listed above** (e.g., `brief / missing-brief`,
  `worksheet / missing-worksheet`, `worksheet / empty-worksheet`,
  `folder / missing-subdir`, or any `error`-severity finding like
  `*-crashed`) — read the `detail` and `fix` fields directly from
  the JSON and relay them to the user verbatim. If `fix` is null or
  not actionable by the AE, hit the beta safety rail.

### Menu Mode (creative-menu / ROM pricing)

When the project is a first-pass creative-menu proposal — multiple
sections, some with customer-choice alternates ("pick one"), some
with always-included items — the Brief uses `mode: menu` and a
different field set than the default tiered mode. Used for projects
like FIGat7th DTLA where the AE wants to present creative directions
to the client before committing to a final scope.

Menu-mode required Brief fields (replace the tiered ones):

- `mode: menu`
- `design_phrase`, `voice`
- `prebuilt_cover_image`, `creative_vision_hero`
- `sections` — ordered list of `{key, label, name, is_lead, item_codes}`

Forbidden in menu mode: `recommended_tier`, `pricing_format`, `zones`.

The Worksheet for menu mode uses the ROM (rough-order-of-magnitude)
shape — 15 columns covering Section, Item Name, Description,
Alternate Group, Rental Low/High, Purchase OT Low/High, Purchase Svc
Low/High, Customer-Facing Description, Materials, Notes, and
Rendering Reference. Rental is a single all-inclusive annual fee;
Purchase is a one-time price plus a separate annual service fee.

The pipeline auto-detects mode from the Brief and routes parsing,
compose, and inspection through the menu path. The generate command
is unchanged — `python -m proposal_build generate "Projects/<name>"`
works for both modes.

After fixing a batch of findings, re-run `inspect` and continue from
Step 3 with the new report. Do not loop more than 5 times — if the
same finding persists after 2 attempted fixes, hit the safety rail
(see "Beta safety rail" below).

## Step 4.5 — Ask which theme

Before generating, ask the user which visual theme to use, unless the
project's Brief already pins one in its `theme:` front-matter (in that case,
skip the question and respect the Brief):

> *"Which theme for this proposal — **Editorial** (dark, modern) or
> **Classic** (light)?"*

Pass the answer to generate via `--theme`. If the Brief pins a theme, omit
`--theme` and let it apply. (`--theme` overrides the Brief; the Brief overrides
the engine default.)

## Step 5 — Generate

Run this exact command (substituting the chosen theme). Do not substitute any
other approach (see the CRITICAL section above):

```bash
python -m proposal_build generate "Projects/<name>" --theme <editorial|classic> --use-latest-layouts --compress
```

If the Brief pins a `theme:`, drop the `--theme` flag:

```bash
python -m proposal_build generate "Projects/<name>" --use-latest-layouts --compress
```

If the command exits 0, surface the output PDFs to the user with
their full paths. If non-zero, parse stderr against the "Common
errors and friendly translations" table below — and report it to the
user. Never replace the renderer with a custom build.

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
| `formula cache is stale` / `tier totals don't match` | "The Worksheet's tier totals look stale — open it in Excel, recalculate (Cmd-=), save, then send it back so I can re-run generate." | No (manual). |
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
