"""Generate thin display notebooks for each replication.

Each notebook is a slim wrapper that:
- Shows the paper context (markdown linking to README.md)
- Re-runs the replication script (idempotent — results already on disk)
- Loads result CSVs and PNGs from ``results/`` for inline display

Run:
    python projects/replications/build_notebooks.py
"""

from __future__ import annotations

from pathlib import Path

from _nb_builder import build_notebook

REPL = Path(__file__).resolve().parent

PAPERS = [
    {
        "dir": "cochrane_piazzesi_2005",
        "nb": "01_cp2005_replication.ipynb",
        "title": "Cochrane & Piazzesi (2005) 再現",
        "citation": "Cochrane, J. H., & Piazzesi, M. (2005). Bond Risk Premia. *AER*, 95(1), 138-160.",
        "tables_csv": ["r2_summary.csv"],
        "figures": [
            "tent_shape_cp_paper_1964_2003.png",
            "tent_shape_full_1971_2025.png",
        ],
        "highlight": (
            "**核心**: 単一ファクター制約 `unrestricted R² ≈ single-factor R²` が"
            "全サンプル・全満期で成立。論文の主要結論は再現できた一方、絶対 R² は "
            "GSW vs Fama-Bliss の手法差で論文より 10pt 低い。"
        ),
    },
    {
        "dir": "ludvigson_ng_2009",
        "nb": "01_ln2009_replication.ipynb",
        "title": "Ludvigson & Ng (2009) 再現",
        "citation": "Ludvigson, S. C., & Ng, S. (2009). Macro Factors in Bond Risk Premia. *RFS*, 22(12), 5027-5067.",
        "tables_csv": ["pca_loadings.csv", "r2_summary.csv"],
        "figures": ["macro_factors_ts.png", "r2_comparison.png"],
        "highlight": (
            "**核心**: マクロ PCA 因子は CP factor を超える追加情報を持つ "
            "(+9〜+14 ポイント ΔR²)。ポスト QE 期 (2008-2025) では macro factors "
            "の方が CP factor より強い予測力。"
        ),
    },
    {
        "dir": "houweling_vanzundert_2017",
        "nb": "01_hvz2017_replication.ipynb",
        "title": "Houweling & van Zundert (2017) 再現",
        "citation": "Houweling, P., & van Zundert, J. (2017). Factor Investing in the Corporate Bond Market. *FAJ*, 73(2), 100-115.",
        "tables_csv": [
            "table3_IG_paper_1994_2015.csv",
            "table3_HY_paper_1994_2015.csv",
            "table3_IG_full_1994_2025.csv",
            "table3_HY_full_1994_2025.csv",
            "corr_IG_full.csv",
            "corr_HY_full.csv",
        ],
        "figures": ["cumret_IG.png", "cumret_HY.png"],
        "highlight": (
            "**核心**: IG / HY ともに Size / Low-Risk / Value / Momentum すべてで "
            "正の超過リターン。フルサンプル 1994-2025 では HY 全ファクターの t-stat が "
            "2.7 以上で有意 → **post-BBW でも社債ファクタープレミアムは消失していない**。"
        ),
    },
    {
        "dir": "gilchrist_zakrajsek_2012",
        "nb": "01_gz2012_replication.ipynb",
        "title": "Gilchrist & Zakrajšek (2012) 再現",
        "citation": "Gilchrist, S., & Zakrajšek, E. (2012). Credit Spreads and Business Cycle Fluctuations. *AER*, 102(4), 1692-1720.",
        "tables_csv": ["predictive_regressions.csv"],
        "figures": ["ebp_timeseries.png", "predictive_r2_heatmap.png"],
        "highlight": (
            "**核心**: 論文期間 (1973-2010) で EBP は IP / Payroll / UR を強く予測 "
            "(R² 25-60%, t-stat 5-10)。**論文後 (2011-2025) で予測力が完全に崩壊** "
            "(R² ≈ 0, 全係数 insignificant) → QE による構造変化を示唆。"
        ),
    },
    {
        "dir": "bauer_swanson_2023",
        "nb": "01_bs2023_replication.ipynb",
        "title": "Bauer & Swanson (2023) 再現",
        "citation": "Bauer, M. D., & Swanson, E. T. (2023). An Alternative Explanation for the 'Fed Information Effect'. *AER*, 113(3), 664-700.",
        "tables_csv": ["predictability_mps.csv", "shock_response.csv"],
        "figures": ["info_effect_scatter.png", "response_coefficients.png"],
        "highlight": (
            "**核心**: raw mps は 6 つの事前マクロ変数で予測可能 (R²=0.156, p<0.0001)。"
            "mps_orth は予測不可能 (R²=0.001) → 直交化が機能。Treasury yield 反応は "
            "両者でほぼ同一 (β diff < 0.02) → 構造的 MP 効果は保存される。"
        ),
    },
    {
        "dir": "gurkaynak_sack_wright_2007",
        "nb": "01_gsw2007_verification.ipynb",
        "title": "Gürkaynak, Sack & Wright (2007) 検証",
        "citation": "Gürkaynak, R. S., Sack, B., & Wright, J. H. (2007). The U.S. Treasury yield curve: 1961 to the present. *JME*, 54(8), 2291-2304.",
        "tables_csv": ["svensson_verification.csv", "fred_comparison.csv"],
        "figures": [
            "yield_curves.png",
            "history_stack.png",
            "zero_vs_forward_recent.png",
        ],
        "highlight": (
            "**核心**: Svensson 公式と公開 SVENY は **数値誤差レベル (RMS 0.002 bps, max 0.04 bps)** "
            "で完全一致 → GSW データの内部整合性は完璧。FRED CMT との差は 5-15 bps の "
            "系統的パターン（複利規約 + on-the-run プレミアム）。"
        ),
    },
]


