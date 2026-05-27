# Bundle B: ポスト QE 構造変化の検証

[`projects/replications/gilchrist_zakrajsek_2012`](../../replications/gilchrist_zakrajsek_2012/README.md) で発見した「EBP の予測力が 2011 年以降崩壊」という現象を 3 つの角度から精緻化し、構造変化の **真の正体**を識別する。

## 1. 動機

GZ 再現で観察された事実:
- EBP は論文期間 (1973-2010) で実体経済を強く予測 (R² 25-60%, t-stat 5-10)
- 論文後 (2011-2025) で予測力がほぼ消失 (R² < 0.05)

可能な解釈:
- (a) EBP 固有の問題: 構築手法が QE/Dodd-Frank 後の世界に陳腐化
- (b) 全 stress index 共通の現象: 金融-実体の伝達経路自体が変質
- (c) 期間ベースの解釈ではなく、レジーム (QE on/off, recession in/out) ベースで見るべき

本バンドルはこれら 3 仮説を区別する。

## 2. 構成

| script | 目的 |
|---|---|
| [`scripts/ebp_horse_race.py`](scripts/ebp_horse_race.py) | 9 つの stress index (EBP/NFCI/ANFCI/STLFSI4/OFR FSI×3/MOVE/VIX) を univariate predictive regression で並列比較 |
| [`scripts/regime_decomposition.py`](scripts/regime_decomposition.py) | EBP と OFR FSI Credit の予測力を NBER × QE active の 4 セルに分解 |
| [`scripts/cp_rolling.py`](scripts/cp_rolling.py) | CP factor 回帰 (rx ~ f1..f5) の 10y rolling R² と係数の時変ダイナミクス |

QE active は Fed BS (WALCL) の前年比成長 > 10% で定義 → 自動検出:
- 2008-09 〜 2009-10 (QE1)
- 2010-01 〜 2010-09 (QE2)
- 2011-02 〜 2012-03 (Twist期)
- 2013-03 〜 2015-01 (QE3)
- 2020-03 〜 2022-07 (COVID QE)

## 3. 実行

```bash
python projects/derivatives/b_post_qe_structural/scripts/ebp_horse_race.py
python projects/derivatives/b_post_qe_structural/scripts/regime_decomposition.py
python projects/derivatives/b_post_qe_structural/scripts/cp_rolling.py
```

成果物: `results/`
- `horse_race_results.csv` / `_heatmap.png` / `_bars_payroll12m.png`
- `regime_decomposition.csv` / `regime_r2_bars.png`
- `cp_rolling.parquet` / `cp_rolling.csv` / `cp_rolling_r2.png` / `cp_rolling_coefs_rx5.png` / `cp_rolling_r2_with_recessions.png`

## 4. 結果サマリ

### 4.1 Horse Race: 全 stress index が同じパターン

**Pre-2011** (h=3m, target=Payroll growth, R²):

| Stress | R² |
|---|---:|
| OFR FSI total | **0.74** |
| OFR FSI Credit | 0.72 |
| OFR FSI US | 0.64 |
| MOVE | 0.60 |
| STLFSI4 | 0.60 |
| EBP | 0.39 |
| ANFCI | 0.30 |
| VIX | 0.37 |
| NFCI | 0.21 |

**Post-2011** (h=3m, target=Payroll growth, R²):

| Stress | R² |
|---|---:|
| STLFSI4 | 0.053 |
| VIX | 0.030 |
| MOVE | 0.015 |
| OFR FSI US | 0.022 |
| OFR FSI Credit | 0.000 |
| EBP | 0.005 |
| その他 | < 0.01 |

**結論**: 仮説 (b) が正しい — **EBP 固有の問題ではなく、全 stress index が一斉に崩壊**。金融条件と実体経済の伝達経路全体が変質した。

OFR FSI Credit (信用市場ストレス特化) が pre-2011 で 0.72 → post-2011 で 0.00 と劇的に崩壊。これは EBP の崩壊と完全にパラレル。

### 4.2 Regime Decomposition: 崩壊の本質は「QE 終了後の calm 期」

**EBP → Δlog Payroll (h=12m), regime 別 R²**:

| Regime | R² | β | t-stat | n |
|---|---:|---:|---:|---:|
| All | 0.174 | -1.78 | -6.86 | 628 |
| NBER recession | 0.152 | -1.14 | -7.21 | 74 |
| no NBER | 0.054 | -1.23 | -3.35 | 554 |
| **QE active** | **0.512** | -1.90 | -11.40 | 84 |
| no QE | 0.114 | -1.74 | -4.06 | 544 |
| NBER × no QE | 0.121 | -1.62 | -2.21 | 62 |
| no NBER × QE | 0.145 | -2.02 | -2.17 | 72 |
| **no NBER × no QE** | **0.040** | -1.06 | -2.66 | 482 |

