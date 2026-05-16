# AE Standard Operating Procedure — Proposal Builder

This guide is for St. Nick's account executives using the proposal-
builder skill in Claude Desktop. It walks through one-time setup, the
per-project workflow, and reference material.

If you get stuck, ping Daniel.

---

## Setup (one-time)

You only do this once per Mac.

### 1. Install Claude Desktop

Download Claude Desktop from <https://claude.ai/download> and sign in
with your `@st-nicks.com` account.

### 2. Enable shell access in Claude Desktop

The skill needs Claude to run command-line commands on your behalf.
In Claude Desktop's settings, allow Bash / shell tool access for the
proposal-builder skill. Daniel can walk you through this if needed.

### 3. Clone the team repository

Ask Claude:

> *"Clone the proposal-build repo from GitHub into my Documents folder."*

Claude will run the clone for you. The repo lives at
`~/Documents/Claude/Projects/proposal-build/`.

### 4. Install the skill

In Claude Desktop's skill settings, point to
`~/Documents/Claude/Projects/proposal-build/skill_assets/skill.md` and
install the skill. Claude Desktop should now activate the skill on
phrases like *"build a proposal for X."*

### 5. Verify with a smoke test

Ask Claude:

> *"Run the proposal builder on Downtown Riverside Metro Link as a smoke
> test."*

Expected outcome: Claude inspects, reports "Ready to generate," runs
the generator, and tells you the PDF paths in
`Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/`. Open
one PDF to confirm it renders correctly.

If anything fails, send Daniel the error message Claude shows you.

### Setup troubleshooting

If the smoke test fails with a font/library error like
`cannot load library 'libgobject-2.0-0'`, the proposal renderer's
system dependencies aren't on your machine yet. Send Daniel the error
and he'll walk you through installing Pango/Cairo via Homebrew. (Most
AE machines already have it from a prior project; only first-time
setups hit this.)

For any other smoke-test failure, send Daniel the error verbatim. Do
NOT try to "fix" it yourself unless he says so — the skill's beta
safety rails are designed to protect your project files.

---

## Daily workflow — building a new proposal

### 1. Pull the latest

Before starting any project, ask Claude:

> *"Pull the latest changes for the proposal-build repo."*

This makes sure you have the team's latest layouts, boilerplate, and
sibling projects before you start.

### 2. Start the project

Ask Claude:

> *"Build a proposal for `<project name>`."*

Examples:
- *"Build a proposal for Long Beach Airport."*
- *"Generate the Tachi Christmas 2026 proposal."*

If the project doesn't exist yet, Claude will offer to scaffold it from
the template. Say yes — you'll get the full folder structure ready to
fill in.

### 3. Answer the Brief questions

Claude will walk you through filling in the Brief one question at a
time. Examples:

- *"What's the client company?"*
- *"What's the proposal date?"* (today, in YYYY-MM-DD)
- *"Who's the AE on this project?"*

Claude writes your answers into the Brief automatically. If you don't
know an answer, just say so — you can come back to it later.

### 4. Drop the renderings

When Claude tells you the renderings folder is empty, drop your zone
renderings (PNG / JPG files from Stephanie or your design source) into:

```
Projects/<project name>/02 - Renderings/Base Scope/
```

Use the sibling `02 - Renderings/Enhancements/` folder for enhancement-tier
images. Greenery reference photos go in `Projects/<project name>/Greenery references/` (at the project root, NOT under `02 - Renderings/`).

If you have unsorted renderings, drop them into `_inbox/` first and
sort them later.

Reply *"renderings ready"* and Claude will pick up.

### 5. Fill the Worksheet

Claude will tell you when the Worksheet needs work. Open the file in
Excel:

```
Projects/<project name>/03 - Scope & Pricing/<project> - Scope Worksheet.xlsx
```

Fill the Customer-Facing Description and Tiers columns for every line
item. Daniel can show you the format if it's your first time.

Save and close Excel before you reply *"worksheet ready"* — the skill
can't read the file while it's open.

### 6. Pick hero images per zone

Claude will list the renderings you dropped and ask which one fits each
zone. Pick the best one per zone (the photo customers will associate
with that location).

### 7. Generate

Once everything's filled in, Claude says *"Ready to generate"* and runs
the generator. The output PDFs land in
`03 - Scope & Pricing/`:

- `<project> - <year> Holiday Proposal.pdf` — the proposal deck.
- `<project> - <year> Itemized Pricing - Essential.pdf` /
  `Enhanced.pdf` / `Signature.pdf` — the per-tier pricing supplements.

Open them and review.

### 8. Commit & push

Claude will offer to save your work to the team repo:

> *"Want me to commit and push?"*

Say yes. Your project folder is now safely backed up and visible to
the rest of the team.

---

## Reference

### Brief frontmatter — what each field means

The Brief is the YAML at the top of `Project Brief.md`. Fields marked
**bold** are required (the inspector blocks generation if they're
empty); the rest are recommended but optional.

