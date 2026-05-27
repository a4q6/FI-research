"""Bundle C.1 — Credit spread reaction to MPS on FOMC days.

The Bauer-Swanson replication showed that raw mps and orthogonalized
mps_orth produce nearly identical Treasury-yield reactions on FOMC days
(β diff < 0.02). Does the same hold for **credit risk premia**?

Two questions:
1. Do investment-grade and high-grade credit spreads contract or expand
   on contractionary MP surprises? (The "credit channel" predicts that
   tightening → spread widening; the "risk-taking channel" predicts the
   opposite in some scenarios.)
2. Does the contemporaneous credit reaction differ between raw mps and
   mps_orth — i.e., is the credit reaction driven by the "Fed response
   to news" component or the pure MP component?

Data caveats:
- BAML OAS via FRED has only ~3 years (license limit). We use BAA10Y
  (Moody's BAA corporate yield minus 10y Treasury, 1986+) and AAA10Y
  (Moody's AAA minus 10y, 1983+) as long-history substitutes.
- BAA-AAA spread captures the risk-premium portion within IG.
- HY OAS is not available with long history; HY analysis is omitted.

Methodology: on each FOMC date d, compute Δspread_d = spread_{d} −
spread_{d−1} (close-to-close 1-day change). Regress on mps and on
mps_orth. This is daily (not 30-min like Treasuries) so we cannot use
intraday windows but the daily change still isolates the FOMC announcement
effect well for non-noisy event-window methodology.

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

SAMPLES = {
    "paper_full_1988_2019": ("1988-01-01", "2019-12-31"),
    "incl_covid_1988_2023": ("1988-01-01", "2023-12-31"),
}


def build_credit_panel() -> pd.DataFrame:
    """Daily panel of BAA10Y, AAA10Y, BAA-AAA risk premium spread, and
    BAML OAS (only 2023+)."""
    fred = load_panel(["BAA10Y", "AAA10Y", "BAMLC0A0CM", "BAMLH0A0HYM2"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index()
    fred["BAA_AAA_spread"] = fred["BAA10Y"] - fred["AAA10Y"]
    return fred


def event_window_changes(daily: pd.DataFrame, fomc_dates: pd.Series, window: int = 1) -> pd.DataFrame:
    """For each FOMC date d, compute Δseries = series[d] − series[d−window]
    using business-day-aware lookup (last available value)."""
    out = []
    daily_sorted = daily.sort_index()
    for d in fomc_dates:
        if d not in daily_sorted.index:
            # Find nearest prior business day
            prior_dates = daily_sorted.index[daily_sorted.index <= d]
            if len(prior_dates) == 0:
                continue
            d_actual = prior_dates[-1]
        else:
            d_actual = d
        # Day before (last available business day strictly before d)
        prior_dates = daily_sorted.index[daily_sorted.index < d]
        if len(prior_dates) < window:
            continue
        d_prev = prior_dates[-window]
        row_d = daily_sorted.loc[d_actual]
        row_prev = daily_sorted.loc[d_prev]
        out.append({
            "event_date": d,
            "d_actual": d_actual,
            "d_prev": d_prev,
            **{f"d_{col}": row_d[col] - row_prev[col] for col in daily.columns},
        })
    return pd.DataFrame(out)


def regress_change_on_shock(events_df: pd.DataFrame, shocks_df: pd.DataFrame,
                             sample: tuple[str, str]) -> pd.DataFrame:
    """Regress each `d_<series>` on `mps` and `mps_orth` separately."""
    start, end = sample
    merged = events_df.merge(
        shocks_df.reset_index()[["date", "mps", "mps_orth"]],
        left_on="event_date", right_on="date", how="inner",
    )
    merged = merged[(merged["event_date"] >= start) & (merged["event_date"] <= end)]
    # Only numeric change columns (exclude d_actual, d_prev which are datetimes)
    change_cols = [
        c for c in events_df.columns
        if c.startswith("d_") and c not in ("d_actual", "d_prev")
        and pd.api.types.is_numeric_dtype(events_df[c])
    ]
    rows = []
    for col in change_cols:
        for shock in ["mps", "mps_orth"]:
            sub = merged[[col, shock]].dropna()
            if len(sub) < 20:
                continue
            X = sm.add_constant(sub[shock])
            m = sm.OLS(sub[col], X).fit(cov_type="HC1")
            rows.append({
                "series": col.replace("d_", ""),
                "shock": shock,
                "coef": float(m.params[shock]),
                "se": float(m.bse[shock]),
                "t": float(m.tvalues[shock]),
                "R2": float(m.rsquared),
                "n_obs": int(m.nobs),
            })
    return pd.DataFrame(rows)


def main() -> None:
    fomc = load_mp_shocks("fomc_2023update")
    fomc["date"] = pd.to_datetime(fomc["date"])
    fomc = fomc.set_index("date").sort_index()
    print(f"FOMC events: {len(fomc)} from {fomc.index.min():%Y-%m} to {fomc.index.max():%Y-%m}")

    daily = build_credit_panel()
    print(f"Credit panel: {daily.shape}, cols: {list(daily.columns)}")
    print("Credit series first / last:")
    for col in daily.columns:
        s = daily[col].dropna()
        print(f"  {col:18s}: {s.index.min():%Y-%m-%d} ~ {s.index.max():%Y-%m-%d} (n={len(s)})")

    # Event-window changes (1-day)
    events = event_window_changes(daily, pd.Series(fomc.index), window=1)
    events.to_parquet(RESULTS_DIR / "fomc_event_changes.parquet")
    print(f"\nEvent changes: {len(events)} FOMC events with at least one available change")

    all_results = []
    for sample_name, sample in SAMPLES.items():
        print(f"\n========== Sample {sample_name} ==========")
        tab = regress_change_on_shock(events, fomc, sample)
        tab["sample"] = sample_name
        all_results.append(tab)
        for series in tab["series"].unique():
            print(f"  {series}:")
            for shock in ["mps", "mps_orth"]:
                row = tab[(tab["series"] == series) & (tab["shock"] == shock)]
                if len(row):
                    r = row.iloc[0]
                    print(
                        f"    {shock:10s}: β={r['coef']:+7.3f} (t={r['t']:+5.2f}), "
                        f"R²={r['R2']:.3f}, n={int(r['n_obs'])}"
                    )

    summary = pd.concat(all_results, ignore_index=True)
    summary.to_csv(RESULTS_DIR / "fomc_credit_reactions.csv", index=False)

    # === Scatter plot: BAA10Y change vs mps_orth ===
    merged = events.merge(
        fomc.reset_index()[["date", "mps", "mps_orth"]],
        left_on="event_date", right_on="date", how="inner",
    )
    sub_paper = merged[
        (merged["event_date"] >= "1988-01-01") & (merged["event_date"] <= "2019-12-31")
    ].dropna(subset=["d_BAA10Y", "mps", "mps_orth"])
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, shock, title in zip(
        axes, ["mps", "mps_orth"], ["Raw MPS", "Orthogonalized MPS (BS 2023)"]
    ):
        ax.scatter(sub_paper[shock], sub_paper["d_BAA10Y"] * 100, s=14, alpha=0.6,
                   color="steelblue")
        X = sm.add_constant(sub_paper[shock])
        m = sm.OLS(sub_paper["d_BAA10Y"] * 100, X).fit()
        xs = np.linspace(sub_paper[shock].min(), sub_paper[shock].max(), 20)
        ax.plot(xs, m.params[0] + m.params[1] * xs, color="firebrick", linewidth=1.5)
        ax.axhline(0, color="k", linewidth=0.4)
        ax.axvline(0, color="k", linewidth=0.4)
        ax.set_xlabel(f"{shock}")
        ax.set_ylabel("Δ BAA10Y (bps) — 1-day change around FOMC")
        ax.set_title(f"{title}\nβ = {m.params[1]:+.2f} bps per shock, t = {m.tvalues[1]:+.2f}, R²={m.rsquared:.3f}")
        ax.grid(alpha=0.3)
    fig.suptitle("Credit spread (BAA10Y) reaction to MP shock on FOMC days")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "baa10y_fomc_scatter.png", dpi=130)
    plt.close(fig)

    # === Coefficient bar chart by series ===
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, sample_name in zip(axes, ["paper_full_1988_2019", "incl_covid_1988_2023"]):
        sub = summary[summary["sample"] == sample_name]
        # Order series
        series_order = ["AAA10Y", "BAA10Y", "BAA_AAA_spread", "BAMLC0A0CM", "BAMLH0A0HYM2"]
        series_order = [s for s in series_order if s in sub["series"].unique()]
        x = np.arange(len(series_order))
        width = 0.35
        for i, shock in enumerate(["mps", "mps_orth"]):
            coefs = []
            for s in series_order:
                row = sub[(sub["series"] == s) & (sub["shock"] == shock)]
                coefs.append(float(row["coef"].iloc[0]) if len(row) else np.nan)
            ax.bar(x + (i - 0.5) * width, coefs, width, label=shock)
        ax.set_xticks(x)
        ax.set_xticklabels(series_order, rotation=20)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_title(f"{sample_name}")
        ax.set_ylabel("β (Δspread per unit shock, units of original spread)")
        ax.legend()
        ax.grid(alpha=0.3, axis="y")
    fig.suptitle("Credit spread coefficients on MP shock — by series and sample", y=1.02)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "credit_coefficients.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
