"""Renderer top-level: model + slides + pricing_docs → PDFs + report + pin."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from proposal_build.models import ProjectModel, ValidationResult
from proposal_build.renderer.pdf import render_proposal_pdf
from proposal_build.renderer.pricing_pdf import render_pricing_pdf
from proposal_build.renderer.report import (
    write_coverage_report, write_layout_pin, check_layout_pin,
)


LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def render(
    project_dir: Path,
    model: ProjectModel,
    slides: list,
    pricing_docs: list,
    artifacts: dict,
    result: ValidationResult,
    use_latest_layouts: bool = False,
) -> dict:
    """Top-level: writes all outputs, returns paths dict."""
    project_dir = Path(project_dir)
    notes = project_dir / "04 - Process & Notes"
    pricing_dir = project_dir / "03 - Scope & Pricing"

    # Run dir
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = notes / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Layout pin check (blocking error if drift and not --use-latest-layouts)
    pin_path = notes / "layout_pin.json"
    pin_blockers = check_layout_pin(pin_path, LAYOUTS_DIR, use_latest_layouts)
    result.blockers.extend(pin_blockers)

    # If we have any blockers, write the report and return without rendering
    if not result.passed:
        report_path = notes / "coverage_report.md"
        write_coverage_report(report_path, model, artifacts, result, slides, pricing_docs,
                               use_latest_layouts)
        shutil.copy(report_path, run_dir / "coverage_report.md")
        return {"status": "blocked", "report": report_path, "run_dir": run_dir, "pdfs": []}

    # Render proposal PDF
    proposal_filename = f"{model.project_name} - {model.project_year} {model.proposal_type}.pdf"
    proposal_run = run_dir / proposal_filename
    render_proposal_pdf([(s.layout_name, s.context) for s in slides], proposal_run)

    # Render pricing PDFs
    pricing_runs = []
    for doc in pricing_docs:
        pname = f"{model.project_name} - {model.project_year} Itemized Pricing - {doc.tier.value}.pdf"
        prun = run_dir / pname
        render_pricing_pdf(doc, prun)
        pricing_runs.append(prun)

    # Copy run outputs to 03 - Scope & Pricing/ (latest)
    pricing_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(proposal_run, pricing_dir / proposal_filename)
    for prun in pricing_runs:
        shutil.copy(prun, pricing_dir / prun.name)

    # Write/update layout pin
    write_layout_pin(pin_path, LAYOUTS_DIR)

    # Write coverage report
    report_path = notes / "coverage_report.md"
    write_coverage_report(report_path, model, artifacts, result, slides, pricing_docs,
                          use_latest_layouts)
    shutil.copy(report_path, run_dir / "coverage_report.md")

    return {
        "status": "ok",
        "report": report_path,
        "run_dir": run_dir,
        "pdfs": [pricing_dir / proposal_filename] + [pricing_dir / p.name for p in pricing_runs],
    }
