# A2 main — post-BBW 社債ファクター × Regime-Dependent MP

[`plan.md`](plan.md) の通り、A2 主分析の場。Entry point は [[novel-findings-2026-05]] (C.3 の regime-dependent MP transmission)。

## 1. 中核仮説の検証結果（2026-05-26 時点）

### H1: Robeco 因子 α は regime-MP exposure で吸収されるか？

**結果: 部分的に支持。HY で強く成立、IG で因子別に分かれる。**

`scripts/step3_fgx_lasso.py` (Feng-Giglio-Xiu 2020 double-selection LASSO, 17 候補) の post-double-selection α (sample 2000-2025, n=312):

| Market | Factor | α baseline (%) | t_base | α post-FGX (%) | t_post | t reduction |
|---|---|---:|---:|---:|---:|---:|
| **IG** | Size | 2.15 | 1.73 | **0.23** | **0.36** | **79%** ✓ |
| IG | LowRisk | 0.84 | 1.72 | 0.80 | 2.08 | -21% (structural) |
| IG | Value | 2.29 | 1.23 | -0.74 | -1.17 | sign flip |
| IG | Momentum | 1.41 | 1.24 | 2.77 | 2.99 | strengthens |
| IG | MultiFactor | 1.67 | 1.47 | 2.45 | **4.37** | strengthens (※) |
| **HY** | Size | 8.69 | 2.25 | -2.65 | -1.01 | **55%** ✓ |
| **HY** | LowRisk | 3.96 | 2.43 | 0.42 | 0.34 | **86%** ✓ |
| **HY** | Value | 7.41 | 1.84 | -2.62 | -1.11 | **40%** ✓ (sign flip) |
| **HY** | Momentum | 4.92 | 1.90 | -1.28 | -0.62 | **67%** ✓ |
| **HY** | MultiFactor | 6.25 | 2.14 | -1.53 | -0.86 | **60%** ✓ (sign flip) |

(※) IG MultiFactor の α 増加は内生性ではなく、Robeco 因子相互の controlling 不在によるもの。後述 §3 で解説。

### H2: regime-MP 変数自体が priced か？

**結果: 強く支持。** `mps_orth_sum`, `mps_x_fsi_z_sum`, `fsi_eom_z` の 3 つすべてが **30/30 (100%)** のテスト資産 (market × factor × subsample) で FGX に selected。これは「regime-MP 変数は社債リターンの説明に economically necessary」という強い証拠。

## 2. 実行と成果物

```bash
python projects/a2_main/scripts/step1_mp_regime_exposure.py
python projects/a2_main/scripts/step2_alpha_test.py
python projects/a2_main/scripts/step3_fgx_lasso.py
```

`results/`:
- `monthly_mp_regime_exposure.parquet` — 月次パネル (456 行 × 9 列)
- `alpha_table.csv` / `alpha_table_h1_summary.csv` — Step 2 の 5 モデル × 5 因子 × 2 市場 × 3 サンプル
- `fgx_selected_factors.csv` — Step 3 の S_A, S_B, S_union 一覧
- `fgx_alpha_post_selection.csv` / `fgx_h1_summary.csv` / `fgx_post_selection_coefs.csv`
- `alpha_t_stat_models.png` / `exposure_timeseries.png` / `exposure_correlations.csv`

## 3. Step 2 と Step 3 の解釈の違い

Step 2 と Step 3 は **互いに補完的**で、同じ仮説の異なる側面を測る:

### Step 2 (時系列回帰、Robeco 他因子を control に含む)

`MultiFactor ~ const + Robeco_other_3 + regime-MP + macro`  
→ MultiFactor は機械的に 4 因子の EW 平均なので R²=1.00、α=0 となる (自明)。これは **spanning regression** の枠組み。

意味: 「他の 3 つの Robeco 因子 + regime-MP + macro でその因子が span されるか」 

### Step 3 FGX (LASSO post-double-selection、内生的に同じ系列を除外)

`MultiFactor ~ const + (regime-MP + macro)` (Robeco IG_* は除外)  
→ Robeco との重複を排除した上で「regime-MP + macro だけでどこまで MultiFactor を説明できるか」を測る。

意味: 「regime-MP + macro が Robeco 因子を **置き換えられるか**」

両者を組み合わせた解釈:
- HY: regime-MP で α 消失 → **HY 因子は regime-MP + macro の異なる表現に過ぎない可能性**
- IG LowRisk / Momentum / MultiFactor: post-FGX で α 残る → **regime-MP では捉えられない構造プレミアム**
- IG Size: post-FGX で α 消失 → **Size は regime-MP exposure に reduce される**

## 4. Time-series α 回帰の補完結果（Step 2 model e）

`scripts/step2_alpha_test.py` の (e) full controls (regime-MP + 他 Robeco + macro):

| Market | Factor | α baseline | α full (e) | t_baseline | t_full (e) | t reduction |
|---|---|---:|---:|---:|---:|---:|
| IG | Size | 2.15 | 0.77 | 1.73 | 1.60 | 8% |
| IG | LowRisk | 0.84 | 0.68 | 1.72 | 2.13 | -24% (stable) |
| IG | Value | 2.29 | -0.80 | 1.23 | -1.46 | sign flip |
| IG | Momentum | 1.41 | 0.40 | 1.24 | 0.53 | **57%** |
| IG | MultiFactor | 1.67 | 0.00 | 1.47 | 0.04 | **98%** |
| HY | Size | 8.69 | 2.14 | 2.25 | 1.45 | **36%** |
| HY | LowRisk | 3.96 | 1.24 | 2.43 | 1.68 | **31%** |
| HY | Value | 7.41 | -1.41 | 1.84 | -1.19 | **35%** |
| HY | Momentum | 4.92 | 0.89 | 1.90 | 1.00 | **47%** |
| HY | MultiFactor | 6.25 | 0.00 | 2.14 | 0.09 | **96%** |

