# AE Standard Operating Procedure — Proposal Builder

This guide is for St. Nick's account executives. Proposals are **built
for you centrally** — you prepare the inputs on OneDrive, and the finished
deck + pricing PDFs are generated and dropped back into your project
folder. You do not install or run any software.

If you get stuck, ping Daniel.

---

## How it works (read once)

- Everything lives in OneDrive under **`Proposal Builder/Projects/<your project>/`**.
- You prepare three things: the **Brief**, the **renderings**, and the
  **Worksheet**.
- When they're ready, you tell Daniel. Generation runs on the build
  machine, and the finished PDFs sync back into your `03 - Scope & Pricing/`
  folder a few minutes later.
- You review, optionally polish in Canva, and send.

You never run Python, install a skill, or use git. If anything tells you to
"install the proposal builder skill" or "run a smoke test," that's the old
setup — **skip it**, it won't work on a PC and isn't how we run anymore.

---

## Setup (one-time)

1. **OneDrive signed in.** Make sure `OneDrive - Unicon Financial Services, Inc`
   is syncing on your PC.
2. **Keep the folder on your device.** In File Explorer, find
   `OneDrive - Unicon Financial Services, Inc › Proposal Builder`,
   right-click it → **"Always keep on this device."** Renderings must be
   real local files, not cloud placeholders, or generation can stall.
3. **Canva** (for optional final polish) — sign in with your `@st-nicks.com`
   account. The **"St. Nick's Branding Colors"** brand kit is already set up.

No Claude Desktop install, no Python, no repo to clone.

---

## Building a proposal

### 1. Get your project folder

New project? Ask Daniel to set it up — he'll create
`Proposal Builder/Projects/<name>/` with the full folder structure ready to
fill. It syncs to your PC within a minute or two.

### 2. Fill the Brief

Open `Project Brief.md` in the project folder and fill the fields at the top
(see **Brief frontmatter** in Reference for what each one means). If the YAML
format is unfamiliar, send Daniel the details and he'll set it.

### 3. Drop the renderings

Put your zone renderings (PNG / JPG from Stephanie or your design source) into:

```
02 - Renderings/Base Scope/     ← base-tier images
02 - Renderings/Enhancements/   ← enhancement-tier images
02 - Renderings/_inbox/         ← unsorted; sort into the two folders above later
```

Greenery reference photos go in `Greenery references/` at the project root
(NOT under `02 - Renderings/`). Don't delete the `_inbox` or
`Unused Renderings` folders — the generator needs them to exist.

### 4. Fill the Worksheet

Open `03 - Scope & Pricing/<project> - Scope Worksheet.xlsx` in Excel. Fill
the Customer-Facing Description and Tiers columns for every line item
(Size → Item → Details format; Daniel can show you the first time).
**Save and close Excel** when done — the generator can't read the file while
it's open in Excel.

### 5. Request generation

Tell Daniel (or post in the team channel): **"<project> is ready to
generate."** Generation runs centrally — you don't run this step yourself.

### 6. Review

A few minutes later these appear in `03 - Scope & Pricing/` and sync to your PC:

- `<project> - <year> Holiday Proposal.pdf` — the proposal deck.
- `<project> - <year> Itemized Pricing - Essential.pdf` / `Enhanced.pdf` /
  `Signature.pdf` — the per-tier pricing supplements.

Open them and review. Need a change? **Fix the Brief or Worksheet and ask for
another generation** — don't edit the PDF directly.

### 7. Polish in Canva (optional — the "last 10%")

The generated PDF is the source of truth: the numbers, scope, and brand
layout are already correct and approved. Use Canva *only* for final visual
polish on a deck you're done editing — nudging a title, swapping a hero
image, tightening spacing before it goes to the customer. Don't rebuild the
deck in Canva and don't change pricing or scope there; if those need to
change, fix the Worksheet/Brief and request another generation (step 5).

**A. Start from the final PDF.** Finish all real edits first. Canva is the
last step, not part of the drafting loop.

**B. Get the deck into Canva.** Use the manual upload — it's the simplest and
keeps the file off any public link:

1. In Canva, click **Create design → Import file** and choose the proposal
   PDF from `03 - Scope & Pricing/`.
2. Canva converts each PDF page into an editable slide.
3. Heads-up: PDF import can **shift some formatting** (fonts, spacing, image
   crops). That's normal for any PDF-to-Canva conversion — it's exactly the
   kind of thing the polish pass fixes. Apply the **"St. Nick's Branding
   Colors"** brand kit after import to snap colors and fonts back.

