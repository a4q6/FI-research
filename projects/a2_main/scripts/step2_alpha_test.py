"""A2 main — Step 2: Time-series α test with MP-regime controls.

Tests whether the Robeco IG/HY factor alphas (Houweling-van Zundert 2017)
shrink once the regime-dependent MP transmission terms from
[[novel-findings-2026-05]] are added as controls.

Model sequence per factor:

    (a) factor_t = α + ε_t                                  ← baseline
    (b) factor_t = α + β·mps_orth_sum_t + ε_t
    (c) factor_t = α + β·fsi_eom_z_t + ε_t
    (d) factor_t = α + β1·mps_orth_sum_t
                       + β2·mps_x_fsi_z_sum_t
                       + β3·fsi_eom_z_t + ε_t              ← main test
    (e) factor_t = α + (d) + Robeco other 3 factors
                       + macro: dlog_indpro, dur, dlog_cpi  ← full controls

HAC standard errors with maxlags = 6.

H1 judgment: model (d) and (e) alpha t-stats drop by >30% vs (a) for at
least one Robeco factor (especially Value or Momentum, since Size is
expected to be most robust per feasibility findings).

Outputs: ``results/alpha_table.csv``, sub-sample tables, figure.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.fred import load_panel
from fi_research.data.robeco import load_robeco_credit_factors

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FACTORS = ["Size", "LowRisk", "Value", "Momentum", "MultiFactor"]
SAMPLES = {
    "ofr_window_2000_2025": ("2000-01-31", "2025-12-31"),
    "pre_BBW_2000_2018":    ("2000-01-31", "2018-12-31"),
    "post_BBW_2019_2025":   ("2019-01-31", "2025-12-31"),
}


def build_macro_controls() -> pd.DataFrame:
    fred = load_panel(["INDPRO", "UNRATE", "CPIAUCSL", "DGS10", "DFF"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index().resample("M").last()
    fred["dlog_indpro"] = np.log(fred["INDPRO"]).diff() * 100
    fred["dlog_cpi"] = np.log(fred["CPIAUCSL"]).diff() * 100
    fred["dur"] = fred["UNRATE"].diff()
    fred["dgs10"] = fred["DGS10"].diff()
    fred["dff"] = fred["DFF"].diff()
    return fred[["dlog_indpro", "dlog_cpi", "dur", "dgs10", "dff"]]


def alpha_with_controls(
    y: pd.Series, controls: pd.DataFrame | None
) -> sm.regression.linear_model.RegressionResultsWrapper:
    if controls is None or controls.empty:
        df = y.to_frame("y").dropna()
        X = sm.add_constant(np.ones((len(df), 1))[:, :0])  # only constant
        return sm.OLS(df["y"], pd.Series(1.0, index=df.index).to_frame("const")).fit(
            cov_type="HAC", cov_kwds={"maxlags": 6}
        )
    df = pd.concat([y.rename("y"), controls], axis=1).dropna()
    X = sm.add_constant(df[controls.columns])
    return sm.OLS(df["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})


def run_models(
    factor_returns: pd.DataFrame,
    market: str,
    exposure: pd.DataFrame,
    macro: pd.DataFrame,
    sample: tuple[str, str],
) -> pd.DataFrame:
    start, end = sample
    rows = []
    other_factors = [f for f in FACTORS if f != "MultiFactor"]
    fac_sub = factor_returns.loc[start:end]
    exp_sub = exposure.loc[start:end]
    macro_sub = macro.loc[start:end]

    for f in FACTORS:
        y = fac_sub[f]
        # (a) baseline — alpha only
        m_a = alpha_with_controls(y, None)
        # (b) MP only
        m_b = alpha_with_controls(y, exp_sub[["mps_orth_sum"]])
        # (c) FSI only
        m_c = alpha_with_controls(y, exp_sub[["fsi_eom_z"]])
        # (d) MP + MP×FSI + FSI
        m_d = alpha_with_controls(y, exp_sub[["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]])
        # (e) Full: (d) + Robeco other 3 + macro
        other_cols = [c for c in other_factors if c != f]
        x_e = pd.concat([
            exp_sub[["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]],
            fac_sub[other_cols],
            macro_sub,
        ], axis=1)
        m_e = alpha_with_controls(y, x_e)

        for model_name, m in [("a_baseline", m_a), ("b_mps", m_b), ("c_fsi", m_c),
                              ("d_full_regime", m_d), ("e_full_controls", m_e)]:
            alpha = float(m.params["const"])
            t_alpha = float(m.tvalues["const"])
            r2 = float(m.rsquared)
            rows.append({
                "market": market,
                "factor": f,
                "sample": sample[0][:4] + "-" + sample[1][:4],
                "model": model_name,
                "alpha_monthly": alpha,
                "alpha_ann_pct": alpha * 12.0 * 100,
                "t_alpha": t_alpha,
                "R2": r2,
                "n_obs": int(m.nobs),
                # Extra: regime-MP coefficients (only models d, e)
                **{
                    f"b_{c}": float(m.params[c]) if c in m.params.index else np.nan
                    for c in ["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]
                },
                **{
                    f"t_{c}": float(m.tvalues[c]) if c in m.tvalues.index else np.nan
                    for c in ["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]
                },
            })
    return pd.DataFrame(rows)


def main() -> None:
    exposure = pd.read_parquet(RESULTS_DIR / "monthly_mp_regime_exposure.parquet")
    macro = build_macro_controls()
    ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
    hy = load_robeco_credit_factors("HY").set_index("date").sort_index()
    print(f"Exposure: {exposure.shape}, macro: {macro.shape}")
    print(f"IG: {ig.shape}, HY: {hy.shape}")

    all_rows = []
    for sample_name, sample in SAMPLES.items():
        for market_label, df in [("IG", ig), ("HY", hy)]:
            print(f"\n========== {market_label} | {sample_name} ==========")
            res = run_models(df, market_label, exposure, macro, sample)
            res["sample_key"] = sample_name
            all_rows.append(res)
            # Quick print: alpha + t-stat for each factor × model
            for f in FACTORS:
                print(f"  {f}:")
                sub = res[res["factor"] == f]
                for _, r in sub.iterrows():
                    print(
                        f"    {r['model']:18s}: "
                        f"α={r['alpha_ann_pct']:+6.2f}%/yr "
                        f"(t={r['t_alpha']:+5.2f}), R²={r['R2']:.3f}, n={int(r['n_obs'])}"
                    )

    out = pd.concat(all_rows, ignore_index=True)
    out.to_csv(RESULTS_DIR / "alpha_table.csv", index=False)

    # === Compact summary: α %ann + t-stat per (market, factor, model) for full sample ===
    print("\n" + "=" * 80)
    print("=== H1 check: α reduction from baseline (model a) to full regime (model e) ===")
    print("=" * 80)
    sub = out[out["sample_key"] == "ofr_window_2000_2025"]
    summary_rows = []
    for market in ["IG", "HY"]:
        for f in FACTORS:
            a_row = sub[(sub["market"] == market) & (sub["factor"] == f) & (sub["model"] == "a_baseline")]
            e_row = sub[(sub["market"] == market) & (sub["factor"] == f) & (sub["model"] == "e_full_controls")]
            d_row = sub[(sub["market"] == market) & (sub["factor"] == f) & (sub["model"] == "d_full_regime")]
            if len(a_row) and len(e_row):
                a_a = float(a_row["alpha_ann_pct"].iloc[0])
                a_e = float(e_row["alpha_ann_pct"].iloc[0])
                t_a = float(a_row["t_alpha"].iloc[0])
                t_d = float(d_row["t_alpha"].iloc[0])
                t_e = float(e_row["t_alpha"].iloc[0])
                t_reduction = (abs(t_a) - abs(t_e)) / abs(t_a) * 100 if abs(t_a) > 0 else np.nan
                summary_rows.append({
                    "market": market,
                    "factor": f,
                    "α_baseline (%)": round(a_a, 2),
                    "α_full (%)": round(a_e, 2),
                    "t_baseline": round(t_a, 2),
                    "t_regime_only": round(t_d, 2),
                    "t_full": round(t_e, 2),
                    "t_reduction (%)": round(t_reduction, 1),
                })
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    summary_df.to_csv(RESULTS_DIR / "alpha_table_h1_summary.csv", index=False)

    # === Print regime-MP coefficients (model d) ===
    print("\n" + "=" * 80)
    print("=== Regime-MP coefficients (model d) — full sample 2000-2025 ===")
    print("=" * 80)
    for market in ["IG", "HY"]:
        print(f"\n{market}:")
        sub_d = sub[(sub["market"] == market) & (sub["model"] == "d_full_regime")]
        for _, r in sub_d.iterrows():
            print(
                f"  {r['factor']:12s}: "
                f"β_mps={r['b_mps_orth_sum']:+6.3f} (t={r['t_mps_orth_sum']:+5.2f}),  "
                f"β_mps×FSI={r['b_mps_x_fsi_z_sum']:+6.3f} (t={r['t_mps_x_fsi_z_sum']:+5.2f}),  "
                f"β_FSI={r['b_fsi_eom_z']:+6.3f} (t={r['t_fsi_eom_z']:+5.2f})"
            )

    # === Plot: t_alpha across models for IG, full sample ===
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, market in zip(axes, ["IG", "HY"]):
        sub_m = sub[sub["market"] == market]
        models = ["a_baseline", "b_mps", "c_fsi", "d_full_regime", "e_full_controls"]
        x = np.arange(len(FACTORS))
        width = 0.16
        for i, mname in enumerate(models):
            ys = []
            for f in FACTORS:
                row = sub_m[(sub_m["factor"] == f) & (sub_m["model"] == mname)]
                ys.append(float(row["t_alpha"].iloc[0]) if len(row) else np.nan)
            ax.bar(x + (i - 2) * width, ys, width, label=mname)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.axhline(1.96, color="grey", linewidth=0.5, linestyle="--")
        ax.axhline(-1.96, color="grey", linewidth=0.5, linestyle="--")
        ax.set_xticks(x)
        ax.set_xticklabels(FACTORS, rotation=20)
        ax.set_title(f"{market} — α t-stat across models (full 2000-2025)")
        ax.set_ylabel("t-stat on α")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "alpha_t_stat_models.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
