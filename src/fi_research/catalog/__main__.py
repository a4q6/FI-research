"""``python -m fi_research.catalog build`` -> regenerate HTML + Markdown.

Usage::

    python -m fi_research.catalog build      # write both outputs
    python -m fi_research.catalog check       # build model, print diagnostics only
"""

from __future__ import annotations

import sys

from fi_research.catalog.meta import build_catalog
from fi_research.catalog.render import render_html, render_markdown
from fi_research.paths import DOCS_DIR, ensure_dir

HTML_OUT = DOCS_DIR / "catalog" / "data_catalog.html"
MD_OUT = DOCS_DIR / "data_catalog.md"


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "build"
    model = build_catalog()

    t = model["totals"]
    print(f"datasets={t['datasets']} files={t['files']} rows={t['rows']:,} size={t['size']}")
    if model["todos"]:
        print(f"\n⚠ diagnostics ({len(model['todos'])}):")
        for todo in model["todos"]:
            print(f"  - {todo}")
    else:
        print("✓ no drift detected")

    if cmd == "check":
        return 0
    if cmd != "build":
        print(f"unknown command: {cmd!r} (use 'build' or 'check')", file=sys.stderr)
        return 2

    ensure_dir(HTML_OUT.parent)
    HTML_OUT.write_text(render_html(model), encoding="utf-8")
    MD_OUT.write_text(render_markdown(model), encoding="utf-8")
    print(f"\nwrote {HTML_OUT.relative_to(DOCS_DIR.parent)}")
    print(f"wrote {MD_OUT.relative_to(DOCS_DIR.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
