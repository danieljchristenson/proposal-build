"""Integration test for inspect_project()."""
from __future__ import annotations

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
