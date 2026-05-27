"""A2 main — Step 3: Feng-Giglio-Xiu (2020) double-selection LASSO.

Implements the FGX post-double-selection inference procedure to test
which factors among the 17 candidates are economically necessary to
explain the cross-section of corporate bond factor returns.

Procedure (FGX 2020, §3):

For each test asset (Robeco IG/HY × {Size, LowRisk, Value, Momentum,
MultiFactor}):

1. **Step A**: LASSO regress the test-asset return r_t on all 17 candidate
   factors; let S_A = {factors with non-zero coefficient}.
2. **Step B**: For each candidate factor g_j, LASSO regress g_j on the
   other 16 candidates; let S_B = {factors that survive in ANY g_j
   regression}.
3. **Step C**: Run OLS of r_t on the union S = S_A ∪ S_B plus a constant.
   The OLS α coefficient and t-statistic are valid post-selection
   estimates.

Hypothesis H1: regime-MP variables (mps_orth_sum, mps_x_fsi_z_sum,
fsi_eom_z) appear in S for most factors; after their inclusion in Step C,
the Robeco-factor αs collapse.

Outputs: ``results/fgx_selected_factors.csv`` and
``results/fgx_alpha_post_selection.csv``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

from fi_research.data.fred import load_panel
from fi_research.data.robeco import load_robeco_credit_factors

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ROBECO_FACTORS = ["Size", "LowRisk", "Value", "Momentum"]
ROBECO_PORTFOLIOS = ROBECO_FACTORS + ["MultiFactor"]
SAMPLE = ("2000-01-31", "2025-12-31")
SUBSAMPLES = {
    "full_2000_2025": ("2000-01-31", "2025-12-31"),
    "pre_BBW_2000_2018": ("2000-01-31", "2018-12-31"),
    "post_BBW_2019_2025": ("2019-01-31", "2025-12-31"),
}


def build_candidate_factors() -> tuple[pd.DataFrame, list[str]]:
    """Return a (months × 17 candidates) DataFrame.

    Candidates:
    - Robeco IG factors (4): Size, LowRisk, Value, Momentum
    - Macro (10): dlog_indpro, dlog_payems, dur, dlog_cpi, dlog_pce,
      dgs10, dff, t10y3m, baa10y, aaa10y (stationarized)
    - Regime-MP (3): mps_orth_sum, mps_x_fsi_z_sum, fsi_eom_z
    """
    ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
    robeco_pan = ig[ROBECO_FACTORS].copy()

    fred = load_panel([
        "INDPRO", "PAYEMS", "UNRATE", "CPIAUCSL", "PCEPI",
        "DGS10", "DFF", "T10Y3M", "BAA10Y", "AAA10Y",
    ])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index().resample("M").last()
    fred["dlog_indpro"] = np.log(fred["INDPRO"]).diff() * 100
    fred["dlog_payems"] = np.log(fred["PAYEMS"]).diff() * 100
    fred["dlog_cpi"] = np.log(fred["CPIAUCSL"]).diff() * 100
    fred["dlog_pce"] = np.log(fred["PCEPI"]).diff() * 100
    fred["dur"] = fred["UNRATE"].diff()
    fred["dgs10"] = fred["DGS10"].diff()
    fred["dff"] = fred["DFF"].diff()
    fred["t10y3m"] = fred["T10Y3M"]
    fred["baa10y_d"] = fred["BAA10Y"].diff()
    fred["aaa10y_d"] = fred["AAA10Y"].diff()
    macro = fred[[
        "dlog_indpro", "dlog_payems", "dur", "dlog_cpi", "dlog_pce",
        "dgs10", "dff", "t10y3m", "baa10y_d", "aaa10y_d",
    ]]

    exposure = pd.read_parquet(RESULTS_DIR / "monthly_mp_regime_exposure.parquet")
    regime = exposure[["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]]

    candidates = pd.concat([
        robeco_pan.add_prefix("IG_"),
        macro,
        regime,
    ], axis=1)

    cand_names = list(candidates.columns)
    return candidates, cand_names


def lasso_select(
    y: np.ndarray, X: np.ndarray, names: list[str], rng: int = 0
) -> set[str]:
    """Standardize X, run cross-validated LASSO, return names of selected vars."""
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = LassoCV(cv=5, max_iter=20000, random_state=rng)
    model.fit(Xs, y)
    nonzero = np.where(np.abs(model.coef_) > 1e-10)[0]
    return {names[i] for i in nonzero}


def fgx_one_asset(
    y: pd.Series, candidates: pd.DataFrame, exclude: list[str] | None = None
) -> dict:
    """Run FGX procedure for one test asset.

    `exclude` removes candidate columns equal to the test asset itself
    (e.g. when testing IG_Size, do not include IG_Size in candidates).
    """
    cand = candidates.copy()
    if exclude:
        cand = cand.drop(columns=[c for c in exclude if c in cand.columns])
    df = pd.concat([y.rename("y"), cand], axis=1).dropna()
    cand_names = list(cand.columns)
    Xfull = df[cand_names].values

    # Step A: regress y on all candidates
    S_A = lasso_select(df["y"].values, Xfull, cand_names)

    # Step B: regress each candidate on the rest
    S_B: set[str] = set()
    for j, gname in enumerate(cand_names):
        rest_idx = [i for i in range(len(cand_names)) if i != j]
        rest_names = [cand_names[i] for i in rest_idx]
        Xrest = Xfull[:, rest_idx]
        yj = Xfull[:, j]
        sel = lasso_select(yj, Xrest, rest_names)
        S_B |= sel

    S = S_A | S_B

    # Step C: post-selection OLS
    if S:
        X_C = sm.add_constant(df[list(S)])
        m_C = sm.OLS(df["y"], X_C).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        alpha = float(m_C.params["const"])
        t_alpha = float(m_C.tvalues["const"])
        r2 = float(m_C.rsquared)
        coef_dict = m_C.params.to_dict()
        t_dict = m_C.tvalues.to_dict()
    else:
        # No selection — baseline alpha
        m_C = sm.OLS(df["y"], pd.Series(1.0, index=df.index).to_frame("const")).fit(
            cov_type="HAC", cov_kwds={"maxlags": 6}
        )
        alpha = float(m_C.params["const"])
        t_alpha = float(m_C.tvalues["const"])
        r2 = float(m_C.rsquared)
        coef_dict = {"const": alpha}
        t_dict = {"const": t_alpha}

    return {
        "S_A": S_A,
        "S_B": S_B,
        "S": S,
        "alpha_monthly": alpha,
        "alpha_ann_pct": alpha * 12.0 * 100,
        "t_alpha": t_alpha,
        "R2": r2,
        "n_obs": int(m_C.nobs),
        "coefs": coef_dict,
        "tvalues": t_dict,
    }


def main() -> None:
    candidates, cand_names = build_candidate_factors()
    print(f"Candidates ({len(cand_names)}): {cand_names}")
    print(f"Candidate panel shape: {candidates.shape}")

    ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
    hy = load_robeco_credit_factors("HY").set_index("date").sort_index()

    selection_rows = []
    alpha_rows = []
    coef_rows = []

    for sample_name, sample in SUBSAMPLES.items():
        for market_label, df in [("IG", ig), ("HY", hy)]:
            for f in ROBECO_PORTFOLIOS:
                print(f"\n=== {market_label} {f} | {sample_name} ===")
                y = df.loc[sample[0]:sample[1], f]
                if y.dropna().shape[0] < 30:
                    continue
                # Exclude the same factor in the candidate set if we're testing IG factor
                # (we don't want IG_Size to be in candidates when y is IG Size)
                exclude = [f"IG_{f}"] if market_label == "IG" and f != "MultiFactor" else []
                # For MultiFactor, exclude all IG_* to avoid using construct from same series
                if f == "MultiFactor" and market_label == "IG":
                    exclude = [f"IG_{x}" for x in ROBECO_FACTORS]
                cand_sub = candidates.loc[sample[0]:sample[1]]
                res = fgx_one_asset(y, cand_sub, exclude=exclude)
                print(f"  Selected (S_A ∪ S_B), n={len(res['S'])}: {sorted(res['S'])}")
                print(f"  α = {res['alpha_ann_pct']:+.2f}%/yr, t = {res['t_alpha']:+.2f}, R² = {res['R2']:.3f}, n = {res['n_obs']}")

                selection_rows.append({
                    "sample": sample_name,
                    "market": market_label,
                    "factor": f,
                    "S_A": sorted(res["S_A"]),
                    "S_B": sorted(res["S_B"]),
                    "S_union": sorted(res["S"]),
                    "n_selected": len(res["S"]),
                    "regime_mp_selected": [
                        v for v in ["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]
                        if v in res["S"]
                    ],
                })
                alpha_rows.append({
                    "sample": sample_name,
                    "market": market_label,
                    "factor": f,
                    "alpha_ann_pct": res["alpha_ann_pct"],
                    "t_alpha": res["t_alpha"],
                    "R2": res["R2"],
                    "n_obs": res["n_obs"],
                    "n_selected": len(res["S"]),
                })
                for cname in res["S"]:
                    coef_rows.append({
                        "sample": sample_name,
                        "market": market_label,
                        "factor": f,
                        "regressor": cname,
                        "coef": res["coefs"].get(cname, np.nan),
                        "t": res["tvalues"].get(cname, np.nan),
                    })

    sel_df = pd.DataFrame(selection_rows)
    sel_df["S_A"] = sel_df["S_A"].apply(lambda x: ",".join(x))
    sel_df["S_B"] = sel_df["S_B"].apply(lambda x: ",".join(x))
    sel_df["S_union"] = sel_df["S_union"].apply(lambda x: ",".join(x))
    sel_df["regime_mp_selected"] = sel_df["regime_mp_selected"].apply(lambda x: ",".join(x))
    sel_df.to_csv(RESULTS_DIR / "fgx_selected_factors.csv", index=False)

    alpha_df = pd.DataFrame(alpha_rows)
    alpha_df.to_csv(RESULTS_DIR / "fgx_alpha_post_selection.csv", index=False)

    coef_df = pd.DataFrame(coef_rows)
    coef_df.to_csv(RESULTS_DIR / "fgx_post_selection_coefs.csv", index=False)

    # === Comparison: HvZ-paper-style α vs FGX-post-selection α ===
    print("\n" + "=" * 80)
    print("=== H1 check: α before/after FGX post-double-selection (full sample) ===")
    print("=" * 80)
    full = alpha_df[alpha_df["sample"] == "full_2000_2025"]
    # Bring in baseline alphas from Step 2's alpha_table for comparison
    try:
        step2 = pd.read_csv(RESULTS_DIR / "alpha_table.csv")
        baseline = step2[(step2["sample_key"] == "ofr_window_2000_2025")
                         & (step2["model"] == "a_baseline")][
            ["market", "factor", "alpha_ann_pct", "t_alpha"]
        ].rename(columns={"alpha_ann_pct": "alpha_baseline", "t_alpha": "t_baseline"})
        merged = full.merge(baseline, on=["market", "factor"], how="left")
        merged["t_reduction_pct"] = (
            (merged["t_baseline"].abs() - merged["t_alpha"].abs())
            / merged["t_baseline"].abs() * 100
        )
        print(merged[["market", "factor", "alpha_baseline", "t_baseline",
                       "alpha_ann_pct", "t_alpha", "n_selected", "t_reduction_pct"]]
              .round(2).to_string(index=False))
        merged.to_csv(RESULTS_DIR / "fgx_h1_summary.csv", index=False)
    except Exception as e:
        print(f"Could not produce H1 summary: {e}")

    # === Selection frequency of regime-MP variables ===
    print("\n=== Regime-MP variable selection frequency ===")
    print("(across all market × factor × sample combinations)")
    for v in ["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z"]:
        selected_in = sel_df["S_union"].str.contains(v).sum()
        total = len(sel_df)
        print(f"  {v:25s}: selected in {selected_in}/{total} ({selected_in/total*100:.0f}%)")

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
