# projects/replications — 先行研究の再現

`docs/handover.md` §8 の先行研究のうち、手元の公開データ（30 ソース、`data/processed/*.parquet`）だけで原論文水準の再現が可能なものを置く。

## 中身

各サブフォルダは 1 論文に対応。共通構造:

```
<paper_key>/
├── README.md              ← 論文情報・再現対象・データ・結果サマリ
├── notebooks/             ← 番号付き Jupyter（探索・可視化）
├── scripts/               ← 再現スクリプト（.py、ノートブックから呼ぶ／単独実行可）
└── results/               ← 図・パネル parquet・統計量（git ignore 推奨）
```

## ルール（`memory/work_conventions.md` 準拠）

- データ取得・前処理ロジックは **書かない**。`src/fi_research/data/` に追加してから import する
- 番号付き notebook (`NN_topic.ipynb`)
- 重要な発見は各論文 README.md の「結果」セクションに Markdown 化
- 公開できる品質（型ヒント + docstring）

## 対象論文（カテゴリ ① 完全再現可能）

| key | 論文 | 主データ | 状態 | 主要発見 |
|---|---|---|---|---|
| [`cochrane_piazzesi_2005`](cochrane_piazzesi_2005/README.md) | Cochrane & Piazzesi (2005, AER) | GSW forward rates | ✅ done | 単一因子制約は完全再現。R² は GSW vs Fama-Bliss で 10pt 低い |
| [`ludvigson_ng_2009`](ludvigson_ng_2009/README.md) | Ludvigson & Ng (2009, RFS) | FRED マクロ + GSW | ✅ done | マクロ PCA factor が CP factor に +9〜+14pt の R² 寄与 |
| [`houweling_vanzundert_2017`](houweling_vanzundert_2017/README.md) | Houweling & van Zundert (2017, FAJ) | Robeco 公開ファクター | ✅ done | post-BBW (2015-2025) でも HY 全ファクター t > 2.7 |
| [`gilchrist_zakrajsek_2012`](gilchrist_zakrajsek_2012/README.md) | Gilchrist & Zakrajšek (2012, AER) | FRB EBP + FRED | ✅ done | 論文期間で R² 25-60%、論文後で予測力が完全崩壊 |
| [`bauer_swanson_2023`](bauer_swanson_2023/README.md) | Bauer & Swanson (2023, AER) | MPS + GSW + FRED | ✅ done | raw mps R²=0.156, mps_orth R²=0.001 → 直交化機能 |
| [`gurkaynak_sack_wright_2007`](gurkaynak_sack_wright_2007/README.md) | Gürkaynak, Sack & Wright (2007, JME) | GSW NSS | ✅ done | Svensson 公式と公開 SVENY が 0.002bps 一致 |

## 横断的な発見

- **3 つの "ポスト QE で構造変化" 兆候**:
  1. GZ EBP の景気予測力が 2011 年以降ほぼ消失
  2. CP factor の R² が 1971-2025 フルで 0.13 に低下（論文期間の半分以下）
  3. LN マクロ因子は QE 後も予測力を保持 → 国債と社債で QE 影響の非対称性

- **A1 / A2 への含意（強い支持）**:
  - 線形手法の R² が時間とともに低下 → 非線形 (SHAP × 債券) アプローチの動機が補強された
  - Robeco データで post-BBW 期間でも社債ファクタープレミアムが残存 → A2 の妥当性確認
  - マクロ・MPS・EBP の情報は独立にリスクプレミアムを担う → ML での統合の余地大

- **WRDS 不要で出せる主張**:
  - GSW + Robeco + FRED + MPS の 4 ソースで国債・社債リスクプレミアムの大半が議論可能
  - 個別銘柄 (TRACE) が必須なのは A2 の最終段階（横断回帰）と Bai-Bali-Wen 直接再現のみ

## 共通の注意

- **再現の意味**: 原論文と完全に同じ係数を出すことが目的ではなく、**手法・主要結論が公開データだけで再現できるか**を確認する
- **データ範囲の食い違いを明記**: 原論文のサンプル期間と手元のデータ期間にズレが出る場合は README で明示
- **WRDS が必要なステップは省略**: 例えば TRACE 個別取引が必要な箇所はスキップし、その旨を記録
