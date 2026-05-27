"""Auto layer: read facts straight from parquet footers.

Everything here is derived from the files on disk so it is always current. We
deliberately avoid loading row data: schema and row counts come from the parquet
footer, and date coverage is taken from per-row-group column statistics (with a
cheap single-column read as a fallback). This keeps introspection fast even for
the multi-GB EDGAR ``num`` tables.
"""

from __future__ import annotations

import glob
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow.parquet as pq

from fi_research.paths import DATA_PROCESSED


@dataclass
class Column:
    name: str
    dtype: str


@dataclass
class Member:
    """One physical file inside a logical dataset (e.g. one FRED series, one
    CFTC year, one EDGAR quarter)."""

    name: str
    rows: int
    size_bytes: int
    date_min: str | None = None
    date_max: str | None = None


@dataclass
class DatasetAuto:
    n_files: int
    rows: int
    size_bytes: int
    columns: list[Column]
    homogeneous: bool
    date_col: str | None = None
    date_min: str | None = None
    date_max: str | None = None
    members: list[Member] = field(default_factory=list)
    missing: bool = False  # declared in YAML but no files matched


_DATE_COL_CANDIDATES = ("date", "as_of_date", "report_date", "ddate", "period")


def resolve_files(patterns: list[str]) -> list[Path]:
    """Resolve YAML ``files`` entries (globs, relative to ``data/processed``)."""
    out: list[Path] = []
    for pat in patterns:
        matches = sorted(DATA_PROCESSED.glob(pat))
        out.extend(matches)
    # de-dup while preserving order
    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _columns(pf: pq.ParquetFile) -> list[Column]:
    return [Column(f.name, str(f.type)) for f in pf.schema_arrow]


def _pick_date_col(columns: list[Column], hint: str | None) -> str | None:
    names = {c.name for c in columns}
    if hint and hint in names:
        return hint
    for cand in _DATE_COL_CANDIDATES:
        if cand in names:
            return cand
    return None


def _coverage(path: Path, date_col: str) -> tuple[str | None, str | None]:
    """Return (min, max) ISO date for ``date_col`` without loading row data when
    statistics are available; otherwise project just that column."""
    try:
        pf = pq.ParquetFile(path)
        col_idx = pf.schema_arrow.get_field_index(date_col)
        if col_idx < 0:
            return None, None
        lo = hi = None
        meta = pf.metadata
        have_stats = True
        for rg in range(meta.num_row_groups):
            stats = meta.row_group(rg).column(col_idx).statistics
            if stats is None or not stats.has_min_max:
                have_stats = False
                break
            mn, mx = stats.min, stats.max
            lo = mn if lo is None or mn < lo else lo
            hi = mx if hi is None or mx > hi else hi
        if have_stats and lo is not None:
            return _iso(lo), _iso(hi)
        # fallback: read only the date column
        tbl = pf.read(columns=[date_col])
        arr = tbl.column(0).drop_null()
        if len(arr) == 0:
            return None, None
        import pyarrow.compute as pc

        return _iso(pc.min(arr).as_py()), _iso(pc.max(arr).as_py())
    except Exception:
        return None, None


def _iso(v) -> str | None:
    if v is None:
        return None
    try:
        return v.date().isoformat()  # datetime/Timestamp
    except AttributeError:
        return str(v)


def _stem(path: Path, dataset_key: str) -> str:
    """Short member label: filename minus a leading ``<key>_`` prefix."""
    stem = path.stem
    for pre in (dataset_key + "_", "fred_", "kf_", "cftc_tff_", "mp_shocks_"):
        if stem.startswith(pre):
            return stem[len(pre) :]
    return stem


def introspect_dataset(
    key: str,
    patterns: list[str],
    date_col_hint: str | None = None,
    coverage: bool = True,
    representative: str | None = None,
) -> DatasetAuto:
    """Introspect every file matched by ``patterns`` and aggregate.

    ``representative`` optionally names a file (glob) whose schema is shown when
    the dataset's files are heterogeneous (e.g. EDGAR: show a recent quarter).
    """
    files = resolve_files(patterns)
    if not files:
        return DatasetAuto(0, 0, 0, [], True, missing=True)

    total_rows = 0
    total_size = 0
    members: list[Member] = []
    schemas: list[tuple[str, ...]] = []
    per_file_cols: dict[Path, list[Column]] = {}

    for path in files:
        pf = pq.ParquetFile(path)
        cols = _columns(pf)
        per_file_cols[path] = cols
        rows = pf.metadata.num_rows
        size = path.stat().st_size
        total_rows += rows
        total_size += size
        schemas.append(tuple(c.name for c in cols))
        dcol = _pick_date_col(cols, date_col_hint)
        dmin = dmax = None
        if coverage and dcol is not None:
            dmin, dmax = _coverage(path, dcol)
        members.append(Member(_stem(path, key), rows, size, dmin, dmax))

    homogeneous = len(set(schemas)) == 1

    # representative schema
    rep_path = files[0]
    if representative:
        reps = resolve_files([representative])
        if reps:
            rep_path = reps[0]
    columns = per_file_cols[rep_path]

    # dataset-level coverage = span across members
    date_col = _pick_date_col(columns, date_col_hint)
    dmins = [m.date_min for m in members if m.date_min]
    dmaxs = [m.date_max for m in members if m.date_max]
    date_min = min(dmins) if dmins else None
    date_max = max(dmaxs) if dmaxs else None

    return DatasetAuto(
        n_files=len(files),
        rows=total_rows,
        size_bytes=total_size,
        columns=columns,
        homogeneous=homogeneous,
        date_col=date_col,
        date_min=date_min,
        date_max=date_max,
        members=members,
    )


def all_processed_files() -> list[Path]:
    """Every parquet under ``data/processed`` (recursive), for orphan detection."""
    return sorted(Path(p) for p in glob.glob(str(DATA_PROCESSED / "**" / "*.parquet"), recursive=True))
