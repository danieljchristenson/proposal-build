"""Folder-structure readiness checks."""
from __future__ import annotations

from pathlib import Path

from proposal_build.inspector.report import Finding


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


def check(project_path: Path) -> list[Finding]:
    """Return Findings about folder presence + subdirectory completeness."""
    if not project_path.exists() or not project_path.is_dir():
        return [Finding(
            severity="blocker",
            category="folder",
            issue="no-project-folder",
            detail=f"Project folder does not exist: {project_path}",
            fix=(f"Run `python -m proposal_build scaffold "
                 f"\"{project_path.name}\"` to create it from the template."),
        )]

    findings: list[Finding] = []
    for sub in REQUIRED_SUBDIRS:
        if not (project_path / sub).is_dir():
            findings.append(Finding(
                severity="blocker",
                category="folder",
                issue="missing-subdir",
                detail=f"Required subdirectory missing: {sub}",
                fix=f"Create the directory `{project_path / sub}`.",
            ))
    return findings
