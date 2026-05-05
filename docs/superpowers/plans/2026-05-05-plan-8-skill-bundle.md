# Plan 8 — Skill Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the existing Phase 2 generation pipeline as a deployable Claude Desktop skill bundle with deterministic readiness checks (`inspect`), project scaffolding (`scaffold`), the skill manifest (`skill.md`), and the AE-facing SOP (`AE_SOP.md`).

**Architecture:** New Python package `skill_assets/proposal_build/inspector/` runs four categories of readiness checks (folder/brief/worksheet/renderings) and aggregates Findings into a structured InspectionReport. The CLI gains `inspect` (JSON output) and `scaffold` subcommands. `skill.md` orchestrates Claude Desktop's behavior; Claude calls `inspect`, walks the AE through gaps conversationally, calls `generate`, and offers git commit/push.

**Tech Stack:** Python 3.11+, dataclasses, pytest, openpyxl (for worksheet checks), frontmatter (for Brief YAML). Extends existing Plan 3 codebase. No new external deps.

**Spec:** `docs/superpowers/specs/2026-05-05-plan-8-skill-bundle-design.md`

**Branch:** create `plan-8-skill-bundle` off `main` for the work; merge when complete.

---

## Setup

- [ ] **Setup Step 1: Create the feature branch**

```bash
git checkout main && git pull && git checkout -b plan-8-skill-bundle
```

- [ ] **Setup Step 2: Verify clean baseline**

```bash
source .venv/bin/activate && pytest -q 2>&1 | tail -3
```

Expected: `124 passed`. If not, stop and investigate.

---

## Task 1: Inspector Report Types

**Files:**
- Create: `skill_assets/proposal_build/inspector/__init__.py` (empty for now; populated in Task 6)
- Create: `skill_assets/proposal_build/inspector/report.py`
- Test: `tests/test_inspector_report.py`

- [ ] **Step 1: Create the empty package init**

```bash
mkdir -p skill_assets/proposal_build/inspector
```

Then write `skill_assets/proposal_build/inspector/__init__.py`:

```python
"""Inspector — deterministic project-readiness checks.

Public API: see Task 6 for inspect_project()."""
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_inspector_report.py`:

```python
"""Tests for the Finding + InspectionReport dataclasses."""
from pathlib import Path

from proposal_build.inspector.report import Finding, InspectionReport


def test_finding_has_required_fields():
    f = Finding(
        severity="blocker",
        category="brief",
        issue="missing-field",
        detail="Brief is missing required field 'client_company'.",
        fix="Reply with the client company name.",
        field="client_company",
        zone=None,
    )
    assert f.severity == "blocker"
    assert f.category == "brief"
    assert f.issue == "missing-field"
    assert f.field == "client_company"
    assert f.zone is None


def test_finding_optional_fields_default_none():
    f = Finding(
        severity="info",
        category="renderings",
        issue="files-in-inbox",
        detail="14 files unsorted.",
        fix=None,
    )
    assert f.field is None
    assert f.zone is None


def test_inspection_report_ready_when_no_blockers_no_errors():
    report = InspectionReport(
        project_path=Path("/tmp/x"),
        ready_to_generate=True,
        findings=(
            Finding("info", "renderings", "files-in-inbox", "0 files.", None),
        ),
        summary="Ready to generate.",
    )
    assert report.ready_to_generate is True
    assert len(report.findings) == 1


def test_inspection_report_not_ready_when_blocker_present():
    report = InspectionReport(
        project_path=Path("/tmp/x"),
        ready_to_generate=False,
        findings=(
            Finding("blocker", "brief", "missing-field",
                    "Missing client_company.", "Provide client_company.",
                    field="client_company"),
        ),
        summary="1 blocker.",
    )
    assert report.ready_to_generate is False
```

- [ ] **Step 3: Run test to verify failure**

```bash
pytest tests/test_inspector_report.py -v
```

Expected: ImportError or ModuleNotFoundError on `proposal_build.inspector.report`.

- [ ] **Step 4: Implement `report.py`**

Write `skill_assets/proposal_build/inspector/report.py`:

```python
"""Finding and InspectionReport dataclasses for the inspector."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


Severity = Literal["blocker", "warning", "info", "error"]
Category = Literal["folder", "brief", "worksheet", "renderings", "validator"]


@dataclass(frozen=True)
class Finding:
    severity: Severity
    category: Category
    issue: str
    detail: str
    fix: Optional[str] = None
    field: Optional[str] = None
    zone: Optional[str] = None


@dataclass(frozen=True)
class InspectionReport:
    project_path: Path
    ready_to_generate: bool
    findings: tuple[Finding, ...]
    summary: str
```

- [ ] **Step 5: Run test to verify pass**

```bash
pytest tests/test_inspector_report.py -v
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/inspector/__init__.py \
        skill_assets/proposal_build/inspector/report.py \
        tests/test_inspector_report.py && \
git commit -m "plan-8 t1: inspector Finding + InspectionReport types"
```

---

## Task 2: Folder Check

**Files:**
- Create: `skill_assets/proposal_build/inspector/folder.py`
- Test: `tests/test_inspector_folder.py`

The folder check confirms the project folder exists and has the expected subdirectory structure (matching `_template_project/`).

- [ ] **Step 1: Write the failing test**

Create `tests/test_inspector_folder.py`:

```python
"""Tests for the folder-structure inspector."""
from pathlib import Path

import pytest

from proposal_build.inspector.folder import check


REQUIRED_SUBDIRS = (
    "01 - Project Background",
    "02 - Renderings",
    "02 - Renderings/Base Scope",
    "02 - Renderings/Enhancements",
    "02 - Renderings/Greenery references",
    "02 - Renderings/_inbox",
    "03 - Scope & Pricing",
    "04 - Process & Notes",
)


def test_check_returns_no_findings_for_complete_folder(tmp_path):
    proj = tmp_path / "Test Project"
    proj.mkdir()
    for sub in REQUIRED_SUBDIRS:
        (proj / sub).mkdir(parents=True)
    findings = check(proj)
    assert findings == []


def test_check_reports_missing_project_folder(tmp_path):
    proj = tmp_path / "DoesNotExist"
    findings = check(proj)
    assert len(findings) == 1
    assert findings[0].severity == "blocker"
    assert findings[0].issue == "no-project-folder"


def test_check_reports_each_missing_subdir(tmp_path):
    proj = tmp_path / "Half Project"
    proj.mkdir()
    (proj / "01 - Project Background").mkdir()
    # Only one subdir present; expect findings for all the other 7
    findings = check(proj)
    assert len(findings) == len(REQUIRED_SUBDIRS) - 1
    for f in findings:
        assert f.severity == "blocker"
        assert f.issue == "missing-subdir"
        assert f.category == "folder"
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_inspector_folder.py -v
```

