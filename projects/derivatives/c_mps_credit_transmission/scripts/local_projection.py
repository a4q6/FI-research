"""Bundle C.2 — Local projection (Jordà 2005) of credit response to MPS.

The one-day FOMC event analysis (baml_oas_fomc_reaction.py) measured the
immediate response of credit spreads to MP shocks. But:
- Does the credit spread response **persist** over days/weeks/months?
- Or is it quickly reversed (suggesting overshooting / noise trading)?
- Is the response timing different between IG and HY proxy?

Jordà (2005) local projection (LP) regresses outcomes at horizon h on the
shock plus controls, separately for each h ∈ {0, 1, ..., H}. This produces
an impulse response function (IRF) without VAR identifying assumptions.

For each h ∈ {0, 1, ..., 40} business days:
    spread_{d+h} − spread_{d−1} = α_h + β_h · mps_d + γ_h · controls_d + ε_{d+h}

where:
- spread is one of: BAA10Y, AAA10Y, BAA-AAA, DGS10 (Treasury benchmark)
- controls = pre-FOMC variables (to be conservative, but minimal: lagged
  spread level, nfp_12m, sp500_3m)

Standard errors use Newey-West with maxlags = h.

Two shock specifications: mps and mps_orth.

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.fred import load_panel
from fi_research.data.mp_shocks import load_mp_shocks

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

HORIZONS = list(range(0, 41))  # 0 to 40 business days
SERIES = ["BAA10Y", "AAA10Y", "BAA_AAA_spread", "DGS10"]
SHOCKS = ["mps", "mps_orth"]


def build_daily_panel() -> pd.DataFrame:
    fred = load_panel(["BAA10Y", "AAA10Y", "DGS10"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index()
    fred["BAA_AAA_spread"] = fred["BAA10Y"] - fred["AAA10Y"]
    return fred[SERIES]


def local_projection_one(
    daily: pd.DataFrame, fomc: pd.DataFrame, series: str, shock: str, sample: tuple[str, str]
) -> pd.DataFrame:
    """For one series × one shock spec, run LP at each horizon."""
    start, end = sample
    fomc_sub = fomc.loc[start:end, [shock, "nfp_12m", "sp500_3m"]].dropna(subset=[shock])
    daily_s = daily[series].dropna().sort_index()

    rows = []
    for h in HORIZONS:
        # Build the dependent variable y_{d+h} − y_{d-1}
        ys = []
        xs = []
        ctrl_nfp = []
        ctrl_sp = []
        prev_levels = []
        for d in fomc_sub.index:
            prior = daily_s.index[daily_s.index < d]
            if len(prior) == 0:
                continue
            d_prev = prior[-1]
            v_prev = daily_s.loc[d_prev]
            # Find d+h (forward h business days from d_prev)
            future_idx = daily_s.index[daily_s.index >= d_prev]
            if len(future_idx) <= h + 1:
                continue
            v_h = daily_s.iloc[daily_s.index.get_loc(d_prev) + h + 1] if (
                daily_s.index.get_loc(d_prev) + h + 1 < len(daily_s)
            ) else np.nan
            if pd.isna(v_h):
                continue
            ys.append(v_h - v_prev)
            xs.append(fomc_sub.loc[d, shock])
            ctrl_nfp.append(fomc_sub.loc[d, "nfp_12m"])
            ctrl_sp.append(fomc_sub.loc[d, "sp500_3m"])
            prev_levels.append(v_prev)
        if len(ys) < 30:
            continue
        df = pd.DataFrame({
            "y": pd.to_numeric(pd.Series(ys), errors="coerce"),
            "shock": pd.to_numeric(pd.Series(xs), errors="coerce"),
            "ctrl_nfp": pd.to_numeric(pd.Series(ctrl_nfp), errors="coerce"),
            "ctrl_sp": pd.to_numeric(pd.Series(ctrl_sp), errors="coerce"),
            "level": pd.to_numeric(pd.Series(prev_levels), errors="coerce"),
        }).dropna()
        if len(df) < 30:
            continue
        X = sm.add_constant(df[["shock", "ctrl_nfp", "ctrl_sp", "level"]])
        m = sm.OLS(df["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": max(1, h)})
        rows.append({
            "h_days": h,
            "coef": float(m.params["shock"]),
            "se": float(m.bse["shock"]),
            "t": float(m.tvalues["shock"]),
            "ci_lo": float(m.params["shock"] - 1.96 * m.bse["shock"]),
            "ci_hi": float(m.params["shock"] + 1.96 * m.bse["shock"]),
            "n_obs": int(m.nobs),
        })
    return pd.DataFrame(rows)


def main() -> None:
    fomc = load_mp_shocks("fomc_2023update")
    fomc["date"] = pd.to_datetime(fomc["date"])
    fomc = fomc.set_index("date").sort_index()
    daily = build_daily_panel()
    print(f"Daily panel: {daily.shape} from {daily.index.min():%Y-%m} to {daily.index.max():%Y-%m}")

    sample = ("1988-01-01", "2019-12-31")
    print(f"\nSample: {sample[0]} ~ {sample[1]}")

    all_rows = []
    for series in SERIES:
        for shock in SHOCKS:
            tab = local_projection_one(daily, fomc, series, shock, sample)
            if tab.empty:
                continue
            tab["series"] = series
            tab["shock"] = shock
            all_rows.append(tab)
            # Print briefly
            peak_row = tab.iloc[tab["coef"].abs().idxmax()]
            print(
                f"  {series:18s} × {shock:10s}: "
                f"peak |β| at h={int(peak_row['h_days'])}d, "
                f"β={peak_row['coef']:+.3f} (t={peak_row['t']:+.2f})"
            )

    irf = pd.concat(all_rows, ignore_index=True)
    irf.to_csv(RESULTS_DIR / "local_projection_irfs.csv", index=False)
    irf.to_parquet(RESULTS_DIR / "local_projection_irfs.parquet")

    # === IRF plot: 4 series × 2 shocks ===
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
    for ax, series in zip(axes.flat, SERIES):
        for shock, color in zip(SHOCKS, ["steelblue", "darkorange"]):
            sub = irf[(irf["series"] == series) & (irf["shock"] == shock)]
            if sub.empty:
                continue
            ax.plot(sub["h_days"], sub["coef"], label=shock, color=color, linewidth=1.6)
            ax.fill_between(sub["h_days"], sub["ci_lo"], sub["ci_hi"],
                            alpha=0.2, color=color)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_title(f"Local projection IRF: Δ{series}_{{d+h}} on MP shock at d")
        ax.set_xlabel("Horizon (business days)")
        ax.set_ylabel("β (Δspread in pp per unit shock)")
        ax.legend()
        ax.grid(alpha=0.3)
    fig.suptitle(
        f"Credit spread impulse response to FOMC-day MP shock — Jordà LP "
        f"({sample[0][:4]}-{sample[1][:4]})",
        y=1.01,
    )
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "local_projection_irfs.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # === Comparison plot: mps_orth IRFs for all 4 series on one axis ===
    fig, ax = plt.subplots(figsize=(10, 6))
    for series, color in zip(SERIES, ["steelblue", "forestgreen", "firebrick", "purple"]):
        sub = irf[(irf["series"] == series) & (irf["shock"] == "mps_orth")]
        if sub.empty:
            continue
        ax.plot(sub["h_days"], sub["coef"], label=series, color=color, linewidth=1.5)
        ax.fill_between(sub["h_days"], sub["ci_lo"], sub["ci_hi"], alpha=0.12, color=color)
    ax.axhline(0, color="k", linewidth=0.5)
    ax.set_title(
        "IRFs (mps_orth shock): persistence of credit & Treasury response over 40 days"
    )
    ax.set_xlabel("Horizon (business days)")
    ax.set_ylabel("Cumulative β (pp per unit shock)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "irf_mps_orth_comparison.png", dpi=130)
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
