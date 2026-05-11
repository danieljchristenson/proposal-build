# Plan 9 — Creative-Menu Mode + ROM Pricing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a second proposal mode ("menu") to the existing parser → composer → renderer pipeline so FIGat7th-style decks can be generated from a properly structured Brief + Worksheet, the same way Riverside/Sheraton are today, without hand-authored fixtures.

**Architecture:** New `mode: menu` flag in Brief frontmatter routes parsing and composition through a parallel path: `parser/worksheet_rom.py` parses a ROM-pricing worksheet (rental + purchase one-time + service, low/high ranges, alternate groups, section labels). `composer/menu_compose.py` emits slides using the four layouts already authored in Plan 9-prep (`image_fullbleed`, `section_divider`, `zone_2up_gallery`, `rom_investment`). Tiered mode (existing) is untouched and continues to work for Riverside/Sheraton; the dispatcher in `composer/__init__.py` picks the right compose entry based on `mode`.

**Tech Stack:** Python 3.11+, dataclasses, openpyxl, frontmatter, Jinja2, WeasyPrint. No new external deps. Extends existing Plan 3 codebase.

**Reference material:**
- Pattern learnings: `Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/Session Notes — Pattern Learnings.md` — durable lessons + open layout debt
- Locked FIGat7th fixture: `tests/fixtures/figat7th.py` — the working hand-authored reference (Plan 9 must produce equivalent output from data files alone)
- Locked FIGat7th data: Brief at `Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/Project Brief.md`, worksheet at `Projects/Fig at 7th - 2026 - Multi-Rendering Project/03 - Scope & Pricing/FIGat7th DTLA - Scope Worksheet.xlsx`

