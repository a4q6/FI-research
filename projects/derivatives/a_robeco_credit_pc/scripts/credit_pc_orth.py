"""Bundle A.1 — Robeco factor returns orthogonalized against credit PC1.

The HvZ (2017) replication showed annualized vols of 3-7% (IG) for the
Robeco factor portfolios because the published series include the credit
market beta (excess over duration-matched Treasury, NOT vs index). The
paper's Table 3 IR values use long-short or active-return constructs that
remove the common credit factor.

Here we approximate that step by:
- Extracting the first principal component of the 4 single factors
  (Size, LowRisk, Value, Momentum) as a common credit-beta proxy.
- Orthogonalizing each factor against PC1 (residuals from
  ``factor ~ const + PC1``).
- Recomputing mean / vol / IR / t-stat on the residuals.

This should yield IR values closer to the paper and validate the
hypothesis that the Robeco public dataset's high vols come from credit
beta exposure.

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from fi_research.data.fred import load_panel
from fi_research.data.robeco import load_robeco_credit_factors

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FACTORS = ["Size", "LowRisk", "Value", "Momentum"]
PAPER_SAMPLE = ("1994-01-31", "2015-09-30")


def annualized_stats(s: pd.Series) -> dict[str, float]:
    mu_m = s.mean()
    sd_m = s.std(ddof=1)
    n = s.notna().sum()
    return {
        "mean_ann_pct": mu_m * 12.0 * 100,
        "vol_ann_pct": sd_m * np.sqrt(12.0) * 100,
        "IR": (mu_m / sd_m) * np.sqrt(12.0) if sd_m > 0 else np.nan,
        "t_stat": (mu_m / sd_m) * np.sqrt(n) if sd_m > 0 else np.nan,
        "n_months": int(n),
    }


def analyze_one_market(label: str, df: pd.DataFrame, sample: tuple[str, str]) -> dict:
    sub = df.loc[sample[0] : sample[1], FACTORS].dropna()

    # Standardize, then PCA on 4 factors
    scaler = StandardScaler()
    X = scaler.fit_transform(sub.values)
    pca = PCA(n_components=4)
    pcs = pca.fit_transform(X)
    pcs_df = pd.DataFrame(pcs, index=sub.index, columns=[f"PC{i + 1}" for i in range(4)])

    loadings = pd.DataFrame(
        pca.components_.T,
        index=FACTORS,
        columns=[f"PC{i + 1}" for i in range(4)],
    )

    # Orthogonalize each factor against PC1 — alpha / TE / IR semantics:
    #   factor = alpha + beta * PC1 + epsilon
    #   alpha   = const term (factor return after controlling for PC1 exposure)
    #   TE      = std(epsilon)  (residual / tracking-error volatility)
    #   IR      = alpha / TE * sqrt(12)  annualized
    #   t_alpha = const / SE(const)
    residuals = pd.DataFrame(index=sub.index, columns=FACTORS, dtype=float)
    coefs_pc1 = {}
    alpha_stats: dict[str, dict] = {}
    for f in FACTORS:
        y = sub[f].values
        X1 = sm.add_constant(pcs_df[["PC1"]].values)
        m = sm.OLS(y, X1).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        residuals[f] = m.resid
        coefs_pc1[f] = float(m.params[1])
        alpha_m = float(m.params[0])
        te_m = float(np.std(m.resid, ddof=1))
        n = len(m.resid)
        alpha_stats[f] = {
            "alpha_ann_pct": alpha_m * 12.0 * 100,
            "TE_ann_pct": te_m * np.sqrt(12.0) * 100,
            "IR": (alpha_m / te_m) * np.sqrt(12.0) if te_m > 0 else np.nan,
            "t_alpha": float(m.tvalues[0]),
            "beta_PC1": coefs_pc1[f],
            "n_months": int(n),
        }

    # MultiFactor(EW) — regress EW average return on PC1 too
    ew_raw = sub.mean(axis=1)
    X1 = sm.add_constant(pcs_df[["PC1"]].values)
    m_ew = sm.OLS(ew_raw.values, X1).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    alpha_stats["MultiFactor(EW)"] = {
        "alpha_ann_pct": float(m_ew.params[0]) * 12.0 * 100,
        "TE_ann_pct": float(np.std(m_ew.resid, ddof=1)) * np.sqrt(12.0) * 100,
        "IR": (float(m_ew.params[0]) / float(np.std(m_ew.resid, ddof=1))) * np.sqrt(12.0),
        "t_alpha": float(m_ew.tvalues[0]),
        "beta_PC1": float(m_ew.params[1]),
        "n_months": int(len(m_ew.resid)),
    }

    # Raw stats (re-used from HvZ replication)
    raw_stats = pd.DataFrame({f: annualized_stats(sub[f]) for f in FACTORS}).T
    raw_stats.loc["MultiFactor(EW)"] = annualized_stats(sub.mean(axis=1))

    alpha_stats_df = pd.DataFrame(alpha_stats).T[
        ["alpha_ann_pct", "TE_ann_pct", "IR", "t_alpha", "beta_PC1", "n_months"]
    ]

    return {
        "label": label,
        "raw_stats": raw_stats,
        "alpha_stats": alpha_stats_df,
        "pca_explained": pca.explained_variance_ratio_,
        "loadings": loadings,
        "coefs_pc1": coefs_pc1,
        "residuals": residuals,
        "pc_scores": pcs_df,
    }


def analyze_with_external_credit_proxy(
    label: str, factor_df: pd.DataFrame, credit_proxy: pd.Series, sample: tuple[str, str]
) -> pd.DataFrame:
    """Orthogonalize each factor against an EXOGENOUS credit market proxy
    (Δ BAML OAS times approximate duration → monthly credit market return).

    This avoids the endogeneity of PC1 (PC1 is constructed from the same
    factors). Output is the alpha/TE/IR table.
    """
    sub = factor_df.loc[sample[0] : sample[1], FACTORS].dropna()
    cp = credit_proxy.reindex(sub.index)
    sub_aligned = sub.join(cp.rename("credit_proxy")).dropna()

    rows = {}
    residuals = pd.DataFrame(index=sub_aligned.index, columns=FACTORS, dtype=float)
    for f in FACTORS:
        y = sub_aligned[f].values
        X1 = sm.add_constant(sub_aligned[["credit_proxy"]].values)
        m = sm.OLS(y, X1).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        residuals[f] = m.resid
        alpha_m = float(m.params[0])
        te_m = float(np.std(m.resid, ddof=1))
        rows[f] = {
            "alpha_ann_pct": alpha_m * 12.0 * 100,
            "TE_ann_pct": te_m * np.sqrt(12.0) * 100,
            "IR": (alpha_m / te_m) * np.sqrt(12.0) if te_m > 0 else np.nan,
            "t_alpha": float(m.tvalues[0]),
            "beta_proxy": float(m.params[1]),
            "n_months": int(len(m.resid)),
        }
    ew_raw = sub_aligned[FACTORS].mean(axis=1)
    X1 = sm.add_constant(sub_aligned[["credit_proxy"]].values)
    m_ew = sm.OLS(ew_raw.values, X1).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    rows["MultiFactor(EW)"] = {
        "alpha_ann_pct": float(m_ew.params[0]) * 12.0 * 100,
        "TE_ann_pct": float(np.std(m_ew.resid, ddof=1)) * np.sqrt(12.0) * 100,
        "IR": (float(m_ew.params[0]) / float(np.std(m_ew.resid, ddof=1))) * np.sqrt(12.0),
        "t_alpha": float(m_ew.tvalues[0]),
        "beta_proxy": float(m_ew.params[1]),
        "n_months": int(len(m_ew.resid)),
    }
    return pd.DataFrame(rows).T


def build_credit_proxy() -> pd.Series:
    """Monthly credit-market return proxy:
    return ≈ -duration × Δ spread.

    BAML OAS via FRED has only ~3 years of history (license limitation per
    repository caveats). Instead we use BAA10Y (Moody's Baa corporate yield
    minus 10y Treasury) which covers 1986-01 onward — long enough to fit
    the Robeco factor sample (1994-01+).

    Output: monthly series in DECIMAL (matches Robeco units)."""
    fred = load_panel(["BAA10Y"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index()
    monthly = fred["BAA10Y"].resample("M").last()
    spread_decimal = monthly / 100.0  # spread in decimal
    d_spread = spread_decimal.diff()
    DURATION = 7.0
    return (-DURATION * d_spread).rename("credit_return_proxy")


def main() -> None:
    ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
    hy = load_robeco_credit_factors("HY").set_index("date").sort_index()
    credit_proxy = build_credit_proxy()
    print(
        f"Credit proxy (−7·Δ BAA10Y) — {credit_proxy.dropna().shape[0]} months "
        f"from {credit_proxy.dropna().index.min():%Y-%m} to {credit_proxy.dropna().index.max():%Y-%m}"
    )

    out_rows = []
    summary_paper = {}
    for label, df in [("IG", ig), ("HY", hy)]:
        for sample_name, sample in [
            ("paper_1994_2015", PAPER_SAMPLE),
            ("full_1994_2025", ("1994-01-31", "2025-12-31")),
        ]:
            res = analyze_one_market(label, df, sample)
            print(f"\n=== {label} {sample_name} ===")
            print(f"PCA explained: {res['pca_explained'].round(3).tolist()}")
            print(f"PC1 cumulative: {res['pca_explained'][0]:.3f}")
            print("\nPC loadings (4 factors → 4 PCs):")
            print(res["loadings"].round(3).to_string())
            print(f"\nFactor loading on PC1 (β_PC1 from `factor ~ PC1` OLS):")
            for f, b in res["coefs_pc1"].items():
                print(f"  {f}: β_PC1 = {b:+.4f}")

            print(f"\n--- RAW factor stats ---")
            print(res["raw_stats"].round(3).to_string())
            print(f"\n--- PC1-orthogonalized: alpha / TE / IR ---")
            print(res["alpha_stats"].round(3).to_string())

            # Stash CSVs
            res["raw_stats"].to_csv(RESULTS_DIR / f"raw_stats_{label}_{sample_name}.csv")
            res["alpha_stats"].to_csv(RESULTS_DIR / f"alpha_stats_{label}_{sample_name}.csv")
            res["loadings"].to_csv(RESULTS_DIR / f"pca_loadings_{label}_{sample_name}.csv")

            if sample_name == "paper_1994_2015":
                summary_paper[label] = res

            # Append for combined CSV
            for kind, tab in [("raw", res["raw_stats"]), ("pc1_orth_alpha", res["alpha_stats"])]:
                for f, row in tab.iterrows():
                    out_rows.append(
                        {
                            "market": label,
                            "sample": sample_name,
                            "kind": kind,
                            "factor": f,
                            **{k: v for k, v in row.to_dict().items()},
                        }
                    )

    combined = pd.DataFrame(out_rows)
    combined.to_csv(RESULTS_DIR / "all_stats.csv", index=False)

    # Houweling-van Zundert (2017) Table 3 IRs (paper sample 1994-Sep 2015).
    PAPER_IR_IG = {
        "Size": 0.74,
        "LowRisk": 0.73,
        "Value": 0.67,
        "Momentum": 0.58,
        "MultiFactor(EW)": 1.38,
    }
    PAPER_IR_HY = {
        "Size": 1.08,
        "LowRisk": 0.96,
        "Value": 0.69,
        "Momentum": 0.62,
        "MultiFactor(EW)": 1.42,
    }
    paper_table = {"IG": PAPER_IR_IG, "HY": PAPER_IR_HY}

    # === Exogenous credit proxy (BAA10Y-based) orthogonalization ===
    print("\n" + "=" * 70)
    print("Exogenous credit proxy orthogonalization (−7·Δ BAA10Y)")
    print("=" * 70)
    exo_summary_paper = {}
    for label, df in [("IG", ig), ("HY", hy)]:
        for sample_name, sample in [
            ("paper_1994_2015", ("1994-01-31", "2015-09-30")),
            ("full_1994_2025", ("1994-01-31", "2025-12-31")),
        ]:
            tab = analyze_with_external_credit_proxy(label, df, credit_proxy, sample)
            print(f"\n=== {label} {sample_name} ===")
            print(tab.round(3).to_string())
            tab.to_csv(RESULTS_DIR / f"exo_credit_orth_{label}_{sample_name}.csv")
            if sample_name == "paper_1994_2015":
                exo_summary_paper[label] = tab

    # === Final comparison plot: 4 IR variants side by side (paper sample) ===
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    factors_plus = FACTORS + ["MultiFactor(EW)"]
    x = np.arange(len(factors_plus))
    width = 0.2
    for ax, label in zip(axes, ["IG", "HY"]):
        res = summary_paper[label]
        raw_ir = [res["raw_stats"].loc[f, "IR"] for f in factors_plus]
        pc1_ir = [res["alpha_stats"].loc[f, "IR"] for f in factors_plus]
        exo_ir = [exo_summary_paper[label].loc[f, "IR"] for f in factors_plus]
        paper_ir = [paper_table[label][f] for f in factors_plus]
        ax.bar(x - 1.5 * width, raw_ir, width, label="Raw (excess over DM Tsy)", color="steelblue")
        ax.bar(x - 0.5 * width, pc1_ir, width, label="Orth to endogenous PC1", color="darkorange")
        ax.bar(x + 0.5 * width, exo_ir, width, label="Orth to BAA10Y proxy", color="forestgreen")
        ax.bar(x + 1.5 * width, paper_ir, width, label="HvZ paper Table 3", color="firebrick")
        ax.set_xticks(x)
        ax.set_xticklabels(factors_plus, rotation=20)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_ylabel("Information Ratio (annualized)")
        ax.set_title(f"Robeco {label} — IR variants (paper sample 1994-Sep 2015)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "ir_4way_comparison.png", dpi=130)
    plt.close(fig)

    # === Cumulative return of MultiFactor: raw vs orthogonalized ===
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, label, df in [
        (axes[0], "IG", ig),
        (axes[1], "HY", hy),
    ]:
        res = analyze_one_market(label, df, ("1994-01-31", "2025-12-31"))
        sub = df.loc["1994-01-31":"2025-12-31", FACTORS].dropna()
        raw_mf = sub.mean(axis=1)
        # Add back the alpha (constant) to residuals to visualize the "tracking" series
        ew_alpha_monthly = res["alpha_stats"].loc["MultiFactor(EW)", "alpha_ann_pct"] / 12.0 / 100
        res_mf = res["residuals"].mean(axis=1) + ew_alpha_monthly
        cum_raw = (1 + raw_mf).cumprod() - 1
        cum_res = (1 + res_mf).cumprod() - 1
        ax.plot(cum_raw.index, cum_raw.values, label="MultiFactor (raw, with credit beta)", linewidth=1.3)
        ax.plot(cum_res.index, cum_res.values, label="MultiFactor (alpha-only, orth to PC1)", linewidth=1.3)
        ax.axhline(0, color="k", linewidth=0.4)
        ax.set_title(f"Robeco {label} — MultiFactor cumulative return")
        ax.set_ylabel("Cumulative return")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "cumret_orth_vs_raw.png", dpi=130)
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
