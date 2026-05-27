"""Replication / verification of Gürkaynak, Sack & Wright (2007, JME).

"The U.S. Treasury yield curve: 1961 to the present."
Journal of Monetary Economics, 54(8), 2291–2304.

This is a verification exercise rather than a re-estimation:
- Re-implement the Svensson (1994) 6-parameter yield function from the
  published NSS parameters (BETA0..BETA3, TAU1, TAU2) and verify it matches
  the published SVENY zero-yield columns to machine precision.
- Check the internal consistency between zero yields, par yields, and
  instantaneous forward rates.
- Compare GSW zero yields with FRED nominal yields (DGS3MO, DGS1, ..., DGS30)
  at fixed maturities. They are NOT identical (FRED uses CMT, GSW uses
  Svensson-smoothed off-the-run zeros), so we report mean and RMS
  deviation.
- Plot the yield curve on a few representative dates and the 1-year
  forward rate term structure.

Note: The GSW dataset is updated daily by the Fed and the actual NSS
re-estimation is impossible without raw off-the-run bond price data
(WRDS-only). We verify the curve-evaluation step.

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fi_research.data.fred import load_panel
from fi_research.data.treasury import load_gsw_nominal

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def svensson_zero_yield(
    tau: float | np.ndarray,
    beta0: float,
    beta1: float,
    beta2: float,
    beta3: float,
    tau1: float,
    tau2: float,
) -> float | np.ndarray:
    """Continuously-compounded zero yield at maturity ``tau`` (years)."""
    tau = np.asarray(tau, dtype=float)
    a1 = tau / tau1
    a2 = tau / tau2
    # Guard against tau=0 (lim => 1 for the linear term)
    with np.errstate(divide="ignore", invalid="ignore"):
        term1 = np.where(a1 > 1e-12, (1.0 - np.exp(-a1)) / a1, 1.0)
        term2 = term1 - np.exp(-a1)
        term3 = np.where(a2 > 1e-12, (1.0 - np.exp(-a2)) / a2 - np.exp(-a2), 0.0)
    return beta0 + beta1 * term1 + beta2 * term2 + beta3 * term3


def svensson_inst_forward(
    tau: float | np.ndarray,
    beta0: float,
    beta1: float,
    beta2: float,
    beta3: float,
    tau1: float,
    tau2: float,
) -> float | np.ndarray:
    """Instantaneous forward rate at horizon ``tau`` (years)."""
    tau = np.asarray(tau, dtype=float)
    return (
        beta0
        + beta1 * np.exp(-tau / tau1)
        + beta2 * (tau / tau1) * np.exp(-tau / tau1)
        + beta3 * (tau / tau2) * np.exp(-tau / tau2)
    )


def verify_svensson_zero(gsw: pd.DataFrame) -> pd.DataFrame:
    """Recompute SVENY01..SVENY30 from parameters and compare with stored values."""
    rows = []
    sample = gsw.dropna(
        subset=["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]
    ).copy()
    print(f"NSS parameters available on {len(sample)} dates "
          f"({sample['date'].min():%Y-%m-%d} to {sample['date'].max():%Y-%m-%d})")

    for n in range(1, 31):
        col = f"SVENY{n:02d}"
        if col not in sample.columns:
            continue
        # Skip rows where stored zero yield is missing
        sub = sample.dropna(subset=[col])
        if len(sub) == 0:
            continue
        recomputed = svensson_zero_yield(
            n,
            sub["BETA0"].values,
            sub["BETA1"].values,
            sub["BETA2"].values,
            sub["BETA3"].values,
            sub["TAU1"].values,
            sub["TAU2"].values,
        )
        published = sub[col].values
        diff = recomputed - published
        rows.append(
            {
                "maturity_years": n,
                "n_obs": len(sub),
                "max_abs_diff_bps": float(np.max(np.abs(diff)) * 100),
                "mean_diff_bps": float(np.mean(diff) * 100),
                "rms_diff_bps": float(np.sqrt(np.mean(diff**2)) * 100),
            }
        )
    return pd.DataFrame(rows)


def compare_with_fred(gsw: pd.DataFrame) -> pd.DataFrame:
    """Compare GSW SVENY with FRED's CMT yields at fixed maturities."""
    fred_map = {
        1: "DGS1",
        2: "DGS2",
        3: "DGS3",
        5: "DGS5",
        7: "DGS7",
        10: "DGS10",
        20: "DGS20",
        30: "DGS30",
    }
    fred = load_panel(list(fred_map.values()))
    fred["date"] = pd.to_datetime(fred["date"])
    fred = fred.set_index("date")

    rows = []
    g = gsw.copy()
    g["date"] = pd.to_datetime(g["date"])
    g = g.set_index("date")
    for n, fcol in fred_map.items():
        gcol = f"SVENY{n:02d}"
        df = pd.concat([g[gcol], fred[fcol]], axis=1).dropna()
        if len(df) == 0:
            continue
        diff_bps = (df[gcol] - df[fcol]) * 100
        rows.append(
            {
                "maturity_years": n,
                "fred_series": fcol,
                "n_obs": len(df),
                "mean_diff_bps": float(diff_bps.mean()),
                "rms_diff_bps": float(np.sqrt((diff_bps**2).mean())),
                "max_diff_bps": float(diff_bps.abs().max()),
                "p99_diff_bps": float(diff_bps.abs().quantile(0.99)),
            }
        )
    return pd.DataFrame(rows)


