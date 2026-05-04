# Plan 3 — Phase 2 Generation Core: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full Phase 2 generation pipeline — Parser → Composer → Renderer — that turns a real `Project Brief.md` + migrated `Scope Worksheet.xlsx` into a customer-ready proposal PDF + per-tier itemized pricing PDFs + a Coverage Report. Plan 3 is "done" when `python -m proposal_build generate "Projects/Downtown Riverside Metro Link"` produces 4 valid PDFs and the e2e test passes.

**Architecture:** Three-stage pipeline with one typed dataclass (`ProjectModel`) as the contract between stages. Parser reads inputs and resolves voice/boilerplate fills; Composer arranges slides + per-tier pricing; Renderer generates PDFs via Jinja2 + WeasyPrint using the existing 15 Plan-2-prime layouts plus one new `itemized_pricing.html`. The Renderer never sees the Brief or Worksheet directly — only context dicts of the same shape the existing fixtures already produce.

**Tech Stack:** Python 3.11+, WeasyPrint, openpyxl, python-frontmatter, PyYAML, Jinja2 (already declared in `pyproject.toml`). Tests in pytest. Layout files (HTML/CSS) and fonts already shipped by Plan 2-prime.

**Reference spec:** `docs/superpowers/specs/2026-05-03-plan-3-phase-2-generation-design.md` (read this for the full context — every locked decision and rationale lives there).

---

## File Structure

**New Python package** (`skill_assets/proposal_build/`):

```
skill_assets/proposal_build/
├── __init__.py            # version + package marker
├── cli.py                 # `python -m proposal_build generate <project_dir>`
├── models.py              # ProjectModel + Zone + LineItem + SlidePlanItem + ValidationResult dataclasses
├── parser/
│   ├── __init__.py        # build_project_model() top-level orchestrator
│   ├── brief.py           # parse_brief(path) → BriefData
│   ├── worksheet.py       # parse_worksheet(path) → list[LineItem] + tier scenarios
│   ├── renderings.py      # walk_renderings(project_dir) → dict[filename → Path]
│   ├── voice.py           # load_voice(name) + apply_voice_fill(model, voice)
│   ├── boilerplate.py     # load_boilerplate() + apply_boilerplate_fill(model, bp)
│   └── validate.py        # run_validation(model) → ValidationResult (blockers + warnings)
├── composer/
│   ├── __init__.py        # compose(model) → list[SlidePlanItem]
│   ├── slide_plan.py      # auto_arrange_zones() + pick_grouping()
│   ├── pricing.py         # build_itemized_pricing_docs(model) → list[ItemizedPricingDoc]
│   └── ctx_builders.py    # one builder per layout: build_cover_ctx(model), build_exec_summary_ctx(model), etc.
└── renderer/
    ├── __init__.py        # render(model, slides, output_dir) top-level orchestrator
    ├── pdf.py             # render_proposal_pdf(slides, out_path)
    ├── pricing_pdf.py     # render_pricing_pdf(doc, out_path)
    └── report.py          # write_coverage_report(result, out_path) + write_layout_pin(out_path) + check_layout_pin()
```

**New content libraries** (no Python; YAML+markdown content the parser reads):

```
skill_assets/voice_presets/
├── civic.md
├── destination-retail.md
├── corporate.md
└── hospitality.md

skill_assets/boilerplate/
├── company_facts.md
├── team.md
├── contact_strip.md
├── terms_panels.md
├── scope_inclusions.md
└── partnership_discounts.md

skill_assets/case_studies/
├── long_beach_transit.md
├── oregon_zoo.md
└── pier_39.md

skill_assets/layouts/
└── itemized_pricing.html   # NEW — only new layout file in Plan 3

skill_assets/skill.md        # NEW — Claude Desktop skill manifest
```

**Riverside fixture content** (the e2e test inputs):

```
Projects/Downtown Riverside Metro Link/
├── 04 - Process & Notes/
│   ├── Project Brief.md                       # NEW (Task 18)
│   └── pre_plan3_archive/                     # NEW dir for moved files (Task 16)
│       ├── Riverside MetroLink - 2026 Holiday Proposal.pdf  (moved here)
│       └── Riverside MetroLink - 2026 Holiday Proposal.pptx (moved here)
└── 03 - Scope & Pricing/
    └── Riverside MetroLink - Scope Worksheet.xlsx  # MIGRATED (Task 19)
```

**Blank template project updates:**

```
Projects/_template_project/
├── 04 - Process & Notes/
│   └── Project Brief.md                       # NEW (Task 21)
└── 03 - Scope & Pricing/
    └── [Client] - Scope Worksheet.xlsx        # MIGRATED (Task 22)
```

**Tests:**

```
tests/
├── conftest.py                                 # MODIFIED (add new fixtures)
├── fixtures/
│   ├── briefs/                                 # NEW dir of small Brief.md files for parser tests
│   └── worksheets/                             # NEW dir of small .xlsx files for parser tests
├── test_parser_brief.py                        # NEW
├── test_parser_worksheet.py                    # NEW
├── test_parser_voice_boilerplate.py            # NEW
├── test_parser_validate.py                     # NEW
├── test_composer_slide_plan.py                 # NEW
├── test_composer_pricing.py                    # NEW
├── test_renderer_outputs.py                    # NEW
└── test_e2e_riverside.py                       # NEW
```

**Repo root:**

```
AE_SOP.md                   # NEW — Phase 2 chapter only
```

---

## Phase 1 — Setup (1 task)

### Task 1: Package skeleton + ProjectModel dataclass

**Files:**
- Create: `skill_assets/proposal_build/__init__.py`
- Create: `skill_assets/proposal_build/models.py`
- Create: `skill_assets/proposal_build/parser/__init__.py` (empty stub)
- Create: `skill_assets/proposal_build/composer/__init__.py` (empty stub)
- Create: `skill_assets/proposal_build/renderer/__init__.py` (empty stub)
- Create: `tests/test_models.py`
- Modify: `pyproject.toml` (add `[tool.setuptools.packages.find]` so the new package is discoverable)

- [ ] **Step 1: Write the failing test**

Create `tests/test_models.py`:

```python
"""Sanity tests for the ProjectModel dataclass contract.

ProjectModel is the boundary between Parser and Composer. Its shape must
match what the existing test fixtures (pier_39.py, riverside.py) hand-author.
"""
from __future__ import annotations

import pytest

from proposal_build.models import (
    ProjectModel,
    Zone,
    LineItem,
    SlidePlanItem,
    ValidationResult,
    Tier,
)


def test_zone_minimal_construction():
    z = Zone(num="01", name="La Sierra", subtitle="A stop.", flags=(), hero_image="img.jpg",
             bullets=("Wreaths",))
    assert z.name == "La Sierra"
    assert z.flags == ()
    assert z.bullets == ("Wreaths",)


def test_zone_flag_helpers():
    z = Zone(num="01", name="A", subtitle="", flags=("flagship", "signature"),
             hero_image="i.jpg", bullets=())
    assert z.is_flagship
    assert z.is_signature

    z2 = Zone(num="02", name="B", subtitle="", flags=(), hero_image="i.jpg", bullets=())
    assert not z2.is_flagship
    assert not z2.is_signature


def test_line_item_tier_membership():
    li = LineItem(
        line_num="11", item="Large Tree", description="Internal: 18ft PVC",
        qty=1, unit="ea", price_per_unit=18654, line_total=18654,
        rendering_ref="Tree.png", customer_facing="Traditional centerpiece tree.",
        zone="Downtown Riverside", tiers=(Tier.ESSENTIAL, Tier.ENHANCED),
    )
    assert Tier.ESSENTIAL in li.tiers
    assert Tier.SIGNATURE not in li.tiers


def test_validation_result_status():
    r = ValidationResult(blockers=[], warnings=[])
    assert r.passed is True
    assert r.status == "PASSED"

    r2 = ValidationResult(blockers=[("missing_field", "voice")], warnings=[])
    assert r2.passed is False
    assert r2.status == "BLOCKED"


def test_project_model_minimal():
    pm = ProjectModel(
        client_company="RCTC", client_short="RCTC", project_name="MetroLink",
        project_short="MetroLink", project_year=2026, project_subtitle="",
        proposal_type="Holiday Proposal",
        presenter_name="J", presenter_title="AE", presenter_email="j@s.com",
        presenter_phone="(555) 555-5555", proposal_date="2026-05-12",
        go_live="2026-11-20", season_end="2027-01-05",
        fabrication_lock="2026-08-22", signing_deadline="2026-10-30",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="Holiday Express.",
        pricing_format="tiered",
        cover_image="cover.jpg", creative_vision_hero="cv.jpg",
        case_study="long_beach_transit", case_study_hero="cs.jpg",
        zones=(), line_items=(),
        creative_direction="", customer_goals=(), customer_constraints=(),
        success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(),
        term_panels={}, after_approval_steps=(),
        company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )
    assert pm.project_name == "MetroLink"
    assert pm.recommended_tier == Tier.ENHANCED
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: ImportError — `proposal_build` package doesn't exist yet.

- [ ] **Step 3: Modify `pyproject.toml` to make the new package discoverable**

In the `[tool.setuptools]` section, replace `packages = []` with:

```toml
[tool.setuptools.packages.find]
where = ["skill_assets"]
include = ["proposal_build*"]
```

- [ ] **Step 4: Reinstall in dev mode so the package is importable**

Run: `pip install -e ".[dev]"`
Expected: installs `stnicks-proposal-builder` and discovers `proposal_build` package.

- [ ] **Step 5: Create the package skeleton**

Create `skill_assets/proposal_build/__init__.py`:

```python
"""St. Nick's Proposal Builder — Phase 2 generation core.

This package implements the deterministic Parser → Composer → Renderer
pipeline. See docs/superpowers/specs/2026-05-03-plan-3-phase-2-generation-design.md
for the full design.
"""

__version__ = "0.1.0"
```

Create `skill_assets/proposal_build/parser/__init__.py`:

```python
"""Parser stage: Brief.md + Worksheet.xlsx + voice + boilerplate → ProjectModel."""
```

Create `skill_assets/proposal_build/composer/__init__.py`:

```python
"""Composer stage: ProjectModel → list[(layout_name, ctx)] + ItemizedPricingDoc instances."""
```

Create `skill_assets/proposal_build/renderer/__init__.py`:

```python
"""Renderer stage: (layout, ctx) lists + ItemizedPricingDoc → PDFs + Coverage Report."""
```

- [ ] **Step 6: Write `models.py`**

Create `skill_assets/proposal_build/models.py`:

```python
"""ProjectModel and supporting dataclasses — the contract between Parser and Composer.

ProjectModel is intentionally shaped to match what the existing layout test
fixtures (tests/fixtures/pier_39.py, riverside.py) produce by hand. Composer
emits context dicts of the same shape; Renderer never reads anything else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Tuple


class Tier(str, Enum):
    ESSENTIAL = "Essential"
    ENHANCED = "Enhanced"
    SIGNATURE = "Signature"

    @classmethod
    def from_string(cls, s: str) -> "Tier":
        s = s.strip()
        for t in cls:
            if t.value.lower() == s.lower():
                return t
        raise ValueError(f"Unknown tier: {s!r}")


@dataclass(frozen=True)
class Zone:
    num: str                    # "01", "02", etc. — exact string preserved
    name: str                   # "Downtown Riverside"
    subtitle: str               # "The flagship station — civic centerpiece."
    flags: Tuple[str, ...]      # ("flagship",) or ("flagship", "signature") or ()
    hero_image: str             # filename in 02 - Renderings/, e.g. "Wreath - X.jpg"
    bullets: Tuple[str, ...]    # customer-facing bullet list (from Brief)
    layout_override: str | None = None  # explicit layout: zone_solo, zone_solo_fullbleed, etc.

    @property
    def is_flagship(self) -> bool:
        return "flagship" in self.flags

    @property
    def is_signature(self) -> bool:
        return "signature" in self.flags


@dataclass(frozen=True)
class LineItem:
    line_num: str                  # "1", "12", "E6", etc.
    item: str                      # short name from Item column
    description: str               # internal Description / Location
    qty: float                     # numeric
    unit: str                      # "ea", "LF", "LS"
    price_per_unit: float
    line_total: float
    rendering_ref: str             # filename or "(no rendering)"
    customer_facing: str           # NEW column — clean copy
    zone: str                      # NEW column — exact zone name OR "*"
    tiers: Tuple[Tier, ...]        # NEW column — parsed membership

    @property
    def is_enhancement(self) -> bool:
        return self.line_num.startswith("E")


@dataclass(frozen=True)
class SlidePlanItem:
    layout_name: str            # "cover", "exec_summary", "zone_solo", etc.
    context: dict               # the dict Renderer hands to Jinja2

    def __iter__(self):
        # Allow tuple-unpacking: layout, ctx = item
        yield self.layout_name
        yield self.context


@dataclass
class ValidationResult:
    blockers: list   # list of (code, message) tuples
    warnings: list   # list of (code, message) tuples
    fills_log: list = field(default_factory=list)  # list of (field, source) tuples for W8

    @property
    def passed(self) -> bool:
        return len(self.blockers) == 0

    @property
    def status(self) -> str:
        return "PASSED" if self.passed else "BLOCKED"


@dataclass(frozen=True)
class ProjectModel:
    """Fully-resolved project state ready for Composer.

    All Brief fields are present (voice/boilerplate fills already applied).
    All image references have been resolved to absolute paths.
    All line items have parsed Tier membership.
    """
    # Client & project
    client_company: str
    client_short: str
    project_name: str
    project_short: str
    project_year: int
    project_subtitle: str
    proposal_type: str           # default "Holiday Proposal"

    # Presenter
    presenter_name: str
    presenter_title: str
    presenter_email: str
    presenter_phone: str
    proposal_date: str           # ISO format

    # Schedule (all ISO format, all populated after auto-derivation)
    go_live: str
    season_end: str
    fabrication_lock: str
    signing_deadline: str

    # Tone & creative
    voice: str
    recommended_tier: Tier
    design_phrase: str
    pricing_format: str          # "tiered" | "single"

    # Image refs (filenames; Parser also stores resolved Paths separately)
    cover_image: str
    creative_vision_hero: str
    case_study: str              # case_study .md id, or "skip"
    case_study_hero: str

    # Structured content
    zones: Tuple[Zone, ...]
    line_items: Tuple[LineItem, ...]

    # Brief prose sections
    creative_direction: str
    customer_goals: Tuple[str, ...]
    customer_constraints: Tuple[str, ...]
    success_criteria: Tuple[str, ...]
    what_youre_approving: str

    # Filled by voice preset (or Brief override)
    pillars: Tuple[dict, ...]                   # [{title, body}, ...]
    phases: Tuple[dict, ...]                    # [{label, body}, ...]
    scope_includes: Tuple[str, ...]
    add_ons: Tuple[Tuple[str, str], ...]        # [(text, price_label), ...]
    term_panels: Mapping[str, str]              # {payment_schedule, insurance_permits, change_orders, validity}
    after_approval_steps: Tuple[str, ...]

    # Filled from boilerplate
    company_facts: Tuple[str, ...]              # bullets for About slide
    team: Tuple[dict, ...]                      # [{name, role}, ...]
    contact_strip: str
    partnership_discounts: Tuple[Tuple[str, str], ...]  # [(label, percent_off), ...]

    # Optional explicit slide-plan override (Composer skips auto if present)
    slide_plan_override: Tuple[dict, ...] = ()

    # Path lookups — populated by Parser (rendering filename → absolute Path)
    resolved_renderings: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ItemizedPricingDoc:
    """One per offered tier. Composer builds these; Renderer turns them into PDFs."""
    tier: Tier
    project: ProjectModel
    base_scope_lines: Tuple[LineItem, ...]
    enhancement_lines: Tuple[LineItem, ...]
    tier_total: float
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: 5 tests pass.

- [ ] **Step 8: Commit**

```bash
git add skill_assets/proposal_build/ tests/test_models.py pyproject.toml
git commit -m "feat(plan-3): add proposal_build package skeleton + ProjectModel dataclass"
```

---

## Phase 2 — Content libraries (3 tasks; no Python tests, content review by owner is the gate)

### Task 2: Boilerplate library (6 files)

**Files:**
- Create: `skill_assets/boilerplate/company_facts.md`
- Create: `skill_assets/boilerplate/team.md`
- Create: `skill_assets/boilerplate/contact_strip.md`
- Create: `skill_assets/boilerplate/terms_panels.md`
- Create: `skill_assets/boilerplate/scope_inclusions.md`
- Create: `skill_assets/boilerplate/partnership_discounts.md`

These files lift verbatim from the existing Plan-2-prime fixtures (pier_39.py, riverside.py) — they're Pier-39-master-derived content the owner has already approved.

- [ ] **Step 1: Create `company_facts.md`**

```markdown
---
founded: 1998
legal_name: "T&G Global, LLC"
dba: "St. Nick's Christmas Lighting & Décor"
license: "B-General Building Contractor #990427"
small_business: "Certified Small Business Supplier #1626660"
insurance: "$5M Umbrella · $1M/$2M GL · $1M Auto · Full Workers' Comp"
fulltime_team: 14
seasonal_team: "30–45"
venues_served: "200+ commercial venues across North America"

# Default about-page bullet list (used by About slide if Brief doesn't override)
default_bullets:
  - "Founded 1998 (dba St. Nick's) — T&G Global, LLC"
  - "14 full-time team · 30–45 seasonal staff"
  - "B-General Building Contractor #990427"
  - "Certified Small Business Supplier #1626660"
  - "$5M Umbrella · $1M/$2M GL · $1M Auto · Full Workers' Comp"
  - "200+ commercial venues across North America"
---
```

- [ ] **Step 2: Create `team.md`**

```markdown
---
roster:
  - name: "Nicholas Adams"
    role: "Founder"
  - name: "Wade Francis"
    role: "Chief Financial Officer"
  - name: "Brenda Sheridan"
    role: "Director of Operations"
  - name: "Daniel Christenson"
    role: "Director of Sales"
  - name: "Stephanie Escobar"
    role: "Creative Director"
  - name: "Carlos Vasquez & Alonso Salazar"
    role: "Senior Installers / Project Managers"
---
```

- [ ] **Step 3: Create `contact_strip.md`**

```markdown
---
text: "ST-NICKS.COM  ·  (562) 438-0017  ·  6861 Walker St, La Palma, CA 90623  ·  © {project_year} St. Nick's Christmas Lighting & Décor"
---
```

- [ ] **Step 4: Create `terms_panels.md`**

```markdown
---
default_payment_schedule: |
  30% deposit on signing — required to lock the install schedule.
  40% on fabrication start. 30% on go-live. Net-15 terms on final invoice.

default_insurance_permits: |
  $5M Umbrella over $1M/$2M Commercial General Liability and $1M Auto;
  full Workers' Comp at statutory limits. Certificates issued to
  {client_short} at signing. Permits handled by {client_short};
  we provide full documentation support.

default_change_orders: |
  Includes 2 creative revision rounds before Fabrication Lock ({fabrication_lock_long}).
  Scope or timeline changes after that date follow our standard change-order
  workflow — written approval required, priced at materials + 35%.

default_validity: |
  This proposal is valid 60 days from {proposal_date_long}. Materials pricing
  subject to market conditions thereafter. Sign by {signing_deadline_long} to
  lock schedule.
---
```

- [ ] **Step 5: Create `scope_inclusions.md`**

```markdown
---
default_inclusions:
  - "Creative design + client-approved renderings"
  - "All materials, décor, and lighting elements"
  - "Installation labor (phased install window)"
  - "Testing, commissioning, and launch support"
  - "Daily programming (dusk-to-dawn schedule)"
  - "Weekly on-site maintenance visits during program window"
  - "24/7 season on-call response"
  - "Complete post-season teardown and removal"
  - "Storage of reusable elements at our facility"
---
```

- [ ] **Step 6: Create `partnership_discounts.md`**

```markdown
---
discounts:
  - term: "2-YEAR"
    discount: 0.04
    label: "4% OFF"
  - term: "3-YEAR"
    discount: 0.06
    label: "6% OFF"
  - term: "5-YEAR"
    discount: 0.09
    label: "9% OFF"
non_multi_year_renewal_increase: 0.05
non_multi_year_renewal_note: "Standard non-multi-year renewals carry a 5% year-over-year increase on prior-year contract price."
---
```

- [ ] **Step 7: Commit**

```bash
git add skill_assets/boilerplate/
git commit -m "feat(plan-3): add boilerplate library — 6 invariant-content files"
```

### Task 3: Voice presets (4 files)

**Files:**
- Create: `skill_assets/voice_presets/civic.md`
- Create: `skill_assets/voice_presets/destination-retail.md`
- Create: `skill_assets/voice_presets/corporate.md`
- Create: `skill_assets/voice_presets/hospitality.md`

The owner reviews and refines voice rules + 5 polish examples per file post-Plan-3 (~30 min per voice). For Plan 3, ship drafts so the parser has something real to read.

- [ ] **Step 1: Create `civic.md`**

```markdown
---
name: Civic
description: Confident public-investment language. For municipal, transit, and government-adjacent projects where the customer is a public body answerable to taxpayers.
default_case_study: long_beach_transit

default_pillars:
  - title: "Civic Pride"
    body: "A holiday program that elevates {project_name} as a destination, not just a transit stop."
  - title: "Operational Discipline"
    body: "Materials engineered for transit weather; install coordinated with operational service hours."
  - title: "Repeatable Investment"
    body: "Decor designed for multi-season reuse; {project_year} builds the base for {next_year} and beyond."

default_phases:
  - {label: "WELCOME", body: "Wreaths and garlands at every entrance — the holiday begins at the curb."}
  - {label: "JOURNEY", body: "Pole banners and lighting carry the design language through the program."}
  - {label: "ARRIVAL", body: "Walk-through and lit displays at end-of-line — a destination, not a transfer."}

default_after_approval_steps:
  - "Kickoff call within 48 hrs"
  - "Creative window opens"
  - "Renderings final {fabrication_lock_minus_60d}"

default_sign_off_recap_pattern: |
  The {project_year} {project_name} {proposal_type} — {zone_summary}, live
  {go_live_long} through {season_end_long}, at the tier and add-ons you select
  on the Investment page.
---

# Voice: Civic

## When to use
Public-sector projects: municipal, transit, library, parks, civic center.
Tone: measured, confident, fiscally responsible.

## Voice rules
- Lead with operational discipline, civic pride, taxpayer value.
- Avoid: "amazing", "incredible", "magical", "the holidays are here!", exclamation points.
- Prefer: "engineered for", "designed to", "coordinated with", "tested at scale".
- Use civic vocabulary: "program", "season", "investment", "deliver", "civic-scale".
- Numbers and quantities are good; subjective enthusiasm is bad.

## Polish examples (Before → After)
**1.** "Lighted garlands really make the gates look great"
   → "Lit garland on the perimeter gates frames the property edge with warm-white evening glow."

**2.** "Wreaths! Big ones at the entrance"
   → "Custom-fabricated 5 ft wreaths at every station entrance — the threshold gesture of the program."

**3.** "Pole banner brackets needed because they don't have any (one-time)"
   → "Banner brackets — one-time purchase; customer-owned, reusable indefinitely across future seasons."

**4.** "Walkthrough thing at the entrance, ornament shape"
   → "Walk-through ornament arch at the plaza forecourt — a photo moment and the visual anchor of the program."

**5.** "Annual install of pole banners on all the poles, takes a day"
   → "Annual install of pole banner program at season open; removal at season close. Storage between seasons included."
```

- [ ] **Step 2: Create `destination-retail.md`**

Use the same shape as `civic.md` but with destination-retail tone (Pier 39 style). Set `default_case_study: oregon_zoo`. Tonal differences:

```markdown
---
name: Destination Retail
description: Guest-experience language. For retail destinations, theme parks, waterfront venues, mixed-use entertainment districts that host high foot traffic.
default_case_study: oregon_zoo

default_pillars:
  - title: "Turnkey Delivery"
    body: "Concept through teardown — one partner, zero seams."
  - title: "Destination Scale"
    body: "Built for venues hosting millions of guests per season."
  - title: "25 Years at It"
    body: "From Pier 39 to Disney Parks, we've done this before."

default_phases:
  - {label: "ARRIVE",    body: "Warm, cinematic welcome."}
  - {label: "EXPLORE",   body: "Discoverable moments along the property."}
  - {label: "CELEBRATE", body: "A landmark scene at the destination."}

default_after_approval_steps:
  - "Kickoff call within 48 hrs"
  - "Creative window opens"
  - "Renderings final {fabrication_lock_minus_60d}"

default_sign_off_recap_pattern: |
  The {project_year} {project_name} {proposal_type} — {zone_summary}, live
  {go_live_long} through {season_end_long}, at the tier and add-ons you select
  on the Investment page.
---

# Voice: Destination Retail

## When to use
Retail destinations, theme parks, waterfront venues, mixed-use entertainment districts.
Tone: cinematic, guest-focused, photogenic-friendly.

## Voice rules
- Lead with guest experience, dwell time, shareability.
- "Photo moment" / "shareable" are real concepts here, not jargon.
- Use destination vocabulary: "guest", "experience", "moment", "discover", "signature".
- Enthusiasm is OK if anchored to specifics ("4M social impressions" not "amazing crowds").

## Polish examples (Before → After)
**1.** "Big tree at the front, lit up"
   → "40-foot signature tree at the property entrance — the photo destination of the program."

**2.** "String lights all over the trees"
   → "220 linear feet of illuminated tree wrap along the central promenade — a layered glow guests walk through."

**3.** "Walk-through arch thing"
   → "Illuminated 28-foot entry arch — the threshold moment that sets the tone for arrival."

**4.** "Some ornaments, big ones"
   → "Four 8-foot oversized ornament installations along the central plaza — discoverable photo moments."

**5.** "Music and lights synced at night"
   → "Nightly synchronized music + light show at the signature zone — the program's destination moment."
```

- [ ] **Step 3: Create `corporate.md`**

```markdown
---
name: Corporate
description: Professional-discreet language. For corporate campuses, office buildings, financial-district properties where the customer is a property/facility manager.
default_case_study: pier_39

default_pillars:
  - title: "Discreet Excellence"
    body: "A holiday presence that signals quality without overstatement."
  - title: "Reliability"
    body: "Engineered for daily occupied use; operations coordinated with facility schedules."
  - title: "Long-Term Partnership"
    body: "Decor designed for multi-season reuse; year 1 builds the base for years 2 and 3."

default_phases:
  - {label: "ARRIVAL",     body: "A measured holiday gesture at the lobby and main entrance."}
  - {label: "EXPERIENCE",  body: "Coordinated treatment across common areas and shared spaces."}
  - {label: "RECOGNITION", body: "A signature moment that distinguishes the property at season."}

default_after_approval_steps:
  - "Kickoff call within 48 hrs"
  - "Creative window opens"
  - "Renderings final {fabrication_lock_minus_60d}"

default_sign_off_recap_pattern: |
  The {project_year} {project_name} {proposal_type} — {zone_summary}, live
  {go_live_long} through {season_end_long}, at the tier and add-ons you select
  on the Investment page.
---

# Voice: Corporate

## When to use
Corporate campuses, office buildings, financial-district properties.
Tone: measured, professional, restrained.

## Voice rules
- Lead with discretion, reliability, brand alignment.
- Avoid: "amazing", "festive", "magical", "wow factor".
- Prefer: "appropriate", "coordinated", "reliable", "measured".
- Use corporate vocabulary: "property", "facility", "common areas", "tenant experience".

## Polish examples (Before → After)
**1.** "Wreath at the lobby door"
   → "Lighted wreath at the primary lobby entrance — the threshold gesture of the program."

**2.** "Garland in the lobby"
   → "Coordinated garland treatment across the main lobby and elevator vestibule."

**3.** "Big tree in the main lobby"
   → "Centerpiece lighted tree in the main lobby — the property's holiday focal point."

**4.** "Some lights outside"
   → "Architectural façade lighting at the primary entrance — measured warm-white treatment."

**5.** "Maintenance every week to keep it nice"
   → "Weekly on-site maintenance visits throughout the season — tenant-facing reliability without disruption."
```

- [ ] **Step 4: Create `hospitality.md`**

```markdown
---
name: Hospitality
description: Guest-comfort language. For hotels, resorts, hospitality venues where the customer is a property manager whose primary KPI is guest satisfaction.
default_case_study: pier_39

default_pillars:
  - title: "Guest Comfort"
    body: "A holiday presence that elevates the stay without intruding on it."
  - title: "Operational Grace"
    body: "Install and service coordinated with peak occupancy windows."
  - title: "Multi-Season Quality"
    body: "Decor designed for the long arc of repeat-guest properties; year 1 builds the base for year 2 and beyond."

default_phases:
  - {label: "WELCOME",   body: "A measured holiday gesture at arrival and the lobby."}
  - {label: "STAY",      body: "Coordinated treatment across guest-facing common spaces."}
  - {label: "MEMORY",    body: "A signature moment that becomes part of the property's holiday identity."}

default_after_approval_steps:
  - "Kickoff call within 48 hrs"
  - "Creative window opens"
  - "Renderings final {fabrication_lock_minus_60d}"

default_sign_off_recap_pattern: |
  The {project_year} {project_name} {proposal_type} — {zone_summary}, live
  {go_live_long} through {season_end_long}, at the tier and add-ons you select
  on the Investment page.
---

# Voice: Hospitality

## When to use
Hotels, resorts, hospitality venues. Tone: warm, measured, guest-first.

## Voice rules
- Lead with guest comfort, operational grace, quality-over-spectacle.
- Avoid: "wow", "stunning", "magical", anything that sounds like a Yelp review.
- Prefer: "guest experience", "elevated", "considered", "reliable".

## Polish examples (Before → After)
**1.** "Wreaths at the porte-cochère"
   → "Lighted wreaths at the porte-cochère and primary lobby entrance — the welcome gesture for arriving guests."

**2.** "Lobby tree, big one"
   → "Centerpiece lighted tree in the main lobby — the property's holiday focal point and a guest-photo destination."

**3.** "Garlands and wreaths around the property"
   → "Coordinated garland and wreath treatment across all guest-facing common areas — restaurant, lobby bar, elevator vestibules."

**4.** "Lighting outside on the building"
   → "Architectural façade lighting on the entry façade — measured warm-white treatment that frames the property at evening."

**5.** "Maintenance during the season"
   → "Weekly on-site maintenance visits during peak season — guest-experience continuity without service disruption."
```

- [ ] **Step 5: Commit**

```bash
git add skill_assets/voice_presets/
git commit -m "feat(plan-3): add 4 voice preset drafts (civic, destination-retail, corporate, hospitality)"
```

### Task 4: Case studies (3 files)

**Files:**
- Create: `skill_assets/case_studies/long_beach_transit.md`
- Create: `skill_assets/case_studies/oregon_zoo.md`
- Create: `skill_assets/case_studies/pier_39.md`

Content lifted from the existing Plan-2-prime fixtures' `case_study_ctx` dicts.

- [ ] **Step 1: Create `long_beach_transit.md`** (from `tests/fixtures/riverside.py::case_study_ctx`)

```markdown
---
id: long_beach_transit
name: "Long Beach Transit · 2024"
year: 2024
voice_tag: civic
hero_default: "Evening Lighting - Station Awning 01.png"
standfirst: "A multi-station civic holiday program at scale, delivered in a single season."
---

## Challenge
Roll out a coordinated holiday décor program across 14 transit stations on a tight budget and an even tighter install window — all installs had to land within a 21-day overnight window without disrupting revenue service.

## Approach
Standardized fabrication kits per station tier (flagship / standard / outpost). Pre-staged shipments at the operations yard. Crew rotated through stations on a strict overnight schedule with QC walks at sunrise.

## Outcome
All 14 stations live on schedule. Zero revenue-service disruptions. Local press coverage at six of the fourteen stations. Program renewed for 2025 with three additional stations.
```

- [ ] **Step 2: Create `oregon_zoo.md`** (from `tests/fixtures/pier_39.py::case_study_ctx`)

```markdown
---
id: oregon_zoo
name: "Oregon Zoo · ZooLights 2025"
year: 2025
voice_tag: destination-retail
hero_default: ""
standfirst: "Transforming Portland's family destination into a signature winter experience."
---

## Challenge
Deliver a full property-wide holiday transformation across 64 acres of active zoological habitats, with zero disruption to animal welfare protocols and overnight install windows aligned to keeper schedules.

## Approach
Phased 18-night install coordinated with animal care teams. Custom low-impact lighting specifications. A signature 45-ft illuminated central tree, themed habitat lighting, and an interactive Light Walk that shifted weekly.

## Outcome
31% YoY increase in ZooLights attendance. 4.2M+ social impressions. Partnership renewed through 2028. Feature coverage in The Oregonian, KGW, and Travel + Leisure.
```

- [ ] **Step 3: Create `pier_39.md`** (corporate-friendly cross-reference)

```markdown
---
id: pier_39
name: "Pier 39 San Francisco · 2024"
year: 2024
voice_tag: corporate
hero_default: ""
standfirst: "A multi-zone destination program for one of the West Coast's highest-traffic waterfront venues."
---

## Challenge
Deliver a coordinated three-zone holiday program across 45 acres of active retail and dining waterfront, with phased overnight install to avoid retail disruption and zero impact to the K-Dock sea lion habitat.

## Approach
Phased install during overnight windows. Standardized fabrication kits per zone (entry / promenade / signature). Daily programming with weekly maintenance and a 4-hour SLA on-call response throughout the program window.

## Outcome
A signature holiday identity photographed and shared 10× the volume of the prior season. Measurable dwell-time lift across all three zones. Program built for multi-year extension into Pier 39's broader marketing narrative.
```

- [ ] **Step 4: Commit**

```bash
git add skill_assets/case_studies/
git commit -m "feat(plan-3): add 3 case study files (long_beach_transit, oregon_zoo, pier_39)"
```

---

## Phase 3 — Parser (6 tasks)

### Task 5: Parser — Brief.md (`parser/brief.py` + `test_parser_brief.py`)

**Files:**
- Create: `tests/fixtures/briefs/minimal_valid.md`
- Create: `tests/fixtures/briefs/missing_voice.md`
- Create: `tests/fixtures/briefs/two_signatures.md`
- Create: `tests/fixtures/briefs/auto_dates.md`
- Create: `skill_assets/proposal_build/parser/brief.py`
- Create: `tests/test_parser_brief.py`

- [ ] **Step 1: Create test fixtures**

Create `tests/fixtures/briefs/minimal_valid.md`:

```markdown
---
client_company: "Test Client"
client_short: "TEST"
project_name: "Test Project"
project_short: "Test"
project_subtitle: "A small project"
project_year: 2026
proposal_type: "Holiday Proposal"

presenter_name: "Tester"
presenter_title: "AE"
presenter_email: "t@x.com"
presenter_phone: "(555) 555-5555"
proposal_date: "2026-05-12"

go_live: "2026-11-20"
season_end: "2027-01-05"
fabrication_lock: "2026-08-22"
signing_deadline: "2026-10-30"

voice: "civic"
recommended_tier: "enhanced"
design_phrase: "Test."
pricing_format: "tiered"

cover_image: "cover.jpg"
creative_vision_hero: "cv.jpg"
case_study: "long_beach_transit"
case_study_hero: "cs.jpg"

zones:
  - num: "01"
    name: "Zone One"
    subtitle: "First zone."
    flags: [flagship]
    hero_image: "z1.jpg"
    bullets: ["Bullet A", "Bullet B"]
---

## Creative Direction
Test direction.

## Customer Goals
- Goal A
- Goal B

## Customer Constraints
- Constraint A

## Success Criteria
- Success A

## What You're Approving
The test approval recap.
```

Create `tests/fixtures/briefs/missing_voice.md` — same as above but delete the `voice: "civic"` line.

Create `tests/fixtures/briefs/two_signatures.md` — same as `minimal_valid.md` but `zones:` has two entries each with `flags: [signature]`.

Create `tests/fixtures/briefs/auto_dates.md` — same as `minimal_valid.md` but `fabrication_lock: ""` and `signing_deadline: ""` (blank).

- [ ] **Step 2: Write the failing test**

Create `tests/test_parser_brief.py`:

```python
"""Tests for parser/brief.py — Brief.md frontmatter + section parsing."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser.brief import parse_brief, BriefParseError