> If you'd rather not upload by hand, Claude can pull the deck in
> automatically — but only from a public download link (e.g. a OneDrive
> "share with download" URL). Because that briefly exposes the pricing deck
> at a URL, prefer the manual upload for customer proposals and ask Daniel
> before using the link method.

**C. Let Claude do the polish.** Once the deck is open in Canva, Claude can
edit it directly through the Canva connection. Ask things like:

> *"Apply the St. Nick's brand kit to this Canva design and fix any fonts
> that imported wrong."*
>
> *"Swap the cover image on page 1 for this rendering."*
>
> *"Tighten the spacing on the pricing slide so nothing's cut off."*

Claude can adjust text, swap assets, re-apply brand colors/fonts, and tidy
layout. It **cannot** reach a file on your computer — the deck has to be in
Canva first (step B).

**D. Export the finished deck from Canva** (Share → Download → PDF) and save
it back into `03 - Scope & Pricing/` as your send-ready version. The original
generated PDF stays as the system-of-record copy.

---

## For the build operator (Daniel)

Generation runs on the Mac that has the engine installed (the repo + venv +
WeasyPrint). It reads and writes the OneDrive project folder directly, so
outputs sync straight back to the AE.

```bash
cd "/Users/Daniel-Admin/Documents/Claude/Projects/proposal-build"
.venv/bin/python -m proposal_build inspect  "<OneDrive>/Proposal Builder/Projects/<name>"
.venv/bin/python -m proposal_build generate "<OneDrive>/Proposal Builder/Projects/<name>"
```

(Or do it conversationally in your own Claude Desktop, where the skill + venv
already work — just point it at the OneDrive path.)

- **Scaffolding a new project:** `python -m proposal_build scaffold "<name>"`
  creates the folder skeleton; create it under the OneDrive `Projects/` path
  so the AE can fill it.
- **Snapshots / diff mode:** each `generate` writes a `runs/` snapshot and
  `last_run.json` into `04 - Process & Notes/`. These power diff-mode
  regeneration (regenerate only what changed), so keep them on — AEs never
  open that folder. Prune old `runs/` occasionally to keep OneDrive tidy. Use
  `--no-snapshot` only for throwaway test runs.
- **Source of truth:** active customer projects live on OneDrive; the git repo
  holds the engine + the Riverside fixture only.

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

| What you'll hear | What's actually wrong | Fix |
|---|---|---|
| "Brief is missing `client_company`." | Required field empty in the YAML. | Fill the value in `Project Brief.md`. |
| "X.png referenced but not in renderings folder." | A `hero_image:`/`cover_image:` points at a file that's not there. | Drop the file into `Base Scope/` (or fix the reference). |
| "Worksheet appears to be open in Excel." | The `.xlsx` is locked because Excel is editing it. | Close Excel, then ask for generation again. |
| PDFs never show up after you asked for generation | The request didn't reach Daniel, or a blocker stopped it. | Ping Daniel — he'll see the blocker and tell you what to fix. |

### FAQ

**Q: Why do I have to fill the Worksheet manually instead of it being
   filled from the RFP?**
A: That automation is on the roadmap. For now, prep the Worksheet yourself.

**Q: Can two AEs work on the same project at the same time?**
A: Avoid it. OneDrive will create "conflict copies" if two people edit the
same file at once. Coordinate so one person owns a project's inputs at a
time; if you see a conflict copy, ping Daniel before resolving it.

**Q: Where do the generated PDFs go?**
A: `Projects/<project>/03 - Scope & Pricing/` on OneDrive. They sync to your
PC automatically a few minutes after generation runs.

**Q: Who do I ask for help?**
A: Daniel (`daniel@st-nicks.com`). For design / rendering questions,
Stephanie Escobar.

---

## Revision Tracking (operator reference)

After each successful `python -m proposal_build generate <project>`
run, the engine writes three artifacts into the project folder:

- `04 - Process & Notes/last_run.json` — internal snapshot of all
  inputs and outputs. Drives the next run's change report. Do not edit
  by hand.
- `04 - Process & Notes/revisions/v<n>/` — automatic archive of the
  deck, itemized PDF, last_run.json, and change_summary.md at the time
  of revision N. Open in Finder/Explorer to recover a prior version.
- `05 - Output/change_summary.md` — paste into the customer email
  body. The section above the second `---` is customer-facing; the
  section below it is internal notes to trim before sending.
