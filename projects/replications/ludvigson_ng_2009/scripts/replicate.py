"""Replication of Ludvigson & Ng (2009, RFS).

"Macro Factors in Bond Risk Premia." Review of Financial Studies 22(12),
5027-5067.

Replication scope:
- Stationarize a panel of FRED macro series and extract PCA factors F1..F5.
- Augment the Cochrane-Piazzesi (2005) forecasting regression with macro
  factors:  rx^(n)_{t+12} ~ const + CP_t + F1_t + ... + F5_t.
- Compare R^2 vs CP-only and report the LN "macro spanning" residual.
- Examine factor loadings to characterize what each PC captures.

Note on scope:
- Ludvigson-Ng used a 132-series macro panel ("Stock-Watson style").
  We restrict to ~12 long-history FRED series. The PCs are therefore
  coarser than LN's F1-F8 but capture the same dominant comovement
  (real activity, prices, financial stress).
- We re-use the CP factor saved by the cochrane_piazzesi_2005 replication.

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
from fi_research.data.treasury import load_gsw_nominal

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CP_RESULTS = (
    Path(__file__).resolve().parent.parent.parent
    / "cochrane_piazzesi_2005"
    / "results"
)

# Macro panel — long-history FRED series. Each transformed to a stationary form.
# code: 1=level (Δ), 2=log level (Δlog), 3=already stationary (use level)
MACRO_TRANSFORMS = {
    "INDPRO":   ("dlog", "Industrial production"),
    "PAYEMS":   ("dlog", "Nonfarm payrolls"),
    "UNRATE":   ("diff", "Unemployment rate"),
    "CPIAUCSL": ("dlog", "CPI all urban"),
    "PCEPI":    ("dlog", "PCE price index"),
    "DFF":      ("diff", "Federal funds rate"),
    "DGS10":    ("diff", "10y Treasury"),
    "T10Y3M":   ("level", "Term spread 10y-3m"),
    "T10Y2Y":   ("level", "Term spread 10y-2y"),
    "BAA10Y":   ("level", "BAA-10y spread"),
    "AAA10Y":   ("level", "AAA-10y spread"),
}
NUM_FACTORS = 5

MATURITIES = [2, 3, 4, 5]
SAMPLES = {
    "ln_paper_1964_2007": ("1964-01-01", "2007-12-31"),
    "post_paper_2008_2025": ("2008-01-01", "2025-12-31"),
    "full_1973_2025": ("1973-01-01", "2025-12-31"),
}


def build_macro_factors(start: str = "1959-01-01") -> tuple[pd.DataFrame, PCA, list]:
    """Return monthly DataFrame of F1..F_K, fitted PCA, and the input variable labels."""
    raw = load_panel(list(MACRO_TRANSFORMS.keys()))
    raw = raw.set_index("date") if "date" in raw.columns else raw
    raw.index = pd.to_datetime(raw.index)

    monthly = raw.resample("M").last()
    monthly = monthly.loc[start:].copy()

    # Apply transformations
    transformed = pd.DataFrame(index=monthly.index)
    labels = []
    for col, (how, _label) in MACRO_TRANSFORMS.items():
        s = monthly[col]
        if how == "dlog":
            transformed[col] = np.log(s).diff() * 100
        elif how == "diff":
            transformed[col] = s.diff()
        else:
            transformed[col] = s
        labels.append(col)

    transformed = transformed.dropna(how="all")

    # Drop initial rows until all columns are non-null
    full = transformed.dropna()
    print(f"Macro panel for PCA: {full.shape} from {full.index.min():%Y-%m} to {full.index.max():%Y-%m}")

    scaler = StandardScaler()
    X = scaler.fit_transform(full.values)

    pca = PCA(n_components=NUM_FACTORS)
    F = pca.fit_transform(X)
    factors = pd.DataFrame(
        F, index=full.index, columns=[f"F{i + 1}" for i in range(NUM_FACTORS)]
    )

    return factors, pca, labels


def build_excess_returns_from_gsw() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Re-build the CP excess return panel (monthly)."""
    gsw = load_gsw_nominal()
    df = gsw[["date"] + [f"SVENY{n:02d}" for n in [1, 2, 3, 4, 5]]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna().set_index("date").sort_index()
    me = df.resample("M").last() / 100.0
    me.columns = [f"y{n}" for n in [1, 2, 3, 4, 5]]
    p = pd.DataFrame({f"p{n}": -n * me[f"y{n}"] for n in [1, 2, 3, 4, 5]})

    rx = pd.DataFrame(index=me.index)
    for n in [2, 3, 4, 5]:
        rx[f"rx{n}"] = p[f"p{n - 1}"].shift(-12) - p[f"p{n}"] - me["y1"]
    rx["rxavg"] = rx[[f"rx{n}" for n in [2, 3, 4, 5]]].mean(axis=1)
    return me, rx


def load_cp_factor() -> pd.Series:
    if not (CP_RESULTS / "cp_factor.parquet").exists():
        raise RuntimeError(
            "Run cochrane_piazzesi_2005/scripts/replicate.py first to produce cp_factor.parquet"
        )
    cp = pd.read_parquet(CP_RESULTS / "cp_factor.parquet")
    cp = cp.iloc[:, 0]
    cp.name = "cp"
    return cp


def fit_regressions(
    rx: pd.DataFrame, cp: pd.Series, factors: pd.DataFrame, sample: tuple[str, str]
) -> dict:
    start, end = sample
    out = {}
    F_cols = list(factors.columns)
    for n in [2, 3, 4, 5, "avg"]:
        y_col = f"rx{n}" if n != "avg" else "rxavg"
        df = pd.concat([cp, factors, rx[y_col]], axis=1).loc[start:end].dropna()
        if len(df) < 50:
            continue
        # CP only
        Xcp = sm.add_constant(df[["cp"]].values)
        m_cp = sm.OLS(df[y_col].values, Xcp).fit(cov_type="HAC", cov_kwds={"maxlags": 18})
        # Macro only
        Xm = sm.add_constant(df[F_cols].values)
        m_macro = sm.OLS(df[y_col].values, Xm).fit(cov_type="HAC", cov_kwds={"maxlags": 18})
        # CP + macro
        Xboth = sm.add_constant(df[["cp"] + F_cols].values)
        m_both = sm.OLS(df[y_col].values, Xboth).fit(cov_type="HAC", cov_kwds={"maxlags": 18})
        out[str(n)] = {"cp_only": m_cp, "macro_only": m_macro, "cp_plus_macro": m_both}
    return out


def main() -> None:
    factors, pca, labels = build_macro_factors()
    factors.to_parquet(RESULTS_DIR / "macro_factors.parquet")

    print("\nExplained variance ratio:", pca.explained_variance_ratio_.round(3))
    print("Cumulative:", pca.explained_variance_ratio_.cumsum().round(3))

    # Loadings
    loadings = pd.DataFrame(
        pca.components_.T,
        index=labels,
        columns=[f"F{i + 1}" for i in range(NUM_FACTORS)],
    )
    loadings.to_csv(RESULTS_DIR / "pca_loadings.csv")
    print("\nLoadings:")
    print(loadings.round(2).to_string())

    yields, rx = build_excess_returns_from_gsw()
    cp = load_cp_factor()

    rows = []
    for sample_name, sample in SAMPLES.items():
        print(f"\n========== Sample {sample_name} ({sample[0]} ~ {sample[1]}) ==========")
        res = fit_regressions(rx, cp, factors, sample)
        for n_str, models in res.items():
            for label, m in models.items():
                rows.append(
                    {
                        "sample": sample_name,
                        "maturity": n_str,
                        "model": label,
                        "R2": m.rsquared,
                        "R2_adj": m.rsquared_adj,
                        "n_obs": int(m.nobs),
                    }
                )
            print(
                f"  rx{n_str:>3}: "
                f"R² CP={models['cp_only'].rsquared:.3f}, "
                f"macro={models['macro_only'].rsquared:.3f}, "
                f"CP+macro={models['cp_plus_macro'].rsquared:.3f}, "
                f"Δ(CP→both)={models['cp_plus_macro'].rsquared - models['cp_only'].rsquared:+.3f}"
            )

    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS_DIR / "r2_summary.csv", index=False)

    # === Plot factor time series ===
    fig, ax = plt.subplots(figsize=(11, 5))
    factors.plot(ax=ax, linewidth=0.8)
    ax.set_title("Ludvigson-Ng style macro PCA factors (FRED 11-variable panel)")
    ax.set_ylabel("Standardized PC score")
    ax.axhline(0, color="k", linewidth=0.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "macro_factors_ts.png", dpi=130)
    plt.close(fig)

    # === R² comparison bar chart ===
    pivot = summary.pivot_table(
        index=["sample", "maturity"], columns="model", values="R2"
    ).reset_index()
    # Filter avg rows for cleanest comparison plot
    avg_only = pivot[pivot["maturity"] == "avg"]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(avg_only))
    width = 0.25
    for i, col in enumerate(["cp_only", "macro_only", "cp_plus_macro"]):
        ax.bar(x + (i - 1) * width, avg_only[col].values, width, label=col)
    ax.set_xticks(x)
    ax.set_xticklabels(avg_only["sample"], rotation=20)
    ax.set_ylabel("R²")
    ax.set_title("rx_avg^(2..5) — R² with CP only / macro only / CP + macro")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "r2_comparison.png", dpi=130)
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
