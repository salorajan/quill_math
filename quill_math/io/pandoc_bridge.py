"""Pandoc document conversion bridge."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class PandocUnavailableError(Exception):
    """Raised when Pandoc binary is not found on PATH."""


class PandocConversionError(Exception):
    """Raised when Pandoc subprocess exits with a non-zero code."""


def is_pandoc_available() -> bool:
    """Return True if pandoc executable exists."""
    return shutil.which("pandoc") is not None


def convert_file_with_pandoc(
    source: Path,
    target: Path,
    *,
    from_format: str = "gfm",
    to_format: str = "docx",
) -> None:
    """Run pandoc to convert *source* to *target*."""
    if not is_pandoc_available():
        raise PandocUnavailableError("pandoc executable not found on system PATH.")

    cmd = [
        "pandoc",
        "-f",
        from_format,
        "-t",
        to_format,
        "-o",
        str(target),
        str(source),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise PandocConversionError(f"Pandoc failed: {proc.stderr}")
    except OSError as exc:
        raise PandocUnavailableError(f"Could not execute pandoc: {exc}") from exc
