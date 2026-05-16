"""End-to-end: run generate twice on Riverside, assert diff behavior.

These tests run the full render pipeline and are therefore slow
(~45s per generate call). They are the real proof that the Plan 4
diff hooks behave correctly across revisions.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from proposal_build.cli import main


RIVERSIDE = (
    Path(__file__).resolve().parent.parent
    / "Projects" / "Downtown Riverside Metro Link"
)


def _pristine_copy(dst: Path) -> None:
    """Copy the Riverside fixture and scrub any diff/output artifacts a prior
    real `generate` run may have left behind, so each test starts clean
    regardless of the on-disk fixture state."""
    shutil.copytree(RIVERSIDE, dst)
    notes = dst / "04 - Process & Notes"
    for stale in [notes / "last_run.json", *notes.glob("last_run.json.broken-*")]:
        stale.unlink(missing_ok=True)
    shutil.rmtree(notes / "revisions", ignore_errors=True)
    shutil.rmtree(dst / "05 - Output", ignore_errors=True)


def _last_run(project: Path) -> dict:
    return json.loads(
        (project / "04 - Process & Notes" / "last_run.json").read_text()
    )


def test_run_twice_with_brief_edit_in_between(tmp_path: Path):
    project = tmp_path / "p"
    _pristine_copy(project)

    # First run: no prior snapshot, creates v1.
    rc = main(["generate", str(project)])
    assert rc == 0
    last_run_path = project / "04 - Process & Notes" / "last_run.json"
    assert last_run_path.exists()
    v1 = project / "04 - Process & Notes" / "revisions" / "v1"
    assert v1.exists()
    assert (v1 / "deck.pdf").exists()
    assert (v1 / "last_run.json").exists()
    assert _last_run(project)["revision"] == 1
    assert (project / "05 - Output" / "change_summary.md").exists()

    # Modify the Brief — change design_phrase only (targeted line replace;
    # "Holiday Express" also appears inside a rendering filename, so a broad
    # replace would break image resolution).
    brief_path = project / "04 - Process & Notes" / "Project Brief.md"
    text = brief_path.read_text()
    assert 'design_phrase: "Holiday Express"' in text
    brief_path.write_text(
        text.replace(
            'design_phrase: "Holiday Express"',
            'design_phrase: "Holiday Express Deluxe"',
        )
    )

    # Second run: detects the change, writes v2.
    rc = main(["generate", str(project)])
    assert rc == 0
    assert _last_run(project)["revision"] == 2
    v2 = project / "04 - Process & Notes" / "revisions" / "v2"
    assert v2.exists()
    assert (v2 / "change_summary.md").exists()

    summary_text = (project / "05 - Output" / "change_summary.md").read_text()
    assert "Revision 2" in summary_text


def test_run_twice_with_no_changes_does_not_bump_revision(tmp_path: Path):
    project = tmp_path / "p"
    _pristine_copy(project)

    rc = main(["generate", str(project)])
    assert rc == 0
    first_revision = _last_run(project)["revision"]

    rc = main(["generate", str(project)])
    assert rc == 0
    second_revision = _last_run(project)["revision"]

    # Per spec section 7 no-changes case: revision counter does NOT increment.
    assert second_revision == first_revision
    # And v<first_revision + 1> should NOT exist.
    bumped = (
        project / "04 - Process & Notes" / "revisions"
        / f"v{first_revision + 1}"
    )
    assert not bumped.exists()


def test_no_snapshot_flag_skips_snapshot(tmp_path: Path):
    project = tmp_path / "p"
    _pristine_copy(project)

    rc = main(["generate", str(project), "--no-snapshot"])
    assert rc == 0
    assert not (project / "04 - Process & Notes" / "last_run.json").exists()
    assert not (project / "04 - Process & Notes" / "revisions").exists()