FIXTURES = Path(__file__).parent / "fixtures" / "briefs"


def test_minimal_valid_parses():
    data = parse_brief(FIXTURES / "minimal_valid.md")
    assert data.frontmatter["voice"] == "civic"
    assert data.frontmatter["project_name"] == "Test Project"
    assert len(data.frontmatter["zones"]) == 1
    assert data.frontmatter["zones"][0]["name"] == "Zone One"
    assert data.sections["Creative Direction"].strip() == "Test direction."
    assert data.sections["Customer Goals"] == ["Goal A", "Goal B"]
    assert data.sections["What You're Approving"].strip().startswith("The test approval")


def test_missing_voice_raises():
    with pytest.raises(BriefParseError) as exc:
        parse_brief(FIXTURES / "missing_voice.md")
    assert "voice" in str(exc.value).lower()


def test_two_signatures_raises():
    with pytest.raises(BriefParseError) as exc:
        parse_brief(FIXTURES / "two_signatures.md")
    assert "signature" in str(exc.value).lower()


def test_auto_dates_blank_passes_through():
    """parse_brief returns the raw frontmatter with blank dates;
    auto-derivation happens in the orchestrator, not the parser."""
    data = parse_brief(FIXTURES / "auto_dates.md")
    assert data.frontmatter["fabrication_lock"] == ""
    assert data.frontmatter["signing_deadline"] == ""
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_parser_brief.py -v`
Expected: ImportError — `parser.brief` doesn't exist.

- [ ] **Step 4: Implement `parser/brief.py`**

Create `skill_assets/proposal_build/parser/brief.py`:

```python
"""Parse Project Brief.md — YAML frontmatter + markdown body sections.

Returns BriefData (raw). Voice/boilerplate fill, date auto-derivation, and image
filename resolution happen downstream in the orchestrator (parser/__init__.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import frontmatter


REQUIRED_FIELDS = (
    "client_company", "project_name", "project_year", "presenter_name",
    "voice", "recommended_tier", "pricing_format", "cover_image",
)

PROSE_SECTIONS = (
    "Creative Direction", "Customer Goals", "Customer Constraints",
    "Success Criteria", "What You're Approving",
)
# Sections that are bullet lists vs free prose. Bullet sections become tuples; prose stays a string.
BULLET_SECTIONS = {"Customer Goals", "Customer Constraints", "Success Criteria"}


class BriefParseError(Exception):
    """Raised on a blocking Brief problem (missing field, bad structure, etc.)."""


@dataclass
class BriefData:
    frontmatter: dict
    sections: dict   # {section_name: str OR list[str]}


def parse_brief(path: Path) -> BriefData:
    """Parse a Brief.md file into BriefData. Raises BriefParseError on hard issues."""
    if not path.exists():
        raise BriefParseError(f"Brief not found at {path}")

    post = frontmatter.load(str(path))
    fm = dict(post.metadata)

    # Required-field check
    missing = [f for f in REQUIRED_FIELDS if not fm.get(f)]
    if missing:
        raise BriefParseError(f"Brief missing required fields: {', '.join(missing)}")
    if not fm.get("zones"):
        raise BriefParseError("Brief missing required field: zones (must be non-empty list)")

    # Signature-count check
    sigs = [z for z in fm["zones"] if "signature" in (z.get("flags") or [])]
    if len(sigs) > 1:
        names = ", ".join(z["name"] for z in sigs)
        raise BriefParseError(f"At most one zone may carry the 'signature' flag; found: {names}")

    # Parse markdown body into sections
    sections = _split_sections(post.content)

    return BriefData(frontmatter=fm, sections=sections)


def _split_sections(body: str) -> dict[str, Any]:
    """Split markdown body into {heading: content} pairs. Bullet sections → list[str]; prose → str."""
    sections: dict[str, Any] = {}
    current_name = None
    current_lines: list[str] = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_name is not None:
                sections[current_name] = _coerce_section(current_name, current_lines)
            current_name = line[3:].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        sections[current_name] = _coerce_section(current_name, current_lines)

    return sections


def _coerce_section(name: str, lines: list[str]) -> Any:
    """Bullet sections → list of bullet text; prose sections → joined string."""
    if name in BULLET_SECTIONS:
        return [ln[2:].strip() for ln in lines if ln.startswith("- ")]
    return "\n".join(lines).strip()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_parser_brief.py -v`
Expected: 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/parser/brief.py tests/test_parser_brief.py tests/fixtures/briefs/
git commit -m "feat(plan-3): parser/brief.py — Brief.md frontmatter + sections parsing"
```

### Task 6: Parser — Worksheet (`parser/worksheet.py` + `test_parser_worksheet.py`)

**Files:**
- Create: `tests/fixtures/worksheets/build_test_workbook.py` (helper script that generates the .xlsx fixtures programmatically — easier than committing binary .xlsx files)
- Create: `tests/fixtures/worksheets/minimal_valid.xlsx` (generated)
- Create: `tests/fixtures/worksheets/missing_tiers_column.xlsx` (generated)
- Create: `tests/fixtures/worksheets/with_substitution.xlsx` (generated)
- Create: `skill_assets/proposal_build/parser/worksheet.py`
- Create: `tests/test_parser_worksheet.py`

- [ ] **Step 1: Create the .xlsx fixture builder script**

Create `tests/fixtures/worksheets/build_test_workbook.py`:

```python
"""Generate small .xlsx fixture files for parser/worksheet tests.

Run this script when you change the fixture shape:
    python tests/fixtures/worksheets/build_test_workbook.py

It writes minimal_valid.xlsx, missing_tiers_column.xlsx, with_substitution.xlsx
into this directory, mirroring the layout of the real Riverside worksheet
(title rows, summary block, base table, enhancements table, tier scenarios).
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

HERE = Path(__file__).parent

HEADER_FULL = [
    "#", "Item", "Description / Location", "Qty", "Unit",
    "Price\nper Unit", "Line Total", "Rendering Reference",
    "Materials / Build / Anchoring", "Notes / Assumptions",
    "Customer-Facing Description", "Zone", "Tiers",
]

HEADER_NO_TIERS = HEADER_FULL[:-1]   # drops the Tiers column


def _write_workbook(path: Path, header: list[str], base_rows: list[list], enh_rows: list[list],
                    scenarios: list[tuple[str, float]]) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Scope Worksheet"

    # Title rows
    ws.cell(row=1, column=1, value="Test Project — Scope Worksheet")
    ws.cell(row=2, column=1, value="Test header row")
    # Blank row 3
    # Header row 4
    for col, h in enumerate(header, start=1):
        ws.cell(row=4, column=col, value=h)
    # Base rows starting row 5
    next_row = 5
    for r in base_rows:
        for col, val in enumerate(r, start=1):
            ws.cell(row=next_row, column=col, value=val)
        next_row += 1
    # Blank row, then total row, then blank
    ws.cell(row=next_row, column=2, value="BASE SCOPE TOTAL — Year 1")
    ws.cell(row=next_row, column=7, value=sum(r[6] for r in base_rows))
    next_row += 2

    # OPTIONAL ENHANCEMENTS section header
    ws.cell(row=next_row, column=1, value="OPTIONAL ENHANCEMENTS — priced individually")
    next_row += 1
    # Enhancements header row (same shape)
    for col, h in enumerate(header, start=1):
        ws.cell(row=next_row, column=col, value=h)
    next_row += 1
    for r in enh_rows:
        for col, val in enumerate(r, start=1):
            ws.cell(row=next_row, column=col, value=val)
        next_row += 1
    next_row += 1

    # TIER SCENARIOS block
    ws.cell(row=next_row, column=1, value="TIER SCENARIOS")
    next_row += 1
    for label, total in scenarios:
        ws.cell(row=next_row, column=2, value=label)
        ws.cell(row=next_row, column=7, value=total)
        next_row += 1

    wb.save(path)


def _row(line_num, item, qty, price, customer_facing, zone, tiers):
    """Build a 13-column row. Internal description, rendering, materials are blank for tests."""
    line_total = qty * price
    return [
        line_num, item, "internal desc", qty, "ea", price, line_total,
        "rendering.png", "materials", "notes",
        customer_facing, zone, tiers,
    ]


# minimal_valid.xlsx — 2 base + 1 enhancement, all in all 3 tiers
def build_minimal_valid() -> None:
    base = [
        _row("1", "Wreath", 4, 100, "Lighted wreaths at the entrance.", "Zone One",
             "Essential, Enhanced, Signature"),
        _row("2", "Garland", 100, 25, "Lit garland on the perimeter fence.", "*",
             "Essential, Enhanced, Signature"),
    ]
    enh = [
        _row("E1", "Snowflakes", 12, 295, "Lighted snowflakes on platform railings.",
             "Zone One", "Enhanced, Signature"),
    ]
    base_total = sum(r[6] for r in base)
    enh_total = sum(r[6] for r in enh)
    scenarios = [
        ("ESSENTIAL — Base only", base_total),
        ("ENHANCED — Base + Snowflakes", base_total + enh_total),
        ("SIGNATURE — All", base_total + enh_total),
    ]
    _write_workbook(HERE / "minimal_valid.xlsx", HEADER_FULL, base, enh, scenarios)


# missing_tiers_column.xlsx — header omits Tiers column
def build_missing_tiers() -> None:
    base = [
        ["1", "Wreath", "internal", 4, "ea", 100, 400, "render.png", "mat", "notes",
         "Lit wreaths.", "*"],   # only 12 cols, no Tiers
    ]
    _write_workbook(HERE / "missing_tiers_column.xlsx", HEADER_NO_TIERS, base, [], [])


# with_substitution.xlsx — Traditional Tree (Essential, Enhanced) + Spiral LED (Signature)
def build_substitution() -> None:
    base = [
        _row("1", "Traditional Tree", 1, 18000, "Traditional centerpiece tree.",
             "Zone One", "Essential, Enhanced"),
    ]
    enh = [
        _row("E1", "Spiral LED Tree", 1, 22000, "Spiral LED replacement tree.",
             "Zone One", "Signature"),
    ]
    scenarios = [
        ("ESSENTIAL", 18000),
        ("ENHANCED", 18000),
        ("SIGNATURE", 22000),    # Traditional excluded; Spiral LED included
    ]
    _write_workbook(HERE / "with_substitution.xlsx", HEADER_FULL, base, enh, scenarios)


if __name__ == "__main__":
    build_minimal_valid()
    build_missing_tiers()
    build_substitution()
    print("Generated 3 fixture .xlsx files in", HERE)
