# St. Nick's Proposal Builder Skill — Design Document

**Status:** Draft for review
**Date:** 2026-05-01
**Owner:** Daniel Christenson (daniel@st-nicks.com)
**Surface:** Claude Desktop skill

---

## 1. Purpose & Scope

A Claude Desktop skill that turns customer RFP materials, a structured project brief, a scope worksheet, and renderings into a polished, on-brand proposal — consistently, with minimal AE input time and no slide-by-slide cleanup.

### Goals

1. **Consistent output.** Same brand standards (colors, typography, layout, voice) on every proposal.
2. **Efficient for AEs.** Realistic input time by phase:
   - **Phase 0 review + pricing:** 45–90 min — mostly offline (site walk follow-up, line-item review, pricing), not skill interaction
   - **Phase 1 confirmation:** 5–10 min — batch-confirm rendering names + categories
   - **Phase 2 review:** 10–20 min — review coverage report, review generated PDF, request fixes if needed

   The speedup vs. the prior process comes from **eliminated rework** (no slide-by-slide visual fixes, no missed renderings, no copy paraphrasing failures), not from compressing the raw input AEs already do. Pricing 25 line items takes 30 minutes whether Claude helps or not.
3. **No information lost.** Every rendering is placed; every line item is on a slide. Coverage is verified before generation.
4. **Variable scope.** Deck length, slide selection, tier structure, and voice all adapt to the project.
5. **Iterative-friendly.** Skill is designed for incremental upgrades — new layouts, voices, libraries, project archetypes can be added without rewriting.

### Non-goals (V1)

- PowerPoint editing (.pptx output is dropped; see Architecture Decision)
- Pricing math or quote generation (the Worksheet owns pricing; the skill never invents numbers)
- CRM integration (Zoho)
- E-signature workflow integration

### Deferred to future iterations

- Project archetypes beyond holiday/seasonal commercial decor (multi-year master agreement preview slide; equipment-purchase-only slim deck; one-day-event timeline)
- Spanish-language output
- Multi-decision-maker signature blocks

### Driving constraints (from past failure modes)

The prior attempt at this skill failed for specific, documented reasons (see `Sample Proposal/Downtown Riverside Metro Link/04 - Process & Notes/Session Debrief and Proposal SOP.md`). The design directly addresses each:

| Past failure | Design response |
|--------------|-----------------|
| Find-and-replace from another deck → text overflow + image distortion | HTML/CSS templates render with proper text reflow + image aspect-ratio handling |
| Most renderings never made it into the deck | Coverage check before generation; rendering ingestion phase enforces every rendering has a home |
| Loose paraphrase instead of pulling from worksheet | Customer-Facing Description column owned by AE; skill never paraphrases |
| No QA per slide | Optional checkpoint mode + post-generation coverage report |
| Treated build as one step | Three-phase workflow with explicit state detection at each invocation |

---

## 2. System Overview

### Inputs (per project)

| Input | File | Purpose |
|-------|------|---------|
| RFP materials | Whatever the customer sent | Source for Phase 0 RFP intake |
| Project Brief | `Project Brief.md` | Project metadata + voice + creative direction |
| Scope Worksheet | `[Client] - Scope Worksheet.xlsx` | Line items + pricing + renderings + tier scenarios |
| Renderings | Image files | Visual content for the deck |

### Outputs (generated per project)

| Output | Format | Purpose |
|--------|--------|---------|
| Polished Proposal | PDF | Customer-facing send |
| Canva Bulk Create CSV | CSV | Editable Canva path |
| Itemized Pricing Supplements | PDF (one per offered tier) | Detailed line-item pricing per tier (Essential/Enhanced/Signature when tiered; recommended only when single-price) |
| Coverage Report | Markdown | Pre/post-generation audit |

### Three-phase workflow

The skill is **stateful**. On each invocation it scans the project folder, reports state, and prompts the AE for the next action.