**Out of scope (deferred to later plans):**
- Customer-facing scope workbook xlsx (Riverside-style multi-tier deliverable adapted for ROM)
- "Replace-and-supersede" rendering inbox CLI tool
- Multi-page investment auto-fragmentation (current fixture splits manually; Plan 9 keeps that)
- N-up auto-arrangement (Plan 9 hard-codes 2-up for galleries; 4-up layout retained but unused by default)
- Per-item-overhead pricing category (e.g., canopy's $5K lift equipment under purchase mode) — current workaround inlines it in the service total; future schema enhancement

**Branch:** create `plan-9-creative-menu` off `main`; merge when complete.

---

## Setup

- [ ] **Setup Step 1: Create the feature branch**

```bash
git checkout main && git pull && git checkout -b plan-9-creative-menu
```

- [ ] **Setup Step 2: Verify clean baseline**

```bash
source .venv/bin/activate && pytest -q 2>&1 | tail -3
```

Expected: all tests pass (count depends on current main; record the number for comparison after later tasks).

---

## Task 1: ROM Data Models

**Files:**
- Modify: `skill_assets/proposal_build/models.py` — add `ProposalMode`, `ROMLineItem`, `Section`, `MenuProjectModel`
- Test: `tests/test_models_rom.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_models_rom.py`:

```python
"""Tests for the ROM (Rough Order of Magnitude) pricing data model
used by the creative-menu proposal mode."""
from __future__ import annotations

import pytest

from proposal_build.models import (
    ProposalMode, ROMLineItem, Section, MenuProjectModel,
)


def test_proposal_mode_values():
    assert ProposalMode.TIERED.value == "tiered"
    assert ProposalMode.MENU.value == "menu"


def test_rom_line_item_basic():
    item = ROMLineItem(
        code="20",
        section="Overhead",
        name="Mixed Ornament Canopy",
        description="16 oversized 6-foot overhead ornaments forming a layered canopy.",
        alternate_group="",
        rental_low=22400,
        rental_high=22400,
        purchase_ot_low=19200,
        purchase_ot_high=19200,
        purchase_svc_low=18600,
        purchase_svc_high=18600,
        customer_facing="An ornament canopy that turns the FIGat7th courtyard ceiling into a winter night sky.",
        materials="Steel/metal frames; warm-white and cool-white LED lights; tinsel; rope light.",
        notes="",
        rendering_ref="20_overhead-mixed-canopy.png",
    )
    assert item.is_alternate is False
    assert item.is_point_estimate is True


def test_rom_line_item_range_and_alternate():
    item = ROMLineItem(
        code="43", section="Standalones", name="Gift Box Trio",
        description="", alternate_group="",
        rental_low=4000, rental_high=6000,
        purchase_ot_low=6000, purchase_ot_high=8000,
        purchase_svc_low=4000, purchase_svc_high=7000,
        customer_facing="", materials="", notes="",
        rendering_ref="43_gift-box-trio.png",
    )
    assert item.is_point_estimate is False
    arch = ROMLineItem(
        code="30", section="Arches", name="Letter Arch",
        description="", alternate_group="arch_alternates",
        rental_low=9500, rental_high=9500,
        purchase_ot_low=9000, purchase_ot_high=9000,
        purchase_svc_low=2000, purchase_svc_high=2000,
        customer_facing="", materials="", notes="",
        rendering_ref="30_arch-letters-happy-holidays.png",
    )
    assert arch.is_alternate is True


def test_section_holds_ordered_items():
    item_a = ROMLineItem(
        code="30", section="Arches", name="Letter Arch", description="",
        alternate_group="arch_alternates",
        rental_low=9500, rental_high=9500,
        purchase_ot_low=9000, purchase_ot_high=9000,
        purchase_svc_low=2000, purchase_svc_high=2000,
        customer_facing="", materials="", notes="", rendering_ref="",
    )
    item_b = ROMLineItem(
        code="31", section="Arches", name="Bauble Arch", description="",
        alternate_group="arch_alternates",
        rental_low=9000, rental_high=9000,
        purchase_ot_low=8900, purchase_ot_high=8900,
        purchase_svc_low=2000, purchase_svc_high=2000,
        customer_facing="", materials="", notes="", rendering_ref="",
    )
    section = Section(
        key="3a",
        label="Section 3a — Plaza Arches (customer picks one)",
        name="Plaza Arches",
        is_lead=True,
        items=(item_a, item_b),
    )
    assert section.has_alternates is True
    assert len(section.items) == 2


def test_menu_project_model_smoke():
    model = MenuProjectModel(
        client_company="FIGat7th",
        client_short="FIGat7th DTLA",
        project_name="FIGat7th DTLA — 2026 Holiday Program",
        project_short="FIGat7th DTLA",
        project_year=2026,
        project_subtitle="First-Pass Creative Menu",
        presenter_name="Daniel Christenson",
        presenter_title="Director of Sales",
        presenter_org="St. Nick's Christmas Lighting & Décor",
        proposal_date="May 9, 2026",
        client_contact_name="Alexandra Castro",
        client_contact_title="Property Manager, Athena Property Management",
        client_contact_email="acastro@athenapm.com",
        client_contact_phone="",
        design_phrase="Modern Magic",
        voice="destination-retail",
        creative_direction="FIGat7th becomes Downtown LA's most photographed holiday destination.",
        customer_goals=("Drive foot traffic.", "Generate Instagram moments.", "Athena's first-year statement."),
        creative_phases=(
            {"label": "ARRIVE", "body": "An ornament canopy turns the courtyard into a winter night sky."},
            {"label": "GATHER", "body": "The centerpiece tree anchors the plaza."},
            {"label": "EXPLORE", "body": "A menu of arches, frames, and selfie moments."},
        ),
        prebuilt_cover_image="01_cover-slide-cityscape.png",
        prebuilt_palette_image="02_palette-board-mood.png",
        creative_vision_hero="10_tree-A-studio-blackbg.png",
        sections=(),
        what_youre_approving="Approve this first-pass creative menu and ROM pricing as the basis for site walk.",
    )
    assert model.client_company == "FIGat7th"
    assert model.design_phrase == "Modern Magic"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models_rom.py -v`
Expected: ImportError — `ProposalMode`, `ROMLineItem`, `Section`, `MenuProjectModel` not in `proposal_build.models`.

- [ ] **Step 3: Add the new dataclasses to `models.py`**

Append to `skill_assets/proposal_build/models.py`:

```python
class ProposalMode(str, Enum):
    """Selects which compose path the pipeline runs.

    TIERED: existing Essential/Enhanced/Signature path (Riverside, Sheraton, Pier 39).
    MENU:   creative-menu / ROM pricing path (FIGat7th).
    """
    TIERED = "tiered"
    MENU = "menu"


@dataclass(frozen=True)
class ROMLineItem:
    """Line item for ROM (Rough Order of Magnitude) pricing.

    Each item carries six numbers: rental low/high (all-inclusive annual fee),
    purchase one-time low/high, and purchase annual service low/high (install +
    removal + storage bundled).

    Point estimates (no range) are stored as low==high.

    Alternate groups: items sharing an `alternate_group` value are mutually
    exclusive options (customer picks one). Totals across the group are
    bookended by min(low) and max(high) of group members.
    """
    code: str            # e.g. "20", "10-enh", "30"
    section: str         # human-readable section key, e.g. "Arches"
    name: str
    description: str
    alternate_group: str
    rental_low: int
    rental_high: int
    purchase_ot_low: int
    purchase_ot_high: int
    purchase_svc_low: int
    purchase_svc_high: int
    customer_facing: str
    materials: str
    notes: str
    rendering_ref: str

    @property
    def is_alternate(self) -> bool:
        return bool(self.alternate_group)

    @property
    def is_point_estimate(self) -> bool:
        return (self.rental_low == self.rental_high
                and self.purchase_ot_low == self.purchase_ot_high
                and self.purchase_svc_low == self.purchase_svc_high)


@dataclass(frozen=True)
class Section:
    """A grouping of ROMLineItems on the proposal.

    key:      stable identifier ("1", "2", "3a", "3b" — used to order sections)
    label:    full table-row label ("Section 3a — Plaza Arches (customer picks one)")
    name:     short title for the section header strip on the lead slide
    is_lead:  if True, this section's first slide carries a section header block
    items:    tuple of ROMLineItems in display order
    """
    key: str
    label: str
    name: str
    is_lead: bool
    items: Tuple[ROMLineItem, ...]

    @property
    def has_alternates(self) -> bool:
        return any(it.is_alternate for it in self.items)


@dataclass(frozen=True)
class MenuProjectModel:
    """Fully-resolved project state for the creative-menu proposal mode.

    Parallel to ProjectModel, but with sections + ROMLineItems instead of
    zones + LineItems with tiers. The composer picks the right model based
    on Brief frontmatter `mode`.
    """
    client_company: str
    client_short: str
    project_name: str
    project_short: str
    project_year: int
    project_subtitle: str

    presenter_name: str
    presenter_title: str
    presenter_org: str
    proposal_date: str

    client_contact_name: str
    client_contact_title: str
    client_contact_email: str
    client_contact_phone: str

    design_phrase: str
    voice: str

    creative_direction: str
    customer_goals: Tuple[str, ...]
    creative_phases: Tuple[dict, ...]   # [{"label": "ARRIVE", "body": "..."}]

    prebuilt_cover_image: str           # filename in Base Scope/
    prebuilt_palette_image: str         # filename in Base Scope/ (or "" if no palette slide)
    creative_vision_hero: str           # filename for the creative-vision page hero

    sections: Tuple[Section, ...]
    what_youre_approving: str
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models_rom.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/models.py tests/test_models_rom.py
git commit -m "feat(plan-9): add ROM pricing data models (ProposalMode, ROMLineItem, Section, MenuProjectModel)"
```

---

## Task 2: ROM Worksheet Parser

**Files:**
- Create: `skill_assets/proposal_build/parser/worksheet_rom.py`
- Test: `tests/test_parser_worksheet_rom.py`

The FIGat7th worksheet has 15 columns: `#`, `Section`, `Item Name`, `Description / Build Notes`, `Alternate Group`, `Rental Low`, `Rental High`, `Purchase OT Low`, `Purchase OT High`, `Purchase Svc Low`, `Purchase Svc High`, `Customer-Facing Description`, `Materials / Build`, `Notes / Assumptions`, `Rendering Reference`. Header row sits at row 9 (or wherever — discover dynamically), data rows follow until first all-empty row, with `Section — …` divider rows interspersed (which start with a section label in column A).

- [ ] **Step 1: Write the failing test**

Create `tests/test_parser_worksheet_rom.py`:

```python
"""Tests for the ROM (Rough Order of Magnitude) worksheet parser
used by the creative-menu proposal mode."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser.worksheet_rom import (
    parse_rom_worksheet, ROMWorksheetParseError, ROMWorksheetData,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH_WORKSHEET = (
    REPO_ROOT
    / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
    / "03 - Scope & Pricing" / "FIGat7th DTLA - Scope Worksheet.xlsx"
)


def test_parse_figat7th_worksheet_yields_eleven_items():
    """The locked FIGat7th worksheet has 11 priced items."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    assert isinstance(data, ROMWorksheetData)
    assert len(data.line_items) == 11


def test_parse_figat7th_canopy_pricing():
    """Item 20 (canopy) prices should round-trip exactly from the worksheet."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    canopy = next(it for it in data.line_items if it.code == "20")
    assert canopy.name == "Mixed Ornament Canopy"
    assert canopy.rental_low == 22400 and canopy.rental_high == 22400
    assert canopy.purchase_ot_low == 19200 and canopy.purchase_ot_high == 19200
    assert canopy.purchase_svc_low == 18600 and canopy.purchase_svc_high == 18600


def test_parse_figat7th_arch_alternates_have_group():
    """Items 30, 31, 32, 33 share alternate_group='arch_alternates'."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    by_code = {it.code: it for it in data.line_items}
    for code in ("30", "31", "32", "33"):
        assert by_code[code].alternate_group, (
            f"Item {code} should carry an alternate_group flag in the worksheet"
        )
        assert by_code[code].alternate_group == by_code["30"].alternate_group


def test_parse_figat7th_gift_box_trio_is_range():
    """Item 43 (Gift Box Trio) is the only true range in the locked sheet."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    trio = next(it for it in data.line_items if it.code == "43")
    assert trio.rental_low == 4000 and trio.rental_high == 6000
    assert trio.is_point_estimate is False


def test_parse_missing_file_raises():
    with pytest.raises(ROMWorksheetParseError):
        parse_rom_worksheet(Path("/nonexistent/path.xlsx"))


def test_parse_worksheet_section_grouping():
    """line_items are emitted with the section column populated, matching
    the section divider rows in the worksheet."""
    data = parse_rom_worksheet(FIGAT7TH_WORKSHEET)
    sections_seen = {it.section for it in data.line_items}
    # Canonical four buckets from the locked sheet:
    assert sections_seen == {"Overhead", "Tree", "Arches", "Standalones"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser_worksheet_rom.py -v`
Expected: ImportError — `proposal_build.parser.worksheet_rom` doesn't exist.

- [ ] **Step 3: Create the parser**

Create `skill_assets/proposal_build/parser/worksheet_rom.py`:

```python
"""Parse the ROM (Rough Order of Magnitude) Scope Worksheet for menu-mode proposals.

The ROM worksheet's column shape differs from the tiered worksheet
(see parser/worksheet.py):

  # | Section | Item Name | Description / Build Notes | Alternate Group
    | Rental Low | Rental High | Purchase OT Low | Purchase OT High
    | Purchase Svc Low | Purchase Svc High | Customer-Facing Description
    | Materials / Build | Notes / Assumptions | Rendering Reference

The sheet also contains section divider rows (single label cell in column A,
the rest empty) interspersed between item groups. Those are skipped here;
the `section` field on each ROMLineItem captures the grouping.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import openpyxl

from proposal_build.models import ROMLineItem


REQUIRED_HEADERS = (
    "#", "Section", "Item Name", "Alternate Group",
    "Rental Low", "Rental High",
    "Purchase OT Low", "Purchase OT High",
    "Purchase Svc Low", "Purchase Svc High",
    "Customer-Facing Description", "Rendering Reference",
)


class ROMWorksheetParseError(Exception):
    """Raised on a blocking ROM-worksheet problem."""


@dataclass(frozen=True)
class ROMWorksheetData:
    line_items: Tuple[ROMLineItem, ...]


def parse_rom_worksheet(path: Path) -> ROMWorksheetData:
    if not path.exists():
        raise ROMWorksheetParseError(f"Worksheet not found at {path}")

    wb = openpyxl.load_workbook(str(path), data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    header_idx = _find_header_row(rows)
    if header_idx is None:
        raise ROMWorksheetParseError(
            f"Worksheet missing required columns: {', '.join(REQUIRED_HEADERS)}"
        )
    headers = [_norm(c) for c in rows[header_idx]]
    col = {h: i for i, h in enumerate(headers)}

    items = []
    for row in rows[header_idx + 1:]:
        if _is_section_divider(row):
            continue
        if not _is_data_row(row, col):
            # End of data table: first all-empty row after items
            continue
        items.append(_parse_row(row, col))

    return ROMWorksheetData(line_items=tuple(items))


def _find_header_row(rows) -> int | None:
    needed = set(REQUIRED_HEADERS)
    for i, row in enumerate(rows):
        cells = {_norm(c) for c in row}
        if needed.issubset(cells):
            return i
    return None


def _norm(cell) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _is_section_divider(row) -> bool:
    """A divider row has a single label cell in column A starting with 'Section '."""
    if not row or row[0] is None:
        return False
    first = _norm(row[0])
    rest_empty = all(_norm(c) == "" for c in row[1:])
    return first.lower().startswith("section ") and rest_empty


def _is_data_row(row, col: dict) -> bool:
    """A data row has a non-empty `#` and `Item Name`."""
    code = _norm(row[col["#"]]) if col["#"] < len(row) else ""
    name = _norm(row[col["Item Name"]]) if col["Item Name"] < len(row) else ""
    return bool(code) and bool(name)


def _int_or_zero(v) -> int:
    if v is None or v == "":
        return 0
    return int(v)


def _parse_row(row, col: dict) -> ROMLineItem:
    def cell(name: str) -> str:
        i = col.get(name)
        if i is None or i >= len(row):
            return ""
        return _norm(row[i])
    def cell_int(name: str) -> int:
        i = col.get(name)
        if i is None or i >= len(row):
            return 0
        return _int_or_zero(row[i])

    return ROMLineItem(
        code=cell("#"),
        section=cell("Section"),
        name=cell("Item Name"),
        description=cell("Description / Build Notes"),
        alternate_group=cell("Alternate Group"),
        rental_low=cell_int("Rental Low"),
        rental_high=cell_int("Rental High"),
        purchase_ot_low=cell_int("Purchase OT Low"),
        purchase_ot_high=cell_int("Purchase OT High"),
        purchase_svc_low=cell_int("Purchase Svc Low"),
        purchase_svc_high=cell_int("Purchase Svc High"),
        customer_facing=cell("Customer-Facing Description"),
        materials=cell("Materials / Build"),
        notes=cell("Notes / Assumptions"),
        rendering_ref=cell("Rendering Reference"),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_parser_worksheet_rom.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/parser/worksheet_rom.py tests/test_parser_worksheet_rom.py
git commit -m "feat(plan-9): ROM worksheet parser handles FIGat7th 15-column schema with section dividers"
```

---

## Task 3: Brief Menu-Mode Parser

**Files:**
- Modify: `skill_assets/proposal_build/parser/brief.py` — add menu-mode validation
- Test: `tests/test_parser_brief_menu_mode.py`

Menu-mode briefs differ from tiered: they have `mode: menu` in frontmatter, drop `recommended_tier` / `pricing_format` / `zones`, and add `sections` (an ordered list of `{key, label, name, is_lead, item_codes}`). Pre-built cover / palette / creative-vision hero are filenames.

- [ ] **Step 1: Write the failing test**

Create `tests/test_parser_brief_menu_mode.py`:

```python
"""Tests for menu-mode (creative-menu / ROM) Brief parsing.

The existing tiered-mode parse continues to work unchanged; this test
focuses on the new mode-detection and validation path.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from proposal_build.parser.brief import parse_brief, BriefParseError


def _write_brief(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "Project Brief.md"
    p.write_text(dedent(content).lstrip("\n"))
    return p


MENU_BRIEF_VALID = """
---
status: ready
mode: menu

client_company: "FIGat7th"
client_decision_maker: "Alexandra Castro"
client_decision_maker_title: "Property Manager, Athena PM"
client_decision_maker_email: "acastro@athenapm.com"

project_name: "FIGat7th DTLA — 2026 Holiday Program"
project_short: "FIGat7th DTLA"
project_year: 2026

design_phrase: "Modern Magic"
voice: "destination-retail"

prebuilt_cover_image: "01_cover-slide-cityscape.png"
prebuilt_palette_image: "02_palette-board-mood.png"
creative_vision_hero: "10_tree-A-studio-blackbg.png"

sections:
  - { key: "1",  label: "Section 1 — Main Entrance Overhead",   name: "Main Entrance Overhead", is_lead: true,  item_codes: ["20"] }
  - { key: "2",  label: "Section 2 — Holiday Tree + Photo Op",  name: "The FIGat7th Tree",      is_lead: true,  item_codes: ["10", "10-enh"] }
  - { key: "3a", label: "Section 3a — Plaza Arches",            name: "Plaza Photo-Ops",        is_lead: true,  item_codes: ["33", "32", "30", "31"] }
  - { key: "3b", label: "Section 3b — Plaza Photo-Ops",         name: "Plaza Photo-Ops",        is_lead: false, item_codes: ["40", "41", "42", "43"] }
---

## Creative Direction

FIGat7th becomes Downtown LA's most photographed holiday destination.

## Customer Goals

- Drive incremental foot traffic.
- Generate Instagram-worthy moments.
- Athena's first-year statement.

## Showcase Sections

1. **Main Entrance Overhead** — An ornament canopy that turns the courtyard ceiling into a winter night sky.
2. **The FIGat7th Tree** — The centerpiece every shopper poses with.
3. **Plaza Photo-Ops** — A menu of arches, frames, and selfie moments.
"""


def test_menu_mode_parses(tmp_path):
    """Menu-mode briefs parse without requiring tier-related fields."""
    path = _write_brief(tmp_path, MENU_BRIEF_VALID)
    brief = parse_brief(path)
    assert brief.frontmatter["mode"] == "menu"
    assert brief.frontmatter["design_phrase"] == "Modern Magic"
    assert len(brief.frontmatter["sections"]) == 4


def test_menu_mode_rejects_when_sections_missing(tmp_path):
    """Brief with mode: menu but no sections list is rejected."""
    bad = MENU_BRIEF_VALID.replace(
        "sections:\n  - { key:", "# sections removed\n# - { key:"
    )
    path = _write_brief(tmp_path, bad)
    with pytest.raises(BriefParseError, match="sections"):
        parse_brief(path)


def test_menu_mode_rejects_tiered_fields(tmp_path):
    """Brief with mode: menu must not carry recommended_tier or zones."""
    bad = MENU_BRIEF_VALID.replace(
        "mode: menu",
        'mode: menu\nrecommended_tier: "essential"',
    )
    path = _write_brief(tmp_path, bad)
    with pytest.raises(BriefParseError, match="recommended_tier"):
        parse_brief(path)


def test_tiered_mode_unchanged(tmp_path):
    """An existing tiered-mode Brief (no `mode` field, defaults to tiered) still parses."""
    tiered = """
        ---
        status: ready
        client_company: "RCTC"
        project_name: "Riverside MetroLink"
        project_year: 2026
        presenter_name: "Jonathan Yang"
        voice: "civic"
        recommended_tier: "enhanced"
        pricing_format: "three"
        cover_image: "tree.png"
        zones:
          - { name: "Downtown", subtitle: "flagship", flags: [flagship] }
        ---

        ## Creative Direction
        Civic-scale program.
    """
    path = _write_brief(tmp_path, tiered)
    brief = parse_brief(path)
    # mode field absent → tiered default behavior is preserved
    assert brief.frontmatter.get("mode", "tiered") == "tiered"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser_brief_menu_mode.py -v`
Expected: at least `test_menu_mode_rejects_when_sections_missing` and `test_menu_mode_rejects_tiered_fields` fail because the parser doesn't yet check those.

- [ ] **Step 3: Extend `brief.py` with menu-mode validation**

Modify `skill_assets/proposal_build/parser/brief.py`. Replace the `parse_brief` function body's required-field check with mode-aware logic:

```python
TIERED_REQUIRED_FIELDS = (
    "client_company", "project_name", "project_year", "presenter_name",
    "voice", "recommended_tier", "pricing_format", "cover_image",
)
MENU_REQUIRED_FIELDS = (
    "client_company", "project_name", "project_year",
    "voice", "design_phrase",
    "prebuilt_cover_image", "creative_vision_hero",
    "sections",
)
MENU_FORBIDDEN_FIELDS = ("recommended_tier", "pricing_format", "zones")


def parse_brief(path: Path) -> BriefData:
    """Parse a Brief.md file into BriefData. Raises BriefParseError on hard issues."""
    if not path.exists():
        raise BriefParseError(f"Brief not found at {path}")

    post = frontmatter.load(str(path))
    fm = dict(post.metadata)
    mode = fm.get("mode", "tiered")

    if mode == "menu":
        _validate_menu_mode(fm)
    elif mode == "tiered":
        _validate_tiered_mode(fm)
    else:
        raise BriefParseError(f"Unknown mode: {mode!r} (expected 'tiered' or 'menu')")

    sections = _split_sections(post.content)
    return BriefData(frontmatter=fm, sections=sections)


def _validate_tiered_mode(fm: dict) -> None:
    missing = [f for f in TIERED_REQUIRED_FIELDS if not fm.get(f)]
    if missing:
        raise BriefParseError(f"Brief missing required fields: {', '.join(missing)}")
    if not fm.get("zones"):
        raise BriefParseError("Brief missing required field: zones (must be non-empty list)")
    sigs = [z for z in fm["zones"] if "signature" in (z.get("flags") or [])]
    if len(sigs) > 1:
        names = ", ".join(z["name"] for z in sigs)
        raise BriefParseError(f"At most one zone may carry the 'signature' flag; found: {names}")


def _validate_menu_mode(fm: dict) -> None:
    missing = [f for f in MENU_REQUIRED_FIELDS if not fm.get(f)]
    if missing:
        raise BriefParseError(f"Menu-mode Brief missing required fields: {', '.join(missing)}")
    forbidden = [f for f in MENU_FORBIDDEN_FIELDS if fm.get(f)]
    if forbidden:
        raise BriefParseError(
            f"Menu-mode Brief carries fields used only in tiered mode: {', '.join(forbidden)}"
        )
    if not isinstance(fm["sections"], list) or not fm["sections"]:
        raise BriefParseError("Menu-mode Brief: `sections` must be a non-empty list")
    for s in fm["sections"]:
        for required_key in ("key", "label", "name", "is_lead", "item_codes"):
            if required_key not in s:
                raise BriefParseError(
                    f"Menu-mode section missing key: {required_key!r}"
                )
        if not s["item_codes"]:
            raise BriefParseError(
                f"Menu-mode section {s['key']!r} has empty item_codes"
            )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_parser_brief_menu_mode.py -v`
Expected: 4 passed. Also run the existing brief tests to confirm no regression:
Run: `pytest tests/test_parser_brief.py -v` (if the file exists; else `pytest tests/ -k brief -v`).
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/parser/brief.py tests/test_parser_brief_menu_mode.py
git commit -m "feat(plan-9): brief parser accepts mode: menu with sections schema"
```

---

## Task 4: Author the FIGat7th Brief on Disk

**Files:**
- Modify: `Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/Project Brief.md` — add menu-mode frontmatter

The current FIGat7th Brief was written for the hand-authored fixture and uses tiered-mode frontmatter fields. To validate the menu-mode pipeline end-to-end, rewrite it using the new schema. Customer-facing prose stays unchanged.

- [ ] **Step 1: Write the new Brief**

Replace `Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/Project Brief.md` entirely with:

```markdown
---
status: ready
mode: menu

client_company: "FIGat7th"
client_decision_maker: "Alexandra Castro"
client_decision_maker_title: "Property Manager, Athena Property Management"
client_decision_maker_email: "acastro@athenapm.com"

project_name: "FIGat7th DTLA — 2026 Holiday Program"
project_short: "FIGat7th DTLA"
project_year: 2026
project_subtitle: "First-Pass Creative Menu"

presenter_name: "Daniel Christenson"
presenter_title: "Director of Sales"
presenter_org: "St. Nick's Christmas Lighting & Décor"
proposal_date: "May 9, 2026"

design_phrase: "Modern Magic"
voice: "destination-retail"

prebuilt_cover_image: "01_cover-slide-cityscape.png"
prebuilt_palette_image: "02_palette-board-mood.png"
creative_vision_hero: "10_tree-A-studio-blackbg.png"
creative_vision_hero_fit: "contain"

what_youre_approving: "This first-pass creative menu and rough-order-of-magnitude pricing as the basis for site walk and final scope refinement. Approval here authorizes St. Nick's to schedule the on-site walk-through with Athena Property Management and prepare a finalized scope and committed pricing for execution."

creative_phases:
  - { label: "ARRIVE",  body: "An ornament canopy turns the FIGat7th courtyard ceiling into a winter night sky." }
  - { label: "GATHER",  body: "The centerpiece tree anchors the plaza as the moment every shopper poses with." }
  - { label: "EXPLORE", body: "A menu of arches, frames, and selfie moments scattered through the plaza." }

sections:
  - { key: "1",  label: "Section 1 — Main Entrance Overhead",        name: "Main Entrance Overhead", is_lead: true,  item_codes: ["20"] }
  - { key: "2",  label: "Section 2 — Holiday Tree + Photo Op",       name: "The FIGat7th Tree",      is_lead: true,  item_codes: ["10", "10-enh"] }
  - { key: "3a", label: "Section 3a — Plaza Arches (customer picks one)", name: "Plaza Photo-Ops",   is_lead: true,  item_codes: ["33", "32", "30", "31"] }
  - { key: "3b", label: "Section 3b — Plaza Photo-Ops (all included)",    name: "Plaza Photo-Ops",   is_lead: false, item_codes: ["40", "41", "42", "43"] }
---

## Creative Direction

FIGat7th becomes Downtown LA's most photographed holiday destination, where a modern landmark turns into a glowing photo op after dark. The energy is upscale, festive, and dressed up for the camera, built for FIGat7th's nightlife audience rather than the traditional family-in-PJs crowd. Sapphire teal, jewel teal, and champagne gold carry the property's signature color story through every moment.

## Customer Goals

- Drive incremental foot traffic and dwell time across the plaza throughout November and December.
- Generate Instagram-worthy moments that turn every shopper photo into organic reach for the property.
- Make this holiday season Athena PM's signature first-year statement on FIGat7th in their first year managing the property.

## Showcase Sections

1. **Main Entrance Overhead** — An ornament canopy that turns the courtyard ceiling into a winter night sky.
2. **The FIGat7th Tree** — The centerpiece every shopper poses with, framed in the property's signature glow.
3. **Plaza Photo-Ops** — A menu of arches, frames, and selfie moments scattered through the plaza.
```

- [ ] **Step 2: Verify the Brief parses**

Run:
```bash
python -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from proposal_build.parser.brief import parse_brief
b = parse_brief(Path('Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/Project Brief.md'))
print('mode:', b.frontmatter['mode'])
print('sections:', len(b.frontmatter['sections']))
"
```
Expected: `mode: menu` / `sections: 4`.

- [ ] **Step 3: Commit**

```bash
git add "Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/Project Brief.md"
git commit -m "feat(plan-9): rewrite FIGat7th Brief in menu-mode schema with sections + ROM frontmatter"
```

---

## Task 5: Parser Orchestrator Routing

**Files:**
- Modify: `skill_assets/proposal_build/parser/__init__.py` — route to menu pipeline when mode==menu
- Create: `skill_assets/proposal_build/parser/menu_resolver.py` — assembles MenuProjectModel from BriefData + ROMWorksheetData
- Test: `tests/test_parser_menu_pipeline.py`

The orchestrator currently builds `ProjectModel` from `BriefData` + `WorksheetData`. For menu mode it needs to build `MenuProjectModel` from `BriefData` + `ROMWorksheetData`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_parser_menu_pipeline.py`:

```python
"""Full menu-mode pipeline test: Brief + ROM Worksheet → MenuProjectModel."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.models import MenuProjectModel, ROMLineItem, Section


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def test_parse_figat7th_yields_menu_model():
    model = parse_project(FIGAT7TH)
    assert isinstance(model, MenuProjectModel)
    assert model.client_company == "FIGat7th"
    assert model.design_phrase == "Modern Magic"


def test_figat7th_sections_match_brief_order():
    model = parse_project(FIGAT7TH)
    keys = [s.key for s in model.sections]
    assert keys == ["1", "2", "3a", "3b"]


def test_figat7th_section_3a_items_in_brief_order():
    """Arches section emits items in the order specified by the Brief's
    item_codes (D=33, C=32, A=30, B=31) — same order the customer sees on the deck."""
    model = parse_project(FIGAT7TH)
    arches = next(s for s in model.sections if s.key == "3a")
    codes = [it.code for it in arches.items]
    assert codes == ["33", "32", "30", "31"]


def test_figat7th_line_item_count():
    """11 priced items, distributed across 4 sections."""
    model = parse_project(FIGAT7TH)
    total = sum(len(s.items) for s in model.sections)
    assert total == 11
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser_menu_pipeline.py -v`
Expected: ImportError or attribute error — `parse_project` doesn't yet handle menu mode.

- [ ] **Step 3: Create the menu resolver**

Create `skill_assets/proposal_build/parser/menu_resolver.py`:

```python
"""Assemble MenuProjectModel from parsed Brief + ROM Worksheet data."""
from __future__ import annotations

from typing import Mapping

from proposal_build.models import MenuProjectModel, ROMLineItem, Section
from proposal_build.parser.brief import BriefData
from proposal_build.parser.worksheet_rom import ROMWorksheetData


def resolve_menu_project(
    brief: BriefData, worksheet: ROMWorksheetData
) -> MenuProjectModel:
    """Combine BriefData (menu-mode) + ROMWorksheetData into a MenuProjectModel.

    Sections are built in Brief order; within each section, items appear in
    the Brief's item_codes order (NOT worksheet order — Brief is authoritative
    on customer-facing display sequence).
    """
    fm = brief.frontmatter
    items_by_code: Mapping[str, ROMLineItem] = {it.code: it for it in worksheet.line_items}

    sections = []
    for s in fm["sections"]:
        items = []
        for code in s["item_codes"]:
            if code not in items_by_code:
                raise ValueError(
                    f"Section {s['key']!r} references item code {code!r} "
                    f"not found in the worksheet"
                )
            items.append(items_by_code[code])
        sections.append(Section(
            key=s["key"],
            label=s["label"],
            name=s["name"],
            is_lead=bool(s["is_lead"]),
            items=tuple(items),
        ))

    return MenuProjectModel(
        client_company=fm["client_company"],
        client_short=fm.get("project_short", fm["client_company"]),
        project_name=fm["project_name"],
        project_short=fm.get("project_short", fm["project_name"]),
        project_year=int(fm["project_year"]),
        project_subtitle=fm.get("project_subtitle", ""),
        presenter_name=fm.get("presenter_name", ""),
        presenter_title=fm.get("presenter_title", ""),
        presenter_org=fm.get("presenter_org", ""),
        proposal_date=fm.get("proposal_date", ""),
        client_contact_name=fm.get("client_decision_maker", ""),
        client_contact_title=fm.get("client_decision_maker_title", ""),
        client_contact_email=fm.get("client_decision_maker_email", ""),
        client_contact_phone=fm.get("client_decision_maker_phone", ""),
        design_phrase=fm["design_phrase"],
        voice=fm["voice"],
        creative_direction=_section_text(brief, "Creative Direction"),
        customer_goals=tuple(_section_list(brief, "Customer Goals")),
        creative_phases=tuple(fm.get("creative_phases", ())),
        prebuilt_cover_image=fm["prebuilt_cover_image"],
        prebuilt_palette_image=fm.get("prebuilt_palette_image", ""),
        creative_vision_hero=fm["creative_vision_hero"],
        sections=tuple(sections),
        what_youre_approving=fm.get("what_youre_approving", ""),
    )


def _section_text(brief: BriefData, name: str) -> str:
    v = brief.sections.get(name, "")
    return v if isinstance(v, str) else ""


def _section_list(brief: BriefData, name: str) -> list[str]:
    v = brief.sections.get(name, [])
    return list(v) if isinstance(v, list) else []
```

- [ ] **Step 4: Wire up the orchestrator**

In `skill_assets/proposal_build/parser/__init__.py`, locate the existing `parse_project()` function (or whatever the top-level entry is). At the top of its body, after the Brief is parsed and before the existing tiered logic runs, add the menu-mode branch:

```python
# After parse_brief(brief_path) returns `brief`:
if brief.frontmatter.get("mode", "tiered") == "menu":
    from proposal_build.parser.worksheet_rom import parse_rom_worksheet
    from proposal_build.parser.menu_resolver import resolve_menu_project
    ws = parse_rom_worksheet(_find_worksheet_path(project_dir))
    return resolve_menu_project(brief, ws)
# Else, continue with the existing tiered path...
```

(If `parse_project` does not exist in the orchestrator yet, locate the equivalent top-level function and apply the same branch.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_parser_menu_pipeline.py -v`
Expected: 4 passed.

Run: `pytest tests/ -q` (full suite) to confirm tiered fixtures still parse.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/parser/__init__.py skill_assets/proposal_build/parser/menu_resolver.py tests/test_parser_menu_pipeline.py
git commit -m "feat(plan-9): parser orchestrator routes menu mode through ROM resolver"
```

---

## Task 6: Menu-Mode Ctx Builders

**Files:**
- Create: `skill_assets/proposal_build/composer/menu_ctx_builders.py`
- Test: `tests/test_composer_menu_ctx_builders.py`

Mirror the tiered composer's `ctx_builders.py` for the menu-mode layouts. Each builder takes the model + page numbers + section/items and returns a dict ready for the renderer.

- [ ] **Step 1: Write the failing test**

Create `tests/test_composer_menu_ctx_builders.py`:

```python
"""Unit tests for menu-mode ctx builders."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.composer.menu_ctx_builders import (
    build_image_fullbleed_ctx,
    build_menu_creative_vision_ctx,
    build_menu_zone_solo_ctx,
    build_menu_zone_2up_gallery_ctx,
    build_menu_rom_investment_ctx,
    build_menu_sign_off_ctx,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


@pytest.fixture(scope="module")
def model():
    return parse_project(FIGAT7TH)


def test_image_fullbleed_cover(model):
    ctx = build_image_fullbleed_ctx(model, page_num=1, page_total=12, kind="cover")
    assert ctx["page_num"] == 1
    assert ctx["page_total"] == 12
    assert ctx["hero_image"].endswith("01_cover-slide-cityscape.png")


def test_image_fullbleed_palette(model):
    ctx = build_image_fullbleed_ctx(model, page_num=2, page_total=12, kind="palette")
    assert ctx["hero_image"].endswith("02_palette-board-mood.png")


def test_creative_vision_passes_phases_and_hero(model):
    ctx = build_menu_creative_vision_ctx(model, page_num=3, page_total=12)
    assert ctx["design_phrase"].startswith("Modern Magic")
    assert ctx["hero_fit"] == "contain"
    assert len(ctx["phases"]) == 3


def test_zone_solo_for_single_item_section(model):
    """Section 1 (canopy) renders as zone_solo with section header inlined."""
    section = next(s for s in model.sections if s.key == "1")
    ctx = build_menu_zone_solo_ctx(model, section, page_num=4, page_total=12)
    assert ctx["section_label"] == "Section One"
    assert ctx["section_name"] == "Main Entrance Overhead"
    assert ctx["zone_name"] == "Mixed Ornament Canopy"
    assert ctx["hero_image"].endswith("20_overhead-mixed-canopy.png")


def test_zone_2up_gallery_for_arch_alternates(model):
    """Section 3a, slide A: first two arches with section header + alt banner."""
    section = next(s for s in model.sections if s.key == "3a")
    ctx = build_menu_zone_2up_gallery_ctx(
        model, section, items=section.items[:2],
        page_num=6, page_total=12, is_first_slide_of_section=True,
        alternate_banner="Customer Choice — Pick One",
    )
    assert ctx["section_label"] == "Section Three"
    assert ctx["section_name"] == "Plaza Photo-Ops"
    assert ctx["alternate_banner"] == "Customer Choice — Pick One"
    assert len(ctx["cells"]) == 2
    # Option A is the first item in the Brief order (which is rendering 33)
    assert ctx["cells"][0]["eyebrow"] == "OPTION A"


def test_rom_investment_totals(model):
    """ROM totals math: rental, purchase OT, purchase service — verified
    against the FIGat7th values locked in session memory."""
    ctx = build_menu_rom_investment_ctx(
        model, page_num=10, page_total=12, page_part=1,
    )
    # When page_part=1, totals are not shown (continuation slide carries them).
    assert ctx["show_totals"] is False
    ctx2 = build_menu_rom_investment_ctx(
        model, page_num=11, page_total=12, page_part=2,
    )
    assert ctx2["show_totals"] is True
    assert ctx2["total_rental"] == "$227,150 – $234,650"
    assert ctx2["total_purchase_ot"] == "$280,000 – $289,600"
    assert ctx2["total_purchase_svc"] == "$117,000 – $120,900"


def test_sign_off_uses_dm_contact(model):
    ctx = build_menu_sign_off_ctx(model, page_num=12, page_total=12)
    assert ctx["client_contact_name"] == "Alexandra Castro"
    assert ctx["client_contact_email"] == "acastro@athenapm.com"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_composer_menu_ctx_builders.py -v`
Expected: ImportError — module doesn't exist yet.

- [ ] **Step 3: Create the ctx builders**

Create `skill_assets/proposal_build/composer/menu_ctx_builders.py`:

```python
"""Ctx builders for menu-mode (creative-menu / ROM) layouts.

Each builder takes the MenuProjectModel + page coordinates + any needed
section/items, and returns a dict ready for renderer/pdf.py.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from proposal_build.models import MenuProjectModel, ROMLineItem, Section


# Word-form section labels for the deck header strip ("Section One", "Section Two", ...).
_SECTION_WORDS = {
    "1": "Section One",
    "2": "Section Two",
    "3": "Section Three",
    "3a": "Section Three",
    "3b": "Section Three",
}


def _project_dir_from_model(model: MenuProjectModel) -> Path:
    """The project dir is needed to resolve rendering filenames into file URIs.

    The model itself doesn't carry it; the orchestrator sets it on the model
    via _resolved_project_dir below (see compose_menu in Task 7)."""
    return getattr(model, "_resolved_project_dir", Path("."))


def _resolve_image_uri(model: MenuProjectModel, filename: str) -> str:
    if not filename:
        return ""
    project_dir = _project_dir_from_model(model)
    return (project_dir / "02 - Renderings" / "Base Scope" / filename).as_uri()


def _project_dict(model: MenuProjectModel) -> dict:
    """The shared project block every slide includes (matches the base.html footer needs)."""
    return {
        "client_company": model.client_company,
        "client_short": model.client_short,
        "project_name": model.project_name,
        "project_short": model.project_short,
        "project_year": model.project_year,
        "project_subtitle": model.project_subtitle,
        "presenter_name": model.presenter_name,
        "presenter_title": model.presenter_title,
        "presenter_org": model.presenter_org,
        "proposal_date": model.proposal_date,
    }


def build_image_fullbleed_ctx(
    model: MenuProjectModel, page_num: int, page_total: int, *, kind: str
) -> dict:
    """kind: 'cover' or 'palette'. Picks the right pre-built image."""
    if kind == "cover":
        image = model.prebuilt_cover_image
        alt = f"{model.project_name} — Cover"
    elif kind == "palette":
        image = model.prebuilt_palette_image
        alt = f"{model.project_name} — Selected Ornament Palette"
    else:
        raise ValueError(f"image_fullbleed kind must be 'cover' or 'palette', got {kind!r}")
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": alt,
        "hero_image": _resolve_image_uri(model, image),
        "alt_text": alt,
    }


def build_menu_creative_vision_ctx(
    model: MenuProjectModel, page_num: int, page_total: int
) -> dict:
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": "Creative Vision",
        "standfirst": f"The design direction for {model.client_short}'s {model.project_year} holiday program.",
        "design_phrase": model.design_phrase + ".",
        "design_direction_body": model.creative_direction,
        "phases": list(model.creative_phases),
        "hero_image": _resolve_image_uri(model, model.creative_vision_hero),
        "hero_fit": "contain",
    }