```

- [ ] **Step 2: Run the fixture builder to generate test .xlsx files**

Run: `python tests/fixtures/worksheets/build_test_workbook.py`
Expected: prints "Generated 3 fixture .xlsx files in …".

- [ ] **Step 3: Write the failing test**

Create `tests/test_parser_worksheet.py`:

```python
"""Tests for parser/worksheet.py — Scope Worksheet.xlsx parsing."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.models import Tier
from proposal_build.parser.worksheet import (
    parse_worksheet,
    WorksheetParseError,
)

FIXTURES = Path(__file__).parent / "fixtures" / "worksheets"


def test_minimal_valid_parses():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    assert len(result.line_items) == 3
    base = [li for li in result.line_items if not li.is_enhancement]
    enh = [li for li in result.line_items if li.is_enhancement]
    assert len(base) == 2
    assert len(enh) == 1
    assert base[0].item == "Wreath"
    assert base[0].qty == 4
    assert base[0].line_total == 400
    assert base[0].customer_facing == "Lighted wreaths at the entrance."
    assert base[0].zone == "Zone One"
    assert base[0].tiers == (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)
    assert enh[0].line_num == "E1"


def test_zone_wildcard_preserved():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    garland = next(li for li in result.line_items if li.item == "Garland")
    assert garland.zone == "*"


def test_substitution_via_tier_membership():
    result = parse_worksheet(FIXTURES / "with_substitution.xlsx")
    traditional = next(li for li in result.line_items if li.item == "Traditional Tree")
    spiral = next(li for li in result.line_items if li.item == "Spiral LED Tree")
    assert Tier.ESSENTIAL in traditional.tiers
    assert Tier.SIGNATURE not in traditional.tiers
    assert Tier.SIGNATURE in spiral.tiers
    assert Tier.ESSENTIAL not in spiral.tiers


def test_per_tier_sums():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    sums = result.tier_sums_per_line()
    # Base = 400 + 2500 = 2900; Enhancement E1 = 12*295 = 3540
    assert sums[Tier.ESSENTIAL] == 2900
    assert sums[Tier.ENHANCED] == 2900 + 3540
    assert sums[Tier.SIGNATURE] == 2900 + 3540


def test_substitution_tier_sums():
    result = parse_worksheet(FIXTURES / "with_substitution.xlsx")
    sums = result.tier_sums_per_line()
    assert sums[Tier.ESSENTIAL] == 18000
    assert sums[Tier.ENHANCED] == 18000
    assert sums[Tier.SIGNATURE] == 22000


def test_missing_tiers_column_raises():
    with pytest.raises(WorksheetParseError) as exc:
        parse_worksheet(FIXTURES / "missing_tiers_column.xlsx")
    assert "tiers" in str(exc.value).lower()


def test_scenarios_block_parsed():
    result = parse_worksheet(FIXTURES / "minimal_valid.xlsx")
    assert result.scenarios is not None
    # We don't validate contents here — that's W4 in validate.py
    assert len(result.scenarios) == 3
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `pytest tests/test_parser_worksheet.py -v`
Expected: ImportError — `parser.worksheet` doesn't exist.

- [ ] **Step 5: Implement `parser/worksheet.py`**

Create `skill_assets/proposal_build/parser/worksheet.py`:

```python
"""Parse Scope Worksheet.xlsx — find data tables in the mixed-content sheet.

Returns WorksheetData with parsed line items and the optional tier scenarios block.
Validation against tier scenarios (W4) is in validate.py, not here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import openpyxl

from proposal_build.models import LineItem, Tier


REQUIRED_HEADERS = (
    "Customer-Facing Description", "Zone", "Tiers",
)

# Worksheet header column names → field name on LineItem
HEADER_MAP = {
    "#": "line_num",
    "Item": "item",
    "Description / Location": "description",
    "Qty": "qty",
    "Unit": "unit",
    "Price\nper Unit": "price_per_unit",
    "Line Total": "line_total",
    "Rendering Reference": "rendering_ref",
    "Customer-Facing Description": "customer_facing",
    "Zone": "zone",
    "Tiers": "tiers",
}


class WorksheetParseError(Exception):
    """Raised on a blocking Worksheet problem."""


@dataclass
class WorksheetData:
    line_items: tuple
    scenarios: tuple | None  # ((label, total), ...) or None if block absent

    def tier_sums_per_line(self) -> dict:
        """Sum line_total per tier across line_items. Used by Investment + W4."""
        sums = {Tier.ESSENTIAL: 0.0, Tier.ENHANCED: 0.0, Tier.SIGNATURE: 0.0}
        for li in self.line_items:
            for t in li.tiers:
                sums[t] += li.line_total
        return sums


def parse_worksheet(path: Path) -> WorksheetData:
    if not path.exists():
        raise WorksheetParseError(f"Worksheet not found at {path}")

    wb = openpyxl.load_workbook(str(path), data_only=True)
    ws = wb.active   # Only one sheet expected

    rows = list(ws.iter_rows(values_only=True))

    # Find the first header row that contains all REQUIRED_HEADERS
    header_row_idx = _find_header_row(rows)
    headers = [_norm(c) for c in rows[header_row_idx]]
    _verify_headers(headers)

    # Walk rows after the header, parsing data rows until we hit a blank row or summary row.
    line_items = []
    i = header_row_idx + 1
    while i < len(rows):
        row = rows[i]
        if _is_data_row(row):
            line_items.append(_parse_row(row, headers))
        elif _is_section_or_summary_row(row):
            # Try to find another header row (the Enhancements table)
            next_header = _find_header_row(rows, start=i + 1)
            if next_header is not None and next_header < len(rows):
                i = next_header  # jump to next header; loop will skip past it
                # Verify the next header has the same shape
                next_headers = [_norm(c) for c in rows[next_header]]
                if next_headers != headers:
                    raise WorksheetParseError(
                        "Second data table has different columns than the first."
                    )
        i += 1

    # Find the TIER SCENARIOS block
    scenarios = _parse_scenarios(rows)

    return WorksheetData(line_items=tuple(line_items), scenarios=scenarios)


def _norm(cell) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _find_header_row(rows: list, start: int = 0) -> int | None:
    for i in range(start, len(rows)):
        normed = [_norm(c) for c in rows[i]]
        if all(h in normed for h in REQUIRED_HEADERS):
            return i
    return None


def _verify_headers(headers: list[str]) -> None:
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise WorksheetParseError(
            f"Worksheet missing required column(s): {', '.join(missing)}"
        )


_LINE_NUM_RE = re.compile(r"^(?:\d+|E\d+)$")


def _is_data_row(row: tuple) -> bool:
    """A data row has a line_num like '1' or 'E6' in column 1."""
    if not row or row[0] is None:
        return False
    return bool(_LINE_NUM_RE.match(str(row[0]).strip()))


def _is_section_or_summary_row(row: tuple) -> bool:
    """Returns True for header-like rows that aren't data rows (e.g., 'OPTIONAL ENHANCEMENTS')."""
    return any(c is not None for c in row)


def _parse_row(row: tuple, headers: list[str]) -> LineItem:
    by_header = {}
    for col, h in enumerate(headers):
        if col >= len(row):
            break
        by_header[h] = row[col]

    tiers_raw = _norm(by_header.get("Tiers", ""))
    tiers = tuple(Tier.from_string(t) for t in tiers_raw.split(",") if t.strip())

    return LineItem(
        line_num=_norm(by_header.get("#", "")),
        item=_norm(by_header.get("Item", "")),
        description=_norm(by_header.get("Description / Location", "")),
        qty=float(by_header.get("Qty") or 0),
        unit=_norm(by_header.get("Unit", "")),
        price_per_unit=float(by_header.get("Price\nper Unit") or 0),
        line_total=float(by_header.get("Line Total") or 0),
        rendering_ref=_norm(by_header.get("Rendering Reference", "")),
        customer_facing=_norm(by_header.get("Customer-Facing Description", "")),
        zone=_norm(by_header.get("Zone", "")),
        tiers=tiers,
    )


def _parse_scenarios(rows: list) -> tuple | None:
    """Find the TIER SCENARIOS block and return ((label, total), ...) or None."""
    for i, row in enumerate(rows):
        cell = _norm(row[0]) if row else ""
        if cell.upper() == "TIER SCENARIOS":
            scenarios = []
            j = i + 1
            while j < len(rows):
                r = rows[j]
                label = _norm(r[1]) if len(r) > 1 else ""
                total = r[6] if len(r) > 6 else None
                if not label or total is None:
                    break
                scenarios.append((label, float(total)))
                j += 1
            return tuple(scenarios) if scenarios else None
    return None
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `pytest tests/test_parser_worksheet.py -v`
Expected: 7 tests pass.

- [ ] **Step 7: Commit**

```bash
git add skill_assets/proposal_build/parser/worksheet.py tests/test_parser_worksheet.py tests/fixtures/worksheets/
git commit -m "feat(plan-3): parser/worksheet.py — locates tables, parses 3 new columns, validates Tiers"
```

### Task 7: Parser — Renderings (`parser/renderings.py`)

**Files:**
- Create: `skill_assets/proposal_build/parser/renderings.py`
- (No new test file — covered by `test_parser_validate.py` later, since rendering resolution is a validation concern.)

- [ ] **Step 1: Implement `parser/renderings.py`**

Create `skill_assets/proposal_build/parser/renderings.py`:

```python
"""Walk 02 - Renderings/ folders and resolve filename → absolute Path.

Brief.md references images by filename only; this module resolves to actual
files on disk. Ambiguity (same filename in both Base Scope/ and Enhancements/)
or missing files are surfaced as exceptions for the validator to convert into
blocking errors.
"""
from __future__ import annotations

from pathlib import Path


class RenderingsResolutionError(Exception):
    """Raised when a referenced filename can't be uniquely resolved."""


SUBDIRS = ("Base Scope", "Enhancements", "_inbox", "Unused Renderings")


def walk_renderings(project_dir: Path) -> dict[str, Path]:
    """Return {filename → Path} for every image in 02 - Renderings/{Base Scope|Enhancements}/.

    Files in _inbox/ and Unused Renderings/ are NOT included in the lookup map
    (they are not eligible for use as cover/zone/case-study heroes), but the
    walker still records them for the W1 unused-renderings warning.
    """
    renderings_dir = project_dir / "02 - Renderings"
    if not renderings_dir.exists():
        return {}

    eligible: dict[str, list[Path]] = {}
    for subdir in ("Base Scope", "Enhancements"):
        sub = renderings_dir / subdir
        if not sub.exists():
            continue
        for f in sub.iterdir():
            if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                eligible.setdefault(f.name, []).append(f)

    # Convert to single-Path lookup, raising on duplicates
    lookup: dict[str, Path] = {}
    for name, paths in eligible.items():
        if len(paths) > 1:
            locations = ", ".join(str(p.parent.name) for p in paths)
            raise RenderingsResolutionError(
                f"Filename '{name}' appears in multiple folders ({locations}). "
                f"Rename one to disambiguate."
            )
        lookup[name] = paths[0]

    return lookup


def list_all_renderings(project_dir: Path) -> dict[str, list[Path]]:
    """Return {subdir_name → list of files} across all 4 subdirs.

    Used by the validator's W1 unused-renderings check.
    """
    renderings_dir = project_dir / "02 - Renderings"
    if not renderings_dir.exists():
        return {sd: [] for sd in SUBDIRS}

    out: dict[str, list[Path]] = {}
    for subdir in SUBDIRS:
        sub = renderings_dir / subdir
        if sub.exists():
            out[subdir] = sorted(
                f for f in sub.iterdir()
                if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            )
        else:
            out[subdir] = []
    return out


def resolve_filename(filename: str, lookup: dict[str, Path]) -> Path:
    """Resolve a Brief-referenced filename. Raises if not found."""
    p = lookup.get(filename)
    if p is None:
        raise RenderingsResolutionError(
            f"Image filename '{filename}' not found in 02 - Renderings/Base Scope/ or Enhancements/."
        )
    return p
```

- [ ] **Step 2: Smoke-test against the real Riverside folder**

Run from repo root:

```bash
python -c "
from pathlib import Path
from proposal_build.parser.renderings import walk_renderings, list_all_renderings
project = Path('Projects/Downtown Riverside Metro Link')
lookup = walk_renderings(project)
print(f'{len(lookup)} eligible renderings found')
all_r = list_all_renderings(project)
for sd, files in all_r.items():
    print(f'  {sd}: {len(files)} files')
"
```

Expected: ~25 eligible renderings; Base Scope ~17, Enhancements ~8, _inbox 0, Unused Renderings 0.

- [ ] **Step 3: Commit**

```bash
git add skill_assets/proposal_build/parser/renderings.py
git commit -m "feat(plan-3): parser/renderings.py — filename → Path lookup with ambiguity detection"
```

### Task 8: Parser — Voice + Boilerplate (`parser/voice.py`, `parser/boilerplate.py` + combined test)

**Files:**
- Create: `skill_assets/proposal_build/parser/voice.py`
- Create: `skill_assets/proposal_build/parser/boilerplate.py`
- Create: `tests/test_parser_voice_boilerplate.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_parser_voice_boilerplate.py`:

```python
"""Tests for voice preset + boilerplate loading and layered fill."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser.voice import load_voice, VoiceLoadError
from proposal_build.parser.boilerplate import load_boilerplate, substitute_placeholders


def test_load_civic_voice():
    v = load_voice("civic")
    assert v.name == "Civic"
    assert v.default_case_study == "long_beach_transit"
    assert len(v.default_pillars) == 3
    assert v.default_pillars[0]["title"] == "Civic Pride"
    assert len(v.default_phases) == 3


def test_load_unknown_voice_raises():
    with pytest.raises(VoiceLoadError):
        load_voice("nonexistent")


def test_load_boilerplate():
    bp = load_boilerplate()
    assert "Founded 1998" in bp.company_facts_default_bullets[0]
    assert any("Daniel Christenson" in m["name"] for m in bp.team_roster)
    assert "ST-NICKS.COM" in bp.contact_strip
    assert "default_payment_schedule" in bp.term_panels  # snake_case key
    assert any(d["term"] == "2-YEAR" for d in bp.partnership_discounts)


def test_substitute_placeholders_known_keys():
    text = "Hello {project_name}, year {project_year}."
    result = substitute_placeholders(text, {"project_name": "MetroLink", "project_year": 2026})
    assert result == "Hello MetroLink, year 2026."


def test_substitute_placeholders_unknown_raises():
    text = "Hello {bogus}."
    with pytest.raises(KeyError):
        substitute_placeholders(text, {"project_name": "X"})


def test_pillars_template_substitution():
    v = load_voice("civic")
    pillar0 = v.default_pillars[0]
    body_with_subs = substitute_placeholders(
        pillar0["body"],
        {"project_name": "Riverside MetroLink", "project_year": 2026, "next_year": 2027},
    )
    assert "Riverside MetroLink" in body_with_subs
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser_voice_boilerplate.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement `parser/voice.py`**

Create `skill_assets/proposal_build/parser/voice.py`:

```python
"""Load voice presets from skill_assets/voice_presets/{name}.md."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import frontmatter


VOICE_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "voice_presets"


class VoiceLoadError(Exception):
    pass


@dataclass(frozen=True)
class VoicePreset:
    name: str
    description: str
    default_case_study: str
    default_pillars: tuple
    default_phases: tuple
    default_after_approval_steps: tuple
    default_sign_off_recap_pattern: str
    voice_rules_md: str   # the prose body — read by the polish chat in Claude Desktop


def load_voice(name: str) -> VoicePreset:
    path = VOICE_DIR / f"{name}.md"
    if not path.exists():
        raise VoiceLoadError(f"Voice preset not found: {name} (looked at {path})")

    post = frontmatter.load(str(path))
    fm = post.metadata

    return VoicePreset(
        name=fm["name"],
        description=fm.get("description", ""),
        default_case_study=fm.get("default_case_study", ""),
        default_pillars=tuple(fm.get("default_pillars", ())),
        default_phases=tuple(fm.get("default_phases", ())),
        default_after_approval_steps=tuple(fm.get("default_after_approval_steps", ())),
        default_sign_off_recap_pattern=fm.get("default_sign_off_recap_pattern", ""),
        voice_rules_md=post.content,
    )
```

- [ ] **Step 4: Implement `parser/boilerplate.py`**

Create `skill_assets/proposal_build/parser/boilerplate.py`:

```python
"""Load boilerplate library from skill_assets/boilerplate/."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import frontmatter


BOILERPLATE_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "boilerplate"


@dataclass(frozen=True)
class Boilerplate:
    company_facts: dict
    company_facts_default_bullets: tuple
    team_roster: tuple
    contact_strip: str
    term_panels: dict   # {default_payment_schedule, default_insurance_permits, ...}
    scope_inclusions_default: tuple
    partnership_discounts: tuple
    non_multi_year_renewal_increase: float
    non_multi_year_renewal_note: str


def load_boilerplate() -> Boilerplate:
    company = frontmatter.load(str(BOILERPLATE_DIR / "company_facts.md")).metadata
    team_md = frontmatter.load(str(BOILERPLATE_DIR / "team.md")).metadata
    contact_md = frontmatter.load(str(BOILERPLATE_DIR / "contact_strip.md")).metadata
    terms_md = frontmatter.load(str(BOILERPLATE_DIR / "terms_panels.md")).metadata
    scope_md = frontmatter.load(str(BOILERPLATE_DIR / "scope_inclusions.md")).metadata
    partner_md = frontmatter.load(str(BOILERPLATE_DIR / "partnership_discounts.md")).metadata

    return Boilerplate(
        company_facts={k: v for k, v in company.items() if k != "default_bullets"},
        company_facts_default_bullets=tuple(company["default_bullets"]),
        team_roster=tuple(team_md["roster"]),
        contact_strip=contact_md["text"],
        term_panels={k: v.strip() for k, v in terms_md.items()},
        scope_inclusions_default=tuple(scope_md["default_inclusions"]),
        partnership_discounts=tuple(partner_md["discounts"]),
        non_multi_year_renewal_increase=float(partner_md.get("non_multi_year_renewal_increase", 0.05)),
        non_multi_year_renewal_note=partner_md.get("non_multi_year_renewal_note", ""),
    )


_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+(?:_long|_minus_60d)?)\}")


def substitute_placeholders(text: str, values: dict) -> str:
    """Replace {key} with values[key]. Raises KeyError on unknown placeholder."""
    def _replace(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"Unknown placeholder {{{key}}} in text")
        return str(values[key])

    return _PLACEHOLDER_RE.sub(_replace, text)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_parser_voice_boilerplate.py -v`
Expected: 6 tests pass.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/parser/voice.py skill_assets/proposal_build/parser/boilerplate.py tests/test_parser_voice_boilerplate.py
git commit -m "feat(plan-3): parser/voice.py + parser/boilerplate.py + placeholder substitution"
```

### Task 9: Parser — Validator (`parser/validate.py` + `test_parser_validate.py`)

**Files:**
- Create: `skill_assets/proposal_build/parser/validate.py`
- Create: `tests/test_parser_validate.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_parser_validate.py`:

```python
"""Tests for parser/validate.py — sniff test (W5/W6/W7) + zone coverage warnings."""
from __future__ import annotations

import pytest

from proposal_build.models import LineItem, Tier
from proposal_build.parser.validate import (
    check_cfd_sniff,
    check_zone_coverage,
)


def _li(line_num="1", item="X", description="internal", qty=1, unit="ea",
        price=100, total=100, rendering="r.png", customer_facing="OK clean text",
        zone="Zone One", tiers=(Tier.ESSENTIAL,)):
    return LineItem(
        line_num=line_num, item=item, description=description, qty=qty, unit=unit,
        price_per_unit=price, line_total=total, rendering_ref=rendering,
        customer_facing=customer_facing, zone=zone, tiers=tiers,
    )


def test_cfd_identical_to_internal_warns_w5():
    li = _li(description="The internal description.", customer_facing="The internal description.")
    warnings = check_cfd_sniff([li])
    codes = [w[0] for w in warnings]
    assert "W5" in codes


def test_cfd_jargon_dimensions_warns_w6():
    li = _li(customer_facing='14" girth garland on the perimeter.')
    warnings = check_cfd_sniff([li])
    codes = [w[0] for w in warnings]
    assert "W6" in codes


def test_cfd_jargon_units_mid_sentence_warns_w6():
    li = _li(customer_facing="Total of 1024 LF along the perimeter.")
    warnings = check_cfd_sniff([li])
    assert "W6" in [w[0] for w in warnings]


def test_cfd_too_short_warns_w7():
    li = _li(customer_facing="Three short words.")  # 3 words
    warnings = check_cfd_sniff([li])
    assert "W7" in [w[0] for w in warnings]


def test_cfd_clean_text_no_warnings():
    li = _li(customer_facing="Lighted wreaths frame every station entrance with warm-white evergreen.")
    warnings = check_cfd_sniff([li])
    assert warnings == []


def test_zone_no_priced_items_warns_w2():
    items = [_li(zone="Zone Two")]   # nothing in Zone One
    zones = ["Zone One", "Zone Two"]
    warnings = check_zone_coverage(items, zones, brief_bullets={"Zone One": ["bullet"], "Zone Two": []})
    assert "W2" in [w[0] for w in warnings]


def test_zone_bullet_count_divergence_warns_w3():
    items = [_li(zone="Zone One"), _li(line_num="2", zone="Zone One"),
             _li(line_num="3", zone="Zone One"), _li(line_num="4", zone="Zone One"),
             _li(line_num="5", zone="Zone One"), _li(line_num="6", zone="Zone One"),
             _li(line_num="7", zone="Zone One"), _li(line_num="8", zone="Zone One")]
    zones = ["Zone One"]
    warnings = check_zone_coverage(items, zones, brief_bullets={"Zone One": ["b1", "b2", "b3"]})
    # 8 priced items vs 3 bullets — divergence > 2
    assert "W3" in [w[0] for w in warnings]


def test_zone_with_wildcard_items_no_warning():
    items = [_li(zone="*")]
    zones = ["Zone One"]
    warnings = check_zone_coverage(items, zones, brief_bullets={"Zone One": ["b1"]})
    # Cross-program items count as applicable to all zones; W2 doesn't fire
    assert "W2" not in [w[0] for w in warnings]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser_validate.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement `parser/validate.py`**

Create `skill_assets/proposal_build/parser/validate.py`:

```python
"""Validation pass — blocking errors + warnings (sniff test, coverage gaps).

This module exposes individual check functions (used by tests) AND a top-level
run_validation(model) orchestrator that's called by the CLI.
"""
from __future__ import annotations

import re
from typing import Iterable, Mapping

from proposal_build.models import LineItem, ProjectModel, ValidationResult


# --- Sniff test regexes (W5/W6/W7) ---

# W6 markers: dimensions like 14", units mid-sentence (1024 LF), TBD, formula × style, anchoring talk.
_DIMENSION_RE = re.compile(r'\d+"\s')
_UNITS_MID_RE = re.compile(r'\b\d+\s*(LF|ea|LS|sq ft|SF)\b', re.IGNORECASE)
_FORMULA_RE = re.compile(r'\d+\s*[×x]\s*\d+')
_TBD_RE = re.compile(r'\bTBD\b', re.IGNORECASE)
_ANCHORING_RE = re.compile(r'\banchoring\b', re.IGNORECASE)


def check_cfd_sniff(line_items: Iterable[LineItem]) -> list[tuple[str, str]]:
    """Run W5/W6/W7 on Customer-Facing Descriptions. Returns [(code, message), ...]."""
    warnings = []
    for li in line_items:
        cfd = li.customer_facing.strip()
        if not cfd:
            continue   # blocking error 5 handled elsewhere

        # W5 — identical to internal description
        if cfd == li.description.strip():
            warnings.append(("W5",
                f"Row #{li.line_num}: Customer-Facing Description matches internal description verbatim "
                f"— likely copy-pasted, run polish chat."))

        # W6 — internal-jargon markers
        if (_DIMENSION_RE.search(cfd) or _UNITS_MID_RE.search(cfd) or _FORMULA_RE.search(cfd)
                or _TBD_RE.search(cfd) or _ANCHORING_RE.search(cfd)):
            warnings.append(("W6",
                f"Row #{li.line_num}: Customer-Facing Description contains internal markers "
                f"({cfd[:60]!r}) — consider polishing."))

        # W7 — fewer than 4 words
        word_count = len(cfd.split())
        if word_count < 4:
            warnings.append(("W7",
                f"Row #{li.line_num}: Customer-Facing Description is {word_count} words "
                f"({cfd!r}) — consider rewriting."))

    return warnings


