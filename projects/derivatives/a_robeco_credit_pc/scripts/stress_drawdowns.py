"""Bundle A.2 — Stress period drawdowns of Robeco credit factors.

For each of three stress episodes:
- **GFC**: 2007-07 → 2009-12
- **COVID**: 2020-02 → 2020-12
- **2022 inflation / rate shock**: 2022-01 → 2022-12

Compute, for each Robeco factor (IG and HY × Size, Low-Risk, Value, Momentum,
MultiFactor):
- Maximum drawdown (peak-to-trough on cumulative excess return)
- Underwater duration in months
- Recovery date and months to recover full DD
- Downside semi-deviation (Sortino ratio numerator)
- Sortino ratio (annualized)
- Cumulative excess return over the window

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fi_research.data.fred import load_panel
from fi_research.data.robeco import load_robeco_credit_factors

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FACTORS = ["Size", "LowRisk", "Value", "Momentum", "MultiFactor"]
STRESS_PERIODS = {
    "GFC_2007_2009": ("2007-07-01", "2009-12-31"),
    "COVID_2020": ("2020-02-01", "2020-12-31"),
    "Inflation_2022": ("2022-01-01", "2022-12-31"),
}


def max_drawdown_metrics(series: pd.Series) -> dict[str, float | pd.Timestamp]:
    """Compute max drawdown stats from a monthly excess return series.

    cumret = (1+r).cumprod() - 1  -> use wealth W = (1+r).cumprod()
    DD_t = W_t / max(W_{s<=t}) - 1
    """
    if series.dropna().empty:
        return {
            "max_dd": np.nan,
            "peak_date": pd.NaT,
            "trough_date": pd.NaT,
            "underwater_months": np.nan,
            "recovery_date": pd.NaT,
            "months_to_recover": np.nan,
            "cum_ret": np.nan,
            "downside_dev_ann": np.nan,
            "sortino_ann": np.nan,
        }
    s = series.dropna()
    W = (1.0 + s).cumprod()
    running_peak = W.cummax()
    DD = W / running_peak - 1.0
    trough_idx = DD.idxmin()
    max_dd_val = DD.loc[trough_idx]
    peak_W = running_peak.loc[trough_idx]
    # Identify peak date as the first month achieving peak_W on or before trough
    peak_candidates = W.loc[:trough_idx][W.loc[:trough_idx] == peak_W]
    peak_date = peak_candidates.index[0] if len(peak_candidates) else pd.NaT
    underwater_months = (trough_idx.year - peak_date.year) * 12 + (
        trough_idx.month - peak_date.month
    )
    # Recovery
    post = W.loc[trough_idx:]
    rec = post[post >= peak_W]
    if len(rec):
        recovery_date = rec.index[0]
        months_to_rec = (recovery_date.year - trough_idx.year) * 12 + (
            recovery_date.month - trough_idx.month
        )
    else:
        recovery_date = pd.NaT
        months_to_rec = np.nan

    # Downside deviation (only negative returns)
    neg = s[s < 0]
    if len(neg) > 1:
        ddev = float(np.sqrt(np.mean(neg**2))) * np.sqrt(12.0)
    else:
        ddev = np.nan
    mean_ann = s.mean() * 12.0
    sortino = mean_ann / ddev if (ddev and ddev > 0) else np.nan

    cum_ret = float(W.iloc[-1] - 1.0)
    return {
        "max_dd": float(max_dd_val),
        "peak_date": peak_date,
        "trough_date": trough_idx,
        "underwater_months": int(underwater_months) if pd.notna(peak_date) else np.nan,
        "recovery_date": recovery_date,
        "months_to_recover": float(months_to_rec) if pd.notna(months_to_rec) else np.nan,
        "cum_ret": cum_ret,
        "downside_dev_ann": ddev,
        "sortino_ann": sortino,
    }


def build_credit_benchmark() -> pd.Series:
    """Monthly IG credit proxy return: −duration × Δ BAA10Y (decimal)."""
    fred = load_panel(["BAA10Y"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index()
    monthly = fred["BAA10Y"].resample("M").last() / 100.0
    return (-7.0 * monthly.diff()).rename("BAA10Y_excess_proxy")


def main() -> None:
    ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
    hy = load_robeco_credit_factors("HY").set_index("date").sort_index()
    bench = build_credit_benchmark()

    rows = []
    for market_label, df in [("IG", ig), ("HY", hy)]:
        for period_name, (start, end) in STRESS_PERIODS.items():
            print(f"\n=== {market_label} | {period_name} ({start} ~ {end}) ===")
            for f in FACTORS + ["BENCH_BAA10Y_excess"]:
                if f == "BENCH_BAA10Y_excess":
                    series = bench.loc[start:end]
                else:
                    series = df.loc[start:end, f]
                metrics = max_drawdown_metrics(series)
                rows.append(
                    {
                        "market": market_label,
                        "stress": period_name,
                        "factor": f,
                        **metrics,
                    }
                )
                if metrics["max_dd"] is not None and pd.notna(metrics["max_dd"]):
                    rec_str = (
                        "N/A" if pd.isna(metrics["months_to_recover"])
                        else f"{int(metrics['months_to_recover'])}m"
                    )
                    print(
                        f"  {f:25s} MaxDD={metrics['max_dd']*100:+6.2f}%  "
                        f"Trough={metrics['trough_date']:%Y-%m}  "
                        f"UW={metrics['underwater_months']}m  "
                        f"Rec={rec_str}  "
                        f"CumRet={metrics['cum_ret']*100:+6.2f}%  "
                        f"Sortino={metrics['sortino_ann']:+.2f}"
                    )

    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS_DIR / "stress_drawdowns.csv", index=False)

    # === Plot: cumulative excess return per market × stress period ===
    for market_label, df in [("IG", ig), ("HY", hy)]:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
        for ax, (period_name, (start, end)) in zip(axes, STRESS_PERIODS.items()):
            sub = df.loc[start:end]
            bench_sub = bench.loc[start:end]
            for f in FACTORS:
                cum = (1 + sub[f]).cumprod() - 1
                ax.plot(cum.index, cum.values * 100, label=f, linewidth=1.3)
            cum_b = (1 + bench_sub).cumprod() - 1
            ax.plot(cum_b.index, cum_b.values * 100, label="−7·ΔBAA10Y proxy", linewidth=1.0, linestyle="--", color="grey")
            ax.axhline(0, color="k", linewidth=0.4)
            ax.set_title(f"{market_label} — {period_name}")
            ax.set_ylabel("Cumulative excess return (%)")
            ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax.tick_params(axis="x", rotation=30)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=7, loc="lower left")
        fig.suptitle(
            f"Robeco {market_label} factor cumulative excess return — three stress episodes",
            y=1.01,
        )
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f"stress_cumret_{market_label}.png", dpi=130, bbox_inches="tight")
        plt.close(fig)

    # === Max DD heatmap (markets × stresses × factors) ===
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for ax, market_label in zip(axes, ["IG", "HY"]):
        sub = summary[(summary["market"] == market_label) & (summary["factor"].isin(FACTORS))]
        pivot = sub.pivot_table(index="factor", columns="stress", values="max_dd") * 100
        # Order rows
        pivot = pivot.loc[FACTORS]
        im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=-25, vmax=0, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=20)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        for i, row in enumerate(pivot.values):
            for j, val in enumerate(row):
                ax.text(j, i, f"{val:+.1f}%", ha="center", va="center", fontsize=10,
                        color="black")
        ax.set_title(f"Robeco {market_label} — Max Drawdown")
    fig.colorbar(im, ax=axes, label="Max DD (%)", fraction=0.025)
    fig.suptitle("Stress period max drawdowns by factor", y=1.02)
    fig.savefig(RESULTS_DIR / "max_dd_heatmap.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
