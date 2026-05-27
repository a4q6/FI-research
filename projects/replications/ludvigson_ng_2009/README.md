# Ludvigson & Ng (2009) 再現

> Ludvigson, S. C., & Ng, S. (2009). "Macro Factors in Bond Risk Premia." *Review of Financial Studies*, 22(12), 5027–5067.

## 1. 論文の主張

- マクロ経済変数のパネル（Stock-Watson 風 132 系列）から PCA で抽出した因子 F1...F8 が、Cochrane-Piazzesi (2005) の CP factor を **超えて** 国債超過リターンを予測する
- CP factor + macro factors の R² ≈ 0.45 (CP alone は 0.30)
- 「マクロ情報は利回り曲線サマリーには含まれない」ことを示し、affine term structure model に reduced-form の限界を提示
- インフレ・実体経済の因子が特に重要

## 2. 再現対象

- **マクロ PCA**: FRED 11 系列を標準化 → PCA → F1..F5 抽出
- **Augmented CP regression**: `rx^(n)_{t+12} ~ CP_t + F1_t + ... + F5_t`
- **3 モデル比較**: CP only / macro only / CP + macro
- **3 サンプル**: 論文期間に近い (1964-2007) / 論文後 (2008-2025) / フル

**注**: LN は 132 系列を使用。本再現は手元の長期 FRED 11 系列に限定するため、PC は LN の F1-F8 より粗い。それでも実体経済・物価・金融条件の主成分は捉えられる。

## 3. データ

| カテゴリ | 系列 | 変換 |
|---|---|---|
| 実体経済 | INDPRO, PAYEMS | Δlog × 100 |
| 雇用 | UNRATE | Δ |
| 物価 | CPIAUCSL, PCEPI | Δlog × 100 |
| 金利 | DFF, DGS10 | Δ |
| 期間構造 | T10Y3M, T10Y2Y | level |
| クレジット | BAA10Y, AAA10Y | level |

CP factor は `cochrane_piazzesi_2005/results/cp_factor.parquet` を再利用。

**重要なボトルネック**: T10Y3M, BAA10Y, AAA10Y が 1986 年から開始するため、PCA 入力パネルは **1986-01 以降**に制限される（n=481 ヶ月）。LN 原論文 (1964-2003) のフル期間は再現できない。

## 4. 実行

```bash
# 先に CP factor を生成
python projects/replications/cochrane_piazzesi_2005/scripts/replicate.py
# 次に LN replication
python projects/replications/ludvigson_ng_2009/scripts/replicate.py
```

成果物: `results/`
- `macro_factors.parquet` — 月次 F1..F5
- `pca_loadings.csv` — 各因子の loading
- `r2_summary.csv` — モデル × 満期 × サンプル別 R²
- `macro_factors_ts.png` — F1..F5 時系列
- `r2_comparison.png` — CP-only / macro-only / CP+macro の R² 比較棒グラフ

## 5. 結果サマリ

### 5.1 PCA loadings（解釈）

| 系列 | F1 | F2 | F3 | F4 | F5 |
|---|---:|---:|---:|---:|---:|
| INDPRO | -0.31 | -0.40 | -0.20 | +0.06 | -0.08 |
| PAYEMS | -0.32 | -0.43 | -0.25 | -0.03 | +0.03 |
| UNRATE | +0.30 | +0.45 | +0.24 | +0.01 | -0.03 |
| CPIAUCSL | -0.34 | -0.04 | **+0.51** | -0.23 | +0.27 |
| PCEPI | -0.34 | -0.02 | **+0.52** | -0.24 | +0.24 |
| DFF | -0.06 | +0.01 | +0.04 | **+0.80** | +0.59 |
| DGS10 | -0.12 | -0.02 | +0.34 | +0.42 | -0.49 |
| T10Y3M | +0.24 | -0.39 | +0.33 | +0.16 | -0.25 |
| T10Y2Y | +0.30 | -0.41 | +0.29 | +0.07 | -0.13 |
| BAA10Y | **+0.41** | -0.23 | +0.00 | -0.15 | +0.30 |
| AAA10Y | **+0.39** | -0.28 | +0.02 | -0.16 | +0.31 |

説明分散率: F1=31.6%, F2=22.9%, F3=15.3%, F4=9.3%, F5=8.5%（累積 87.6%）

**解釈**:
- **F1 (32%)**: クレジット-マクロ共通因子。BAA10Y / AAA10Y が高く、実体経済が弱く、物価上昇が鈍るとき正 → 「信用ストレス / マクロ悪化」因子
- **F2 (23%)**: 純粋な景気循環因子。実体経済 (PAYEMS, INDPRO) と負相関、UR と正相関、期間スプレッドフラット化と相関 → 「リセッション」因子
- **F3 (15%)**: 物価因子。CPI と PCE に強く正
- **F4 (9%)**: 短期金利水準因子（DFF）
- **F5 (9%)**: 名目-実質 spread 系の残差

