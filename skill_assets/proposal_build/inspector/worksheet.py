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
                fix=(f"Add a comma-separated tier list for line {line_num} "
                     "(Essential, Enhanced, Signature)."),
            ))

    return findings
