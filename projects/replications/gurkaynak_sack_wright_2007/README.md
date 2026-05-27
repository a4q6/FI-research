# Gürkaynak, Sack & Wright (2007) 再現／検証

> Gürkaynak, R. S., Sack, B., & Wright, J. H. (2007). "The U.S. Treasury yield curve: 1961 to the present." *Journal of Monetary Economics*, 54(8), 2291–2304.

## 1. 論文の主張

- Svensson (1994) の 6 パラメータ拡張 Nelson-Siegel モデル `y(τ) = β0 + β1·f1(τ,τ1) + β2·f2(τ,τ1) + β3·f3(τ,τ2)` を米国財務省 off-the-run zero coupon yield に適用
- 1961 年 6 月 〜 現在まで日次の連続複利ゼロ利回り曲線を構築・公開
- FRB が daily 更新で公開、bond pricing / monetary economics の **デファクト標準データ**
- 公開フォーマット: BETA0..BETA3, TAU1, TAU2 + SVENY01..SVENY30（ゼロ）+ SVENPY01..SVENPY30（パー）+ SVENF01..SVENF30（瞬間フォワード）+ SVEN1F01/04/09（1年フォワード）

## 2. 再現対象

本論文は **データ構築論文**。NSS パラメータの**再推定**には off-the-run bond の生価格データが必要（WRDS / FRB internal）で公開データだけでは不可能。代わりに以下を検証:

1. **Svensson 公式の検証**: 公開された BETA0..3, TAU1, TAU2 から零クーポン利回りを再計算し、SVENY01..SVENY30 と一致するか
2. **FRED CMT との比較**: GSW (off-the-run zero) と FRED の constant-maturity Treasury yields の系統的差を測定
3. **可視化**: 主要な歴史的日付の曲線、瞬間フォワードレートの形状、長期時系列

## 3. データ

| 項目 | ソース | loader |
|---|---|---|
| NSS パラメータ + 評価済 zero/par/forward | FRB H.15 派生データ | `fi_research.data.treasury.load_gsw_nominal` |
| FRED CMT (DGS1-DGS30) | FRED | `fi_research.data.fred.load_panel` |

NSS パラメータ (BETA0..3, TAU1, TAU2) は **1980-01-02 以降**のみ公開。1961-1980 は SVENY のみ（4-parameter NS で推定、長期パラメータ不明）。

## 4. 実行

```bash
python projects/replications/gurkaynak_sack_wright_2007/scripts/replicate.py
```

成果物: `results/`
- `svensson_verification.csv` — 公式 vs 公開 SVENY の差（bps）
- `fred_comparison.csv` — GSW vs FRED CMT の系統的差
- `yield_curves.png` — 主要日付の曲線（再計算線 + 公開ドット）
- `history_stack.png` — 1y/2y/5y/10y/30y の長期時系列
- `zero_vs_forward_recent.png` — 最新日のゼロ vs 瞬間フォワード

## 5. 結果サマリ

### 5.1 Svensson 公式の検証

| 満期 | 観測数 | max 差 (bps) | 平均差 (bps) | RMS 差 (bps) |
|---|---:|---:|---:|---:|
| 1y | 11,574 | 0.005 | 0.000 | 0.002 |
| 5y | 11,574 | 0.030 | -0.000 | 0.002 |
| 10y | 11,574 | 0.005 | 0.000 | 0.002 |
| 20y | 11,199 | 0.019 | -0.000 | 0.002 |
| 30y | 10,104 | 0.027 | 0.000 | 0.002 |

**全 30 満期で max 差 < 0.04 bps、RMS 差 ≈ 0.002 bps**。つまり Svensson 公式と公開 SVENY は **数値誤差レベルで完全一致**。公開データの内部整合性は完璧。

これにより、任意の満期 τ（非整数含む）で Svensson 公式から zero yield を再構築できることが確認できた → A1 / A2 の派生分析で曲線評価が自由にできる。

### 5.2 FRED CMT との比較

GSW (off-the-run smoothed zero) vs FRED (on-the-run CMT par yield) の差:

| 満期 | n | 平均差 (bps) | RMS 差 (bps) | max 差 (bps) | p99 差 (bps) |
|---|---:|---:|---:|---:|---:|
| 1y | 16,057 | **-5.81** | 18.08 | 128.4 | 74.9 |
| 2y | 12,465 | **-8.12** | 18.50 | 108.4 | 82.7 |
| 3y | 16,057 | **-7.53** | 17.35 | 122.8 | 80.8 |
| 5y | 16,057 | **-6.17** | 18.78 | 135.6 | 89.7 |
| 7y | 14,187 | **-5.36** | 20.56 | 123.0 | 88.7 |
| 10y | 13,658 | **+4.63** | 25.28 | 115.5 | 82.3 |
| 20y | 9,518 | **+12.75** | 27.47 | 114.3 | 87.7 |
| 30y | 10,104 | **+13.59** | 27.75 | 129.3 | 95.1 |

