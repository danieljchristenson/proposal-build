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
    gen.add_argument("--no-snapshot", action="store_true",
                     help="Skip writing last_run.json and revisions/ archive.")
    gen.add_argument("--diff-only", action="store_true",
                     help="Run differ + write change_summary.md, skip render and snapshot.")

    insp = sub.add_parser("inspect", help="Report project readiness as JSON.")
    insp.add_argument("project_dir", help="Path to the project folder")
    insp.add_argument("--format", choices=("json", "human"), default="json",
                      help="Output format (default: json)")

    sca = sub.add_parser("scaffold", help="Create a new project folder from the template.")
    sca.add_argument("project_name", help="Name of the new project (folder under Projects/)")

    args = parser.parse_args(argv)

    if args.command == "generate":
        return _do_generate(
            Path(args.project_dir),
            args.use_latest_layouts,
            args.compress,
            no_snapshot=args.no_snapshot,
            diff_only=args.diff_only,
        )
    if args.command == "inspect":
        return _do_inspect(Path(args.project_dir), args.format)
    if args.command == "scaffold":
        return _do_scaffold(args.project_name)
    return 1


def _do_generate(
    project_dir: Path,
    use_latest: bool,
    compress: bool,
    *,
    no_snapshot: bool = False,
    diff_only: bool = False,
) -> int:
    from datetime import datetime, timezone
    from proposal_build.diff import (
        load_dep_map, hash_brief, hash_worksheet_rows, hash_file,
        diff_snapshots, compute_affected_slides, flatten_brief,
        write_snapshot, read_snapshot, render_change_summary, render_initial_summary,
        copy_to_revision,
    )

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

    # === DIFF: pre-render snapshot + change report ===
    notes_dir = project_dir / "04 - Process & Notes"
    snapshot_path = notes_dir / "last_run.json"
    prior = read_snapshot(snapshot_path)

    brief_data = artifacts.get("brief_data")
    worksheet_rows = artifacts.get("worksheet_rows", [])
    eligible_renderings = artifacts.get("eligible_renderings", {})

    current_brief_hashes = hash_brief(brief_data) if brief_data else {}
    current_worksheet_hashes = hash_worksheet_rows(worksheet_rows)
    renderings_dir = project_dir / "02 - Renderings"
    current_rendering_hashes: dict[str, str] = {}
    for name, path in eligible_renderings.items():
        if path.exists():
            try:
                rel = str(path.resolve().relative_to(renderings_dir.resolve()))
            except ValueError:
                rel = name
            h = hash_file(path)
            if h is not None:
                current_rendering_hashes[rel] = h
    current_brief_flat = flatten_brief(brief_data) if brief_data else {}

    skill_dep_map_path = Path(__file__).resolve().parent.parent / "dependency_map.yaml"
    dep_map = load_dep_map(skill_dep_map_path)

    rendered_layout_names = tuple(s.layout_name for s in slides)
    rendered_slide_records = [
        {"layout": s.layout_name, "page": i + 1}
        for i, s in enumerate(slides)
    ]

    change_report = None
    affected_slides: set[str] = set()
    if prior is not None:
        current_snapshot_preview = {
            "brief": current_brief_hashes,
            "worksheet": current_worksheet_hashes,
            "renderings": current_rendering_hashes,
            "slides_rendered": rendered_slide_records,
        }
        change_report = diff_snapshots(prior=prior, current=current_snapshot_preview)
        affected_slides = compute_affected_slides(
            change_report, dep_map,
            brief_flat=current_brief_flat,
            worksheet_hashes=current_worksheet_hashes,
            rendered_slides=rendered_layout_names,
        )
        _print_change_report(change_report, affected_slides, prior)
    else:
        print("[diff] first run — no prior snapshot to compare against.")

    client_name = (
        getattr(model, "client_company", None)
        or getattr(model, "client_short", "")
        or "Project"
    )

    # === --diff-only: stop here, write summary only if prior existed ===
    if diff_only:
        if prior is None:
            print("[diff-only] no prior run to diff against; exiting.")
            return 0
        text = render_change_summary(
            client_name=client_name,
            revision=prior.get("revision", 0) + 1,
            prior_revision=prior.get("revision", 0),
            prior_generated_at=prior.get("generated_at", "(unknown)")[:10],
            current_generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            change_report=change_report,
            affected_slides=affected_slides,
            dep_map=dep_map,
        )
        (project_dir / "05 - Output").mkdir(parents=True, exist_ok=True)
        (project_dir / "05 - Output" / "change_summary.md").write_text(text, encoding="utf-8")
        print("[diff-only] wrote change_summary.md (no render performed).")
        return 0

    # === Render (unchanged from before) ===
    outcome = render(project_dir, model, slides, pricing_docs, artifacts, result,
                     use_latest, compress=compress)

    if outcome["status"] == "blocked":
        print(f"❌ BLOCKED. See: {outcome['report']}", file=sys.stderr)
        return 1

    # === Post-render: snapshot, summary, revisions ===
    if not no_snapshot:
        pdfs = outcome.get("pdfs", [])
        deck_pdf = pdfs[0] if pdfs else None
        itemized_pdf = pdfs[1] if len(pdfs) > 1 else None
        # workbook is currently script-generated (not produced by render); leave None.
        workbook_xlsx = None

        output_hashes: dict[str, str | None] = {}
        for p in pdfs:
            if p and p.exists():
                output_hashes[p.name] = hash_file(p)

        # No-changes case (per spec §7): don't bump revision counter, don't
        # create a new revisions/v<n>/, but DO refresh generated_at + write a
        # one-line change_summary.
        if prior is not None and change_report is not None and not change_report.has_changes:
            prior_revision_num = prior.get("revision", 0)
            no_change_payload = {
                **prior,
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            write_snapshot(snapshot_path, no_change_payload)
            (project_dir / "05 - Output").mkdir(parents=True, exist_ok=True)
            (project_dir / "05 - Output" / "change_summary.md").write_text(
                f"# {client_name} — no changes since revision {prior_revision_num}\n",
                encoding="utf-8",
            )
            print(f"[snapshot] no input changes since rev {prior_revision_num}; "
                  "revision counter not bumped.")
        else:
            revision = (prior.get("revision", 0) + 1) if prior else 1
            generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            payload = {
                "schema_version": 1,
                "generated_at": generated_at,
                "revision": revision,
                "brief": current_brief_hashes,
                "worksheet": current_worksheet_hashes,
                "renderings": current_rendering_hashes,
                "slides_rendered": rendered_slide_records,
                "outputs": output_hashes,
            }
            write_snapshot(snapshot_path, payload)

            (project_dir / "05 - Output").mkdir(parents=True, exist_ok=True)
            change_summary_path = project_dir / "05 - Output" / "change_summary.md"
            if prior is None:
                text = render_initial_summary(
                    client_name=client_name,
                    revision=revision,
                    generated_at=generated_at[:10],
                )
            else:
                text = render_change_summary(
                    client_name=client_name,
                    revision=revision,
                    prior_revision=prior.get("revision", 0),
                    prior_generated_at=prior.get("generated_at", "(unknown)")[:10],
                    current_generated_at=generated_at[:10],
                    change_report=change_report,
                    affected_slides=affected_slides,
                    dep_map=dep_map,
                )
            change_summary_path.write_text(text, encoding="utf-8")

            copy_to_revision(
                notes_dir=notes_dir,
                revision=revision,
                deck=deck_pdf,
                itemized=itemized_pdf,
                workbook=workbook_xlsx,
                change_summary=change_summary_path,
                last_run_json=snapshot_path,
            )
            print(f"[snapshot] wrote last_run.json (revision {revision})")
            print(f"[snapshot] copied outputs to 04 - Process & Notes/revisions/v{revision}/")
            print("[summary]  wrote change_summary.md")

    print("✅ Generation complete.")
    print(f"   Coverage Report: {outcome['report']}")
    print("   Outputs:")
    for p in outcome["pdfs"]:
        print(f"     • {p.name}")
    return 0


def _print_change_report(cr, affected_slides, prior) -> None:
    rev = prior.get("revision", 0)
    when = prior.get("generated_at", "(unknown)")[:10]
    print(f"[diff] CHANGES SINCE LAST RUN (rev {rev}, {when}):")
    if cr.brief:
        print("       Brief:")
        for path, change in sorted(cr.brief.items()):
            print(f"         - {path}: {change[0]}")
    if cr.worksheet:
        print("       Worksheet:")
        for key, change in sorted(cr.worksheet.items()):
            print(f"         - {key}: {change[0]}")
    if cr.renderings:
        print("       Renderings:")
        for path, change in sorted(cr.renderings.items()):
            print(f"         - {path}: {change[0]}")
    if not (cr.brief or cr.worksheet or cr.renderings):
        print("       no input changes detected.")
    if affected_slides:
        print(f"       Affected slides ({len(affected_slides)}): "
              f"{', '.join(sorted(affected_slides))}")


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
        theme="classic",
    )


if __name__ == "__main__":
    sys.exit(main())
