# Plan 3 — Phase 2 Generation Core: Design

**Status:** Approved 2026-05-03 (brainstorming session, Daniel + Claude)
**Parent spec:** `docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md`
**Builds on:** `docs/superpowers/specs/2026-05-03-plan-2-prime-master-driven-design.md` (15 master-derived layouts)
**Successor:** Plan 4+ — see §13 deferred items

---

## 1. Goal

Wire the parent spec's Phase 2 (Proposal Generation) end-to-end: read a real `Project Brief.md` and migrated `Scope Worksheet.xlsx`, validate them, compose context dicts that match the Plan-2-prime fixture shape, and render a customer-ready proposal PDF + per-tier itemized pricing PDFs + a coverage report.

After Plan 3:
- An AE can open Claude Desktop, point at a project folder, and get a polished proposal without slide-by-slide work.
- The Riverside fixture project has a real Brief, a migrated worksheet, and a passing end-to-end test.
- The deterministic pipeline (Parser → Composer → Renderer) is in place for Plans 4+ to build diff-mode regeneration, Phase 0 RFP intake, and Phase 1 rendering ingestion on top.

## 2. Scope

**In scope (locked):**
1. Parser: reads Brief.md + Worksheet.xlsx + rendering folders + voice presets + boilerplate library.
2. Composer: builds slide plan (auto with AE override) + per-tier itemized pricing structure.
3. Renderer: produces 1 main proposal PDF + N per-tier itemized pricing PDFs + Coverage Report.
4. Validation: blocking errors + warnings (including a "sniff test" for sloppy customer-facing copy).
5. Versioned output directory + layout-version pin per project (cosmetic-drift protection).
6. Voice presets (4) + boilerplate library (6 files).
7. Riverside fixture migration: Project Brief + 3 new worksheet columns drafted, end-to-end test passes.
8. AE-facing surface: CLI for local dev + skill.md for Claude Desktop.

**Explicitly out of scope (deferred to Plan 4+):**
- Canva Bulk Create CSV
- Diff-mode regeneration (full version with `dependency_map.yaml`)
- Layout snapshot copying (only version-header pin shipped in Plan 3)
- Phase 0 RFP intake (`analyze_rfp.py`)
- Phase 1 rendering ingestion (`ingest_renderings.py`)
- Checkpoint mode (per-slide review-and-approve)
- Polish-via-script (polish stays in chat workflow per §10)
- Project archetypes beyond holiday/seasonal commercial decor
- Spanish-language output
- Multi-decision-maker signature blocks

## 3. Architecture

Three-stage pipeline. Each stage is its own module with one documented contract between it and the next.

```
                   ┌──────────────────────────────────────────────────┐
                   │          skill_assets/proposal_build/            │
                   │                                                  │
project folder ──▶ │ parser/   (Brief.md + Worksheet.xlsx +           │
                   │            renderings/ + voice + boilerplate)    │
                   │      │                                           │
                   │      ▼                                           │
                   │ models.py ◀── ProjectModel (typed dataclass)     │
                   │      │                                           │
                   │      ▼                                           │
                   │ composer/ (decides slide_plan, builds            │
                   │            one context dict per slide)           │
                   │      │                                           │
                   │      ▼ list[(layout_name, ctx)]                  │
                   │      ▼                                           │
                   │ renderer/ (Jinja2 + WeasyPrint;                  │
                   │            proposal PDF + N pricing PDFs +       │
                   │            coverage_report.md + layout_pin.json) │
                   │      │                                           │
                   │      ▼                                           │
                   │ cli.py    (entrypoint; arg parsing, paths, exit) │
                   └──────────────────────────────────────────────────┘
                            │
                            ▼
                  03 - Scope & Pricing/<latest PDFs>
                  04 - Process & Notes/coverage_report.md
                  04 - Process & Notes/layout_pin.json
                  04 - Process & Notes/runs/<timestamp>/<all artefacts>
```

**Module layout:**

```
skill_assets/proposal_build/
├── __init__.py
├── cli.py             ← `python -m proposal_build generate <project_dir>`
├── models.py          ← ProjectModel + supporting dataclasses (the contract)
├── parser/
│   ├── __init__.py
│   ├── brief.py       ← Brief.md → frontmatter dict + section bodies
│   ├── worksheet.py   ← Worksheet.xlsx → list[LineItem] + tier totals
│   ├── renderings.py  ← walks 02 - Renderings/*; resolves filenames to paths
│   ├── voice.py       ← loads voice preset, fills Brief blanks
│   ├── boilerplate.py ← loads boilerplate, fills remaining blanks
│   └── validate.py    ← runs all blocking + warning checks; emits ValidationResult
├── composer/
│   ├── __init__.py
│   ├── slide_plan.py  ← zone-count rules + Brief-override merge → list of (layout, ctx)
│   ├── pricing.py     ← per-tier itemized pricing → ItemizedPricingDoc instances
│   └── ctx_builders.py ← one builder function per layout: build_cover(model) → ctx, etc.
└── renderer/
    ├── __init__.py
    ├── pdf.py         ← Jinja2 + WeasyPrint; assembles N HTMLs → 1 PDF
    ├── pricing_pdf.py ← itemized pricing layout(s) → tier PDFs
    └── report.py      ← writes coverage_report.md + layout_pin.json
```

**Key contract:** `models.ProjectModel` is a frozen dataclass that **is the same shape the existing Plan-2-prime fixtures already produce**. The Composer's job is to emit `list[(layout_name: str, context: dict)]` — exactly what `tests/test_layouts.py` already feeds to `render_layout()`. This means:

