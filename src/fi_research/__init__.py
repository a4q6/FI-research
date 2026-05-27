"""FI-research: fixed income research utilities (public data only)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fi-research")
except PackageNotFoundError:
    __version__ = "0.0.0+local"

__all__ = ["__version__"]
