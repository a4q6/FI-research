"""Curated layer + merge.

Loads ``docs/catalog/catalog_meta.yaml``, introspects each declared dataset and
merges the two into a plain-dict model ready to be embedded as JSON. Also reports
drift: parquet files on disk that no dataset claims (orphans) and curated tables
whose columns lack definitions.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path

import yaml

from fi_research.catalog import introspect
from fi_research.paths import DOCS_DIR

META_PATH = DOCS_DIR / "catalog" / "catalog_meta.yaml"


# --- column-definition pattern expansion ------------------------------------
# Keys in the YAML may compress column families, e.g. ``SVENY{01..30}`` (numeric
# range, zero-padded), ``SVEN1F{01,04,09}`` (list), ``BETA0..BETA3`` (bare range)
# or ``<industry>`` (wildcard). We expand these so each physical column can be
# matched to its definition.


def _expand_defs(defs: dict[str, str]) -> tuple[dict[str, str], list[tuple[re.Pattern, str]]]:
    exact: dict[str, str] = {}
    wild: list[tuple[re.Pattern, str]] = []
    for key, val in (defs or {}).items():
        for sub in _split_top(key):
            _add_one(sub, val, exact, wild)
    return exact, wild


def _split_top(key: str) -> list[str]:
    """Split a comma list of column names, but not commas inside ``{...}``."""
    parts: list[str] = []
    depth = 0
    buf = ""
    for ch in key:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts or [key]


def _add_one(sub: str, val: str, exact: dict[str, str], wild: list[tuple[re.Pattern, str]]) -> None:
    if "<" in sub or "*" in sub:  # wildcard: "<industry>" / "Asset_Mgr_Positions_*"
        rx = re.escape(sub)
        rx = rx.replace(r"\*", ".*")
        rx = re.sub(r"<[^>]+>", ".+", rx.replace(r"\<", "<").replace(r"\>", ">"))
        wild.append((re.compile(f"^{rx}$"), val))
        return
    names = _expand_key(sub)
    if names is None:
        exact[sub] = val
    else:
        for n in names:
            exact.setdefault(n, val)


def _expand_key(key: str) -> list[str] | None:
    # bare range: "BETA0..BETA3" (repeated prefix, numeric tail)
    m = re.match(r"^(.*?)(\d+)\.\.(.*?)(\d+)$", key)
    if m and "{" not in key and m.group(1) == m.group(3):
        prefix, a, _, b = m.groups()
        width = len(a)
        return [f"{prefix}{i:0{width}d}" for i in range(int(a), int(b) + 1)]
    # brace group: "<pre>{...}<post>"
    bm = re.match(r"^(.*?)\{([^}]+)\}(.*)$", key)
    if bm:
        pre, body, post = bm.groups()
        items: list[str] = []
        if ".." in body:  # numeric range "01..30"
            lo, hi = body.split("..")
            width = len(lo)
            items = [f"{i:0{width}d}" for i in range(int(lo), int(hi) + 1)]
        else:  # comma list "01,04,09" or "Long,Short,Spread"
            items = [x.strip() for x in body.split(",")]
        return [f"{pre}{it}{post}" for it in items]
    return None


def _match_def(col: str, exact: dict[str, str], wild: list[tuple[re.Pattern, str]]) -> str | None:
    if col in exact:
        return exact[col]
    for rx, val in wild:
        if rx.match(col):
            return val
    return None


# --- merge -------------------------------------------------------------------


def _fmt_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    f = float(n)
    for u in units:
        if f < 1024 or u == units[-1]:
            return f"{f:.0f} {u}" if u == "B" else f"{f:.1f} {u}"
        f /= 1024
    return f"{n} B"


def build_catalog() -> dict:
    """Return the merged catalog model + diagnostics."""
    raw = yaml.safe_load(META_PATH.read_text(encoding="utf-8"))
    meta = raw.get("meta", {})
    categories = raw.get("categories", [])
    dataset_specs = raw.get("datasets", [])

    claimed: set[Path] = set()
    datasets: list[dict] = []
    todos: list[str] = []

    for spec in dataset_specs:
        key = spec["key"]
        patterns = spec.get("files", [])
        auto = introspect.introspect_dataset(
            key,
            patterns,
            date_col_hint=spec.get("date_col"),
            coverage=spec.get("coverage", True),
            representative=spec.get("representative"),
        )
        for p in introspect.resolve_files(patterns):
            claimed.add(p.resolve())

        if auto.missing:
            todos.append(f"[no files] dataset '{key}' declared but no parquet matched {patterns}")

        # merge column definitions onto the introspected schema
        exact, wild = _expand_defs(spec.get("columns", {}))
        cols = []
        undocumented = 0
        for c in auto.columns:
            defn = _match_def(c.name, exact, wild)
            if defn is None:
                undocumented += 1
            cols.append({"name": c.name, "dtype": c.dtype, "definition": defn})
        documented_ratio = (
            (len(cols) - undocumented) / len(cols) if cols else 1.0
        )
        if spec.get("columns") and undocumented:
            todos.append(f"[cols] '{key}': {undocumented}/{len(cols)} columns undocumented")
        if not spec.get("columns") and cols:
            todos.append(f"[cols] '{key}': no column definitions yet ({len(cols)} columns)")

        members = [
            {
                "name": m.name,
                "rows": m.rows,
                "size": _fmt_size(m.size_bytes),
                "start": m.date_min,
                "end": m.date_max,
            }
            for m in auto.members
        ]

        datasets.append(
            {
                "key": key,
                "title": spec.get("title", key),
                "category": spec.get("category", "Other"),
                "provider": spec.get("provider"),
                "loader": spec.get("loader"),
                "frequency": spec.get("frequency"),
                "upstream_url": spec.get("upstream_url"),
                "citation": spec.get("citation"),
                "license": spec.get("license"),
                "caveats": spec.get("caveats", []),
                "usage": spec.get("usage", {}),
                "relations": spec.get("relations", []),
                "members_note": spec.get("members_note"),
                # auto
                "n_files": auto.n_files,
                "rows": auto.rows,
                "size_bytes": auto.size_bytes,
                "size": _fmt_size(auto.size_bytes),
                "homogeneous": auto.homogeneous,
                "date_col": auto.date_col,
                "start": auto.date_min,
                "end": auto.date_max,
                "columns": cols,
                "n_columns": len(cols),
                "documented_ratio": round(documented_ratio, 2),
                "members": members,
                "missing": auto.missing,
            }
        )

    # orphan detection: parquet on disk not claimed by any dataset
    orphans = []
    for p in introspect.all_processed_files():
        if p.resolve() not in claimed:
            orphans.append(p.name)
    if orphans:
        todos.append(f"[orphan] {len(orphans)} parquet not in any dataset: {', '.join(sorted(orphans)[:8])}{' …' if len(orphans) > 8 else ''}")

    totals = {
        "datasets": len(datasets),
        "files": sum(d["n_files"] for d in datasets),
        "rows": sum(d["rows"] for d in datasets),
        "size": _fmt_size(sum(d["size_bytes"] for d in datasets)),
    }

    return {
        "meta": meta,
        "categories": categories,
        "datasets": datasets,
        "pending": raw.get("pending", []),
        "totals": totals,
        "orphans": sorted(orphans),
        "todos": todos,
    }
