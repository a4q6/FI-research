# Cochrane & Piazzesi (2005) 再現

> Cochrane, J. H., & Piazzesi, M. (2005). "Bond Risk Premia." *American Economic Review*, 95(1), 138–160.

## 1. 論文の主張

- 1 年・2 年・…・5 年フォワードレート（1 年フォワード）の **単一線形結合**（CP factor）が、2-5 年国債の超過リターンの **約 30-44% を予測**する
- ファクター係数は **テント型** — 中央満期で正・両端で負
- 1 因子制約は満期横断で頑健（unrestricted full-forward 回帰の R² ≈ single-factor R²）
- これが Affine Term Structure Model の標準化に大きな影響を与えた

## 2. 再現対象

- **Table 2 相当**: rx^(n) ~ y_t^(1) + f_t^(2) + f_t^(3) + f_t^(4) + f_t^(5) の unrestricted 回帰、満期 n=2..5 別の R² と係数
- **Figure 1 相当**: テント型係数パターン
- **Single-factor**: CP factor = rx_avg ~ forwards の fitted、これで再回帰して R² 比較
- 3 サンプル: 論文期間 (1964-2003)、論文後 (2004-2025)、フル (1971-2025)

## 3. データ

| 項目 | ソース | loader |
|---|---|---|
| 米国財務省 zero coupon yield (1y-5y) | GSW NSS smoothed curve | `fi_research.data.treasury.load_gsw_nominal` |

- 月次サンプリング: 各月末の最後の営業日の zero yield
- フォワードレート: `f^(n→n+1) = n·y^(n) − (n−1)·y^(n−1)` (連続複利、年率小数換算)
- 超過リターン: `rx_{t+12}^(n) = p_{t+12}^(n−1) − p_t^(n) − y_t^(1)`

## 4. 実行

```bash
python projects/replications/cochrane_piazzesi_2005/scripts/replicate.py
```

成果物: `results/`
- `r2_summary.csv` — サンプル × モデル別 R²
- `tent_shape_cp_paper_1964_2003.png` / `_full_1971_2025.png` — 係数プロット
- `cp_factor.parquet` — 月次 CP factor 時系列
- `monthly_yields_forwards.parquet` — 月次 zero yields + forwards
- `monthly_excess_returns.parquet` — 12 ヶ月先 1 年ホールド超過リターン

## 5. 結果サマリ

### 5.1 論文サンプル (1964-01 〜 2003-12, n=480)

**Unrestricted regression** `rx^(n) ~ const + f1 + f2 + f3 + f4 + f5`:

| n | R² | b_f1 | b_f2 | b_f3 | b_f4 | b_f5 |
|---|---:|---:|---:|---:|---:|---:|
| 2 | 0.203 | -1.19 | +1.38 | +0.87 | -1.37 | +0.51 |
| 3 | 0.227 | -2.35 | +2.71 | +1.21 | -1.98 | +0.73 |
| 4 | 0.245 | -3.43 | +4.21 | +0.51 | -1.51 | +0.66 |
| 5 | 0.258 | -4.45 | +5.75 | -0.21 | -1.58 | +1.06 |

**Single-factor regression** `rx^(n) ~ const + cp_factor`:

| n | R² | b_cp |
|---|---:|---:|
| 2 | 0.199 | +0.43 |
| 3 | 0.226 | +0.83 |
| 4 | 0.245 | +1.20 |
| 5 | 0.257 | +1.54 |

### 5.2 論文後サンプル (2004-01 〜 2025-12, n=257)

| n | unrestricted R² | single-factor R² |
|---|---:|---:|
| 2 | 0.189 | 0.175 |
| 3 | 0.200 | 0.198 |
| 4 | 0.229 | 0.229 |
| 5 | 0.265 | 0.262 |

### 5.3 フルサンプル (1971-08 〜 2025-12, n=646)

