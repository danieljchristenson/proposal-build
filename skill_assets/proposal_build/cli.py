"""CLI entrypoint: `python -m proposal_build generate <project_dir>`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from proposal_build.parser import build_project_model, ProjectLoadError
from proposal_build.parser.validate import run_validation
from proposal_build.composer import compose
from proposal_build.renderer import render
from proposal_build.models import ValidationResult


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="proposal_build")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Generate a proposal for a project folder")
    gen.add_argument("project_dir", help="Path to the project folder")
    gen.add_argument("--use-latest-layouts", action="store_true",
                     help="Refresh the layout_pin.json to current versions")
    gen.add_argument("--compress", action="store_true",
                     help="Run ghostscript /ebook on output PDFs (smaller send-size).")

    args = parser.parse_args(argv)

    if args.command == "generate":
        return _do_generate(Path(args.project_dir), args.use_latest_layouts, args.compress)
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
