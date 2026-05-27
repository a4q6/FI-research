# projects/derivatives — 派生分析

`projects/replications/` の各論文の §7 で挙げた **派生分析候補**を、複数論文・データ源を組み合わせて実装する。再現ではなく、本研究テーマ (A1 / A2) の予備分析として位置づけ。

## バンドル

| key | テーマ | A2 紐付け | 状態 |
|---|---|---|---|
| [`a_robeco_credit_pc`](a_robeco_credit_pc/README.md) | 社債ファクター精緻化（credit PC1 直交化 + ストレス期 drawdown） | A2 主分析の精度向上 | ✅ done |
| [`b_post_qe_structural`](b_post_qe_structural/README.md) | ポスト QE 構造変化検証（stress index horse race + regime decomp + CP rolling） | A2 の regime 章 | ✅ done |
| [`c_mps_credit_transmission`](c_mps_credit_transmission/README.md) | MPS × クレジット伝播（FOMC-day OAS 反応 + LP IRF + regime interaction） | A2 補章候補 (novel) | ✅ done |

## 主要発見（A2 章立てに直結する 5 つ）

1. **Robeco 公開データで論文 IR を概ね再現可能** ([Bundle A](a_robeco_credit_pc/README.md))  
   BAA10Y proxy で直交化すれば論文 Table 3 IR の 80-100% を回復 → A2 の予備分析が公開データで成立する確証
2. **post-2011 stress index 崩壊は universal、EBP 特有ではない** ([Bundle B.1](b_post_qe_structural/README.md))  
   9 つの stress index 全てが pre-2011 で R² 0.4-0.7 → post-2011 で R² < 0.05 に崩壊
3. **崩壊の本質は「QE 終了後の calm 期」** ([Bundle B.2](b_post_qe_structural/README.md))  
   EBP の予測力は QE active 期間で R²=0.51、平穏時 (no NBER × no QE) で R²=0.04 — 期間ベースではなくレジームベースで見るべき
4. **CP factor R² が rolling window で 0.04 〜 0.91 まで変動** ([Bundle B.3](b_post_qe_structural/README.md))  
   最大は 2007-2017 window (GFC + QE)、最小は 2014-2024 window
5. **MP 伝達が信用ストレス regime で完全に sign-reversed** ([Bundle C.3](c_mps_credit_transmission/README.md))  
   Calm 期は引締め → 社債スプレッド narrow、Stress 期は引締め → widen。Interaction t > 6。**novel finding 候補**

## 全体方針

- スクリプトは `scripts/`、結果は `results/`、ノートブックは表示用の薄ラッパー
- 各バンドル README に **問題意識・データ・結果・A2 への含意**を記録
- replications の `cp_factor.parquet` などを再利用 (DRY)
- 公開データのみで完結する範囲で実装、WRDS が必要な extension は TODO に記録

## 全体方針

- スクリプトは `scripts/`、結果は `results/`、ノートブックは表示用の薄ラッパー
- 各バンドル README に **問題意識・データ・結果・A1/A2 への含意**を記録
- replications の `cp_factor.parquet` などを再利用 (DRY)
- 公開データのみで完結する範囲で実装、WRDS が必要な extension は TODO に記録