- Existing 15-layout test infrastructure keeps passing without modification.
- Composer tests assert "given this ProjectModel, expect this list of (layout, ctx) tuples" — pure functions, no I/O.
- Renderer tests assert "given this list of (layout, ctx) tuples, the PDF has N pages and embeds Roboto + Poppins" — independent of parsing.
- Parser tests assert "given this Brief.md + this Worksheet.xlsx, expect this ProjectModel" — independent of rendering.

**Architectural rule (locked):** the Renderer never sees the Brief or Worksheet directly. It only ever sees context dicts. Polish, voice fill, boilerplate fill, validation, slide-plan logic — none of it can leak into rendering as a hidden side effect. Same input → same output, every time.

## 4. `Project Brief.md` schema

YAML frontmatter for project metadata + structured zones, prose markdown sections for narrative.

```yaml
---
# Client & project
client_company: "Riverside County Transportation Commission (RCTC)"
client_short:   "RCTC METROLINK"          # tracked-caps in footer
project_name:   "Riverside MetroLink"
project_short:  "MetroLink"
project_subtitle: "Six-Station Civic Holiday Program"
project_year: 2026
proposal_type: "Holiday Proposal"         # default; overrides for Lunar New Year, Lighting Refresh, etc.

# Presenter
presenter_name:  "Jonathan Yang"
presenter_title: "Account Executive"
presenter_email: "jonathan@st-nicks.com"
presenter_phone: "(562) 438-0017"
proposal_date:   "2026-05-12"             # ISO; rendered as "May 12, 2026"

# Schedule (only go_live required; rest auto-derive if blank)
go_live: "2026-11-20"
season_end: "2027-01-05"
fabrication_lock: ""                      # blank → go_live − 90d
signing_deadline: "2026-10-30"            # blank → go_live − 21d

# Tone & creative
voice: "civic"                            # civic | destination-retail | corporate | hospitality
recommended_tier: "enhanced"              # essential | enhanced | signature
design_phrase: "Holiday Express."         # period intentional
pricing_format: "tiered"                  # tiered | single

# Image selections (filename in 02 - Renderings/{Base Scope|Enhancements}/)
cover_image:           "Wreath - Brick Column Night.jpg"
creative_vision_hero:  "Pole Banner Artwork - Holiday Express 01.jpg"
case_study:            "long_beach_transit"   # case_study .md id, or "skip"
case_study_hero:       "Evening Lighting - Station Awning 01.png"

# Zones (1–10ish; flags drive layout selection)
zones:
  - num: "01"
    name: "Downtown Riverside"
    subtitle: "The flagship station — civic centerpiece."
    flags: [flagship]                          # flagship → own slide; signature → fullbleed
    hero_image: "Walk-Through Ornament - Warm White.png"
    bullets:
      - "Custom-fabricated wreaths at every entrance"
      - "Full-canopy garland across the platform overhang"
      - "Pole banner program (8 poles)"
      - "Lighted walk-through arch at plaza forecourt"
      - "Evening lighting program — platform + awning + curb-edge"
  - num: "02"
    name: "La Sierra"
    subtitle: "First park-and-ride stop — community gateway."
    hero_image: "Wreaths - Station Entrance 01.png"
    bullets:
      - "Wreaths at primary entrance"
      - "Pole banner program (4 poles)"
      - "Lighted accent at platform sign"
  # ... 4 more zones ...

# Slide plan override (optional; composer auto-derives if absent)
# slide_plan:
#   - {layout: zone_solo_fullbleed, zones: ["Downtown Riverside"]}
#   - {layout: zone_2up, zones: ["La Sierra", "Pedley"]}
---

## Creative Direction
A civic-scale holiday aesthetic that turns the MetroLink line itself into the
holiday gesture. Wreaths and garlands frame each station entrance like a
ceremonial gateway; evening lighting turns the platforms themselves into
destinations after sundown.

## Customer Goals
- Establish RCTC's MetroLink line as a regional holiday destination
- Drive non-transit foot traffic to Downtown Riverside
- Position the County as a leader in civic seasonal programming

## Customer Constraints
- All decor must clear MetroLink overhead catenary safety envelope
- Install and removal outside revenue service hours
- Materials must withstand winter Santa Ana wind events

## Success Criteria
- Measurable increase in evening visitors during the program window
- Local press and social media coverage of the activation
- Zero MetroLink operational disruptions during install/strike

## What You're Approving
The 2026 Riverside MetroLink Holiday Program — six stations from Downtown
Riverside through Perris-Downtown, live Nov 20, 2026 through Jan 5, 2027,
at the tier and add-ons you select on the Investment page.
```

**Optional override blocks** (the AE adds these to override voice/boilerplate defaults):

```markdown
## Pillars       (default: from voice preset)
## Phases        (default: from voice preset)
## Scope Includes (default: from boilerplate)
## Add-Ons       (omit entirely → Scope card hides the add-ons column)
## Term Panels   (default: from boilerplate; per-key override allowed via term_panel_overrides)
```

**Parser rules:**

1. **Blank or absent field → layered fill.** Composer logs every fill in the Coverage Report.
2. **Image filenames resolve across both `Base Scope/` and `Enhancements/`.** Ambiguous match (file with same name in both) = blocking error. No match = blocking error.
3. **`flags:` per zone:** `flagship` (gets its own zone_solo slide, never grouped) and `signature` (gets the dark-bg `zone_solo_fullbleed` treatment — at most one zone per project carries this).
4. **`slide_plan:` overrides composer arrangement entirely** when present. Composer validates that every zone is named exactly once and every layout is real.
5. **`pricing_format: single`** suppresses the tier selector on the Investment slide and produces only one Itemized Pricing PDF (the recommended tier).