Expected: ImportError on `proposal_build.inspector.folder`.

- [ ] **Step 3: Implement `folder.py`**

Write `skill_assets/proposal_build/inspector/folder.py`:

```python
"""Folder-structure readiness checks."""
from __future__ import annotations

from pathlib import Path

from proposal_build.inspector.report import Finding


REQUIRED_SUBDIRS = (
    "01 - Project Background",
    "02 - Renderings",
    "02 - Renderings/Base Scope",
    "02 - Renderings/Enhancements",
    "02 - Renderings/Greenery references",
    "02 - Renderings/_inbox",
    "03 - Scope & Pricing",
    "04 - Process & Notes",
)


def check(project_path: Path) -> list[Finding]:
    """Return Findings about folder presence + subdirectory completeness."""
    if not project_path.exists() or not project_path.is_dir():
        return [Finding(
            severity="blocker",
            category="folder",
            issue="no-project-folder",
            detail=f"Project folder does not exist: {project_path}",
            fix=(f"Run `python -m proposal_build scaffold "
                 f"\"{project_path.name}\"` to create it from the template."),
        )]

    findings: list[Finding] = []
    for sub in REQUIRED_SUBDIRS:
        if not (project_path / sub).is_dir():
            findings.append(Finding(
                severity="blocker",
                category="folder",
                issue="missing-subdir",
                detail=f"Required subdirectory missing: {sub}",
                fix=f"Create the directory `{project_path / sub}`.",
            ))
    return findings
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_inspector_folder.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/inspector/folder.py \
        tests/test_inspector_folder.py && \
git commit -m "plan-8 t2: inspector folder-structure check"
```

---

## Task 3: Brief Check

**Files:**
- Create: `skill_assets/proposal_build/inspector/brief.py`
- Test: `tests/test_inspector_brief.py`

The brief check looks at `04 - Process & Notes/Project Brief.md`: file presence, YAML parseable, required frontmatter fields populated (no template-default sentinels), required prose sections non-empty, zones each have a `hero_image`.

- [ ] **Step 1: Identify the required Brief frontmatter fields**

Read `skill_assets/proposal_build/parser/__init__.py` and `skill_assets/proposal_build/parser/brief.py` to find the canonical required-fields list. The parser raises `ProjectLoadError` when these are missing — the inspector should detect them up-front.

The required frontmatter keys (cross-check against parser):

```python
REQUIRED_FIELDS = (
    "client_company", "client_short", "project_name", "project_short",
    "project_year", "proposal_type", "presenter_name", "presenter_title",
    "presenter_email", "presenter_phone", "proposal_date", "go_live",
    "voice", "recommended_tier", "design_phrase", "pricing_format",
    "cover_image",
)
```

If the parser uses a different exact set, update `REQUIRED_FIELDS` to match.

- [ ] **Step 2: Identify required prose sections**

From `skill_assets/proposal_build/parser/brief.py`, the BULLET_SECTIONS set + non-bullet prose required sections. For the inspector:

```python
REQUIRED_BULLET_SECTIONS = (
    "Customer Goals", "Customer Constraints", "Success Criteria",
    "Scope Includes",
)
REQUIRED_PROSE_SECTIONS = (
    "Creative Direction",
)
```

Confirm exact section names against `parser/brief.py` before coding.

- [ ] **Step 3: Write the failing test**

Create `tests/test_inspector_brief.py`:

```python
"""Tests for the Brief inspector."""
from pathlib import Path

import pytest

from proposal_build.inspector.brief import check


def _write_brief(path: Path, frontmatter: dict, body: str = "") -> None:
    import yaml
    text = "---\n" + yaml.safe_dump(frontmatter) + "---\n" + body
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_missing_brief_file_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    (proj / "04 - Process & Notes").mkdir(parents=True)
    findings = check(proj)
    blockers = [f for f in findings if f.severity == "blocker"
                                       and f.issue == "missing-brief"]
    assert len(blockers) == 1


def test_missing_required_frontmatter_field_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    _write_brief(brief, frontmatter={
        "project_name": "Test", "project_short": "T",
    })
    findings = check(proj)
    issues = [(f.issue, f.field) for f in findings
              if f.issue == "missing-field"]
    assert ("missing-field", "client_company") in issues


def test_zone_without_hero_image_reports_warning(tmp_path):
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    _write_brief(brief, frontmatter={
        "client_company": "X", "client_short": "X",
        "project_name": "Y", "project_short": "Y",
        "project_year": 2026, "proposal_type": "Holiday Proposal",
        "presenter_name": "P", "presenter_title": "T",
        "presenter_email": "p@x.com", "presenter_phone": "555-0100",
        "proposal_date": "2026-05-05", "go_live": "2026-11-14",
        "voice": "civic", "recommended_tier": "Enhanced",
        "design_phrase": "Test", "pricing_format": "tiered",
        "cover_image": "cover.png",
        "zones": [
            {"num": 1, "name": "Zone One", "subtitle": "x"},
        ],
    })
    findings = check(proj)
    no_hero = [f for f in findings if f.issue == "no-hero-image"]
    assert len(no_hero) == 1
    assert no_hero[0].zone == "Zone One"
    assert no_hero[0].severity == "warning"


def test_malformed_yaml_reports_error_finding(tmp_path):
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("---\nclient: [ broken yaml\n---\n")
    findings = check(proj)
    errors = [f for f in findings if f.severity == "error"
                                     and f.issue == "brief-yaml-parse-error"]
    assert len(errors) == 1