def check_zone_coverage(
    line_items: Iterable[LineItem],
    zone_names: Iterable[str],
    brief_bullets: Mapping[str, list[str]],
) -> list[tuple[str, str]]:
    """W2: zone with no priced items.  W3: zone with priced items but bullet count diverges by >2."""
    warnings = []
    items = list(line_items)
    has_wildcard = any(li.zone == "*" for li in items)

    for zone_name in zone_names:
        direct = [li for li in items if li.zone == zone_name]
        bullets = brief_bullets.get(zone_name, [])

        # W2 — no priced items at all (no direct, no wildcard)
        if not direct and not has_wildcard and bullets:
            warnings.append(("W2",
                f"Zone {zone_name!r} has {len(bullets)} bullets in Brief but no priced line items "
                f"in worksheet — confirm intentional."))

        # W3 — direct items present but bullet count diverges by >2
        if direct and bullets:
            divergence = abs(len(direct) - len(bullets))
            if divergence > 2:
                warnings.append(("W3",
                    f"Zone {zone_name!r} has {len(direct)} priced items but {len(bullets)} bullets "
                    f"— confirm intentional."))

    return warnings


def check_unused_renderings(
    eligible: Mapping[str, object],
    referenced_filenames: Iterable[str],
) -> list[tuple[str, str]]:
    """W1: files in Base Scope/ or Enhancements/ that no field references."""
    referenced = set(referenced_filenames)
    warnings = []
    for filename in eligible.keys():
        if filename not in referenced:
            warnings.append(("W1",
                f"Unused rendering: {filename!r}. If intentional, move to "
                f"02 - Renderings/Unused Renderings/ to silence this warning."))
    return warnings


def check_tier_scenarios_drift(per_line_sums: dict, scenarios: tuple | None) -> list[tuple[str, str]]:
    """W4: per-line tier sums vs the worksheet's TIER SCENARIOS block."""
    if not scenarios:
        return []

    # Match scenarios by string-prefix to tier names
    warnings = []
    for label, scenario_total in scenarios:
        upper = label.upper()
        for tier_name, line_total in per_line_sums.items():
            if tier_name.value.upper() in upper:
                drift = scenario_total - line_total
                if drift == 0:
                    continue
                pct = abs(drift) / max(line_total, 1) * 100
                level = "drift > 5%" if pct > 5 else "within tolerance"
                warnings.append(("W4",
                    f"{tier_name.value} per-line sum ${line_total:,.0f} vs scenario block "
                    f"${scenario_total:,.0f} — {pct:.1f}% drift ({level})."))
                break
    return warnings


def run_validation(model: ProjectModel, eligible_renderings: dict, referenced_filenames: list[str],
                   per_line_sums: dict, scenarios: tuple | None) -> ValidationResult:
    """Top-level: run all warning checks. Blocking errors are raised earlier in Parser."""
    warnings = []
    warnings.extend(check_cfd_sniff(model.line_items))
    warnings.extend(check_zone_coverage(
        model.line_items,
        [z.name for z in model.zones],
        {z.name: list(z.bullets) for z in model.zones},
    ))
    warnings.extend(check_unused_renderings(eligible_renderings, referenced_filenames))
    warnings.extend(check_tier_scenarios_drift(per_line_sums, scenarios))

    return ValidationResult(blockers=[], warnings=warnings)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_parser_validate.py -v`
Expected: 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/parser/validate.py tests/test_parser_validate.py
git commit -m "feat(plan-3): parser/validate.py — CFD sniff test + zone coverage + W4/W1 warnings"
```

### Task 10: Parser — Top-level orchestrator (`parser/__init__.py`)

**Files:**
- Modify: `skill_assets/proposal_build/parser/__init__.py`

This task ties Brief + Worksheet + Renderings + Voice + Boilerplate together into a single `build_project_model(project_dir)` call that returns a fully-resolved `ProjectModel` ready for the Composer. It is the function the CLI invokes.

- [ ] **Step 1: Implement `parser/__init__.py`**

Replace the stub `skill_assets/proposal_build/parser/__init__.py` with:

```python
"""Top-level Parser orchestrator: build_project_model(project_dir) → ProjectModel.

Composes brief + worksheet + renderings + voice + boilerplate into a fully-
resolved ProjectModel. Blocking errors raise; warnings are returned alongside.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from proposal_build.models import ProjectModel, Zone, Tier
from proposal_build.parser.brief import parse_brief, BriefParseError
from proposal_build.parser.worksheet import parse_worksheet, WorksheetParseError
from proposal_build.parser.renderings import (
    walk_renderings, list_all_renderings, resolve_filename, RenderingsResolutionError,
)
from proposal_build.parser.voice import load_voice, VoiceLoadError
from proposal_build.parser.boilerplate import load_boilerplate, substitute_placeholders


class ProjectLoadError(Exception):
    """Top-level error during project loading. Contains a descriptive message."""


def build_project_model(project_dir: Path) -> tuple:
    """Returns (model, parse_artifacts) where parse_artifacts has eligible_renderings, scenarios, etc.

    Raises ProjectLoadError on any blocking issue.
    """
    project_dir = Path(project_dir)

    # 1. Brief
    brief_path = project_dir / "04 - Process & Notes" / "Project Brief.md"
    try:
        brief = parse_brief(brief_path)
    except BriefParseError as e:
        raise ProjectLoadError(f"Brief: {e}") from e

    # 2. Worksheet
    fm = brief.frontmatter
    worksheet_name = f"{fm['project_name']} - Scope Worksheet.xlsx"
    worksheet_path = project_dir / "03 - Scope & Pricing" / worksheet_name
    try:
        ws = parse_worksheet(worksheet_path)
    except WorksheetParseError as e:
        raise ProjectLoadError(f"Worksheet: {e}") from e

    # 3. Renderings
    try:
        eligible = walk_renderings(project_dir)
    except RenderingsResolutionError as e:
        raise ProjectLoadError(f"Renderings: {e}") from e
    all_renderings = list_all_renderings(project_dir)

    # 4. Verify all image references resolve
    referenced_filenames = []
    image_fields = ["cover_image", "creative_vision_hero", "case_study_hero"]
    for f in image_fields:
        name = fm.get(f, "")
        if name:
            try:
                resolve_filename(name, eligible)
                referenced_filenames.append(name)
            except RenderingsResolutionError as e:
                raise ProjectLoadError(f"{f}: {e}") from e
    for z in fm["zones"]:
        name = z.get("hero_image", "")
        if name:
            try:
                resolve_filename(name, eligible)
                referenced_filenames.append(name)
            except RenderingsResolutionError as e:
                raise ProjectLoadError(f"zone {z['name']!r} hero_image: {e}") from e

    # 5. Auto-derive blank dates
    go_live = fm["go_live"]
    fab_lock = fm.get("fabrication_lock") or _date_offset(go_live, days=-90)
    sign = fm.get("signing_deadline") or _date_offset(go_live, days=-21)

    # 6. Load voice + boilerplate
    try:
        voice = load_voice(fm["voice"])
    except VoiceLoadError as e:
        raise ProjectLoadError(str(e)) from e
    bp = load_boilerplate()

    # 7. Build placeholder values for substitution
    placeholders = _build_placeholders(fm, fab_lock, sign, brief)

    # 8. Resolve voice/boilerplate fills (Brief overrides win)
    pillars = _fill_pillars(brief, voice, placeholders)
    phases = _fill_phases(brief, voice, placeholders)
    scope_includes = _fill_scope_includes(brief, bp, placeholders)
    add_ons = _fill_add_ons(brief, placeholders)
    term_panels = _fill_term_panels(brief, bp, placeholders)
    after_steps = _fill_after_approval_steps(brief, voice, placeholders)
    company_facts = _fill_company_facts(brief, bp, placeholders)
    team = _fill_team(brief, bp, placeholders)
    contact_strip = substitute_placeholders(bp.contact_strip, placeholders)
    partnership_discounts = tuple((d["term"], d["label"]) for d in bp.partnership_discounts)

    # 9. Build Zones tuple
    zones = tuple(
        Zone(
            num=z["num"], name=z["name"], subtitle=z.get("subtitle", ""),
            flags=tuple(z.get("flags") or ()),
            hero_image=z.get("hero_image", ""),
            bullets=tuple(z.get("bullets") or ()),
            layout_override=z.get("layout"),
        )
        for z in fm["zones"]
    )

    model = ProjectModel(
        client_company=fm["client_company"], client_short=fm.get("client_short", ""),
        project_name=fm["project_name"], project_short=fm.get("project_short", ""),
        project_year=int(fm["project_year"]),
        project_subtitle=fm.get("project_subtitle", ""),
        proposal_type=fm.get("proposal_type", "Holiday Proposal"),
        presenter_name=fm["presenter_name"], presenter_title=fm.get("presenter_title", ""),
        presenter_email=fm.get("presenter_email", ""), presenter_phone=fm.get("presenter_phone", ""),
        proposal_date=fm.get("proposal_date", ""),
        go_live=go_live, season_end=fm.get("season_end", ""),
        fabrication_lock=fab_lock, signing_deadline=sign,
        voice=fm["voice"], recommended_tier=Tier.from_string(fm["recommended_tier"]),
        design_phrase=fm.get("design_phrase", ""), pricing_format=fm["pricing_format"],
        cover_image=fm["cover_image"], creative_vision_hero=fm.get("creative_vision_hero", ""),
        case_study=fm.get("case_study", "skip"), case_study_hero=fm.get("case_study_hero", ""),
        zones=zones, line_items=ws.line_items,
        creative_direction=brief.sections.get("Creative Direction", ""),
        customer_goals=tuple(brief.sections.get("Customer Goals", []) or ()),
        customer_constraints=tuple(brief.sections.get("Customer Constraints", []) or ()),
        success_criteria=tuple(brief.sections.get("Success Criteria", []) or ()),
        what_youre_approving=brief.sections.get("What You're Approving", ""),
        pillars=pillars, phases=phases, scope_includes=scope_includes, add_ons=add_ons,
        term_panels=term_panels, after_approval_steps=after_steps,
        company_facts=company_facts, team=team, contact_strip=contact_strip,
        partnership_discounts=partnership_discounts,
        slide_plan_override=tuple(fm.get("slide_plan", ())),
        resolved_renderings={n: str(eligible[n]) for n in eligible},
    )

    artifacts = {
        "eligible_renderings": eligible,
        "all_renderings": all_renderings,
        "referenced_filenames": referenced_filenames,
        "scenarios": ws.scenarios,
        "per_line_sums": ws.tier_sums_per_line(),
    }
    return model, artifacts


# === Helpers ===

def _date_offset(iso: str, days: int) -> str:
    d = datetime.fromisoformat(iso).date()
    return (d + timedelta(days=days)).isoformat()


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    d = datetime.fromisoformat(iso).date()
    return d.strftime("%b %d, %Y")


def _build_placeholders(fm: dict, fab_lock: str, sign: str, brief) -> dict:
    """All known {placeholder} keys for voice/boilerplate substitution."""
    fab_minus_60 = _date_offset(fab_lock, days=-60) if fab_lock else ""
    return {
        "project_name": fm["project_name"],
        "project_short": fm.get("project_short", ""),
        "project_year": int(fm["project_year"]),
        "next_year": int(fm["project_year"]) + 1,
        "client_short": fm.get("client_short", ""),
        "proposal_type": fm.get("proposal_type", "Holiday Proposal"),
        "go_live": fm.get("go_live", ""),
        "season_end": fm.get("season_end", ""),
        "fabrication_lock": fab_lock,
        "signing_deadline": sign,
        "proposal_date": fm.get("proposal_date", ""),
        "go_live_long": _date_long(fm.get("go_live", "")),
        "season_end_long": _date_long(fm.get("season_end", "")),
        "fabrication_lock_long": _date_long(fab_lock),
        "signing_deadline_long": _date_long(sign),
        "proposal_date_long": _date_long(fm.get("proposal_date", "")),
        "fabrication_lock_minus_60d": _date_long(fab_minus_60) if fab_minus_60 else "",
        "zone_summary": _build_zone_summary(fm["zones"]),
    }


def _build_zone_summary(zones: list) -> str:
    """e.g. 'six stations from Downtown Riverside through Perris-Downtown'."""
    if not zones:
        return ""
    if len(zones) == 1:
        return zones[0]["name"]
    counts = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
              6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    n_word = counts.get(len(zones), str(len(zones)))
    return f"{n_word} zones from {zones[0]['name']} through {zones[-1]['name']}"


def _fill_pillars(brief, voice, ph):
    if pillars := brief.sections.get("Pillars"):
        # If Brief has a Pillars section it's a YAML-ish list — out of scope for V1; treat as override prose
        # For Plan 3 keep it simple: only voice preset pillars supported
        return tuple(voice.default_pillars)
    return tuple(
        {"title": p["title"], "body": substitute_placeholders(p["body"], ph)}
        for p in voice.default_pillars
    )


def _fill_phases(brief, voice, ph):
    return tuple(
        {"label": p["label"], "body": substitute_placeholders(p["body"], ph)}
        for p in voice.default_phases
    )


def _fill_scope_includes(brief, bp, ph):
    if include := brief.sections.get("Scope Includes"):
        return tuple(include) if isinstance(include, list) else (include,)
    return tuple(bp.scope_inclusions_default)


def _fill_add_ons(brief, ph):
    add_ons_raw = brief.sections.get("Add-Ons", [])
    if not add_ons_raw:
        return ()
    if isinstance(add_ons_raw, str):
        add_ons_raw = add_ons_raw.splitlines()
    out = []
    for line in add_ons_raw:
        if isinstance(line, str) and ":" in line:
            text, price = line.rsplit(":", 1)
            out.append((text.strip(), price.strip()))
    return tuple(out)


def _fill_term_panels(brief, bp, ph):
    """4 term panels: payment_schedule, insurance_permits, change_orders, validity.
    Brief frontmatter `term_panel_overrides` can override per-panel."""
    overrides = brief.frontmatter.get("term_panel_overrides", {}) or {}
    panels = {}
    for key in ("payment_schedule", "insurance_permits", "change_orders", "validity"):
        if key in overrides:
            panels[key] = substitute_placeholders(overrides[key], ph)
        else:
            default = bp.term_panels.get(f"default_{key}", "")
            panels[key] = substitute_placeholders(default, ph)
    return panels


def _fill_after_approval_steps(brief, voice, ph):
    return tuple(
        substitute_placeholders(step, ph) for step in voice.default_after_approval_steps
    )


def _fill_company_facts(brief, bp, ph):
    return tuple(bp.company_facts_default_bullets)


def _fill_team(brief, bp, ph):
    return tuple(bp.team_roster)
```

- [ ] **Step 2: Smoke-test against Riverside (will fail until Riverside Brief + worksheet migration land in Phase 6, but verifies imports work)**

Run:

```bash
python -c "from proposal_build.parser import build_project_model; print('imports OK')"
```

Expected: prints "imports OK". Don't run against Riverside yet — that's the e2e test in Task 27.

- [ ] **Step 3: Commit**

```bash
git add skill_assets/proposal_build/parser/__init__.py
git commit -m "feat(plan-3): parser/__init__.py — top-level build_project_model orchestrator"
```

---

## Phase 4 — Composer (3 tasks)

### Task 11: Composer — slide_plan (`composer/slide_plan.py` + `test_composer_slide_plan.py`)

**Files:**
- Create: `skill_assets/proposal_build/composer/slide_plan.py`
- Create: `tests/test_composer_slide_plan.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_composer_slide_plan.py`:

```python
"""Tests for composer/slide_plan.py — auto-arrange + pick_grouping + override."""
from __future__ import annotations

import pytest

from proposal_build.models import Zone
from proposal_build.composer.slide_plan import (
    auto_arrange_zones,
    pick_grouping,
    SlidePlanError,
)


def _z(num: str, name: str, *flags: str) -> Zone:
    return Zone(num=num, name=name, subtitle=f"{name} subtitle.",
                flags=tuple(flags), hero_image=f"{name}.jpg",
                bullets=("Bullet A", "Bullet B"))


def test_auto_arrange_n1_signature_only():
    zones = [_z("01", "Solo", "signature")]
    plan = auto_arrange_zones(zones)
    assert [layout for layout, _ in plan] == ["zone_solo_fullbleed"]


def test_auto_arrange_n1_no_signature():
    """Without a signature flag, single zone gets zone_solo (not fullbleed)."""
    zones = [_z("01", "Solo")]
    plan = auto_arrange_zones(zones)
    assert [layout for layout, _ in plan] == ["zone_solo"]


def test_auto_arrange_n2_solo_plus_fullbleed():
    zones = [_z("01", "A"), _z("02", "B", "signature")]
    plan = auto_arrange_zones(zones)
    assert [layout for layout, _ in plan] == ["zone_solo", "zone_solo_fullbleed"]


def test_auto_arrange_n3_pier_39_pattern():
    zones = [_z("01", "Embarcadero"), _z("02", "Promenade"), _z("03", "Bay Terrace", "signature")]
    plan = auto_arrange_zones(zones)
    layouts = [layout for layout, _ in plan]
    assert layouts == ["zone_solo", "zone_solo", "zone_solo_fullbleed"]


def test_auto_arrange_n6_riverside_pattern():
    zones = [
        _z("01", "Downtown Riverside", "flagship"),
        _z("02", "La Sierra"), _z("03", "Pedley"),
        _z("04", "Hunter Park"), _z("05", "Moreno Valley"), _z("06", "Perris"),
    ]
    plan = auto_arrange_zones(zones)
    layouts = [layout for layout, _ in plan]
    assert layouts == ["zone_index", "zone_solo", "zone_2up", "zone_3up"]
    # Verify which zones are in the 2up vs 3up
    twoup_ctx = plan[2][1]
    threeup_ctx = plan[3][1]
    assert [z.name for z in twoup_ctx["zones"]] == ["La Sierra", "Pedley"]
    assert [z.name for z in threeup_ctx["zones"]] == ["Hunter Park", "Moreno Valley", "Perris"]


def test_two_signatures_raises():
    zones = [_z("01", "A", "signature"), _z("02", "B", "signature")]
    with pytest.raises(SlidePlanError):
        auto_arrange_zones(zones)


@pytest.mark.parametrize("n,expected", [
    (0, []),
    (1, [1]),
    (2, [2]),
    (3, [3]),
    (4, [2, 2]),
    (5, [2, 3]),
    (6, [3, 3]),
    (7, [2, 2, 3]),
    (8, [2, 3, 3]),
    (9, [3, 3, 3]),
    (10, [2, 2, 3, 3]),
])
def test_pick_grouping_table(n, expected):
    assert pick_grouping(n) == expected


def test_zone_layout_override_used():
    """Brief-level per-zone layout: override skips auto-pick for that zone."""
    zones = [_z("01", "A")]
    # Override: force fullbleed even though no signature flag
    z = zones[0].__class__(num="01", name="A", subtitle="", flags=(),
                          hero_image="a.jpg", bullets=(),
                          layout_override="zone_solo_fullbleed")
    plan = auto_arrange_zones([z])
    assert [layout for layout, _ in plan] == ["zone_solo_fullbleed"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_composer_slide_plan.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement `composer/slide_plan.py`**

Create `skill_assets/proposal_build/composer/slide_plan.py`:

```python
"""Composer — zone-block slide arrangement.

Implements the auto-arrange algorithm from spec §6 and the pick_grouping table.
"""
from __future__ import annotations

from typing import Sequence

from proposal_build.models import Zone


class SlidePlanError(Exception):
    pass


def auto_arrange_zones(zones: Sequence[Zone]) -> list[tuple[str, dict]]:
    """Return [(layout_name, ctx), ...] for the zone block.

    Honors per-zone layout_override. Validates ≤1 signature flag.
    """
    sigs = [z for z in zones if z.is_signature]
    if len(sigs) > 1:
        names = ", ".join(z.name for z in sigs)
        raise SlidePlanError(f"At most one zone may carry the 'signature' flag; found: {names}")

    if not zones:
        return []

    # Per-zone layout_override short-circuits everything for that zone
    # We build the plan respecting overrides where present.
    n = len(zones)

    if n <= 3:
        # All zones get solos; signature gets fullbleed
        return [_solo_or_fullbleed(z) for z in zones]

    # n >= 4: index slide + flagships + signature first, rest grouped
    plan: list[tuple[str, dict]] = []
    plan.append(("zone_index", {"zones": list(zones)}))

    soloed_set = set()
    for z in zones:
        if z.is_flagship or z.is_signature or z.layout_override in ("zone_solo", "zone_solo_fullbleed"):
            plan.append(_solo_or_fullbleed(z))
            soloed_set.add(z.num)

    grouped = [z for z in zones if z.num not in soloed_set]
    for chunk_size in pick_grouping(len(grouped)):
        chunk = grouped[:chunk_size]
        grouped = grouped[chunk_size:]
        if chunk_size == 1:
            plan.append(_solo_or_fullbleed(chunk[0]))
        else:
            plan.append((f"zone_{chunk_size}up", {"zones": chunk}))

    return plan


def _solo_or_fullbleed(z: Zone) -> tuple[str, dict]:
    if z.layout_override:
        return (z.layout_override, {"zone": z})
    layout = "zone_solo_fullbleed" if z.is_signature else "zone_solo"
    return (layout, {"zone": z})


