"""Bulk-fetch JSDA month-end snapshots.

Run from your **local machine** (not from a sandbox / CI runner — JSDA
rate-limits aggressively by IP and the sandbox IP got blocked during
development).

Usage:
    cd /path/to/FI-research
    pip install -e .              # if not already

    # 売買参考統計値 (~12k bonds/day, 1.8-2.2 MB/file)
    python scripts/fetch_jsda.py --kind S --start 2020 --end 2025 --sleep 3

    # 格付マトリクス表 (rating × maturity bucket yields, small files)
    python scripts/fetch_jsda.py --kind R --start 2020 --end 2025 --sleep 2

    # Both kinds in one invocation
    python scripts/fetch_jsda.py --kind both --start 2020 --end 2025

The script is resumable: already-downloaded daily CSVs are reused, so you
can stop with Ctrl+C and re-run.

After the daily CSVs are cached, the concatenated parquet is written to:
    data/processed/jsda_monthend_{start}_{end}.parquet         (S-file)
    data/processed/jsda_matrix_monthend_{start}_{end}.parquet  (R-file)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from fi_research.data.jsda import find_month_end_file
from fi_research.paths import DATA_PROCESSED, ensure_dir


def fetch_kind(
    kind: str,
    start: int,
    end: int,
    sleep: float,
    max_back: int,
) -> int:
    """Fetch all month-ends for one kind. Returns 0 on success, 1 on total failure."""
    n_months_total = (end - start + 1) * 12
    print(f"\n=== Fetching {n_months_total} month-end snapshots, kind={kind} "
          f"({start}-{end}) ===")
    print(f"Sleep between requests: {sleep}s, max-back: {max_back} days\n")

    frames: list[pd.DataFrame] = []
    misses: list[tuple[int, int]] = []
    n_done = 0

    for year in range(start, end + 1):
        for month in range(1, 13):
            n_done += 1
            try:
                actual, res = find_month_end_file(
                    year, month, kind=kind, sleep_after=sleep, max_days_back=max_back
                )
            except Exception as e:
                print(f"[{n_done:3d}/{n_months_total}] {year}-{month:02d} EXCEPTION: {e}",
                      flush=True)
                misses.append((year, month))
                continue
            if res is None:
                print(f"[{n_done:3d}/{n_months_total}] {year}-{month:02d} no file found",
                      flush=True)
                misses.append((year, month))
                continue
            print(
                f"[{n_done:3d}/{n_months_total}] {year}-{month:02d} {actual} — "
                f"{len(res.df):,} rows",
                flush=True,
            )
            frames.append(res.df)

    if not frames:
        print(f"\nERROR: no {kind}-snapshots fetched. Check network connectivity to "
              "market.jsda.or.jp.", file=sys.stderr)
        return 1

    out = pd.concat(frames, ignore_index=True)
    proc_dir = ensure_dir(DATA_PROCESSED)
    suffix = "monthend" if kind == "S" else "matrix_monthend"
    proc_path = proc_dir / f"jsda_{suffix}_{start}_{end}.parquet"
    out.to_parquet(proc_path, index=False)

    print(f"\n[OK] Saved {proc_path}")
    print(f"    {out.shape[0]:,} rows x {out.shape[1]} cols")
    print(f"    Date range: {out['date'].dropna().min().date()} ~ "
          f"{out['date'].dropna().max().date()}")
    print(f"    Months covered: {out['date'].dt.to_period('M').nunique()}")
    if misses:
        print(f"\n[!] Missing months ({len(misses)}):")
        for y, m in misses:
            print(f"    {y}-{m:02d}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="JSDA month-end bulk fetcher")
    parser.add_argument("--kind", choices=["S", "R", "both"], default="S",
                        help="S=売買参考統計値 (default), R=格付マトリクス表, both=両方")
    parser.add_argument("--start", type=int, default=2020, help="start year (default 2020)")
    parser.add_argument("--end", type=int, default=2025, help="end year (default 2025)")
    parser.add_argument("--sleep", type=float, default=3.0,
                        help="seconds between requests (default 3, increase if throttled)")
    parser.add_argument("--max-back", type=int, default=10,
                        help="days to walk back from month-end (default 10)")
    args = parser.parse_args()

    kinds = ["S", "R"] if args.kind == "both" else [args.kind]
    rc = 0
    for k in kinds:
        rc |= fetch_kind(k, args.start, args.end, args.sleep, args.max_back)
    return rc


if __name__ == "__main__":
    sys.exit(main())
