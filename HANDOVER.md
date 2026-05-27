# HANDOVER（次セッション開始用スナップショット）

最終更新: **2026-05-25**  
次セッション: **A1 / A2 feasibility 予備分析へ**

このファイルは「新しい Claude セッションを開いた時に最初に読む 1 枚紙」です。  
研究テーマや過去の議論経緯は [`docs/handover.md`](docs/handover.md) に詳述、データの全体像は [`docs/data_catalog.md`](docs/data_catalog.md) を参照。

---

## 1. 現状（5 行）

- 公開データのみで構築する FI 研究データ基盤の **整備フェーズが完了**
- 取得済 **30 ソース**、loader **15 モジュール**、processed **約 4.9 GB**（うち EDGAR が ~4.7 GB）
- すべて `data/processed/*.parquet` にローカルキャッシュ済、再 fetch は `force=True` で
- 研究テーマは 2 候補 [`A1: SHAP×債券アトリビューション`](docs/handover.md) と [`A2: ポスト BBW 社債ファクター`](docs/handover.md)
- **次の一手: 整備済データで A1 / A2 の feasibility 予備分析**（→ § 4）

---

## 2. 整備済データ — 即時利用可

| カテゴリ | パッケージ / loader | 主要シリーズ・テーブル |
|---|---|---|
| 金利カーブ | `fi_research.data.treasury` | `gsw_nominal` / `gsw_real` (NSS パラメータ + 各満期 zero/par/forward) |
| 金利 (FRED) | `fi_research.data.fred` | `DGS*` / `DFF` / `SOFR` / `T10Y2Y` 等、45 系列 |
| クレジット | `fi_research.data.fred` + `fi_research.data.frb_ebp` | `BAML*` OAS (5y) / `BAA10Y` / `AAA10Y` / EBP |
| インフレ | `fi_research.data.fred` | `DFII*` / `T*YIE` / CPI / PCE |
| マクロ | `fi_research.data.fred` + `fi_research.data.mp_shocks` | `INDPRO`/`UNRATE`/`USREC` + Bauer-Swanson MPS |
| Vol | `fi_research.data.fred` + `fi_research.data.move` | VIX / OVX / **MOVE** |
| Stress | `fi_research.data.ofr_fsi` + `fi_research.data.fred` | OFR FSI (5 sub + 3 region) / NFCI / STLFSI4 |
| 株式ファクター | `fi_research.data.kenneth_french` | FF5 / Momentum / Industries 12-30-49（m+d） |
| Dealer | `fi_research.data.ny_fed_pd` + `fi_research.data.cftc_tff` | NY Fed PD FR2004 / CFTC TFF |
| 発行体 fundamentals | `fi_research.data.edgar` + `fi_research.data.sec_tickers` + `fi_research.data.openfigi` | EDGAR FSDS 69 quarters / CIK↔ticker (10,371) / ticker→FIGI (9,190 hit) |
| 社債ファクター | `fi_research.data.robeco` | Robeco IG/HY × Size/LowRisk/Value/Momentum/MultiFactor（月次） |

各 loader の使い方とスキーマ詳細: [`docs/data_sources.md`](docs/data_sources.md)。  
俯瞰図: [`docs/data_catalog_coverage.png`](docs/data_catalog_coverage.png)（ガントチャート）。

### ロード cheatsheet