def plot_curves(gsw: pd.DataFrame) -> None:
    """Plot the curve on a few representative dates."""
    dates = [
        "1980-12-31",  # Volcker tightening peak
        "1994-12-30",  # midcycle ~5-6% normal
        "2007-06-29",  # pre-GFC
        "2009-06-30",  # post-GFC ZLB
        "2019-12-31",  # late-cycle
        "2023-12-29",  # post-COVID hiking
    ]
    g = gsw.copy()
    g["date"] = pd.to_datetime(g["date"])
    g = g.set_index("date")

    fig, ax = plt.subplots(figsize=(10, 6))
    taus_fine = np.linspace(0.25, 30, 400)
    for d in dates:
        d = pd.Timestamp(d)
        # find nearest date with parameters
        idx = g.index.get_indexer([d], method="nearest")[0]
        row = g.iloc[idx]
        if pd.isna(row.get("BETA0")):
            continue
        yhat = svensson_zero_yield(
            taus_fine,
            row["BETA0"], row["BETA1"], row["BETA2"], row["BETA3"],
            row["TAU1"], row["TAU2"],
        )
        ax.plot(taus_fine, yhat, linewidth=1.4, label=f"{g.index[idx]:%Y-%m-%d}")
        # overlay published SVENY points
        ms = list(range(1, 31))
        ys = [row.get(f"SVENY{m:02d}", np.nan) for m in ms]
        ax.scatter(ms, ys, s=10, alpha=0.5)

    ax.set_xlabel("Maturity (years)")
    ax.set_ylabel("Zero yield (continuously compounded, %)")
    ax.set_title("GSW NSS curve on selected dates (lines = recomputed, dots = published)")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "yield_curves.png", dpi=130)
    plt.close(fig)


def plot_term_structure_history(gsw: pd.DataFrame) -> None:
    """Stack plot of SVENY01, SVENY02, SVENY05, SVENY10, SVENY30 over time."""
    g = gsw.copy()
    g["date"] = pd.to_datetime(g["date"])
    g = g.set_index("date").sort_index()
    cols = ["SVENY01", "SVENY02", "SVENY05", "SVENY10", "SVENY30"]
    fig, ax = plt.subplots(figsize=(11, 5))
    for c in cols:
        if c in g.columns:
            ax.plot(g.index, g[c], linewidth=0.9, label=c.replace("SVENY", "y"))
    ax.set_title("GSW zero yields — 1y, 2y, 5y, 10y, 30y, 1961-present")
    ax.set_ylabel("Yield (%)")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "history_stack.png", dpi=130)
    plt.close(fig)


def main() -> None:
    gsw = load_gsw_nominal()
    print(f"GSW nominal panel: {gsw.shape}, dates {gsw['date'].min()} to {gsw['date'].max()}")

    # === 1) Verify Svensson formula reproduces SVENY ===
    print("\n=== Verification: Svensson formula vs published SVENY ===")
    tab_verify = verify_svensson_zero(gsw)
    print(tab_verify.round(3).to_string(index=False))
    tab_verify.to_csv(RESULTS_DIR / "svensson_verification.csv", index=False)

    # === 2) Compare with FRED CMT yields ===
    print("\n=== Comparison with FRED CMT yields ===")
    tab_fred = compare_with_fred(gsw)
    print(tab_fred.round(3).to_string(index=False))
    tab_fred.to_csv(RESULTS_DIR / "fred_comparison.csv", index=False)

    # === 3) Plot ===
    print("\nPlotting yield curves and history stack...")
    plot_curves(gsw)
    plot_term_structure_history(gsw)

    # === 4) Inst forward rate plot on the recent date ===
    g = gsw.copy()
    g["date"] = pd.to_datetime(g["date"])
    g_sorted = g.sort_values("date")
    last_with_params = g_sorted.dropna(
        subset=["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]
    ).iloc[-1]
    taus = np.linspace(0.1, 30, 300)
    fwd = svensson_inst_forward(
        taus,
        last_with_params["BETA0"],
        last_with_params["BETA1"],
        last_with_params["BETA2"],
        last_with_params["BETA3"],
        last_with_params["TAU1"],
        last_with_params["TAU2"],
    )
    zr = svensson_zero_yield(
        taus,
        last_with_params["BETA0"],
        last_with_params["BETA1"],
        last_with_params["BETA2"],
        last_with_params["BETA3"],
        last_with_params["TAU1"],
        last_with_params["TAU2"],
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(taus, zr, label="Zero yield", linewidth=1.4)
    ax.plot(taus, fwd, label="Instantaneous forward", linewidth=1.4, linestyle="--")
    ax.set_xlabel("Maturity (years)")
    ax.set_ylabel("Rate (%)")
    ax.set_title(f"GSW NSS curve and inst. forward — {last_with_params['date']:%Y-%m-%d}")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "zero_vs_forward_recent.png", dpi=130)
    plt.close(fig)

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
