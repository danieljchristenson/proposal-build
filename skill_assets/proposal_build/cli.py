"""CLI entrypoint: `python -m proposal_build generate <project_dir>`."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from proposal_build.parser import build_project_model, ProjectLoadError
from proposal_build.parser.validate import run_validation
from proposal_build.composer import compose
from proposal_build.renderer import render
from proposal_build.models import ValidationResult
from proposal_build.inspector import inspect_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="proposal_build")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Generate a proposal for a project folder")
    gen.add_argument("project_dir", help="Path to the project folder")
    gen.add_argument("--use-latest-layouts", action="store_true",
                     help="Refresh the layout_pin.json to current versions")
    gen.add_argument("--compress", action="store_true",
                     help="Run ghostscript /ebook on output PDFs (smaller send-size).")

    insp = sub.add_parser("inspect", help="Report project readiness as JSON.")
    insp.add_argument("project_dir", help="Path to the project folder")
    insp.add_argument("--format", choices=("json", "human"), default="json",
                      help="Output format (default: json)")

    sca = sub.add_parser("scaffold", help="Create a new project folder from the template.")
    sca.add_argument("project_name", help="Name of the new project (folder under Projects/)")

    args = parser.parse_args(argv)

    if args.command == "generate":
        return _do_generate(Path(args.project_dir), args.use_latest_layouts, args.compress)
    if args.command == "inspect":
        return _do_inspect(Path(args.project_dir), args.format)
    if args.command == "scaffold":
        return _do_scaffold(args.project_name)
    return 1


def _do_generate(project_dir: Path, use_latest: bool, compress: bool) -> int:
    try:
        model, artifacts = build_project_model(project_dir)
    except ProjectLoadError as e:
        # Convert to a ValidationResult so the report still gets written
        result = ValidationResult(blockers=[("project_load", str(e))], warnings=[])
        outcome = render(project_dir, _placeholder_model(), [], [], {}, result, use_latest)
        print(f"❌ BLOCKED — {e}", file=sys.stderr)
        print(f"   See: {outcome['report']}", file=sys.stderr)
        return 1

    # Validation pass
    result = run_validation(
        model,
        eligible_renderings=artifacts["eligible_renderings"],
        referenced_filenames=artifacts["referenced_filenames"],
        per_line_sums=artifacts["per_line_sums"],
        scenarios=artifacts["scenarios"],
    )

    # Composition
    slides, pricing_docs = compose(model)

    # Render
    outcome = render(project_dir, model, slides, pricing_docs, artifacts, result,
                     use_latest, compress=compress)

    if outcome["status"] == "blocked":
        print(f"❌ BLOCKED. See: {outcome['report']}", file=sys.stderr)
        return 1

    print("✅ Generation complete.")
    print(f"   Coverage Report: {outcome['report']}")
    print("   Outputs:")
    for p in outcome["pdfs"]:
        print(f"     • {p.name}")
    return 0


def _do_inspect(project_dir: Path, fmt: str) -> int:
    report = inspect_project(project_dir)
    if fmt == "json":
        # Convert dataclass to dict, then dumps; Path → str.
        payload = {
            "project_path": str(report.project_path),
            "ready_to_generate": report.ready_to_generate,
            "summary": report.summary,
            "findings": [asdict(f) for f in report.findings],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(report.summary)
        for f in report.findings:
            print(f"  [{f.severity}] {f.category}/{f.issue}: {f.detail}")
            if f.fix:
                print(f"    fix: {f.fix}")
    if any(f.severity == "error" for f in report.findings):
        return 2
    if not report.ready_to_generate:
        return 1
    return 0


def _do_scaffold(project_name: str) -> int:
    from proposal_build.scaffold import scaffold_project
    target = Path.cwd() / "Projects" / project_name
    try:
        out = scaffold_project(target)
    except FileExistsError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    print(f"✅ Created {out}")
    return 0


def _placeholder_model():
    """Return a no-op model when project loading itself failed,
    so the renderer can still write a coverage report."""
    from proposal_build.models import ProjectModel, Tier
    return ProjectModel(
        client_company="(unknown)", client_short="", project_name="(unknown)",
        project_short="", project_year=0, project_subtitle="", proposal_type="Holiday Proposal",
        presenter_name="", presenter_title="", presenter_email="", presenter_phone="",
        proposal_date="", go_live="", season_end="",
        fabrication_lock="", signing_deadline="",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="", pricing_format="tiered",
        cover_image="", creative_vision_hero="", case_study="skip", case_study_hero="",
        zones=(), line_items=(), creative_direction="", customer_goals=(),
        customer_constraints=(), success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(), term_panels={},
        after_approval_steps=(), company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )


if __name__ == "__main__":
    sys.exit(main())
