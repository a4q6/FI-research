# A2 main project — plan

最終収束テーマ [[research-themes]]: **post-BBW 社債ファクター構造の再評価**。  
本フォルダはその主分析の場。Entry point は [[novel-findings-2026-05]] の **regime-dependent MP transmission to credit (C.3)**。

## 1. 中核的な研究仮説

> **H1 (main)**: Bai-Bali-Wen (2019) の社債ファクターアルファの一部は、Bauer-Swanson (2023) 直交化 MP ショック × 信用ストレスレジームの相互作用に吸収される。FGX (2020) double-selection LASSO で regime-MP 変数を controlling すると、Robeco 4 ファクターの独立 α が消える / 弱まるはず。

> **H2 (corollary)**: regime-MP 変数自体は社債横断面で priced (Fama-MacBeth)。これは Gertler-Karadi (2015) credit channel の cross-sectional 帰結。

> **H3 (auxiliary)**: 独立な α が残るのは Size のみ ([[feasibility-findings-2026-05]] で確認済) であり、これは regime-MP に吸収されない構造的プレミアム → A2 の最終的な「残った 1 ファクター」候補。

## 2. データ依存関係

| ファイル | 役割 | 上流 |
|---|---|---|
| `results/monthly_mp_regime_exposure.parquet` | 月次パネル: mps_orth_sum, mps×FSI_sum, FSI 月末値 等 | scripts/step1_*  |
| `projects/00_exploration/results/01_macro_credit_state/monthly_panel.parquet` | FRED 45 + EBP + OFR FSI + MOVE + Robeco の月次マスタ | (作成済) |
| `data/processed/robeco_credit_factors_{IG,HY}.parquet` | Robeco 月次因子 | (作成済) |
| `data/processed/mp_shocks_fomc_2023update.parquet` | BS FOMC-level shocks | (作成済) |
| `data/processed/ofr_fsi.parquet` | OFR FSI 日次 | (作成済) |

## 3. 実装ステップ（依存順）

### Step 1 — Monthly MP × regime exposure (scripts/step1_mp_regime_exposure.py)

入力: FOMC events (1988-2023, 361 イベント), OFR FSI daily, Fed BS YoY  
出力: `results/monthly_mp_regime_exposure.parquet`

計算する月次系列:
- `mps_orth_sum_t`: 月 t に発生した FOMC イベントの mps_orth の総和
- `mps_x_fsi_sum_t`: 同じく mps_orth × FSI_d の総和（FSI は FOMC 日の値）
- `mps_x_fsi_z_sum_t`: FSI を z-score 化した版
- `mps_count_t`: 月 t の FOMC イベント数（control 用）
- `fsi_eom_t`: 月末の OFR FSI level
- `walcl_yoy_t`: 月末の Fed BS YoY（QE proxy）

### Step 2 — Time-series α test (scripts/step2_alpha_test.py)

入力: Step 1 の monthly_mp_regime_exposure + Robeco IG/HY 因子  
出力: `results/alpha_table.csv`

回帰モデル群:
- (a) baseline: `factor_t ~ α + ε` (raw mean)
- (b) MP-only: `factor_t ~ α + β·mps_orth_sum + ε`
- (c) FSI: `factor_t ~ α + β·FSI_eom + ε`
- (d) interaction: `factor_t ~ α + β1·mps + β2·mps×FSI + β3·FSI + ε`
- (e) full controls: (d) + Robeco 他 3 因子 + マクロ
- HAC SE (lag=6) で α の t-stat 報告

H1 の判定基準: model (e) で Robeco 4 因子 + MultiFactor の α |t| が baseline より 30%+ 低下 = "MP-regime が α の一部を吸収"。

### Step 3 — FGX double-selection LASSO (scripts/step3_fgx_lasso.py)

入力: Step 1 の exposure + 17 候補ファクター  
出力: `results/fgx_selected_factors.csv`, `results/fgx_alpha_post_selection.csv`

候補ファクター (17):
- Robeco 4: Size, LowRisk, Value, Momentum
- マクロ 11: INDPRO, PAYEMS, UNRATE, CPI, PCE, DFF, DGS10, T10Y3M, T10Y2Y, BAA10Y, AAA10Y (stationarized)
- regime-MP 3: mps_orth_sum, mps_x_fsi_sum, fsi_eom

