"""Filesystem paths used across the project.

Resolves relative to the repo root rather than the current working directory,
so notebooks and scripts can import them regardless of where they are invoked.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = REPO_ROOT / "data"
DATA_RAW: Path = DATA_DIR / "raw"
DATA_PROCESSED: Path = DATA_DIR / "processed"
DOCS_DIR: Path = REPO_ROOT / "docs"


def ensure_dir(path: Path) -> Path:
    """Create ``path`` (and parents) if missing, return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
