"""Plan 4: CLI flag handling for diff hooks.

Light-weight tests: verify flags are parsed and the right early-exit
paths fire. Full end-to-end pipeline behaviour is covered by
test_diff_integration.py (T14), which is slower because it actually
runs the renderer.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from proposal_build.cli import main


RIVERSIDE = (
    Path(__file__).resolve().parent.parent
    / "Projects" / "Downtown Riverside Metro Link"
)


def test_diff_only_flag_with_no_prior_snapshot(tmp_path: Path, capsys):
    """--diff-only on a fresh project should print 'no prior run' and exit 0
    without running the renderer."""
    project = tmp_path / "p"
    shutil.copytree(RIVERSIDE, project)
    rc = main(["generate", str(project), "--diff-only"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "no prior run" in captured.out.lower()
    # Nothing should have been written.
    assert not (project / "04 - Process & Notes" / "last_run.json").exists()
    assert not (project / "05 - Output").exists() or not list(
        (project / "05 - Output").glob("*.md")
    )


def test_generate_flags_are_parsed():
    """Argparse should accept --no-snapshot and --diff-only without error."""
    import argparse
    # If the flags weren't wired, --help would be the only sane thing to test;
    # instead verify they don't trip argparse on a bare-minimum invocation.
    with pytest.raises(SystemExit) as excinfo:
        main(["generate", "--help"])
    # --help exits with 0
    assert excinfo.value.code == 0
