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
PAST_WORK_LIBRARY_DIR = (
    Path(__file__).resolve().parents[3] / "skill_assets" / "past_work_library"
)
TREE_LIBRARY_DIR = (
    Path(__file__).resolve().parents[3] / "skill_assets" / "tree_library"
)


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

    findings.extend(_check_sample_work(project_path, fm))
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

    findings.extend(_check_sample_work(project_path, fm))
    findings.extend(_check_tree_comparison(project_path, fm))
    return findings


def _check_sample_work(project_path: Path, fm: dict) -> list[Finding]:
    """Findings on the sample_work: field. Empty/absent → no findings."""
    findings: list[Finding] = []
    sample_work = fm.get("sample_work") or []
    if not sample_work:
        return findings

    if len(sample_work) != 6:
        findings.append(Finding(
            severity="blocker", category="brief",
            issue="sample_work_wrong_count",
            detail=(
                f"sample_work: lists {len(sample_work)} IDs; the past-work "
                "slide requires exactly 6."
            ),
            fix=(
                "Edit the Brief so `sample_work:` has exactly 6 project IDs "
                "from skill_assets/past_work_library/, or remove the field "
                "entirely to skip the slide."
            ),
            field="sample_work",
        ))
        return findings

    for pid in sample_work:
        md_path = PAST_WORK_LIBRARY_DIR / f"{pid}.md"
        if not md_path.exists():
            findings.append(Finding(
                severity="blocker", category="brief",
                issue="sample_work_unknown_id",
                detail=(
                    f"sample_work ID '{pid}' has no entry at "
                    f"{md_path.relative_to(PAST_WORK_LIBRARY_DIR.parents[1])}"
                ),
                fix=(
                    f"Either remove '{pid}' from sample_work: in the Brief, "
                    f"or add {pid}.md (and {pid}.jpg) to the past_work_library/."
                ),
                field="sample_work",
            ))
        jpg_path = PAST_WORK_LIBRARY_DIR / f"{pid}.jpg"
        if md_path.exists() and not jpg_path.exists():
            findings.append(Finding(
                severity="blocker", category="brief",
                issue="sample_work_missing_image",
                detail=(
                    f"sample_work ID '{pid}' has a .md entry but no "
                    f"matching {pid}.jpg in past_work_library/."
                ),
                fix=(
                    f"Add {pid}.jpg to skill_assets/past_work_library/ "
                    f"(recommended ~1200x800)."
                ),
                field="sample_work",
            ))

    return findings


def _check_tree_comparison(project_path: Path, fm: dict) -> list[Finding]:
    """Findings on the tree_comparison: field (menu-mode Brief).

    Empty/absent → no findings. Mirrors _check_sample_work's wrong-count
    short-circuit so per-ID errors don't drown out the real problem when
    the user's count is off.
    """
    findings: list[Finding] = []
    tc = fm.get("tree_comparison") or {}
    if not tc:
        return findings

    trees = tc.get("trees") or []
    if len(trees) != 3:
        findings.append(Finding(
            severity="blocker", category="brief",
            issue="tree_comparison_wrong_count",
            detail=(
                f"tree_comparison.trees lists {len(trees)} IDs; the "
                "Alternate Tree Options slide requires exactly 3."
            ),
            fix=(
                "Edit the Brief so `tree_comparison.trees:` has exactly 3 "
                "tree IDs from skill_assets/tree_library/, or remove the "
                "`tree_comparison:` block entirely to skip the slide."
            ),
            field="tree_comparison",
        ))
        return findings  # short-circuit per-ID checks

    for tid in trees:
        md_path = TREE_LIBRARY_DIR / f"{tid}.md"
        if not md_path.exists():
            findings.append(Finding(
                severity="blocker", category="brief",
                issue="tree_comparison_unknown_id",
                detail=(
                    f"tree_comparison ID '{tid}' has no entry at "
                    f"{md_path}"
                ),
                fix=(
                    f"Either remove '{tid}' from tree_comparison.trees in the "
                    f"Brief, or add {tid}.md (and {tid}.jpg) to the tree_library/."
                ),
                field="tree_comparison",
            ))
            continue  # skip image check if md is missing — unknown_id already covers it

        jpg_path = TREE_LIBRARY_DIR / f"{tid}.jpg"
        if not jpg_path.exists():
            findings.append(Finding(
                severity="blocker", category="brief",
                issue="tree_comparison_missing_image",
                detail=(
                    f"tree_comparison ID '{tid}' has a .md entry but no "
                    f"matching {tid}.jpg in tree_library/."
                ),
                fix=(
                    f"Add {tid}.jpg to skill_assets/tree_library/ "
                    f"(recommended ~1200x800, landscape)."
                ),
                field="tree_comparison",
            ))

    recommended = tc.get("recommended")
    if not recommended:
        findings.append(Finding(
            severity="blocker", category="brief",
            issue="tree_comparison_recommended_missing",
            detail=(
                "tree_comparison block is present but `recommended:` is "
                "missing or empty."
            ),
            fix=(
                "Add `recommended: <tree_id>` to the tree_comparison: block "
                "in the Brief. The ID must be one of those in `trees:`."
            ),
            field="tree_comparison",
        ))
    elif recommended not in trees:
        findings.append(Finding(
            severity="blocker", category="brief",
            issue="tree_comparison_recommended_not_in_trees",
            detail=(
                f"tree_comparison.recommended is '{recommended}', which is "
                f"not in tree_comparison.trees ({trees})."
            ),
            fix=(
                "Set `recommended:` to one of the tree IDs already listed "
                "under `tree_comparison.trees:`."
            ),
            field="tree_comparison",
        ))

    return findings
