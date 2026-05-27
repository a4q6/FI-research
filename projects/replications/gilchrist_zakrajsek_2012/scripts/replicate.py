"""Replication of Gilchrist & Zakrajšek (2012, AER).

"Credit Spreads and Business Cycle Fluctuations." American Economic Review,
102(4), 1692-1720.

Replication scope:
- Time series of GZ spread, EBP, and estimated default probability (Figures 1-3).
- Table 1-style predictive regressions of real activity (Δlog IP, Δlog
  payroll, unemployment rate change) on EBP at horizons h = 3, 6, 12, 24
  months, with controls: term spread (T10Y3M), real fed funds rate
  (DFF − 12m CPI inflation).
- EBP behavior around NBER recessions (Figure 5-style).

Data:
- ``fi_research.data.frb_ebp.load_ebp`` (EBP, GZ spread, est_prob) — Favara,
  Gilchrist, Lewis, Zakrajšek (2016) FEDS Note update of GZ (2012).
- ``fi_research.data.fred`` for IP, payroll, UR, T10Y3M, DFF, CPIAUCSL, USREC.

The firm-level construction of EBP (from corporate bond TRACE + Compustat)
is intentionally NOT replicated — we use the published FRB series.

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.frb_ebp import load_ebp
from fi_research.data.fred import load_panel

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FRED_SERIES = [
    "INDPRO",      # industrial production
    "PAYEMS",      # nonfarm payrolls
    "UNRATE",      # unemployment rate
    "T10Y3M",      # term spread
    "DFF",         # fed funds (daily, will average to monthly)
    "CPIAUCSL",    # CPI all urban
    "USREC",       # NBER recession dummy
]
SAMPLES = {
    "paper_1973_2010": ("1973-01-01", "2010-12-31"),
    "post_paper_2011_2025": ("2011-01-01", "2025-12-31"),
    "full_1973_2025": ("1973-01-01", "2025-12-31"),
}
HORIZONS = [3, 6, 12, 24]


def build_monthly_panel() -> pd.DataFrame:
    ebp = load_ebp().set_index("date").sort_index()
    # FRED panel
    fred = load_panel(FRED_SERIES)
    # Some series are daily, some monthly. Normalize to month-end.
    fred = fred.set_index("date") if "date" in fred.columns else fred
    fred.index = pd.to_datetime(fred.index)
    fred_m = fred.resample("M").mean()  # average daily → month
    ebp.index = pd.to_datetime(ebp.index)
    ebp_m = ebp.resample("M").last()    # EBP is already monthly, ensure month-end stamp

    # Compute real fed funds: DFF − YoY CPI inflation
    fred_m["cpi_yoy"] = 100 * (fred_m["CPIAUCSL"] / fred_m["CPIAUCSL"].shift(12) - 1)
    fred_m["real_ff"] = fred_m["DFF"] - fred_m["cpi_yoy"]

    # Compute monthly Δlog IP, Δlog payroll, ΔUR
    fred_m["dlog_indpro"] = np.log(fred_m["INDPRO"]).diff() * 100
    fred_m["dlog_payems"] = np.log(fred_m["PAYEMS"]).diff() * 100
    fred_m["dur"] = fred_m["UNRATE"].diff()

    panel = ebp_m.join(fred_m, how="outer")
    panel = panel.sort_index()
    return panel


def predictive_regression(
    panel: pd.DataFrame,
    target: str,
    horizon: int,
    sample: tuple[str, str],
    controls: list[str] = ["T10Y3M", "real_ff"],
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Run `target_{t+h_cum} ~ ebp_t + controls_t`.

    target_{t+h_cum} = average of target over months t+1, ..., t+h.
    Equivalent to sum/h. For Δlog series this is the average monthly growth
    rate; multiply by h for cumulative growth.
    """
    start, end = sample
    df = panel.loc[start:end].copy()

    # cumulative h-month change
    if target == "dur":
        # UR: cumulative change = UR_{t+h} - UR_t
        df["y"] = df["UNRATE"].shift(-horizon) - df["UNRATE"]
    else:
        # Δlog series: sum next h monthly changes
        df["y"] = df[target].rolling(horizon).sum().shift(-horizon)

    cols = ["ebp"] + controls
    df = df[["y"] + cols].dropna()
    X = sm.add_constant(df[cols])
    model = sm.OLS(df["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": horizon + 6})
    return model


