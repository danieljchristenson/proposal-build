"""Walk 02 - Renderings/ folders and resolve filename → absolute Path.

Brief.md references images by filename only; this module resolves to actual
files on disk. Ambiguity (same filename in both Base Scope/ and Enhancements/)
or missing files are surfaced as exceptions for the validator to convert into
blocking errors.
"""
from __future__ import annotations

from pathlib import Path


class RenderingsResolutionError(Exception):
    """Raised when a referenced filename can't be uniquely resolved."""


SUBDIRS = ("Base Scope", "Enhancements", "_inbox", "Unused Renderings")


def walk_renderings(project_dir: Path) -> dict[str, Path]:
    """Return {filename → Path} for every image in 02 - Renderings/{Base Scope|Enhancements}/.

    Files in _inbox/ and Unused Renderings/ are NOT included in the lookup map
    (they are not eligible for use as cover/zone/case-study heroes), but the
    walker still records them for the W1 unused-renderings warning.
    """
    renderings_dir = project_dir / "02 - Renderings"
    if not renderings_dir.exists():
        return {}

    eligible: dict[str, list[Path]] = {}
    for subdir in ("Base Scope", "Enhancements"):
        sub = renderings_dir / subdir
        if not sub.exists():
            continue
        for f in sub.iterdir():
            if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                eligible.setdefault(f.name, []).append(f)

    # Convert to single-Path lookup, raising on duplicates
    lookup: dict[str, Path] = {}
    for name, paths in eligible.items():
        if len(paths) > 1:
            locations = ", ".join(str(p.parent.name) for p in paths)
            raise RenderingsResolutionError(
                f"Filename '{name}' appears in multiple folders ({locations}). "
                f"Rename one to disambiguate."
            )
        lookup[name] = paths[0]

    return lookup


def list_all_renderings(project_dir: Path) -> dict[str, list[Path]]:
    """Return {subdir_name → list of files} across all 4 subdirs.

    Used by the validator's W1 unused-renderings check.
    """
    renderings_dir = project_dir / "02 - Renderings"
    if not renderings_dir.exists():
        return {sd: [] for sd in SUBDIRS}

    out: dict[str, list[Path]] = {}
    for subdir in SUBDIRS:
        sub = renderings_dir / subdir
        if sub.exists():
            out[subdir] = sorted(
                f for f in sub.iterdir()
                if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            )
        else:
            out[subdir] = []
    return out


def resolve_filename(filename: str, lookup: dict[str, Path]) -> Path:
    """Resolve a Brief-referenced filename. Raises if not found."""
    p = lookup.get(filename)
    if p is None:
        raise RenderingsResolutionError(
            f"Image filename '{filename}' not found in 02 - Renderings/Base Scope/ or Enhancements/."
        )
    return p
