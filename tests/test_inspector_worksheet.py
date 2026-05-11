"""Tests for the Worksheet inspector."""
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from proposal_build.inspector.worksheet import check


def _scope_dir(proj: Path) -> Path:
    d = proj / "03 - Scope & Pricing"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_brief(proj: Path, project_name: str) -> Path:
    notes_dir = proj / "04 - Process & Notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    brief_path = notes_dir / "Project Brief.md"
    brief_path.write_text(
        f"---\nproject_name: \"{project_name}\"\n---\n\n## Creative Direction\nplaceholder\n"
    )
    return brief_path


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
                     data_rows=[["1", "X", "Essential, Enhanced"]])
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
                         ["1", "", "Essential, Enhanced"],
                         ["2", "Some copy", "Essential"],
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
                         ["1", "X", ""],
                         ["2", "Y", ""],
                     ])
    findings = check(proj)
    assert any(f.issue == "no-tiers-on-line"
               for f in findings)


def test_worksheet_name_mismatch_blocks(tmp_path):
    """If the Brief's project_name doesn't match the on-disk worksheet
    filename, generation will fail. Surface that at inspect time."""
    proj = tmp_path / "Test Project"
    sd = _scope_dir(proj)
    _write_brief(proj, project_name="Sheraton San Diego Hotel & Marina")
    # Worksheet on disk uses a different name (the bug we hit on Sheraton).
    _write_worksheet(sd, "Sheraton San Diego Resort",
                     header_row=["Line #", "Customer-Facing Description", "Tiers"],
                     data_rows=[["1", "X", "Essential, Enhanced"]])
    findings = check(proj)
    name_mismatch = [f for f in findings if f.issue == "worksheet-name-mismatch"]
    assert len(name_mismatch) == 1
    assert name_mismatch[0].severity == "blocker"
    assert "Sheraton San Diego Hotel & Marina - Scope Worksheet.xlsx" in name_mismatch[0].detail


def test_worksheet_name_match_proceeds_to_content_checks(tmp_path):
    """When the Brief and worksheet names match, the inspector continues
    into the content checks rather than stopping at the name check."""
    proj = tmp_path / "Test Project"
    sd = _scope_dir(proj)
    _write_brief(proj, project_name="Match Project")
    _write_worksheet(sd, "Match Project",
                     header_row=["Line #", "Customer-Facing Description", "Tiers"],
                     data_rows=[["1", "X", "Essential, Enhanced"]])
    findings = check(proj)
    assert not any(f.issue == "worksheet-name-mismatch" for f in findings)


def test_worksheet_name_check_skipped_when_brief_missing(tmp_path):
    """When the Brief is missing (unrelated blocker reported by brief.py),
    the worksheet inspector falls back to glob match rather than emitting
    a name-mismatch finding alongside an unrelated brief error."""
    proj = tmp_path / "Test Project"
    sd = _scope_dir(proj)
    _write_worksheet(sd, "Whatever Name",
                     header_row=["Line #", "Customer-Facing Description", "Tiers"],
                     data_rows=[["1", "X", "Essential, Enhanced"]])
    findings = check(proj)
    assert not any(f.issue == "worksheet-name-mismatch" for f in findings)
