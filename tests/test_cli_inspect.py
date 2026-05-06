"""CLI tests for `python -m proposal_build inspect`."""
from __future__ import annotations

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
