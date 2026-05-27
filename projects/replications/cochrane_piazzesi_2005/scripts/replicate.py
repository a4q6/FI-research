"""Replication of Cochrane & Piazzesi (2005, AER).

"Bond Risk Premia." American Economic Review 95(1), 138-160.

Replication scope:
- Construct 1-year forward rates from GSW zero yields (replacing the
  Fama-Bliss data used in the paper).
- 1-year holding-period excess returns rx_{t+12}^(n) for n=2,...,5.
- CP regression: rx_{t+12}^(n) ~ y_t^(1) + f_t^(2) + f_t^(3) + f_t^(4) + f_t^(5).
- Tent-shaped coefficient pattern (Figure 1).
- Single-factor restriction: extract CP factor as the fitted value of
  average rx across maturities, then re-run R^2 with CP factor only.
- Compare R^2 with the unrestricted full-yield regression.

Data: ``fi_research.data.treasury.load_gsw_nominal`` (1971-2025).

Note: forecasting overlapping 12-month returns from monthly data implies
serially correlated residuals. We report Newey-West HAC standard errors
with 18 lags as in Cochrane-Piazzesi.

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.treasury import load_gsw_nominal

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MATURITIES = [1, 2, 3, 4, 5]
SAMPLES = {
    "cp_paper_1964_2003": ("1964-01-01", "2003-12-31"),
    "post_paper_2004_2025": ("2004-01-01", "2025-12-31"),
    "full_1971_2025": ("1971-08-16", "2025-12-31"),
}


def build_monthly_forwards(gsw: pd.DataFrame) -> pd.DataFrame:
    """Return month-end forwards f^(n→n+1) and zero yields y^(n) for n=1..5."""
    df = gsw[["date"] + [f"SVENY{n:02d}" for n in MATURITIES]].copy()
    df = df.dropna(subset=[f"SVENY{n:02d}" for n in MATURITIES])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # Resample to month-end (last available daily observation in the month)
    me = df.resample("M").last()
    # GSW yields are annualized percent, continuously compounded.
    # Convert to decimals.
    y = me / 100.0
    y.columns = [f"y{n}" for n in MATURITIES]

    # log price p^(n) = -n * y^(n)
    p = pd.DataFrame({f"p{n}": -n * y[f"y{n}"] for n in MATURITIES}, index=y.index)
    # 1-year forwards: f^(n) = p^(n-1) - p^(n) for n=2..5
    fwd = pd.DataFrame(index=y.index)
    fwd["f1"] = y["y1"]  # by convention f^(1) ≡ y^(1)
    for n in [2, 3, 4, 5]:
        fwd[f"f{n}"] = p[f"p{n - 1}"] - p[f"p{n}"]

    out = y.join(p).join(fwd)
    return out


def build_excess_returns(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute 1-year holding-period excess log returns rx_{t+12}^(n).

    rx_{t+12}^(n) = p_{t+12}^(n-1) - p_t^(n) - y_t^(1)
    """
    rx = pd.DataFrame(index=panel.index)
    for n in [2, 3, 4, 5]:
        rx[f"rx{n}"] = panel[f"p{n - 1}"].shift(-12) - panel[f"p{n}"] - panel["y1"]
    rx["rxavg"] = rx[[f"rx{n}" for n in [2, 3, 4, 5]]].mean(axis=1)
    return rx


def cp_regression(
    panel: pd.DataFrame, rx: pd.DataFrame, sample: tuple[str, str]
) -> dict[str, sm.regression.linear_model.RegressionResultsWrapper]:
    """Run the CP unrestricted regression for each maturity over `sample`."""
    start, end = sample
    X_cols = ["f1", "f2", "f3", "f4", "f5"]
    X = panel.loc[start:end, X_cols]

    results = {}
    for n in [2, 3, 4, 5, "avg"]:
        y_col = f"rx{n}"
        df = X.join(rx.loc[start:end, [y_col]]).dropna()
        Xm = sm.add_constant(df[X_cols].values)
        model = sm.OLS(df[y_col].values, Xm).fit(
            cov_type="HAC", cov_kwds={"maxlags": 18}
        )
        results[str(n)] = model
    return results


def extract_cp_factor(
    panel: pd.DataFrame, rx: pd.DataFrame, sample: tuple[str, str]
) -> pd.Series:
    """CP factor = fitted value from regressing rx_avg on forwards."""
    start, end = sample
    X_cols = ["f1", "f2", "f3", "f4", "f5"]
    df = panel.loc[start:end, X_cols].join(rx.loc[start:end, ["rxavg"]]).dropna()
    Xm = sm.add_constant(df[X_cols].values)
    mdl = sm.OLS(df["rxavg"].values, Xm).fit(
        cov_type="HAC", cov_kwds={"maxlags": 18}
    )
    # Use the FULL panel to build cp factor (not just regression sample)
    Xfull = sm.add_constant(panel[X_cols].dropna().values)
    cp = pd.Series(
        Xfull @ mdl.params,
        index=panel[X_cols].dropna().index,
        name="cp_factor",
    )
    return cp, mdl