手順 (FGX 2020 §3):
1. **Step A**: 各社債ファクターポートフォリオの α を全 17 候補で LASSO 選択 (cross-validated λ)
2. **Step B**: 各候補を残り 16 候補で LASSO 選択
3. **Step C**: A と B の和集合のみ統制した OLS で α 検定（post double-selection inference）

H1 判定: regime-MP の 1 つ以上が Step A or B で selected され、Step C で Robeco 4 因子のうち少なくとも 1 つの α が消える。

### Step 4 (将来) — Fama-MacBeth cross-section
### Step 5 (将来) — Sub-sample BBW pre/post + 日本社債拡張

## 4. ファイル配置

```
projects/a2_main/
├── plan.md                          ← 本ファイル
├── README.md                        ← 結果サマリ（実装後に追記）
├── scripts/
│   ├── step1_mp_regime_exposure.py
│   ├── step2_alpha_test.py
│   ├── step3_fgx_lasso.py
│   └── (step4_, step5_)
├── notebooks/
│   ├── 01_step1_exposure.ipynb     ← step 完了後に build_notebooks.py で生成
│   ├── 02_step2_alpha.ipynb
│   └── 03_step3_fgx.ipynb
├── results/                         ← parquet / csv / png
└── figures/                         ← 論文用の最終図
```

## 5. 既存資産の再利用方針

- replications/HvZ から: Robeco data loader、論文 Table 3 IR の参照値
- replications/BS から: mps_orth の予測可能性 / Fed-day reaction 結果（intro / methodology の引用元）
- derivatives/A.1 から: BAA10Y proxy 直交化の妥当性 (公開データで論文 IR を再現できる根拠)
- derivatives/B.2 から: regime decomposition の方法論
- derivatives/C.3 から: **monthly aggregation の interaction 結果が main hypothesis の根拠**
- 00_exploration/01-03 から: monthly_panel, daily_panel, spanning regression

## 6. 評価軸

### "回るか"のチェック
- [ ] Step 1: monthly_mp_regime_exposure.parquet が ~430 行で出力される
- [ ] Step 2: Robeco IG MultiFactor の α が model (a) 1.53% → model (e) で X.XX% に変化（H1 検証）
- [ ] Step 3: regime-MP 3 変数のうち 1 つ以上が Step A or B で selected
- [ ] Step 3: post-selection で α |t| が baseline より低下

### 論文化に耐えるか
- HAC / Newey-West SE で全 α t-stat 報告
- サブサンプル (pre-BBW 1994-2018 vs post-BBW 2019-2025) で stability check
- 多重比較対応 (Bonferroni or FDR) は Section 5 で実施

## 7. 議論されるべきリスク / 限界

- **規模 1**: HY OAS データなしのため、HY 因子は credit beta 控除が IG ほど精緻でない
- **規模 2**: OFR FSI が 2000-01 開始 → 1994-1999 の Robeco 期間が regime-MP analysis から脱落 (n=72 月)
- **規模 3**: 月次集計の MP exposure は intra-month の timing 効果を消す → robust check に persistent IRF (C.2 の LP) を併用
- **規模 4**: BAA10Y proxy は zero coupon でなく par yield 系 → vs WRDS LSTA / TRACE で argue
- **規模 5**: 17 候補は FGX 元論文の 100+ より少ない → robust に "selected" と言うには bootstrap が必要かも

## 8. このプランの更新ポリシー

- Step 1 完了時に Step 2/3 の入力仕様を確定
- 各 step 完了時に README.md に結果サマリを追記
- 新発見や方針変更があれば本 plan.md を更新（変更履歴は git）

## 9. 関連文献（[`docs/handover.md`](../../docs/handover.md) §8 から抜粋 + 追加）

- Bai, Bali, Wen (2019/2023 retraction) — A2 起点
- Houweling & van Zundert (2017) — Robeco data 出典 + ベンチマーク
- Feng, Giglio, Xiu (2020) — Step 3 メイン手法
- Bauer & Swanson (2023) — mps_orth の根拠
- Gertler & Karadi (2015) — Step 3 H2 の理論基盤
- Kozak, Nagel, Santosh (2020) — Step 4 (将来) の補完手法
