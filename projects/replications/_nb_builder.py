"""Tiny helper to build .ipynb files programmatically.

Usage:
    from _nb_builder import build_notebook
    cells = [
        ("markdown", "# Title"),
        ("code", "import pandas as pd\\nprint('hi')"),
    ]
    build_notebook(cells, "out.ipynb")

Notebooks are saved without executed output. Run via:
    jupyter nbconvert --to notebook --execute --inplace out.ipynb
"""

from __future__ import annotations

import json
from pathlib import Path


def _cell(cell_type: str, source: str) -> dict:
    lines = source.splitlines(keepends=True)
    if cell_type == "code":
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": lines,
        }
    return {"cell_type": cell_type, "metadata": {}, "source": lines}


def build_notebook(cells: list[tuple[str, str]], out_path: str | Path) -> Path:
    nb = {
        "cells": [_cell(t, s) for t, s in cells],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1))
    return out
