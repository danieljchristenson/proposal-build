"""Coverage Report writer + layout pin reader/writer."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from proposal_build.models import ProjectModel, ValidationResult


LAYOUT_VERSION_RE = re.compile(r"<!-- layout-version:\s*([\d-]+)\s*-->")


class LayoutPinError(Exception):
    pass


def read_layout_versions(layouts_dir: Path) -> dict[str, str]:
    """Scan all .html files in layouts_dir; extract their layout-version header."""
    versions: dict[str, str] = {}
    for f in sorted(layouts_dir.iterdir()):
        if f.suffix.lower() != ".html":
            continue
        first_line = f.read_text().splitlines()[0] if f.exists() else ""
        m = LAYOUT_VERSION_RE.search(first_line)
        if m:
            versions[f.name] = m.group(1)
    return versions


def write_layout_pin(pin_path: Path, layouts_dir: Path) -> dict:
    """Create or update layout_pin.json. Sets first_run if file doesn't exist; updates last_run otherwise."""
    versions = read_layout_versions(layouts_dir)
    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")

    if pin_path.exists():
        existing = json.loads(pin_path.read_text())
        first_run = existing.get("first_run", now_iso)
    else:
        first_run = now_iso

    pin = {"first_run": first_run, "last_run": now_iso, "layouts": versions}
    pin_path.parent.mkdir(parents=True, exist_ok=True)
    pin_path.write_text(json.dumps(pin, indent=2))
    return pin


def check_layout_pin(pin_path: Path, layouts_dir: Path, use_latest: bool) -> list[tuple[str, str]]:
    """Compare on-disk layout versions to the pin. Returns list of blocker tuples (empty if OK or use_latest=True)."""
    if not pin_path.exists():
        return []   # First run — no pin to check
    if use_latest:
        return []

    pin = json.loads(pin_path.read_text())
    pinned = pin.get("layouts", {})
    on_disk = read_layout_versions(layouts_dir)

    blockers = []
    for filename, pinned_version in pinned.items():
        disk_version = on_disk.get(filename)
        if disk_version is None:
            continue   # layout file removed; not a Plan 3 concern
        if disk_version != pinned_version:
            blockers.append((
                "layout_pin_drift",
                f"{filename} version is {disk_version} on disk but pinned to {pinned_version}. "
                f"Pass --use-latest-layouts to refresh, or revert layout to pinned version.",
            ))
    return blockers


def write_coverage_report(
    report_path: Path,
    model: ProjectModel,
    artifacts: dict,
    result: ValidationResult,
    slides: list,
    pricing_docs: list,
    use_latest_layouts: bool,
) -> Path:
    """Write the human-readable coverage report Markdown."""
    lines = []
    lines.append(f"# Coverage Report — {model.project_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if use_latest_layouts:
        lines.append("\n**LAYOUT PIN UPDATED** — visual output may differ from prior runs.")
    status_icon = "✅ PASSED — proposal generated." if result.passed else "❌ BLOCKED — see errors below."
    lines.append(f"Status: {status_icon}")
    lines.append("")

    if not result.passed:
        lines.append("## Blocking Errors")
        for code, msg in result.blockers:
            lines.append(f"- **{code}**: {msg}")
        lines.append("")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines))
        return report_path

    # PASSED path — full summary
    items = list(model.line_items)
    lines.append("## Summary")
    lines.append(f"- Worksheet line items: {len(items)} "
                 f"({sum(1 for li in items if not li.is_enhancement)} base + "
                 f"{sum(1 for li in items if li.is_enhancement)} enhancements)")
    lines.append(f"  ✓ {sum(1 for li in items if li.tiers)} mapped to a tier")
    lines.append(f"  ✓ {sum(1 for li in items if li.customer_facing)} have Customer-Facing Description")
    lines.append(f"  ✓ {sum(1 for li in items if li.zone)} have Zone assignment")
    lines.append(f"- Zones: {len(model.zones)} declared in Brief")
    for z in model.zones:
        direct = sum(1 for li in items if li.zone == z.name)
        lines.append(f"  ✓ {z.name} ({direct} priced items, {len(z.bullets)} bullets)")
    lines.append(f"- Renderings: {len(artifacts['eligible_renderings'])} on disk")
    lines.append(f"  ✓ {len(set(artifacts['referenced_filenames']))} wired into hero_image fields")
    lines.append("")

    lines.append("## Slide Plan")
    for i, item in enumerate(slides, start=1):
        layout = item.layout_name
        lines.append(f"{i}. {layout}")
    lines.append("")

    lines.append("## Itemized Pricing PDFs")
    for d in pricing_docs:
        all_lines = list(d.base_scope_lines) + list(d.enhancement_lines)
        lines.append(f"- {d.tier.value} (${d.tier_total:,.0f}) — {len(all_lines)} line items")
    lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        by_code: dict[str, list[str]] = {}
        for code, msg in result.warnings:
            by_code.setdefault(code, []).append(msg)
        for code in sorted(by_code):
            lines.append(f"### {code}")
            for msg in by_code[code]:
                lines.append(f"- {msg}")
        lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    return report_path