| Field | What it means |
|---|---|
| **`client_company`** | Full legal client name (e.g. "Riverside County Transportation Commission (RCTC)"). |
| `client_short` | Short version for headers (e.g. "RCTC"). |
| **`project_name`** | Full project name (e.g. "Downtown Riverside Metro Link"). |
| `project_short` | Short version (e.g. "Riverside MetroLink"). |
| **`project_year`** | The decoration year (e.g. 2026). |
| `proposal_type` | Usually "Holiday Proposal". |
| **`presenter_name`** / `presenter_title` / `presenter_email` / `presenter_phone` | The AE on the project (probably you). Only `presenter_name` is required; the other three are strongly recommended. |
| `proposal_date` | Today, in YYYY-MM-DD. |
| `go_live` | Decoration go-live date (YYYY-MM-DD). |
| **`voice`** | One of `civic`, `destination-retail`, `hospitality`. |
| **`recommended_tier`** | Your tier recommendation (`Essential`, `Enhanced`, or `Signature`). |
| `design_phrase` | Short evocative phrase for the Creative Vision slide (e.g. "Holiday Express"). |
| **`pricing_format`** | `tiered` for 3-tier proposals, `single` for one-tier. |
| **`cover_image`** | Filename of the cover hero (must exist in `02 - Renderings/Base Scope/`). |

### Menu-Mode Project Walkthrough

For projects where you want to present creative options to the client
before committing to a final scope (multi-rendering decks, first-pass
concept proposals like FIGat7th DTLA), use **menu mode** instead of
the default tiered flow.

The high-level workflow is the same — Brief, Worksheet, renderings,
generate — but the Brief schema and Worksheet shape are different:

1. In the Brief frontmatter, set `mode: menu` and define `sections:`
   instead of `zones:`. Each section is `{key, label, name, is_lead,
   item_codes}` — a short identifier (e.g. `"3a"`), the customer-
   facing label, the section name, whether this section's first slide
   carries a section header strip, and the ordered list of item codes
   to include from the worksheet.
2. Drop `recommended_tier`, `pricing_format`, `cover_image`, and
   `zones` — they don't apply in menu mode. Add `design_phrase`,
   `prebuilt_cover_image`, and `creative_vision_hero` instead.
3. Build the **ROM Worksheet** using the 15-column menu schema (see
   `Projects/Fig at 7th .../03 - Scope & Pricing/FIGat7th DTLA - Scope
   Worksheet.xlsx` for the canonical example). Each row carries
   rental low/high, purchase one-time low/high, and purchase annual
   service low/high — point estimates use low == high.
4. Drop pre-built cover and palette renderings into
   `02 - Renderings/Base Scope/` and reference them by filename in
   the Brief's `prebuilt_cover_image` and `prebuilt_palette_image`
   fields.
5. Single-item sections render as one `zone_solo` slide; multi-item
   sections render as one or two `zone_2up_gallery` slides (the lead
   slide carries the section header strip).
6. The customer sees a 3-column ROM pricing table at the end:
   Item / Rental (annual, all-in) / Purchase (one-time + annual
   service). Customer can mix and match per line item.

### Past Work slide (`sample_work:` in Brief)

The Past Work slide is a 6-tile image grid of prior-season installations.
To include it in a proposal, add a `sample_work:` list to the Brief naming
exactly 6 project IDs from `skill_assets/past_work_library/`.

```yaml
sample_work:
  - project_id_one
  - project_id_two
  - project_id_three
  - project_id_four
  - project_id_five
  - project_id_six
```

Rules:

- **Past work only.** Never include current-cycle prospects or any project
  still being pitched. The slide is social proof; an active deal on it reads
  as inflated track record.
- **Real customers only.** Every ID must correspond to a real installed
  project. No fictional, aspirational, or stand-in names.
- **Library is curated by Daniel.** New past-work entries (`.md` + `.jpg`)
  are added out-of-band. Do not auto-fill from the `Projects/` directory.

Omit `sample_work:` to skip the slide entirely. The inspector blocks
generation if `sample_work:` is present but lists ≠ 6 IDs, an unknown ID,
or an ID with a missing image.

### Tree Comparison slide (`tree_comparison:` in Brief, menu mode)

The Tree Comparison slide shows three tree-size alternatives near the
end of a menu-mode deck. Useful when the main pitch carries a flagship
tree that may be larger than the customer's budget. The slide does NOT
modify Section 2's pricing — it presents scale-down options as a
conversation tool, giving a customer who balks at the headline tree
price a downgrade path without St. Nick's pulling out a new proposal.

To include it, add a `tree_comparison:` block to the Brief naming
exactly 3 tree IDs from `skill_assets/tree_library/` plus a
`recommended:` ID (must be one of the three):

```yaml
tree_comparison:
  trees: [tree_30, tree_40, tree_50]
  recommended: tree_50
```

