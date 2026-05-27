"""Bundle B.2 — Regime decomposition of EBP predictability (NBER × QE).

The horse race revealed that all financial stress indices lose predictive
power for real activity after 2011. This script decomposes the EBP /
OFR FSI Credit predictive regression by:

1. **NBER recession periods** (USREC == 1) vs expansion (USREC == 0)
2. **Fed QE active** (WALCL YoY growth > 10%) vs **not QE**

Cross-tabulating gives 4 cells. We compare:
- The unconditional sample R² (paper-style)
- The conditional sample R² within each cell

If the EBP/stress-index → real-activity relationship is strongest **in
recessions outside of QE**, this would suggest QE-era recessions (COVID,
2022) have a fundamentally different macro-credit transmission.

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
from fi_research.data.ofr_fsi import load_ofr_fsi

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def build_panel() -> pd.DataFrame:
    fred = load_panel(
        ["INDPRO", "PAYEMS", "UNRATE", "USREC", "NFCI", "ANFCI", "WALCL"]
    )
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index().resample("M").last()
    fred["dlog_indpro"] = np.log(fred["INDPRO"]).diff() * 100
    fred["dlog_payems"] = np.log(fred["PAYEMS"]).diff() * 100
    fred["dur"] = fred["UNRATE"].diff()
    # WALCL YoY growth as QE proxy
    fred["walcl_yoy"] = (fred["WALCL"] / fred["WALCL"].shift(12) - 1) * 100
    fred["qe_active"] = (fred["walcl_yoy"] > 10).astype(int)

    ebp = load_ebp()
    ebp["date"] = pd.to_datetime(ebp["date"])
    ebp = ebp.set_index("date").sort_index().resample("M").last()

    ofr = load_ofr_fsi()
    ofr["date"] = pd.to_datetime(ofr["date"])
    ofr = ofr.set_index("date").sort_index()
    ofr_m = ofr[["ofr_fsi", "credit"]].resample("M").last()
    ofr_m.columns = ["ofr_fsi_total", "ofr_fsi_credit"]

    panel = fred.join(ebp[["ebp", "gz_spread"]], how="outer")
    panel = panel.join(ofr_m, how="outer")
    return panel.sort_index()


REGIME_DEFS = {
    "all":     lambda p: pd.Series(True, index=p.index),
    "NBER":    lambda p: p["USREC"] == 1,
    "noNBER":  lambda p: p["USREC"] == 0,
    "QE":      lambda p: p["qe_active"] == 1,
    "noQE":    lambda p: p["qe_active"] == 0,
    "NBER×QE":     lambda p: (p["USREC"] == 1) & (p["qe_active"] == 1),
    "NBER×noQE":   lambda p: (p["USREC"] == 1) & (p["qe_active"] == 0),
    "noNBER×QE":   lambda p: (p["USREC"] == 0) & (p["qe_active"] == 1),
    "noNBER×noQE": lambda p: (p["USREC"] == 0) & (p["qe_active"] == 0),
}


def predictive(panel: pd.DataFrame, target: str, horizon: int, stress: str,
               mask: pd.Series) -> sm.regression.linear_model.RegressionResultsWrapper | None:
    df = panel.copy()
    if target == "dur":
        df["y"] = df["UNRATE"].shift(-horizon) - df["UNRATE"]
    else:
        df["y"] = df[target].rolling(horizon).sum().shift(-horizon)
    sub = df.loc[mask.fillna(False), ["y", stress]].dropna()
    if len(sub) < 24:
        return None
    X = sm.add_constant(sub[stress])
    return sm.OLS(sub["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": horizon + 6})


def main() -> None:
    panel = build_panel()
    print(f"Panel shape: {panel.shape}")
    print(f"QE periods (WALCL YoY > 10%): n={int(panel['qe_active'].sum())} months")
    qe_active_dates = panel.loc[panel["qe_active"] == 1].index
    if len(qe_active_dates):
        print(f"  earliest QE month: {qe_active_dates.min():%Y-%m}")
        print(f"  latest QE month:   {qe_active_dates.max():%Y-%m}")
        # Pretty print contiguous QE periods
        qe_flag = panel["qe_active"].fillna(0).astype(int)
        change = qe_flag.diff().fillna(0)
        starts = panel.index[change == 1]
        ends = panel.index[change == -1]
        if len(starts) and len(ends):
            print("  QE episodes (start → end):")
            for s, e in zip(starts, ends):
                print(f"    {s:%Y-%m} → {e:%Y-%m}")

    targets = ["dlog_payems", "dur"]
    rows = []
    for stress in ["ebp", "ofr_fsi_credit", "NFCI", "ANFCI"]:
        for target in targets:
            for h in [6, 12, 24]:
                for regime_name, mask_fn in REGIME_DEFS.items():
                    mask = mask_fn(panel)
                    m = predictive(panel, target, h, stress, mask)
                    if m is None:
                        continue
                    rows.append({
                        "stress": stress,
                        "target": target,
                        "horizon": h,
                        "regime": regime_name,
                        "coef": float(m.params[stress]),
                        "t": float(m.tvalues[stress]),
                        "R2": float(m.rsquared),
                        "n_obs": int(m.nobs),
                    })

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / "regime_decomposition.csv", index=False)

    # Print main result: EBP × Payroll @ h=12m by regime
    print("\n=== EBP → Δlog Payroll (h=12m) by regime ===")
    sub = out[(out["stress"] == "ebp") & (out["target"] == "dlog_payems") & (out["horizon"] == 12)]
    for _, r in sub.iterrows():
        print(f"  {r['regime']:14s}: R²={r['R2']:.3f}, β={r['coef']:+.3f}, t={r['t']:+.2f}, n={int(r['n_obs'])}")

    print("\n=== OFR FSI Credit → Δlog Payroll (h=12m) by regime ===")
    sub = out[(out["stress"] == "ofr_fsi_credit") & (out["target"] == "dlog_payems") & (out["horizon"] == 12)]
    for _, r in sub.iterrows():
        print(f"  {r['regime']:14s}: R²={r['R2']:.3f}, β={r['coef']:+.3f}, t={r['t']:+.2f}, n={int(r['n_obs'])}")

    # === Bar chart by regime ===
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    for ax_row, target in zip(axes, ["dlog_payems", "dur"]):
        for ax, h in zip(ax_row, [12, 24]):
            sub = out[(out["target"] == target) & (out["horizon"] == h)]
            stresses = ["ebp", "ofr_fsi_credit", "NFCI", "ANFCI"]
            regimes = ["all", "noNBER×noQE", "noNBER×QE", "NBER×noQE", "NBER×QE"]
            x = np.arange(len(regimes))
            width = 0.2
            for i, stress in enumerate(stresses):
                ys = []
                for r in regimes:
                    cell = sub[(sub["stress"] == stress) & (sub["regime"] == r)]
                    ys.append(cell["R2"].iloc[0] if len(cell) else 0)
                ax.bar(x + (i - 1.5) * width, ys, width, label=stress)
            ax.set_xticks(x)
            ax.set_xticklabels(regimes, rotation=20)
            ax.set_ylabel("R²")
            ax.set_title(f"target={target}, h={h}m")
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3, axis="y")
    fig.suptitle("Predictive R² by NBER × QE regime", y=1.01)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "regime_r2_bars.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Save the panel with regime flags
    panel[["USREC", "qe_active", "walcl_yoy", "ebp", "ofr_fsi_credit", "NFCI"]].to_parquet(
        RESULTS_DIR / "regime_flagged_panel.parquet"
    )

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