def main() -> None:
    panel = build_monthly_panel()
    print(f"Panel shape: {panel.shape}")
    print(f"Date range: {panel.index.min():%Y-%m} to {panel.index.max():%Y-%m}")
    print(f"EBP range: {panel['ebp'].dropna().index.min():%Y-%m} to {panel['ebp'].dropna().index.max():%Y-%m}")

    panel.to_parquet(RESULTS_DIR / "monthly_panel.parquet")

    # === Predictive regressions ===
    rows = []
    targets = {"dlog_indpro": "Δlog IP", "dlog_payems": "Δlog Payroll", "dur": "ΔUR"}
    for sample_name, sample in SAMPLES.items():
        print(f"\n========== Sample {sample_name} ({sample[0]} ~ {sample[1]}) ==========")
        for tgt, label in targets.items():
            for h in HORIZONS:
                m = predictive_regression(panel, tgt, h, sample)
                ebp_b = m.params["ebp"]
                ebp_t = m.tvalues["ebp"]
                r2 = m.rsquared
                rows.append(
                    {
                        "sample": sample_name,
                        "target": label,
                        "horizon": h,
                        "ebp_coef": ebp_b,
                        "ebp_t": ebp_t,
                        "R2": r2,
                        "n_obs": int(m.nobs),
                    }
                )
                print(
                    f"  {label:12s} h={h:>2}m: β_EBP={ebp_b:+.3f} "
                    f"(t={ebp_t:+.2f}), R²={r2:.3f}, n={int(m.nobs)}"
                )

    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS_DIR / "predictive_regressions.csv", index=False)

    # === Time series plot of EBP and GZ spread with recessions ===
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    p = panel.dropna(subset=["ebp"])
    # GZ
    axes[0].plot(p.index, p["gz_spread"], color="steelblue", linewidth=1.2)
    axes[0].set_title("GZ credit spread (Gilchrist-Zakrajšek)")
    axes[0].set_ylabel("Percent")
    # EBP
    axes[1].plot(p.index, p["ebp"], color="firebrick", linewidth=1.2)
    axes[1].axhline(0, color="k", linewidth=0.5)
    axes[1].set_title("Excess Bond Premium (EBP)")
    axes[1].set_ylabel("Percent")
    # est_prob
    axes[2].plot(p.index, p["est_prob"] * 100, color="forestgreen", linewidth=1.2)
    axes[2].set_title("Expected default component (%)")
    axes[2].set_ylabel("Percent")
    axes[2].set_xlabel("")

    # Shade NBER recessions
    usrec = panel["USREC"].dropna()
    if len(usrec):
        in_rec = False
        rec_start = None
        for d, v in usrec.items():
            if v == 1 and not in_rec:
                rec_start = d
                in_rec = True
            elif v == 0 and in_rec:
                for ax in axes:
                    ax.axvspan(rec_start, d, color="lightgrey", alpha=0.4)
                in_rec = False
        if in_rec:
            for ax in axes:
                ax.axvspan(rec_start, usrec.index[-1], color="lightgrey", alpha=0.4)

    for ax in axes:
        ax.grid(alpha=0.3)
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "ebp_timeseries.png", dpi=130)
    plt.close(fig)

    # === Heatmap of R² across samples / targets / horizons ===
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (sample_name, sample) in zip(axes, SAMPLES.items()):
        sub = summary[summary["sample"] == sample_name].pivot_table(
            index="target", columns="horizon", values="R2"
        )
        im = ax.imshow(sub.values, cmap="viridis", aspect="auto", vmin=0, vmax=0.5)
        ax.set_xticks(range(len(sub.columns)))
        ax.set_xticklabels([f"h={h}m" for h in sub.columns])
        ax.set_yticks(range(len(sub.index)))
        ax.set_yticklabels(sub.index)
        ax.set_title(sample_name.replace("_", " "))
        for i, row in enumerate(sub.values):
            for j, val in enumerate(row):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color="white" if val < 0.25 else "black", fontsize=9)
    fig.colorbar(im, ax=axes, label="R²", fraction=0.025)
    fig.suptitle("Predictive R² of EBP for real activity (controlled for term spread + real FF)", y=1.02)
    fig.savefig(RESULTS_DIR / "predictive_r2_heatmap.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