## 5. `Scope Worksheet.xlsx` schema

The existing 10 columns retained. **Three new columns added**:

| Column | Required | Drives |
|---|---|---|
| **Customer-Facing Description** | Yes for any row in any tier | Row label on the Itemized Pricing PDF. (NOT zone-slide bullets — those come from Brief.) |
| **Zone** | Yes for any row in any tier | Coverage cross-check. Value is either an exact zone name from Brief, or `*` for cross-program items (canopy lighting, banners, perimeter garland). |
| **Tiers** | Yes for any row in any tier | Comma-separated subset of `{Essential, Enhanced, Signature}`. Drives per-tier Itemized Pricing filtering, Investment slide tier prices, and substitution semantics. |

**Substitutions** are expressed via Tiers membership. Example from Riverside: line #11 (Traditional Tree) = `Essential, Enhanced`; E6 (Spiral LED Tree) = `Signature`. Together they describe "Spiral LED replaces Traditional in Signature tier." No separate substitution column.

**Parser locates data tables by header-row detection.** The Riverside worksheet has title rows, a summary block, two data tables (Base Scope, Optional Enhancements), a TIER SCENARIOS block, and a LEGEND block — all in one sheet. Parser scans top-to-bottom looking for header rows matching `# | Item | Description / Location | …` (now extended with the 3 new columns). Anything between a header row and the next blank row or summary row is data. The two tables are distinguished by the `#` column: numeric (`1`–`N`) → base, `E\d+` → enhancements.

**Tier scenario totals are validated, not load-bearing.** The Investment slide's tier prices come from summing per-line `Tiers` membership, not from the worksheet's TIER SCENARIOS block. The TIER SCENARIOS block (if present) is read and **compared** to the per-line math; mismatch is a **warning** in the Coverage Report, not a blocking error. Drift >5% escalates the warning to suggest reconciliation.

**Cross-program items (`Zone: *`).** Coverage check counts these as "applicable to all zones." A zone with zero direct items + zero `*` items gets a warning. A zone with direct items but bullet count diverges by >2 also gets a warning.

## 6. Composer rules

**The deck is a fixed-order pipeline with a variable zone block:**

```
Cover → Executive Summary → Our Understanding → Creative Vision
       → [zone block — composer-arranged]
       → Scope of Work
       → [Case Study, if case_study != "skip"]
       → Investment
       → Terms & Next Steps
       → Sign-off
       → About St. Nick's
```

Page numbers and `page_total` are computed by Composer once the final slide list is known.

### 6.1 Zone block — auto-arrange algorithm

Triggered when no `slide_plan:` override is present in the Brief.

```
N = number of zones declared in Brief
flagships = zones where flags include 'flagship'
signature = zone where flags include 'signature'  (≤1; blocking error if >1)

if N ≤ 3:
    # Small project: every zone gets its own slide, declared order preserved
    for z in zones (declared order):
        emit ("zone_solo_fullbleed" if z is signature else "zone_solo", z)

elif N ≥ 4:
    # Large project: prepend index, soloed zones first, then grouped
    emit ("zone_index", all zones in declared order)
    for z in flagships ∪ {signature} (declared order, dedup):
        emit ("zone_solo_fullbleed" if z is signature else "zone_solo", z)
    grouped = zones not yet emitted
    for chunk in pick_grouping(len(grouped)):
        emit (f"zone_{len(chunk)}up", chunk)   # chunks consume from grouped in declared order
```

### 6.2 `pick_grouping(n)` — chunks zones into 2-ups and 3-ups, smaller first

| n | chunks | output |
|---|---|---|
| 0 | `[]` | (nothing) |
| 1 | `[1]` | 1× zone_solo |
| 2 | `[2]` | 1× zone_2up |
| 3 | `[3]` | 1× zone_3up |
| 4 | `[2, 2]` | 2× zone_2up |
| 5 | `[2, 3]` | 1× zone_2up + 1× zone_3up |
| 6 | `[3, 3]` | 2× zone_3up |
| 7 | `[2, 2, 3]` | 2× zone_2up + 1× zone_3up |
| 8 | `[2, 3, 3]` | 1× zone_2up + 2× zone_3up |
| 9+ | greedy 3s with leading 2-pair when `n % 3 == 1` to avoid orphan 1s | … |

### 6.3 Verification against Plan-2-prime fixtures

- **Pier 39 (N=3, Bay Terrace=signature):** → `zone_solo`, `zone_solo`, `zone_solo_fullbleed` — matches `tests/fixtures/pier_39.py` exactly.
- **Riverside (N=6, Downtown=flagship, no signature):** → `zone_index`, `zone_solo` (Downtown), `zone_2up` (La Sierra + Pedley), `zone_3up` (Hunter Park + Moreno Valley + Perris) — matches `tests/fixtures/riverside.py` exactly.

### 6.4 AE overrides

```yaml
# Per-zone override — one zone's layout differs from auto
zones:
  - num: "01"
    name: "Downtown Riverside"
    layout: zone_solo_fullbleed   # force fullbleed for this zone

# Whole-program override — composer disables auto entirely
slide_plan:
  - {layout: zone_solo_fullbleed, zones: ["Downtown Riverside"]}
  - {layout: zone_2up,            zones: ["La Sierra", "Pedley"]}
  - {layout: zone_3up,            zones: ["Hunter Park", "Moreno Valley", "Perris"]}
```