| n | unrestricted R² | single-factor R² |
|---|---:|---:|
| 2 | 0.132 | 0.122 |
| 3 | 0.133 | 0.131 |
| 4 | 0.142 | 0.142 |
| 5 | 0.154 | 0.152 |

## 6. 論文との乖離と解釈

### 6.1 R² の絶対水準

- **論文 (Fama-Bliss data, 1964-2003)**: R² ≈ 0.32 〜 0.37（rx2 〜 rx5）
- **本再現 (GSW data, 1964-2003)**: R² ≈ 0.20 〜 0.26

10〜15 ポイント低い。原因は **GSW (Svensson 6 パラメータ平滑化) vs Fama-Bliss (bootstrap)** の手法差。GSW は滑らかな曲線を強制するため、フォワードレートの「不規則変動」が抑制され、これが超過リターンとの相関を弱めている可能性。Fama-Bliss を WRDS 経由で取得すれば再現精度が上がる見込み。

### 6.2 テント型パターン

論文 Figure 1 の典型例 (rx^(5)):
- y_t^(1): 大きく負 (-2.1 程度)
- f_t^(2): 中程度に正 (+0.8)
- f_t^(3): 大きく正 (+3.0) — **テントの頂点**
- f_t^(4): 中程度に正 (+0.8)
- f_t^(5): やや負 (-2.1)

本再現の rx^(5):
- f_1 = y_1: -4.45 (大きく負) ✓
- f_2: +5.75 (大きく正) ← 論文より頂点が左にシフト
- f_3: -0.21
- f_4: -1.58
- f_5: +1.06

**完全なテント型は再現できていない**。GSW では頂点が f_2 にシフトし、f_3 以降は不規則。これも GSW の平滑化に起因する可能性が高い（GSW NSS では隣接フォワードが強く相関するため、テントの頂点の位置が data 上不安定）。

### 6.3 単一因子制約（最も重要な結論）

論文の核となる主張「CP factor 1 つで満期横断の超過リターン予測の大半を説明」は **完全に再現できた**。各サンプル・各満期で `unrestricted R² ≈ single-factor R²`（差は 0.01 未満）。

| サンプル | 平均 unrestricted R² | 平均 single-factor R² | 差 |
|---|---:|---:|---:|
| 1964-2003 | 0.233 | 0.232 | 0.001 |
| 2004-2025 | 0.221 | 0.216 | 0.005 |
| 1971-2025 | 0.140 | 0.137 | 0.003 |

### 6.4 論文後サンプル (2004-2025) の挙動

CP の予測力は **論文後も維持されている**（R² ≈ 0.18-0.26）。これは興味深い発見:
- A1 (SHAP × 債券) で CP factor を **線形ベンチマーク** として使う妥当性を支持
- ML 手法が CP factor を超える追加情報を捕捉できるかが A1 の検証ポイント

### 6.5 フルサンプルでの R² 低下

フル 1971-2025 で R² が 0.13 に低下。これは:
- 2008-2025 のゼロ金利・QE 期間でフォワードレートのダイナミクスが変化
- 構造変化の存在を示唆 → A1 でレジーム依存 ML が有効になる可能性

## 7. 次に進める派生分析

- [ ] WRDS 経由で Fama-Bliss yields を取得し、論文 R² (0.32-0.37) を厳密再現
- [ ] CP factor の時変係数 (rolling regression / Kalman filter) でレジーム性を可視化
- [ ] A1 文脈で CP factor を ML benchmark、SHAP で「CP factor 以外の非線形寄与」を抽出
- [ ] Ludvigson-Ng (2009) のマクロ PC と CP factor を同時に投入する augmented 回帰（→ `ludvigson_ng_2009/` で実装予定）

## 8. 引用

```
Cochrane, J. H., & Piazzesi, M. (2005). Bond Risk Premia.
American Economic Review, 95(1), 138-160.
```

データソース:
```
Gürkaynak, R. S., Sack, B., & Wright, J. H. (2007). The U.S. Treasury yield
curve: 1961 to the present. Journal of Monetary Economics, 54(8), 2291-2304.
```
