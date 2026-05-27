"""Project-wide environment loading.

Reads a ``.env`` file from the project root (searched from cwd upward) and
merges its keys into ``os.environ`` **without** overriding existing variables.
A shell ``export`` always wins over the file.

Idempotent — repeated calls are a no-op after the first successful load.
"""

from __future__ import annotations

from dotenv import find_dotenv, load_dotenv

_loaded = False


def load_project_env(*, force: bool = False) -> None:
    """Populate ``os.environ`` from a project ``.env``, once per process."""
    global _loaded
    if _loaded and not force:
        return
    path = find_dotenv(usecwd=True)
    if path:
        load_dotenv(path, override=False)
    _loaded = True
