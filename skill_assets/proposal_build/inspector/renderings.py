"""Renderings-folder readiness checks."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.inspector.brief import BRIEF_RELPATH
from proposal_build.inspector.report import Finding


# Folder names mirror inspector.folder.REQUIRED_SUBDIRS. Keep in sync.
RENDERINGS_DIR = "02 - Renderings"
SEARCH_SUBDIRS = ("Base Scope", "Enhancements", "Greenery references")
INBOX_SUBDIR = "_inbox"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return [p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS]


def _all_renderings(rd: Path) -> list[Path]:
    out: list[Path] = []
    for sub in SEARCH_SUBDIRS:
        out.extend(_list_images(rd / sub))
    return out


def check(project_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    rd = project_path / RENDERINGS_DIR
    if not rd.is_dir():
        return []  # folder.py already reports this

    all_files = _all_renderings(rd)
    if not all_files:
        findings.append(Finding(
            severity="warning", category="renderings",
            issue="no-renderings-present",
            detail=("No renderings found in `Base Scope/`, `Enhancements/`,"
                    " or `Greenery references/`."),
            fix=("Drop renderings into the appropriate subfolder under "
                 f"`{RENDERINGS_DIR}/`."),
        ))

    inbox_files = _list_images(rd / INBOX_SUBDIR)
    if inbox_files:
        findings.append(Finding(
            severity="warning", category="renderings",
            issue="files-in-inbox",
            detail=f"{len(inbox_files)} file(s) sitting in `_inbox/` "
                   "unsorted.",
            fix=("Move each into the appropriate subfolder "
                 "(`Base Scope/`, `Enhancements/`, or "
                 "`Greenery references/`)."),
        ))

    # Resolve hero_image references from the Brief
    brief_path = project_path / BRIEF_RELPATH
    if brief_path.is_file():
        try:
            post = frontmatter.load(str(brief_path))
            zones = post.metadata.get("zones") or []
        except Exception:
            zones = []  # brief.py reports the parse error
        available = {p.name for p in all_files}
        for z in zones:
            if not isinstance(z, dict):
                continue
            zone_name = z.get("name") or f"zone {z.get('num', '?')}"
            refs: list[str] = []
            if z.get("hero_image"):
                refs.append(z["hero_image"])
            for hi in z.get("hero_images") or []:
                refs.append(hi)
            for ref in refs:
                if ref not in available:
                    findings.append(Finding(
                        severity="blocker", category="renderings",
                        issue="hero-image-unresolved",
                        detail=(f"Zone '{zone_name}' references "
                                f"`{ref}` but no such file exists in "
                                "the renderings subfolders."),
                        fix=(f"Add the file to "
                             f"`{RENDERINGS_DIR}/<subfolder>/` or "
                             "update the Brief reference."),
                        zone=zone_name,
                    ))

    return findings