Composer validates: every zone in Brief appears exactly once in the override; every layout name is real; chunk sizes match layout (`zone_2up` requires exactly 2 zones).

### 6.5 Per-tier Itemized Pricing composition

Driven by `pricing_format:` + `Tiers` column.

- `pricing_format: tiered` → produces 3 PDFs: `Itemized Pricing — Essential.pdf`, `… Enhanced.pdf`, `… Signature.pdf`. Each contains worksheet rows where its tier appears in the `Tiers` column.
- `pricing_format: single` → produces 1 PDF: `Itemized Pricing — <recommended_tier>.pdf` only.
- Each PDF is the 2-page master format:
  - **Page 1:** header band + client/project/tier/total/date metadata panel + grouped item table (Base Scope rows above, Optional Enhancements rows below) with `Customer-Facing Description` as the row label, qty/unit/amount columns, group subtotals, big tier total at bottom.
  - **Page 2:** payment schedule (from boilerplate or Brief override) + multi-year partnership savings table (computed from the tier total + partnership_discounts) + terms summary (from boilerplate).

The Investment slide tier prices come from the same per-line tier sums — guaranteed consistent with the supplements because both read the same `Tiers` column math.

## 7. Renderer outputs, file naming, run versioning, layout pin

### 7.1 Where each artifact lands

```
Projects/<Project>/
├── 03 - Scope & Pricing/                    ← what the AE sends to the customer
│   ├── <Project> - <Year> <Proposal Type>.pdf
│   ├── <Project> - <Year> Itemized Pricing - Essential.pdf
│   ├── <Project> - <Year> Itemized Pricing - Enhanced.pdf
│   └── <Project> - <Year> Itemized Pricing - Signature.pdf
└── 04 - Process & Notes/                    ← internal generation history
    ├── coverage_report.md                   ← latest
    ├── layout_pin.json
    └── runs/
        ├── 2026-05-12_142301/               ← every prior generation preserved
        │   ├── <Project> - <Year> <Proposal Type>.pdf
        │   ├── <Project> - <Year> Itemized Pricing - Essential.pdf
        │   ├── ... (all PDFs from this run)
        │   └── coverage_report.md
        └── 2026-05-12_154822/
            └── ...
```

The PDFs in `03 - Scope & Pricing/` are **always the latest run** — every `generate` overwrites them with copies from the new run dir. The `04/runs/` dir is the immutable history; nothing there gets overwritten.

### 7.2 File naming

Pattern: `{project_name} - {project_year} {proposal_type}.pdf` and `{project_name} - {project_year} Itemized Pricing - {Tier}.pdf`. `proposal_type` defaults to `"Holiday Proposal"` if absent; this allows Lunar New Year, Lighting Refresh, Spring Activation projects to ship without code changes. The footer crumb on every slide also reads `{proposal_type | upper}` so it stays in sync.

### 7.3 Run timestamp format

`YYYY-MM-DD_HHMMSS` (24-hour, local time). Sortable, no spaces, unambiguous on macOS. Generated once per `generate` invocation.

### 7.4 Layout pin

`04 - Process & Notes/layout_pin.json`:

```json
{
  "first_run":  "2026-05-12T14:23:01-07:00",
  "last_run":   "2026-05-15T09:14:32-07:00",
  "layouts": {
    "cover.html":               "2026-05-03",
    "exec_summary.html":        "2026-05-03",
    "understanding.html":       "2026-05-03",
    "creative_vision.html":     "2026-05-03",
    "zone_index.html":          "2026-05-03",
    "zone_solo.html":           "2026-05-03",
    "zone_solo_fullbleed.html": "2026-05-03",
    "zone_2up.html":            "2026-05-03",
    "zone_3up.html":            "2026-05-03",
    "scope.html":               "2026-05-03",
    "case_study.html":          "2026-05-03",
    "investment.html":          "2026-05-03",
    "terms.html":               "2026-05-03",
    "sign_off.html":            "2026-05-03",
    "about.html":               "2026-05-03",
    "itemized_pricing.html":    "2026-05-12"
  }
}
```

**Pin behavior:**

- **First run:** reads `<!-- layout-version: YYYY-MM-DD -->` header from each rendered layout, writes the pin.
- **Subsequent runs:** compares current layout headers to the pin. If all match → render with current files. If any differ → blocking error with a clear diagnostic ("zone_solo.html version is 2026-06-15 on disk but pinned to 2026-05-03 — pass `--use-latest-layouts` to refresh, or revert layout to pinned version").
- **`--use-latest-layouts`** (CLI flag, or `use_latest_layouts: true` in chat with Claude Desktop): re-reads current versions, updates the pin, renders with current files. Logged prominently in the Coverage Report.

**Trust assumption:** layout authors bump the `<!-- layout-version: -->` header whenever they change a layout file. Plan 4+ may harden this by snapshotting layout files into each run dir.

### 7.5 Pre-existing files in `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/`

Pre-Plan-3 PDFs and PPTXs (`Riverside MetroLink - 2026 Holiday Proposal.pdf`, `.pptx`) move to `04 - Process & Notes/pre_plan3_archive/` before first Plan 3 run, preserving them as historical comparison artifacts.

## 8. Validation rules + Coverage Report

Two validation passes run on every `generate` invocation, before any rendering: a **hard pass** producing blocking errors, and a **soft pass** producing warnings. Both write to a single `coverage_report.md`.

### 8.1 Blocking errors (refuse to render)