- **Phase 0 — RFP Intake.** Reads `01 - RFP/`. Drafts `Project Brief.md` and `Scope Worksheet.xlsx` from RFP content + element taxonomy. Pricing and final wording are AE responsibilities.
- **Phase 1 — Rendering Ingestion.** Walks `02 - Renderings/_inbox/`. Uses Claude Desktop vision to identify decor elements. Cross-references the worksheet. Renames + relocates files following convention. AE confirms in batch.
- **Phase 2 — Proposal Generation.** Validates inputs, runs coverage check, generates PDF + CSV + Itemized Pricing PDF + Coverage Report.

The AE never has to remember which mode to invoke — the skill detects state and prompts.

---

## 3. Architecture Decision

### PDF generation: HTML/CSS templates → WeasyPrint → PDF

**Why this beats the alternatives:**

- Pixel-perfect, deterministic. Same input → same output every time.
- CSS is locked — brand colors and typography are CSS variables that the model never edits at runtime.
- Text overflow is handled by CSS, not by the model. The python-pptx failure mode (text bleeding out of boxes, image distortion) is structurally impossible.
- WeasyPrint runs as pure Python in Claude's code sandbox — no headless browser dependency.
- Adding a new layout (4-up gallery, full-bleed hero) is minutes — just a new HTML file.
- Easiest visual debugging — open the assembled HTML in a browser to see exactly what the PDF will look like.

**Alternatives considered and discarded:**

- **python-pptx → .pptx.** Caused the prior failure. Discarded.
- **Markdown → Pandoc → PDF.** Doesn't handle multi-column showcase grids well. Discarded.
- **Headless browser (Playwright) → PDF.** More flexible than WeasyPrint, but heavier dependency. Held in reserve for edge cases.

### Brand enforcement

CSS variables in `skill_assets/layouts/brand.css`:

```css
:root {
  --color-red: #B31315;        /* Headlines, accents, CTAs ONLY — never body */
  --color-charcoal: #1C1C1C;   /* Body on light backgrounds */
  --color-gray: #555555;       /* Captions, secondary text */
  --color-navy: #12355B;       /* Secondary accent */
  --color-light: #ECEFF1;      /* Body on dark backgrounds; light fills */
  --font-heading: "Roboto", sans-serif;     /* Bold for headings */
  --font-body: "Poppins", sans-serif;        /* Regular for body */
}
```

The model never writes a hex color into a slide. All color references resolve through these variables.

### Font & sandbox dependencies

Roboto and Poppins **must be embedded in `skill_assets/fonts/`** and loaded by WeasyPrint via `@font-face` declarations in `brand.css`. They are never loaded from the system.

```css
@font-face {
  font-family: "Roboto";
  src: url("../fonts/Roboto-Bold.ttf") format("truetype");
  font-weight: 700;
}
@font-face {
  font-family: "Poppins";
  src: url("../fonts/Poppins-Regular.ttf") format("truetype");
  font-weight: 400;
}
/* ...additional weights */
```

**Why:** Claude's code sandbox does not guarantee specific system fonts are available. Relying on the system would cause silent font substitution at generation time — the model would render fine in dev and then ship Times Roman to the customer. Embedded fonts make output identical across every environment.

Required font files (TTF or WOFF2) shipped in `skill_assets/fonts/`:

- Roboto Bold — headings, key statements
- Roboto Regular — subheadings
- Poppins Regular — long-form body
- Poppins Medium — body emphasis
- Poppins Light — captions, descriptions

### Canva-editable path

The same Python generation pass emits a CSV matching Abigail's Canva master template's named placeholders. AE drops it into Canva Bulk Create → deck text auto-fills. AE manually swaps in renderings (Bulk Create supports text only, not images). ~2 minutes of Canva work for an editable backup.

---

## 4. Inputs in Detail

### 4.1 Project Brief schema (`Project Brief.md`)

YAML frontmatter for structured fields, prose sections below for narrative content.

