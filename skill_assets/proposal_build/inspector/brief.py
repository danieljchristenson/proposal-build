"""Brief-readiness checks."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.inspector.report import Finding
from proposal_build.parser.brief import (
    TIERED_REQUIRED_FIELDS,
    MENU_REQUIRED_FIELDS,
)


# Backward-compat alias — external callers may still reference REQUIRED_FIELDS.
REQUIRED_FIELDS = TIERED_REQUIRED_FIELDS
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
    mode = fm.get("mode", "tiered")
    if mode == "menu":
        findings.extend(_check_menu_mode(project_path, fm, post.content or ""))
        return findings

    # Tiered-mode checks (the original path).

    # Frontmatter field presence
    for field_name in TIERED_REQUIRED_FIELDS:
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


def _check_menu_mode(project_path: Path, fm: dict, body: str) -> list[Finding]:
    """Menu-mode-specific Brief readiness checks."""
    findings: list[Finding] = []

    # Required fields
    for field_name in MENU_REQUIRED_FIELDS:
        value = fm.get(field_name)
        if value is None or value == "" or value == "(unknown)":
            findings.append(Finding(
                severity="blocker", category="brief", issue="missing-field",
                detail=f"Menu-mode Brief missing required field: {field_name}",
                fix=f"Provide a value for `{field_name}:` in the Brief.",
                field=field_name,
            ))

    # Sections structural validation
    sections = fm.get("sections") or []
    if not sections:
        findings.append(Finding(
            severity="blocker", category="brief", issue="no-sections-defined",
            detail="Menu-mode Brief defines no sections.",
            fix="Add a `sections:` list to the Brief frontmatter (see Plan 9 docs).",
        ))
    else:
        for s in sections:
            if not isinstance(s, dict):
                continue
            for required_key in ("key", "label", "name", "is_lead", "item_codes"):
                if required_key not in s:
                    findings.append(Finding(
                        severity="blocker", category="brief", issue="section-missing-key",
                        detail=f"Menu-mode section missing required key: {required_key}",
                        fix=f"Add `{required_key}:` to each entry under `sections:`.",
                    ))
                    break
            if not s.get("item_codes"):
                findings.append(Finding(
                    severity="blocker", category="brief", issue="section-empty-item-codes",
                    detail=f"Menu-mode section {s.get('key', '?')!r} has empty item_codes",
                    fix="Add at least one item code to this section's item_codes list.",
                ))

    # Pre-built rendering files exist
    renderings_dir = project_path / "02 - Renderings" / "Base Scope"
    for name in ("prebuilt_cover_image", "creative_vision_hero"):
        fname = fm.get(name, "")
        if not fname:
            continue  # missing-field already reported above
        if not (renderings_dir / fname).exists():
            findings.append(Finding(
                severity="blocker", category="brief", issue="menu-hero-file-not-found",
                detail=f"{name} references missing rendering file: {fname}",
                fix=f"Place {fname} in 02 - Renderings/Base Scope/ or update the Brief.",
                field=name,
            ))

    return findings
