"""Tests for the folder-structure inspector."""
from proposal_build.inspector.folder import check


# Mirrors folder.py:REQUIRED_SUBDIRS — keep in sync.
REQUIRED_SUBDIRS = (
    "01 - RFP",
    "02 - Renderings",
    "02 - Renderings/Base Scope",
    "02 - Renderings/Enhancements",
    "02 - Renderings/Unused Renderings",
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
    (proj / "01 - RFP").mkdir()
    # Only one subdir present; expect findings for all the others
    findings = check(proj)
    assert len(findings) == len(REQUIRED_SUBDIRS) - 1
    for f in findings:
        assert f.severity == "blocker"
        assert f.issue == "missing-subdir"
        assert f.category == "folder"