```yaml
---
# Client
client_company: "Riverside County Transportation Commission (RCTC)"
client_decision_maker: "Jacklyn Moreno"
client_decision_maker_title: "Capital Projects Manager"
client_decision_maker_email: "jmoreno@bec-riv.org"
client_address: ""              # optional

# Project
project_name: "Downtown Riverside MetroLink — 2026 Holiday Program"
project_short: "Riverside MetroLink"   # used in footers
project_year: 2026

# Presenter
presenter_name: "Jonathan Yang"
presenter_email: "jonathan@st-nicks.com"
presenter_phone: "(562) 438-0017"

# Schedule (only go_live is required; rest auto-derive if blank)
go_live: "2026-11-20"
season_end: "2027-01-05"
fabrication_lock: ""             # default: go_live − 90 days
signing_deadline: ""             # default: go_live − 21 days

# Tone & creative
voice: "civic"                   # civic | destination-retail | corporate | hospitality
recommended_tier: "enhanced"     # essential | enhanced | signature
design_phrase: "Holiday Express"

# Assets
cover_image: "Wreaths - Station Entrance 01.png"
case_study: "oregon_zoo"         # filename (sans .md) or "skip"

# Slide control (defaults shown — only set to override)
include_case_study: true
include_add_ons: true
pricing_format: "tiered"          # tiered | single
mode: "one-shot"                  # one-shot | checkpoint

# Sample of Our Work — array of past_work IDs (optional; default = best-of for voice)
sample_work: ["pier_39", "jfk_terminal_1", "oregon_zoo", "sphere_tree", "led_angels", "music_center"]
---

## Creative Direction

(2–3 sentences. Sets the visual narrative for slide 4.)

## Customer Goals
- (bullet 1)
- (bullet 2)

## Customer Success Criteria
- (bullet 1)
- (bullet 2)

## Constraints
- (bullet — or "none" to omit the box on slide 3)

## Showcase Sections
1. **Section Name** — one-line subtitle
2. **Section Name** — one-line subtitle
3. **Section Name** — one-line subtitle
```

The Brief is intentionally lean. Boilerplate (insurance terms, payment schedule, change-order policy, scope inclusions) lives in the skill, not here.

### 4.2 Scope Worksheet schema

Existing columns retained. **Three new columns added:**

| Column | Required | Notes |
|--------|:---:|-------|
| # | yes | Line ID (`1`–`N` for base, `E1`–`EN` for enhancements) |
| Item | yes | Short name |
| Description / Location | yes | Internal language — for ops |
| Qty | yes | |
| Unit | yes | `ea`, `LF`, `LS`, etc. |
| Price per Unit | yes | Worksheet owns pricing |
| Line Total | yes | `Qty × Price` (formula) |
| Rendering Reference | yes | Filename in `02 - Renderings/{Base Scope|Enhancements}/` or `(no rendering)` |
| Materials / Build / Anchoring | optional | Internal — surfaces to slide 8 if useful |
| Notes / Assumptions | optional | Internal-only |
| **Customer-Facing Description** *(NEW)* | **yes** | Clean copy for showcase slides |
| **Section** *(NEW)* | **yes** | Showcase Section assignment (1, 2, or 3) — matches Brief |
| **Tiers** *(NEW)* | **yes** | Comma-separated values from `{Essential, Enhanced, Signature}` indicating which tier(s) include this line item. Drives per-tier itemized pricing PDFs and tier-scoped slide content. |

**Tier-membership rules and substitutions:**

