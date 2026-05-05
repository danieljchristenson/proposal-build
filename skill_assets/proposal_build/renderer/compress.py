"""Optional ghostscript-based PDF compression.

Used when the CLI is invoked with --compress so the FINAL deliverable
ships in one command instead of a manual gs post-step. Targets the
/ebook profile, which keeps text crisp and downsamples images to
roughly 150 dpi — typical 60-80% size reduction on image-heavy decks
without visible quality loss at proposal viewing scales.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class CompressionUnavailableError(RuntimeError):
    """Raised when ghostscript is requested but not on PATH."""


def compress_pdf_in_place(path: Path) -> int:
    """Compress `path` with gs /ebook, atomically replacing the original.

    Returns the new file size in bytes. Raises CompressionUnavailableError
    if gs isn't on PATH and CalledProcessError if gs exits non-zero.
    """
    gs = shutil.which("gs")
    if not gs:
        raise CompressionUnavailableError(
            "ghostscript not found. Install with `brew install ghostscript` "
            "or rerun without --compress."
        )
    tmp = path.with_suffix(path.suffix + ".compress.tmp")
    subprocess.run(
        [gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
         "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
         f"-sOutputFile={tmp}", str(path)],
        check=True,
    )
    tmp.replace(path)
    return path.stat().st_size
