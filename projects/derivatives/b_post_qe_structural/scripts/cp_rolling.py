"""Bundle B.3 — Rolling Cochrane-Piazzesi factor regression.

The CP (2005) replication showed R² 0.20-0.26 over the paper sample
(1964-2003) but only 0.13 over the full 1971-2025 sample. To diagnose
whether this is a smooth decline or driven by a few regime breaks, we
estimate the CP regression on a rolling 120-month (10-year) window:

    rx^(n)_{t+12} ~ const + f1 + f2 + f3 + f4 + f5

ending at month t, with n ∈ {2, 3, 4, 5, avg}. We track:
- R² over time
- The 5 coefficients (tent-shape variation)
- The implied "CP factor" itself recomputed at each window

Outputs: ``results/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from fi_research.data.treasury import load_gsw_nominal

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MATURITIES_RX = [2, 3, 4, 5]


def build_monthly_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    gsw = load_gsw_nominal()
    df = gsw[["date"] + [f"SVENY{n:02d}" for n in [1, 2, 3, 4, 5]]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna().set_index("date").sort_index()
    me = df.resample("M").last() / 100.0
    me.columns = [f"y{n}" for n in [1, 2, 3, 4, 5]]
    p = pd.DataFrame({f"p{n}": -n * me[f"y{n}"] for n in [1, 2, 3, 4, 5]})

    # Forwards
    fwd = pd.DataFrame(index=me.index)
    fwd["f1"] = me["y1"]
    for n in [2, 3, 4, 5]:
        fwd[f"f{n}"] = p[f"p{n - 1}"] - p[f"p{n}"]
    panel = me.join(p).join(fwd)

    rx = pd.DataFrame(index=me.index)
    for n in MATURITIES_RX:
        rx[f"rx{n}"] = p[f"p{n - 1}"].shift(-12) - p[f"p{n}"] - me["y1"]
    rx["rxavg"] = rx[[f"rx{n}" for n in MATURITIES_RX]].mean(axis=1)
    return panel, rx


def rolling_cp(panel: pd.DataFrame, rx: pd.DataFrame, window: int = 120) -> pd.DataFrame:
    """Rolling window CP regression. Output: month-end → R² and coefficients."""
    X_cols = ["f1", "f2", "f3", "f4", "f5"]
    df = panel.join(rx, how="inner").dropna()
    dates = df.index
    rows = []
    for t_end_pos in range(window, len(dates)):
        t_end = dates[t_end_pos]
        sub = df.iloc[t_end_pos - window : t_end_pos]
        for n in MATURITIES_RX + ["avg"]:
            y_col = f"rx{n}"
            try:
                Xm = sm.add_constant(sub[X_cols].values)
                m = sm.OLS(sub[y_col].values, Xm).fit()
                rows.append({
                    "date": t_end,
                    "maturity": str(n),
                    "R2": float(m.rsquared),
                    "n_obs": int(m.nobs),
                    "b_const": float(m.params[0]),
                    "b_f1": float(m.params[1]),
                    "b_f2": float(m.params[2]),
                    "b_f3": float(m.params[3]),
                    "b_f4": float(m.params[4]),
                    "b_f5": float(m.params[5]),
                })
            except Exception:
                continue
    return pd.DataFrame(rows)


def main() -> None:
    panel, rx = build_monthly_panel()
    print(f"Panel: {panel.shape}, rx: {rx.shape}")
    print(f"Date range: {panel.index.min():%Y-%m} to {panel.index.max():%Y-%m}")

    print("\n--- Rolling 10y window CP regression ---")
    roll = rolling_cp(panel, rx, window=120)
    print(f"Rolling output rows: {len(roll)}")
    roll.to_parquet(RESULTS_DIR / "cp_rolling.parquet")
    roll.to_csv(RESULTS_DIR / "cp_rolling.csv", index=False)

    # === Plot 1: R² over time for n=2,3,4,5,avg ===
    fig, ax = plt.subplots(figsize=(11, 5))
    for n in MATURITIES_RX + ["avg"]:
        sub = roll[roll["maturity"] == str(n)]
        ax.plot(sub["date"], sub["R2"], linewidth=1.2,
                label=f"rx^({n})" if n != "avg" else "rx_avg")
    ax.set_title("CP regression rolling 10y R² — rx^(n) ~ const + f1..f5\n(window end on x-axis)")
    ax.set_ylabel("R²")
    ax.set_ylim(-0.05, 1.0)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "cp_rolling_r2.png", dpi=130)
    plt.close(fig)

    # === Plot 2: rolling coefficients of rx^(5) ===
    fig, axes = plt.subplots(5, 1, figsize=(11, 11), sharex=True)
    sub = roll[roll["maturity"] == 5]
    for ax, col, label in zip(axes,
                              ["b_f1", "b_f2", "b_f3", "b_f4", "b_f5"],
                              ["y_t^(1)", "f_t^(2)", "f_t^(3)", "f_t^(4)", "f_t^(5)"]):
        ax.plot(sub["date"], sub[col], linewidth=1.0)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.set_ylabel(f"β on {label}")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Window end date")
    fig.suptitle("Rolling 10y CP regression coefficients for rx^(5)")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "cp_rolling_coefs_rx5.png", dpi=130)
    plt.close(fig)

    # === Plot 3: rolling R² with NBER shading ===
    fig, ax = plt.subplots(figsize=(11, 5))
    avg = roll[roll["maturity"] == "avg"]
    ax.plot(avg["date"], avg["R2"], linewidth=1.4, color="steelblue", label="rx_avg R²")
    ax.set_title("Rolling 10y R² of CP regression (rx_avg)")
    ax.set_ylabel("R²")
    ax.grid(alpha=0.3)
    ax.legend()

    # Add NBER shading
    from fi_research.data.fred import load_panel
    usrec = load_panel(["USREC"])
    usrec["date"] = pd.to_datetime(usrec["date"])
    usrec = usrec.set_index("date")["USREC"].resample("M").last().dropna()
    in_rec = False
    rec_start = None
    for d, v in usrec.items():
        if v == 1 and not in_rec:
            rec_start = d
            in_rec = True
        elif v == 0 and in_rec:
            ax.axvspan(rec_start, d, color="lightgrey", alpha=0.4)
            in_rec = False
    if in_rec:
        ax.axvspan(rec_start, usrec.index[-1], color="lightgrey", alpha=0.4)

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "cp_rolling_r2_with_recessions.png", dpi=130)
    plt.close(fig)

    # === Headline summary stats ===
    print("\n=== Summary stats per maturity ===")
    for n in MATURITIES_RX + ["avg"]:
        sub = roll[roll["maturity"] == str(n)]
        print(
            f"  n={n}: R² mean={sub['R2'].mean():.3f}, "
            f"std={sub['R2'].std():.3f}, "
            f"min={sub['R2'].min():.3f} at {sub.loc[sub['R2'].idxmin(), 'date']:%Y-%m}, "
            f"max={sub['R2'].max():.3f} at {sub.loc[sub['R2'].idxmax(), 'date']:%Y-%m}"
        )

    print("\nDone. Results in", RESULTS_DIR)


if __name__ == "__main__":
    main()