Rules:

- **Real configurations only.** Every ID must correspond to a tree
  St. Nick's can actually deliver from the vendor (Unisun frame tree
  series; `Master Proposal Reference/Reference Tree Catalog/` has the
  source docs).
- **Pricing must be confirmed.** Catalog dollar figures are
  heavy-decorated purchase prices pulled from the 2026 Frame Tree
  Pricing spreadsheet and appear on a customer-facing slide. Never
  seed an entry with placeholder or unconfirmed pricing.
- **Library is curated by Daniel.** New tree entries (`.md` + `.jpg`)
  are added out-of-band from confirmed spec sheets. The skill bundle
  ships the library with `.md` files for sizes 30/40/50; Daniel drops
  the matching `.jpg` photos before using the slide in a real customer
  deck.

**Internal note on ornament counts.** The 2026 Frame Tree Pricing
spreadsheet header column reads "22 Ornaments Per Branch" but the
customer-facing brochure (`St Nick's Frame Trees - 2026 Collection.pdf`)
defines heavy decoration as 20 ornaments per branch. The brochure
language is authoritative for customer copy; the pricing-column header
reconciliation is pending with the vendor (Abigail Lacson). Always
quote 20/branch on the customer slide.

Omit `tree_comparison:` entirely to skip the slide.

### Common errors and what they mean

| What Claude says | What's actually wrong | Fix |
|---|---|---|
| "Brief is missing `client_company`." | Required field empty in the YAML. | Reply with the value when Claude asks. |
| "X.png referenced but not in renderings folder." | A `hero_image:` points at a file that's not there. | Either drop the file in, or change the reference. |
| "Worksheet appears to be open in Excel." | The `.xlsx` is locked because Excel is editing it. | Close Excel, reply "ready". |
| "I've tried twice and the same error came back." | The skill hit its safety rail. | Send Daniel the output Claude shows. |

### FAQ

**Q: Why do I have to fill the Worksheet manually instead of Claude
   filling it from the RFP?**
A: That automation is on the roadmap (Plan 6 / Phase 0). For now,
the skill assumes you've prepped the Worksheet.

**Q: Can two AEs work on the same project at the same time?**
A: Not safely. Pull first, work, push when done. If two of you push
overlapping changes, ping Daniel before resolving.

**Q: Where do generated PDFs go?**
A: `Projects/<project>/03 - Scope & Pricing/`. They're git-ignored
(you don't push the PDFs themselves; the team regenerates from the
Brief + Worksheet + renderings).

**Q: Who do I ask for help?**
A: Daniel (`daniel@st-nicks.com`). For design / rendering questions,
Stephanie Escobar.

---

## Revision Tracking

After each successful `python -m proposal_build generate <project>`
run, the skill writes three new artifacts:

- `04 - Process & Notes/last_run.json` — internal snapshot of all
  inputs and outputs. Drives the next run's change report. Do not edit
  by hand.
- `04 - Process & Notes/revisions/v<n>/` — automatic archive of the
  deck, itemized PDF, last_run.json, and change_summary.md at the time
  of revision N. Gitignored, local-only. Open in Finder to recover a
  prior version.
- `05 - Output/change_summary.md` — paste into the customer email
  body. The section above the second `---` is customer-facing; the
  section below it is internal notes you should trim before sending.

### Re-generating after a Brief or Worksheet edit

Just run `python -m proposal_build generate <project>` again. The
terminal prints a CHANGES SINCE LAST RUN block listing exactly what
changed and which slides are affected. Review it before sending the
revised proposal to the customer.

If nothing changed since the last run, the skill rebuilds the outputs
but does not bump the revision counter or create a new `v<n>/` folder.

### Flags

- `--no-snapshot` — skip writing last_run.json and the revisions/
  archive. Use for throwaway or test renders.
- `--diff-only` — run the differ and write change_summary.md, but skip
  the render entirely. Use to preview what would change without
  rebuilding the deck.

### Schema mismatch

If a future skill version changes the snapshot format, an old
last_run.json will stop the run with upgrade instructions. Delete the
file to start fresh — you lose the revision counter but no actual
proposal data.

---

## Glossary

- **Brief**: the YAML + Markdown file at `04 - Process & Notes/
  Project Brief.md`. Defines everything about the project.
- **Worksheet**: the `.xlsx` at `03 - Scope & Pricing/<project> -
  Scope Worksheet.xlsx`. Defines line items and pricing per tier.
- **Skill**: the proposal-builder skill in Claude Desktop. Activates
  on phrases like "build a proposal for X."
- **Tier**: Essential / Enhanced / Signature — the three tiers of
  scope/pricing.
- **Hero image**: the primary rendering for a zone, shown big on the
  zone slide.
- **Inspect**: the readiness check the skill runs to find what's
  missing before generating.
- **Generate**: the actual PDF-creation step, run after all checks
  pass.
