"""Brief-readiness checks."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.inspector.report import Finding


# Mirrors parser.brief.REQUIRED_FIELDS (source of truth). Keep in sync.
REQUIRED_FIELDS = (
    "client_company", "project_name", "project_year", "presenter_name",
    "voice", "recommended_tier", "pricing_format", "cover_image",
)
REQUIRED_BULLET_SECTIONS = (
    "Customer Goals", "Customer Constraints", "Success Criteria",
    "Scope Includes",
)
REQUIRED_PROSE_SECTIONS = (
    "Creative Direction",
)
BRIEF_RELPATH = "04 - Process & Notes/Project Brief.md"


def check(project_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    brief_path = project_path / BRIEF_RELPATH

    if not brief_path.is_file():
        findings.append(Finding(
            severity="blocker", category="brief", issue="missing-brief",
            detail=f"Brief not found at {BRIEF_RELPATH}",
            fix=("Scaffold the project (or copy the template Brief into "
                 "`04 - Process & Notes/Project Brief.md`)."),
        ))
        return findings

    # Try to parse
    try:
        post = frontmatter.load(str(brief_path))
    except Exception as exc:
        findings.append(Finding(
            severity="error", category="brief",
            issue="brief-yaml-parse-error",
            detail=f"Could not parse Brief frontmatter: {exc}",
            fix="Open the Brief and fix the YAML syntax error.",
        ))
        return findings

    fm = post.metadata or {}

    # Frontmatter field presence
    for field_name in REQUIRED_FIELDS:
        value = fm.get(field_name)
        if value is None or value == "" or value == "(unknown)":
            findings.append(Finding(
                severity="blocker", category="brief", issue="missing-field",
                detail=f"Brief is missing required frontmatter field: {field_name}",
                fix=f"Provide a value for `{field_name}:` in the Brief.",
                field=field_name,
            ))

    # Zones present + hero_image per zone
    zones = fm.get("zones") or []
    if not zones:
        findings.append(Finding(
            severity="blocker", category="brief", issue="no-zones-defined",
            detail="Brief defines no zones.",
            fix="Add at least one zone under `zones:` in the frontmatter.",
        ))
    else:
        for z in zones:
            if not isinstance(z, dict):
                continue
            zone_name = z.get("name") or f"zone {z.get('num', '?')}"
            has_hero = z.get("hero_image") or z.get("hero_images")
            if not has_hero:
                findings.append(Finding(
                    severity="warning", category="brief", issue="no-hero-image",
                    detail=f"Zone '{zone_name}' has no hero_image assigned.",
                    fix=("Pick a rendering from `02 - Renderings/Base Scope/`"
                         " and set `hero_image:` on this zone."),
                    zone=zone_name,
                ))

    # Prose sections (lightweight check: section header present)
    body = post.content or ""
    for section in REQUIRED_BULLET_SECTIONS + REQUIRED_PROSE_SECTIONS:
        marker = f"## {section}"
        if marker not in body:
            findings.append(Finding(
                severity="blocker", category="brief", issue="missing-section",
                detail=f"Brief is missing required section: {section}",
                fix=f"Add a `## {section}` section with content.",
                field=section,
            ))

    return findings