系統的な符号反転（短期で GSW < FRED、長期で GSW > FRED）が観察される。原因:

1. **複利規約**: GSW は連続複利、FRED CMT は半年複利等価。短期では cc < 半年複利、長期では差は小さくなる（5 〜 8 bps の系統差を説明）
2. **on-the-run vs off-the-run**: 流動性プレミアムで on-the-run が低利回り。これが長期で GSW > FRED となる原因（GSW は off-the-run、流動性プレミアム控除前）
3. **par vs zero**: パー利回りはクーポン bond の利回り、ゼロ利回りは割引債。長期では (par yield) < (zero yield) で 5 〜 15 bps 差

**実務的含意**: A1 で曲線パラメータを直接使う場合は GSW（連続複利、滑らか）。トレーディング水準感には FRED CMT。論文化時には GSW を使うのが学界標準。

### 5.3 NSS パラメータの利用可能性

- BETA0, BETA1, BETA2, TAU1: **1961-06 〜 2026-05** (全期間)
- **BETA3, TAU2: 1980-01 〜 2026-05** のみ
- 1961-1979 は 4-parameter Nelson-Siegel（β3=0, τ2 任意）で曲線評価が必要 → SVENY 値はそのまま使えるが、再評価する場合は注意

これは [memory/data_source_caveats.md](../../../.claude/projects/-home-tarai-Research-FI-research/memory/data_source_caveats.md) に追記すべき情報。

## 6. 派生的な発見

### Svensson 公式が正確に再現できることの価値

A1 / A2 / 派生研究で:
- 任意の満期（例: 7.3年）でゼロ利回りを直接評価可能
- 1 年フォワードを連続スペクトルで構築可能（Cochrane-Piazzesi の `f^(n→n+1)` を整数満期に依存せず）
- 曲線のスムーズな第 1・第 2 階微分を解析的に計算可能（duration / convexity の理論値）

### GSW vs FRED の選択基準

| 用途 | 推奨 |
|---|---|
| 学術論文（特にbond pricing） | **GSW** |
| 実務的水準感、メディア参照 | FRED CMT |
| 時系列分析で滑らかさが重要 | **GSW**（スパイク無し） |
| Real-time な on-the-run | FRED CMT |
| 長期超長期（20y, 30y）の解析 | GSW（CMT は欠損あり） |

### A1 / A2 への含意

- **A1**: GSW BETA0..3, TAU1, TAU2 をそのまま XGBoost の入力にできる（曲線形状の 6 パラメータ表現）。SHAP で「level / slope / curvature 寄与」を分解できる
- **A2**: 社債リターンの説明変数として GSW フォワードレートを使う場合、連続スペクトルで自由に取れる
- 共通: NSS パラメータの時変ダイナミクスを VAR や ML でモデル化 → 曲線シフト予測 → 超過リターン予測

## 7. 次に進める派生分析

- [ ] Real (TIPS) GSW (`load_gsw_real`) も同様に Svensson 検証 → 期待インフレ・実質金利の分解
- [ ] BETA0..3 の時変ダイナミクスを Kalman filter / state-space で抽出 → level / slope / curvature factor
- [ ] NSS パラメータ自体の VAR モデル化（Diebold-Li 2006 style）
- [ ] BETA3 / TAU2 の値が NSS（β3=0）と Svensson（β3≠0）の切替の影響を測定

## 8. 引用

```
Gürkaynak, R. S., Sack, B., & Wright, J. H. (2007). The U.S. Treasury
yield curve: 1961 to the present. Journal of Monetary Economics, 54(8),
2291-2304.

Svensson, L. E. O. (1994). Estimating and Interpreting Forward Interest
Rates: Sweden 1992-1994. NBER Working Paper 4871.

Nelson, C. R., & Siegel, A. F. (1987). Parsimonious Modeling of Yield
Curves. Journal of Business, 60(4), 473-489.
```

データ提供: Board of Governors of the Federal Reserve System  
最新: [federalreserve.gov/data/nominal-yield-curve.htm](https://www.federalreserve.gov/data/nominal-yield-curve.htm)
