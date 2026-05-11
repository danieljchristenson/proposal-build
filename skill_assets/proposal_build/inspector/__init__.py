"""Inspector — deterministic project-readiness checks.

Public API: inspect_project(project_path) -> InspectionReport
"""
from __future__ import annotations

from pathlib import Path

from proposal_build.inspector import folder, brief, worksheet, renderings
from proposal_build.inspector.report import Finding, InspectionReport


def inspect_project(project_path: Path) -> InspectionReport:
    """Run all readiness checks and aggregate Findings."""
    project_path = Path(project_path)
    findings: list[Finding] = []

    # Order matters: if folder is missing, downstream checks would fail
    # spuriously, so we short-circuit. Brief/worksheet/renderings each
    # also short-circuit internally if their root subdir is missing.
    folder_findings = _safe_check(folder.check, project_path, "folder")
    findings.extend(folder_findings)

    has_blocking_folder_issue = any(
        f.severity == "blocker" and f.issue == "no-project-folder"
        for f in folder_findings
    )
    if not has_blocking_folder_issue:
        findings.extend(_safe_check(brief.check, project_path, "brief"))
        findings.extend(_safe_check(worksheet.check, project_path, "worksheet"))
        findings.extend(_safe_check(renderings.check, project_path, "renderings"))
        findings.extend(_run_validator_pass(project_path))

    blockers = [f for f in findings if f.severity == "blocker"]
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    ready = not blockers and not errors

    if ready:
        summary = (
            f"Ready to generate ({len(warnings)} warning(s))."
            if warnings else "Ready to generate."
        )
    else:
        bits = []
        if blockers:
            bits.append(f"{len(blockers)} blocker(s)")
        if errors:
            bits.append(f"{len(errors)} error(s)")
        if warnings:
            bits.append(f"{len(warnings)} warning(s)")
        summary = ", ".join(bits) + "."

    return InspectionReport(
        project_path=project_path,
        ready_to_generate=ready,
        findings=tuple(findings),
        summary=summary,
    )


def _safe_check(fn, project_path: Path, category: str) -> list[Finding]:
    """Wrap a category check so an unexpected exception becomes a Finding."""
    try:
        return fn(project_path)
    except Exception as exc:
        return [Finding(
            severity="error", category=category, issue="check-crashed",
            detail=f"Inspector module {category} crashed: {exc!r}",
            fix="Send this output to Daniel; the inspector has a bug.",
        )]


def _run_validator_pass(project_path: Path) -> list[Finding]:
    """Try to parse the project and run W1-W8 validators. For menu-mode
    projects the tier-specific validators don't apply; return [] without
    crashing. If tiered parsing fails, the brief/worksheet inspectors
    already reported the cause."""
    import frontmatter
    brief_path = project_path / "04 - Process & Notes" / "Project Brief.md"
    if brief_path.is_file():
        try:
            mode = frontmatter.load(str(brief_path)).metadata.get("mode", "tiered")
        except Exception:
            mode = "tiered"
        if mode == "menu":
            return []  # W1-W8 don't apply to menu mode (yet)

    from proposal_build.parser import build_project_model, ProjectLoadError
    from proposal_build.parser.validate import run_validation

    try:
        model, artifacts = build_project_model(project_path)
    except ProjectLoadError:
        return []  # already reported by upstream inspectors
    except Exception as exc:
        return [Finding(
            severity="error", category="validator",
            issue="parser-crashed",
            detail=f"Parser crashed unexpectedly: {exc!r}",
            fix="Send this output to Daniel; the parser has a bug.",
        )]

    result = run_validation(
        model,
        eligible_renderings=artifacts["eligible_renderings"],
        referenced_filenames=artifacts["referenced_filenames"],
        per_line_sums=artifacts["per_line_sums"],
        scenarios=artifacts["scenarios"],
    )

    findings: list[Finding] = []
    for code, msg in result.blockers:
        findings.append(Finding(
            severity="blocker", category="validator", issue=code,
            detail=msg, fix=None,
        ))
    for code, msg in result.warnings:
        findings.append(Finding(
            severity="warning", category="validator", issue=code,
            detail=msg, fix=None,
        ))
    return findings
