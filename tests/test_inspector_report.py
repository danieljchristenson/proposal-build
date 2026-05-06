"""Tests for the Finding + InspectionReport dataclasses."""
from __future__ import annotations

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
