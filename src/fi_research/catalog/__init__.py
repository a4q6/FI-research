"""Data catalog generator.

Two layers, merged at build time so the rendered catalog never drifts from the
parquet files on disk:

- **Auto layer** (:mod:`introspect`): schema, row counts, date coverage and file
  sizes read straight from the parquet footers (fast, always current).
- **Curated layer** (``docs/catalog/catalog_meta.yaml``, loaded by :mod:`meta`):
  provider, frequency, citation, license caveats, A1/A2 usage, column definitions
  and cross-dataset relations -- the knowledge that cannot be introspected.

:mod:`render` joins the two into a single self-contained interactive HTML page
and a regenerated ``docs/data_catalog.md``.

Rebuild with::

    python -m fi_research.catalog build
"""

from fi_research.catalog.meta import build_catalog
from fi_research.catalog.render import render_html, render_markdown

__all__ = ["build_catalog", "render_html", "render_markdown"]