- A typical base-scope item that ships in all three tiers: `Essential, Enhanced, Signature`
- An enhancement included in Enhanced + Signature only: `Enhanced, Signature`
- A Signature-only item (e.g., custom Bell Display, Spiral LED Tree alt): `Signature`
- **Substitutions are handled by precise membership, not a separate column.** Example from Riverside: the Traditional Tree (line #11) is in `Essential, Enhanced` (excluded from Signature because the Spiral LED Tree replaces it); the Spiral LED Tree (E6) is in `Signature` only. The two rows together describe the substitution.

Tier scenarios at bottom of sheet retained as today (Essential / Enhanced / Signature with totals); these are computed by summing line items where the `Tiers` column contains the relevant tier name. The skill validates that the bottom-row tier totals match the per-line tier-membership math; mismatches halt generation.

### 4.3 Rendering convention

Filenames after Phase 1: `{Element} - {Description} - {Location}.png`

Folder structure under `02 - Renderings/`:

| Folder | Contents |
|--------|----------|
| `_inbox/` | Raw drops, any names — Phase 1 input |
| `Base Scope/` | Used in Essential and above |
| `Enhancements/` | Used in Enhanced/Signature tiers + Add-Ons slide |
| `Unused Renderings/` | Explicitly skipped, with documented reason |

---

## 5. Phase 0 — RFP Intake

### Inputs

Whatever the customer sent, dropped into `01 - RFP/`. Common contents:

- A conceptual deck (.pptx)
- Written scope (.pdf, .docx)
- Site photos and architectural references
- Mood boards / aesthetic references
- Pole counts, square footage, construction notes

### Process

1. Skill scans `01 - RFP/` recursively.
2. For each file:
   - Text: extract content (PyMuPDF for PDF, openpyxl for Excel, python-pptx for slide text, Pillow + vision for images embedded in slides)
   - Slide images: vision identifies decor elements
   - Standalone reference photos: vision identifies decor elements
3. Cross-reference against `skill_assets/rfp_taxonomy/elements.yaml` — controlled vocabulary of ~30 known decor elements:

   ```yaml
   elements:
     - id: pole_banner
       names: [pole banner, light pole banner, lamppost banner]
       unit: ea
       common_locations: [streetlight pole, station entrance, plaza]
     - id: perimeter_garland
       names: [perimeter garland, fence garland, swag garland]
       unit: LF
       common_locations: [perimeter fence, plaza fence, building eave, gates]
     - id: signature_wreath
       names: [signature wreath, oversized wreath, tower wreath]
       unit: ea
       common_locations: [stair tower, brick column, building façade]
     # ... ~27 more entries
   ```

4. Drafts:
   - **`Project Brief.md`** — fills: customer goals, success criteria, constraints, design phrase, suggested voice, suggested showcase sections, suggested case study reference, cover image suggestion. Prose sections drafted from RFP content.
   - **`Scope Worksheet.xlsx`** — fills: identified line items, qty estimates (or `TBD - confirm on site walk`), Customer-Facing Description draft, Section assignment, Rendering Reference left blank. **Pricing left blank.**

5. Skill produces a summary report for AE:

   ```
   RFP ANALYSIS — Downtown Riverside MetroLink
   ───────────────────────────────────────────
   CUSTOMER INTENT (extracted):
   - Holiday Express theme (Mission Inn-inspired)
   - Multi-zone application: station entrance, platforms, perimeter
   - Civic landmark for downtown Riverside

   12 LINE ITEMS PROPOSED (pricing left blank):
   1. Pole banners (qty TBD — count poles on site walk)
   2. Canopy lighting (16 standard + 2 large bus stop)
   ...

   3 SHOWCASE SECTIONS PROPOSED:
   1. Station Arrival & Plaza
   2. Platforms & Perimeter
   3. Custom Centerpieces

   CASE STUDY SUGGESTION: oregon_zoo
   VOICE INFERENCE: civic
   COVER IMAGE: TBD — no rendering yet
   ```

6. AE confirms or edits.

### Unknown element handling

When vision identifies a decor element that does not match any entry in `elements.yaml`, the skill **never silently drops or guess-tags it.** The item is recorded with:

- `status: needs_ae_confirmation`
- `vision_description:` the model's description, **verbatim, with no rewording**
- `proposed_taxonomy_entry:` a suggested element ID + names + unit + locations the AE can adopt or override

The same flag applies when a match exists but vision confidence is **below 0.75**. The AE confirms or corrects every flagged item in the Phase 0 summary. Confirmed novel elements can be promoted into `elements.yaml` for future reuse — the taxonomy grows organically with the business.

This is critical because the V1 taxonomy ships with ~30 entries and the business will encounter elements not yet cataloged. Silent failure here would replicate the prior attempt's failure mode of items getting missed.

### What stays the AE's job

- Pricing every line item
- Confirming quantities (especially `TBD` items) — usually requires site walk
- Refining customer-facing prose
- Final voice/tone tuning

### Output

- `04 - Process & Notes/Project Brief.md` (draft)
- `03 - Scope & Pricing/[Client] - Scope Worksheet.xlsx` (draft)

The AE then opens both, reviews, fills pricing, and signs off.

---

## 6. Phase 1 — Rendering Ingestion

### Trigger

Files exist in `02 - Renderings/_inbox/`.

### Process

For each unsorted image:

1. Vision: identify what decor element is shown.
2. Cross-reference the Worksheet: find the matching line item by item type + location.
3. Propose:
   - New filename: `{Element} - {Description} - {Location}.png`
   - Category: `Base Scope` if matches a base line item; `Enhancements` if matches an `Eitem`; `Unused Renderings` if no clear match.

4. Batch the proposals into a single AE confirmation:

   ```
   RENDERING INGESTION — 8 files in _inbox/

   1. ChatGPT_Image_Apr_30...02_33_45.jpg
      → Garlands - Decorated Swag - Plaza Fence.png
      → Enhancements/  (matches E8: Decorated Garland Upgrade — Front Gate)

   2. revised_1ChatGPT_Image_Apr_30...02_33_45.png
      → Lighted Snowflakes - Railing 02.png
      → Enhancements/  (matches E1: Lighted Snowflakes — Railing Mounted)

   ...
   ```

5. AE responds: "1 ✓, 2 change to Base Scope, 3 ✗ skip, ..."
6. Skill executes the rename + move.

### Edge cases

- **No worksheet line matches:** skill asks: "this image shows a 12 ft custom wreath, but no worksheet line matches — add a line item, or move to Unused Renderings?"
- **No rendering for a worksheet line:** Phase 2 coverage report flags it; AE either generates/sources the rendering or accepts the gap.
- **Duplicate match:** skill numbers automatically (`Wreaths - Station Entrance 01.png`, `02.png`).

---

## 7. Phase 2 — Proposal Generation

### Coverage check (pre-generation)

```
COVERAGE REPORT — Riverside MetroLink

Worksheet line items:   25 base + enhancements
  ✓ 25 mapped to slides
  ✗ 0 unmapped

Renderings:             26 in folders
  ✓ 24 placed on slides (Base Scope: 18, Enhancements: 6)
  ⚠ 2 in "Unused Renderings/" — confirming intentional skip:
      • Garlands - Decorated Straight - Parking Lot.png
      • Garlands - Decorated Straight - Street Fence.png

Brief fields:           filled
  ✓ All required fields present
  ⚠ case_study: skip → Case Study slide will be omitted

Estimated deck length:  16 slides
```

AE confirms or fixes gaps before rendering. Skill will not generate with `✗` issues unresolved.

### Slide catalog

| # | Slide | Always or conditional | Layout family |
|---|-------|-----------------------|---------------|
| 1 | Cover | Always | hero-image |
| 2 | Executive Summary | Always | at-a-glance grid + 3 pillars |
| 3 | Our Understanding | Always (constraints box hidden if "none") | 4-box |
| 4 | Creative Vision | Always | hero + 3-phase narrative |
| 5..N | Showcase Sections (1–3 sections) | Each spans 1–4 slides via auto-pagination | hero, 2-up, 3-up, 4-up grid, full-bleed |
| N+1 | Scope of Work | Always | 2-column inclusions + add-ons |
| N+2 | Sample of Our Work | Always | 6-tile grid |
| N+3 | Case Study | Conditional (`include_case_study`) | challenge / approach / outcome |
| N+4 | Investment | Always; layout switches by `pricing_format` | 3-tier or 1-tier |
| N+5 | Add-Ons | Conditional (auto-included if Worksheet has Enhancement rows) | line-item list with prices |
| N+6 | Terms & Next Steps | Always | dates + payment + insurance + change orders + validity |
| N+7 | Sign Block | Always | signature lines |
| N+8 | About St. Nick's | Always | company + team |

Total deck length: typically 11–18 slides.

### Auto-pagination of Showcase Sections

For each Showcase Section, the skill counts items + renderings and picks layout(s):

| Items in section | Renderings in section | Output |
|------------------|----------------------|--------|
| 1–3 / 1–2 | 1 slide (hero + sidebar) |
| 3–6 / 3–4 | 1 slide (2-up grid) |
| 6–10 / 4–6 | 2 slides (3-up grid + overflow) |
| 10+ / 7+ | 3+ slides as needed |

Layout choice can be overridden per section in the Brief: `Section 1 layout: full-bleed-hero`.

### Layout versioning

Every HTML layout file in `skill_assets/layouts/` carries a version header on its first line:

```html
<!-- layout-version: 2026-05-01 -->
```

The generation pass records which layout version each slide used in the Coverage Report:

```
LAYOUT VERSIONS USED
  cover.html              2026-05-01
  exec_summary.html       2026-05-01
  showcase_3up.html       2026-06-15
  investment_tiered.html  2026-05-01
  ...
```

**Default regeneration locks layout versions** to whatever was used on the previous run for that project (recorded in `04 - Process & Notes/last_run.json`). This protects in-flight proposals from cosmetic drift if a layout is updated mid-cycle — slide 6 will not suddenly look different on the second customer revision because we shipped a layout fix that morning.

To pull the latest layouts on regeneration, opt in via:

```
build proposal --use-latest-layouts
```

**Why this matters:** layouts evolve. Lock-by-default means an in-flight proposal stays visually consistent across all customer revisions. Refreshes are explicit, not accidental.

### Diff-mode regeneration

After the first successful generation, the skill writes a snapshot to `04 - Process & Notes/last_run.json` containing:

- Brief hash (per field, so we can detect which fields changed)
- Worksheet hash (per row, so we can detect which lines changed)
- Rendering inventory (filenames + sizes)
- Layout versions used per slide
- Output file hashes

On subsequent runs, the skill compares current inputs to the snapshot and:

**1. Reports what changed:**

```
CHANGES SINCE LAST RUN (2026-05-08)
- Brief: design_phrase changed ("Holiday Express" → "Holiday Express 2.0")
- Worksheet: 2 line items modified (E2 qty 4→6, E5 price $295→$310)
- Renderings: 1 added (Lighted Snowflakes - Railing 03.png), 0 removed
```

**2. Identifies which slides are affected:**

```
SLIDES TO REGENERATE
- Slide 4 (Creative Vision) — design_phrase changed
- Slide 6 (Showcase: Platforms & Perimeter) — E2 qty + new rendering placement
- Slide 10 (Investment) — pricing change
- Itemized Pricing — Enhanced — pricing change
```

**3. Regenerates only those slides + outputs**, leaving the rest bit-identical to the prior run.

**Dependency map (V1 build artifact):** the "identifies affected slides" step is driven by `skill_assets/dependency_map.yaml`, which declares for each slide and each per-tier itemized pricing PDF the set of Brief fields and Worksheet columns/rows it consumes. Diff mode loads the map, intersects the diff with each slide's dependency set, and produces the regeneration list. **This file is built as part of V1 deliverables — without it, "identifies affected slides" is hand-waving.** The dependency map and the layout files evolve together; layout versioning (above) is what keeps the two in sync — the map is keyed to layout versions, so updating a layout requires updating its dependency entry in the same change.

**Why this is V1, not deferred:** **2–3 customer revision rounds per proposal is typical** — drop a tier, add an item, adjust pricing, swap a rendering. Diff mode keeps the unchanged 80% of the deck stable across revisions, cuts regeneration time by ~70%, and gives the AE a clean change-log to summarize for the customer ("here's what changed in this round"). Without it, every revision regenerates the full deck and risks cosmetic drift between rounds — defeating the whole point of consistent output.

### Voice presets

Each `voice:` value in the Brief maps to:

- A tone preset (civic = confident-public-investment language; destination-retail = guest-experience language; corporate = professional-discreet language; hospitality = guest-comfort language)
- Default copy for prose sections the AE leaves blank
- A default case study suggestion if `case_study:` is blank

Voice presets live in `skill_assets/voice_presets/{voice}.md`.

### Past Work library

Bundled with the skill in `skill_assets/past_work_library/`. ~20 curated past projects. Each project has:

- `{project_id}.md` — name, year, scope summary, tags (civic, destination, corporate, hospitality)
- `{project_id}.jpg` — single hero image, sized for the 6-tile grid (typically 1200×800)

Brief specifies `sample_work:` array (or leaves blank for default-by-voice). Skill picks 6 for the slide.

### Case Study library

Same shape: `{case_id}.md` per study. Brief picks one via the `case_study:` field. Studies follow a fixed structure: challenge / approach / outcome.

---

## 8. AE Workflow Modes

The Brief flag `mode:` controls generation behavior:

- **`one-shot`** (default): coverage check → generate full deck → AE reviews PDF → AE requests fixes if needed.
- **`checkpoint`**: per-slide build, AE approves each before next. ~30–45 min/proposal. Use for first proposal of a new project type or when the AE wants to QA each slide.

---

## 9. Repo Structure

```
proposal-build/                                   ← Repo root
│
├── 00_Company_Context/                           ← Always-on context
│   ├── about_st_nicks.md
│   ├── glossary.md
│   └── org_chart.md
│
├── Branding Board/                               ← Brand assets, logos, colors
│
├── skill_assets/                  (NEW)
│   ├── fonts/                                    ← Embedded TTF/WOFF2 (Roboto + Poppins)
│   │   ├── Roboto-Bold.ttf
│   │   ├── Roboto-Regular.ttf
│   │   ├── Poppins-Regular.ttf
│   │   ├── Poppins-Medium.ttf
│   │   └── Poppins-Light.ttf
│   ├── layouts/                                  ← HTML + CSS slide templates (each carries layout-version header)
│   │   ├── brand.css                             ← LOCKED color/font/spacing rules; @font-face loads from ../fonts/
│   │   ├── cover.html
│   │   ├── exec_summary.html
│   │   ├── showcase_2up.html
│   │   ├── showcase_3up.html
│   │   ├── showcase_4up.html
│   │   ├── showcase_fullbleed.html
│   │   └── ... (etc.)
│   ├── boilerplate/                              ← Reusable text blocks
│   │   ├── terms.md
│   │   ├── payment_schedule.md
│   │   ├── change_orders.md
│   │   └── scope_inclusions.md
│   ├── voice_presets/
│   │   ├── civic.md
│   │   ├── destination-retail.md
│   │   ├── corporate.md
│   │   └── hospitality.md
│   ├── past_work_library/                        ← 20 curated projects
│   │   ├── pier_39.md
│   │   ├── pier_39.jpg
│   │   └── ...
│   ├── case_studies/                             ← Case study .md files
│   │   ├── oregon_zoo.md
│   │   ├── pier_39.md
│   │   └── ...
│   ├── rfp_taxonomy/
│   │   └── elements.yaml                         ← ~30 known decor elements
│   ├── dependency_map.yaml                       ← Slide ↔ Brief/Worksheet field map (drives diff mode)
│   ├── generate.py                               ← Python: Phase 2 generation
│   ├── ingest_renderings.py                      ← Python: Phase 1 ingestion
│   ├── analyze_rfp.py                            ← Python: Phase 0 RFP intake
│   └── skill.md                                  ← Skill manifest + AE-facing instructions
│
├── Projects/                      (RENAMED from "Sample Proposal/")
│   ├── _master_templates/         (NEW)         ← Reference-only originals
│   │   ├── StNicks_Proposal_v2_Master.pptx
│   │   └── StNicks_Supplemental_Itemized_Pricing.pdf
│   │
│   ├── _template_project/         (NEW)         ← Blank — duplicate this
│   │   ├── 01 - RFP/
│   │   ├── 02 - Renderings/
│   │   │   ├── _inbox/
│   │   │   ├── Base Scope/
│   │   │   ├── Enhancements/
│   │   │   └── Unused Renderings/
│   │   ├── 03 - Scope & Pricing/
│   │   │   └── [Client] - Scope Worksheet.xlsx   ← blank template w/ new columns
│   │   └── 04 - Process & Notes/
│   │       └── Project Brief.md                   ← blank template
│   │
│   └── Downtown Riverside Metro Link/             ← Existing project
│       └── (untouched — but Brief.md added)
│
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-05-01-proposal-builder-skill-design.md   ← This document
│
└── AE_SOP.md                       (NEW)         ← AE-facing operations manual
```

### Changes from current state

- Rename `Sample Proposal/` → `Projects/`
- Move `StNicks_Proposal_v2_Master.pptx` and `StNicks_Supplemental_Itemized_Pricing.pdf` into `Projects/_master_templates/`
- Add `Projects/_template_project/` (blank — duplicated for each new project)
- Add `skill_assets/` at repo root containing all skill libraries + Python code
- Add `_inbox/` subfolder under each project's `02 - Renderings/`
- Add `AE_SOP.md` at repo root

---

## 10. Deliverables

1. **Skill bundle** at `skill_assets/`:
   - `skill.md` — manifest + skill instructions
   - **Embedded fonts** (Roboto Bold/Regular, Poppins Regular/Medium/Light) in `fonts/`
   - HTML/CSS layout templates (each with `<!-- layout-version: YYYY-MM-DD -->` header)
   - Brand CSS (locked) with `@font-face` declarations loading from `fonts/`
   - Past Work library (20 projects + photos)
   - Case Study library (3+ studies — start with oregon_zoo, pier_39, plus one civic-relevant project)
   - Boilerplate text (terms, payment schedule, change-order policy, scope inclusions)
   - Voice presets (4)
   - RFP element taxonomy (~30 elements)
   - **Dependency map** (`dependency_map.yaml`) — slide ↔ Brief/Worksheet field dependencies, required for diff-mode regeneration
   - Python: `analyze_rfp.py`, `ingest_renderings.py`, `generate.py`

   **Itemized Pricing PDFs are generated per offered tier:** when `pricing_format: tiered` produces three PDFs (Essential / Enhanced / Signature); when `pricing_format: single` produces one (recommended tier only). Per-tier line items are derived from the Worksheet's `Tiers` column.

2. **Blank template project folder** (`Projects/_template_project/`) with empty input files at correct paths

3. **Master templates relocated** to `Projects/_master_templates/`

4. **AE-facing SOP** (`AE_SOP.md`) — operations manual covering:
   - Starting a new proposal (duplicate template, rename, drop RFP materials)
   - Phase 0: invoke skill → review draft Brief + draft Worksheet → price + refine
   - Phase 1: drop renderings into `_inbox/` → invoke skill → confirm names + categories
   - Phase 2: invoke skill → review coverage report → confirm → outputs land in `03 - Scope & Pricing/`
   - Optional checkpoint mode for high-stakes/first-of-type proposals
   - Troubleshooting (common failures + fixes)

5. **Updated repo structure** — renames + new directories committed

---

## 11. Open Items / Future Iterations

- Project archetypes beyond holiday/seasonal commercial decor:
  - Multi-year master agreement preview slide ("Year 1 / Year 2 / Year 3")
  - Equipment-purchase-only slim deck (skips most service slides)
  - One-day-event timeline (corporate gala) with single timeline slide
- Spanish-language output
- Multi-decision-maker signature blocks
- Zoho CRM integration for AE intake auto-population
- Customer-side e-sign integration

---

## 12. Spec self-review

Reviewed against:
- **Placeholder scan:** no TBDs, all sections complete
- **Internal consistency:** every component referenced is defined; data flows resolve. Per-tier itemized pricing depends on Worksheet `Tiers` column (§4.2). Diff-mode regeneration depends on `dependency_map.yaml` (§7) which is keyed to layout versions (§7).
- **Scope:** single-implementation-plan-sized — three phases, well-bounded, leaning on existing libraries (WeasyPrint, openpyxl, Pillow). Diff-mode and per-tier pricing are added to V1 with concrete supporting artifacts (snapshot file, dependency map, Tiers column).
- **Ambiguity:** schemas and field requirements are explicit; voice/tier/mode/pricing_format flags are enumerated; vision confidence threshold for unknown-element flagging set at 0.75 (§5).
- **Sandbox/font determinism:** fonts embedded in `skill_assets/fonts/`, never loaded from system (§3).
- **Layout drift protection:** layout versioning per file + lock-by-default on regeneration (§7).
