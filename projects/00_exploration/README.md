# 00_exploration — テーマ非依存の探索場

最終的なテーマ（A1 / A2 ともに未確定）に依存しない、初期の探索作業の置き場。

## 中身

- `notebooks/` — 番号付きの探索 notebook（`NN_topic.ipynb`）
- `results/` — notebook から書き出した図や中間結果

## ルール

- データ取得や前処理ロジックは **ここに書かない**。`src/fi_research/data/` に書いて import する
- ここの notebook は「呼ぶ・確認する・図を出す」だけに留める
- 重要な発見は `docs/` に Markdown 化（notebook は再現用の薄いラッパーに）

## 既存 notebook

- `notebooks/01_frb_ebp.ipynb` — FRB EBP の取得と基本可視化（A1/A2 共通のマクロ要因）