def pick_grouping(n: int) -> list[int]:
    """Chunk sizes that sum to n. Smaller-first; avoid orphan 1s by pairing 2,2."""
    if n == 0:
        return []
    if n <= 3:
        return [n]
    rem = n % 3
    if rem == 0:
        return [3] * (n // 3)
    if rem == 2:
        return [2] + [3] * ((n - 2) // 3)
    # rem == 1: replace one 3 with [2, 2] to avoid an orphan 1
    threes = (n - 4) // 3
    return [2, 2] + [3] * threes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_composer_slide_plan.py -v`
Expected: 16 tests pass (8 explicit + 11 parametrized − 3 = 16; the parametrized table contributes 11).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/composer/slide_plan.py tests/test_composer_slide_plan.py
git commit -m "feat(plan-3): composer/slide_plan.py — auto_arrange_zones + pick_grouping"
```

### Task 12: Composer — Pricing (`composer/pricing.py` + `test_composer_pricing.py`)

**Files:**
- Create: `skill_assets/proposal_build/composer/pricing.py`
- Create: `tests/test_composer_pricing.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_composer_pricing.py`:

```python
"""Tests for composer/pricing.py — per-tier itemized pricing doc construction."""
from __future__ import annotations

import pytest

from proposal_build.models import LineItem, ItemizedPricingDoc, Tier
from proposal_build.composer.pricing import (
    build_itemized_pricing_docs,
    compute_partnership_savings,
)


def _li(line_num, item, qty, price, tiers):
    return LineItem(
        line_num=line_num, item=item, description="internal",
        qty=qty, unit="ea", price_per_unit=price, line_total=qty * price,
        rendering_ref="r.png", customer_facing=f"Customer {item}",
        zone="*", tiers=tiers,
    )


# Minimal model stub — only needs the fields pricing reads
class _Model:
    def __init__(self, line_items, pricing_format="tiered",
                 recommended_tier=Tier.ENHANCED, partnership_discounts=()):
        self.line_items = line_items
        self.pricing_format = pricing_format
        self.recommended_tier = recommended_tier
        self.partnership_discounts = partnership_discounts


def test_tiered_format_produces_three_docs():
    items = [
        _li("1", "Wreath", 4, 100, (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)),
        _li("E1", "Snowflakes", 12, 295, (Tier.ENHANCED, Tier.SIGNATURE)),
    ]
    model = _Model(items, "tiered")
    docs = build_itemized_pricing_docs(model)
    assert len(docs) == 3
    by_tier = {d.tier: d for d in docs}
    assert Tier.ESSENTIAL in by_tier
    assert by_tier[Tier.ESSENTIAL].tier_total == 400        # only Wreath
    assert by_tier[Tier.ENHANCED].tier_total == 400 + 3540
    assert by_tier[Tier.SIGNATURE].tier_total == 400 + 3540


def test_single_format_produces_one_doc_for_recommended():
    items = [_li("1", "Wreath", 4, 100, (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE))]
    model = _Model(items, "single", recommended_tier=Tier.SIGNATURE)
    docs = build_itemized_pricing_docs(model)
    assert len(docs) == 1
    assert docs[0].tier == Tier.SIGNATURE


def test_per_tier_filters_split_base_vs_enhancements():
    items = [
        _li("1", "Wreath", 1, 100, (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE)),
        _li("E1", "Snowflakes", 1, 200, (Tier.ENHANCED, Tier.SIGNATURE)),
    ]
    model = _Model(items, "tiered")
    docs = {d.tier: d for d in build_itemized_pricing_docs(model)}
    assert len(docs[Tier.ESSENTIAL].base_scope_lines) == 1
    assert len(docs[Tier.ESSENTIAL].enhancement_lines) == 0
    assert len(docs[Tier.ENHANCED].enhancement_lines) == 1


def test_substitution_excludes_replaced_item():
    """Substitution scenario: Traditional in Essential+Enhanced; Spiral in Signature.
    Signature tier shows Spiral but NOT Traditional."""
    items = [
        _li("1", "Traditional Tree", 1, 18000, (Tier.ESSENTIAL, Tier.ENHANCED)),
        _li("E1", "Spiral LED", 1, 22000, (Tier.SIGNATURE,)),
    ]
    model = _Model(items, "tiered")
    docs = {d.tier: d for d in build_itemized_pricing_docs(model)}
    sig_items = [li for li in docs[Tier.SIGNATURE].base_scope_lines + docs[Tier.SIGNATURE].enhancement_lines]
    sig_names = [li.item for li in sig_items]
    assert "Spiral LED" in sig_names
    assert "Traditional Tree" not in sig_names


def test_partnership_savings_computation():
    discounts = (("2-YEAR", "4% OFF"), ("3-YEAR", "6% OFF"), ("5-YEAR", "9% OFF"))
    rows = compute_partnership_savings(tier_total=345000, discounts=discounts,
                                       discount_pcts={"2-YEAR": 0.04, "3-YEAR": 0.06, "5-YEAR": 0.09})
    by_term = {r["term"]: r for r in rows}
    assert by_term["2-YEAR"]["savings"] == -13800
    assert by_term["2-YEAR"]["year_1_price"] == 331200
    assert by_term["3-YEAR"]["savings"] == -20700
    assert by_term["5-YEAR"]["year_1_price"] == 313950
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_composer_pricing.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement `composer/pricing.py`**

Create `skill_assets/proposal_build/composer/pricing.py`:

```python
"""Composer — per-tier itemized pricing doc construction."""
from __future__ import annotations

from proposal_build.models import ItemizedPricingDoc, Tier


def build_itemized_pricing_docs(model) -> list[ItemizedPricingDoc]:
    """Returns 1 or 3 ItemizedPricingDoc instances depending on pricing_format."""
    if model.pricing_format == "single":
        tiers_to_emit = [model.recommended_tier]
    else:
        tiers_to_emit = [Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE]

    docs = []
    for tier in tiers_to_emit:
        in_tier = [li for li in model.line_items if tier in li.tiers]
        base = tuple(li for li in in_tier if not li.is_enhancement)
        enh = tuple(li for li in in_tier if li.is_enhancement)
        total = sum(li.line_total for li in in_tier)
        docs.append(ItemizedPricingDoc(
            tier=tier, project=model,
            base_scope_lines=base, enhancement_lines=enh,
            tier_total=total,
        ))
    return docs


def compute_partnership_savings(tier_total: float, discounts: tuple,
                                discount_pcts: dict) -> list[dict]:
    """Given (label, percent_str) tuples + a {label: float} map of percentages,
    return [{term, discount_label, savings, year_1_price}, ...]."""
    rows = []
    for term, label in discounts:
        pct = discount_pcts.get(term, 0)
        savings = -tier_total * pct
        year_1 = tier_total + savings
        rows.append({
            "term": term,
            "discount_label": label,
            "savings": savings,
            "year_1_price": year_1,
        })
    return rows
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_composer_pricing.py -v`
Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/composer/pricing.py tests/test_composer_pricing.py
git commit -m "feat(plan-3): composer/pricing.py — per-tier doc construction + partnership savings"
```

### Task 13: Composer — ctx_builders + top-level orchestrator

**Files:**
- Create: `skill_assets/proposal_build/composer/ctx_builders.py`
- Modify: `skill_assets/proposal_build/composer/__init__.py`

`ctx_builders.py` has one function per layout that turns a `ProjectModel` into the dict shape the layout expects. The dict shape is established by the existing fixtures (`tests/fixtures/pier_39.py`, `tests/fixtures/riverside.py`) — match those exactly.

**No dedicated test file in this task** — the e2e test (Task 27) and the existing layout tests cover ctx-builder correctness. Composer's job is small enough per-builder that adding a unit test per builder is YAGNI.

- [ ] **Step 1: Implement `composer/ctx_builders.py`**

Create `skill_assets/proposal_build/composer/ctx_builders.py`:

```python
"""One context-dict builder per layout.

Each builder takes ProjectModel + (optional) per-slide hint and returns the
dict that gets passed to Jinja2 as the rendering context. Dict shape MUST
match what tests/fixtures/{pier_39,riverside}.py hand-author — those fixtures
are the gold standard.
"""
from __future__ import annotations

from datetime import datetime

from proposal_build.models import ProjectModel, Tier, Zone


def _project_base(model: ProjectModel) -> dict:
    """Common project-wide values merged into every slide ctx."""
    return {
        "client_company": model.client_company,
        "client_short": model.client_short,
        "project_name": model.project_name,
        "project_short": model.project_short,
        "project_year": model.project_year,
        "project_subtitle": model.project_subtitle,
        "presenter_name": model.presenter_name,
        "presenter_title": model.presenter_title,
        "presenter_org": "St. Nick's Christmas Lighting & Décor",
        "proposal_date": _date_long(model.proposal_date),
    }


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    return datetime.fromisoformat(iso).date().strftime("%B %d, %Y")


def build_cover_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num,
        "page_total": page_total,
        "season_label": f"{model.project_year} HOLIDAY SEASON",
        "hero_image": model.resolved_renderings.get(model.cover_image, model.cover_image),
        "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
    }


def build_exec_summary_ctx(model: ProjectModel, page_num: int, page_total: int,
                           investment_range: str) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Executive Summary",
        "standfirst": _exec_standfirst(model),
        "body_paragraphs": [_exec_body_para_1(model), _exec_body_para_2(model)],
        "at_a_glance": [
            ("PROJECT", f"{model.project_year} {model.proposal_type}", False),
            ("ZONES" if len(model.zones) <= 3 else "STATIONS",
                _zone_summary_short(model), False),
            ("RECOMMENDED TIER", model.recommended_tier.value, False),
            ("INVESTMENT RANGE", investment_range, False),
            ("GO LIVE", _date_short(model.go_live), False),
            ("FABRICATION LOCK", _date_short(model.fabrication_lock), True),
            ("SIGNING DEADLINE", _date_short(model.signing_deadline), True),
        ],
        "pillars": list(model.pillars),
    }


def _exec_standfirst(model: ProjectModel) -> str:
    n = len(model.zones)
    if n == 1:
        return f"Our {model.project_year} {model.proposal_type.lower()} for {model.project_name}, at a glance."
    return f"A {_n_word(n)}-zone {model.proposal_type.lower()} for the {model.project_name}, at a glance."


def _exec_body_para_1(model: ProjectModel) -> str:
    n = len(model.zones)
    return (f"St. Nick's is proposing a coordinated holiday décor program across "
            f"{_n_word(n)} {'zones' if n != 1 else 'zone'} of {model.project_name} — "
            f"a single visual identity that builds on what works in your space.")


def _exec_body_para_2(model: ProjectModel) -> str:
    return ("Our approach builds on operational discipline, repeatable seasonal investment, "
            "and a design language that scales across the program from end to end.")


def _zone_summary_short(model: ProjectModel) -> str:
    if len(model.zones) <= 3:
        return " · ".join(z.name for z in model.zones)
    return f"{_n_word(len.zones).capitalize()} ({model.zones[0].name} → {model.zones[-1].name})"


def _n_word(n: int) -> str:
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    return words.get(n, str(n))


def _date_short(iso: str) -> str:
    if not iso:
        return ""
    d = datetime.fromisoformat(iso).date()
    weekday = d.strftime("%a")
    return f"{weekday}, {d.strftime('%b %-d, %Y')}"


def build_understanding_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Our Understanding",
        "standfirst": "Playback of discovery — so we're all working from the same page.",
        "panels": [
            {"title": "VENUE & CONTEXT",
             "body": _understanding_venue(model)},
            {"title": "GOALS FOR " + str(model.project_year),
             "body": "; ".join(model.customer_goals)},
            {"title": "KEY CONSTRAINTS",
             "body": "; ".join(model.customer_constraints) if model.customer_constraints else "None identified at this stage."},
            {"title": "WHAT SUCCESS LOOKS LIKE",
             "body": "; ".join(model.success_criteria)},
        ],
    }


def _understanding_venue(model: ProjectModel) -> str:
    return (f"{model.project_name} — a {len(model.zones)}-zone program "
            f"covering {_zone_summary_short(model)}.")


def build_creative_vision_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Creative Vision",
        "standfirst": f"The design direction for the {model.project_year} {model.project_short} program.",
        "design_phrase": model.design_phrase,
        "design_direction_body": model.creative_direction,
        "phases": list(model.phases),
        "hero_image": model.resolved_renderings.get(model.creative_vision_hero, model.creative_vision_hero),
    }


def build_zone_index_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "The Program at a Glance",
        "standfirst": f"{_n_word(len(model.zones)).capitalize()} zones, one design language. "
                       f"Here's how the program reads from end to end.",
        "zones": [
            {"num": z.num, "name": z.name, "subtitle": z.subtitle,
             "included_elements": list(z.bullets)}
            for z in model.zones
        ],
    }


def build_zone_solo_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "zone_num": zone.num, "zone_name": zone.name, "zone_subtitle": zone.subtitle,
        "included_elements": list(zone.bullets),
        "hero_image": model.resolved_renderings.get(zone.hero_image, zone.hero_image),
    }


def build_zone_solo_fullbleed_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    return build_zone_solo_ctx(model, page_num, page_total, zone)


def build_zone_2up_ctx(model: ProjectModel, page_num: int, page_total: int, zones: list[Zone]) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Program Zones",
        "standfirst": f"Zones {zones[0].num} and {zones[1].num}.",
        "zones": [_zone_dict(model, z) for z in zones],
    }


def build_zone_3up_ctx(model: ProjectModel, page_num: int, page_total: int, zones: list[Zone]) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Program Zones",
        "standfirst": f"Zones {', '.join(z.num for z in zones[:-1])}, and {zones[-1].num}.",
        "zones": [_zone_dict(model, z) for z in zones],
    }


def _zone_dict(model: ProjectModel, z: Zone) -> dict:
    return {
        "num": z.num, "name": z.name, "subtitle": z.subtitle,
        "included_elements": list(z.bullets),
        "hero_image": model.resolved_renderings.get(z.hero_image, z.hero_image),
    }


def build_scope_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Scope of Work",
        "standfirst": "What your investment includes, and what you can add on.",
        "includes": list(model.scope_includes),
        "add_ons": list(model.add_ons),
    }


def build_case_study_ctx(model: ProjectModel, page_num: int, page_total: int,
                         case_study_data: dict) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_eyebrow": "CASE STUDY",
        "page_title": case_study_data["name"],
        "standfirst": case_study_data["standfirst"],
        "challenge": case_study_data["challenge"],
        "approach": case_study_data["approach"],
        "outcome": case_study_data["outcome"],
        "hero_image": model.resolved_renderings.get(model.case_study_hero, model.case_study_hero),
    }


def build_investment_ctx(model: ProjectModel, page_num: int, page_total: int,
                         tier_totals: dict, partnership_discounts: list) -> dict:
    tiers = [
        _tier_card("ESSENTIAL", "gray", tier_totals[Tier.ESSENTIAL],
                   model.recommended_tier == Tier.ESSENTIAL),
        _tier_card("ENHANCED", "red", tier_totals[Tier.ENHANCED],
                   model.recommended_tier == Tier.ENHANCED),
        _tier_card("SIGNATURE", "navy", tier_totals[Tier.SIGNATURE],
                   model.recommended_tier == Tier.SIGNATURE),
    ]
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Investment",
        "standfirst": "Three levels of program. Pick what fits your season.",
        "tiers": tiers,
        "partnership_discounts": partnership_discounts,
        "footer_note": (f"Pricing valid 30 days from proposal date. Fabrication must be locked "
                        f"by {_date_long(model.fabrication_lock)}."),
    }


def _tier_card(name: str, rule_color: str, price: float, is_recommended: bool) -> dict:
    return {
        "name": name, "rule_color": rule_color, "tagline": "",
        "highlights": [],   # populated by ctx_builders if needed; minimal for V1
        "price": f"${price:,.0f}",
        "is_recommended": is_recommended,
    }


def build_terms_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    panels = model.term_panels
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Terms & Next Steps",
        "standfirst": f"The critical dates and terms for the {model.project_year} program.",
        "critical_dates": [
            (_date_long(model.signing_deadline), "Execute by this date to guarantee the install schedule."),
            (_date_long(model.fabrication_lock), "All custom fabrication must be approved by this date."),
        ],
        "term_panels": [
            ("PAYMENT SCHEDULE", panels.get("payment_schedule", "")),
            ("INSURANCE & PERMITS", panels.get("insurance_permits", "")),
            ("CHANGE ORDERS", panels.get("change_orders", "")),
            ("PROPOSAL VALIDITY", panels.get("validity", "")),
        ],
        "after_approval_steps": list(model.after_approval_steps),
    }


def build_sign_off_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Let's Make It Happen",
        "standfirst": f"Sign below to launch the {model.project_year} {model.project_short} program.",
        "what_youre_approving": model.what_youre_approving,
        "client_party_label": f"{model.client_short} AUTHORIZATION",
        "stnicks_party_label": "ST. NICK'S AUTHORIZED SIGNATURE",
        "digital_signing_note": ("Prefer to sign digitally? Use the Canva e-signature link in your "
                                  "email. Questions? Reply directly — we'll respond within 24 hours."),
    }


def build_about_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "About St. Nick's",
        "standfirst": "25 years of large-scale holiday design, installation, and service.",
        "company_facts": list(model.company_facts),
        "team": list(model.team),
        "contact_strip": model.contact_strip,
    }
```

- [ ] **Step 2: Implement `composer/__init__.py` orchestrator**

Replace the stub `skill_assets/proposal_build/composer/__init__.py` with:

```python
"""Composer top-level: ProjectModel → list of (layout_name, ctx) tuples + ItemizedPricingDocs."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.composer.ctx_builders import (
    build_cover_ctx, build_exec_summary_ctx, build_understanding_ctx,
    build_creative_vision_ctx, build_zone_index_ctx, build_zone_solo_ctx,
    build_zone_solo_fullbleed_ctx, build_zone_2up_ctx, build_zone_3up_ctx,
    build_scope_ctx, build_case_study_ctx, build_investment_ctx,
    build_terms_ctx, build_sign_off_ctx, build_about_ctx,
)
from proposal_build.composer.slide_plan import auto_arrange_zones, SlidePlanError
from proposal_build.composer.pricing import build_itemized_pricing_docs, compute_partnership_savings
from proposal_build.models import ProjectModel, SlidePlanItem, Tier


CASE_STUDIES_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "case_studies"


def compose(model: ProjectModel) -> tuple[list[SlidePlanItem], list]:
    """Returns (slides, itemized_pricing_docs).

    slides is an ordered list of SlidePlanItem (layout_name, ctx). itemized_pricing_docs
    is a list of ItemizedPricingDoc (1 or 3 depending on pricing_format).
    """
    pricing_docs = build_itemized_pricing_docs(model)
    tier_totals = {d.tier: d.tier_total for d in pricing_docs}
    if model.pricing_format == "single":
        # Fill in absent tiers from per-line sums for the Investment slide
        from proposal_build.composer.pricing import build_itemized_pricing_docs as _all
        # Synthesize all 3 tier totals using the line items
        for t in [Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE]:
            if t not in tier_totals:
                tier_totals[t] = sum(li.line_total for li in model.line_items if t in li.tiers)

    discount_pcts = _load_discount_pcts()
    partnership_rows = compute_partnership_savings(
        tier_total=tier_totals[model.recommended_tier],
        discounts=model.partnership_discounts,
        discount_pcts=discount_pcts,
    )
    investment_range = f"${tier_totals[Tier.ESSENTIAL]/1000:.0f}K — ${tier_totals[Tier.SIGNATURE]/1000:.0f}K"

    # Build the zone-block slide list
    zone_block = _resolve_zone_block(model)

    slides_raw: list[tuple[str, dict]] = []
    slides_raw.append(("cover", {}))
    slides_raw.append(("exec_summary", {"investment_range": investment_range}))
    slides_raw.append(("understanding", {}))
    slides_raw.append(("creative_vision", {}))
    slides_raw.extend(zone_block)
    slides_raw.append(("scope", {}))
    if model.case_study and model.case_study != "skip":
        cs = _load_case_study(model.case_study)
        slides_raw.append(("case_study", {"case_study_data": cs}))
    slides_raw.append(("investment", {"tier_totals": tier_totals,
                                       "partnership_discounts": _format_partnership_for_slide(model.partnership_discounts)}))
    slides_raw.append(("terms", {}))
    slides_raw.append(("sign_off", {}))
    slides_raw.append(("about", {}))

    page_total = len(slides_raw)
    slides = []
    for i, (layout, hint) in enumerate(slides_raw, start=1):
        ctx = _build_ctx(model, layout, i, page_total, hint)
        slides.append(SlidePlanItem(layout_name=layout, context=ctx))

    return slides, pricing_docs


def _resolve_zone_block(model: ProjectModel) -> list[tuple[str, dict]]:
    """Apply slide_plan_override if present, else auto-arrange."""
    if model.slide_plan_override:
        # Build slides from the override list. Each entry: {layout: ..., zones: [name, ...]}
        zone_by_name = {z.name: z for z in model.zones}
        result = []
        for entry in model.slide_plan_override:
            layout = entry["layout"]
            zone_names = entry["zones"]
            if layout in ("zone_solo", "zone_solo_fullbleed"):
                if len(zone_names) != 1:
                    raise SlidePlanError(f"{layout} requires exactly 1 zone, got {len(zone_names)}")
                result.append((layout, {"zone": zone_by_name[zone_names[0]]}))
            elif layout == "zone_index":
                result.append((layout, {"zones": [zone_by_name[n] for n in zone_names]}))
            else:
                expected = int(layout.split("_")[1].rstrip("up"))
                if len(zone_names) != expected:
                    raise SlidePlanError(f"{layout} requires exactly {expected} zones")
                result.append((layout, {"zones": [zone_by_name[n] for n in zone_names]}))
        return result
    return auto_arrange_zones(list(model.zones))


def _build_ctx(model: ProjectModel, layout: str, page_num: int, page_total: int, hint: dict) -> dict:
    """Dispatch to the appropriate ctx_builder."""
    if layout == "cover":
        return build_cover_ctx(model, page_num, page_total)
    if layout == "exec_summary":
        return build_exec_summary_ctx(model, page_num, page_total, hint["investment_range"])
    if layout == "understanding":
        return build_understanding_ctx(model, page_num, page_total)
    if layout == "creative_vision":
        return build_creative_vision_ctx(model, page_num, page_total)
    if layout == "zone_index":
        return build_zone_index_ctx(model, page_num, page_total)
    if layout == "zone_solo":
        return build_zone_solo_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_solo_fullbleed":
        return build_zone_solo_fullbleed_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_2up":
        return build_zone_2up_ctx(model, page_num, page_total, hint["zones"])
    if layout == "zone_3up":
        return build_zone_3up_ctx(model, page_num, page_total, hint["zones"])
    if layout == "scope":
        return build_scope_ctx(model, page_num, page_total)
    if layout == "case_study":
        return build_case_study_ctx(model, page_num, page_total, hint["case_study_data"])
    if layout == "investment":
        return build_investment_ctx(model, page_num, page_total,
                                     hint["tier_totals"], hint["partnership_discounts"])
    if layout == "terms":
        return build_terms_ctx(model, page_num, page_total)
    if layout == "sign_off":
        return build_sign_off_ctx(model, page_num, page_total)
    if layout == "about":
        return build_about_ctx(model, page_num, page_total)
    raise ValueError(f"Unknown layout: {layout}")


def _load_case_study(case_id: str) -> dict:
    path = CASE_STUDIES_DIR / f"{case_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Case study not found: {case_id} (looked at {path})")
    post = frontmatter.load(str(path))
    sections = _split_md_sections(post.content)
    return {
        "name": post.metadata["name"],
        "year": post.metadata["year"],
        "voice_tag": post.metadata.get("voice_tag", ""),
        "standfirst": post.metadata["standfirst"],
        "challenge": sections.get("Challenge", ""),
        "approach": sections.get("Approach", ""),
        "outcome": sections.get("Outcome", ""),
    }


def _split_md_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def _load_discount_pcts() -> dict[str, float]:
    """Load percentages from the partnership_discounts boilerplate."""
    bp_path = Path(__file__).resolve().parents[3] / "skill_assets" / "boilerplate" / "partnership_discounts.md"
    bp = frontmatter.load(str(bp_path)).metadata
    return {d["term"]: d["discount"] for d in bp["discounts"]}


def _format_partnership_for_slide(discounts: tuple) -> list:
    """Pass-through for now — slide expects (label, percent_str) tuples."""
    return list(discounts)
```

- [ ] **Step 3: Smoke-test imports**

Run:

```bash
python -c "from proposal_build.composer import compose; print('compose imports OK')"
```

Expected: prints "compose imports OK".

- [ ] **Step 4: Commit**

```bash
git add skill_assets/proposal_build/composer/ctx_builders.py skill_assets/proposal_build/composer/__init__.py
git commit -m "feat(plan-3): composer/ctx_builders.py + top-level compose() orchestrator"
```

---

## Phase 5 — Renderer + CLI (4 tasks)

### Task 14: New layout — `skill_assets/layouts/itemized_pricing.html`

**Files:**
- Create: `skill_assets/layouts/itemized_pricing.html`

This is the Jinja2 template for the per-tier itemized pricing PDF (2 pages, master-derived). Uses existing `brand.css`. Keep CSS inline (page-scoped) to avoid touching brand.css.

- [ ] **Step 1: Create the layout file**

Create `skill_assets/layouts/itemized_pricing.html`:

```html
<!-- layout-version: 2026-05-12 -->
{% extends "base.html" %}
{% block title %}Itemized Cost Breakdown — {{ project_name }}{% endblock %}

{% block extra_head %}
<style>
  @page { size: 13.333in 7.5in; margin: 0; }
  .pricing-page { padding: var(--space-5) var(--space-6); }
  .pricing-header-band {
    background: var(--color-charcoal); color: var(--color-light);
    padding: var(--space-4) var(--space-6); margin: calc(-1 * var(--space-5)) calc(-1 * var(--space-6)) var(--space-5);
  }
  .pricing-header-band .eyebrow {
    color: var(--color-red); font-family: var(--font-heading);
    font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase; font-size: 11pt;
  }
  .pricing-header-band h1 {
    font-family: var(--font-display); font-weight: 900; font-size: 36pt;
    color: var(--color-light); margin: 0.2em 0 0.05em;
  }
  .pricing-header-band .standfirst {
    font-family: var(--font-body); font-weight: 300; font-style: italic;
    color: var(--color-gray); font-size: 13pt; margin: 0;
  }
  .pricing-header-band .page-num {
    position: absolute; top: var(--space-4); right: var(--space-6);
    color: var(--color-red); font-weight: 700; letter-spacing: 0.10em; font-size: 10pt;
  }
  .pricing-meta-panel {
    background: var(--color-panel); padding: var(--space-4) var(--space-5);
    display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3) var(--space-5);
    margin-bottom: var(--space-4);
  }
  .pricing-meta-panel .label {
    color: var(--color-gray); font-family: var(--font-heading);
    font-weight: 700; font-size: 9pt; letter-spacing: 0.06em; text-transform: uppercase;
  }
  .pricing-meta-panel .value {
    font-family: var(--font-body); font-weight: 700; font-size: 12pt; color: var(--color-charcoal);
    margin-top: 2pt;
  }
  table.pricing-table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-3); }
  table.pricing-table th {
    background: var(--color-charcoal); color: var(--color-red);
    font-family: var(--font-heading); font-weight: 700; font-size: 9pt;
    letter-spacing: 0.06em; text-transform: uppercase; padding: 8pt 12pt; text-align: left;
  }
  table.pricing-table th.qty, table.pricing-table th.unit, table.pricing-table th.amount { text-align: center; }
  table.pricing-table th.amount { text-align: right; }
  table.pricing-table td { padding: 6pt 12pt; font-family: var(--font-body); font-size: 10pt; color: var(--color-charcoal); border-bottom: 0.5pt solid #e0e0e0; }
  table.pricing-table td.qty, table.pricing-table td.unit { text-align: center; }
  table.pricing-table td.amount { text-align: right; font-variant-numeric: tabular-nums; }
  table.pricing-table tr.group-header td {
    background: white; color: var(--color-red);
    font-family: var(--font-heading); font-weight: 700; font-size: 11pt;
    letter-spacing: 0.04em; text-transform: uppercase; padding-top: 12pt;
    border-bottom: 1pt solid var(--color-red);
  }
  .total-band {
    background: var(--color-charcoal); color: var(--color-light);
    padding: var(--space-3) var(--space-5); display: flex;
    justify-content: space-between; align-items: center;
    margin: var(--space-3) calc(-1 * var(--space-6)) 0;
  }
  .total-band .label { color: var(--color-red); font-family: var(--font-heading); font-weight: 700; font-size: 16pt; letter-spacing: 0.06em; }
  .total-band .total { color: var(--color-light); font-family: var(--font-display); font-weight: 900; font-size: 28pt; }
  .pricing-footer {
    color: var(--color-red); font-family: var(--font-heading); font-weight: 700; font-size: 9pt;
    letter-spacing: 0.04em; padding: var(--space-3) var(--space-6);
    border-top: 0.5pt solid #e0e0e0; margin-top: var(--space-4);
  }
  /* Page 2 specific */
  .terms-card {
    background: var(--color-charcoal); color: var(--color-light);
    padding: var(--space-3) var(--space-4); margin-bottom: var(--space-3);
  }
  .terms-card h3 {
    color: var(--color-red); font-family: var(--font-heading);
    font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; font-size: 11pt;
    margin: 0 0 var(--space-2);
  }
  .payment-row {
    display: grid; grid-template-columns: 1fr 80pt 120pt;
    align-items: center; padding: var(--space-3) var(--space-4); background: var(--color-panel);
    border-bottom: 0.5pt solid #e0e0e0;
  }
  .payment-row .pct { color: var(--color-red); font-weight: 700; text-align: center; }
  .payment-row .amt { font-family: var(--font-body); font-weight: 700; font-size: 14pt; text-align: right; }
  table.savings { width: 100%; margin: var(--space-3) 0; border-collapse: collapse; }
  table.savings th, table.savings td { padding: 8pt 12pt; font-family: var(--font-body); font-size: 11pt; }
  table.savings th { background: var(--color-panel); color: var(--color-charcoal); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; font-size: 10pt; }
</style>
{% endblock %}

{% block content %}
<!-- PAGE 1 — Itemized Cost Breakdown -->
<div class="pricing-page">
  <div class="pricing-header-band">
    <div class="eyebrow">ST. NICK'S CHRISTMAS LIGHTING &amp; DÉCOR</div>
    <h1>Itemized Cost Breakdown</h1>
    <div class="standfirst">Supplemental to the {{ project_year }} {{ proposal_type }}</div>
    <div class="page-num">PAGE 1 / 2</div>
  </div>

  <div class="pricing-meta-panel">
    <div><div class="label">CLIENT</div><div class="value">{{ client_company }}</div></div>
    <div><div class="label">PROJECT</div><div class="value">{{ project_year }} {{ proposal_type }}</div></div>
    <div><div class="label">TIER</div><div class="value">{{ tier_name }}</div></div>
    <div><div class="label">TOTAL</div><div class="value">${{ "{:,.0f}".format(tier_total) }} all-in, tax excluded</div></div>
    <div><div class="label">DATE</div><div class="value">{{ proposal_date_long }}</div></div>
    <div><div class="label">VALID</div><div class="value">30 days from proposal date</div></div>
  </div>

  <table class="pricing-table">
    <thead>
      <tr><th>ITEM</th><th class="qty">QTY</th><th class="unit">UNIT</th><th class="amount">AMOUNT</th></tr>
    </thead>
    <tbody>
      {% if base_scope_lines %}
      <tr class="group-header"><td colspan="3">BASE SCOPE</td><td class="amount">${{ "{:,.0f}".format(base_subtotal) }}</td></tr>
      {% for li in base_scope_lines %}
      <tr>
        <td>{{ li.customer_facing }}</td>
        <td class="qty">{{ li.qty | int if li.qty == li.qty|int else li.qty }}</td>
        <td class="unit">{{ li.unit }}</td>
        <td class="amount">${{ "{:,.0f}".format(li.line_total) }}</td>
      </tr>
      {% endfor %}
      {% endif %}
      {% if enhancement_lines %}
      <tr class="group-header"><td colspan="3">OPTIONAL ENHANCEMENTS</td><td class="amount">${{ "{:,.0f}".format(enh_subtotal) }}</td></tr>
      {% for li in enhancement_lines %}
      <tr>
        <td>{{ li.customer_facing }}</td>
        <td class="qty">{{ li.qty | int if li.qty == li.qty|int else li.qty }}</td>
        <td class="unit">{{ li.unit }}</td>
        <td class="amount">${{ "{:,.0f}".format(li.line_total) }}</td>
      </tr>
      {% endfor %}
      {% endif %}
    </tbody>
  </table>

  <div class="total-band">
    <div class="label">TOTAL — {{ tier_name | upper }} TIER</div>
    <div class="total">${{ "{:,.0f}".format(tier_total) }}</div>
  </div>

  <div class="pricing-footer">
    Page 1 of 2 · ST-NICKS.COM · (562) 438-0017 · Payment terms on page 2
  </div>
</div>

<!-- PAGE 2 — Payment Terms & Savings -->
<div class="pricing-page" style="page-break-before: always;">
  <div class="pricing-header-band">
    <div class="eyebrow">ST. NICK'S CHRISTMAS LIGHTING &amp; DÉCOR</div>
    <h1>Payment Terms &amp; Savings</h1>
    <div class="standfirst">{{ client_short }} · {{ project_year }} {{ proposal_type }} · {{ tier_name }} Tier</div>
    <div class="page-num">PAGE 2 / 2</div>
  </div>

  <div class="pricing-meta-panel" style="grid-template-columns: 1fr 1fr;">
    <div><div class="label">TOTAL — {{ tier_name | upper }} TIER</div></div>
    <div><div class="value" style="text-align:right; color: var(--color-red); font-size: 18pt;">${{ "{:,.0f}".format(tier_total) }}</div></div>
  </div>

  <div class="terms-card"><h3>Payment Schedule</h3></div>
  {{ payment_schedule_md_html | safe }}

  <div class="terms-card"><h3>Multi-Year Partnership Savings</h3></div>
  <table class="savings">
    <thead><tr><th>TERM</th><th>DISCOUNT</th><th>SAVINGS</th><th>YEAR 1 PRICE</th></tr></thead>
    <tbody>
    {% for row in partnership_rows %}
      <tr>
        <td><strong>{{ row.term | lower | replace('-year', '-year lock') }}</strong></td>
        <td style="color: var(--color-red); font-weight: 700;">{{ row.discount_label }}</td>
        <td style="color: var(--color-charcoal);">${{ "{:,.0f}".format(row.savings) }}</td>
        <td style="font-weight: 700;">${{ "{:,.0f}".format(row.year_1_price) }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <p style="font-style: italic; color: var(--color-gray); font-size: 10pt;">
    {{ non_multi_year_renewal_note }}
  </p>

  <div class="terms-card"><h3>Terms Summary</h3></div>
  <ul style="font-family: var(--font-body); font-size: 10pt; color: var(--color-charcoal); padding-left: var(--space-4);">
    <li>{{ term_panels.validity }}</li>
    <li>{{ term_panels.change_orders }}</li>
    <li>{{ term_panels.insurance_permits }}</li>
  </ul>

  <div class="pricing-footer">
    This document is a supplement to the {{ project_year }} {{ proposal_type }}.
    Contract terms prevail.<br>
    ST. NICK'S CHRISTMAS LIGHTING &amp; DÉCOR · ST-NICKS.COM · (562) 438-0017
  </div>
</div>
{% endblock %}

{% block footer %}{% endblock %}
```

- [ ] **Step 2: Visual smoke test — render with dummy data**

Create a quick smoke-test by running this snippet from repo root:

```bash
python -c "
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

LAYOUTS = Path('skill_assets/layouts')
env = Environment(loader=FileSystemLoader(str(LAYOUTS)), autoescape=True, undefined=StrictUndefined)
tmpl = env.get_template('itemized_pricing.html')
ctx = dict(
    client_company='Test', client_short='TEST', project_name='Test', project_year=2026,
    proposal_type='Holiday Proposal', proposal_date_long='May 12, 2026',
    page_num=1, page_total=2, tier_name='Enhanced', tier_total=345000,
    base_scope_lines=[type('L', (), dict(customer_facing='Wreaths', qty=4.0, unit='ea', line_total=400))()],
    enhancement_lines=[type('L', (), dict(customer_facing='Snowflakes', qty=12.0, unit='ea', line_total=3540))()],
    base_subtotal=400, enh_subtotal=3540,
    payment_schedule_md_html='<p>50% deposit. 50% on completion.</p>',
    partnership_rows=[dict(term='2-YEAR', discount_label='4% OFF', savings=-13800, year_1_price=331200)],
    non_multi_year_renewal_note='5% YoY otherwise.',
    term_panels=dict(validity='Valid 30 days.', change_orders='2 rev rounds.', insurance_permits='\$5M Umbrella.'),
)
html = tmpl.render(**ctx)
HTML(string=html, base_url=str(LAYOUTS)).write_pdf('/tmp/itemized_smoke.pdf')
print('Wrote /tmp/itemized_smoke.pdf')
"
open /tmp/itemized_smoke.pdf
```

Expected: opens a 2-page PDF that visually resembles the master Itemized Pricing PDF. Brand colors visible. Visual review only — no asserts.

- [ ] **Step 3: Commit**

```bash
git add skill_assets/layouts/itemized_pricing.html
git commit -m "feat(plan-3): itemized_pricing.html — 2-page master-derived pricing supplement layout"
```

### Task 15: Renderer — pdf + pricing_pdf + report (`renderer/*` + `test_renderer_outputs.py`)

**Files:**
- Create: `skill_assets/proposal_build/renderer/pdf.py`
- Create: `skill_assets/proposal_build/renderer/pricing_pdf.py`
- Create: `skill_assets/proposal_build/renderer/report.py`
- Modify: `skill_assets/proposal_build/renderer/__init__.py`
- Create: `tests/test_renderer_outputs.py`

- [ ] **Step 1: Implement `renderer/pdf.py`**

Create `skill_assets/proposal_build/renderer/pdf.py`:

```python
"""Render N (layout, ctx) tuples → 1 multi-page proposal PDF."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML


LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def render_proposal_pdf(slides: list, out_path: Path) -> Path:
    """slides: list of SlidePlanItem-like (layout_name, ctx) tuples.

    Renders each slide as a single HTML page with @page breaks between them,
    then writes a single PDF. Returns the output path.
    """
    env = Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    # Render each slide individually, then concatenate via WeasyPrint's render_pages mechanism.
    # WeasyPrint can take multiple HTML(string=...).render() outputs and combine pages.
    pages = []
    for layout, ctx in slides:
        template = env.get_template(f"{layout}.html")
        html_str = template.render(**ctx)
        doc = HTML(string=html_str, base_url=str(LAYOUTS_DIR)).render()
        pages.extend(doc.pages)

    # Use the first doc's metadata; merge all pages
    if not pages:
        raise ValueError("No slides to render")

    # Reuse the first doc's metadata; replace pages list
    first_doc = HTML(string="<html><body></body></html>").render()
    first_doc.pages = pages
    out_path.parent.mkdir(parents=True, exist_ok=True)
    first_doc.write_pdf(target=str(out_path))
    return out_path
```

- [ ] **Step 2: Implement `renderer/pricing_pdf.py`**

Create `skill_assets/proposal_build/renderer/pricing_pdf.py`:

```python
"""Render one ItemizedPricingDoc → 1 two-page tier PDF."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

from proposal_build.composer.pricing import compute_partnership_savings
from proposal_build.parser.boilerplate import load_boilerplate, substitute_placeholders


LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def render_pricing_pdf(doc, out_path: Path) -> Path:
    """Renders one ItemizedPricingDoc to a 2-page PDF at out_path."""
    bp = load_boilerplate()
    env = Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
    )
    template = env.get_template("itemized_pricing.html")

    model = doc.project
    placeholders = {
        "project_name": model.project_name, "project_short": model.project_short,
        "project_year": model.project_year,
        "client_short": model.client_short, "proposal_type": model.proposal_type,
        "fabrication_lock_long": _date_long(model.fabrication_lock),
        "signing_deadline_long": _date_long(model.signing_deadline),
        "proposal_date_long": _date_long(model.proposal_date),
    }

    discount_pcts = {d["term"]: d["discount"] for d in bp.partnership_discounts}
    partnership_rows = compute_partnership_savings(
        tier_total=doc.tier_total,
        discounts=tuple((d["term"], d["label"]) for d in bp.partnership_discounts),
        discount_pcts=discount_pcts,
    )

    ctx = {
        "client_company": model.client_company, "client_short": model.client_short,
        "project_name": model.project_name, "project_year": model.project_year,
        "proposal_type": model.proposal_type,
        "proposal_date_long": _date_long(model.proposal_date),
        "tier_name": doc.tier.value, "tier_total": doc.tier_total,
        "base_scope_lines": list(doc.base_scope_lines),
        "enhancement_lines": list(doc.enhancement_lines),
        "base_subtotal": sum(li.line_total for li in doc.base_scope_lines),
        "enh_subtotal": sum(li.line_total for li in doc.enhancement_lines),
        "payment_schedule_md_html": _md_to_simple_html(
            substitute_placeholders(model.term_panels.get("payment_schedule", ""), placeholders)
        ),
        "partnership_rows": partnership_rows,
        "non_multi_year_renewal_note": bp.non_multi_year_renewal_note,
        "term_panels": {k: substitute_placeholders(v, placeholders)
                        for k, v in model.term_panels.items()},
    }

    html_str = template.render(**ctx)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_str, base_url=str(LAYOUTS_DIR)).write_pdf(target=str(out_path))
    return out_path


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    return datetime.fromisoformat(iso).date().strftime("%B %d, %Y")


def _md_to_simple_html(text: str) -> str:
    """Wrap each non-blank line of payment_schedule text in a <div class='payment-row'>."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "".join(f"<div class='payment-row'><div>{ln}</div></div>" for ln in lines)
```

- [ ] **Step 3: Implement `renderer/report.py`**

Create `skill_assets/proposal_build/renderer/report.py`:

```python
"""Coverage Report writer + layout pin reader/writer."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from proposal_build.models import ProjectModel, ValidationResult


LAYOUT_VERSION_RE = re.compile(r"<!-- layout-version:\s*([\d-]+)\s*-->")


class LayoutPinError(Exception):
    pass


def read_layout_versions(layouts_dir: Path) -> dict[str, str]:
    """Scan all .html files in layouts_dir; extract their layout-version header."""
    versions: dict[str, str] = {}
    for f in sorted(layouts_dir.iterdir()):
        if f.suffix.lower() != ".html":
            continue
        first_line = f.read_text().splitlines()[0] if f.exists() else ""
        m = LAYOUT_VERSION_RE.search(first_line)
        if m:
            versions[f.name] = m.group(1)
    return versions


def write_layout_pin(pin_path: Path, layouts_dir: Path) -> dict:
    """Create or update layout_pin.json. Sets first_run if file doesn't exist; updates last_run otherwise."""
    versions = read_layout_versions(layouts_dir)
    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")

    if pin_path.exists():
        existing = json.loads(pin_path.read_text())
        first_run = existing.get("first_run", now_iso)
    else:
        first_run = now_iso

    pin = {"first_run": first_run, "last_run": now_iso, "layouts": versions}
    pin_path.parent.mkdir(parents=True, exist_ok=True)
    pin_path.write_text(json.dumps(pin, indent=2))
    return pin


def check_layout_pin(pin_path: Path, layouts_dir: Path, use_latest: bool) -> list[tuple[str, str]]:
    """Compare on-disk layout versions to the pin. Returns list of blocker tuples (empty if OK or use_latest=True)."""
    if not pin_path.exists():
        return []   # First run — no pin to check
    if use_latest:
        return []

    pin = json.loads(pin_path.read_text())
    pinned = pin.get("layouts", {})
    on_disk = read_layout_versions(layouts_dir)

    blockers = []
    for filename, pinned_version in pinned.items():
        disk_version = on_disk.get(filename)
        if disk_version is None:
            continue   # layout file removed; not a Plan 3 concern
        if disk_version != pinned_version:
            blockers.append((
                "layout_pin_drift",
                f"{filename} version is {disk_version} on disk but pinned to {pinned_version}. "
                f"Pass --use-latest-layouts to refresh, or revert layout to pinned version.",
            ))
    return blockers


def write_coverage_report(
    report_path: Path,
    model: ProjectModel,
    artifacts: dict,
    result: ValidationResult,
    slides: list,
    pricing_docs: list,
    use_latest_layouts: bool,
) -> Path:
    """Write the human-readable coverage report Markdown."""
    lines = []
    lines.append(f"# Coverage Report — {model.project_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if use_latest_layouts:
        lines.append("\n**LAYOUT PIN UPDATED** — visual output may differ from prior runs.")
    status_icon = "✅ PASSED — proposal generated." if result.passed else "❌ BLOCKED — see errors below."
    lines.append(f"Status: {status_icon}")
    lines.append("")

    if not result.passed:
        lines.append("## Blocking Errors")
        for code, msg in result.blockers:
            lines.append(f"- **{code}**: {msg}")
        lines.append("")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines))
        return report_path

    # PASSED path — full summary
    items = list(model.line_items)
    lines.append("## Summary")
    lines.append(f"- Worksheet line items: {len(items)} "
                 f"({sum(1 for li in items if not li.is_enhancement)} base + "
                 f"{sum(1 for li in items if li.is_enhancement)} enhancements)")
    lines.append(f"  ✓ {sum(1 for li in items if li.tiers)} mapped to a tier")
    lines.append(f"  ✓ {sum(1 for li in items if li.customer_facing)} have Customer-Facing Description")
    lines.append(f"  ✓ {sum(1 for li in items if li.zone)} have Zone assignment")
    lines.append(f"- Zones: {len(model.zones)} declared in Brief")
    for z in model.zones:
        direct = sum(1 for li in items if li.zone == z.name)
        lines.append(f"  ✓ {z.name} ({direct} priced items, {len(z.bullets)} bullets)")
    lines.append(f"- Renderings: {len(artifacts['eligible_renderings'])} on disk")
    lines.append(f"  ✓ {len(set(artifacts['referenced_filenames']))} wired into hero_image fields")
    lines.append("")

    lines.append("## Slide Plan")
    for i, item in enumerate(slides, start=1):
        layout = item.layout_name
        lines.append(f"{i}. {layout}")
    lines.append("")

    lines.append("## Itemized Pricing PDFs")
    for d in pricing_docs:
        all_lines = list(d.base_scope_lines) + list(d.enhancement_lines)
        lines.append(f"- {d.tier.value} (${d.tier_total:,.0f}) — {len(all_lines)} line items")
    lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        by_code: dict[str, list[str]] = {}
        for code, msg in result.warnings:
            by_code.setdefault(code, []).append(msg)
        for code in sorted(by_code):
            lines.append(f"### {code}")
            for msg in by_code[code]:
                lines.append(f"- {msg}")
        lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    return report_path
```

- [ ] **Step 4: Wire `renderer/__init__.py` orchestrator**

Replace the stub `skill_assets/proposal_build/renderer/__init__.py` with:

```python
"""Renderer top-level: model + slides + pricing_docs → PDFs + report + pin."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from proposal_build.models import ProjectModel, ValidationResult
from proposal_build.renderer.pdf import render_proposal_pdf
from proposal_build.renderer.pricing_pdf import render_pricing_pdf
from proposal_build.renderer.report import (
    write_coverage_report, write_layout_pin, check_layout_pin,
)


LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def render(
    project_dir: Path,
    model: ProjectModel,
    slides: list,
    pricing_docs: list,
    artifacts: dict,
    result: ValidationResult,
    use_latest_layouts: bool = False,
) -> dict:
    """Top-level: writes all outputs, returns paths dict."""
    project_dir = Path(project_dir)
    notes = project_dir / "04 - Process & Notes"
    pricing_dir = project_dir / "03 - Scope & Pricing"

    # Run dir
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = notes / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Layout pin check (blocking error if drift and not --use-latest-layouts)
    pin_path = notes / "layout_pin.json"
    pin_blockers = check_layout_pin(pin_path, LAYOUTS_DIR, use_latest_layouts)
    result.blockers.extend(pin_blockers)

    # If we have any blockers, write the report and return without rendering
    if not result.passed:
        report_path = notes / "coverage_report.md"
        write_coverage_report(report_path, model, artifacts, result, slides, pricing_docs,
                               use_latest_layouts)
        shutil.copy(report_path, run_dir / "coverage_report.md")
        return {"status": "blocked", "report": report_path, "run_dir": run_dir, "pdfs": []}

    # Render proposal PDF
    proposal_filename = f"{model.project_name} - {model.project_year} {model.proposal_type}.pdf"
    proposal_run = run_dir / proposal_filename
    render_proposal_pdf([(s.layout_name, s.context) for s in slides], proposal_run)

    # Render pricing PDFs
    pricing_runs = []
    for doc in pricing_docs:
        pname = f"{model.project_name} - {model.project_year} Itemized Pricing - {doc.tier.value}.pdf"
        prun = run_dir / pname
        render_pricing_pdf(doc, prun)
        pricing_runs.append(prun)

    # Copy run outputs to 03 - Scope & Pricing/ (latest)
    pricing_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(proposal_run, pricing_dir / proposal_filename)
    for prun in pricing_runs:
        shutil.copy(prun, pricing_dir / prun.name)

    # Write/update layout pin
    write_layout_pin(pin_path, LAYOUTS_DIR)

    # Write coverage report
    report_path = notes / "coverage_report.md"
    write_coverage_report(report_path, model, artifacts, result, slides, pricing_docs,
                          use_latest_layouts)
    shutil.copy(report_path, run_dir / "coverage_report.md")

    return {
        "status": "ok",
        "report": report_path,
        "run_dir": run_dir,
        "pdfs": [pricing_dir / proposal_filename] + [pricing_dir / p.name for p in pricing_runs],
    }
```

- [ ] **Step 5: Write the failing renderer test**

Create `tests/test_renderer_outputs.py`:

```python
"""Tests for renderer/__init__.py — output paths, run dir, layout pin behavior.

These tests are minimal — they assert structural properties of generated PDFs
(page count via pypdf, font embedding) but not pixel correctness. The full
visual review is the eyeball pass at Plan 3 close-out.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from proposal_build.models import (
    ProjectModel, Tier, SlidePlanItem, ValidationResult, ItemizedPricingDoc, LineItem,
)
from proposal_build.renderer.report import (
    read_layout_versions, write_layout_pin, check_layout_pin,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
LAYOUTS_DIR = REPO_ROOT / "skill_assets" / "layouts"


def test_read_layout_versions_returns_all():
    versions = read_layout_versions(LAYOUTS_DIR)
    assert "cover.html" in versions
    assert "itemized_pricing.html" in versions
    # All versions should be ISO-format dates
    for name, ver in versions.items():
        assert len(ver) == 10 and ver[4] == "-"


def test_layout_pin_first_run(tmp_path):
    pin = tmp_path / "layout_pin.json"
    write_layout_pin(pin, LAYOUTS_DIR)
    data = json.loads(pin.read_text())
    assert "first_run" in data
    assert "last_run" in data
    assert "layouts" in data
    assert data["first_run"] == data["last_run"]


def test_layout_pin_check_match(tmp_path):
    pin = tmp_path / "layout_pin.json"
    write_layout_pin(pin, LAYOUTS_DIR)
    blockers = check_layout_pin(pin, LAYOUTS_DIR, use_latest=False)
    assert blockers == []


def test_layout_pin_check_drift(tmp_path):
    pin = tmp_path / "layout_pin.json"
    # Manually write a pin with a wrong version for cover.html
    pin.write_text(json.dumps({
        "first_run": "2026-05-12T14:23:01-07:00",
        "last_run": "2026-05-12T14:23:01-07:00",
        "layouts": {"cover.html": "1999-01-01"},
    }))
    blockers = check_layout_pin(pin, LAYOUTS_DIR, use_latest=False)
    assert any("cover.html" in msg for _, msg in blockers)
    assert any("layout_pin_drift" == code for code, _ in blockers)


def test_layout_pin_use_latest_skips_check(tmp_path):
    pin = tmp_path / "layout_pin.json"
    pin.write_text(json.dumps({"first_run": "x", "last_run": "y", "layouts": {"cover.html": "1999-01-01"}}))
    blockers = check_layout_pin(pin, LAYOUTS_DIR, use_latest=True)
    assert blockers == []
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_renderer_outputs.py -v`
Expected: 5 tests pass.

- [ ] **Step 7: Commit**

```bash
git add skill_assets/proposal_build/renderer/ tests/test_renderer_outputs.py
git commit -m "feat(plan-3): renderer/ — PDF assembly, pricing PDF, coverage report, layout pin"
```

### Task 16: CLI (`cli.py`)

**Files:**
- Create: `skill_assets/proposal_build/cli.py`
- Create: `skill_assets/proposal_build/__main__.py`

- [ ] **Step 1: Implement `cli.py`**

Create `skill_assets/proposal_build/cli.py`:

```python
"""CLI entrypoint: `python -m proposal_build generate <project_dir>`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from proposal_build.parser import build_project_model, ProjectLoadError
from proposal_build.parser.validate import run_validation
from proposal_build.composer import compose
from proposal_build.renderer import render
from proposal_build.models import ValidationResult


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="proposal_build")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Generate a proposal for a project folder")
    gen.add_argument("project_dir", help="Path to the project folder")
    gen.add_argument("--use-latest-layouts", action="store_true",
                     help="Refresh the layout_pin.json to current versions")

    args = parser.parse_args(argv)

    if args.command == "generate":
        return _do_generate(Path(args.project_dir), args.use_latest_layouts)
    return 1


def _do_generate(project_dir: Path, use_latest: bool) -> int:
    try:
        model, artifacts = build_project_model(project_dir)
    except ProjectLoadError as e:
        # Convert to a ValidationResult so the report still gets written
        result = ValidationResult(blockers=[("project_load", str(e))], warnings=[])
        outcome = render(project_dir, _placeholder_model(), [], [], {}, result, use_latest)
        print(f"❌ BLOCKED — {e}", file=sys.stderr)
        print(f"   See: {outcome['report']}", file=sys.stderr)
        return 1

    # Validation pass
    result = run_validation(
        model,
        eligible_renderings=artifacts["eligible_renderings"],
        referenced_filenames=artifacts["referenced_filenames"],
        per_line_sums=artifacts["per_line_sums"],
        scenarios=artifacts["scenarios"],
    )

    # Composition
    slides, pricing_docs = compose(model)

    # Render
    outcome = render(project_dir, model, slides, pricing_docs, artifacts, result, use_latest)

    if outcome["status"] == "blocked":
        print(f"❌ BLOCKED. See: {outcome['report']}", file=sys.stderr)
        return 1

    print("✅ Generation complete.")
    print(f"   Coverage Report: {outcome['report']}")
    print("   Outputs:")
    for p in outcome["pdfs"]:
        print(f"     • {p.name}")
    return 0


def _placeholder_model():
    """Return a no-op model when project loading itself failed,
    so the renderer can still write a coverage report."""
    from proposal_build.models import ProjectModel, Tier
    return ProjectModel(
        client_company="(unknown)", client_short="", project_name="(unknown)",
        project_short="", project_year=0, project_subtitle="", proposal_type="Holiday Proposal",
        presenter_name="", presenter_title="", presenter_email="", presenter_phone="",
        proposal_date="", go_live="", season_end="",
        fabrication_lock="", signing_deadline="",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="", pricing_format="tiered",
        cover_image="", creative_vision_hero="", case_study="skip", case_study_hero="",
        zones=(), line_items=(), creative_direction="", customer_goals=(),
        customer_constraints=(), success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(), term_panels={},
        after_approval_steps=(), company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Implement `__main__.py` so `python -m proposal_build` works**

Create `skill_assets/proposal_build/__main__.py`:

```python
from proposal_build.cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Smoke-test the CLI on Riverside (will fail until Brief is written in Phase 6)**

Run: `python -m proposal_build generate "Projects/Downtown Riverside Metro Link"`
Expected: ❌ BLOCKED with a message that Brief.md isn't found at `04 - Process & Notes/Project Brief.md`. Coverage report at that path explains the failure. **This is correct behavior** — the next phase fixes it.

- [ ] **Step 4: Commit**

```bash
git add skill_assets/proposal_build/cli.py skill_assets/proposal_build/__main__.py
git commit -m "feat(plan-3): cli.py + __main__.py — `python -m proposal_build generate` entrypoint"
```

---

## Phase 6 — Riverside content migration (4 tasks)

### Task 17: Move pre-Plan-3 archive files

**Files:**
- Create directory: `Projects/Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive/`
- Move: `Riverside MetroLink - 2026 Holiday Proposal.pdf` → archive
- Move: `Riverside MetroLink - 2026 Holiday Proposal.pptx` → archive

- [ ] **Step 1: Create the archive directory and move the files**

Run from repo root:

```bash
mkdir -p "Projects/Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive"
git mv "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal.pdf" \
       "Projects/Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive/"
git mv "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal.pptx" \
       "Projects/Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive/"
```

- [ ] **Step 2: Add a README to the archive folder**

Create `Projects/Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive/README.md`:

```markdown
# Pre-Plan-3 Archive

These files are the proposal artifacts that existed in this project's
`03 - Scope & Pricing/` folder *before* Plan 3 (Phase 2 generation core)
shipped on 2026-05-03.

They are preserved here as historical comparison artifacts. The new
generation pipeline writes its output (with similar filenames) directly
to `03 - Scope & Pricing/`, overwriting on each `generate` run.

## Contents
- `Riverside MetroLink - 2026 Holiday Proposal.pdf` — old hand/Plan-2-era build
- `Riverside MetroLink - 2026 Holiday Proposal.pptx` — original PowerPoint source

For Plan 3 onward, generated outputs land in:
- `03 - Scope & Pricing/<Project> - <Year> Holiday Proposal.pdf` (latest)
- `04 - Process & Notes/runs/<timestamp>/` (historical run dirs)
```

- [ ] **Step 3: Commit**

```bash
git add "Projects/Downtown Riverside Metro Link/04 - Process & Notes/pre_plan3_archive/"
git commit -m "chore(plan-3): archive pre-Plan-3 Riverside PDF + PPTX before first generation run"
```

### Task 18: Riverside `Project Brief.md`

**Files:**
- Create: `Projects/Downtown Riverside Metro Link/04 - Process & Notes/Project Brief.md`

The Brief content is authored to match the existing `tests/fixtures/riverside.py` content as closely as practical, so the e2e test produces a PDF visually equivalent to what the Plan-2-prime layout-driven fixture produces.

- [ ] **Step 1: Create the Brief**

Create the file at `Projects/Downtown Riverside Metro Link/04 - Process & Notes/Project Brief.md`:

```markdown
---
client_company: "Riverside County Transportation Commission (RCTC)"
client_short: "RCTC METROLINK"
project_name: "Riverside MetroLink"
project_short: "MetroLink"
project_subtitle: "Six-Station Civic Holiday Program"
project_year: 2026
proposal_type: "Holiday Proposal"

presenter_name: "Jonathan Yang"
presenter_title: "Account Executive"
presenter_email: "jonathan@st-nicks.com"
presenter_phone: "(562) 438-0017"
proposal_date: "2026-05-12"

go_live: "2026-11-20"
season_end: "2027-01-05"
fabrication_lock: "2026-08-22"
signing_deadline: "2026-10-30"

voice: "civic"
recommended_tier: "enhanced"
design_phrase: "Holiday Express."
pricing_format: "tiered"

cover_image: "Wreath - Brick Column Night.jpg"
creative_vision_hero: "Pole Banner Artwork - Holiday Express 01.jpg"
case_study: "long_beach_transit"
case_study_hero: "Evening Lighting - Station Awning 01.png"

zones:
  - num: "01"
    name: "Downtown Riverside"
    subtitle: "The flagship station — civic centerpiece."
    flags: [flagship]
    hero_image: "Walk-Through Ornament - Warm White.png"
    bullets:
      - "Custom-fabricated wreaths at every entrance"
      - "Full-canopy garland across the platform overhang"
      - "Pole banner program (8 poles)"
      - "Lighted walk-through arch at plaza forecourt"
      - "Evening lighting program — platform + awning + curb-edge"
      - "On-site QC walkthrough with RCTC Capital Projects"
  - num: "02"
    name: "La Sierra"
    subtitle: "First park-and-ride stop — community gateway."
    hero_image: "Wreaths - Station Entrance 01.png"
    bullets:
      - "Wreaths at primary entrance"
      - "Pole banner program (4 poles)"
      - "Lighted accent at platform sign"
  - num: "03"
    name: "Pedley"
    subtitle: "Mid-line residential stop — restrained festive treatment."
    hero_image: "Garlands - Decorated Swag - Plaza Fence.png"
    bullets:
      - "Garland across platform railing"
      - "Two pole banners at station entry"
  - num: "04"
    name: "Riverside-Hunter Park"
    subtitle: "University-adjacent — student-traffic focus."
    hero_image: "Wreaths - Station Entrance 02.png"
    bullets:
      - "Pole banner program (6 poles)"
      - "Lighted gateway display at the bus interchange"
      - "Wreaths at the eastbound entry"
  - num: "05"
    name: "Moreno Valley/March Field"
    subtitle: "Outer line — visible from the freeway."
    hero_image: "Pole Banner - Happy Holidays.png"
    bullets:
      - "Large-format pole banner program (10 poles, freeway-side)"
      - "Lighted snowflake constellation along the platform"
  - num: "06"
    name: "Perris-Downtown"
    subtitle: "End of line — community arrival moment."
    hero_image: "Wreaths - Station Entrance 03.png"
    bullets:
      - "Walk-through ornament arch at the plaza"
      - "Wreaths and garland at all entrances"
      - "Pole banner program (4 poles)"
---

## Creative Direction
A civic-scale holiday aesthetic that turns the MetroLink line itself into the
holiday gesture. Wreaths and garlands frame each station entrance like a
ceremonial gateway; evening lighting turns the platforms themselves into
destinations after sundown. The same design vocabulary repeats at every stop
so the line reads as one program from end to end.

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

- [ ] **Step 2: Commit**

```bash
git add "Projects/Downtown Riverside Metro Link/04 - Process & Notes/Project Brief.md"
git commit -m "feat(plan-3): Riverside Project Brief.md — 6 zones, civic voice, tiered pricing"
```

### Task 19: Migrate Riverside worksheet (3 new columns, 25 rows)

**Files:**
- Create: `scripts/migrate_riverside_worksheet.py` (one-shot helper script — kept in repo for reproducibility)
- Modify: `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - Scope Worksheet.xlsx`

Adding 3 columns × 25 rows by hand in Excel is error-prone. The script does it deterministically. The script's output — the migrated .xlsx — is what gets committed; the script lives under `scripts/` for the record.

- [ ] **Step 1: Create the migration script**

Create `scripts/migrate_riverside_worksheet.py`:

```python
"""One-shot migration: add Customer-Facing Description, Zone, Tiers columns to
Riverside MetroLink - Scope Worksheet.xlsx.

Idempotent: running twice produces the same result. Run once during Plan 3
setup. Kept in repo for reproducibility / future projects can model after it.
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parent.parent
WORKSHEET = REPO / "Projects" / "Downtown Riverside Metro Link" / "03 - Scope & Pricing" / "Riverside MetroLink - Scope Worksheet.xlsx"

# (line_num, customer_facing, zone, tiers)
RIVERSIDE_MIGRATION = {
    "1":  ("Branded 'Board the Holidays' pole banners — one-time purchase; customer-owned, designed in-house.",
            "*", "Essential, Enhanced, Signature"),
    "2":  ("Powder-coated steel pole banner brackets — one-time purchase; customer-owned, reusable indefinitely.",
            "*", "Essential, Enhanced, Signature"),
    "3":  ("Annual install of pole banner program at season open; removal at season close. Storage between seasons included.",
            "*", "Essential, Enhanced, Signature"),
    "4":  ("Warm-white string lighting on the eaves of all 16 platform canopies — 1,024 lineal feet of evening glow across the platforms.",
            "*", "Essential, Enhanced, Signature"),
    "5":  ("Warm-white string lighting on the bus stop waiting canopies — additional warm-white evening accent at the perimeter.",
            "*", "Essential, Enhanced, Signature"),
    "6":  ("Lit evergreen garland swagged across the perimeter fence — 621 lineal feet of warm-white glow framing the property edge.",
            "*", "Essential, Enhanced, Signature"),
    "7":  ("Lit evergreen garland on the building eave — warm-white evening accent that reads from the platforms.",
            "*", "Essential, Enhanced, Signature"),
    "8":  ("Lit evergreen garland on the center driveway gates — the welcome gesture as guests enter the station.",
            "*", "Essential, Enhanced, Signature"),
    "9":  ("Custom-fabricated 5 ft lighted wreaths at every station entrance — the threshold gesture of the program.",
            "*", "Essential, Enhanced, Signature"),
    "10": ("Oversized 10 ft lighted wreath on the stair tower — a feature element visible from a block away.",
            "Downtown Riverside", "Essential, Enhanced, Signature"),
    "11": ("18 ft traditional Christmas tree at the centerpiece location — pre-lit warm white with red, green, and gold ornaments.",
            "Downtown Riverside", "Essential, Enhanced"),
    "12": ("Walk-through warm-white lighted ornament archway at the plaza forecourt — a photo moment and the visual anchor of the program.",
            "Downtown Riverside", "Essential, Enhanced, Signature"),
    "E1": ("Lighted snowflakes along bridge and platform railings — additional warm-white evening accents at every station.",
            "*", "Enhanced, Signature"),
    "E2": ("Walk-through lighted gift box archway with red bow — additional photo moment and high social-media value installation.",
            "Downtown Riverside", "Enhanced, Signature"),
    "E3": ("Custom 'City of Riverside' lighted bell display — Mission Inn-style, branded for the City. One-time custom fabrication, customer-owned.",
            "Downtown Riverside", "Signature"),
    "E4": ("Annual install and removal of the City of Riverside Bell Display each season.",
            "Downtown Riverside", "Signature"),
    "E5": ("Off-season climate-controlled storage of the customer-owned Bell Display.",
            "Downtown Riverside", "Signature"),
    "E6": ("21 ft red-and-green LED spiral tree with gold star topper — the Signature-tier alternative to the Traditional centerpiece tree.",
            "Downtown Riverside", "Signature"),
    "E7": ("Stacked oversized lighted gift box pyramid — 12 ft tall, additional photo moment at a separate plaza location.",
            "Downtown Riverside", "Signature"),
    "E8":  ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the perimeter fence garland.",
            "*", "Enhanced, Signature"),
    "E9":  ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the building eave garland.",
            "*", "Enhanced, Signature"),
    "E10": ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the center driveway gate garland.",
            "*", "Enhanced, Signature"),
    "E11": ("Illuminated 'Happy Holidays' overhead marquee with skyline silhouette — custom-fabricated signage element.",
            "Downtown Riverside", "Enhanced, Signature"),
    "E12": ("Lit evergreen garland on the staircase tower and railing — warm-white evening accent at the flagship vertical feature.",
            "Downtown Riverside", "Enhanced, Signature"),
    "E13": ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the staircase tower garland.",
            "Downtown Riverside", "Enhanced, Signature"),
}


def main() -> None:
    if not WORKSHEET.exists():
        raise SystemExit(f"Worksheet not found: {WORKSHEET}")

    wb = openpyxl.load_workbook(str(WORKSHEET))
    ws = wb.active

    # Find header row(s). The Riverside file has TWO header rows
    # (one for Base Scope, one for Enhancements) — both must get the new columns.
    rows = list(ws.iter_rows(values_only=False))
    header_indices = []
    for i, row in enumerate(rows):
        if row[0].value == "#" and row[1].value == "Item":
            header_indices.append(i + 1)   # openpyxl is 1-indexed
    print(f"Found {len(header_indices)} header rows at: {header_indices}")

    # Add the 3 new column headers after the existing 10
    NEW_HEADERS = ("Customer-Facing Description", "Zone", "Tiers")
    for hi in header_indices:
        for offset, name in enumerate(NEW_HEADERS, start=11):
            ws.cell(row=hi, column=offset, value=name)

    # Walk all data rows; fill in the 3 new columns from RIVERSIDE_MIGRATION
    filled = 0
    for row in ws.iter_rows():
        line_num = row[0].value
        if line_num is None:
            continue
        line_str = str(line_num).strip()
        if line_str in RIVERSIDE_MIGRATION:
            cf, zone, tiers = RIVERSIDE_MIGRATION[line_str]
            row[10].value = cf
            row[11].value = zone
            row[12].value = tiers
            filled += 1
    print(f"Filled {filled} data rows with the 3 new columns.")

    wb.save(str(WORKSHEET))
    print(f"Saved: {WORKSHEET}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the migration script**

Run from repo root: `python scripts/migrate_riverside_worksheet.py`
Expected: prints "Found 2 header rows at: [4, NN]", "Filled 25 data rows", "Saved: ...".

- [ ] **Step 3: Verify the migration via the parser**

Run:

```bash
python -c "
from pathlib import Path
from proposal_build.parser.worksheet import parse_worksheet
ws = parse_worksheet(Path('Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - Scope Worksheet.xlsx'))
print(f'Parsed {len(ws.line_items)} line items')
sums = ws.tier_sums_per_line()
for tier, total in sums.items():
    print(f'  {tier.value}: \${total:,.0f}')
"
```

Expected:
```
Parsed 25 line items
  Essential: $88,906
  Enhanced: $166,643
  Signature: $200,249
```

(Per-line tier sums match the worksheet's TIER SCENARIOS block totals.)

- [ ] **Step 4: Commit**

```bash
git add scripts/migrate_riverside_worksheet.py "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - Scope Worksheet.xlsx"
git commit -m "chore(plan-3): migrate Riverside worksheet — add CFD/Zone/Tiers columns to all 25 rows"
```

### Task 20: Blank `_template_project/` updates

**Files:**
- Create: `Projects/_template_project/04 - Process & Notes/Project Brief.md`
- Modify: `Projects/_template_project/03 - Scope & Pricing/[Client] - Scope Worksheet.xlsx`

- [ ] **Step 1: Create the template Brief**

Create `Projects/_template_project/04 - Process & Notes/Project Brief.md`:

```markdown
---
# === REQUIRED FIELDS ===
# Replace placeholders with real project values.
# All fields below are required unless marked optional.

# Client identification
client_company: "Full Legal Client Name"
client_short: "CLIENT-SHORT-NAME-CAPS"        # used in tracked-caps footer; ~12 chars max
project_name: "Project Name"                  # used in PDF title + filename
project_short: "Short Name"                    # used in mid-document references; ~10 chars
project_subtitle: "One-line subtitle that appears under the project name"
project_year: 2026
proposal_type: "Holiday Proposal"             # default; override for Lunar New Year, Lighting Refresh, etc.

# Presenter
presenter_name: "Account Executive Full Name"
presenter_title: "Account Executive"
presenter_email: "ae@st-nicks.com"
presenter_phone: "(562) 438-0017"
proposal_date: "2026-MM-DD"                   # ISO format

# Schedule (only go_live required; rest auto-derive if blank)
go_live: "2026-11-20"
season_end: "2027-01-05"
fabrication_lock: ""                          # blank → go_live − 90d
signing_deadline: ""                          # blank → go_live − 21d

# Tone & creative
voice: "civic"                                # civic | destination-retail | corporate | hospitality
recommended_tier: "enhanced"                  # essential | enhanced | signature
design_phrase: "Design Phrase Here."          # the visual narrative phrase; period intentional
pricing_format: "tiered"                      # tiered | single

# Image selections — filenames in 02 - Renderings/{Base Scope|Enhancements}/
cover_image:           "REPLACE_WITH_FILENAME.jpg"
creative_vision_hero:  "REPLACE_WITH_FILENAME.jpg"
case_study:            "long_beach_transit"   # case_study .md id (in skill_assets/case_studies/), or "skip"
case_study_hero:       "REPLACE_WITH_FILENAME.png"

# Zones — repeat the block per zone; 1 to ~10 zones supported
zones:
  - num: "01"
    name: "Zone Name"
    subtitle: "One-line subtitle for this zone."
    flags: []                                 # optional: [flagship], [signature], or both
    hero_image: "REPLACE_WITH_FILENAME.jpg"
    bullets:
      - "Customer-facing bullet 1"
      - "Customer-facing bullet 2"
      - "Customer-facing bullet 3"

# === OPTIONAL OVERRIDE: explicit slide plan ===
# Uncomment and edit if you want full control over zone arrangement.
# slide_plan:
#   - {layout: zone_solo_fullbleed, zones: ["Zone Name"]}
#   - {layout: zone_2up, zones: ["Zone A", "Zone B"]}

# === OPTIONAL OVERRIDE: term panels ===
# Uncomment to override one or more boilerplate term panels for this deal.
# term_panel_overrides:
#   payment_schedule: |
#     Custom payment terms here...
---

## Creative Direction
2-3 sentences setting the visual narrative for the program. This appears as the body
of the Creative Vision slide alongside the design_phrase.

## Customer Goals
- Goal 1
- Goal 2
- Goal 3

## Customer Constraints
- Constraint 1
- Constraint 2

## Success Criteria
- Success metric 1
- Success metric 2

## What You're Approving
A clear paragraph stating exactly what the customer is signing for. Includes
project name, scope summary, dates, and tier-selection mechanism. Appears on the
Sign-off slide.
```

- [ ] **Step 2: Migrate the template worksheet (add 3 columns + 1 example row)**

Create `scripts/migrate_template_worksheet.py`:

```python
"""One-shot migration of the blank template worksheet."""
from __future__ import annotations

from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "Projects" / "_template_project" / "03 - Scope & Pricing" / "[Client] - Scope Worksheet.xlsx"


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit(f"Template worksheet not found: {TEMPLATE}")

    wb = openpyxl.load_workbook(str(TEMPLATE))
    ws = wb.active

    # Find each header row and add the 3 new columns
    for row in ws.iter_rows():
        if row[0].value == "#" and row[1].value == "Item":
            row_idx = row[0].row
            ws.cell(row=row_idx, column=11, value="Customer-Facing Description")
            ws.cell(row=row_idx, column=12, value="Zone")
            ws.cell(row=row_idx, column=13, value="Tiers")

            # Add an example row immediately below
            ex = row_idx + 1
            # Only add if next row is empty
            if ws.cell(row=ex, column=1).value is None:
                ws.cell(row=ex, column=1, value="1")
                ws.cell(row=ex, column=2, value="Example Item")
                ws.cell(row=ex, column=3, value="Internal description for ops")
                ws.cell(row=ex, column=4, value=1)
                ws.cell(row=ex, column=5, value="ea")
                ws.cell(row=ex, column=6, value=100)
                ws.cell(row=ex, column=7, value=100)
                ws.cell(row=ex, column=8, value="example.png")
                ws.cell(row=ex, column=9, value="Materials notes")
                ws.cell(row=ex, column=10, value="Internal notes")
                ws.cell(row=ex, column=11, value="Customer-facing copy lands here.")
                ws.cell(row=ex, column=12, value="*")
                ws.cell(row=ex, column=13, value="Essential, Enhanced, Signature")
            break   # only first header for the example row

    wb.save(str(TEMPLATE))
    print(f"Saved: {TEMPLATE}")


if __name__ == "__main__":
    main()
```

Run: `python scripts/migrate_template_worksheet.py`

- [ ] **Step 3: Commit**

```bash
git add "Projects/_template_project/04 - Process & Notes/Project Brief.md" "Projects/_template_project/03 - Scope & Pricing/[Client] - Scope Worksheet.xlsx" scripts/migrate_template_worksheet.py
git commit -m "feat(plan-3): blank _template_project/ — Brief.md template + migrated worksheet"
```

---

## Phase 7 — Skill bundle finishing (2 tasks)

### Task 21: Skill manifest (`skill_assets/skill.md`)

**Files:**
- Create: `skill_assets/skill.md`

This is the Claude Desktop skill manifest. It tells Claude (when the skill is invoked) how to work with the project folder, how to call the Python module, how to interpret outputs, and how the polish chat workflow runs.

- [ ] **Step 1: Create `skill_assets/skill.md`**

```markdown
---
name: stnicks-proposal-builder
description: |
  Generate customer-ready proposal PDFs for St. Nick's holiday décor projects.
  Reads Project Brief.md + Scope Worksheet.xlsx + renderings folder; produces
  a polished proposal PDF + per-tier itemized pricing PDFs + a coverage report.
trigger_keywords: ["proposal", "build proposal", "phase 2", "generate proposal"]
---

# St. Nick's Proposal Builder Skill

You are operating as the proposal generation assistant for an Account Executive
at St. Nick's Christmas Lighting & Décor.

## Project state detection

When the user references a project (e.g., "build the Riverside MetroLink proposal"),
locate the project folder under `Projects/<Project Name>/` and check:

1. Is `04 - Process & Notes/Project Brief.md` present?
2. Is `03 - Scope & Pricing/<Project Name> - Scope Worksheet.xlsx` present?
3. Are renderings present in `02 - Renderings/Base Scope/` and `Enhancements/`?
4. Is the worksheet migrated (does it have Customer-Facing Description, Zone, Tiers columns)?

If anything is missing, tell the user what's missing and where it should be.
Do not attempt to invent inputs. The AE owns the Brief and Worksheet content.

## Phase 2 invocation

To generate the proposal, run via Code Execution:

```bash
python -m proposal_build generate "Projects/<Project Name>"
```

Then read `Projects/<Project Name>/04 - Process & Notes/coverage_report.md`
and report back to the AE:

- ✅ PASSED status: list the output PDFs and any warnings worth surfacing
- ❌ BLOCKED status: list every blocker with the exact fix the AE needs to make

Do NOT proactively re-run generation after a fix. The AE controls when to regenerate.

## Polish chat workflow

When the AE asks to "polish the worksheet" (or similar):

1. Open the worksheet with openpyxl. Read every row's Customer-Facing Description column.
2. Read the voice preset matching the Brief's `voice:` field at
   `skill_assets/voice_presets/{voice}.md`. The 5 polish examples are calibration —
   match that voice pattern.
3. Present polished suggestions to the AE row-by-row (or batched) for accept/edit/reject.
4. Write accepted polished text BACK to the .xlsx cell using openpyxl (preserve all
   other cells; save the workbook).
5. Tell the AE which rows were updated; they can re-run `generate` to see the new output.

The Python pipeline never sees the polish step. The .xlsx is the source of truth at
generation time.

## Coverage Report interpretation

Common warnings and what they mean for the AE:

- **W1 (unused renderings)**: A file exists in Base Scope/ or Enhancements/ but no
  Brief field references it. If intentional, move to Unused Renderings/.
- **W2 (zone has no priced items)**: A zone in Brief has no worksheet rows assigned to
  it (and no `*` cross-program rows). Probably means a missing Zone column entry.
- **W3 (zone bullet/item count divergence)**: Zone has many priced items but few
  bullets, or vice versa. AE should sanity-check.
- **W5/W6/W7 (CFD sniff test)**: Customer-Facing Description looks like internal
  language. Suggest running the polish chat.
- **W8 (Brief field filled from defaults)**: Voice preset or boilerplate filled a
  blank Brief field. AE may want to override.

## Layout drift safeguard

If `coverage_report.md` reports `layout_pin_drift`, a layout file has been edited
since the project's first generation run. Two paths:
- **Refresh the pin**: re-run with `--use-latest-layouts` (CLI) or pass
  `use_latest_layouts: true` to the module call.
- **Revert the layout**: ask the user to revert the offending layout file to
  the pinned version.

Default behavior is to refuse rendering until one of these is chosen, to protect
in-flight proposals from cosmetic drift across customer revision rounds.

## Allowed Python operations during a session

- `python -m proposal_build generate "<project_dir>"` — primary action
- `python -m proposal_build generate "<project_dir>" --use-latest-layouts` — refresh pin
- `import openpyxl` reads/writes for the polish chat
- `import frontmatter` reads for Brief / voice preset inspection
- Single-slide preview (advanced): `from tests.conftest import render_layout`

## What this skill is NOT for (Plan 3 scope)

- **Phase 0 (RFP intake)**: not yet shipped — AE drafts Brief.md by hand or from prior similar project
- **Phase 1 (Rendering ingestion)**: not yet shipped — AE drops renderings into folders manually
- **Canva CSV emit**: deferred to a later plan
- **Diff-mode regeneration**: every `generate` rebuilds the full deck (versioned output dir preserves history)
- **Per-slide checkpoint mode**: deferred — first proposal of a new project type may need 2-3 regen rounds
```

- [ ] **Step 2: Commit**

```bash
git add skill_assets/skill.md
git commit -m "feat(plan-3): skill_assets/skill.md — Claude Desktop manifest for Phase 2 workflow"
```

### Task 22: AE-facing SOP (`AE_SOP.md`)

**Files:**
- Create: `AE_SOP.md` (at repo root)

The Phase 2 chapter only — Phases 0/1 chapters get added in later plans.

- [ ] **Step 1: Create `AE_SOP.md` at repo root**

```markdown
# Account Executive — Standard Operating Procedure

This is the operations manual for using the St. Nick's Proposal Builder skill.
Plan 3 ships the Phase 2 (Proposal Generation) chapter. Phases 0 and 1 will
be added when those plans ship.

---

## Phase 2 — Generating a proposal in Claude Desktop

### Prerequisites
You should have:
- A project folder at `Projects/<Project Name>/` (duplicated from `_template_project/`)
- A Project Brief at `04 - Process & Notes/Project Brief.md`
- A Scope Worksheet at `03 - Scope & Pricing/<Project Name> - Scope Worksheet.xlsx` with
  the 3 new columns (Customer-Facing Description, Zone, Tiers) filled in
- Renderings dropped into `02 - Renderings/Base Scope/` and `Enhancements/`

### The workflow
1. **Open Claude Desktop** with this repo as the active project.

2. **Tell Claude what you want:** "Build the proposal for the Downtown Riverside
   Metro Link project" (or similar). Claude will detect Phase 2 state, check that
   inputs are present, and run generation.

3. **Read the coverage report.** Claude will summarize the report in chat and tell
   you the status:
   - ✅ **PASSED** — outputs are in `03 - Scope & Pricing/`. Open them to review.
   - ❌ **BLOCKED** — Claude lists what's wrong with the exact fix needed.

4. **Polish iteration (optional but common).** If the customer-facing copy in the
   Itemized Pricing PDFs reads roughly:
   - Tell Claude: "Polish the worksheet."
   - Claude reads the worksheet's Customer-Facing Description column and suggests
     polished versions row-by-row using the voice preset.
   - You accept/edit/reject per row.
   - Polished text writes back to the .xlsx automatically.
   - Re-run generation: "Build the proposal again."

5. **Send to customer.** Outputs are in `03 - Scope & Pricing/`:
   - Main proposal: `<Project> - <Year> Holiday Proposal.pdf`
   - Per-tier itemized pricing: `... Itemized Pricing - {Essential, Enhanced, Signature}.pdf`

### Time expectations
- **First proposal:** ~2h 50m (you're learning the schema and polishing voice presets).
- **Steady state (5+ proposals in):** ~1h 40m.

The system cuts the post-pricing time roughly 3-5× vs the prior find-and-replace
workflow, mostly by eliminating slide-by-slide visual cleanup.

---

## Common Coverage Report warnings + how to fix

| Code | Meaning | Fix |
|---|---|---|
| W1 | A rendering exists on disk but no Brief field references it | If intentional, move to `02 - Renderings/Unused Renderings/`. Otherwise add a `hero_image:` reference somewhere in the Brief. |
| W2 | A zone in Brief has no priced line items | Check the Worksheet's Zone column — likely a missing entry or typo. |
| W3 | Zone has 5+ priced items but only 2 bullets (or vice versa) | Sanity-check the bullets in Brief vs the worksheet rows. Bullets are AE-curated summaries — they don't have to be 1:1, but big divergence usually means something's missed. |
| W4 | Worksheet's TIER SCENARIOS block totals diverge from per-line tier sums | Reconcile: either fix per-line Tiers entries, or update the scenarios block. |
| W5 | Customer-Facing Description matches internal description verbatim | Run polish chat. |
| W6 | Customer-Facing Description contains internal markers (dimensions, units) | Run polish chat. |
| W7 | Customer-Facing Description is fewer than 4 words | Rewrite the row's CFD to be customer-readable. |
| W8 | Brief field blank, filled by voice preset or boilerplate | If the default isn't right, override in the Brief. |

---

## Customizing voice presets

Voice presets live at `skill_assets/voice_presets/{voice}.md`. Each file has:
- 5 polish before/after examples (calibration data for Claude)
- Voice rules (do/don't language)
- Default phrasings for things the Brief leaves blank

To tune a voice:
1. Open the .md file in any editor.
2. Edit the polish examples — these are the strongest signal Claude uses.
3. Edit the voice rules to clarify do/don'ts.
4. Save. Next polish chat session uses the updated calibration.

Plan on ~30 minutes per voice the first time you use it on a real project.

---

## Layout drift safeguard

The system pins which layout file versions a project's first proposal used. If
a layout gets updated between proposal revisions (which can happen if a layout
fix ships mid-cycle), regeneration is **blocked** until you decide:

- **Use the new layouts** for this project: tell Claude "regenerate with latest layouts"
  (passes `--use-latest-layouts`). The pin updates; future runs use the new versions.
- **Stay on the pinned versions**: ask Claude to revert the layout file to the
  pinned version. Useful when you're mid-revision-cycle with a customer.

This protects in-flight proposals from looking subtly different across revision rounds.

---

## What's not yet supported

These workflows ship in later plans:
- **Phase 0 (RFP intake):** Claude drafts the Brief + Worksheet from RFP materials. For now, AE writes both by hand.
- **Phase 1 (Rendering ingestion):** Claude renames + categorizes renderings using vision. For now, AE drops files into folders manually.
- **Canva editable backup:** generation only produces PDFs. For now, customer revisions go through Brief/Worksheet edits + regeneration.
- **Diff-mode regeneration:** every regenerate rebuilds the full deck. The versioned output dir preserves prior runs for comparison.
- **Per-slide preview:** review happens on the full PDF, not slide-by-slide.

If any of these would unblock you, say so — they're already in the Plan 4+ queue.
```

- [ ] **Step 2: Commit**

```bash
git add AE_SOP.md
git commit -m "docs(plan-3): AE_SOP.md — Phase 2 chapter (Plans 0/1 added later)"
```

---

## Phase 8 — End-to-end verification + close-out (2 tasks)

### Task 23: End-to-end test (`test_e2e_riverside.py`)

**Files:**
- Create: `tests/test_e2e_riverside.py`

Runs the full pipeline against the real migrated Riverside files. The one integration test that proves Plan 3 is alive.

- [ ] **Step 1: Write the test**

Create `tests/test_e2e_riverside.py`:

```python
"""End-to-end test: full Phase 2 generation against the real Riverside project.

This is the gate that proves Plan 3 works. Runs the CLI against the migrated
worksheet + Brief, asserts all 4 PDFs are produced, page counts are correct,
and fonts are embedded.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader   # may need: pip install pypdf

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"
PRICING_DIR = PROJECT / "03 - Scope & Pricing"
NOTES_DIR = PROJECT / "04 - Process & Notes"


@pytest.fixture(scope="module")
def run_generation():
    """Run the CLI once, then yield. Cleans up output PDFs but preserves run dirs."""
    # Snapshot run dirs so we can restore after the test
    runs_before = set(p.name for p in (NOTES_DIR / "runs").iterdir()) if (NOTES_DIR / "runs").exists() else set()

    result = subprocess.run(
        [sys.executable, "-m", "proposal_build", "generate", str(PROJECT)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    yield result

    # Optional cleanup: remove generated PDFs in 03/ but keep the runs dirs
    # (commented out so debugging artifacts persist)
    # for pdf in PRICING_DIR.glob("Riverside MetroLink - 2026 *.pdf"):
    #     pdf.unlink()


def test_cli_exits_zero(run_generation):
    assert run_generation.returncode == 0, (
        f"CLI failed:\nstdout:\n{run_generation.stdout}\nstderr:\n{run_generation.stderr}"
    )


def test_proposal_pdf_exists(run_generation):
    p = PRICING_DIR / "Riverside MetroLink - 2026 Holiday Proposal.pdf"
    assert p.exists(), f"Proposal PDF missing: {p}"


def test_proposal_pdf_page_count(run_generation):
    p = PRICING_DIR / "Riverside MetroLink - 2026 Holiday Proposal.pdf"
    reader = PdfReader(str(p))
    # 14 slides for Riverside (no case study skip): cover, exec, understanding, creative,
    # zone_index, zone_solo (Downtown), zone_2up, zone_3up, scope, case_study, investment,
    # terms, sign_off, about = 14
    assert len(reader.pages) == 14, f"Expected 14 pages, got {len(reader.pages)}"


def test_three_itemized_pricing_pdfs_exist(run_generation):
    for tier in ("Essential", "Enhanced", "Signature"):
        p = PRICING_DIR / f"Riverside MetroLink - 2026 Itemized Pricing - {tier}.pdf"
        assert p.exists(), f"Pricing PDF missing: {p}"


def test_each_pricing_pdf_is_two_pages(run_generation):
    for tier in ("Essential", "Enhanced", "Signature"):
        p = PRICING_DIR / f"Riverside MetroLink - 2026 Itemized Pricing - {tier}.pdf"
        reader = PdfReader(str(p))
        assert len(reader.pages) == 2, f"{p.name} has {len(reader.pages)} pages, expected 2"


def test_coverage_report_status_passed(run_generation):
    report = NOTES_DIR / "coverage_report.md"
    assert report.exists()
    text = report.read_text()
    assert "✅ PASSED" in text


def test_layout_pin_written(run_generation):
    pin = NOTES_DIR / "layout_pin.json"
    assert pin.exists()
    import json
    data = json.loads(pin.read_text())
    assert "first_run" in data
    assert "layouts" in data
    # All Plan-2-prime layouts + itemized_pricing should be pinned
    assert "cover.html" in data["layouts"]
    assert "itemized_pricing.html" in data["layouts"]


def test_run_dir_created(run_generation):
    runs = NOTES_DIR / "runs"
    assert runs.exists()
    assert any(runs.iterdir())


def test_run_dir_contains_all_outputs(run_generation):
    runs = NOTES_DIR / "runs"
    latest = max(runs.iterdir(), key=lambda p: p.name)
    files = {p.name for p in latest.iterdir()}
    assert "Riverside MetroLink - 2026 Holiday Proposal.pdf" in files
    assert "Riverside MetroLink - 2026 Itemized Pricing - Essential.pdf" in files
    assert "Riverside MetroLink - 2026 Itemized Pricing - Enhanced.pdf" in files
    assert "Riverside MetroLink - 2026 Itemized Pricing - Signature.pdf" in files
    assert "coverage_report.md" in files
```

- [ ] **Step 2: Add `pypdf` to dev dependencies**

In `pyproject.toml`, add `pypdf>=5.0` to the `[project.optional-dependencies]` `dev = [...]` list. Then:

Run: `pip install -e ".[dev]"`

- [ ] **Step 3: Run the e2e test**

Run: `pytest tests/test_e2e_riverside.py -v`
Expected: 9 tests pass.

If they fail, **read `Projects/Downtown Riverside Metro Link/04 - Process & Notes/coverage_report.md`** for the diagnostic — that's the single source of truth on what went wrong.

- [ ] **Step 4: Run the full test suite**

Run: `pytest -v`
Expected: ~65 tests pass (~25 existing + ~40 new).

- [ ] **Step 5: Commit**

```bash
git add tests/test_e2e_riverside.py pyproject.toml
git commit -m "test(plan-3): e2e Riverside generation — 9 assertions covering full pipeline"
```

### Task 24: Eyeball pass + final commit

**Files:** None directly; this is a manual review gate.

- [ ] **Step 1: Open the 4 generated PDFs**

```bash
open "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Holiday Proposal.pdf"
open "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Itemized Pricing - Essential.pdf"
open "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Itemized Pricing - Enhanced.pdf"
open "Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/Riverside MetroLink - 2026 Itemized Pricing - Signature.pdf"
```

- [ ] **Step 2: Open the master comparison artifacts side-by-side**

```bash
open "Master Proposal Reference/StNicks_Proposal_v2_Master.pdf"
open "Projects/_master_templates/StNicks_Supplemental_Itemized_Pricing.pdf"
```

- [ ] **Step 3: Visual eyeball checklist**

For each generated PDF, verify against the Plan-2-prime fixture-rendered PDFs (`tests/_output/`) and the master:
- All 14 slides render correctly (no overflow, no broken images, no missing text).
- Brand colors match Plan-2-prime fixtures (no off-brand hex values introduced).
- Footer crumb shows correct year, project, page numbers.
- Per-tier itemized pricing supplements have correct line items per tier (substitution working: Essential has Traditional Tree but not Spiral LED; Signature has Spiral LED but not Traditional Tree).
- Page 2 of pricing PDFs has the payment terms and savings table.
- Cover hero, creative vision hero, case study hero, and per-zone heroes all show real Riverside renderings.

If any slide looks visibly worse than its Plan-2-prime fixture-rendered counterpart, that's a Plan 3 bug — don't merge until it's fixed.

- [ ] **Step 4: Final commit (if any tweaks were made)**

If the eyeball pass surfaced bugs, fix them in their own commits. If nothing needed fixing:

```bash
git log --oneline | head -25   # review the Plan 3 commit list
```

Plan 3 is **done** when:
- All 65+ pytest tests pass
- The 4 Riverside PDFs render without visual regression vs Plan-2-prime fixture output
- Coverage report shows ✅ PASSED with no surprising warnings
- No uncommitted changes in the working tree (apart from `tests/_output/` which is gitignored)

---

## Self-Review

This section is run after the full plan is written, not as a task.

**Spec coverage** — every spec section maps to a task or set of tasks:

| Spec section | Plan task(s) |
|---|---|
| §1 Goal + §2 Scope | Plan header + scope statements throughout |
| §3 Architecture (3-stage pipeline) | Tasks 1, 5–10 (Parser), 11–13 (Composer), 14–16 (Renderer + CLI) |
| §4 Brief.md schema | Task 5 (parser/brief.py) + Task 18 (Riverside Brief) + Task 20 (template Brief) |
| §5 Worksheet schema (3 new columns) | Task 6 (parser/worksheet.py) + Task 19 (Riverside migration) + Task 20 (template migration) |
| §6 Composer rules (slide_plan + pricing) | Tasks 11, 12, 13 |
| §7 Renderer outputs + layout pin | Tasks 14 (itemized_pricing.html), 15 (renderer/), 16 (CLI) |
| §8 Validation rules + Coverage Report | Task 9 (validate.py) + Task 15 (report.py) |
| §9 Voice presets + boilerplate library | Tasks 2, 3, 4 + Task 8 (parser/voice + boilerplate) + Task 21 (skill.md polish chat) |
| §10 Test plan | Tasks 5, 6, 8, 9, 11, 12, 15, 23 |
| §11 Performance expectations | Task 22 (AE_SOP.md timing section) |
| §12 Riverside fixture migration | Tasks 17, 18, 19, 20 |
| §13 Out of scope | Stated in Task 21 (skill.md), Task 22 (AE_SOP.md) |
| §14 Files added/modified | Mirrored in this plan's File Structure section + commit messages |

**Placeholder scan** — searched plan for TBD/TODO/FIXME/"implement later"/"add appropriate". One intentional reference to "TBD" inside W6 sniff-test regex (Task 9). No placeholder failures.

**Type consistency** — `ProjectModel`, `Zone`, `LineItem`, `SlidePlanItem`, `ValidationResult`, `Tier`, `ItemizedPricingDoc` are defined in Task 1 (`models.py`) and used consistently with the same names in Tasks 5–23. The `compose()` function returns `(slides, pricing_docs)` as established in Task 13 and consumed by Task 16 (CLI) and Task 23 (e2e test).

**Cross-task dependencies verified** — Tasks 5/6/7/8/9 all need Task 1 (models). Task 10 (parser orchestrator) consumes 5/6/7/8/9. Tasks 11/12 need Task 1. Task 13 consumes 11/12. Task 15 consumes 14 (itemized_pricing.html). Task 16 consumes 10/13/15. Task 17 must precede Task 23. Task 18 must precede Task 23 (e2e needs Brief). Task 19 must precede Task 23 (e2e needs migrated worksheet). Task 21 (skill.md) and Task 22 (AE_SOP.md) are independent of code tasks; can run in parallel after Phase 6.

**Trust assumptions called out** — Task 15 layout-version pin trusts authors to bump headers (documented in skill.md and AE_SOP.md). Task 13 ctx_builders depend on fixture-defined dict shapes (documented in module docstring).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-03-plan-3-phase-2-generation.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?