**重要な発見**: 
- **EBP の予測力が最も強いのは QE active 期間中** (R² = 0.51) — Fed BS が拡大している危機期はクレジットスプレッドが景気を強く予測
- **最も弱いのは「平常時 (no NBER × no QE)」** (R² = 0.04) — 大多数の月 (n=482) を占める平穏な経済拡大期では EBP は無力

これは仮説 (c) が正しいことを示す:
- 「post-2011 で崩壊」というのは間違い
- 「平穏な拡大期は EBP が機能しない」が正解。1990 年代後半・2002-2007 のような長期 expansion 期間も平穏なら R² 低い
- post-2011 は QE が断続的にあったが、その間隔の「平穏な穏やかな拡大」 (2015-2019) で機能していないのが集計時に影響している

OFR FSI Credit についても同じパターン (QE active R²=0.53, no NBER × no QE R²=0.03)。

### 4.3 CP rolling: 規則的な時変パターン

10y rolling 窓での CP regression 結果:

| 満期 | R² 平均 | R² 標準偏差 | R² 最大 | R² 最小 |
|---|---:|---:|---:|---:|
| rx^(2) | 0.402 | 0.171 | 0.914 (2017-01) | 0.039 (2024-09) |
| rx^(3) | 0.408 | 0.166 | 0.877 (2017-01) | 0.033 (2024-09) |
| rx^(4) | 0.417 | 0.157 | 0.817 (2017-01) | 0.040 (2024-10) |
| rx^(5) | 0.424 | 0.148 | 0.756 (2017-01) | 0.047 (2024-10) |
| rx_avg | 0.418 | 0.158 | 0.829 (2017-01) | 0.037 (2024-10) |

**R² が最大の window: 2007-01 〜 2017-01** (GFC + Fed QE + 緩やかな回復)。CP factor が国債超過リターンを最強で予測した時期。

**R² が最小の window: 2014-10 〜 2024-10** (post-QE + COVID + インフレ + 利上げ)。CP factor の予測力がほぼ消失。

CP factor のフルサンプル R² (0.13) と論文サンプル R² (0.24) の差は、**「最近 10 年のサンプル」の予測力が壊れていることで説明される**。

## 5. 統合的解釈

3 つの分析を統合すると:

1. **構造変化は EBP 特有ではなく、stress index と国債曲線情報の両方で起きている**
2. **構造変化の本質は「QE 期と通常期の境界が曖昧になった」こと**: Fed の介入が長期間続いたことで、平常時の credit-real economy 伝達経路が薄まった
3. **マクロ-金融状態がレジーム依存になった**: 平穏期は線形 stress index も yield curve も予測力低、危機期 (NBER) と Fed 介入期 (QE) で線形手法が機能する

### A2 (post-BBW 社債ファクター) への直接的含意

- **線形 cross-sectional 回帰の R² が時期によって 5 倍変動**するなら、ポスト BBW 期に Bai-Bali-Wen の頑健性が崩れたのは「線形手法の問題」かもしれない
- レジーム依存の social factor 構造を仮定する HMM-based Fama-MacBeth が補章 B1 として活きる
- **平穏期 (no NBER × no QE) では線形ファクターモデルの説明力が低い**: ML / nonlinear モデルでないと拾えないアルファが存在する可能性

### A1 (SHAP × 債券アトリビューション、保留中)

- レジーム依存の線形性 → SHAP で「平常期と危機期の非線形寄与のシフト」を可視化できれば論文の貢献として明確
- ただし [memory/research_themes](../../../.claude/projects/-home-tarai-Research-FI-research/memory/research_themes.md) の通り、A1 は MBS/Callable データ待ちで現状保留

## 6. 次に進める派生分析

- [ ] horse race を multivariate にして冗長性を除去 (LASSO with 9 stress vars)
- [ ] regime 4 セル別に CP 回帰 → 国債曲線情報の regime 依存性
- [ ] HMM (2-state Markov) で endogeneous regime extraction → no NBER × no QE と "active" 状態
- [ ] CP rolling 係数の time-varying tent shape を可視化 (heatmap of 5 coefficients × time)
- [ ] OFR FSI subcomponent 別に同じ分析 (funding/credit/equity/safe-assets/volatility のどれが寿命を持つか)

## 7. 引用

```
Gilchrist, S., & Zakrajšek, E. (2012). Credit Spreads and Business Cycle
Fluctuations. American Economic Review, 102(4), 1692-1720.

Cochrane, J. H., & Piazzesi, M. (2005). Bond Risk Premia. American
Economic Review, 95(1), 138-160.
```
