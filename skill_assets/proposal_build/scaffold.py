"""Scaffold a new project folder from `_template_project/`."""
from __future__ import annotations

import shutil
from pathlib import Path


# parents[2] == repo root (skill_assets/proposal_build/scaffold.py → ../../..)
_DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / "Projects" / "_template_project"


def scaffold_project(target: Path, source: Path | None = None) -> Path:
    """Copy the template project tree into target. Refuses overwrite.

    Returns the resolved target path on success.
    """
    target = Path(target)
    src = Path(source) if source is not None else _DEFAULT_SOURCE
    if not src.is_dir():
        raise FileNotFoundError(f"Template source missing: {src}")
    if target.exists():
        raise FileExistsError(
            f"Target already exists: {target}. "
            "Refusing to overwrite — pick a different name or delete the "
            "existing folder first."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target)
    return target.resolve()
