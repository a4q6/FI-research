# Gilchrist & Zakrajšek (2012) 再現

> Gilchrist, S., & Zakrajšek, E. (2012). "Credit Spreads and Business Cycle Fluctuations." *American Economic Review*, 102(4), 1692–1720.

## 1. 論文の主張

- 米国社債スプレッドを (a) 予想デフォルト成分 と (b) **Excess Bond Premium (EBP)** に分解
- EBP は実体経済活動（生産・雇用・失業率）の **強い先行指標**
- EBP は反景気循環的で、危機時にスパイク（NBER recession に先行）
- 1973-2010 の予測回帰で EBP の係数は強く有意（t-stat 5-10）

## 2. 再現対象

- **Figure 1-3 相当**: GZ spread / EBP / 予想デフォルト確率の時系列
- **Table 1 相当**: 予測回帰 — h=3,6,12,24 ヶ月先の Δlog IP / Δlog Payroll / ΔUR を `EBP + 期間スプレッド + 実質 FF レート` で回帰
- **NBER 不況期との重ね合わせ**
- **3 サンプル**: 論文 (1973-2010)、論文後 (2011-2025)、フル (1973-2025)

**注**: 企業レベルの社債データから EBP 自体を構築する作業（TRACE + Compustat + Mergent FISD 必要）は **省略**。Favara, Gilchrist, Lewis, Zakrajšek (2016) FEDS Note が更新版を公開しており、`fi_research.data.frb_ebp` でロード済。

## 3. データ

| 項目 | ソース | loader |
|---|---|---|
| GZ spread / EBP / est_prob | FRB FEDS Notes update | `fi_research.data.frb_ebp.load_ebp` |
| INDPRO / PAYEMS / UNRATE | FRED | `fi_research.data.fred.load_panel` |
| T10Y3M / DFF / CPIAUCSL / USREC | FRED | 同上 |

実質 FF レート = DFF − 12 ヶ月 CPI 前年比

## 4. 実行

```bash
python projects/replications/gilchrist_zakrajsek_2012/scripts/replicate.py
```

成果物: `results/`
- `monthly_panel.parquet` — EBP + マクロの月次パネル
- `predictive_regressions.csv` — 全 36 回帰結果
- `ebp_timeseries.png` — GZ spread, EBP, est_prob の時系列（NBER シェード付き）
- `predictive_r2_heatmap.png` — サンプル × ターゲット × ホライズン別の R² ヒートマップ

## 5. 結果サマリ

### 5.1 論文サンプル (1973-2010, EBP 係数と t-stat)

| ターゲット | h=3m | h=6m | h=12m | h=24m |
|---|---:|---:|---:|---:|
| Δlog IP | **-1.30** (t=-5.79) | **-2.10** (t=-5.06) | **-2.53** (t=-3.77) | **-2.22** (t=-2.09) |
| Δlog Payroll | **-0.52** (t=-8.60) | **-1.00** (t=-9.31) | **-1.69** (t=-10.28) | **-2.20** (t=-6.84) |
| ΔUR | **+0.31** (t=+6.47) | **+0.57** (t=+6.95) | **+0.84** (t=+7.26) | **+0.81** (t=+3.40) |

R² 範囲: 0.25 〜 0.60。**論文の主要結論を完全に再現**。EBP は実体経済の強い先行指標。

### 5.2 論文後サンプル (2011-2025, n≈170)

| ターゲット | h=3m | h=6m | h=12m | h=24m |
|---|---:|---:|---:|---:|
| Δlog IP | -0.16 (t=-0.19) | +0.04 (t=+0.03) | -0.19 (t=-0.13) | +2.91 (t=+1.95) |
| Δlog Payroll | -0.34 (t=-0.95) | +0.09 (t=+0.13) | -0.36 (t=-0.42) | -0.22 (t=-0.18) |
| ΔUR | +0.22 (t=+0.91) | -0.25 (t=-0.41) | +0.08 (t=+0.12) | -0.46 (t=-0.58) |

R² ≈ 0.01-0.12、**全係数が統計的に無意味**。

### 5.3 フルサンプル (1973-2025)

| ターゲット | h=3m | h=6m | h=12m | h=24m |
|---|---:|---:|---:|---:|
| Δlog IP | -1.19 (t=-4.60) | -1.93 (t=-4.03) | -2.41 (t=-3.51) | -1.25 (t=-1.60) |
| Δlog Payroll | -0.53 (t=-7.01) | -0.97 (t=-5.83) | -1.74 (t=-6.81) | -2.25 (t=-6.53) |
| ΔUR | +0.32 (t=+5.38) | +0.54 (t=+3.94) | +0.89 (t=+4.61) | +0.81 (t=+3.44) |

論文期間の強い結果が薄まる形だが、Payroll と UR では依然有意。

## 6. 解釈：論文後の EBP 予測力の崩壊

**最も重要な発見**: EBP の景気予測力は **2011 年以降ほぼ消失**している。原因の仮説:

1. **QE による信用スプレッド圧縮**: 中央銀行が信用市場に直接介入し、EBP が情報を反映しなくなった可能性
2. **「正常な景気循環」の欠如**: 2011-2019 は緩やかな拡大、2020 はコロナという外生ショック、2022 はインフレショック。EBP が予測してきた「クレジット主導の景気後退」が起きていない
3. **企業金融構造の変化**: 私募債・プライベートクレジット市場の拡大で、公開社債市場が経済を代表しなくなった
4. **構造変化に対する EBP モデル自体の陳腐化**: GZ (2012) は 1973-2010 にキャリブレートされており、ポスト QE 期のリスクプライシングを反映できていない可能性

これは **A1 (SHAP × 債券) に重要な示唆**を与える:
- 線形 EBP の予測力がレジーム依存的に変化する → 非線形・状態依存モデルの必要性
- SHAP で「EBP が効く期間」と「効かない期間」を識別できれば、線形手法に対する明確な貢献

また **A2 (ポスト BBW) にも関連**:
- 社債市場のリスクファクター構造が 2010 年代以降変化した可能性
- 公開データだけで構造変化の存在を示唆できる強力な材料

## 7. 次に進める派生分析

- [ ] VAR (EBP, IP, UR, FF) で衝撃応答関数を比較（論文 Figure 6 相当）
- [ ] レジーム別 (NBER vs non-NBER、QE vs non-QE) で予測力を分解
- [ ] EBP の構成要素 (GZ spread vs est_prob) を分けた予測回帰
- [ ] OFR FSI、NFCI、MOVE を EBP の代替として並べた horse race
- [ ] A1 で EBP を SHAP モデルに投入し、非線形寄与の時変性を可視化

## 8. 引用

```
Gilchrist, S., & Zakrajšek, E. (2012). Credit Spreads and Business Cycle
Fluctuations. American Economic Review, 102(4), 1692-1720.

Favara, G., Gilchrist, S., Lewis, K. F., & Zakrajšek, E. (2016). Updating
the Recession Risk and the Excess Bond Premium. FEDS Notes, Board of
Governors of the Federal Reserve System.
```