```

- [ ] **Step 4: Run test to verify failure**

```bash
pytest tests/test_inspector_brief.py -v
```

Expected: ImportError on `proposal_build.inspector.brief`.

- [ ] **Step 5: Implement `brief.py`**

Write `skill_assets/proposal_build/inspector/brief.py`:

```python
"""Brief-readiness checks."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.inspector.report import Finding


REQUIRED_FIELDS = (
    "client_company", "client_short", "project_name", "project_short",
    "project_year", "proposal_type", "presenter_name", "presenter_title",
    "presenter_email", "presenter_phone", "proposal_date", "go_live",
    "voice", "recommended_tier", "design_phrase", "pricing_format",
    "cover_image",
)
REQUIRED_BULLET_SECTIONS = (
    "Customer Goals", "Customer Constraints", "Success Criteria",
    "Scope Includes",
)
REQUIRED_PROSE_SECTIONS = (
    "Creative Direction",
)
BRIEF_RELPATH = "04 - Process & Notes/Project Brief.md"


def check(project_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    brief_path = project_path / BRIEF_RELPATH

    if not brief_path.is_file():
        findings.append(Finding(
            severity="blocker", category="brief", issue="missing-brief",
            detail=f"Brief not found at {BRIEF_RELPATH}",
            fix=("Scaffold the project (or copy the template Brief into "
                 "`04 - Process & Notes/Project Brief.md`)."),
        ))
        return findings

    # Try to parse
    try:
        post = frontmatter.load(str(brief_path))
    except Exception as exc:
        findings.append(Finding(
            severity="error", category="brief",
            issue="brief-yaml-parse-error",
            detail=f"Could not parse Brief frontmatter: {exc}",
            fix="Open the Brief and fix the YAML syntax error.",
        ))
        return findings

    fm = post.metadata or {}

    # Frontmatter field presence
    for field_name in REQUIRED_FIELDS:
        value = fm.get(field_name)
        if value is None or value == "" or value == "(unknown)":
            findings.append(Finding(
                severity="blocker", category="brief", issue="missing-field",
                detail=f"Brief is missing required frontmatter field: {field_name}",
                fix=f"Provide a value for `{field_name}:` in the Brief.",
                field=field_name,
            ))

    # Zones present + hero_image per zone
    zones = fm.get("zones") or []
    if not zones:
        findings.append(Finding(
            severity="blocker", category="brief", issue="no-zones-defined",
            detail="Brief defines no zones.",
            fix="Add at least one zone under `zones:` in the frontmatter.",
        ))
    else:
        for z in zones:
            if not isinstance(z, dict):
                continue
            zone_name = z.get("name") or f"zone {z.get('num', '?')}"
            has_hero = z.get("hero_image") or z.get("hero_images")
            if not has_hero:
                findings.append(Finding(
                    severity="warning", category="brief", issue="no-hero-image",
                    detail=f"Zone '{zone_name}' has no hero_image assigned.",
                    fix=("Pick a rendering from `02 - Renderings/Base Scope/`"
                         " and set `hero_image:` on this zone."),
                    zone=zone_name,
                ))

    # Prose sections (lightweight check: section header present + non-empty body)
    body = post.content or ""
    for section in REQUIRED_BULLET_SECTIONS + REQUIRED_PROSE_SECTIONS:
        marker = f"## {section}"
        if marker not in body:
            findings.append(Finding(
                severity="blocker", category="brief", issue="missing-section",
                detail=f"Brief is missing required section: {section}",
                fix=f"Add a `## {section}` section with content.",
                field=section,
            ))

    return findings
```

- [ ] **Step 6: Run test to verify pass**

```bash
pytest tests/test_inspector_brief.py -v
```

Expected: 4 passed. If any test fails, inspect mismatch and fix code or test (the spec is the source of truth).

- [ ] **Step 7: Commit**

```bash
git add skill_assets/proposal_build/inspector/brief.py \
        tests/test_inspector_brief.py && \
git commit -m "plan-8 t3: inspector Brief readiness check"
```

---

## Task 4: Worksheet Check

**Files:**
- Create: `skill_assets/proposal_build/inspector/worksheet.py`
- Test: `tests/test_inspector_worksheet.py`

The worksheet check looks at `03 - Scope & Pricing/<project> - Scope Worksheet.xlsx`. It detects missing file, file-locked, no tier columns set, blank customer-facing copy.

- [ ] **Step 1: Inspect the canonical worksheet structure**

Read `skill_assets/proposal_build/parser/worksheet.py` to learn the column layout. Note specifically:
- How tier columns are detected
- How customer-facing copy column is named
- File-locking behavior on macOS (lock file = `.~lock.<filename>#`)

- [ ] **Step 2: Write the failing test**

Create `tests/test_inspector_worksheet.py`:

```python
"""Tests for the Worksheet inspector."""
from pathlib import Path

import pytest
from openpyxl import Workbook

from proposal_build.inspector.worksheet import check


def _scope_dir(proj: Path) -> Path:
    d = proj / "03 - Scope & Pricing"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_worksheet(scope_dir: Path, name: str, header_row: list,
                     data_rows: list[list]) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.append(header_row)
    for row in data_rows:
        ws.append(row)
    out = scope_dir / f"{name} - Scope Worksheet.xlsx"
    wb.save(out)
    return out


def test_missing_worksheet_reports_blocker(tmp_path):
    proj = tmp_path / "Test Project"
    _scope_dir(proj)
    findings = check(proj)
    assert any(f.issue == "missing-worksheet" and f.severity == "blocker"
               for f in findings)


def test_locked_worksheet_reports_error(tmp_path):
    proj = tmp_path / "Test Project"
    sd = _scope_dir(proj)
    _write_worksheet(sd, "Test Project",
                     header_row=["Line #", "Customer-Facing Description",
                                 "Tiers"],
                     data_rows=[["B01", "X", "Essential, Enhanced"]])
    # macOS LibreOffice lock file
    (sd / ".~lock.Test Project - Scope Worksheet.xlsx#").write_text("locked")
    findings = check(proj)
    assert any(f.issue == "worksheet-locked" and f.severity == "error"
               for f in findings)


def test_blank_customer_facing_reports_blocker(tmp_path):
    proj = tmp_path / "Test Project"
    sd = _scope_dir(proj)
    _write_worksheet(sd, "Test Project",
                     header_row=["Line #", "Customer-Facing Description",
                                 "Tiers"],
                     data_rows=[
                         ["B01", "", "Essential, Enhanced"],
                         ["B02", "Some copy", "Essential"],
                     ])
    findings = check(proj)
    assert any(f.issue == "blank-customer-facing"
               for f in findings)


def test_no_tier_columns_reports_blocker(tmp_path):
    proj = tmp_path / "Test Project"
    sd = _scope_dir(proj)
    _write_worksheet(sd, "Test Project",
                     header_row=["Line #", "Customer-Facing Description",
                                 "Tiers"],
                     data_rows=[
                         ["B01", "X", ""],
                         ["B02", "Y", ""],
                     ])
    findings = check(proj)
    assert any(f.issue == "no-tiers-on-line"
               for f in findings)
```

- [ ] **Step 3: Run test to verify failure**

```bash
pytest tests/test_inspector_worksheet.py -v
```

Expected: ImportError.

- [ ] **Step 4: Implement `worksheet.py`**

Write `skill_assets/proposal_build/inspector/worksheet.py`:

```python
"""Worksheet-readiness checks."""
from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from proposal_build.inspector.report import Finding


SCOPE_DIR = "03 - Scope & Pricing"
WORKSHEET_SUFFIX = " - Scope Worksheet.xlsx"


def _find_worksheet(scope_dir: Path) -> Path | None:
    for p in scope_dir.glob(f"*{WORKSHEET_SUFFIX}"):
        if not p.name.startswith(".~lock."):
            return p
    return None


def _is_locked(worksheet_path: Path) -> bool:
    return (worksheet_path.parent /
            f".~lock.{worksheet_path.name}#").exists()


def check(project_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    scope_dir = project_path / SCOPE_DIR
    if not scope_dir.is_dir():
        # folder.py already reports this; don't duplicate.
        return []

    ws_path = _find_worksheet(scope_dir)
    if ws_path is None:
        findings.append(Finding(
            severity="blocker", category="worksheet",
            issue="missing-worksheet",
            detail=f"No `*{WORKSHEET_SUFFIX}` file found in {SCOPE_DIR}/",
            fix=("Scaffold the project (or copy the template Worksheet "
                 f"into `{SCOPE_DIR}/<Project Name>{WORKSHEET_SUFFIX}`)."),
        ))
        return findings

    if _is_locked(ws_path):
        findings.append(Finding(
            severity="error", category="worksheet",
            issue="worksheet-locked",
            detail=f"Worksheet appears to be open in Excel: {ws_path.name}",
            fix="Close the file in Excel and re-run inspect.",
        ))
        return findings

    try:
        wb = load_workbook(ws_path, data_only=True, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as exc:
        findings.append(Finding(
            severity="error", category="worksheet",
            issue="worksheet-read-error",
            detail=f"Could not read worksheet: {exc}",
            fix="Open the worksheet in Excel and check for corruption.",
        ))
        return findings

    if not rows:
        findings.append(Finding(
            severity="blocker", category="worksheet",
            issue="empty-worksheet",
            detail="Worksheet has no rows.",
            fix="Add header + line-item rows to the worksheet.",
        ))
        return findings

    header = [str(c) if c is not None else "" for c in rows[0]]
    try:
        cf_col = header.index("Customer-Facing Description")
    except ValueError:
        cf_col = None
    try:
        tiers_col = header.index("Tiers")
    except ValueError:
        tiers_col = None

    if cf_col is None:
        findings.append(Finding(
            severity="blocker", category="worksheet",
            issue="missing-customer-facing-column",
            detail="Worksheet has no `Customer-Facing Description` column.",
            fix="Restore the column from the template.",
        ))
    if tiers_col is None:
        findings.append(Finding(
            severity="blocker", category="worksheet",
            issue="missing-tiers-column",
            detail="Worksheet has no `Tiers` column.",
            fix="Restore the column from the template.",
        ))

    if cf_col is None or tiers_col is None:
        return findings

    for i, row in enumerate(rows[1:], start=2):
        line_num = str(row[0]) if row[0] is not None else f"row {i}"
        cf_val = row[cf_col] if cf_col < len(row) else None
        tiers_val = row[tiers_col] if tiers_col < len(row) else None

        if cf_val is None or str(cf_val).strip() == "":
            findings.append(Finding(
                severity="blocker", category="worksheet",
                issue="blank-customer-facing",
                detail=f"Line {line_num} has no Customer-Facing Description.",
                fix=f"Fill in the customer-facing copy for line {line_num}.",
            ))
        if tiers_val is None or str(tiers_val).strip() == "":
            findings.append(Finding(
                severity="blocker", category="worksheet",
                issue="no-tiers-on-line",
                detail=f"Line {line_num} has no Tiers assigned.",
                fix=("Add a comma-separated tier list for line {line_num} "
                     "(Essential, Enhanced, Signature)."),
            ))

    return findings
```

- [ ] **Step 5: Run test to verify pass**

```bash
pytest tests/test_inspector_worksheet.py -v
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/inspector/worksheet.py \
        tests/test_inspector_worksheet.py && \
git commit -m "plan-8 t4: inspector Worksheet readiness check"
```

---

## Task 5: Renderings Check

**Files:**
- Create: `skill_assets/proposal_build/inspector/renderings.py`
- Test: `tests/test_inspector_renderings.py`

The renderings check inspects the `02 - Renderings/` folder: any files at all, files unsorted in `_inbox/`, hero_image references in the Brief that don't resolve to actual files.

- [ ] **Step 1: Write the failing test**

Create `tests/test_inspector_renderings.py`:

```python
"""Tests for the Renderings inspector."""
from pathlib import Path

import pytest

from proposal_build.inspector.renderings import check


def _setup_renderings(proj: Path) -> Path:
    rd = proj / "02 - Renderings"
    for sub in ("Base Scope", "Enhancements", "Greenery references", "_inbox"):
        (rd / sub).mkdir(parents=True)
    return rd


def _write_brief(proj: Path, fm: dict) -> None:
    import yaml
    bp = proj / "04 - Process & Notes" / "Project Brief.md"
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text("---\n" + yaml.safe_dump(fm) + "---\n")


def test_no_renderings_reports_warning(tmp_path):
    proj = tmp_path / "P"
    _setup_renderings(proj)
    findings = check(proj)
    assert any(f.issue == "no-renderings-present" and f.severity == "warning"
               for f in findings)


def test_files_in_inbox_reports_info(tmp_path):
    proj = tmp_path / "P"
    rd = _setup_renderings(proj)
    (rd / "_inbox" / "unsorted.png").write_bytes(b"x")
    findings = check(proj)
    assert any(f.issue == "files-in-inbox" and f.severity == "warning"
               for f in findings)


def test_hero_image_unresolved_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    _setup_renderings(proj)
    _write_brief(proj, {
        "zones": [{"num": 1, "name": "Z1", "hero_image": "missing.png"}]
    })
    findings = check(proj)
    assert any(f.issue == "hero-image-unresolved" and f.severity == "blocker"
               for f in findings)


def test_hero_image_resolved_no_finding(tmp_path):
    proj = tmp_path / "P"
    rd = _setup_renderings(proj)
    (rd / "Base Scope" / "wreath.png").write_bytes(b"x")
    _write_brief(proj, {
        "zones": [{"num": 1, "name": "Z1", "hero_image": "wreath.png"}]
    })
    findings = check(proj)
    assert not any(f.issue == "hero-image-unresolved" for f in findings)
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_inspector_renderings.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `renderings.py`**

Write `skill_assets/proposal_build/inspector/renderings.py`:

```python
"""Renderings-folder readiness checks."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.inspector.report import Finding