def single_factor_regression(
    cp: pd.Series, rx: pd.DataFrame, sample: tuple[str, str]
) -> dict:
    start, end = sample
    out = {}
    for n in [2, 3, 4, 5, "avg"]:
        df = pd.concat([cp, rx[f"rx{n}"]], axis=1).loc[start:end].dropna()
        df.columns = ["cp", "y"]
        Xm = sm.add_constant(df["cp"].values)
        m = sm.OLS(df["y"].values, Xm).fit(cov_type="HAC", cov_kwds={"maxlags": 18})
        out[str(n)] = m
    return out


def format_table(results: dict, label: str) -> pd.DataFrame:
    rows = []
    for n_str, m in results.items():
        rows.append(
            {
                "maturity": n_str,
                "n_obs": int(m.nobs),
                "R2": float(m.rsquared),
                "R2_adj": float(m.rsquared_adj),
                **{f"b_{name}": v for name, v in zip(["const"] + ["f1","f2","f3","f4","f5"], m.params) if len(m.params)==6},
            }
        )
    return pd.DataFrame(rows).assign(model=label)


def main() -> None:
    gsw = load_gsw_nominal()
    panel = build_monthly_forwards(gsw)
    rx = build_excess_returns(panel)

    print(f"Panel shape: {panel.shape}, rx shape: {rx.shape}")
    print(f"Date range: {panel.index.min():%Y-%m} to {panel.index.max():%Y-%m}")

    summary_rows = []

    for sample_name, sample in SAMPLES.items():
        print(f"\n========== Sample: {sample_name} ({sample[0]} ~ {sample[1]}) ==========")

        # --- (1) Unrestricted CP regression per maturity ---
        unrestr = cp_regression(panel, rx, sample)
        print("\n--- Unrestricted: rx^(n) ~ const + f1..f5 ---")
        for n_str, m in unrestr.items():
            params = m.params
            r2 = m.rsquared
            print(
                f"  rx{n_str:>3}: R²={r2:.3f} | "
                f"b=[{params[0]:+.3f}, "
                + ", ".join(f"{p:+.2f}" for p in params[1:])
                + f"] (n={int(m.nobs)})"
            )
            summary_rows.append(
                {
                    "sample": sample_name,
                    "model": "unrestricted",
                    "maturity": n_str,
                    "R2": r2,
                    "n_obs": int(m.nobs),
                }
            )

        # --- (2) CP factor from rx_avg, then single-factor regression ---
        cp, cp_mdl = extract_cp_factor(panel, rx, sample)
        print(f"\nCP factor extraction R² (rx_avg ~ f1..f5): {cp_mdl.rsquared:.3f}")
        single = single_factor_regression(cp, rx, sample)
        print("\n--- Single-factor: rx^(n) ~ const + cp ---")
        for n_str, m in single.items():
            b1 = m.params[1]
            r2 = m.rsquared
            print(f"  rx{n_str:>3}: b_cp={b1:+.3f}, R²={r2:.3f} (n={int(m.nobs)})")
            summary_rows.append(
                {
                    "sample": sample_name,
                    "model": "cp_single_factor",
                    "maturity": n_str,
                    "R2": r2,
                    "n_obs": int(m.nobs),
                }
            )

        # --- (3) Save tent-shape plot only for paper sample ---
        if sample_name == "cp_paper_1964_2003":
            fig, ax = plt.subplots(figsize=(8, 5))
            xs = ["f1", "f2", "f3", "f4", "f5"]
            for n_str, m in unrestr.items():
                if n_str == "avg":
                    continue
                ax.plot(xs, m.params[1:], marker="o", label=f"rx^({n_str})")
            ax.axhline(0, color="k", linewidth=0.6)
            ax.set_title(
                f"CP regression coefficients — tent shape (sample {sample[0][:4]}-{sample[1][:4]})"
            )
            ax.set_xlabel("Right-hand side variable")
            ax.set_ylabel("Coefficient")
            ax.grid(alpha=0.3)
            ax.legend()
            fig.tight_layout()
            fig.savefig(RESULTS_DIR / f"tent_shape_{sample_name}.png", dpi=130)
            plt.close(fig)

            # Save CP factor time series
            cp.to_frame().to_parquet(RESULTS_DIR / "cp_factor.parquet")

        # --- (4) Save tent-shape plot for full sample too ---
        if sample_name == "full_1971_2025":
            fig, ax = plt.subplots(figsize=(8, 5))
            xs = ["f1", "f2", "f3", "f4", "f5"]
            for n_str, m in unrestr.items():
                if n_str == "avg":
                    continue
                ax.plot(xs, m.params[1:], marker="o", label=f"rx^({n_str})")
            ax.axhline(0, color="k", linewidth=0.6)
            ax.set_title(
                f"CP regression coefficients — full sample 1971-2025"
            )
            ax.set_xlabel("Right-hand side variable")
            ax.set_ylabel("Coefficient")
            ax.grid(alpha=0.3)
            ax.legend()
            fig.tight_layout()
            fig.savefig(RESULTS_DIR / f"tent_shape_{sample_name}.png", dpi=130)
            plt.close(fig)

    # --- Save summary ---
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(RESULTS_DIR / "r2_summary.csv", index=False)
    print("\n=== R² summary ===")
    print(summary.pivot_table(index=["sample", "model"], columns="maturity", values="R2").round(3))

    panel.to_parquet(RESULTS_DIR / "monthly_yields_forwards.parquet")
    rx.to_parquet(RESULTS_DIR / "monthly_excess_returns.parquet")
    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