| # | Check |
|---|---|
| 1 | `Project Brief.md` exists at `04 - Process & Notes/Project Brief.md` |
| 2 | All required Brief fields present (client_company, project_name, project_year, presenter_name, voice, recommended_tier, pricing_format, cover_image, plus zones list non-empty) |
| 3 | Worksheet exists at `03 - Scope & Pricing/<project_name> - Scope Worksheet.xlsx` |
| 4 | Worksheet has all 3 new columns (Customer-Facing Description, Zone, Tiers) |
| 5 | Every line item with non-empty Tiers has non-empty Customer-Facing Description |
| 6 | Every line item with non-empty Tiers has non-empty Zone (or `*`) |
| 7 | Every Tiers value is a subset of `{Essential, Enhanced, Signature}` |
| 8 | All `cover_image`, `creative_vision_hero`, per-zone `hero_image`, `case_study_hero` resolve to existing files in `02 - Renderings/` |
| 9 | No filename ambiguity (same name in both Base Scope/ and Enhancements/) |
| 10 | At most one zone has `signature` flag |
| 11 | If `slide_plan:` override present: every Brief zone appears exactly once; every layout name is real; chunk sizes match layout |
| 12 | If `case_study: != "skip"`: case study .md file exists at `skill_assets/case_studies/{case_study}.md`; `case_study_hero` is set |
| 13 | Layout pin (if exists): on-disk versions match pinned versions, OR `--use-latest-layouts` was passed |

### 8.2 Warnings (render anyway)

| # | Check |
|---|---|
| W1 | Renderings in `Base Scope/` or `Enhancements/` not referenced by any field |
| W2 | Zone in Brief has no priced line items (no row with that Zone, no `*` rows) |
| W3 | Zone in Brief has direct items but bullet count diverges by >2 |
| W4 | Tier scenarios block in worksheet diverges from per-line tier sums (warn at any drift; escalate at >5%) |
| W5 | Customer-Facing Description **identical** to internal `Description / Location` cell |
| W6 | C-F-D contains internal-jargon markers: dimensions like `\d+"`, units mid-sentence `\d+\s*(LF\|ea\|LS)`, `TBD`, "anchoring", formula text `\d+\s*×\s*\d+` |
| W7 | C-F-D fewer than 4 words |
| W8 | Brief field blank, filled by voice/boilerplate (logged for transparency) |
| W9 | Composer auto-arranged slide plan — review reminder, AE override available |

### 8.3 Coverage Report format

`04 - Process & Notes/coverage_report.md`:

```markdown
# Coverage Report — Riverside MetroLink
Generated: 2026-05-12 14:23:01 (run dir: 04 - Process & Notes/runs/2026-05-12_142301/)
Status: ✅ PASSED — proposal generated.

## Summary
- Worksheet line items: 25 (12 base + 13 enhancements)
  ✓ 25 mapped to a tier
  ✓ 25 have Customer-Facing Description
  ✓ 25 have Zone assignment
- Zones: 6 declared in Brief
  ✓ Downtown Riverside (5 priced items, 5 bullets, hero image OK)
  ✓ La Sierra (0 direct + 3 cross-program *, 3 bullets, hero image OK)
  ⚠ Pedley (1 priced item, 2 bullets — see W3)
  ...
- Renderings: 26 on disk
  ✓ 7 wired into hero_image fields
  ⚠ 2 not referenced anywhere (see W1)
- Brief fills:
  ⚠ Pillars filled from voice preset 'civic' (see W8)
  ⚠ After-approval steps filled from boilerplate
- Tier totals (per-line math):
  Essential:  $88,906   (matches scenarios block)
  Enhanced:  $166,643   (matches)
  Signature: $200,249   (matches)

## Slide Plan (auto)
1. Cover                                       layout: cover                v2026-05-03
2. Executive Summary                           layout: exec_summary         v2026-05-03
...

## Itemized Pricing PDFs
- Essential ($88,906) — 12 line items
- Enhanced ($166,643) — 22 line items
- Signature ($200,249) — 21 line items (Traditional Tree replaced by Spiral LED)

## Warnings
W1 — Unused renderings (2):
  • Lighted Bell Display - Scene.png (in Enhancements/)
  • Walk-Through Display - Lighted Gift Box.png (in Enhancements/)
W3 — Zone bullet/item count divergence:
  • Pedley: 1 priced item, 2 bullets — confirm intentional
W6 — C-F-D internal-jargon markers:
  • Row #11 contains "18 ft commercial PVC tree on steel frame"
  → Run polish chat in Claude Desktop.
W8 — Brief fields filled from defaults:
  • Pillars: filled from voice preset 'civic'
  • after_approval_steps: filled from boilerplate

## Outputs Written
✓ 03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal.pdf
✓ 03 - Scope & Pricing/Riverside MetroLink - 2026 Itemized Pricing - Essential.pdf
✓ 03 - Scope & Pricing/Riverside MetroLink - 2026 Itemized Pricing - Enhanced.pdf
✓ 03 - Scope & Pricing/Riverside MetroLink - 2026 Itemized Pricing - Signature.pdf
```

On blocking failures the status flips to `❌ BLOCKED` and the report lists every blocking error with row numbers, file paths, and (where possible) a suggested fix. The "Slide Plan", "Itemized Pricing PDFs", and "Outputs Written" sections are omitted.

## 9. Voice presets + boilerplate library

### 9.1 Voice presets (`skill_assets/voice_presets/{voice}.md`)

Four files: `civic`, `destination-retail`, `corporate`, `hospitality`. Each supplies:

