"""Replication of Bauer & Swanson (2023, AER).

"An Alternative Explanation for the 'Fed Information Effect'."
American Economic Review 113(3), 664-700. (Also see the companion paper
"A Reassessment of Monetary Policy Surprises and High-Frequency
Identification", NBER MA 2023.)

Replication scope:
- Table 2-style: predictability of raw high-frequency monetary policy
  surprises (mps) from pre-FOMC macroeconomic and financial information
  (nfp surprises, 12-mo NFP, 3-mo S&P 500 return, 3-mo yield curve slope,
  3-mo commodity return, Treasury return skewness).
- Table 3-4-style: contemporaneous Fed-day response of stock prices and
  Treasury yields to mps vs mps_orth. The "Fed information effect"
  (positive coefficient of stock returns on contractionary surprises) is
  expected to disappear when using orthogonalized surprises.

Data: ``fi_research.data.mp_shocks.load_mp_shocks('fomc_2023update')`` and
``'monthly_2023update'`` — 1988-02 to 2023-12.

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.mp_shocks import load_mp_shocks

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PRE_FOMC_PREDICTORS = ["nfp_surp", "nfp_12m", "sp500_3m", "slope_3m", "bcom_3m", "tr_skew"]
RESPONSES = {
    "sp500_emini": "S&P 500 e-mini (30-min FOMC window)",
    "tnote02": "2y Treasury yield Δ (FOMC window)",
    "tnote05": "5y Treasury yield Δ (FOMC window)",
    "tnote10": "10y Treasury yield Δ (FOMC window)",
    "tbond": "30y Treasury bond yield Δ (FOMC window)",
}
SAMPLES = {
    "paper_full_1988_2019": ("1988-01-01", "2019-12-31"),
    "incl_covid_1988_2023": ("1988-01-01", "2023-12-31"),
}


def predictability_table(df: pd.DataFrame, sample: tuple[str, str]) -> pd.DataFrame:
    """Regress raw and orthogonalized MPS on pre-FOMC predictors. Univariate + joint."""
    start, end = sample
    rows = []
    for lhs in ["mps", "mps_orth"]:
        # Univariate
        for pred in PRE_FOMC_PREDICTORS:
            sub = df.loc[start:end, [lhs, pred]].dropna()
            X = sm.add_constant(sub[pred])
            m = sm.OLS(sub[lhs], X).fit(cov_type="HC1")
            rows.append(
                {
                    "lhs": lhs,
                    "model": f"univariate({pred})",
                    "predictor": pred,
                    "coef": m.params[pred],
                    "t": m.tvalues[pred],
                    "R2": m.rsquared,
                    "n": int(m.nobs),
                }
            )
        # Joint
        sub = df.loc[start:end, [lhs] + PRE_FOMC_PREDICTORS].dropna()
        X = sm.add_constant(sub[PRE_FOMC_PREDICTORS])
        m = sm.OLS(sub[lhs], X).fit(cov_type="HC1")
        rows.append(
            {
                "lhs": lhs,
                "model": "joint",
                "predictor": "ALL",
                "coef": np.nan,
                "t": np.nan,
                "R2": m.rsquared,
                "R2_adj": m.rsquared_adj,
                "F": m.fvalue,
                "F_pvalue": m.f_pvalue,
                "n": int(m.nobs),
            }
        )
    return pd.DataFrame(rows)


def response_table(df: pd.DataFrame, sample: tuple[str, str]) -> pd.DataFrame:
    """Regress each response variable on mps and mps_orth (separately)."""
    start, end = sample
    rows = []
    for resp_col, resp_label in RESPONSES.items():
        for shock in ["mps", "mps_orth"]:
            sub = df.loc[start:end, [resp_col, shock]].dropna()
            X = sm.add_constant(sub[shock])
            m = sm.OLS(sub[resp_col], X).fit(cov_type="HC1")
            rows.append(
                {
                    "response": resp_col,
                    "response_label": resp_label,
                    "shock": shock,
                    "coef": m.params[shock],
                    "se": m.bse[shock],
                    "t": m.tvalues[shock],
                    "R2": m.rsquared,
                    "n": int(m.nobs),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    fomc = load_mp_shocks("fomc_2023update")
    fomc["date"] = pd.to_datetime(fomc["date"])
    fomc = fomc.set_index("date").sort_index()
    print(f"FOMC sample: {len(fomc)} events from {fomc.index.min():%Y-%m} to {fomc.index.max():%Y-%m}")
    print(f"  scheduled events: {(fomc['unscheduled'] == 0).sum()}, unscheduled: {(fomc['unscheduled'] == 1).sum()}")

    monthly = load_mp_shocks("monthly_2023update")
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly = monthly.set_index("date").sort_index()

    # === Section 1: Predictability of mps vs mps_orth from pre-FOMC info ===
    print("\n" + "=" * 70)
    print("Section 1: Predictability of mps vs mps_orth (FOMC-level)")
    print("=" * 70)

    pred_results = []
    for sample_name, sample in SAMPLES.items():
        print(f"\n--- Sample: {sample_name} ---")
        tab = predictability_table(fomc, sample)
        tab["sample"] = sample_name
        pred_results.append(tab)
        joint = tab[tab["model"] == "joint"]
        for _, row in joint.iterrows():
            print(
                f"  Joint regression of {row['lhs']}: R²={row['R2']:.3f}, "
                f"F={row['F']:.2f} (p={row['F_pvalue']:.4f}), n={int(row['n'])}"
            )
        # show univariate t-stats for raw mps
        print("  Univariate t-stats for mps:")
        uni = tab[(tab["lhs"] == "mps") & (tab["model"] != "joint")]
        for _, row in uni.iterrows():
            print(f"    {row['predictor']:10s}: t={row['t']:+.2f}, R²={row['R2']:.3f}")
    pred_summary = pd.concat(pred_results, ignore_index=True)
    pred_summary.to_csv(RESULTS_DIR / "predictability_mps.csv", index=False)

    # === Section 2: Fed-day response of stock and bond markets ===
    print("\n" + "=" * 70)
    print("Section 2: Fed-day response: shock → market reaction")
    print("=" * 70)

    resp_results = []
    for sample_name, sample in SAMPLES.items():
        print(f"\n--- Sample: {sample_name} ---")
        tab = response_table(fomc, sample)
        tab["sample"] = sample_name
        resp_results.append(tab)
        for resp_col in RESPONSES:
            print(f"  {resp_col}:")
            for shock in ["mps", "mps_orth"]:
                row = tab[(tab["response"] == resp_col) & (tab["shock"] == shock)].iloc[0]
                sign_note = ""
                if resp_col == "sp500_emini" and shock == "mps":
                    sign_note = " ← info effect: positive expected"
                elif resp_col == "sp500_emini" and shock == "mps_orth":
                    sign_note = " ← BS argue this should turn NEGATIVE"
                print(
                    f"    {shock:10s}: β={row['coef']:+.3f} (t={row['t']:+.2f}), "
                    f"R²={row['R2']:.3f}{sign_note}"
                )
    resp_summary = pd.concat(resp_results, ignore_index=True)
    resp_summary.to_csv(RESULTS_DIR / "shock_response.csv", index=False)

    # === Plot: scatter of stock reaction vs mps and mps_orth ===
    sample = SAMPLES["paper_full_1988_2019"]
    sub = fomc.loc[sample[0] : sample[1]].dropna(
        subset=["sp500_emini", "mps", "mps_orth"]
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, shock, title in zip(
        axes, ["mps", "mps_orth"], ["Raw MPS (Nakamura-Steinsson style)", "Orthogonalized MPS (Bauer-Swanson)"]
    ):
        ax.scatter(sub[shock], sub["sp500_emini"], s=14, alpha=0.6, color="steelblue")
        # OLS line
        X = sm.add_constant(sub[shock])
        m = sm.OLS(sub["sp500_emini"], X).fit()
        xs = np.linspace(sub[shock].min(), sub[shock].max(), 20)
        ax.plot(xs, m.params[0] + m.params[1] * xs, color="firebrick", linewidth=1.5)
        ax.axhline(0, color="k", linewidth=0.4)
        ax.axvline(0, color="k", linewidth=0.4)
        ax.set_xlabel(f"{shock} (FOMC-day shock)")
        ax.set_title(f"{title}\nβ = {m.params[1]:+.2f}, t = {m.tvalues[1]:+.2f}, R²={m.rsquared:.3f}")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("S&P 500 e-mini Δ (FOMC window)")
    fig.suptitle("Fed information effect — does it disappear with orthogonalized shock?")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "info_effect_scatter.png", dpi=130)
    plt.close(fig)

    # === Plot: bar chart of coefficients across responses, shocks, samples ===
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (sample_name, sample) in zip(axes, SAMPLES.items()):
        sub_tab = resp_summary[resp_summary["sample"] == sample_name]
        responses = list(RESPONSES.keys())
        x = np.arange(len(responses))
        width = 0.36
        for i, shock in enumerate(["mps", "mps_orth"]):
            ys = [
                sub_tab[(sub_tab["response"] == r) & (sub_tab["shock"] == shock)]["coef"].iloc[0]
                for r in responses
            ]
            ax.bar(x + (i - 0.5) * width, ys, width, label=shock)
        ax.set_xticks(x)
        ax.set_xticklabels(responses, rotation=20)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_title(f"Coefficient by shock — {sample_name}")
        ax.set_ylabel("β (response per unit shock)")
        ax.legend()
        ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "response_coefficients.png", dpi=130)
    plt.close(fig)

    # Save the FOMC-level merged frame
    fomc.to_parquet(RESULTS_DIR / "fomc_panel.parquet")
    monthly.to_parquet(RESULTS_DIR / "monthly_panel.parquet")

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
