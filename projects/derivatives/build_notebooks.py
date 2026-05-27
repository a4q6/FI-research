"""Build thin display notebooks for each derivative analysis."""

from __future__ import annotations

import sys
from pathlib import Path

# Re-use replication notebook builder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "replications"))
from _nb_builder import build_notebook

DERIV = Path(__file__).resolve().parent

ANALYSES = [
    {
        "dir": "a_robeco_credit_pc",
        "nb": "01_credit_pc_orth.ipynb",
        "title": "Bundle A.1: Robeco PC1 直交化",
        "script": "credit_pc_orth.py",
        "tables": [
            "all_stats.csv",
            "exo_credit_orth_IG_paper_1994_2015.csv",
            "exo_credit_orth_HY_paper_1994_2015.csv",
        ],
        "figures": ["ir_4way_comparison.png", "cumret_orth_vs_raw.png"],
        "highlight": (
            "**核心**: BAA10Y proxy 直交化で HvZ 論文 Table 3 IR の 80-100% を回復。"
            "PC1 (endogenous) は内生性で IR を過大評価。"
        ),
    },
    {
        "dir": "a_robeco_credit_pc",
        "nb": "02_stress_drawdowns.ipynb",
        "title": "Bundle A.2: ストレス期 drawdown",
        "script": "stress_drawdowns.py",
        "tables": ["stress_drawdowns.csv"],
        "figures": ["stress_cumret_IG.png", "stress_cumret_HY.png", "max_dd_heatmap.png"],
        "highlight": (
            "**核心**: GFC で HY Size cum ret=+41%、COVID で HY 全因子プラス、2022 で軽傷。"
            "post-BBW 期でもファクタープレミアム未消失を実証。"
        ),
    },
    {
        "dir": "b_post_qe_structural",
        "nb": "01_stress_horse_race.ipynb",
        "title": "Bundle B.1: stress index horse race",
        "script": "ebp_horse_race.py",
        "tables": ["horse_race_results.csv"],
        "figures": ["horse_race_heatmap.png", "horse_race_bars_payroll12m.png"],
        "highlight": (
            "**核心**: pre-2011 で OFR FSI Credit の R²=0.72。post-2011 で 0.00。"
            "9 つ全ての stress index が一斉に崩壊 → 構造変化は EBP 特有ではない。"
        ),
    },
    {
        "dir": "b_post_qe_structural",
        "nb": "02_regime_decomposition.ipynb",
        "title": "Bundle B.2: regime 分解 (NBER × QE)",
        "script": "regime_decomposition.py",
        "tables": ["regime_decomposition.csv"],
        "figures": ["regime_r2_bars.png"],
        "highlight": (
            "**核心**: EBP は QE active 期間で R²=0.51 と最強、平穏時 R²=0.04。"
            "崩壊は post-2011 ではなく「QE 終了後の calm 期」が正体。"
        ),
    },
    {
        "dir": "b_post_qe_structural",
        "nb": "03_cp_rolling.ipynb",
        "title": "Bundle B.3: CP factor rolling regression",
        "script": "cp_rolling.py",
        "tables": ["cp_rolling.csv"],
        "figures": [
            "cp_rolling_r2.png",
            "cp_rolling_coefs_rx5.png",
            "cp_rolling_r2_with_recessions.png",
        ],
        "highlight": (
            "**核心**: 10y rolling window で R² が 0.04 〜 0.91 まで変動。最大は "
            "2007-2017 window、最小は 2014-2024。レジーム依存性を強く示唆。"
        ),
    },
    {
        "dir": "c_mps_credit_transmission",
        "nb": "01_fomc_credit_reaction.ipynb",
        "title": "Bundle C.1: FOMC 日のクレジット反応",
        "script": "baml_oas_fomc_reaction.py",
        "tables": ["fomc_credit_reactions.csv"],
        "figures": ["baa10y_fomc_scatter.png", "credit_coefficients.png"],
        "highlight": (
            "**核心**: 1 日 window で contractionary mps_orth → BAA10Y β=-0.21 (t=-5.6)。"
            "narrowing は curve mechanical 効果。BAA-AAA risk premium は 1 日では反応せず。"
        ),
    },
    {
        "dir": "c_mps_credit_transmission",
        "nb": "02_local_projection.ipynb",
        "title": "Bundle C.2: Jordà 2005 local projection",
        "script": "local_projection.py",
        "tables": ["local_projection_irfs.csv"],
        "figures": ["local_projection_irfs.png", "irf_mps_orth_comparison.png"],
        "highlight": (
            "**核心**: BAA10Y は h=0 で narrowing → h=30 で widening (β=+0.96)。"
            "Treasury は h=2 でピーク後減衰。Gertler-Karadi credit channel の典型パターンを公開データで再現。"
        ),
    },
    {
        "dir": "c_mps_credit_transmission",
        "nb": "03_regime_interaction.ipynb",
        "title": "Bundle C.3: stress regime × MP shock interaction",
        "script": "regime_interaction.py",
        "tables": ["regime_interaction.csv"],
        "figures": ["regime_interaction_irfs.png"],
        "highlight": (
            "**核心 (novel finding)**: MP 伝達が OFR FSI で完全に sign-reversed。"
            "Calm 期は引締め→ narrowing、Stress 期は引締め→ widening。Interaction t>6。"
        ),
    },
]


def make_notebook(a: dict) -> Path:
    paper_dir = DERIV / a["dir"]
    nb_path = paper_dir / "notebooks" / a["nb"]

    md_intro = f"""# {a['title']}

詳細は [README.md](../README.md) を参照。本ノートブックは結果の表示用。

{a['highlight']}
"""

    code_imports = """from __future__ import annotations

from pathlib import Path

import pandas as pd
from IPython.display import Image, Markdown, display

PAPER_DIR = Path("..").resolve()
RESULTS = PAPER_DIR / "results"
SCRIPT = PAPER_DIR / "scripts" / "{script}"

print(f"Paper dir: {{PAPER_DIR}}")
print(f"Results exists: {{RESULTS.exists()}}")
print(f"Script: {{SCRIPT}} exists: {{SCRIPT.exists()}}")
""".format(script=a["script"])

    md_rerun = """## (オプション) 再実行

```bash
python projects/derivatives/{dir}/scripts/{script}
```
""".format(dir=a["dir"], script=a["script"])

    code_tables = "\n".join(
        f"print('=' * 60)\nprint('Table: {t}')\nprint('=' * 60)\n"
        f"display(pd.read_csv(RESULTS / '{t}').head(40))\n"
        for t in a["tables"]
    )

    code_figures = "\n".join(
        f"display(Markdown('### {fig}'))\ndisplay(Image(str(RESULTS / '{fig}')))\n"
        for fig in a["figures"]
    )

    cells = [
        ("markdown", md_intro),
        ("code", code_imports),
        ("markdown", md_rerun),
        ("markdown", "## 結果テーブル"),
        ("code", code_tables),
        ("markdown", "## 図"),
        ("code", code_figures),
    ]
    return build_notebook(cells, nb_path)


def main() -> None:
    for a in ANALYSES:
        out = make_notebook(a)
        print(f"Built {out}")


if __name__ == "__main__":
    main()