1. **Defaults** for things the Brief leaves blank (pillars, phases, after-approval steps, sign-off recap pattern, default case study).
2. **Polish examples** — 5 before/after pairs of Customer-Facing Description text. **These are static reference text the AE/owner authors and approves once.** Claude reads them at runtime when polishing new AE input, mimicking the voice pattern. The polish chat (§9.3) is the consumer.
3. **Voice rules** — concrete dos and don'ts for the polish chat to honor.

Example shape (`civic.md`):

```yaml
---
name: Civic
description: Confident public-investment language. For municipal, transit, and
             government-adjacent projects.
default_case_study: long_beach_transit
default_pillars:
  - title: "Civic Pride"
    body: "A holiday program that elevates {project_name} as a destination, not just a transit stop."
  - {title: "Operational Discipline", body: "..."}
  - {title: "Repeatable Investment",  body: "..."}
default_phases:
  - {label: "WELCOME",  body: "..."}
  - {label: "JOURNEY",  body: "..."}
  - {label: "ARRIVAL",  body: "..."}
default_after_approval_steps: ["Kickoff call within 48 hrs", ...]
default_sign_off_recap_pattern: "The {project_year} {project_name} {proposal_type} — ..."
---

# Voice: Civic
## When to use
## Voice rules
## Polish examples (Before → After)
**1.** "Lighted garlands really make the gates look great"
   → "Lit garland on the perimeter gates frames the property edge with warm-white evening glow."
... (5 pairs total)
```

### 9.2 Boilerplate library (`skill_assets/boilerplate/`)

Six files lifted from existing master content. Per-file overridable from Brief.md.

| File | Purpose | Used by |
|---|---|---|
| `company_facts.md` | Founded year, legal name, license #, insurance limits, team counts, venues served | About slide |
| `team.md` | Team roster (name + role) | About slide |
| `contact_strip.md` | One-line contact line with `{project_year}` placeholder | About slide bottom red strip |
| `terms_panels.md` | 4 default term panel bodies — Brief can override any one without overriding all 4 | Terms slide + Itemized Pricing page 2 |
| `scope_inclusions.md` | Default "what's included" bullet list | Scope slide (left card) |
| `partnership_discounts.md` | 3-tier partnership discount table (2-yr 4%, 3-yr 6%, 5-yr 9%) | Investment slide + Itemized Pricing page 2 |

### 9.3 Polish chat (workflow, not code)

Polish is a **chat affordance**, not a Python module. The skill.md tells Claude:

- When AE asks to "polish the worksheet", read the worksheet's Customer-Facing Description column.
- Read the voice preset matching the project's `voice:` field. The 5 reference pairs are calibration.
- For each row, suggest a polished version following the voice pattern.
- AE accepts/edits/rejects per row.
- **Polished text writes back to the .xlsx cell** (using openpyxl). The .xlsx is the source of truth at generation time.
- Next `generate` run reads the polished cells.

The Python pipeline never sees the polish step. It only sees the worksheet cells as they are at generate time. Same input → same output, every time.

### 9.4 Placeholder substitution

Voice presets and boilerplate files use simple `{key}` placeholders, not Jinja templating. Parser substitutes from a known key set:

| Placeholder | Source |
|---|---|
| `{project_name}`, `{project_short}`, `{project_year}`, `{client_short}`, `{proposal_type}` | Brief frontmatter |
| `{go_live}`, `{season_end}`, `{fabrication_lock}`, `{signing_deadline}`, `{proposal_date}` | Brief or auto-derived (ISO format) |
| `{go_live_long}`, `{season_end_long}`, `{fabrication_lock_long}`, `{signing_deadline_long}`, `{proposal_date_long}` | Same dates rendered as "Nov 20, 2026" |
| `{next_year}` | `project_year + 1` |
| `{fabrication_lock_minus_60d}` | Computed offset rendered long-form |
| `{zone_summary}` | Composer-built one-liner |

Substitution happens once during the layered fill in Parser. Unknown placeholder = blocking error.

## 10. Test plan

Three test surfaces matching the three pipeline stages, plus an end-to-end smoke test on Riverside.

### 10.1 Existing tests stay green (no modifications)

`tests/test_repo_structure.py`, `tests/test_brand_css.py`, `tests/test_fonts_present.py`, `tests/test_base_html.py`, `tests/test_layouts.py`. The Plan-2-prime fixtures stay unchanged because they are exactly the dict shape Composer emits.

### 10.2 New tests added in Plan 3

| File | Coverage |
|---|---|
| `tests/test_parser_brief.py` | Required fields; signature count; date auto-derive; image filename resolution; slide_plan override validation |
| `tests/test_parser_worksheet.py` | 3-column requirement; table detection; tier membership; `*` zone wildcard; tier scenarios cross-check; substitution semantics |
| `tests/test_parser_voice_boilerplate.py` | Voice preset loading + fill; placeholder substitution; Brief overrides win; partial term-panel override; layered fill order |
| `tests/test_parser_validate.py` | Sniff test (W5/W6/W7); zone coverage warnings (W1/W2/W3) |
| `tests/test_composer_slide_plan.py` | Auto-arrange table (n=0..10); Pier 39 + Riverside fixture matches; slide_plan override; pick_grouping table |
| `tests/test_composer_pricing.py` | Per-tier filtering; pricing_format single vs tiered; partnership savings computation |
| `tests/test_renderer_outputs.py` | Run dir created; latest copies in 03/; layout pin written/blocked/updated; coverage report success/block paths |
| `tests/test_e2e_riverside.py` | Full generation against real migrated Riverside files. Asserts 4 PDFs produced, page counts, font embedding, layout pin file present |