RENDERINGS_DIR = "02 - Renderings"
SEARCH_SUBDIRS = ("Base Scope", "Enhancements", "Greenery references")
INBOX_SUBDIR = "_inbox"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return [p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS]


def _all_renderings(rd: Path) -> list[Path]:
    out: list[Path] = []
    for sub in SEARCH_SUBDIRS:
        out.extend(_list_images(rd / sub))
    return out


def check(project_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    rd = project_path / RENDERINGS_DIR
    if not rd.is_dir():
        return []  # folder.py already reports this

    all_files = _all_renderings(rd)
    if not all_files:
        findings.append(Finding(
            severity="warning", category="renderings",
            issue="no-renderings-present",
            detail=("No renderings found in `Base Scope/`, `Enhancements/`,"
                    " or `Greenery references/`."),
            fix=("Drop renderings into the appropriate subfolder under "
                 f"`{RENDERINGS_DIR}/`."),
        ))

    inbox_files = _list_images(rd / INBOX_SUBDIR)
    if inbox_files:
        findings.append(Finding(
            severity="warning", category="renderings",
            issue="files-in-inbox",
            detail=f"{len(inbox_files)} file(s) sitting in `_inbox/` "
                   "unsorted.",
            fix=("Move each into the appropriate subfolder "
                 "(`Base Scope/`, `Enhancements/`, or "
                 "`Greenery references/`)."),
        ))

    # Resolve hero_image references from the Brief
    brief_path = project_path / "04 - Process & Notes" / "Project Brief.md"
    if brief_path.is_file():
        try:
            post = frontmatter.load(str(brief_path))
            zones = post.metadata.get("zones") or []
        except Exception:
            zones = []  # brief.py reports the parse error
        available = {p.name for p in all_files}
        for z in zones:
            if not isinstance(z, dict):
                continue
            zone_name = z.get("name") or f"zone {z.get('num', '?')}"
            refs: list[str] = []
            if z.get("hero_image"):
                refs.append(z["hero_image"])
            for hi in z.get("hero_images") or []:
                refs.append(hi)
            for ref in refs:
                if ref not in available:
                    findings.append(Finding(
                        severity="blocker", category="renderings",
                        issue="hero-image-unresolved",
                        detail=(f"Zone '{zone_name}' references "
                                f"`{ref}` but no such file exists in "
                                "the renderings subfolders."),
                        fix=(f"Add the file to "
                             f"`{RENDERINGS_DIR}/<subfolder>/` or "
                             "update the Brief reference."),
                        zone=zone_name,
                    ))

    return findings
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_inspector_renderings.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/inspector/renderings.py \
        tests/test_inspector_renderings.py && \
git commit -m "plan-8 t5: inspector Renderings readiness check"
```

---

## Task 6: Aggregator — `inspect_project()`

**Files:**
- Modify: `skill_assets/proposal_build/inspector/__init__.py`
- Test: `tests/test_inspector_aggregate.py`

The aggregator orchestrates: run folder check → if folder OK, run brief/worksheet/renderings checks → if everything parses cleanly, run W1-W8 validators (`parser.validate.run_validation`) and convert each warning/blocker into a Finding. Determines `ready_to_generate`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_inspector_aggregate.py`:

```python
"""Integration test for inspect_project()."""
from pathlib import Path

import pytest

from proposal_build.inspector import inspect_project


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "Projects" / "_template_project"
RIVERSIDE = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"


def test_template_project_has_many_blockers():
    """The blank template should have plenty of blockers — proves the
    inspector finds them rather than silently passing."""
    if not TEMPLATE.is_dir():
        pytest.skip("Template project not present.")
    report = inspect_project(TEMPLATE)
    assert report.ready_to_generate is False
    blockers = [f for f in report.findings if f.severity == "blocker"]
    assert len(blockers) >= 5


def test_riverside_is_ready():
    """Riverside is the canonical end-to-end-ready fixture; it should
    inspect cleanly with no blockers and no errors."""
    if not RIVERSIDE.is_dir():
        pytest.skip("Riverside project not present.")
    report = inspect_project(RIVERSIDE)
    blockers = [f for f in report.findings if f.severity == "blocker"]
    errors = [f for f in report.findings if f.severity == "error"]
    assert blockers == [], f"Unexpected blockers: {blockers}"
    assert errors == [], f"Unexpected errors: {errors}"
    assert report.ready_to_generate is True


def test_summary_string_describes_state(tmp_path):
    """Summary should be a one-liner that says 'Ready' or '<N> blocker(s)…'."""
    proj = tmp_path / "Empty"
    report = inspect_project(proj)
    assert isinstance(report.summary, str)
    assert len(report.summary) < 200
    assert report.summary != ""
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_inspector_aggregate.py -v
```

Expected: ImportError on `inspect_project`.

- [ ] **Step 3: Implement `inspect_project()`**

Replace `skill_assets/proposal_build/inspector/__init__.py` with:

```python
"""Inspector — deterministic project-readiness checks.

Public API: inspect_project(project_path) -> InspectionReport
"""
from __future__ import annotations

from pathlib import Path

from proposal_build.inspector import folder, brief, worksheet, renderings
from proposal_build.inspector.report import Finding, InspectionReport


def inspect_project(project_path: Path) -> InspectionReport:
    """Run all readiness checks and aggregate Findings."""
    project_path = Path(project_path)
    findings: list[Finding] = []

    # Order matters: if folder is missing, downstream checks would fail
    # spuriously, so we short-circuit. Brief/worksheet/renderings each
    # also short-circuit internally if their root subdir is missing.
    folder_findings = _safe_check(folder.check, project_path, "folder")
    findings.extend(folder_findings)

    has_blocking_folder_issue = any(
        f.severity == "blocker" and f.issue == "no-project-folder"
        for f in folder_findings
    )
    if not has_blocking_folder_issue:
        findings.extend(_safe_check(brief.check, project_path, "brief"))
        findings.extend(_safe_check(worksheet.check, project_path, "worksheet"))
        findings.extend(_safe_check(renderings.check, project_path, "renderings"))
        findings.extend(_run_validator_pass(project_path))

    blockers = [f for f in findings if f.severity == "blocker"]
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    ready = not blockers and not errors

    if ready:
        summary = f"Ready to generate ({len(warnings)} warning(s))." \
                  if warnings else "Ready to generate."
    else:
        bits = []
        if blockers:
            bits.append(f"{len(blockers)} blocker(s)")
        if errors:
            bits.append(f"{len(errors)} error(s)")
        if warnings:
            bits.append(f"{len(warnings)} warning(s)")
        summary = ", ".join(bits) + "."

    return InspectionReport(
        project_path=project_path,
        ready_to_generate=ready,
        findings=tuple(findings),
        summary=summary,
    )


def _safe_check(fn, project_path: Path, category: str) -> list[Finding]:
    """Wrap a category check so an unexpected exception becomes a Finding."""
    try:
        return fn(project_path)
    except Exception as exc:
        return [Finding(
            severity="error", category=category, issue="check-crashed",
            detail=f"Inspector module {category} crashed: {exc!r}",
            fix="Send this output to Daniel; the inspector has a bug.",
        )]


def _run_validator_pass(project_path: Path) -> list[Finding]:
    """Try to parse the project and run W1-W8 validators. If parsing
    fails, the brief/worksheet inspectors already reported the cause —
    we just skip the validator pass silently."""
    from proposal_build.parser import build_project_model, ProjectLoadError
    from proposal_build.parser.validate import run_validation

    try:
        model, artifacts = build_project_model(project_path)
    except ProjectLoadError:
        return []  # already reported by upstream inspectors
    except Exception as exc:
        return [Finding(
            severity="error", category="validator",
            issue="parser-crashed",
            detail=f"Parser crashed unexpectedly: {exc!r}",
            fix="Send this output to Daniel; the parser has a bug.",
        )]

    result = run_validation(
        model,
        eligible_renderings=artifacts["eligible_renderings"],
        referenced_filenames=artifacts["referenced_filenames"],
        per_line_sums=artifacts["per_line_sums"],
        scenarios=artifacts["scenarios"],
    )

    findings: list[Finding] = []
    for code, msg in result.blockers:
        findings.append(Finding(
            severity="blocker", category="validator", issue=code,
            detail=msg, fix=None,
        ))
    for code, msg in result.warnings:
        findings.append(Finding(
            severity="warning", category="validator", issue=code,
            detail=msg, fix=None,
        ))
    return findings
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_inspector_aggregate.py -v
```

Expected: 3 passed. If `test_riverside_is_ready` fails, the inspector found a real issue — debug by running `python -c "from proposal_build.inspector import inspect_project; from pathlib import Path; r = inspect_project(Path('Projects/Downtown Riverside Metro Link')); [print(f) for f in r.findings]"` and either fix the inspector or add the Brief field that's actually missing.

- [ ] **Step 5: Run the full suite**

```bash
pytest -q 2>&1 | tail -3
```

Expected: all previously-passing tests still pass + new tests pass.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/inspector/__init__.py \
        tests/test_inspector_aggregate.py && \
git commit -m "plan-8 t6: aggregate inspect_project() with W1-W8 wrap"
```

---

## Task 7: Scaffold Module

**Files:**
- Create: `skill_assets/proposal_build/scaffold.py`
- Test: `tests/test_scaffold.py`

`scaffold_project(target_path, source_path=...)` recursively copies `_template_project/` into a new project folder.

- [ ] **Step 1: Write the failing test**

Create `tests/test_scaffold.py`:

```python
"""Tests for scaffold_project()."""
import shutil
from pathlib import Path

import pytest

from proposal_build.scaffold import scaffold_project


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "Projects" / "_template_project"


@pytest.fixture
def template_clone(tmp_path):
    """Copy the real template into tmp so tests don't depend on absolute path."""
    if not TEMPLATE.is_dir():
        pytest.skip("Template project not present.")
    dst = tmp_path / "_template_project"
    shutil.copytree(TEMPLATE, dst)
    return dst


def test_scaffold_creates_full_tree(tmp_path, template_clone):
    target = tmp_path / "Projects" / "New Test Project"
    scaffold_project(target, source=template_clone)
    assert (target / "01 - Project Background").is_dir()
    assert (target / "02 - Renderings" / "Base Scope").is_dir()
    assert (target / "02 - Renderings" / "_inbox").is_dir()
    assert (target / "03 - Scope & Pricing").is_dir()
    assert (target / "04 - Process & Notes").is_dir()


def test_scaffold_refuses_overwrite(tmp_path, template_clone):
    target = tmp_path / "Projects" / "Existing"
    target.mkdir(parents=True)
    with pytest.raises(FileExistsError):
        scaffold_project(target, source=template_clone)
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_scaffold.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `scaffold.py`**

Write `skill_assets/proposal_build/scaffold.py`:

```python
"""Scaffold a new project folder from `_template_project/`."""
from __future__ import annotations

import shutil
from pathlib import Path


_DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / "Projects" / "_template_project"


def scaffold_project(target: Path, source: Path | None = None) -> Path:
    """Copy the template project tree into target. Refuses overwrite.

    Returns the resolved target path on success.
    """
    target = Path(target)
    src = Path(source) if source is not None else _DEFAULT_SOURCE
    if not src.is_dir():
        raise FileNotFoundError(f"Template source missing: {src}")
    if target.exists():
        raise FileExistsError(
            f"Target already exists: {target}. "
            "Refusing to overwrite — pick a different name or delete the "
            "existing folder first."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target)
    return target.resolve()
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_scaffold.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/scaffold.py \
        tests/test_scaffold.py && \
git commit -m "plan-8 t7: scaffold_project() module"
```

---

## Task 8: CLI `inspect` Subcommand

**Files:**
- Modify: `skill_assets/proposal_build/cli.py`
- Test: `tests/test_cli_inspect.py`

`python -m proposal_build inspect <project_dir> [--format=json|human]` runs `inspect_project()` and prints the report. Exit codes: 0 = ready, 1 = blockers, 2 = errors.

- [ ] **Step 1: Write the failing test**

Create `tests/test_cli_inspect.py`:

```python
"""CLI tests for `python -m proposal_build inspect`."""
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "Projects" / "_template_project"
RIVERSIDE = REPO_ROOT / "Projects" / "Downtown Riverside Metro Link"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "proposal_build"] + args,
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def test_inspect_ready_returns_exit_0_and_valid_json():
    if not RIVERSIDE.is_dir():
        pytest.skip("Riverside project not present.")
    r = _run(["inspect", str(RIVERSIDE)])
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["ready_to_generate"] is True


def test_inspect_blockers_returns_exit_1():
    if not TEMPLATE.is_dir():
        pytest.skip("Template not present.")
    r = _run(["inspect", str(TEMPLATE)])
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    assert payload["ready_to_generate"] is False
    assert len(payload["findings"]) >= 5


def test_inspect_human_format_is_not_json():
    if not RIVERSIDE.is_dir():
        pytest.skip("Riverside project not present.")
    r = _run(["inspect", str(RIVERSIDE), "--format=human"])
    assert r.returncode == 0
    with pytest.raises(json.JSONDecodeError):
        json.loads(r.stdout)
    assert "Ready" in r.stdout or "ready" in r.stdout
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_cli_inspect.py -v
```

Expected: failure (subcommand not recognized → returncode != 0/1).

- [ ] **Step 3: Implement the subcommand**

Modify `skill_assets/proposal_build/cli.py`. Add imports at the top:

```python
import json
from dataclasses import asdict
from proposal_build.inspector import inspect_project
```

In `main()`, after the `gen` subparser block, add the `inspect` subparser:

```python
    insp = sub.add_parser("inspect", help="Report project readiness as JSON.")
    insp.add_argument("project_dir", help="Path to the project folder")
    insp.add_argument("--format", choices=("json", "human"), default="json",
                      help="Output format (default: json)")
```

Replace the `if args.command == "generate":` block with:

```python
    if args.command == "generate":
        return _do_generate(Path(args.project_dir), args.use_latest_layouts, args.compress)
    if args.command == "inspect":
        return _do_inspect(Path(args.project_dir), args.format)
    return 1
```

Add the handler:

```python
def _do_inspect(project_dir: Path, fmt: str) -> int:
    report = inspect_project(project_dir)
    if fmt == "json":
        # Convert dataclass to dict, then dumps; Path → str.
        payload = {
            "project_path": str(report.project_path),
            "ready_to_generate": report.ready_to_generate,
            "summary": report.summary,
            "findings": [asdict(f) for f in report.findings],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(report.summary)
        for f in report.findings:
            print(f"  [{f.severity}] {f.category}/{f.issue}: {f.detail}")
            if f.fix:
                print(f"    fix: {f.fix}")
    if any(f.severity == "error" for f in report.findings):
        return 2
    if not report.ready_to_generate:
        return 1
    return 0
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_cli_inspect.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Run the full suite**

```bash
pytest -q 2>&1 | tail -3
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/cli.py \
        tests/test_cli_inspect.py && \
git commit -m "plan-8 t8: CLI inspect subcommand"
```

---

## Task 9: CLI `scaffold` Subcommand

**Files:**
- Modify: `skill_assets/proposal_build/cli.py`
- Test: extend `tests/test_scaffold.py`

`python -m proposal_build scaffold "<project name>"` calls `scaffold_project(Projects/<name>)`.

- [ ] **Step 1: Add a CLI test to `tests/test_scaffold.py`**

Append to `tests/test_scaffold.py`:

```python
import subprocess
import sys


def test_cli_scaffold_creates_folder(tmp_path, monkeypatch, template_clone):
    """The CLI subcommand should create the project under Projects/."""
    # Layout a tmp repo: Projects/_template_project/ + Projects/ for output
    fake_repo = tmp_path / "fake_repo"
    (fake_repo / "Projects").mkdir(parents=True)
    shutil.copytree(template_clone, fake_repo / "Projects" / "_template_project")
    r = subprocess.run(
        [sys.executable, "-m", "proposal_build", "scaffold", "CLI Test Project"],
        capture_output=True, text=True, cwd=fake_repo,
    )
    assert r.returncode == 0, r.stderr
    assert (fake_repo / "Projects" / "CLI Test Project" / "04 - Process & Notes").is_dir()


def test_cli_scaffold_refuse_overwrite_returns_exit_1(tmp_path, template_clone):
    fake_repo = tmp_path / "fake_repo"
    (fake_repo / "Projects" / "Existing").mkdir(parents=True)
    shutil.copytree(template_clone, fake_repo / "Projects" / "_template_project")
    r = subprocess.run(
        [sys.executable, "-m", "proposal_build", "scaffold", "Existing"],
        capture_output=True, text=True, cwd=fake_repo,
    )
    assert r.returncode == 1
    assert "exists" in (r.stderr + r.stdout).lower()
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_scaffold.py -v
```

Expected: the two new tests fail (subcommand not registered).

- [ ] **Step 3: Add the subcommand to `cli.py`**

In `main()` after the `inspect` subparser:

```python
    sca = sub.add_parser("scaffold", help="Create a new project folder from the template.")
    sca.add_argument("project_name", help="Name of the new project (folder under Projects/)")
```

Add to the dispatch chain in `main()`:

```python
    if args.command == "scaffold":
        return _do_scaffold(args.project_name)
```

Add the handler (use `Path.cwd()` so the CLI works from the repo root):

```python
def _do_scaffold(project_name: str) -> int:
    from proposal_build.scaffold import scaffold_project
    target = Path.cwd() / "Projects" / project_name
    try:
        out = scaffold_project(target)
    except FileExistsError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    print(f"✅ Created {out}")
    return 0
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_scaffold.py -v
```

Expected: 4 passed (2 module + 2 CLI).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/cli.py tests/test_scaffold.py && \
git commit -m "plan-8 t9: CLI scaffold subcommand"
```

---

## Task 10: `skill.md` Manifest

**Files:**
- Create: `skill_assets/skill.md`

Skill manifest with frontmatter + body that orchestrates the proposal flow.

- [ ] **Step 1: Write `skill.md`**

Create `skill_assets/skill.md`:

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add skill_assets/skill.md && \
git commit -m "plan-8 t10: skill.md manifest"
```

---

## Task 11: `AE_SOP.md`

**Files:**
- Create: `skill_assets/AE_SOP.md`

Human-facing SOP for the sales-team AEs.

- [ ] **Step 1: Write `AE_SOP.md`**

Create `skill_assets/AE_SOP.md`:

````markdown
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

Use `Enhancements/` and `Greenery references/` for those tiers.

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

The Brief is the YAML at the top of `Project Brief.md`. Required
fields:

| Field | What it means |
|---|---|
| `client_company` | Full legal client name (e.g. "Riverside County Transportation Commission (RCTC)"). |
| `client_short` | Short version for headers (e.g. "RCTC"). |
| `project_name` | Full project name (e.g. "Downtown Riverside Metro Link"). |
| `project_short` | Short version (e.g. "Riverside MetroLink"). |
| `project_year` | The decoration year (e.g. 2026). |
| `proposal_type` | Usually "Holiday Proposal". |
| `presenter_name` / `presenter_title` / `presenter_email` / `presenter_phone` | The AE on the project (probably you). |
| `proposal_date` | Today, in YYYY-MM-DD. |
| `go_live` | Decoration go-live date (YYYY-MM-DD). |
| `voice` | One of `civic`, `destination-retail`, `hospitality`. |
| `recommended_tier` | Your tier recommendation (`Essential`, `Enhanced`, or `Signature`). |
| `design_phrase` | Short evocative phrase for the Creative Vision slide (e.g. "Holiday Express"). |
| `pricing_format` | `tiered` for 3-tier proposals, `single` for one-tier. |
| `cover_image` | Filename of the cover hero (must exist in `02 - Renderings/Base Scope/`). |

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
````

- [ ] **Step 2: Commit**

```bash
git add skill_assets/AE_SOP.md && \
git commit -m "plan-8 t11: AE_SOP.md"
```

---

## Task 12: Skill Bundle Smoke Test

**Files:**
- Create: `tests/test_skill_bundle.py`

Verifies the skill bundle has the required structure: `skill.md` exists with valid frontmatter, `AE_SOP.md` exists with expected H2 sections.

- [ ] **Step 1: Write the test**

Create `tests/test_skill_bundle.py`:

```python
"""Smoke test: skill bundle has the structure Claude Desktop and AEs expect."""
from pathlib import Path

import pytest
import frontmatter


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_BUNDLE = REPO_ROOT / "skill_assets"


def test_skill_md_exists_and_parses():
    p = SKILL_BUNDLE / "skill.md"
    assert p.is_file(), "skill_assets/skill.md missing"
    post = frontmatter.load(str(p))
    assert post.metadata.get("name"), "skill.md missing `name`"
    desc = post.metadata.get("description", "")
    assert isinstance(desc, str) and len(desc) > 30, \
        "skill.md `description` must be a substantive string"
    # Activation phrases the skill claims to handle
    for phrase in ("build a proposal", "generate"):
        assert phrase.lower() in desc.lower(), \
            f"skill.md description should mention activation phrase: {phrase}"


def test_skill_md_body_has_required_steps():
    body = (SKILL_BUNDLE / "skill.md").read_text()
    for header in ("## Step 1", "## Step 2", "## Step 3", "## Step 4",
                   "## Step 5", "## Step 6", "## Beta safety rail"):
        assert header in body, f"skill.md body missing section: {header}"


def test_ae_sop_exists_and_has_required_sections():
    p = SKILL_BUNDLE / "AE_SOP.md"
    assert p.is_file(), "skill_assets/AE_SOP.md missing"
    body = p.read_text()
    for section in ("## Setup (one-time)", "## Daily workflow", "## Reference"):
        assert section in body, f"AE_SOP.md missing section: {section}"
    assert len(body) > 1000, "AE_SOP.md suspiciously short"
```

- [ ] **Step 2: Run test to verify pass (skill.md and SOP already written)**

```bash
pytest tests/test_skill_bundle.py -v
```

Expected: 3 passed. If a section header doesn't match, fix the test or
the doc — they should be consistent.

- [ ] **Step 3: Run the full suite**

```bash
pytest -q 2>&1 | tail -3
```

Expected: all tests pass (124 prior + new tests for Plan 8).

- [ ] **Step 4: Commit**

```bash
git add tests/test_skill_bundle.py && \
git commit -m "plan-8 t12: skill bundle smoke test"
```

---

## Task 13: Manual smoke test + handoff

This task isn't automated — it's the human verification step Daniel runs before merging Plan 8.

- [ ] **Step 1: Regen-only flow on Riverside**

In Claude Desktop, with the skill installed:

> *"Build the Riverside MetroLink proposal."*

Expected behavior:
1. Skill resolves project from `Projects/Downtown Riverside Metro Link`.
2. `inspect` returns ready-to-generate (only info-severity findings).
3. Skill confirms ready, runs `generate --use-latest-layouts --compress`.
4. Surfaces the 4 PDF paths.
5. Offers commit + push.

Open the regenerated `Riverside MetroLink - 2026 Holiday Proposal.pdf`
and the Essential / Enhanced itemized pricing PDFs — confirm they
render correctly (matches the v3-polish output).

- [ ] **Step 2: Full new-project flow on a throwaway project**

> *"Build a proposal for Plan 8 Smoke Test."*

Expected behavior:
1. Skill says no folder exists; offers to scaffold.
2. Scaffolds from `_template_project/`.
3. Walks through Brief field-by-field. Answer each question with
   minimal-but-valid values.
4. Tells you renderings + Worksheet are manual; reply when ready.
5. Drop 2-3 sample renderings into `02 - Renderings/Base Scope/`.
6. Fill the Worksheet with one base-scope line item per tier.
7. Reply ready; skill walks through hero_image assignment.
8. Skill generates; surfaces PDF paths.
9. Skill offers commit + push (decline for the throwaway).

- [ ] **Step 3: Capture friction**

Note any moments where:
- The skill asked something unclear.
- The skill missed a state Claude Desktop expected.
- An error surfaced that the SOP didn't cover.

Update `skill_assets/AE_SOP.md` with any concrete fixes / clarifications.

- [ ] **Step 4: Clean up the throwaway project**

```bash
rm -rf "Projects/Plan 8 Smoke Test"
```

- [ ] **Step 5: Merge to main**

```bash
git checkout main && \
git merge --no-ff plan-8-skill-bundle -m "Merge plan-8-skill-bundle: deployable skill manifest + AE SOP + inspector + scaffold" && \
git push origin main
```

- [ ] **Step 6: Hand off to Jonathan and Jovany**

Send each of them the AE_SOP.md link from the repo, walk them through
Setup section once, and have them run the smoke test on Riverside.
Capture any new friction in the SOP.

---

## Final verification

- [ ] **All tests pass**

```bash
source .venv/bin/activate && pytest 2>&1 | tail -3
```

Expected: 124 (prior) + ~25 (new across Tasks 1-9 + 12) = ~149 passing.

- [ ] **Riverside still ships clean**

```bash
python -m proposal_build generate "Projects/Downtown Riverside Metro Link" --use-latest-layouts --compress
```

Expected: ✅ Generation complete with 4 output PDFs.

- [ ] **Inspect agrees**

```bash
python -m proposal_build inspect "Projects/Downtown Riverside Metro Link"
```

Expected: exit 0, JSON `ready_to_generate: true`.

- [ ] **Scaffold works**

```bash
python -m proposal_build scaffold "Plan 8 Verify Test" && \
ls "Projects/Plan 8 Verify Test/" && \
rm -rf "Projects/Plan 8 Verify Test"
```

Expected: folder created with all required subdirs, then cleaned up.