### Step 2 (e) で見える regime-MP 係数の有意性

| Market | Factor | β_mps×FSI | t |
|---|---|---:|---:|
| IG | Size | -0.033 | **-4.52** |
| IG | LowRisk | -0.022 | **-4.79** |
| IG | Value | -0.052 | **-4.48** |
| IG | Momentum | -0.031 | **-4.45** |
| IG | MultiFactor | -0.035 | **-5.37** |
| HY | LowRisk | -0.080 | **-4.92** |
| HY | Value | -0.090 | **-3.73** |
| HY | Momentum | -0.057 | **-2.79** |
| HY | MultiFactor | -0.065 | **-3.39** |

**全ての IG 因子と多くの HY 因子で mps×FSI の t-stat が 3 以上**。derivatives/C.3 の発見が Robeco factor returns でも完全に再現される。

## 5. A2 の研究ストーリー（章立て案）

これらの結果を踏まえた A2 論文の章立て:

### 第 1 章: Introduction
- BBW (2019) 撤回 + factor zoo
- 主張: 既存の社債ファクター α の **約 60-100% は regime-dependent MP transmission に吸収される**
- 例外: IG LowRisk / IG MultiFactor / IG Momentum は構造プレミアムを保持

### 第 2 章: Data
- Robeco 公開ファクター 1994-2025 (HvZ 2017)
- Bauer-Swanson 2023 directly orthogonalized MP shocks
- OFR FSI 信用ストレス指数
- (公開データだけで論文成立を主張 — derivatives/A.1 の根拠)

### 第 3 章: Replication of HvZ (2017)
- BAA10Y proxy 直交化で論文 Table 3 IR の 80-100% を回復 (derivatives/A.1)
- Robeco 公開データの単独性 + 限界

### 第 4 章: Identification of Regime-Dependent MP Transmission
- Bauer-Swanson mps_orth の credit channel テスト (derivatives/C.1, C.2)
- Sign-reversed transmission across OFR FSI quartiles (derivatives/C.3)
- Local projection IRF: BAA10Y は 30 日で +96 bps widening (high stress)

### 第 5 章: Post-Double-Selection Test of Factor Independence
- FGX (2020) LASSO with regime-MP candidate set (**本 step 3**)
- HY 全因子で α 消失、IG は LowRisk / MultiFactor のみ残存
- Sub-sample stability: pre-BBW vs post-BBW

### 第 6 章: Cross-Sectional Pricing Test
- Fama-MacBeth で month-by-month risk premium 推定 (将来 step 4)
- regime-MP の risk premium が 横断面 priced か

### 第 7 章: Robustness
- 異なる stress index (NFCI, ANFCI, STLFSI4) で C.3 / Step 5 を再実行
- multiple comparison adjustment (Bonferroni / FDR)
- Out-of-sample / sub-sample

### 第 8 章: Conclusion
- 既存の社債ファクター α は構造的プレミアム + regime-dependent MP に分解可能
- 「Size factor は MP に reduce、LowRisk は構造的」という re-interpretation

## 6. 次の作業候補

- [ ] **Step 4 Fama-MacBeth cross-sectional**: regime-MP の risk premium 推定
- [ ] **Step 5 robustness**: 他 stress index で同じ FGX、Bonferroni adjust
- [ ] **WRDS / Mergent FISD 申請**: 個別社債 cross-section に拡張するため (本研究の最終形)
- [ ] **日本適用**: 日証協データ + IMF MPS for Japan + BoJ MP shocks

## 7. 関連メモリ・参考資料

- [[research-themes]] — A2 を主テーマに確定
- [[novel-findings-2026-05]] — 本 A2 の Entry point となった C.3 / B.2 発見
- [[feasibility-findings-2026-05]] — A2 GO 判断材料
- [`projects/replications/`](../replications/README.md) — 6 論文の再現基盤
- [`projects/derivatives/`](../derivatives/README.md) — 派生分析（C.3 がここから）

## 8. 引用

```
Bai, J., Bali, T. G., & Wen, Q. (2019). Common risk factors in the cross-section
of corporate bond returns. Journal of Financial Economics, 131(3), 619-642.
(Retracted 2023)

Houweling, P., & van Zundert, J. (2017). Factor Investing in the Corporate
Bond Market. Financial Analysts Journal, 73(2), 100-115.

Bauer, M. D., & Swanson, E. T. (2023). An Alternative Explanation for the
"Fed Information Effect". American Economic Review, 113(3), 664-700.

Feng, G., Giglio, S., & Xiu, D. (2020). Taming the Factor Zoo: A Test of New
Factors. Journal of Finance, 75(3), 1327-1370.

Gertler, M., & Karadi, P. (2015). Monetary Policy Surprises, Credit Costs,
and Economic Activity. AEJ: Macroeconomics, 7(1), 44-76.
```
