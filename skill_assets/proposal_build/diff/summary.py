"""Generate change_summary.md text from a ChangeReport."""
from __future__ import annotations

import fnmatch
import logging

from proposal_build.diff.dep_map import DepMap
from proposal_build.diff.differ import ChangeReport


logger = logging.getLogger(__name__)


def render_initial_summary(client_name: str, revision: int, generated_at: str) -> str:
    """Render the change_summary.md text for a first run (no prior to compare)."""
    return (
        f"# {client_name} Revision {revision} Change Summary\n"
        f"\n"
        f"**Generated:** {generated_at}\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Initial revision\n"
        f"\n"
        f"This is the first version generated for this proposal. No prior\n"
        f"revision exists to compare against.\n"
    )


def render_change_summary(
    *,
    client_name: str,
    revision: int,
    prior_revision: int,
    prior_generated_at: str,
    current_generated_at: str,
    change_report: ChangeReport,
    affected_slides: set[str],
    dep_map: DepMap,
) -> str:
    """Render the change_summary.md body for a subsequent run."""
    label_index = _build_label_index(dep_map)
    bullets = _bullets_for(change_report, label_index)

    affected_list = ", ".join(sorted(affected_slides)) or "none"

    body_lines = "\n".join(bullets) if bullets else "_No customer-visible changes._"

    return (
        f"# {client_name} Revision {revision} Change Summary\n"
        f"\n"
        f"**Generated:** {current_generated_at}\n"
        f"**Previous revision:** v{prior_revision} ({prior_generated_at})\n"
        f"\n"
        f"> Copy the section below into your customer email body.\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Changes since revision {prior_revision}\n"
        f"\n"
        f"{body_lines}\n"
        f"\n"
        f"---\n"
        f"\n"
        f"*Internal: affected slides this round: {affected_list}.*\n"
    )


def _build_label_index(dep_map: DepMap) -> dict[str, str]:
    """Flatten all brief/worksheet entries from the dep_map into a single
    {path_or_pattern -> human_label} index."""
    out: dict[str, str] = {}
    for entry in dep_map.slides.values():
        for b in entry.brief:
            if b.human_label and b.path not in out:
                out[b.path] = b.human_label
        for w in entry.worksheet:
            if w.human_label and w.pattern not in out:
                out[w.pattern] = w.human_label
    return out


def _bullets_for(cr: ChangeReport, labels: dict[str, str]) -> list[str]:
    bullets: list[str] = []
    for path, change in sorted(cr.brief.items()):
        kind = change[0]
        label = _label_for_path(path, labels)
        if label is None:
            logger.warning(
                "No human_label for brief path %r in dependency_map.yaml", path
            )
            label = path
        bullets.append(f"- **{label}:** {kind}")
    for key, change in sorted(cr.worksheet.items()):
        kind = change[0]
        label = _label_for_path(key, labels)
        if label is None:
            label = key
        bullets.append(f"- **{label}:** {kind} ({key})")
    for path, change in sorted(cr.renderings.items()):
        kind = change[0]
        bullets.append(f"- **Rendering {kind}:** {path}")
    return bullets


def _label_for_path(path: str, labels: dict[str, str]) -> str | None:
    """Resolve a label by exact match or by matching a glob pattern key."""
    if path in labels:
        return labels[path]
    for pattern, label in labels.items():
        if "*" in pattern and fnmatch.fnmatch(path, pattern):
            return label
    return None