def build_menu_zone_solo_ctx(
    model: MenuProjectModel, section: Section, page_num: int, page_total: int
) -> dict:
    """Single-item section (canopy, tree). Inlines section header on the slide."""
    item = section.items[0]
    bullets = _bullets_for_item(item, extras=(section.items[1:] if len(section.items) > 1 else ()))
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "section_label": _SECTION_WORDS.get(section.key, section.label),
        "section_name": section.name,
        "zone_num": _two_digit_code(item.code),
        "zone_name": item.name,
        "zone_subtitle": item.customer_facing,
        "included_elements": bullets,
        "hero_image": _resolve_image_uri(model, item.rendering_ref),
        "hero_fit": "contain",
    }


def _bullets_for_item(item: ROMLineItem, *, extras: Iterable[ROMLineItem] = ()) -> list[str]:
    """Build the bullet list for a zone_solo cell from materials + extras' names."""
    bullets = []
    if item.materials:
        # Split materials field at semicolons; one bullet per clause.
        bullets.extend(b.strip() for b in item.materials.split(";") if b.strip())
    for x in extras:
        bullets.append(x.customer_facing or x.name)
    return bullets


def _two_digit_code(code: str) -> str:
    """Drop suffixes like '-enh' so the eyebrow reads ZONE 01 / ZONE 10."""
    base = code.split("-")[0]
    if base.isdigit() and len(base) <= 2:
        return base.zfill(2)
    return code


