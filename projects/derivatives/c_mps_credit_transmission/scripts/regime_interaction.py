"""Bundle C.3 — MP shock transmission × credit regime interaction.

Local projection (C.2) showed that BAA10Y widens gradually over ~30 days
in response to contractionary mps_orth. This script tests whether the
strength of that transmission depends on the **prevailing credit stress
regime** measured by OFR FSI on the day of the FOMC announcement.

Hypothesis (Gertler-Karadi / financial accelerator): the credit channel
is **stronger in high-stress periods** when intermediary balance sheet
constraints bind. Conversely, when conditions are calm, MP transmits
primarily through rates rather than spreads.

Specification:
    Δspread_{d+h} = α + β_1·mps_orth_d + β_2·mps_orth_d × FSI_d
                  + γ_1·FSI_d + γ_2·controls_d + ε

If β_2 > 0 (for tightening shocks): high stress amplifies credit widening.

We test at h = 5, 15, 30 days; spread = BAA10Y, AAA10Y, BAA-AAA.

Sample: 2000-01 → 2023-12 (OFR FSI starts 2000-01).

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
from fi_research.data.ofr_fsi import load_ofr_fsi

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SERIES = ["BAA10Y", "AAA10Y", "BAA_AAA_spread"]
HORIZONS = [1, 5, 10, 15, 20, 30, 40]


def build_daily_panel() -> pd.DataFrame:
    fred = load_panel(["BAA10Y", "AAA10Y"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date").sort_index()
    fred["BAA_AAA_spread"] = fred["BAA10Y"] - fred["AAA10Y"]
    return fred[SERIES]


def build_fsi_daily() -> pd.Series:
    ofr = load_ofr_fsi()
    ofr["date"] = pd.to_datetime(ofr["date"])
    ofr = ofr.set_index("date").sort_index()
    return ofr["ofr_fsi"]


def compute_event_data(daily: pd.DataFrame, fomc: pd.DataFrame, fsi: pd.Series,
                       series: str, h: int) -> pd.DataFrame:
    daily_s = daily[series].dropna().sort_index()
    rows = []
    for d in fomc.index:
        # FSI value at d (or nearest prior)
        prior_fsi = fsi.index[fsi.index <= d]
        if len(prior_fsi) == 0:
            continue
        fsi_d = float(fsi.loc[prior_fsi[-1]])

        prior_daily = daily_s.index[daily_s.index < d]
        if len(prior_daily) == 0:
            continue
        d_prev = prior_daily[-1]
        v_prev = float(daily_s.loc[d_prev])
        # h-day forward from d_prev (so h=0 means next business day from d-1 = d)
        loc = daily_s.index.get_loc(d_prev)
        if loc + h + 1 >= len(daily_s):
            continue
        v_h = float(daily_s.iloc[loc + h + 1])

        rows.append({
            "date": d,
            "dy": v_h - v_prev,
            "fsi": fsi_d,
            "mps_orth": float(fomc.loc[d, "mps_orth"]) if pd.notna(fomc.loc[d, "mps_orth"]) else np.nan,
            "mps": float(fomc.loc[d, "mps"]) if pd.notna(fomc.loc[d, "mps"]) else np.nan,
            "level_prev": v_prev,
        })
    return pd.DataFrame(rows).dropna()


def main() -> None:
    fomc = load_mp_shocks("fomc_2023update")
    fomc["date"] = pd.to_datetime(fomc["date"])
    fomc = fomc.set_index("date").sort_index()
    daily = build_daily_panel()
    fsi = build_fsi_daily()
    print(f"OFR FSI: {fsi.dropna().index.min():%Y-%m-%d} to {fsi.dropna().index.max():%Y-%m-%d}")

    all_rows = []
    for series in SERIES:
        for h in HORIZONS:
            df = compute_event_data(daily, fomc, fsi, series, h)
            # Filter to OFR FSI sample
            df = df[df["date"] >= "2000-01-01"].copy()
            if len(df) < 50:
                continue
            df["mps_x_fsi"] = df["mps_orth"] * df["fsi"]

            # Interaction regression
            X = sm.add_constant(df[["mps_orth", "fsi", "mps_x_fsi", "level_prev"]])
            m = sm.OLS(df["dy"], X).fit(cov_type="HAC", cov_kwds={"maxlags": max(1, h)})

            # Compute β at low / high FSI (25th / 75th percentile)
            fsi_25 = float(df["fsi"].quantile(0.25))
            fsi_75 = float(df["fsi"].quantile(0.75))
            beta_low = m.params["mps_orth"] + m.params["mps_x_fsi"] * fsi_25
            beta_high = m.params["mps_orth"] + m.params["mps_x_fsi"] * fsi_75
            # SE for these linear combinations: var(a+bc) = var(a) + c²·var(b) + 2c·cov(a,b)
            cov = m.cov_params()
            v_main = cov.loc["mps_orth", "mps_orth"]
            v_int = cov.loc["mps_x_fsi", "mps_x_fsi"]
            c_mi = cov.loc["mps_orth", "mps_x_fsi"]
            se_low = np.sqrt(v_main + fsi_25**2 * v_int + 2 * fsi_25 * c_mi)
            se_high = np.sqrt(v_main + fsi_75**2 * v_int + 2 * fsi_75 * c_mi)

            all_rows.append({
                "series": series,
                "h_days": h,
                "n": int(m.nobs),
                "beta_mps_orth": float(m.params["mps_orth"]),
                "beta_interaction": float(m.params["mps_x_fsi"]),
                "t_interaction": float(m.tvalues["mps_x_fsi"]),
                "fsi_25": fsi_25,
                "fsi_75": fsi_75,
                "beta_at_low_stress": float(beta_low),
                "beta_at_high_stress": float(beta_high),
                "t_at_low": float(beta_low / se_low),
                "t_at_high": float(beta_high / se_high),
                "R2": float(m.rsquared),
            })

    summary = pd.DataFrame(all_rows)
    summary.to_csv(RESULTS_DIR / "regime_interaction.csv", index=False)

    print("\n=== mps_orth × OFR FSI interaction ===")
    for series in SERIES:
        print(f"\n{series}:")
        sub = summary[summary["series"] == series]
        print(f"  {'h':>3s} {'β_main':>9s} {'β_int':>9s} {'t_int':>7s} {'β@lowFSI':>10s} {'β@highFSI':>11s}")
        for _, r in sub.iterrows():
            print(
                f"  {int(r['h_days']):>3d}d "
                f"{r['beta_mps_orth']:+8.3f}  "
                f"{r['beta_interaction']:+8.3f}  "
                f"{r['t_interaction']:+6.2f}  "
                f"{r['beta_at_low_stress']:+9.3f}  "
                f"{r['beta_at_high_stress']:+10.3f}"
            )

    # === Plot: β at low vs high stress, per series, across horizons ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, series in zip(axes, SERIES):
        sub = summary[summary["series"] == series]
        if sub.empty:
            continue
        ax.plot(sub["h_days"], sub["beta_at_low_stress"], marker="o",
                label="low stress (FSI 25%ile)", color="steelblue", linewidth=1.5)
        ax.plot(sub["h_days"], sub["beta_at_high_stress"], marker="s",
                label="high stress (FSI 75%ile)", color="firebrick", linewidth=1.5)
        ax.plot(sub["h_days"], sub["beta_mps_orth"], marker="x",
                label="β_main (at FSI=0)", color="grey", linewidth=1, linestyle="--")
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_title(f"{series}: response to mps_orth at low vs high stress")
        ax.set_xlabel("Horizon (business days)")
        ax.set_ylabel("β (Δspread per unit shock)")
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
    fig.suptitle(
        "MP shock transmission to credit spreads — conditional on OFR FSI stress level\n"
        "(sample 2000-01 → 2023-12)", y=1.02
    )
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "regime_interaction_irfs.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
