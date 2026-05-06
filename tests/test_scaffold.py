"""Tests for scaffold_project()."""
from __future__ import annotations

import shutil
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