def make_notebook(paper: dict) -> Path:
    paper_dir = REPL / paper["dir"]
    nb_path = paper_dir / "notebooks" / paper["nb"]

    md_intro = f"""# {paper['title']}

> {paper['citation']}

詳細は [README.md](../README.md) を参照。本ノートブックは結果の表示用。

{paper['highlight']}
"""

    code_imports = """from __future__ import annotations

from pathlib import Path

import pandas as pd
from IPython.display import Image, Markdown, display

# Repository-relative paths
PAPER_DIR = Path.cwd() if (Path.cwd().name == "{dir_name}") else Path("..").resolve()
RESULTS = PAPER_DIR / "results"
SCRIPT = PAPER_DIR / "scripts" / "replicate.py"

# Sanity check
print(f"Paper dir: {{PAPER_DIR}}")
print(f"Results dir exists: {{RESULTS.exists()}}")
print(f"Script: {{SCRIPT}} exists: {{SCRIPT.exists()}}")
""".format(dir_name=paper["dir"])

    md_rerun = """## (オプション) 再実行

未実行 or データ更新後に走らせる。既存結果があればスキップしてよい。

```bash
python projects/replications/{dir}/scripts/replicate.py
```
""".format(dir=paper["dir"])

    md_tables = "## 結果テーブル"
    code_tables = "\n".join(
        [
            f"print('=' * 60)\nprint('Table: {csv}')\nprint('=' * 60)\n"
            f"display(pd.read_csv(RESULTS / '{csv}'))\n"
            for csv in paper["tables_csv"]
        ]
    )

    md_figures = "## 図"
    code_figures = "\n".join(
        [
            f"display(Markdown('### {fig}'))\ndisplay(Image(str(RESULTS / '{fig}')))\n"
            for fig in paper["figures"]
        ]
    )

    cells = [
        ("markdown", md_intro),
        ("code", code_imports),
        ("markdown", md_rerun),
        ("markdown", md_tables),
        ("code", code_tables),
        ("markdown", md_figures),
        ("code", code_figures),
    ]
    build_notebook(cells, nb_path)
    return nb_path


def main() -> None:
    for paper in PAPERS:
        out = make_notebook(paper)
        print(f"Built {out}")


if __name__ == "__main__":
    main()
