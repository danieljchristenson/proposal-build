"""Copy outputs into 04 - Process & Notes/revisions/v<n>/ after each render."""
from __future__ import annotations

import re
import shutil
from pathlib import Path


REVISION_DIR_NAME = "revisions"
REVISION_FOLDER_PATTERN = re.compile(r"^v(\d+)$")


def next_revision_number(notes_dir: Path) -> int:
    """Return the next integer N such that revisions/v<N> does not yet exist.

    If revisions/ doesn't exist, returns 1.
    """
    revisions_dir = notes_dir / REVISION_DIR_NAME
    if not revisions_dir.exists():
        return 1
    used = []
    for child in revisions_dir.iterdir():
        if child.is_dir():
            m = REVISION_FOLDER_PATTERN.match(child.name)
            if m:
                used.append(int(m.group(1)))
    return (max(used) + 1) if used else 1


def copy_to_revision(
    *,
    notes_dir: Path,
    revision: int,
    deck: Path | None,
    itemized: Path | None,
    workbook: Path | None,
    change_summary: Path | None,
    last_run_json: Path | None,
) -> Path:
    """Copy the listed outputs into notes_dir/revisions/v<revision>/.

    Existing files at the destination are overwritten. Missing source files
    are silently skipped (intentional — some outputs are optional per mode).
    Returns the path to the revision folder.
    """
    dest = notes_dir / REVISION_DIR_NAME / f"v{revision}"
    dest.mkdir(parents=True, exist_ok=True)
    for src, name in [
        (deck, "deck.pdf"),
        (itemized, "itemized.pdf"),
        (workbook, "workbook.xlsx"),
        (change_summary, "change_summary.md"),
        (last_run_json, "last_run.json"),
    ]:
        if src is not None and src.exists():
            shutil.copy2(src, dest / name)
    return dest