def build_menu_zone_2up_gallery_ctx(
    model: MenuProjectModel, section: Section,
    items: tuple[ROMLineItem, ROMLineItem],
    page_num: int, page_total: int,
    *, is_first_slide_of_section: bool, alternate_banner: str = "",
) -> dict:
    """Two-cell image gallery. First slide of section carries section header."""
    eyebrow_offsets = {0: "OPTION A", 1: "OPTION B"} if is_first_slide_of_section \
                      else {0: "OPTION C", 1: "OPTION D"}
    # Standalone sections don't use OPTION letters; they use MOMENT NN counted from 01.
    # The caller signals this via the alternate_banner: "All ... Included" → MOMENT.
    use_moment_labels = "All" in alternate_banner and "Included" in alternate_banner
    if use_moment_labels:
        base = 1 if is_first_slide_of_section else 3
        eyebrow_offsets = {0: f"MOMENT 0{base}", 1: f"MOMENT 0{base+1}"}

    cells = []
    for i, item in enumerate(items):
        cells.append({
            "eyebrow": eyebrow_offsets[i],
            "name": item.name,
            "hero_image": _resolve_image_uri(model, item.rendering_ref),
        })

    ctx = {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": ("Plaza Arches" if section.has_alternates else "Plaza Moments")
                      + ("" if is_first_slide_of_section else " (continued)"),
        "standfirst": _gallery_standfirst(section, is_first_slide_of_section),
        "alternate_banner": alternate_banner,
        "cells": cells,
    }
    if is_first_slide_of_section and section.is_lead:
        ctx["section_label"] = _SECTION_WORDS.get(section.key, section.label)
        ctx["section_name"] = section.name
    return ctx


