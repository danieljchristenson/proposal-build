"""Tests for scaffold_project()."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from proposal_build.inspector.folder import REQUIRED_SUBDIRS
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
    for sub in REQUIRED_SUBDIRS:
        assert (target / sub).is_dir(), f"Missing: {sub}"


def test_scaffold_refuses_overwrite(tmp_path, template_clone):
    target = tmp_path / "Projects" / "Existing"
    target.mkdir(parents=True)
    with pytest.raises(FileExistsError):
        scaffold_project(target, source=template_clone)


def test_cli_scaffold_creates_folder(tmp_path, monkeypatch, template_clone):
    """The CLI subcommand should create the project under Projects/."""
    # Layout a tmp repo: Projects/_template_project/ + Projects/ for output
    fake_repo = tmp_path / "fake_repo"
    (fake_repo / "Projects").mkdir(parents=True)
    shutil.copytree(template_clone, fake_repo / "Projects" / "_template_project")
    r = subprocess.run(
        [sys.executable, "-m", "proposal_build", "scaffold", "CLI Test Project"],
        capture_output=True, text=True, cwd=fake_repo, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert (fake_repo / "Projects" / "CLI Test Project" / "04 - Process & Notes").is_dir()


def test_cli_scaffold_refuse_overwrite_returns_exit_1(tmp_path, template_clone):
    fake_repo = tmp_path / "fake_repo"
    (fake_repo / "Projects" / "Existing").mkdir(parents=True)
    shutil.copytree(template_clone, fake_repo / "Projects" / "_template_project")
    r = subprocess.run(
        [sys.executable, "-m", "proposal_build", "scaffold", "Existing"],
        capture_output=True, text=True, cwd=fake_repo, timeout=60,
    )
    assert r.returncode == 1
    assert "exists" in (r.stderr + r.stdout).lower()