### 5.2 予測 R² 比較

| サンプル | maturity | CP only | macro only | CP + macro | Δ |
|---|---|---:|---:|---:|---:|
| **1964-2007**[*] | rx2 | 0.015 | 0.093 | **0.160** | +0.146 |
| (n=264) | rx3 | 0.026 | 0.071 | **0.139** | +0.113 |
|  | rx4 | 0.040 | 0.057 | **0.126** | +0.087 |
|  | rx5 | 0.054 | 0.051 | **0.121** | +0.067 |
|  | avg | 0.038 | 0.060 | **0.130** | +0.091 |
| **2008-2025** | rx2 | 0.008 | 0.176 | 0.177 | +0.169 |
| (n≈170) | rx3 | 0.029 | 0.171 | 0.180 | +0.151 |
|  | rx4 | 0.047 | 0.170 | 0.185 | +0.138 |
|  | rx5 | 0.057 | 0.173 | **0.188** | +0.131 |
|  | avg | 0.042 | 0.173 | **0.184** | +0.143 |
| **1973-2025** | rx2 | 0.062 | 0.023 | 0.106 | +0.044 |
| (n≈484)[*] | rx3 | 0.061 | 0.027 | 0.094 | +0.033 |
|  | rx4 | 0.065 | 0.035 | 0.093 | +0.028 |
|  | rx5 | 0.070 | 0.045 | 0.096 | +0.026 |
|  | avg | 0.067 | 0.034 | 0.095 | +0.028 |

[*] パネル制約で実効開始は 1986-01。

## 6. 解釈と論文との関係

### 6.1 LN の核となる主張は再現できた

「マクロ因子は CP factor を超える追加情報を持つ」が **全サンプル**で確認:
- 1964-2007 (実効 1986-2007): R² が 0.04 → 0.13 と **+9 ポイント**改善
- 2008-2025: R² が 0.04 → 0.18 と **+14 ポイント**改善 — ポスト QE 期では **CP factor 単独は無力**
- フル: +3 ポイント程度（CP factor 自体がフル期間で薄まるため改善幅も小さい）

### 6.2 R² の絶対水準の違い

LN 原論文の R² (CP+macro) ≈ 0.45。本再現は 0.13-0.19。差の原因:

1. **マクロパネル**: LN は 132 系列、本再現は 11 系列 → PCA がより粗い
2. **サンプル**: LN は 1964-2003、本再現は実効 1986-2007 / 2008-2025 → 1970s の高インフレ期が抜けている
3. **GSW vs Fama-Bliss**: CP factor 自体の R² が下がる ([cochrane_piazzesi_2005](../cochrane_piazzesi_2005/README.md) で確認)

ただし「macro が CP を超える情報を持つ」という **主張の方向性は完全一致**。R² の絶対水準が下がっても、incremental ΔR² (+9〜+14 ポイント) は LN 論文と同程度。

### 6.3 ポスト QE 期 (2008-2025) の特異性

CP only R² が 0.04 まで低下する一方、macro only R² は **0.17 と高水準を維持**。これは Gilchrist-Zakrajšek (2012) の再現結果（[gilchrist_zakrajsek_2012/README.md](../gilchrist_zakrajsek_2012/README.md) で EBP 予測力が崩壊）とは逆方向の発見:
- EBP は「企業金融状態のサマリー」として QE 後に陳腐化
- マクロ実体経済の因子は QE 後も国債リターンを予測する力を保持
- 国債市場と社債市場で QE の影響が非対称

これは A1 (SHAP × 債券) で「マクロ因子と利回り曲線情報を非線形に組み合わせる」アプローチの妥当性を強く支持する。

### 6.4 F1 (信用-マクロ複合因子) の高 explanatory power

F1 が 32% の分散を説明 + クレジットスプレッドに強く正でロード → BAA/AAA spread と実体経済の共変動を圧縮した因子が、国債超過リターンの予測に効く。これは ATSM (affine term structure model) で「マクロが price of risk に効く」典型例。

## 7. 次に進める派生分析

- [ ] FRED-MD (McCracken-Ng) の 132 系列を取得し、LN 原論文の panel をフル再現
- [ ] PCA の代わりに sparse PCA / factor rotations で解釈可能性向上
- [ ] F1-F5 の時変係数（Kalman filter / rolling regression）でレジーム依存性
- [ ] A1 で GSW yields + マクロ panel を直接 XGBoost に投入 → SHAP で因子寄与の非線形性を可視化（LN の線形 PCA を超えられるか）
- [ ] WRDS Fama-Bliss + 132 series で LN 原論文の R² 0.45 を厳密再現

## 8. 引用

```
Ludvigson, S. C., & Ng, S. (2009). Macro Factors in Bond Risk Premia.
Review of Financial Studies, 22(12), 5027-5067.
```