def _gallery_standfirst(section: Section, is_first: bool) -> str:
    if section.has_alternates:
        return ("Four walk-through arch directions. Each can stand alone as the moment. "
                "Options A and B follow; Options C and D on the next page.") if is_first else \
               "Options C and D — the final two arch directions for customer choice."
    return ("Four standalone photo-ops scattered through the plaza. "
            "Moments 01 and 02 below; Moments 03 and 04 on the next page.") if is_first else \
           "Moments 03 and 04 round out the standalone plaza photo-op program."


def build_menu_rom_investment_ctx(
    model: MenuProjectModel, page_num: int, page_total: int, *, page_part: int
) -> dict:
    """page_part: 1 = sections 1+2+3a (no totals/footnote); 2 = section 3b + totals + footnote."""
    from proposal_build.composer.rom_pricing import (
        rows_for_sections, compute_rom_totals, format_money_range
    )

    if page_part == 1:
        sections_data = _investment_sections(model, keys=("1", "2", "3a"))
        return {
            **_project_dict(model),
            "page_num": page_num,
            "page_total": page_total,
            "page_title": "Investment",
            "standfirst": "Rough order of magnitude pricing — Sections 1, 2, and 3a (continued on next page).",
            "sections": sections_data,
            "show_totals": False,
            "total_rental": "",
            "total_purchase_ot": "",
            "total_purchase_svc": "",
            "footnote": "",
        }

    # page_part == 2
    totals = compute_rom_totals(model.sections)
    sections_data = _investment_sections(model, keys=("3b",))
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": "Investment (continued)",
        "standfirst": "Section 3b plus program total. Customer can mix and match rental and purchase per item.",
        "sections": sections_data,
        "show_totals": True,
        "total_rental": format_money_range(totals["rental_low"], totals["rental_high"]),
        "total_purchase_ot": format_money_range(totals["purchase_ot_low"], totals["purchase_ot_high"]),
        "total_purchase_svc": format_money_range(totals["purchase_svc_low"], totals["purchase_svc_high"]),
        "footnote": _rom_footnote(),
    }


