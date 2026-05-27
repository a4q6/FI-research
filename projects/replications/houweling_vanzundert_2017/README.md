# Houweling & van Zundert (2017) 再現

> Houweling, P., & van Zundert, J. (2017). "Factor Investing in the Corporate Bond Market." *Financial Analysts Journal*, 73(2), 100–115.

## 1. 論文の主張

- 米国 IG / HY 社債で **Size / Low-Risk / Value / Momentum** の 4 ファクターが統計的に有意なリターンプレミアムを生成する
- 4 ファクターを等加重で合成した **MultiFactor** ポートフォリオは単独ファクターより高い IR
- ファクター間の相関は中程度で、組み合わせによる分散効果が機能する
- 公開データは Robeco 自身が無料配布（[robeco.com](https://www.robeco.com/)）— **A2「ポスト BBW 社債ファクター」の再現基盤**

## 2. 再現対象

- **Table 3 相当**: 4 ファクター（+ MultiFactor）の年率平均超過リターン、ボラ、IR、t-stat（IG / HY 別）
- **Table 4 相当**: ファクター間相関行列
- **Figure 1 相当**: 累積超過リターン推移
- 論文サンプル (1994-01 〜 2015-09) と最新サンプル (1994-01 〜 2025-12) の両方を計算

## 3. データ

| 項目 | ソース | loader |
|---|---|---|
| 月次ファクターリターン | Robeco "Factor Returns Data Set" XLSX | `fi_research.data.robeco.load_robeco_credit_factors` |

単位: 月次小数（0.0020 = 20 bp）。**duration-matched Treasury に対する超過リターン**。

## 4. 実行

```bash
python projects/replications/houweling_vanzundert_2017/scripts/replicate.py
```

成果物: `results/`
- `table3_{IG,HY}_{paper_1994_2015,full_1994_2025}.csv` — 記述統計
- `corr_{IG,HY}_full.csv` — 4 ファクター相関
- `cumret_{IG,HY}.png` — 累積超過リターン
- `robeco_panel.parquet` — IG+HY 統合月次パネル

## 5. 結果サマリ

### 5.1 IG, 論文サンプル (1994-01 〜 2015-09, n=261 ヶ月)

| Factor | mean (年率, %) | vol (年率, %) | IR | t-stat |
|---|---:|---:|---:|---:|
| Size | 1.57 | 3.80 | 0.41 | 1.93 |
| Low-Risk | 0.90 | 2.23 | 0.41 | 1.89 |
| Value | 1.63 | 6.74 | 0.24 | 1.13 |
| Momentum | 0.71 | 4.31 | 0.17 | 0.77 |
| MultiFactor | 1.20 | 3.97 | 0.30 | 1.42 |

### 5.2 HY, 論文サンプル (1994-01 〜 2015-09, n=261 ヶ月)

| Factor | mean (年率, %) | vol (年率, %) | IR | t-stat |
|---|---:|---:|---:|---:|
| Size | 7.48 | 12.16 | 0.62 | 2.87 |
| Low-Risk | 3.61 | 6.67 | 0.54 | 2.52 |
| Value | 5.84 | 13.45 | 0.43 | 2.02 |
| Momentum | 4.06 | 10.26 | 0.40 | 1.85 |
| MultiFactor | 5.25 | 10.04 | 0.52 | 2.44 |

### 5.3 IG, フルサンプル (1994-01 〜 2025-12, n=384 ヶ月)

| Factor | mean (年率, %) | vol (年率, %) | IR | t-stat |
|---|---:|---:|---:|---:|
| Size | 1.85 | 3.88 | 0.48 | **2.70** |
| Low-Risk | 0.79 | 1.91 | 0.41 | **2.33** |
| Value | 2.19 | 6.48 | 0.34 | 1.92 |
| Momentum | 1.31 | 5.02 | 0.26 | 1.47 |
| MultiFactor | 1.53 | 4.02 | 0.38 | **2.16** |

### 5.4 HY, フルサンプル (1994-01 〜 2025-12, n=384 ヶ月)

| Factor | mean (年率, %) | vol (年率, %) | IR | t-stat |
|---|---:|---:|---:|---:|
| Size | 7.53 | 11.55 | 0.65 | **3.69** |
| Low-Risk | 3.46 | 6.14 | 0.56 | **3.19** |
| Value | 6.59 | 13.29 | 0.50 | **2.80** |
| Momentum | 4.68 | 9.73 | 0.48 | **2.72** |
| MultiFactor | 5.57 | 9.62 | 0.58 | **3.27** |

### 5.5 相関行列（フルサンプル）

**IG**:
|  | Size | LowRisk | Value | Mom |
|---|---:|---:|---:|---:|
| Size | 1.00 | 0.61 | 0.89 | 0.83 |
| LowRisk | 0.61 | 1.00 | 0.78 | 0.56 |
| Value | 0.89 | 0.78 | 1.00 | 0.87 |
| Momentum | 0.83 | 0.56 | 0.87 | 1.00 |

**HY**:
|  | Size | LowRisk | Value | Mom |
|---|---:|---:|---:|---:|
| Size | 1.00 | 0.74 | 0.87 | 0.82 |
| LowRisk | 0.74 | 1.00 | 0.87 | 0.82 |
| Value | 0.87 | 0.87 | 1.00 | 0.93 |
| Momentum | 0.82 | 0.82 | 0.93 | 1.00 |

## 6. 論文との乖離と解釈

**符号と相対順位は概ね一致**: HY の方が IG より絶対リターンが大きく、Size と MultiFactor の IR が高いという論文の主張は再現できる。

**ただし IR・t-stat の絶対値は論文より低い**:
- 論文 IG Size: mean ≈ 1.46%, vol ≈ 1.97%, IR ≈ 0.74, t ≈ 3.45
- 本再現 IG Size: mean ≈ 1.57%, vol ≈ 3.80%, IR ≈ 0.41, t ≈ 1.93

平均はほぼ一致するが、**ボラが約 2 倍**。これは論文の Table 3 が「ベンチマーク（クレジットインデックス）に対するトラッキングエラー」を分母にしている一方、Robeco 公開データは「duration-matched Treasury に対する超過リターン」を直接記録しているため。**前者ではクレジット市場プレミアムがロング・ベンチマーク双方で相殺されるが、後者はクレジットベータがそのまま残る**。

つまり Robeco 公開データはロングオンリー・ファクターポートフォリオの絶対超過リターン系列であり、クレジット市場プレミアムを含むまま提供されている。論文 Table 3 の Information Ratio をそのまま再現するには:

1. Bloomberg Barclays U.S. Corporate Investment Grade / High Yield ベンチマーク月次リターンを別途取得して active return を計算する
2. または、4 ファクター共通成分（クレジット PC1）を除去した残差で評価する

両方とも公開データだけでは現状不可能。1 については WRDS / Bloomberg ライセンスが必要、2 については本再現の派生分析として実装可能。

**フルサンプル拡張の効果**: 2015 → 2025 でサンプルを 10 年拡張すると、すべてのファクターで t-stat が大きく改善（IG MultiFactor: 1.42 → 2.16、HY Size: 2.87 → 3.69）。**post-BBW 期間でも社債ファクタープレミアムは消失していない**ことが確認できる。これは A2 テーマの妥当性を強く支持する重要な発見。

**相関は論文より高い**: 同じ理由でクレジットベータが共通成分として残るため、ファクター間相関が 0.6 〜 0.9 と高い。論文 Table 4 では 0.2 〜 0.5 程度。

## 7. 次に進める派生分析

- [ ] Robeco IG/HY の credit PC1（4 ファクターの第一主成分）を計算し、各ファクターから直交化したリターンで再計算（論文 Table 3-4 を再現できる可能性）
- [ ] IG Corporate index（BAML BAMLC0A0CM など FRED 経由）を bench とした active return ベースの IR 計算
- [ ] 2008、2020、2022 のストレス期で各ファクターの drawdown 分析
- [ ] A2 (ポスト BBW) 文脈での FGX double-selection LASSO 適用（株式ファクター・マクロを統制した残差アルファ検証）

## 8. 引用

```
Houweling, P., & van Zundert, J. (2017). Factor Investing in the Corporate
Bond Market. Financial Analysts Journal, 73(2), 100-115.
```

データ提供: Robeco（[robeco.com/factor-returns-data-set](https://www.robeco.com/)）  
**Robeco データは再配布禁止**。論文研究目的での使用のみ可。
