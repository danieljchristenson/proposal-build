"""Export AE-facing project files to a OneDrive-synced folder.

The proposal engine is self-contained in ``skill_assets/`` and is deployed
*into Claude Desktop* as a skill -- it is NEVER synced via OneDrive. OneDrive
only needs the per-project working folders the skill reads from and writes to.

This script mirrors ``Projects/`` into a clean destination, dropping the engine,
git/venv, regeneration snapshots, and OneDrive-hostile noise. It is
non-destructive: it copies/refreshes files at the destination but never deletes.

Usage
-----
    # See what WOULD copy, and flag any path too long for a Windows PC:
    python scripts/export_to_onedrive.py --dest "/path/to/OneDrive/proposal-build" \
        --win-root "C:\\Users\\ae\\OneDrive - St Nicks\\proposal-build" --dry-run

    # Do the copy:
    python scripts/export_to_onedrive.py --dest "/path/to/OneDrive/proposal-build"

The ``--win-root`` is the folder path as it will appear on the AEs' PCs. We use
it ONLY to compute the eventual Windows path length and warn about files that
would exceed the 260-char MAX_PATH limit (a common silent OneDrive sync failure).
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

# Directory names dropped wherever they appear in the tree.
# NOTE: "_inbox" and "Unused Renderings" are part of the engine's required
# project structure (the validator blocks if they're missing), so they are
# NOT excluded -- _inbox is also the staging target for incoming renderings.
EXCLUDE_DIRS = {
    "runs",            # 04 - Process & Notes regeneration snapshots
    "_archive",        # archived junk, not part of the project contract
    ".git", ".venv", "__pycache__", ".pytest_cache",
}
# File names / glob patterns dropped wherever they appear.
EXCLUDE_FILE_GLOBS = (".DS_Store", "*.pyc", "~$*", ".~lock.*")
# Top-level repo entries AEs need: the skill bundle (to install in Claude
# Desktop) and the project working folders. Everything else (.git, .venv,
# tests/, docs/, scripts/, pyproject, Master Proposal Reference, archive/)
# is dev-only and never exported.
EXPORT_TOPLEVEL = ("skill_assets", "Projects")

WIN_MAX_PATH = 260
WARN_PATH_LEN = 240  # leave headroom under the hard limit


def _excluded_dir(part: str) -> bool:
    return part in EXCLUDE_DIRS or part.endswith(".egg-info")


def _excluded_file(name: str) -> bool:
    return any(Path(name).match(pat) for pat in EXCLUDE_FILE_GLOBS)


def iter_export_files(src_root: Path):
    """Yield (abs_path, rel_path) for every file that should be exported."""
    for top in EXPORT_TOPLEVEL:
        top_dir = src_root / top
        if not top_dir.is_dir():
            continue
        for path in sorted(top_dir.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(src_root)  # keep "<top>/..." prefix
            if any(_excluded_dir(part) for part in rel.parts):
                continue
            if _excluded_file(path.name):
                continue
            yield path, rel


def iter_export_dirs(src_root: Path):
    """Yield rel_path for every (incl. empty) directory that should exist.

    Reproducing empty dirs matters: the engine requires structural folders
    like ``02 - Renderings/_inbox`` and ``Unused Renderings`` to exist even
    when empty, or it blocks generation.
    """
    for top in EXPORT_TOPLEVEL:
        top_dir = src_root / top
        if not top_dir.is_dir():
            continue
        for path in sorted(top_dir.rglob("*")):
            if not path.is_dir():
                continue
            rel = path.relative_to(src_root)
            if any(_excluded_dir(part) for part in rel.parts):
                continue
            yield rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default=str(Path(__file__).resolve().parent.parent),
                    help="Repo root (default: this repo).")
    ap.add_argument("--dest", required=True,
                    help="Destination root (your locally-synced OneDrive folder).")
    ap.add_argument("--win-root", default=None,
                    help="The folder's eventual Windows path, for MAX_PATH checks.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report only; copy nothing.")
    args = ap.parse_args()

    src_root = Path(args.src)
    dest_root = Path(args.dest)
    if not any((src_root / t).is_dir() for t in EXPORT_TOPLEVEL):
        ap.error(f"None of {EXPORT_TOPLEVEL} found under {args.src!r}")

    copied = skipped_fresh = 0
    total_bytes = 0
    long_paths: list[tuple[int, str]] = []

    if not args.dry_run:
        for rel in iter_export_dirs(src_root):
            (dest_root / rel).mkdir(parents=True, exist_ok=True)

    for src_path, rel in iter_export_files(src_root):
        dest_path = dest_root / rel

        if args.win_root:
            win_len = len(str(Path(args.win_root) / rel).replace("/", "\\"))
            if win_len >= WARN_PATH_LEN:
                long_paths.append((win_len, str(rel)))

        if not args.dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            # refresh only if missing or changed (size/mtime) -> cheap re-runs
            if (not dest_path.exists()
                    or dest_path.stat().st_size != src_path.stat().st_size
                    or dest_path.stat().st_mtime < src_path.stat().st_mtime):
                shutil.copy2(src_path, dest_path)
                copied += 1
                total_bytes += src_path.stat().st_size
            else:
                skipped_fresh += 1
        else:
            copied += 1
            total_bytes += src_path.stat().st_size

    verb = "would copy" if args.dry_run else "copied"
    print(f"\n{verb}: {copied} files  ({total_bytes / 1e6:,.1f} MB)")
    if not args.dry_run:
        print(f"already up to date: {skipped_fresh} files")

    if long_paths:
        print(f"\n⚠️  {len(long_paths)} file(s) will exceed the Windows {WIN_MAX_PATH}-char "
              "path limit on AE PCs and may fail to sync. Shorten names/nesting:")
        for win_len, rel in sorted(long_paths, reverse=True)[:15]:
            print(f"   {win_len:>4} chars  {rel}")
    elif args.win_root:
        print(f"\n✅ All paths fit under the Windows {WIN_MAX_PATH}-char limit.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