def _investment_sections(model: MenuProjectModel, *, keys) -> list[dict]:
    from proposal_build.composer.rom_pricing import format_money_range
    out = []
    for section in model.sections:
        if section.key not in keys:
            continue
        rows = []
        for it in section.items:
            rows.append({
                "name": it.name,
                "description": "",
                "is_alternate": it.is_alternate,
                "rental_price": format_money_range(it.rental_low, it.rental_high),
                "purchase_ot_price": format_money_range(it.purchase_ot_low, it.purchase_ot_high),
                "purchase_svc_price": format_money_range(it.purchase_svc_low, it.purchase_svc_high),
            })
        out.append({"label": section.label, "rows": rows})
    return out


def _rom_footnote() -> str:
    return (
        "<strong>Rental</strong> is an annual all-inclusive fee covering item, install, removal, and storage. "
        "<strong>Purchase</strong> is a one-time price plus a separate annual service fee for install, removal, and storage. "
        "Plaza arches are mutually exclusive — Program ROM Total is bookended by the cheapest-pick (low) and "
        "most-expensive-pick (high) configurations. All figures are rough order of magnitude for first-pass scoping; "
        "final numbers will follow site walk and scope refinement."
    )


def build_menu_sign_off_ctx(
    model: MenuProjectModel, page_num: int, page_total: int
) -> dict:
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": "Let's Make It Happen",
        "standfirst": f"Next steps to lock the {model.client_short} {model.project_year} program.",
        "what_youre_approving": model.what_youre_approving,
        "client_party_label": f"{model.client_short} — {model.client_contact_title.split(',')[-1].strip() if ',' in model.client_contact_title else 'Client'}",
        "client_contact_name": model.client_contact_name,
        "client_contact_title": model.client_contact_title,
        "client_contact_email": model.client_contact_email,
        "client_contact_phone": model.client_contact_phone,
        "stnicks_party_label": "St. Nick's Christmas Lighting & Décor",
        "digital_signing_note": "This proposal may be approved digitally — a countersigned PDF is sufficient to proceed.",
    }
```

- [ ] **Step 4: Create the rom_pricing helper module**

Create `skill_assets/proposal_build/composer/rom_pricing.py`:

```python
"""ROM pricing math: per-section row formatting + totals with alternate-group bookending."""
from __future__ import annotations

from typing import Iterable

from proposal_build.models import Section, ROMLineItem


def format_money(n: int) -> str:
    return f"${n:,}"


def format_money_range(low: int, high: int) -> str:
    if low == high:
        return format_money(low)
    return f"{format_money(low)} – {format_money(high)}"


def compute_rom_totals(sections: Iterable[Section]) -> dict:
    """Sum across all sections. Within each alternate_group, take min(low) /
    max(high) instead of summing — only one alternate is in scope at a time."""
    rental_low = rental_high = 0
    po_low = po_high = 0
    psv_low = psv_high = 0

    # Bucket alternates by group
    groups: dict[str, list[ROMLineItem]] = {}
    non_alts: list[ROMLineItem] = []
    for section in sections:
        for it in section.items:
            if it.is_alternate:
                groups.setdefault(it.alternate_group, []).append(it)
            else:
                non_alts.append(it)

    for it in non_alts:
        rental_low += it.rental_low
        rental_high += it.rental_high
        po_low += it.purchase_ot_low
        po_high += it.purchase_ot_high
        psv_low += it.purchase_svc_low
        psv_high += it.purchase_svc_high

    for items in groups.values():
        rental_low += min(it.rental_low for it in items)
        rental_high += max(it.rental_high for it in items)
        po_low += min(it.purchase_ot_low for it in items)
        po_high += max(it.purchase_ot_high for it in items)
        psv_low += min(it.purchase_svc_low for it in items)
        psv_high += max(it.purchase_svc_high for it in items)

    return {
        "rental_low": rental_low, "rental_high": rental_high,
        "purchase_ot_low": po_low, "purchase_ot_high": po_high,
        "purchase_svc_low": psv_low, "purchase_svc_high": psv_high,
    }


def rows_for_sections(sections, keys):
    """Re-export for ctx_builders import surface symmetry; thin pass-through used in early prototypes."""
    return [s for s in sections if s.key in keys]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_composer_menu_ctx_builders.py -v`
Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/composer/menu_ctx_builders.py skill_assets/proposal_build/composer/rom_pricing.py tests/test_composer_menu_ctx_builders.py
git commit -m "feat(plan-9): ctx builders + ROM totals math for menu-mode layouts"
```

---

## Task 7: Menu Compose Orchestrator

**Files:**
- Create: `skill_assets/proposal_build/composer/menu_compose.py`
- Test: `tests/test_composer_menu_compose.py`

