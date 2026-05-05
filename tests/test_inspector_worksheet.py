"""Tests for the Worksheet inspector."""
from __future__ import annotations

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
