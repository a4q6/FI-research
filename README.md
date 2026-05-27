# FI-research

社会人博士進学を見据えた **債券（Fixed Income）リサーチ** のリポジトリ。
公開データ + 大学経由 WRDS のみで完結させる方針（業務データは持ち込まない）。

詳細な研究計画・先行研究・データソース一覧は [`docs/handover.md`](docs/handover.md)。

## 最有力テーマ

- **A1: SHAP 値ベースの債券アトリビューション** — 非線形要因の事後分解
- **A2: 社債ファクター構造の再評価（ポスト BBW）** — Bai-Bali-Wen 撤回後の文献再構築

意思決定はまだ収束しておらず、まずは公開データで両方のフィージビリティを確認する段階。

## リポジトリ構成

```
.
├── README.md                # このファイル
├── pyproject.toml           # fi_research パッケージ + 依存定義
├── src/
│   └── fi_research/         # 共通モジュール（Python パッケージ）
│       └── data/            # 公開データソース別のローダ
├── data/                    # 公開データ（CSV/Parquet）。SQLite は使わない
│   ├── raw/                 # 取得直後の生データ（gitignore）
│   └── processed/           # 整形済み（小さければ commit）
├── docs/                    # コード・リサーチ結果のドキュメント
│   └── handover.md
├── references/              # 参考文献（PDF・引用メモ）
└── projects/                # テーマ別 sandbox
    └── 00_exploration/      # テーマ非依存の探索場
```

## セットアップ

```bash
# uv を使う場合
uv sync

# pip を使う場合
pip install -e .
```

Python 3.10+ を想定。

## 作業方針

1. データ取得は **再現可能なスクリプト**（URL・取得日・スキーマを記録）
2. 共通コードは `src/fi_research/` の **Python パッケージ** に集約（`from fi_research.data.frb_ebp import load_ebp`）
3. 取得データは `data/raw/<source>/` に置き、整形後は `data/processed/<dataset>.parquet`
4. 分析は番号付き Jupyter ノートブック（`projects/<theme>/notebooks/NN_topic.ipynb`）
5. 重要な発見は Markdown で `docs/` に保存
6. 業務環境のデータ・有料端末は研究目的では使用しない