```python
# 金利カーブ
from fi_research.data.treasury import load_gsw_nominal, load_gsw_real
nom = load_gsw_nominal()   # 16,938 行
real = load_gsw_real()     # 7,140 行

# FRED 全 45 系列をワイドパネルで
from fi_research.data.fred import load_panel, DEFAULT_SERIES
fred = load_panel(list(DEFAULT_SERIES))

# クレジット OAS だけ
from fi_research.data.fred import CREDIT_OAS_SERIES
oas = load_panel(list(CREDIT_OAS_SERIES))

# EBP / OFR FSI / MOVE
from fi_research.data.frb_ebp import load_ebp
from fi_research.data.ofr_fsi import load_ofr_fsi
from fi_research.data.move import load_move

# Robeco 社債ファクター
from fi_research.data.robeco import load_robeco_credit_factors
ig = load_robeco_credit_factors("IG")   # 384 行 (1994-2025)
hy = load_robeco_credit_factors("HY")

# Kenneth French
from fi_research.data.kenneth_french import load_dataset
ff5 = load_dataset("ff5_monthly")
ind49 = load_dataset("ind49_monthly")

# Dealer
from fi_research.data.ny_fed_pd import load_pd_timeseries, load_pd_catalog
from fi_research.data.cftc_tff import load_all as load_cftc_tff
pd_ts = load_pd_timeseries()          # 735,650 行 long-format
cftc = load_cftc_tff()                # 38,306 行

# EDGAR fundamentals
from fi_research.data.edgar import load_concat, available_quarters
sub_all = load_concat("sub")          # 426,003 filings, 17k CIKs
# num.txt は四半期で 100MB+ なので必要時に load_quarter() か filter 推奨

# 発行体 identifier 橋
from fi_research.data.sec_tickers import load_tickers
from fi_research.data.openfigi import load_mapping
tickers = load_tickers()              # 10,371 行
figi = load_mapping()                 # 10,374 行（9,190 ticker に FIGI、ISIN は 0）

# MP shocks
from fi_research.data.mp_shocks import load_mp_shocks
mps_fomc = load_mp_shocks("fomc_2023update")
mps_monthly = load_mp_shocks("monthly_2023update")
```

---

## 3. 環境セットアップ

```bash
cd /home/tarai/Research/FI-research
pip install -e .                # pyproject.toml 完備
```

### `.env`（既に存在、git ignore 済）

```bash
FRED_API_KEY=...                # FRED 全 45 系列
EDGAR_USER_AGENT=Takumi Arai takumi.arai2@gmail.com   # SEC EDGAR / company_tickers
OPENFIGI_API_KEY=...            # OpenFIGI、25 req/min × 100 IDs/req
```

`fi_research.env.load_project_env()` が `.env` を auto-load する。シェル export しなくても loader から透過的に読まれる。

### sanity check

```python
from fi_research.data.fred import load_panel, DEFAULT_SERIES
from fi_research.data.edgar import available_quarters
from fi_research.data.openfigi import load_mapping

assert len(load_panel(list(DEFAULT_SERIES))) > 5000
assert len(available_quarters()) == 69
assert len(load_mapping()) > 10_000
```

---

## 4. 次セッションのアクションプラン（A1 / A2 feasibility）

### 全体方針

整備済データで「A1 と A2 のどちらが（または両方が）実装可能か」を予備分析で診断し、研究テーマを 1 つに収束させる。`projects/00_exploration/` に番号付き Jupyter ノートブックを置く（[`memory/work_conventions.md`](.claude/projects/-home-tarai-Research-FI-research/memory/work_conventions.md) の規約）。

### 推奨初手 — 3 つの notebook

**`01_macro_credit_state.ipynb`** — マクロ × クレジットの状態空間整備
- FRED 全 45 系列 + EBP + OFR FSI + MOVE + MPS を 1 つの月次/日次パネルにマージ
- レジーム分け: NBER リセッション、ストレス局面（OFR FSI > +1σ）、金融緩和/引締めサイクル
- 簡易回帰: `BAML IG OAS ~ EBP + NFCI + MOVE + USREC` で R² 0.7+ が出るか確認
- **A1 にも A2 にも共通のインフラ**

**`02_a1_shap_sketch.ipynb`** — A1 feasibility
- 月次社債リターン代理として **Robeco IG MultiFactor** + **BAML OAS 変化** + **DGS10 変化** を従属変数候補に
- XGBoost / LightGBM で `Δyield ~ Δlevel + Δslope + ΔOAS_BAA + ΔVIX + ΔMOVE + ΔEBP + Δ(NFCI)` 等を学習
- SHAP 分解 → 線形 OLS 分解との比較で「非線形寄与」の存在量を数値化
- **GO/NO-GO 判断**: 非線形寄与が「金利系」「クレジット系」「ボラ系」のどこに偏るか

**`03_a2_robeco_replication.ipynb`** — A2 feasibility
- Robeco IG / HY × Size/LowRisk/Value/Momentum/MultiFactor を月次パネルに
- Fama-MacBeth 風に market + Robeco factor を回帰、α と t 統計量
- 横断的回帰: BBW 撤回後の論点（factor の独立性、cross-sectional R², 構造変化）を Robeco で再現
- EDGAR fundamentals（Leverage / Profitability）を CIK→ticker→FIGI 経由で merge 可能か、社債側 ID（CUSIP/ISIN）の不在を確認
- **GO/NO-GO 判断**: 公開データだけで A2 の最小実証が成立するか

