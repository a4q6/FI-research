"""Replication of Houweling & van Zundert (2017, FAJ).

"Factor Investing in the Corporate Bond Market", Financial Analysts Journal 73(2):100-115.

Replication scope:
- Table 3 (single-factor long-only portfolios, IG and HY): annualized mean
  excess return, vol, information ratio (IR), and t-statistic.
- Multi-factor portfolio descriptive statistics.
- Pairwise correlation matrix of factor returns.
- Cumulative excess return chart.

Data: ``fi_research.data.robeco`` — monthly excess returns over
duration-matched Treasuries (decimal units). Robeco publishes the post-paper
updated time series, so we report both the paper's sample (1994-01 to
2015-09) and the full available sample.

Outputs are written to ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fi_research.data.robeco import load_robeco_credit_factors

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FACTORS = ["Size", "LowRisk", "Value", "Momentum", "MultiFactor"]
PAPER_SAMPLE = ("1994-01-31", "2015-09-30")
FULL_SAMPLE_END = "2025-12-31"


def annualized_stats(series: pd.Series) -> dict[str, float]:
    """Return annualized mean, vol, IR, and t-stat for a monthly excess return."""
    mu_m = series.mean()
    sd_m = series.std(ddof=1)
    n = series.notna().sum()
    return {
        "mean_ann": mu_m * 12.0,
        "vol_ann": sd_m * np.sqrt(12.0),
        "IR": (mu_m / sd_m) * np.sqrt(12.0) if sd_m > 0 else np.nan,
        "t_stat": (mu_m / sd_m) * np.sqrt(n) if sd_m > 0 else np.nan,
        "n_months": int(n),
    }


def stats_table(df: pd.DataFrame, factors: list[str]) -> pd.DataFrame:
    rows = {f: annualized_stats(df[f]) for f in factors}
    return pd.DataFrame(rows).T


def main() -> None:
    ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
    hy = load_robeco_credit_factors("HY").set_index("date").sort_index()

    # --- Table 3-style descriptive stats for both samples ---
    out_tables: dict[str, pd.DataFrame] = {}
    for label, frame in [("IG", ig), ("HY", hy)]:
        paper = frame.loc[PAPER_SAMPLE[0] : PAPER_SAMPLE[1]]
        full = frame.loc[: FULL_SAMPLE_END]
        out_tables[f"{label}_paper_1994_2015"] = stats_table(paper, FACTORS)
        out_tables[f"{label}_full_1994_2025"] = stats_table(full, FACTORS)

    # Print all tables (for log)
    for name, tab in out_tables.items():
        print(f"\n=== {name} ===")
        print(tab.round(4).to_string())
        tab.to_csv(RESULTS_DIR / f"table3_{name}.csv")

    # --- Correlation matrix (single factors only, full sample) ---
    single = [f for f in FACTORS if f != "MultiFactor"]
    for label, frame in [("IG", ig), ("HY", hy)]:
        corr = frame[single].corr()
        print(f"\n=== Correlation ({label}, full sample) ===")
        print(corr.round(3).to_string())
        corr.to_csv(RESULTS_DIR / f"corr_{label}_full.csv")

    # --- Cumulative excess return charts ---
    for label, frame in [("IG", ig), ("HY", hy)]:
        cum = (1 + frame[FACTORS]).cumprod() - 1
        fig, ax = plt.subplots(figsize=(9, 5))
        cum.plot(ax=ax, linewidth=1.4)
        ax.set_title(
            f"Robeco {label} factor portfolios — cumulative excess return "
            f"({frame.index.min():%Y-%m} to {frame.index.max():%Y-%m})"
        )
        ax.set_ylabel("Cumulative return (excess over duration-matched Treasury)")
        ax.axhline(0, color="k", linewidth=0.6)
        ax.grid(alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f"cumret_{label}.png", dpi=130)
        plt.close(fig)

    # --- Save merged monthly panel for downstream use ---
    merged = (
        ig.add_prefix("IG_")
        .join(hy.add_prefix("HY_"), how="outer")
        .sort_index()
    )
    merged.to_parquet(RESULTS_DIR / "robeco_panel.parquet")

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