### 10.3 Test fixtures used

- `tests/fixtures/briefs/` (new) — small Brief.md files for parser unit tests
- `tests/fixtures/worksheets/` (new) — small .xlsx files for worksheet parser unit tests
- The existing `tests/fixtures/pier_39.py` and `tests/fixtures/riverside.py` stay untouched — they remain the Plan-2-prime layout test fixtures.
- The new e2e test consumes the **real** migrated Riverside files

### 10.4 Coverage philosophy

Parser and Composer tests are pure unit tests (no Jinja, no PDF). Renderer tests assert structural properties of generated PDFs (page count, font embedding, file existence) but don't pixel-diff — visual review stays the AE/owner job. The e2e Riverside test is the one integration test that ties everything together.

Estimated test count delta: ~25 existing + ~40 new = ~65 total after Plan 3.

## 11. Performance expectations

Realistic per-project AE time post-renderings, assuming Phase 0 pricing is already complete (separate ~45–90 min that doesn't change) and Plan 1 (vision-driven rendering ingestion) hasn't shipped yet:

| Step | First proposal | Steady state (5+ proposals in) |
|---|---|---|
| 1. Drop renderings into folders + rename | 15 min | 10 min |
| 2. Migrate worksheet — fill 3 new columns (with polish chat) | 50 min | 30 min |
| 3. Author `Project Brief.md` | 60 min | 30–40 min |
| 4. Run `generate`, review Coverage Report | 5 min | 5 min |
| 5. Polish iteration (review PDF, request fixes via chat, regen) | 30 min | 15 min |
| 6. Final review + send | 10 min | 10 min |
| **TOTAL** | **~2h 50m** | **~1h 40m** |

Compared against the prior process (find-and-replace from another deck, slide-by-slide visual cleanup, missed-rendering rework: ~6–9 hours per proposal post-pricing), Plan 3 cuts the post-pricing time roughly **3–5×**. The win compounds because:

- No slide-by-slide cleanup (the worst hours go to zero).
- Output consistency — every proposal is brand-correct without effort.
- Coverage check catches missed renderings before customer review.
- Polish chat keeps copy in voice without re-writing the same drafts in different proposals.

Where time will keep dropping in later plans:

- **Plan 1 (Phase 1 rendering ingestion)** — vision-driven file renaming → step 1 drops from 10 min → ~5 min.
- **Plan 4+ (Phase 0 RFP intake)** — Claude drafts Worksheet line items + Brief skeleton from RFP → combined steps 2+3 drop from 60–80 min → 30–40 min.
- **Diff-mode regeneration (Plan 5+)** — customer revision rounds (typical 2–3 per proposal) only regenerate changed slides → step 5 polish iteration drops further.

Cautions:
- First proposal of a new project type runs slower (AE figuring out zones, voice, copy patterns).
- Pricing isn't faster — Plan 3 doesn't help Phase 0.
- Polish chat quality depends on voice preset quality. ~30 min per voice of owner review post-Plan-3 is the calibration cost.

## 12. Riverside fixture migration + content shipped

### 12.1 Riverside project folder updates

`Projects/Downtown Riverside Metro Link/`:

1. **New: `04 - Process & Notes/Project Brief.md`** — full Brief authored to match the Riverside fixture's content. 6 zones (Downtown Riverside flagship + 5 stations), `voice: civic`, `recommended_tier: enhanced`, `pricing_format: tiered`. Hero image filenames reference the real on-disk renderings the Plan-2-prime fixture already wires.
2. **Migrated: `03 - Scope & Pricing/Riverside MetroLink - Scope Worksheet.xlsx`** — three new columns added, all 25 rows filled. Customer-Facing Description drafted by Claude in civic voice; Zone column mostly `*` for cross-program items with specific assignments for flagship-station-only items; Tiers column reflects substitution semantics (Traditional Tree #11 = `Essential, Enhanced`; Spiral LED E6 = `Signature`).
3. **Archive: pre-Plan-3 outputs** — existing `Riverside MetroLink - 2026 Holiday Proposal.pdf` and `.pptx` move to `04 - Process & Notes/pre_plan3_archive/`.

### 12.2 Blank template project updates

`Projects/_template_project/`:

1. **`04 - Process & Notes/Project Brief.md`** — heavily commented schema template with placeholder values + inline comments + example values from Riverside.
2. **`03 - Scope & Pricing/[Client] - Scope Worksheet.xlsx`** — same migration: 3 new columns added; one example row pre-filled to demonstrate.

### 12.3 New files in `skill_assets/`

1. **`skill_assets/proposal_build/`** — entire Python package (~1,500–2,500 lines).
2. **`skill_assets/voice_presets/{voice}.md`** — 4 files (`civic`, `destination-retail`, `corporate`, `hospitality`). Drafts authored by Claude; voice rules + 5 polish examples per file reviewed and refined by owner. Estimated ~30 min owner review per voice.
3. **`skill_assets/boilerplate/`** — 6 files lifted verbatim from existing master content.
4. **`skill_assets/case_studies/`** — 3 files: `long_beach_transit.md` (from Riverside fixture content), `oregon_zoo.md` and `pier_39.md` (from Pier 39 fixture content). Each: YAML frontmatter (`name`, `year`, `voice_tag`) + 3 prose sections (`## Challenge`, `## Approach`, `## Outcome`).
5. **`skill_assets/layouts/itemized_pricing.html`** — new layout file for the Itemized Pricing PDF (two-page Jinja template using existing `brand.css`, with `<!-- layout-version: 2026-05-12 -->` header).
6. **`skill_assets/skill.md`** — Claude Desktop skill manifest (state detection, Phase 2 invocation pattern, polish chat workflow, Coverage Report interpretation).

### 12.4 AE-facing SOP

`AE_SOP.md` at repo root covering Phase 2 only in this plan: starting a new proposal, the conversation flow with Claude, interpreting the Coverage Report, when to use polish chat, customizing voice presets. Grows as Plans 4+ ship.

### 12.5 Pre-flight verification (the e2e gate)

Plan 3 is "done" when:

```bash
$ pytest -v
====== 65+ tests passed ======

$ python -m proposal_build generate "Projects/Downtown Riverside Metro Link"
✅ Generation complete.
   Coverage Report: Projects/Downtown Riverside Metro Link/04 - Process & Notes/coverage_report.md
   Outputs:
     • Riverside MetroLink - 2026 Holiday Proposal.pdf (14 pages)
     • Riverside MetroLink - 2026 Itemized Pricing - Essential.pdf (2 pages)
     • Riverside MetroLink - 2026 Itemized Pricing - Enhanced.pdf (2 pages)
     • Riverside MetroLink - 2026 Itemized Pricing - Signature.pdf (2 pages)
```

Plus an **eyeball pass** comparing the 4 generated PDFs against the existing master and the Plan-2-prime layout PDFs. Anything that looks worse than the Plan-2-prime fixture-driven output is a Plan 3 bug.

## 13. Out of scope (deferred to Plan 4+)

Already enumerated in §2. Each line below maps to a likely future plan:

- **Plan 4 candidate:** Phase 0 RFP intake (`analyze_rfp.py`) — biggest workflow lift remaining.
- **Plan 5 candidate:** Diff-mode regeneration with `dependency_map.yaml` + layout snapshot copying.
- **Plan 6 candidate:** Phase 1 rendering ingestion (`ingest_renderings.py`) — vision-driven file renaming + categorization.
- **Plan 7 candidate:** Canva Bulk Create CSV emit (editable backup path).
- **Plan 8+ candidates:** Checkpoint mode; project archetypes beyond holiday/seasonal; Spanish-language output; multi-decision-maker signature blocks; Zoho CRM integration; e-signature integration.

## 14. Files added / modified summary

**Added (`skill_assets/`):**
- `proposal_build/` — full Python package (cli, models, parser/, composer/, renderer/)
- `voice_presets/civic.md`, `destination-retail.md`, `corporate.md`, `hospitality.md`
- `boilerplate/company_facts.md`, `team.md`, `contact_strip.md`, `terms_panels.md`, `scope_inclusions.md`, `partnership_discounts.md`
- `case_studies/long_beach_transit.md`, `oregon_zoo.md`, `pier_39.md`
- `layouts/itemized_pricing.html`
- `skill.md`

**Added (`Projects/`):**
- `Downtown Riverside Metro Link/04 - Process & Notes/Project Brief.md`
- `Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive/` (with the moved pre-Plan-3 PDF + PPTX)
- `_template_project/04 - Process & Notes/Project Brief.md`

**Modified:**
- `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - Scope Worksheet.xlsx` — 3 new columns added, all 25 rows filled
- `Projects/_template_project/03 - Scope & Pricing/[Client] - Scope Worksheet.xlsx` — 3 new columns added with example row
- `pyproject.toml` — add `openpyxl`, `pyyaml`, `jinja2`, `weasyprint` to dependencies (some may already be present)
- `tests/conftest.py` — add fixtures for Brief and Worksheet test inputs

**Added (`tests/`):**
- `tests/test_parser_brief.py`
- `tests/test_parser_worksheet.py`
- `tests/test_parser_voice_boilerplate.py`
- `tests/test_parser_validate.py`
- `tests/test_composer_slide_plan.py`
- `tests/test_composer_pricing.py`
- `tests/test_renderer_outputs.py`
- `tests/test_e2e_riverside.py`
- `tests/fixtures/briefs/` (small Brief.md files)
- `tests/fixtures/worksheets/` (small .xlsx files)

**Added (root):**
- `AE_SOP.md` — Phase 2 chapter only

## 15. Spec self-review

Reviewed against:
- **Placeholder scan:** no TBDs, no incomplete sections, all referenced libraries and modules defined.
- **Internal consistency:** Composer's slide-plan rules verified against existing Plan-2-prime fixtures (§6.3 confirms Pier 39 and Riverside both match). The 3 new worksheet columns drive exactly the use cases stated (§5). The layered fill order (Brief → voice → boilerplate) is consistent across §4, §9, and the test plan §10. The polish chat lives in skill.md instructions, not in Python — matches the deterministic-pipeline rule from §3.
- **Scope check:** Single-implementation-plan-sized. Five subsystems (parser, composer, renderer, voice/boilerplate, Riverside content migration) — large but cohesive. The deliberately deferred items (§13) keep this from sprawling.
- **Ambiguity check:** Schemas and field requirements are explicit (§4, §5). Layout selection algorithm has a worked table (§6.2) with verified outputs against existing fixtures. Validation rules enumerate every blocker and warning (§8.1, §8.2). File naming and paths are concrete (§7).
- **Trust assumptions documented:** Layout-version pin trusts authors to bump version headers (§7.4); polish chat trusts AE to invoke before generate; voice preset polish examples trust the authoring owner. Each is called out as a known limitation Plan 4+ may harden.
- **Realistic timing:** §11 sets owner-facing expectations (~2h 50m first proposal, ~1h 40m steady state) so the implementing model — and the owner reviewing this spec — can size effort correctly.