Assemble the slide list for a menu-mode project. Slide sequence is hard-coded for v1 (matches FIGat7th's locked structure):

1. cover (image_fullbleed)
2. palette (image_fullbleed)  — only if `prebuilt_palette_image` set
3. creative_vision
4..N-3. one zone_solo per single-item section; section header inlined on lead
       OR two zone_2up_gallery slides per multi-item section (lead slide carries section header)
N-2. rom_investment (page_part=1)
N-1. rom_investment (page_part=2)
N.   sign_off

- [ ] **Step 1: Write the failing test**

Create `tests/test_composer_menu_compose.py`:

```python
"""Tests for menu-mode slide list assembly."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.composer.menu_compose import compose_menu


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


@pytest.fixture(scope="module")
def slides():
    model = parse_project(FIGAT7TH)
    slides_, _docs = compose_menu(model)
    return slides_


def test_figat7th_compose_yields_twelve_slides(slides):
    assert len(slides) == 12


def test_figat7th_slide_layouts_in_order(slides):
    expected = [
        "image_fullbleed",   # 1 cover
        "image_fullbleed",   # 2 palette
        "creative_vision",   # 3
        "zone_solo",         # 4 canopy (Section 1 lead)
        "zone_solo",         # 5 tree (Section 2 lead)
        "zone_2up_gallery",  # 6 arches A (Section 3 lead)
        "zone_2up_gallery",  # 7 arches B (continuation)
        "zone_2up_gallery",  # 8 moments A
        "zone_2up_gallery",  # 9 moments B
        "rom_investment",    # 10 investment p1
        "rom_investment",    # 11 investment p2
        "sign_off",          # 12
    ]
    actual = [s.layout_name for s in slides]
    assert actual == expected


def test_page_numbers_continuous(slides):
    nums = [s.context["page_num"] for s in slides]
    assert nums == list(range(1, len(slides) + 1))
    assert all(s.context["page_total"] == len(slides) for s in slides)


def test_arches_first_slide_has_section_header(slides):
    arches_a = slides[5]
    assert arches_a.context["section_label"] == "Section Three"
    assert arches_a.context["section_name"] == "Plaza Photo-Ops"


def test_arches_continuation_slide_has_no_section_header(slides):
    arches_b = slides[6]
    assert "section_label" not in arches_b.context


def test_moments_alt_banner_is_all_included(slides):
    moments_a = slides[7]
    assert moments_a.context["alternate_banner"] == "All Four Included"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_composer_menu_compose.py -v`
Expected: ImportError.

- [ ] **Step 3: Create the compose orchestrator**

Create `skill_assets/proposal_build/composer/menu_compose.py`:

```python
"""Menu-mode compose orchestrator: MenuProjectModel → list of (layout, ctx) SlidePlanItems.

Slide sequence (FIGat7th-locked structure for v1):
  1. cover                      (image_fullbleed)
  2. palette                    (image_fullbleed; skipped when no prebuilt_palette_image)
  3. creative_vision
  4..K. section content slides
       - single-item section → 1 zone_solo with section header inlined on lead
       - multi-item section  → 2 zone_2up_gallery slides (or 1 if exactly 2 items),
         alternate-banner derived from section.has_alternates
  K+1. rom_investment p1 (sections 1+2+3a)
  K+2. rom_investment p2 (section 3b + totals)
  K+3. sign_off
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from proposal_build.models import MenuProjectModel, SlidePlanItem, Section
from proposal_build.composer.menu_ctx_builders import (
    build_image_fullbleed_ctx,
    build_menu_creative_vision_ctx,
    build_menu_zone_solo_ctx,
    build_menu_zone_2up_gallery_ctx,
    build_menu_rom_investment_ctx,
    build_menu_sign_off_ctx,
)


def compose_menu(model: MenuProjectModel) -> Tuple[list[SlidePlanItem], list]:
    """Returns (slides, []). The empty second tuple slot mirrors the tiered
    compose() signature (which returns itemized_pricing_docs); menu mode
    doesn't emit per-tier itemized PDFs for v1."""
    layout_hints: list[tuple[str, dict]] = []

    # 1. Cover
    layout_hints.append(("image_fullbleed", {"kind": "cover"}))

    # 2. Palette (conditional)
    if model.prebuilt_palette_image:
        layout_hints.append(("image_fullbleed", {"kind": "palette"}))

    # 3. Creative Vision
    layout_hints.append(("creative_vision_menu", {}))

    # 4..K. Section content
    for section in model.sections:
        layout_hints.extend(_section_slides(section))

    # Investment p1 + p2
    layout_hints.append(("rom_investment", {"page_part": 1}))
    layout_hints.append(("rom_investment", {"page_part": 2}))

    # Sign-off
    layout_hints.append(("sign_off_menu", {}))

    # Stamp page_num/page_total
    total = len(layout_hints)
    slides: list[SlidePlanItem] = []
    for i, (logical, hint) in enumerate(layout_hints, start=1):
        layout_name, ctx = _build_ctx(model, logical, i, total, hint)
        slides.append(SlidePlanItem(layout_name=layout_name, context=ctx))

    return slides, []


def _section_slides(section: Section) -> list[tuple[str, dict]]:
    """Emit one or two slides for a section."""
    if len(section.items) == 1:
        return [("zone_solo_menu", {"section": section})]
    if len(section.items) <= 2:
        return [("zone_2up_gallery_menu", {
            "section": section, "items": tuple(section.items[:2]),
            "is_first_slide_of_section": True,
            "alternate_banner": _alt_banner_for(section),
        })]
    # Multi-item: 2 slides of 2 cells each. For >4 items, extend later; v1 caps at 4.
    return [
        ("zone_2up_gallery_menu", {
            "section": section, "items": tuple(section.items[:2]),
            "is_first_slide_of_section": True,
            "alternate_banner": _alt_banner_for(section),
        }),
        ("zone_2up_gallery_menu", {
            "section": section, "items": tuple(section.items[2:4]),
            "is_first_slide_of_section": False,
            "alternate_banner": _alt_banner_for(section),
        }),
    ]


def _alt_banner_for(section: Section) -> str:
    if section.has_alternates:
        return "Customer Choice — Pick One"
    if len(section.items) == 4:
        return "All Four Included"
    return ""  # 2-item include section can omit banner


def _build_ctx(model: MenuProjectModel, logical: str, page_num: int, page_total: int, hint: dict):
    """Dispatch logical-name → real layout template + ctx."""
    if logical == "image_fullbleed":
        return "image_fullbleed", build_image_fullbleed_ctx(model, page_num, page_total, kind=hint["kind"])
    if logical == "creative_vision_menu":
        return "creative_vision", build_menu_creative_vision_ctx(model, page_num, page_total)
    if logical == "zone_solo_menu":
        return "zone_solo", build_menu_zone_solo_ctx(model, hint["section"], page_num, page_total)
    if logical == "zone_2up_gallery_menu":
        return "zone_2up_gallery", build_menu_zone_2up_gallery_ctx(
            model, hint["section"], hint["items"],
            page_num, page_total,
            is_first_slide_of_section=hint["is_first_slide_of_section"],
            alternate_banner=hint["alternate_banner"],
        )
    if logical == "rom_investment":
        return "rom_investment", build_menu_rom_investment_ctx(
            model, page_num, page_total, page_part=hint["page_part"]
        )
    if logical == "sign_off_menu":
        return "sign_off", build_menu_sign_off_ctx(model, page_num, page_total)
    raise ValueError(f"Unknown logical layout: {logical}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_composer_menu_compose.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/composer/menu_compose.py tests/test_composer_menu_compose.py
git commit -m "feat(plan-9): menu compose orchestrator emits 12-slide FIGat7th deck"
```

---

## Task 8: Composer Dispatcher + End-to-End Render

**Files:**
- Modify: `skill_assets/proposal_build/composer/__init__.py` — dispatch tiered vs menu
- Test: `tests/test_e2e_figat7th_menu_pipeline.py`

Wire the menu compose path into the top-level `compose()` so callers (CLI, tests) get the right slide list without needing to know which mode.

- [ ] **Step 1: Write the failing end-to-end test**

Create `tests/test_e2e_figat7th_menu_pipeline.py`:

```python
"""End-to-end test: parse FIGat7th project → compose → render PDF.

This is the regression test that proves Plan 9 produces the same 12-slide
deck shape as the hand-authored tests/fixtures/figat7th.py fixture.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.composer import compose
from proposal_build.renderer.pdf import render_proposal_pdf


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def test_figat7th_renders_to_pdf(tmp_path):
    model = parse_project(FIGAT7TH)
    slides, _pricing_docs = compose(model)
    assert len(slides) == 12

    out = tmp_path / "figat7th-deck.pdf"
    render_proposal_pdf([(s.layout_name, s.context) for s in slides], out)
    assert out.exists()
    assert out.stat().st_size > 100_000  # multi-page PDF is at least 100 KB
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_e2e_figat7th_menu_pipeline.py -v`
Expected: error in `compose()` — it doesn't know what to do with a MenuProjectModel.

- [ ] **Step 3: Dispatch in `composer/__init__.py`**

Modify `skill_assets/proposal_build/composer/__init__.py`. At the top of `compose()`, before the existing tiered logic, add:

```python
from proposal_build.models import MenuProjectModel

def compose(model):
    """Top-level dispatcher. Routes to tiered or menu compose path based on model type."""
    if isinstance(model, MenuProjectModel):
        from proposal_build.composer.menu_compose import compose_menu
        return compose_menu(model)
    # Existing tiered body follows unchanged.
    pricing_docs = build_itemized_pricing_docs(model)
    # ... (rest of the existing function body)
```

(Rename the existing `compose` function body to live inside the else branch, or extract it to `_compose_tiered(model)` and have the top-level `compose` dispatch.)

- [ ] **Step 4: Run the end-to-end test**

Run: `pytest tests/test_e2e_figat7th_menu_pipeline.py -v`
Expected: 1 passed.

- [ ] **Step 5: Confirm tiered fixtures still work**

Run: `pytest tests/ -q` — all tests should pass, including existing tiered fixtures (Riverside, Pier 39, Sheraton if a fixture exists).

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/composer/__init__.py tests/test_e2e_figat7th_menu_pipeline.py
git commit -m "feat(plan-9): composer dispatches tiered vs menu based on model type"
```

---

## Task 9: Inspector Updates for Menu Mode

**Files:**
- Modify: `skill_assets/proposal_build/inspector/brief.py` — accept menu-mode briefs without flagging missing tier fields
- Modify: `skill_assets/proposal_build/inspector/worksheet.py` — detect ROM worksheet shape and validate it
- Test: `tests/test_inspector_menu_mode.py`

The inspector currently asserts the presence of tier-specific fields. For menu-mode projects, those checks must skip; instead, the inspector checks for menu-required fields (sections, item_codes referenced by sections exist in the ROM worksheet, etc.).

- [ ] **Step 1: Write the failing test**

Create `tests/test_inspector_menu_mode.py`:

```python
"""Inspector accepts menu-mode projects without spurious 'missing tier' findings."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.inspector import inspect_project


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def test_figat7th_inspector_passes():
    report = inspect_project(FIGAT7TH)
    assert report.status in ("ready", "READY")  # match whatever sentinel the report uses
    # Ensure no blockers mentioning tier-related fields:
    tier_blockers = [
        b for b in report.blockers
        if "recommended_tier" in str(b) or "tier" in str(b).lower()
    ]
    assert tier_blockers == [], f"Tier-related blockers leaked into menu mode: {tier_blockers}"


def test_figat7th_inspector_validates_section_items():
    """If the Brief's sections reference an item code not in the worksheet,
    the inspector returns a clear blocker."""
    # This test is structural — we trust the locked FIGat7th project passes.
    # A future fault-injection test would mutate a copy and assert the blocker.
    report = inspect_project(FIGAT7TH)
    assert not any("item_codes" in str(b) for b in report.blockers)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_inspector_menu_mode.py -v`
Expected: fails — inspector flags missing tier fields on the new menu-mode Brief.

- [ ] **Step 3: Skip tier checks for menu mode in `inspector/brief.py`**

In `skill_assets/proposal_build/inspector/brief.py`, locate the function that checks Brief readiness. At the top, read frontmatter's `mode` field; if it's `menu`, skip the tier-specific findings and instead run a menu-mode check that verifies:

- `mode == "menu"` and all `MENU_REQUIRED_FIELDS` (from parser/brief.py) are present
- Each section has `key`, `label`, `name`, `is_lead`, `item_codes` (non-empty list)
- `prebuilt_cover_image` and `creative_vision_hero` resolve to files in `02 - Renderings/Base Scope/`

Implementation outline (add to the file, near the existing readiness checks):

```python
import frontmatter
from pathlib import Path

def _is_menu_mode(brief_path: Path) -> bool:
    if not brief_path.exists():
        return False
    fm = frontmatter.load(str(brief_path)).metadata
    return fm.get("mode", "tiered") == "menu"


def _check_menu_mode_brief(project_dir, brief_path, findings):
    """Findings list mutates in-place."""
    fm = frontmatter.load(str(brief_path)).metadata
    sections = fm.get("sections", [])
    if not sections:
        findings.append(Finding(level="BLOCKER", code="MENU_SECTIONS_MISSING",
                                message="Menu-mode Brief has no `sections` list"))
        return

    rendering_dir = project_dir / "02 - Renderings" / "Base Scope"
    for name in ("prebuilt_cover_image", "creative_vision_hero"):
        fname = fm.get(name, "")
        if not fname:
            findings.append(Finding(level="BLOCKER", code="MENU_HERO_MISSING",
                                    message=f"Menu-mode Brief missing field: {name}"))
            continue
        if not (rendering_dir / fname).exists():
            findings.append(Finding(level="BLOCKER", code="MENU_HERO_FILE_NOT_FOUND",
                                    message=f"{name} references missing file: {fname}"))
```

Then in the existing brief-check entry function, branch on `_is_menu_mode(brief_path)` and call `_check_menu_mode_brief` instead of the tier-specific check.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_inspector_menu_mode.py -v`
Expected: 2 passed.

Run: `pytest tests/ -q` to confirm existing inspector tests still pass.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/inspector/brief.py tests/test_inspector_menu_mode.py
git commit -m "feat(plan-9): inspector accepts menu-mode briefs without spurious tier findings"
```

---

## Task 10: Retire the Hand-Authored Fixture, Lock the Golden

**Files:**
- Modify: `tests/fixtures/figat7th.py` — convert to a thin shim that loads the project via `parse_project`, removing the hand-authored ctx dicts
- Create: `tests/test_figat7th_golden.py` — render the PDF and assert byte-size sanity + slide count + key totals

After tasks 1-9 the data files are authoritative; the fixture is no longer doing real work. Convert it to a shim and add a golden test.

- [ ] **Step 1: Convert the fixture to a shim**

Replace `tests/fixtures/figat7th.py` with:

```python
"""FIGat7th DTLA fixture — Plan 9 data-driven shim.

After Plan 9 the fixture no longer hand-authors slide ctxs; it loads the
project from disk via the same pipeline production uses. Kept for the
test_layouts.py snapshot suite (if any) and for ad-hoc rendering checks.
"""
from __future__ import annotations

from pathlib import Path

from proposal_build.parser import parse_project
from proposal_build.composer import compose


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def load_slides() -> list:
    """Returns [(layout_name, ctx), ...] for renderer.pdf.render_proposal_pdf."""
    model = parse_project(PROJECT_DIR)
    slides, _ = compose(model)
    return [(s.layout_name, s.context) for s in slides]


SLIDES = load_slides()
```

- [ ] **Step 2: Write the golden test**

Create `tests/test_figat7th_golden.py`:

```python
"""Golden test: FIGat7th deck produced by the Plan 9 pipeline must match
the locked structural shape from the May 2026 hand-authored deliverable."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures.figat7th import SLIDES
from proposal_build.renderer.pdf import render_proposal_pdf


def test_slide_count():
    assert len(SLIDES) == 12


def test_first_two_slides_are_prebuilt_creatives():
    assert SLIDES[0][0] == "image_fullbleed"
    assert SLIDES[1][0] == "image_fullbleed"


def test_last_slide_is_sign_off():
    assert SLIDES[-1][0] == "sign_off"


def test_renders_to_pdf(tmp_path):
    out = tmp_path / "figat7th-golden.pdf"
    render_proposal_pdf(SLIDES, out)
    assert out.exists()
    assert out.stat().st_size > 100_000


def test_pricing_totals_in_investment_p2():
    """Find slide 11 (investment p2) and assert the locked Program ROM Total."""
    inv_p2 = SLIDES[10]
    layout, ctx = inv_p2
    assert layout == "rom_investment"
    assert ctx["show_totals"] is True
    assert ctx["total_rental"] == "$227,150 – $234,650"
    assert ctx["total_purchase_ot"] == "$280,000 – $289,600"
    assert ctx["total_purchase_svc"] == "$117,000 – $120,900"
```

- [ ] **Step 3: Run the golden tests**

Run: `pytest tests/test_figat7th_golden.py -v`
Expected: 5 passed.

- [ ] **Step 4: Run the full suite as a regression sweep**

Run: `pytest -q 2>&1 | tail -5`
Expected: all tests pass. Compare the count to the baseline noted in Setup Step 2; difference should be exactly the new tests added by this plan.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/figat7th.py tests/test_figat7th_golden.py
git commit -m "feat(plan-9): retire hand-authored FIGat7th fixture; lock golden via Plan 9 pipeline"
```

---

## Task 11: Update skill.md and AE_SOP.md for Menu Mode

**Files:**
- Modify: `skill_assets/skill.md` — document the `mode: menu` Brief field and the menu-mode workflow
- Modify: `skill_assets/AE_SOP.md` — add the menu-mode AE walkthrough alongside the tiered one

- [ ] **Step 1: Add the menu-mode section to skill.md**

Find the section of `skill_assets/skill.md` that describes the Brief schema. Add a sibling subsection:

```markdown
### Menu Mode (creative-menu / ROM pricing)

When the project is a first-pass creative-menu proposal — multiple sections,
some with customer-choice alternates ("pick one"), some with always-included
items — the Brief uses `mode: menu` and a different field set than the
default tiered mode. Used for projects like FIGat7th DTLA where the AE wants
to present creative directions to the client before committing to a final scope.

Menu-mode required fields (replace the tiered fields):
- `mode: menu`
- `design_phrase`, `voice`, `prebuilt_cover_image`, `creative_vision_hero`
- `sections` — ordered list of `{key, label, name, is_lead, item_codes}`

Forbidden in menu mode: `recommended_tier`, `pricing_format`, `zones`.

Worksheet for menu mode uses the ROM (rough-order-of-magnitude) shape:
columns for Section, Item Name, Description, Alternate Group, Rental Low/High,
Purchase OT Low/High, Purchase Svc Low/High, Customer-Facing, Materials,
Notes, Rendering Reference. Rental is a single all-inclusive annual fee;
Purchase is one-time price plus a separate annual service fee.
```

- [ ] **Step 2: Add the menu-mode walkthrough to AE_SOP.md**

Find the existing tiered-mode walkthrough in `skill_assets/AE_SOP.md`. Add a sibling section after it:

```markdown
## Menu-Mode Project Walkthrough

For projects where you're presenting creative options to a client before
committing to a final scope (e.g. multi-rendering proposals, first-pass
concept decks), use menu mode:

1. In the Brief, set `mode: menu` and define `sections` instead of `zones`.
2. Build the ROM Worksheet using the menu schema (15 columns; see
   `Projects/Fig at 7th .../03 - Scope & Pricing/FIGat7th DTLA - Scope Worksheet.xlsx`
   for the canonical example).
3. Drop your pre-built cover and palette renderings into `02 - Renderings/Base Scope/`
   and reference them by filename in the Brief's `prebuilt_cover_image` and
   `prebuilt_palette_image` fields.
4. Each Section either renders as a single zone_solo slide (for one-item sections)
   or as multiple zone_2up_gallery slides (for multi-item sections, 2 cells per slide).
5. The customer sees a 3-column ROM pricing table at the end: Item / Rental
   (annual, all-in) / Purchase (one-time + annual service).
```

- [ ] **Step 3: Commit**

```bash
git add skill_assets/skill.md skill_assets/AE_SOP.md
git commit -m "docs(plan-9): document menu-mode Brief schema + AE workflow"
```

---

## Task 12: Final Regression and Merge

- [ ] **Step 1: Run the full test suite one more time**

Run: `pytest -q 2>&1 | tail -10`
Expected: all tests pass. Note the count and compare to the Setup baseline.

- [ ] **Step 2: Smoke-render Riverside and FIGat7th end-to-end**

```bash
source .venv/bin/activate
python -c "
from pathlib import Path
from tests.fixtures.figat7th import SLIDES as FIGAT7TH
from tests.fixtures.riverside import SLIDES as RIVERSIDE
from proposal_build.renderer.pdf import render_proposal_pdf
out_dir = Path('/tmp/plan9-smoke')
out_dir.mkdir(exist_ok=True)
render_proposal_pdf(FIGAT7TH, out_dir / 'figat7th.pdf')
render_proposal_pdf(RIVERSIDE, out_dir / 'riverside.pdf')
print('OK', out_dir)
"
```

Expected: both PDFs render successfully. Open both in Preview and confirm visually that nothing regressed.

- [ ] **Step 3: Open the merge PR**

```bash
git push -u origin plan-9-creative-menu
gh pr create --title "plan-9: creative-menu mode + ROM pricing" --body "$(cat <<'EOF'
## Summary
- Adds `mode: menu` Brief flag routing to a parallel parser/composer path
- ROM (rough-order-of-magnitude) worksheet schema with alternate groups
- Four reusable layouts already authored during FIGat7th first-pass
- FIGat7th project now built from data files end-to-end (no hand-authored fixture)

## Test plan
- [ ] All existing tiered fixtures (Riverside, Pier 39) still pass
- [ ] FIGat7th regenerates the same 12-slide deck shape via the pipeline
- [ ] Inspector accepts menu-mode briefs without spurious tier findings
- [ ] PDFs render cleanly in Preview for both fixtures

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 4: After PR review and merge, delete the local branch**

```bash
git checkout main && git pull && git branch -d plan-9-creative-menu
```
