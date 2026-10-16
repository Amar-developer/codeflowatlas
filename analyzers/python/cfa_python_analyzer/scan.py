"""Bounded, symlink-safe file enumeration. Files are only listed here, never opened."""

import os
from dataclasses import dataclass, field
from pathlib import Path


MAX_FILES = 2_000
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 50_000_000
IGNORED_DIRS = {".git", ".hg", ".venv", "venv", "env", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache", ".tox"}


@dataclass
class ScanResult:
    python_files: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)


def scan(root: Path) -> ScanResult:
    """List analyzable Python files as repository-relative POSIX paths, and why others were skipped."""
    result = ScanResult()
    total_bytes = 0

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        kept = []
        for name in sorted(dirnames):
            rel = (current / name).relative_to(root).as_posix()
            if (current / name).is_symlink():
                result.skipped.append((rel, "symlink"))
            elif name in IGNORED_DIRS:
                result.skipped.append((rel, "ignored directory"))
            else:
                kept.append(name)
        dirnames[:] = kept

        for name in sorted(filenames):
            path = current / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                result.skipped.append((rel, "symlink"))
                continue
            if path.suffix != ".py":
                result.skipped.append((rel, "unsupported file type"))
                continue
            size = path.stat().st_size
            if size > MAX_FILE_BYTES:
                result.skipped.append((rel, "file too large"))
            elif len(result.python_files) >= MAX_FILES:
                result.skipped.append((rel, "file limit reached"))
            elif total_bytes + size > MAX_TOTAL_BYTES:
                result.skipped.append((rel, "total size limit reached"))
            else:
                total_bytes += size
                result.python_files.append(rel)

    result.python_files.sort()
    result.skipped.sort()
    return result