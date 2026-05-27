"""Bundle B.1 — Horse race of stress indices for real-activity prediction.

The Gilchrist-Zakrajšek (2012) replication revealed that EBP's predictive
power for real activity collapsed after 2010. Is this:
(a) Specific to EBP (e.g., EBP construction methodology no longer captures
    the relevant credit information in the QE / post-Dodd-Frank world), or
(b) A general pattern across all financial-stress / credit-condition
    indices?

This script runs side-by-side univariate predictive regressions of
real-activity changes at h = 3, 6, 12, 24 months on each of:
- EBP (Favara et al. 2016 update)
- NFCI (Chicago Fed National Financial Conditions Index)
- ANFCI (Adjusted NFCI; orthogonalized to current macro state)
- STLFSI4 (St. Louis Fed Financial Stress Index 4)
- OFR FSI (Office of Financial Research, U.S. component)
- OFR FSI Credit subcomponent
- MOVE (Treasury bond implied volatility)
- VIX

With samples: pre-2011 (corresponds to GZ paper era) and 2011-2025
(post-QE / post-Dodd-Frank).

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.fred import load_panel
from fi_research.data.frb_ebp import load_ebp
from fi_research.data.move import load_move
from fi_research.data.ofr_fsi import load_ofr_fsi

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = {"dlog_indpro": "Δlog IP", "dlog_payems": "Δlog Payroll", "dur": "ΔUR"}
HORIZONS = [3, 6, 12, 24]
SAMPLES = {
    "pre_2011": ("1973-01-01", "2010-12-31"),
    "post_2011": ("2011-01-01", "2025-12-31"),
    "full": ("1973-01-01", "2025-12-31"),
}


def build_panel() -> pd.DataFrame:
    # FRED macro + stress indices
    fred = load_panel(["INDPRO", "PAYEMS", "UNRATE", "NFCI", "ANFCI", "STLFSI4",
                       "VIXCLS", "T10Y3M", "DFF", "CPIAUCSL"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index().resample("M").last()
    fred["dlog_indpro"] = np.log(fred["INDPRO"]).diff() * 100
    fred["dlog_payems"] = np.log(fred["PAYEMS"]).diff() * 100
    fred["dur"] = fred["UNRATE"].diff()

    # EBP
    ebp = load_ebp()
    ebp["date"] = pd.to_datetime(ebp["date"])
    ebp = ebp.set_index("date").sort_index().resample("M").last()

    # OFR FSI
    ofr = load_ofr_fsi()
    ofr["date"] = pd.to_datetime(ofr["date"])
    ofr = ofr.set_index("date").sort_index()
    ofr_m = ofr[["ofr_fsi", "credit", "united_states"]].resample("M").last()
    ofr_m.columns = ["ofr_fsi_total", "ofr_fsi_credit", "ofr_fsi_us"]

    # MOVE
    mv = load_move()
    mv["date"] = pd.to_datetime(mv["date"])
    mv = mv.set_index("date").sort_index()
    mv_m = mv.resample("M").last()
    if mv_m.shape[1] > 1:
        mv_m = mv_m.iloc[:, [0]]
    mv_m.columns = ["MOVE"]

    panel = fred.join(ebp[["ebp", "gz_spread"]], how="outer")
    panel = panel.join(ofr_m, how="outer").join(mv_m, how="outer")
    panel = panel.sort_index()
    return panel


STRESS_VARS = ["ebp", "NFCI", "ANFCI", "STLFSI4", "ofr_fsi_total",
               "ofr_fsi_credit", "ofr_fsi_us", "MOVE", "VIXCLS"]


def predictive(panel: pd.DataFrame, target: str, horizon: int, stress: str,
               sample: tuple[str, str]) -> sm.regression.linear_model.RegressionResultsWrapper:
    start, end = sample
    df = panel.loc[start:end].copy()
    if target == "dur":
        df["y"] = df["UNRATE"].shift(-horizon) - df["UNRATE"]
    else:
        df["y"] = df[target].rolling(horizon).sum().shift(-horizon)
    sub = df[["y", stress]].dropna()
    if len(sub) < 24:
        return None
    X = sm.add_constant(sub[stress])
    return sm.OLS(sub["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": horizon + 6})


def main() -> None:
    panel = build_panel()
    print(f"Panel shape: {panel.shape}")
    print("Stress var coverage:")
    for v in STRESS_VARS:
        if v in panel.columns:
            s = panel[v].dropna()
            print(f"  {v:20s}: {s.index.min():%Y-%m} ~ {s.index.max():%Y-%m} (n={len(s)})")
    panel.to_parquet(RESULTS_DIR / "horse_race_panel.parquet")

    rows = []
    for sample_name, sample in SAMPLES.items():
        for tgt, lbl in TARGETS.items():
            for h in HORIZONS:
                for stress in STRESS_VARS:
                    if stress not in panel.columns:
                        continue
                    m = predictive(panel, tgt, h, stress, sample)
                    if m is None:
                        continue
                    rows.append({
                        "sample": sample_name,
                        "target": lbl,
                        "horizon": h,
                        "stress": stress,
                        "coef": float(m.params[stress]),
                        "t": float(m.tvalues[stress]),
                        "R2": float(m.rsquared),
                        "n_obs": int(m.nobs),
                    })
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / "horse_race_results.csv", index=False)

    # === Print sample summaries ===
    for sample_name in SAMPLES:
        print(f"\n========== Sample: {sample_name} ==========")
        sub = out[out["sample"] == sample_name]
        # For h=12 only, pivot by stress × target
        for h in [3, 12, 24]:
            sub_h = sub[sub["horizon"] == h]
            pivot = sub_h.pivot_table(index="stress", columns="target", values="R2")
            print(f"\nR² @ h={h}m:")
            print(pivot.round(3).to_string())

    # === Heatmap of R² ===
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for col_idx, sample_name in enumerate(["pre_2011", "post_2011", "full"]):
        for row_idx, tgt_label in enumerate(["Δlog IP", "Δlog Payroll"]):
            ax = axes[row_idx, col_idx]
            sub = out[(out["sample"] == sample_name) & (out["target"] == tgt_label)]
            pivot = sub.pivot_table(index="stress", columns="horizon", values="R2")
            # Order stress vars
            order = [s for s in STRESS_VARS if s in pivot.index]
            pivot = pivot.loc[order]
            im = ax.imshow(pivot.values, cmap="viridis", aspect="auto", vmin=0, vmax=0.6)
            ax.set_xticks(range(len(pivot.columns)))
            ax.set_xticklabels([f"h={h}m" for h in pivot.columns])
            ax.set_yticks(range(len(pivot.index)))
            ax.set_yticklabels(pivot.index)
            for i, row in enumerate(pivot.values):
                for j, val in enumerate(row):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            color="white" if val < 0.3 else "black", fontsize=8)
            ax.set_title(f"{tgt_label} — {sample_name}")
    fig.colorbar(im, ax=axes, label="R²", fraction=0.02)
    fig.suptitle("Univariate predictive R² for real activity by stress index",
                 y=1.0, fontsize=13)
    fig.savefig(RESULTS_DIR / "horse_race_heatmap.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # === Bar chart: R² at h=12m, target=Δlog Payroll, across stress vars ===
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    h_pick = 12
    target_pick = "Δlog Payroll"
    for ax, sample_name in zip(axes, ["pre_2011", "post_2011", "full"]):
        sub = out[
            (out["sample"] == sample_name)
            & (out["target"] == target_pick)
            & (out["horizon"] == h_pick)
        ]
        sub = sub.set_index("stress").reindex([s for s in STRESS_VARS if s in sub.index])
        ax.barh(sub.index, sub["R2"], color="steelblue")
        ax.invert_yaxis()
        ax.set_title(f"{sample_name}\n(target={target_pick}, h={h_pick}m)")
        ax.set_xlabel("R²")
        ax.set_xlim(0, 0.65)
        ax.grid(alpha=0.3, axis="x")
        for stress, r2 in zip(sub.index, sub["R2"]):
            ax.text(r2 + 0.01, list(sub.index).index(stress), f"{r2:.3f}", va="center", fontsize=8)
    fig.suptitle("Univariate R² of stress indices for predicting Δlog Payroll (12m)", y=1.04)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "horse_race_bars_payroll12m.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