### 進め方

1. **`01_*` を最初に作る** → A1/A2 共通の baseline
2. `02_*` と `03_*` を並行 — どちらが「素直に走るか」見る
3. 詰まったポイント（特に A2 の社債識別子）を記録 → 次の作業で WRDS や別経路の必要性が見える
4. 1 週間ペースで結果を `projects/00_exploration/README.md` に蓄積

---

## 5. 重要 caveat（コピペ可、つまずきポイント）

1. **FRED の BAML OAS は過去 5 年のみ**（ライセンス制約）。長期は `BAA10Y` / `AAA10Y` で proxy
2. **OpenFIGI Mapping は ISIN を返さない**（仕様）。社債データと CIK を繋ぐには別経路
3. **NY Fed PD の旧 seriesbreak は catalog に無い**（現行 SBN2024 のみ）。長期時系列で旧 SB keyid の description が欠落
4. **Yahoo Finance API は仕様変更が時々入る**（MOVE が依存）。論文化時は ICE 公式へ移行
5. **Robeco データは再配布禁止**。論文では Houweling-van Zundert (2017) を引用、raw XLSX を共有しない
6. **EDGAR FSDS は num.txt が 100MB+/quarter**。69 quarters 全結合は数 GB。必要四半期だけ filter 推奨

全 caveat: [`.claude/projects/-home-tarai-Research-FI-research/memory/data_source_caveats.md`](.claude/projects/-home-tarai-Research-FI-research/memory/data_source_caveats.md)

---

## 6. プロジェクト構造

```
FI-research/
├── HANDOVER.md                      ← 今ここ
├── README.md
├── pyproject.toml                   ← editable install (pip install -e .)
├── .env                             ← API keys (git ignore 済)
├── src/fi_research/
│   ├── env.py                       ← .env auto-load ヘルパー
│   ├── paths.py                     ← DATA_RAW / DATA_PROCESSED
│   └── data/
│       ├── frb_ebp.py
│       ├── treasury.py              ← GSW nominal / real
│       ├── fred.py                  ← 45 系列、カテゴリ別辞書
│       ├── kenneth_french.py        ← FF5 / Mom / Industries 12-30-49
│       ├── ofr_fsi.py
│       ├── ny_fed_pd.py
│       ├── edgar.py                 ← FSDS 69 quarters
│       ├── sec_tickers.py
│       ├── openfigi.py
│       ├── robeco.py
│       ├── move.py
│       ├── cftc_tff.py
│       └── mp_shocks.py
├── data/
│   ├── raw/                         ← git ignore（5.4 GB）
│   └── processed/                   ← git ignore（4.9 GB）
├── docs/
│   ├── data_sources.md              ← loader 詳細・スキーマ
│   ├── data_catalog.md              ← 横断マスタ・俯瞰
│   ├── data_catalog_coverage.png    ← ガントチャート
│   └── handover.md                  ← 研究テーマ議論経緯（長文）
├── projects/00_exploration/         ← ★次セッションで notebook を置く場所
└── references/
```

---

## 7. 関連ドキュメント早見

| ファイル | 役割 |
|---|---|
| [`docs/data_catalog.md`](docs/data_catalog.md) | 横断データマスタ、用途マトリクス、未取得データ |
| [`docs/data_sources.md`](docs/data_sources.md) | 各 loader の使い方、スキーマ、用途 |
| [`docs/handover.md`](docs/handover.md) | A1 / A2 テーマの問題意識・新規性・手法（長文） |
| [`memory/research_themes.md`](.claude/projects/-home-tarai-Research-FI-research/memory/research_themes.md) | A1 / A2 + 補助テーマ、収束状況 |
| [`memory/compliance_data_policy.md`](.claude/projects/-home-tarai-Research-FI-research/memory/compliance_data_policy.md) | 公開データ + WRDS 限定の原則 |
| [`memory/data_source_caveats.md`](.claude/projects/-home-tarai-Research-FI-research/memory/data_source_caveats.md) | 隠れた制約・罠 |
| [`memory/work_conventions.md`](.claude/projects/-home-tarai-Research-FI-research/memory/work_conventions.md) | 番号付き Jupyter、APA 引用等の作業規約 |

---

**次セッションで最初にやること**: `projects/00_exploration/01_macro_credit_state.ipynb` を作って、§ 2 の cheatsheet をベースに月次パネルを構築するところから。
