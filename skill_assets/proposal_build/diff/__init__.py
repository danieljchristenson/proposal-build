"""Diff-mode regeneration: snapshot, dep-map, differ, change summary, revisions."""
from proposal_build.diff.hasher import (
    hash_string, hash_brief, hash_worksheet_rows, hash_file, flatten_brief,
)
from proposal_build.diff.dep_map import (
    load_dep_map, resolve_slide_deps, DepMap, DepMapError, ResolvedDeps,
    SlideEntry, BriefEntry, WorksheetEntry, FollowEntry,
)
from proposal_build.diff.differ import (
    diff_snapshots, compute_affected_slides, ChangeReport,
)
from proposal_build.diff.snapshot import (
    write_snapshot, read_snapshot, SnapshotError, SUPPORTED_SCHEMA_VERSIONS,
)
from proposal_build.diff.summary import (
    render_change_summary, render_initial_summary,
)
from proposal_build.diff.revisions import (
    copy_to_revision, next_revision_number,
)

__all__ = [
    "hash_string", "hash_brief", "hash_worksheet_rows", "hash_file", "flatten_brief",
    "load_dep_map", "resolve_slide_deps", "DepMap", "DepMapError", "ResolvedDeps",
    "SlideEntry", "BriefEntry", "WorksheetEntry", "FollowEntry",
    "diff_snapshots", "compute_affected_slides", "ChangeReport",
    "write_snapshot", "read_snapshot", "SnapshotError", "SUPPORTED_SCHEMA_VERSIONS",
    "render_change_summary", "render_initial_summary",
    "copy_to_revision", "next_revision_number",
]
