"""A2 main — Step 1: Monthly MP × regime exposure construction.

Aggregates Bauer-Swanson (2023) FOMC-level orthogonalized MP shocks
(``mps_orth``) and OFR Financial Stress Index (FSI) into monthly series
that can be merged with Robeco factor returns and used as right-hand-side
controls in Step 2 (time-series α tests) and Step 3 (FGX double-selection
LASSO).

Output: ``results/monthly_mp_regime_exposure.parquet``

Columns:
- ``mps_orth_sum``    — sum of ``mps_orth`` over FOMC events in month t
- ``mps_raw_sum``     — same with raw ``mps`` (for robustness)
- ``mps_x_fsi_sum``   — sum of ``mps_orth × FSI_d`` (FSI value at the FOMC day)
- ``mps_x_fsi_z_sum`` — sum of ``mps_orth × FSI_zscore_d`` (z-scored FSI)
- ``mps_event_count`` — number of FOMC events in month t
- ``fsi_eom``         — month-end OFR FSI level
- ``fsi_eom_z``       — z-scored fsi_eom
- ``walcl_yoy``       — Fed BS year-over-year growth (QE proxy)
- ``qe_active``       — 1 if walcl_yoy > 10%

The exposure series are signed so that **positive = contractionary MP
shock**. The ``mps × FSI`` interaction is signed so that **positive value
≈ contractionary shock arriving during stressed times** — which the
derivatives/C.3 finding shows drives spread widening.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fi_research.data.fred import load_panel
from fi_research.data.mp_shocks import load_mp_shocks
from fi_research.data.ofr_fsi import load_ofr_fsi

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    # === Load FOMC-level shocks ===
    fomc = load_mp_shocks("fomc_2023update")
    fomc["date"] = pd.to_datetime(fomc["date"])
    fomc = fomc.set_index("date").sort_index()
    print(f"FOMC events: {len(fomc)} from {fomc.index.min():%Y-%m} to {fomc.index.max():%Y-%m}")
    print(f"  Non-null mps:      {fomc['mps'].notna().sum()}")
    print(f"  Non-null mps_orth: {fomc['mps_orth'].notna().sum()}")

    # === Load OFR FSI (daily, 2000-01+) ===
    ofr = load_ofr_fsi()
    ofr["date"] = pd.to_datetime(ofr["date"])
    ofr = ofr.set_index("date").sort_index()
    fsi = ofr["ofr_fsi"].dropna()
    fsi_mean = fsi.mean()
    fsi_std = fsi.std(ddof=1)
    print(f"OFR FSI: {fsi.index.min():%Y-%m-%d} ~ {fsi.index.max():%Y-%m-%d} "
          f"(mean={fsi_mean:.3f}, std={fsi_std:.3f})")

    # Map each FOMC event to its FSI on that day (or nearest prior business day)
    fomc_fsi = []
    for d in fomc.index:
        prior = fsi.index[fsi.index <= d]
        fomc_fsi.append(float(fsi.loc[prior[-1]]) if len(prior) else np.nan)
    fomc = fomc.assign(fsi_event=fomc_fsi)
    fomc["fsi_event_z"] = (fomc["fsi_event"] - fsi_mean) / fsi_std
    print(f"FOMC events with FSI: {fomc['fsi_event'].notna().sum()} (FSI starts 2000-01)")

    # === Per-event interaction terms ===
    fomc["mps_x_fsi"] = fomc["mps_orth"] * fomc["fsi_event"]
    fomc["mps_x_fsi_z"] = fomc["mps_orth"] * fomc["fsi_event_z"]

    # === Monthly aggregation ===
    # Group by year-month
    grp = fomc.groupby(pd.Grouper(freq="M"))
    monthly = pd.DataFrame({
        "mps_orth_sum":    grp["mps_orth"].sum(min_count=1),
        "mps_raw_sum":     grp["mps"].sum(min_count=1),
        "mps_x_fsi_sum":   grp["mps_x_fsi"].sum(min_count=1),
        "mps_x_fsi_z_sum": grp["mps_x_fsi_z"].sum(min_count=1),
        "mps_event_count": grp["mps_orth"].count(),
    })

    # === Build a full monthly index (1988-01 → 2025-12) and fill zeros for non-event months ===
    full_idx = pd.date_range("1988-01-31", "2025-12-31", freq="M")
    monthly = monthly.reindex(full_idx)
    # Non-event months: mps_event_count=0, sums=0 (no MPS), interactions=0
    monthly["mps_event_count"] = monthly["mps_event_count"].fillna(0).astype(int)
    for col in ["mps_orth_sum", "mps_raw_sum", "mps_x_fsi_sum", "mps_x_fsi_z_sum"]:
        monthly[col] = monthly[col].fillna(0.0)

    # === Add month-end OFR FSI level (NaN before 2000-01) ===
    fsi_eom = fsi.resample("M").last().reindex(full_idx)
    monthly["fsi_eom"] = fsi_eom
    monthly["fsi_eom_z"] = (fsi_eom - fsi_mean) / fsi_std

    # === Fed BS (WALCL) year-over-year + QE flag ===
    walcl = load_panel(["WALCL"])
    walcl["date"] = pd.to_datetime(walcl["date"])
    walcl = walcl.set_index("date").sort_index()
    walcl_m = walcl["WALCL"].resample("M").last()
    walcl_yoy = (walcl_m / walcl_m.shift(12) - 1) * 100
    monthly["walcl_yoy"] = walcl_yoy.reindex(full_idx)
    monthly["qe_active"] = (monthly["walcl_yoy"] > 10).astype(int)

    monthly = monthly.sort_index()
    monthly.index.name = "date"

    monthly.to_parquet(RESULTS_DIR / "monthly_mp_regime_exposure.parquet")
    print(f"\nSaved monthly_mp_regime_exposure.parquet — shape {monthly.shape}")
    print(f"  date range: {monthly.index.min():%Y-%m} ~ {monthly.index.max():%Y-%m}")

    # === Sanity stats ===
    print("\n=== Sanity stats (full monthly panel) ===")
    print(monthly[["mps_orth_sum", "mps_x_fsi_sum", "mps_x_fsi_z_sum",
                   "fsi_eom", "fsi_eom_z", "walcl_yoy", "mps_event_count",
                   "qe_active"]].describe().round(4).to_string())

    print(f"\nMonths with at least one FOMC event:        {(monthly['mps_event_count'] > 0).sum()}")
    print(f"Months in OFR FSI sample (2000-01+):         {monthly['fsi_eom'].notna().sum()}")
    print(f"Months with FOMC event AND FSI value:        "
          f"{((monthly['mps_event_count'] > 0) & monthly['fsi_eom'].notna()).sum()}")
    print(f"Months in QE active state:                   {int(monthly['qe_active'].sum())}")

    # === Quick visual: monthly exposures + Robeco IG MultiFactor ===
    try:
        from fi_research.data.robeco import load_robeco_credit_factors
        ig = load_robeco_credit_factors("IG").set_index("date").sort_index()
        merged = monthly.join(ig["MultiFactor"].rename("ig_mf"), how="inner")
        sample = merged.loc["2000-01-31":]

        fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
        axes[0].plot(sample.index, sample["mps_orth_sum"], color="steelblue", linewidth=0.8)
        axes[0].axhline(0, color="k", linewidth=0.4)
        axes[0].set_title("Monthly mps_orth sum")
        axes[0].set_ylabel("Sum")
        axes[0].grid(alpha=0.3)

        axes[1].plot(sample.index, sample["mps_x_fsi_z_sum"], color="darkorange", linewidth=0.8)
        axes[1].axhline(0, color="k", linewidth=0.4)
        axes[1].set_title("Monthly mps_orth × FSI (z) sum — regime-MP exposure")
        axes[1].set_ylabel("Sum")
        axes[1].grid(alpha=0.3)

        axes[2].plot(sample.index, sample["ig_mf"], color="forestgreen", linewidth=0.8)
        axes[2].axhline(0, color="k", linewidth=0.4)
        axes[2].set_title("Robeco IG MultiFactor monthly return (for context)")
        axes[2].set_ylabel("Return")
        axes[2].grid(alpha=0.3)

        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "exposure_timeseries.png", dpi=130)
        plt.close(fig)

        # Correlation
        corr = sample[["mps_orth_sum", "mps_x_fsi_z_sum", "fsi_eom_z", "ig_mf"]].corr()
        print("\n=== Correlations (2000-01+ monthly, with Robeco IG MultiFactor) ===")
        print(corr.round(3).to_string())
        corr.to_csv(RESULTS_DIR / "exposure_correlations.csv")
    except Exception as e:
        print(f"Visualization skipped: {e}")

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
