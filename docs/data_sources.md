# データソース運用メモ

公開データのみを対象とする運用ルールと、現時点で実装済みのローダの利用方法。

## ディレクトリ規約

- `data/raw/<source>/<dataset>_<YYYYMMDD>.<ext>` — 上流から取得したそのままのバイト列。取得日付をファイル名に持たせ、複数スナップショット並列保存可。
- `data/raw/<source>/<dataset>_<YYYYMMDD>.json` — メタデータ（URL・取得時刻 UTC・ETag・Last-Modified・content-length・引用）。再現性担保のため取得スクリプトが自動で書き出す。
- `data/processed/<dataset>.parquet` — 整形後のテーブル。型保持・圧縮の利点から Parquet を採用。SQLite は採用しない（DataFrame ベースでの分析が中心）。

## 実装済みローダ

### FRB Excess Bond Premium（EBP）

- 上流: `https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv`
- 出典: Favara, Gilchrist, Lewis & Zakrajšek (2016) "Updating the Recession Risk and the Excess Bond Premium", FEDS Notes。原論文は Gilchrist & Zakrajšek (2012, *AER* 102(4))。
- 更新頻度: 月次
- カバレッジ: 1973-01 〜 直近月（2026-05-21 取得時点で 2026-04 まで、640 ヶ月）

#### 使い方

```python
from fi_research.data.frb_ebp import fetch_ebp, load_ebp

# 取得 + 保存（同日中の再取得はキャッシュを使用、force=True で強制再取得）
result = fetch_ebp()
print(result.raw_path, result.processed_path)

# DataFrame だけ欲しい（キャッシュ優先、refresh=True で再ダウンロード）
df = load_ebp()
df.head()
```

#### スキーマ

| 列名 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 月初日付 |
| `gz_spread` | float64 | Gilchrist-Zakrajšek スプレッド（社債利回り - リスクフリー） |
| `ebp` | float64 | Excess Bond Premium（GZ スプレッドから予想デフォルト成分を控除した残差） |
| `est_prob` | float64 | 12ヶ月先リセッション確率の推定値 |

#### 用途

- **A1**（SHAP アトリビューション）: 月次マクロ要因の1つとして EBP / GZ スプレッドを feature 候補に組み込む
- **A2**（ポスト BBW）: 横断的ファクター回帰における systemic credit risk のプロキシ

---

### FRED（Federal Reserve Economic Data）

- 上流: `https://api.stlouisfed.org/fred/series/observations` （[API doc](https://fred.stlouisfed.org/docs/api/fred/series_observations.html)）
- 出典: Federal Reserve Bank of St. Louis, FRED
- 認証: 無料 API key（[取得ページ](https://fred.stlouisfed.org/docs/api/api_key.html)）
- 形式: JSON 観測列

#### API key の設定

```bash
# .bashrc / .zshrc 等に追記、または都度 export
export FRED_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

API key を引数で渡すことも可能（`fetch_series(..., api_key="xxx")`）。`data/raw/fred/*.meta.json` に書き出される URL は API key を `***` でマスクする。

#### シリーズ・カタログ（用途別）

`fi_research.data.fred` に用途別の辞書を定義済み。`DEFAULT_SERIES` はそれらの union（合計 45 系列、後方互換）。

**金利 (`RATES_SERIES`、14 系列)** — Treasury constant maturity 3mo〜30y、term spread、policy rate (DFF/SOFR)

| 例 | 内容 |
|---|---|
| `DGS3MO / DGS2 / DGS5 / DGS10 / DGS30` | 国債利回り（CMT、日次） |
| `T10Y2Y / T10Y3M` | 期間スプレッド（後者は NY Fed リセッション確率の根拠） |
| `DFF / SOFR` | 政策金利関連 |

**クレジット OAS (`CREDIT_OAS_SERIES`、11 系列)** — ICE BofA インデックス系の OAS と Moody's レガシー

| 例 | 内容 |
|---|---|
| `BAMLC0A0CM` | IG 全体 OAS（日次、1996-12〜） |
| `BAMLC0A1CAAA` 〜 `BAMLC0A4CBBB` | IG 格付け別 OAS（AAA / AA / A / BBB） |
| `BAMLH0A0HYM2` | HY 全体 OAS |
| `BAMLH0A1HYBB` / `BAMLH0A2HYB` / `BAMLH0A3HYC` | HY 格付け別（BB / B / CCC&Lower） |
| `BAA10Y / AAA10Y` | Moody's レガシー（1953〜、長期サンプル用） |

> ⚠️ **ライセンス制約**: FRED 経由の ICE BofA OAS（`BAMLC*` / `BAMLH*`）は ICE Data Indices のライセンス条件により**過去 5 年のみ**しか取れない（取得時点で 2023-05〜）。長期分析が必要なら Moody's レガシー（`BAA10Y` / `AAA10Y`、1953〜）で代用するか、ICE/BofA を直接購読する経路を別途検討する。格付け別 OAS の長期履歴は無料経路では薄い。

**インフレ・実質 (`INFLATION_SERIES`、10 系列)** — TIPS 利回りと breakeven、価格指数

| 例 | 内容 |
|---|---|
| `DFII5 / DFII10 / DFII30` | TIPS CMT（日次） |
| `T5YIE / T10YIE` | 5y / 10y breakeven（日次） |
| `T5YIFR` | 5y, 5y forward breakeven |
| `CPIAUCSL / PCEPI` | 価格指数（月次、SA） |

**マクロ実体 (`MACRO_SERIES`、5 系列)** — 生産・労働・GDP・NBER リセッション

| 例 | 内容 |
|---|---|
| `INDPRO / UNRATE / PAYEMS / GDPC1` | 主要マクロ |
| `USREC` | NBER リセッションダミー（月次、0/1） |

**ボラティリティ (`VOL_SERIES`、2 系列)** — `VIXCLS`（株式 vol）、`OVXCLS`（原油 vol）。MOVE（金利 vol）は FRED にないので別途検討

**金融状況 (`FIN_CONDITIONS_SERIES`、3 系列)** — `NFCI` / `ANFCI`（Chicago Fed、週次）、`STLFSI4`（St. Louis Fed、週次）。EBP と並ぶ systemic risk proxy

#### 使い方

```python
from fi_research.data.fred import fetch_series, load_panel, DEFAULT_SERIES

# 1 シリーズ取得
result = fetch_series("DGS10", start="2000-01-01")
result.df.tail()

# 複数シリーズをワイドな panel として読む
panel = load_panel(list(DEFAULT_SERIES))
panel.tail()
```

#### スキーマ

`fetch_series` / `load_series` が返す DataFrame:

| 列名 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 観測日 |
| `value` | float64 | 値（`.` は NaN に変換済） |
| `series_id` | object | シリーズ ID |

`load_panel` は `date` + 各 `series_id` 列のワイド表。

#### 使い方の例

```python
from fi_research.data.fred import (
    fetch_many, load_panel,
    DEFAULT_SERIES, CREDIT_OAS_SERIES, RATES_SERIES,
)

# 全 45 系列を一気にローカル取得（FRED_API_KEY 必須）
fetch_many(list(DEFAULT_SERIES))

# クレジット OAS だけワイドパネルで欲しい
oas = load_panel(list(CREDIT_OAS_SERIES))
oas.tail()
```

#### 用途

- **A1**: マクロ feature を 6 カテゴリで揃え、SHAP の「金利系 / クレジット系 / マクロ系」サブ寄与の分解が可能に
- **A2**: 格付け別 OAS（IG AAA→BBB、HY BB→CCC）で credit factor のクロスセクション分解、`NFCI` / `STLFSI4` で systemic state を条件付け

---

### Kenneth French Data Library

Tuck School of Business 公開の Fama-French / Carhart 系ファクター。認証不要、ZIP DL。

- 上流: `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/<filename>.zip`
- 出典: Kenneth R. French Data Library。原典は Fama & French (1993, 2015 *JFE*) と Carhart (1997 *JF*)
- 値: **パーセント単位**で上流配信されているのでそのまま保持（`-0.39` = -0.39%）

#### 取得済みデータセット

| key | 内容 | 頻度 | カバレッジ |
|---|---|---|---|
| `ff5_monthly` | Fama-French 5 factors + RF | 月次 | 1963-07〜 |
| `ff5_daily` | 同上 | 日次 | 1963-07-01〜 |
| `mom_monthly` | Carhart Momentum factor | 月次 | 1927-01〜 |
| `mom_daily` | 同上 | 日次 | 1926-11-03〜 |

各 ZIP には複数セクション（primary returns、annual summary、copyright）が同梱されているが、**primary section だけ抽出**して parquet 化している。

#### 使い方

```python
from fi_research.data.kenneth_french import fetch_dataset, load_dataset, DATASETS

# すべて取得
for key in DATASETS:
    fetch_dataset(key)

# DataFrame だけ欲しい
ff5 = load_dataset("ff5_monthly")
mom = load_dataset("mom_daily")
```

#### スキーマ

| 列名 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 月初日付（月次）または取引日（日次） |
| `Mkt-RF` | float64 | 市場超過リターン（%） |
| `SMB` / `HML` / `RMW` / `CMA` | float64 | Size / Value / Profitability / Investment ファクター（%） |
| `Mom` | float64 | Momentum ファクター（%、Momentum データセットのみ） |
| `RF` | float64 | 1-month T-bill（%、FF5 データセットのみ） |

#### 用途

- **A1**: 債券リターンに対する SHAP 分解時、株式ファクター（特に `Mkt-RF`, `HML`）との同時統制で「非株式系の純粋寄与」を抽出
- **A2**: 株式版 Fama-French / Carhart を benchmark にして、社債版 ファクター（CRF, DRF, LRF 等）と直交化・補完関係を診断

---

### OFR Financial Stress Index

Office of Financial Research（米財務省直下のシンクタンク）が公開する日次の市場ベース金融ストレス指数。総合指数 + 5 カテゴリ + 3 地域分解で、`NFCI` / `STLFSI4` と並ぶ systemic stress proxy だが**より高頻度・成分が独立に取得可能**な点が強み。

- 上流: `https://www.financialresearch.gov/financial-stress-index/data/fsi.csv`
- 出典: Monin, P. J. (2019), "The OFR Financial Stress Index", *Risks* 7(1):25
- 更新頻度: 営業日次、T-2 業務日ラグ
- カバレッジ: 2000-01-03 〜 直近（取得時点で 2026-05-20 まで、6,675 営業日）
- 単位: z-score（長期平均 = 0、正値で stress 上昇）

#### 使い方

```python
from fi_research.data.ofr_fsi import fetch_ofr_fsi, load_ofr_fsi

fetch_ofr_fsi()
df = load_ofr_fsi()
df.tail()
```

#### スキーマ

| 列名 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 観測日（営業日） |
| `ofr_fsi` | float64 | 総合指数（z-score、~0 が長期平均） |
| `credit` | float64 | クレジット系サブインデックス（OAS、CDS 等） |
| `equity_valuation` | float64 | 株式バリュエーション（P/E、ERP 等） |
| `safe_assets` | float64 | 安全資産需要（実質金利、term premium 等） |
| `funding` | float64 | 短期ファンディング（LIBOR-OIS、TED 等） |
| `volatility` | float64 | 暗黙ボラ（VIX、MOVE 等） |
| `united_states` / `other_advanced_economies` / `emerging_markets` | float64 | 地域別寄与 |

カテゴリ和 ≒ 総合指数（厳密に等しいかは構成変更年で確認要）、地域和も同様。

#### 用途

- **A1**: マクロ feature として `NFCI` / `EBP` / `STLFSI4` と並列に投入。SHAP の重要度比較で **どの stress proxy が債券リターンに最も効くか** を診断
- **A2**: `credit` 単独成分を「systemic credit factor」として社債横断回帰に使えば、`NFCI` のような equity-weighted 指数より純粋なクレジット成分が抽出できる
- **イベントスタディ**: 5 カテゴリ分解により、ストレス上昇局面の **「どこから来たか」**（クレジット主導 vs ファンディング主導 vs 安全資産フライト）を identify できる

---

### NY Fed Primary Dealer Statistics (FR2004)

NY 連銀がプライマリーディーラー 24 社から週次集計する Form FR2004 のデータ。**dealer balance sheet 研究の中核ソース**で、ポジション・取引高・レポ・受渡失敗を Treasury / MBS / 社債 / ABS 等の instrument 別に分解した時系列が公開されている。

- 上流: NY Fed Markets Data API（`https://markets.newyorkfed.org/api/pd/...`）
- 出典: Federal Reserve Bank of New York, "Primary Dealer Statistics" (FR2004)
- 認証: 不要だが **User-Agent ヘッダ必須**（ない場合 HTTP 400）
- 更新頻度: 週次、T-7 程度
- カバレッジ: 1998-01-28 〜 直近（取得時点で 2026-05-13、1,930 as-of 日）

#### 取得構造

ローダは 3 アーティファクトを並列管理:

| 名前 | 内容 | 形状 | 用途 |
|---|---|---|---|
| `timeseries` | long-format dump `(as_of_date, keyid, value_millions)` | 735,650 行 × 3 | 本体データ |
| `catalog` | 現行 seriesbreak のシリーズ説明 `(keyid, seriesbreak, description)` | 1,539 行 × 3 | keyid 解釈用 |
| `asofs` | 日付 → seriesbreak の対応 `(as_of_date, seriesbreak)` | 1,930 行 × 2 | taxonomy 跨ぎ判定 |

#### seriesbreak（taxonomy バージョン）

FR2004 のスキーマは複数回改訂されており、各改訂で新シリーズ追加・旧シリーズ廃止・再分類が起きる。期間ごとの seriesbreak:

| seriesbreak | カバー日数 |
|---|---|
| SBP2001 | 179 |
| SBP2013 | 613 |
| SBN2013 | 92 |
| SBN2015 | 635 |
| SBN2022 | 234 |
| SBN2024 | 177（現行） |

> ⚠️ **catalog は現行 SB のみ**: `/list/timeseries.json` は現行 (SBN2024) の 1,539 シリーズしか返さないが、`timeseries` には全 SB 通算で **2,290 ユニーク keyid** がある。差分の 751 シリーズは旧 SB で廃止されたもので **description が取れない**。長期時系列を組むときは `asofs` で SB 境界を識別し、SBN2022 以前の keyid は別途 NY Fed の FR2004 instruction PDF を参照する必要がある。

#### 主要シリーズ族（プレフィックス）

| プレフィックス | 内容 |
|---|---|
| `PDPOS*` | Net positions（longs - shorts）by instrument |
| `PDTRAN*` / `PDTR*` | Transaction volumes |
| `PDFTR*` | Dealer financing（repo / reverse repo） |
| `PDFTD*` | Fails to deliver / receive |
| `PDSORA*` / `PDSIRRA*` | Securities out / in by counterparty type |
| `PDMEGNMA` 系 | MBS-specific positions |

#### 使い方

```python
from fi_research.data.ny_fed_pd import (
    fetch_pd_all,
    load_pd_timeseries, load_pd_catalog, load_pd_asofs,
)

# 全部一括取得（~26MB CSV + 2 つの JSON）
fetch_pd_all()

# 個別ロード（キャッシュ優先）
ts = load_pd_timeseries()
cat = load_pd_catalog()
asof = load_pd_asofs()

# 例: 国債 Net position（PDPOSGS-B-TOT のような keyid）の時系列
gs_pos = ts[ts['keyid'] == 'PDPOSGS-B-TOT'].sort_values('as_of_date')
```

#### スキーマ

`ny_fed_pd_timeseries.parquet`:

| 列名 | 型 | 説明 |
|---|---|---|
| `as_of_date` | datetime64[ns] | 報告対象日（通常水曜） |
| `keyid` | object | シリーズ ID（例: `PDPOSGS-B-TOT`） |
| `value_millions` | float64 | 金額（百万ドル）。ポジション系は long-short |

#### 用途

- **dealer balance sheet 研究**（He-Kelly-Manela 系）: `PDPOS*` の集計で dealer inventory factor を再現
- **liquidity研究**: `PDFTD*` (fails) と `PDFTR*` (repo) で funding-side liquidity を proxy
- **A2 補助**: 社債ポジション `PDPOSCSBND-*` で credit factor の dealer-side 数量シグナルを得る

---

### SEC EDGAR Financial Statement Data Sets

SEC が四半期 ZIP で公開する、米国上場企業の **XBRL 数値ファクト全件ダンプ**。10-K / 10-Q / 8-K 等のファイリングから抽出された us-gaap タグ付き数値が、企業 × タグ × 期間の 3 次元で取得できる。社債発行体 fundamentals 取得の正攻法。

- 上流: `https://www.sec.gov/files/dera/data/financial-statement-data-sets/<YYYYqQ>.zip`
- 出典: U.S. SEC, Division of Economic and Risk Analysis, "Financial Statement Data Sets"
- 認証: 不要だが **User-Agent 必須**（連絡先メアド入り、`https://www.sec.gov/os/accessing-edgar-data`）
- 更新頻度: 四半期、対象四半期終了から 3-6 ヶ月遅れ
- カバレッジ: 2009-Q1 〜 直近公開済四半期（2026-05 時点で 2026-Q1 まで）

#### User-Agent の規約

SEC は `User-Agent` ヘッダに利用者の身元 + 連絡先メアドを含めるよう要求している。loader は次の順で UA を決定:

1. 環境変数 `EDGAR_USER_AGENT`（推奨：自分の名前 + メアド）
2. プロジェクト既定値（`fi-research (mailto:takumi.arai2@gmail.com)`）

```bash
# .env 等に追加（推奨）
export EDGAR_USER_AGENT="Takumi Arai takumi.arai2@gmail.com"
```

#### ZIP 内 4 テーブル構造

| ファイル | 形状（2025q3 例） | 内容 |
|---|---|---|
| `sub.txt` | 6,541 行 × 36 列 | submissions（1 行 = 1 ファイリング、CIK / SIC / form / period 等） |
| `num.txt` | 3,720,081 行 × 10 列 | 数値ファクト（1 行 = 1 (filing, tag, period) ファクト） |
| `tag.txt` | 83,782 行 × 9 列 | タグ辞書（us-gaap / dei / custom、定義込み） |
| `pre.txt` | （DEFAULT_TABLES では取得しない） | 表示順序（通常不要） |

#### 使い方

```python
from fi_research.data.edgar import (
    fetch_quarter, fetch_quarters,
    load_quarter, load_concat, available_quarters,
)

# 単一四半期（sub + num + tag を parquet 化）
fetch_quarter(2025, 3)

# 範囲取得（rate-limit 配慮で sleep_sec=0.2 デフォルト）
fetch_quarters([(2024, q) for q in (1, 2, 3, 4)])

# 個別ロード
sub = load_quarter(2025, 3, "sub")
num = load_quarter(2025, 3, "num")

# 複数四半期を縦結合（手元にあるもの全て）
all_sub = load_concat("sub")
```

#### 主要スキーマ

`sub`（filing メタデータ、抜粋）:

| 列 | 型 | 説明 |
|---|---|---|
| `adsh` | object | accession number（filing 一意 ID、num/pre と join） |
| `cik` | Int64 | 企業 CIK |
| `name` | object | 企業名 |
| `sic` | Int64 | SIC code（業種、e.g. `6020`=Commercial Banks、`6199`=Finance Services） |
| `form` | object | `10-K` / `10-Q` / `8-K` / `6-K` 等 |
| `period` | datetime | 報告対象期間末日 |
| `fy` / `fp` | Int64 / object | 会計年度 / 期（`Q1`〜`Q4`, `FY`） |
| `filed` | datetime | SEC への提出日 |

`num`（数値ファクト）:

| 列 | 型 | 説明 |
|---|---|---|
| `adsh` | object | 親 filing |
| `tag` | object | タグ名（例: `Revenues`, `Assets`, `LongTermDebt`） |
| `version` | object | タクソノミ（`us-gaap/2024` 等） |
| `ddate` | datetime | データ期間末日 |
| `qtrs` | Int64 | 期間長（0 = 期末ストック、1/4 = 四半期/年フロー） |
| `uom` | object | 単位（`USD` 等） |
| `value` | float64 | 数値 |

#### 用途・絞り込み例

```python
# SIC で金融業を除く（社債発行体分析の典型）
non_financial = sub[(sub['sic'] < 6000) | (sub['sic'] >= 7000)]

# 10-K のみ
annual = sub[sub['form'] == '10-K']

# 特定タグの全社時系列（例: 長期負債）
ltd = num[(num['tag'] == 'LongTermDebt') & (num['uom'] == 'USD') & (num['qtrs'] == 0)]
# adsh で sub に join すれば cik / name / sic が付く
ltd_panel = ltd.merge(sub[['adsh','cik','name','sic','period']], on='adsh')
```

#### 用途

- **A2 社債ファクター**: 発行体ファンダメンタル（Leverage, Profitability, Size）を社債リターンと結合し、Bali-Subrahmanyam-Wen ファクターを公開データで再構成
- **A1 SHAP 分解**: マクロ feature に加えて発行体固有の財務 feature を加えることで「マクロ寄与 vs 個別企業寄与」の分解が可能
- **発行体クラスタリング**: SIC + 財務指標で同種企業をグルーピングし、サブセット内のクロスセクション分析
- **イベントスタディ**: `filed` 日を起点に、開示前後の社債リターン挙動を見る（決算サプライズ × クレジット反応）

---

### SEC Company Tickers（CIK ↔ ticker）

EDGAR fundamentals は CIK ベース。これと市場データ（社債価格、Bloomberg / Yahoo / Robeco）を繋ぐ唯一の橋。

- 上流: `https://www.sec.gov/files/company_tickers.json`
- 出典: U.S. SEC
- 認証: User-Agent 必須（EDGAR と同じ規約、`EDGAR_USER_AGENT` を共用）
- 更新頻度: 随時（SEC が継続更新）
- カバレッジ: 取得時点で 10,371 企業

#### 使い方

```python
from fi_research.data.sec_tickers import fetch_tickers, load_tickers
fetch_tickers()
df = load_tickers()
df.head()
# cik, ticker, name の 3 列。EDGAR の sub.cik と inner join
```

#### スキーマ

| 列 | 型 | 説明 |
|---|---|---|
| `cik` | Int64 | SEC CIK（EDGAR と共通キー） |
| `ticker` | object | 米国ティッカー（大文字統一） |
| `name` | object | 企業名 |

#### 用途

- EDGAR `sub.cik` ↔ ticker で社債市場データと結合
- 親会社 / 子会社の関係はカバーされないので、複数 CIK が同じ ticker を共有するケースは別途確認

---

### Kenneth French Industry Portfolios（12 / 30 / 49 業種）

既存 Kenneth French loader（`kenneth_french.py`）の `DATASETS` に業種別ポートフォリオを追加。EDGAR の SIC コードと組み合わせて業種コントロールに使う。

| dataset key | 業種数 | 頻度 | 列数 | カバレッジ |
|---|---|---|---|---|
| `ind12_monthly` / `ind12_daily` | 12 | 月次 / 日次 | 13 | 1926-07〜 |
| `ind30_monthly` / `ind30_daily` | 30 | 月次 / 日次 | 31 | 1926-07〜 |
| `ind49_monthly` / `ind49_daily` | 49 | 月次 / 日次 | 50 | 1926-07〜 |

各業種列は value-weighted リターン（%）。

```python
from fi_research.data.kenneth_french import fetch_dataset, load_dataset
fetch_dataset("ind49_monthly")
ind49 = load_dataset("ind49_monthly")  # date + 49 industries
```

業種ラベルと SIC コードの対応は KF Library の "Detail for 49 Industry Portfolios" PDF を参照（loader には含めない）。

---

### ICE BofA MOVE Index（金利ボラティリティ）

VIX の金利版。1ヶ月 ATM オプションの implied vol を 2Y/5Y/10Y/30Y で curve-weight した index。FRED に無いため Yahoo Finance 経由（symbol `^MOVE`）。

- 上流: `https://query2.finance.yahoo.com/v8/finance/chart/%5EMOVE`
- 出典: ICE BofA MOVE Index（methodology は ICE 所有、Yahoo Finance がディレイ配信）
- 認証: 不要（ただし Yahoo は browser-ish User-Agent を要求）
- 更新頻度: 日次（営業日次）
- カバレッジ: 2002-11-12 〜 直近（取得時点で 2026-05-22、5,817 obs）

> ⚠️ **配信元の安定性**: Yahoo の chart API は仕様変更が時々入る（v7 CSV エンドポイントは 2025 年に 401 化）。商用利用や論文 reproducibility 担保には ICE 公式または FRED 派生に移行する余地あり。

#### 使い方

```python
from fi_research.data.move import fetch_move, load_move
fetch_move()
df = load_move()  # date + close
```

#### スキーマ

| 列 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 観測日 |
| `close` | float64 | MOVE Index 終値（bp 換算済の値） |

#### 用途

- **A1**: 金利系 SHAP feature の核（クレジット系の OAS と並んで「不確実性プレミアム」を制御）
- マクロイベント（FOMC、CPI surprise）後の MOVE 反応を見る

---

### Robeco Credit Factor Returns（Houweling & van Zundert 2017 更新版）

Robeco が公開する Bloomberg Barclays U.S. Corporate (IG / HY) 上の Size / LowRisk / Value / Momentum + MultiFactor の月次超過リターン（duration-matched Treasury 控除済）。**ポスト BBW の社債ファクター研究で de-facto 公開ベンチマーク**。

- 上流: `https://www.robeco.com/files/docm/docu-robeco-data-set-factor-returns.xlsx`
- 出典: Houweling, P., & van Zundert, J. (2017), "Factor Investing in the Corporate Bond Market", *FAJ* 73(2):100-115
- 認証: 不要
- 更新頻度: 不定期（年 1-2 回）
- カバレッジ: 1994-01-31 〜 直近月（取得時点で 2025-12-31、各シート 384 obs）

> ⚠️ **ライセンス**: Robeco の "Important information" シートが厳格な再配布禁止条項を含む。**学術研究での利用と論文引用は明示的に許可されているが、raw XLSX の再配布や商用利用は禁止**。研究成果中で Houweling-van Zundert (2017) を必ず引用する。

#### 使い方

```python
from fi_research.data.robeco import fetch_robeco_credit_factors, load_robeco_credit_factors
fetch_robeco_credit_factors()  # IG + HY 両シートを parquet 化
ig = load_robeco_credit_factors("IG")
hy = load_robeco_credit_factors("HY")
```

#### スキーマ（IG / HY 共通）

| 列 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 月末日 |
| `Size` | float64 | サイズファクター超過リターン（decimal、0.001 = 10 bps） |
| `LowRisk` | float64 | 低リスク（low duration × low spread） |
| `Value` | float64 | バリュー（spread per fundamental） |
| `Momentum` | float64 | モメンタム（過去 6 ヶ月リターン） |
| `MultiFactor` | float64 | 4 ファクター等重み平均 |

#### 用途

- **A2 核**: BBW (2019/撤回 2023) の代替として Robeco 系列で社債ファクター回帰を組む
- A2 内の章 "Replication of credit factor zoo with Robeco data" で benchmark
- A1 では SHAP の対比軸として、線形ファクター回帰の予測力と非線形 ML の差分を測る

---

### CFTC Traders in Financial Futures (TFF)

CFTC の週次 Commitments of Traders レポートの financial futures 版。**Dealer / Asset Manager / Leveraged Money / Other Reportable / Non-Reportable** の 5 区分でポジション（long / short / spread）が公開される。

- 上流: `https://www.cftc.gov/files/dea/history/fut_fin_xls_{YYYY}.zip`（年単位 XLS ZIP）
- 出典: U.S. CFTC, "Commitments of Traders — Traders in Financial Futures (Futures Only)"
- 認証: 不要
- 更新頻度: 週次（火曜時点を金曜公表）
- カバレッジ: 2010-07-20 〜 直近（Dodd-Frank 以降）

#### 使い方

```python
from fi_research.data.cftc_tff import fetch_year, fetch_years, load_year, load_all
# 1 年取得
fetch_year(2025)
# 範囲取得（並列ではなく逐次、SEC と同様に sleep）
fetch_years(range(2010, 2027))
# 連結済みの長期パネル
df = load_all()  # 38,306 行 × 84 列、173 markets
```

#### 主要スキーマ（84 列のうち中核）

| 列 | 説明 |
|---|---|
| `market` | 市場名（例: "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"） |
| `report_date` | 報告対象日（火曜） |
| `Dealer_Positions_Long_All` / `_Short_All` / `_Spread_All` | ディーラー（中央 dealer banks 系） |
| `Asset_Mgr_Positions_*` | アセットマネージャー（real money） |
| `Lev_Money_Positions_*` | レバレッジマネー（ヘッジファンド） |
| `Other_Rept_*` / `NonRept_*` | その他 / 非報告 |
| `Open_Interest_All` | 総 OI |
| `Pct_of_OI_*` 系 | 各カテゴリの OI シェア（%） |
| `Traders_*` 系 | 各カテゴリのトレーダー数 |
| `Conc_*_LE_4_TDR_*` / `LE_8_TDR_*` | 上位 4/8 トレーダー集中度 |

#### 用途

- 米国債先物（2Y/5Y/10Y/30Y）でのレバレッジ・ヘッジファンドの大規模ポジション転換 → 国債利回りショック
- **A1**: dealer 系 feature と並列に投入し、SHAP の「現物 vs 先物」寄与分解
- **A2**: hedge fund クレジット先物（CDX 系は別途）の補完。Treasury futures 経由でマクロ金利ショックの dealer-side 数量効果を測定

---

### Bauer-Swanson Monetary Policy Surprises

SF Fed が公開する Bauer-Swanson (2023, *NBER Macro Annual*) の高頻度識別 MP shock データ。FOMC 発表前後の FF / Eurodollar futures 変動の第一主成分から構成され、central bank info effect を直交化した `MPS_ORTH` も含む。

- 上流: `https://www.frbsf.org/wp-content/uploads/monetary-policy-surprises-data.xlsx`
- 出典: Bauer, M. D., & Swanson, E. T. (2023). "A Reassessment of Monetary Policy Surprises and High-Frequency Identification", *NBER Macroeconomic Annual*
- 認証: 不要
- 更新頻度: 不定期（年 1 回程度）
- カバレッジ: 1988-02-04 〜 2023-12-13（FOMC 単位 361 obs / 月次 431 obs）

#### 取得シート（4 種）

| sheet slug | 内容 | obs | 期間 |
|---|---|---|---|
| `fomc_2023update` | FOMC 発表ごと（更新版） | 361 | 1988-02〜2023-12 |
| `monthly_2023update` | 月次集計（更新版） | 431 | 1988-02〜2023-12 |
| `fomc_original` | 元論文版 FOMC | 323 | 1988-02〜2019-12 |
| `monthly_original` | 元論文版月次（SVAR 用マクロ込み） | 566 | 1973-01〜2020-02 |

#### 使い方

```python
from fi_research.data.mp_shocks import fetch_mp_shocks, load_mp_shocks
fetch_mp_shocks()
# 全 4 シート parquet 化

fomc = load_mp_shocks("fomc_2023update")
monthly = load_mp_shocks("monthly_2023update")
```

#### 主要列

| 列 | 説明 |
|---|---|
| `mps` | MPS = first PC of FF1/FF2/ED1-4 around FOMC（標準的 MP shock） |
| `mps_orth` | MPS から CB info effect を直交化した残差 |
| `ff1` / `ff2` | Fed Funds 第 1/2 contract の surprise |
| `ed1`〜`ed4` | Eurodollar 1〜4 quarter ahead の surprise |
| `tnote02` / `tnote05` / `tnote10` / `tbond` | 国債利回り変化 |
| `sp500` | 株式 surprise |
| `nfp_surp` | 直前の payrolls surprise |

#### 用途

- **A1 核**: マクロ shock として `mps_orth` を回帰 / SHAP feature に投入。FOMC イベントスタディの統制変数
- **A2**: monetary policy shock 後のクレジット応答 (impulse response)。systemic risk と独立な金利ショックの identification 源

---

### OpenFIGI Mapping（ticker → FIGI）

Bloomberg の OpenFIGI v3 mapping API。SEC ticker から FIGI（Bloomberg の global identifier）への対応を引き、EDGAR fundamentals と社債データ（FIGI / ISIN ベース）を繋ぐためのインフラ。

- 上流: `https://api.openfigi.com/v3/mapping`
- 出典: OpenFIGI (Bloomberg L.P.), "Open Symbology Mapping API v3"
- 認証: 任意（無料 API key で rate-limit 大幅緩和）
  - **No key**: 5 req/min × 10 ID/req → 50 ID/min
  - **With key (`OPENFIGI_API_KEY`)**: 25 req/min × 100 ID/req → 2500 ID/min

API key は https://www.openfigi.com/api で無料発行（メアド登録）。`.env` に `OPENFIGI_API_KEY=xxx` で auto-load。

#### 使い方

```python
from fi_research.data.openfigi import (
    fetch_figi_for_tickers, fetch_figi_for_sec_tickers, load_mapping
)

# 任意 ticker
fetch_figi_for_tickers(["AAPL", "MSFT", "JPM"])

# SEC tickers の全件（key ありで ~4 分、no key で ~3.5 時間）
fetch_figi_for_sec_tickers()
# 動作確認用に limit 指定可
fetch_figi_for_sec_tickers(limit=100)

# 累積マッピング読込
df = load_mapping()
```

#### スキーマ

| 列 | 説明 |
|---|---|
| `ticker` | 入力ティッカー（大文字） |
| `figi` | FIGI（個別 share class 含む） |
| `composite_figi` | 取引所横断の composite FIGI |
| `share_class_figi` | share class identifier |
| `name` | 発行体名 |
| `exch_code` | 取引所コード（`US` 中心） |
| `security_type` / `security_type_2` | "Common Stock" / "ETP" / "ADR" 等 |
| `market_sector` | "Equity" / "Govt" / "Corp" 等 |
| `isin` | （Mapping API では基本的に空、別経路要） |
| `warning` | OpenFIGI が一致を返さなかった理由 |

> ⚠️ **ISIN は別経路**: OpenFIGI Mapping endpoint は ticker → FIGI / 基本情報のみで、ISIN は通常返さない。FIGI → ISIN 変換は別 search API か外部 DB（CFI / S&P Capital IQ など）が必要。**社債データ（TRACE / Mergent FISD）と繋ぐ際は別途実装**。

#### 取得実績（2026-05-25 時点、全件 fetch 後）

- 入力: 10,371 SEC ticker（key tier で 6.6 分）
- **FIGI ヒット: 9,190 ticker（89%）**
- Warning（一致なし）: 1,181 ticker — 主に SPAC 派生 ticker（Rights / Warrants / Units）と上場廃止銘柄
- ISIN 充足: **0**（仕様通り）
- security_type 分布: Common Stock 6,790 / ADR 673 / Equity WRT 485 / Closed-End Fund 399 / Unit 260 / REIT 199 / ETP 185 / MLP 28
- 社債発行体マッピングのコア候補: Common Stock + REIT + MLP ≒ **7,017 ticker**

#### 用途

- EDGAR `sub.cik` ↔ SEC ticker ↔ FIGI で発行体識別を完成
- 子会社 / 親会社の関係は OpenFIGI ではトラックしない → SEC EDGAR の `former` カラムや FFIEC で補完
- 社債発行体絞り込み: SEC ticker → FIGI → `market_sector == 'Corp'` の bond FIGI 集合（要追加実装）

---

### US Treasury Zero-Coupon Yield Curve（GSW）

連邦準備制度理事会のスタッフが Nelson-Siegel-Svensson モデルで毎日推定・公開しているゼロクーポンイールドカーブ。Nominal 版と TIPS 版がある。FRED の `DGS*` は日次の定数満期だが整数年でしか取れないので、任意満期の forward / par / zero rate を扱いたいときは GSW を使う。

#### Nominal（feds200628）

- 上流: `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv`
- 出典: Gürkaynak, Sack & Wright (2007) "The U.S. Treasury Yield Curve: 1961 to the Present", *JME* 54(8)
- 更新頻度: 営業日次
- カバレッジ: 1961-06-14 〜 直近営業日（2026-05-21 取得時点で 2026-05-15 まで、16,938 営業日）

#### Real / TIPS（feds200805）

- 上流: `https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv`
- 出典: Gürkaynak, Sack & Wright (2010) "The TIPS Yield Curve and Inflation Compensation", *AEJ:Macro* 2(1)
- 更新頻度: 営業日次
- カバレッジ: 1999-01-04 〜 直近営業日（2026-05-21 取得時点で 2026-05-15 まで、7,140 営業日）
- 注意: breakeven は流動性プレミアム・インフレリスクプレミアムを含むため「期待インフレ」ではない（公式注記）

#### 使い方

```python
from fi_research.data.treasury import (
    fetch_gsw_nominal, fetch_gsw_real,
    load_gsw_nominal, load_gsw_real,
)

# 取得 + 保存（force=True で強制再取得）
fetch_gsw_nominal()
fetch_gsw_real()

# DataFrame だけ欲しい（キャッシュ優先、refresh=True で再ダウンロード）
nom = load_gsw_nominal()
real = load_gsw_real()
```

#### スキーマ（共通の主要列）

| 列名 | 型 | 説明 |
|---|---|---|
| `date` | datetime64[ns] | 観測日（営業日） |
| `BETA0`〜`BETA3`, `TAU1`, `TAU2` | float64 | Nelson-Siegel-Svensson パラメータ |

Nominal 固有列（`XX` = 01〜30、満期年）:

| 接頭辞 | 説明 | 複利・換算 |
|---|---|---|
| `SVENYXX` | ゼロクーポン利回り | 連続複利 |
| `SVENPYXX` | パー利回り | 利付債等価 |
| `SVENFXX` | 瞬間フォワードレート | 連続複利 |
| `SVEN1FXX` | 1 年先フォワード | 利付債等価（`01`, `04`, `09` のみ提供） |

Real / TIPS 固有列:

| 接頭辞 | 説明 |
|---|---|
| `TIPSYXX` / `TIPSPYXX` / `TIPSFXX` / `TIPS1FXX` | ゼロ・パー・瞬間フォワード・1 年先フォワード（XX = 02〜20） |
| `TIPS5F5` | 5y-5y フォワード（中期インフレ期待のプロキシ） |
| `BKEVENXX` 系 | 名目−実質のインフレ補償。`BKEVEN5F5` は 5y-5y |

欠損は `NA`（CSV 上の文字列）と `-999.99`（初期 `TAU2` の sentinel）の両方を NaN に変換済。

#### 用途

- **A1**: 任意満期 (e.g. callable 債券の OAS 計算用 reference curve)、par yield と zero yield の差から convexity / liquidity 効果を分離
- **A2**: 期間構造ファクター（level / slope / curvature を BETA0/1/2 ベースで直接構築可能）、breakeven をマクロ feature の 1 つに加える

---

# Phase 2 拡張データソース (2026-05-26)

A2 (post-BBW 社債ファクター) の robustness + 国際比較拡張用に追加した 11 ソース。
すべて公開データ。WRDS 不要。

## ① US 拡張

### FRED-MD (McCracken-Ng 2016)
- Loader: `fi_research.data.fred_md` (`load_fred_md(stationary=False)`)
- 132 系列の月次マクロデータ + 変換コード
- **⚠️ 自動 fetch ブロック中**: Akamai/S3 が anti-bot。手動 download し
  `data/raw/fred_md/current.csv` に置く必要あり。
  URL: `https://files.stlouisfed.org/files/htdocs/fred-md/monthly/current.csv`
- 用途: A2 章 5 FGX double-selection LASSO の候補ファクターを 17 → 130+ に拡張

### He-Kelly-Manela intermediary capital ratio (2017)
- Loader: `fi_research.data.hkm_intermediary` (`load_hkm("monthly"/"quarterly"/"daily")`)
- 月次 666 行 (1970-01 ~ 2025-05), 四半期 222, 日次 6580
- 列: `intermediary_capital_ratio`, `intermediary_capital_risk_factor`, `intermediary_value_weighted_investment_return`, `intermediary_leverage_ratio_squared`
- URL: `https://zhiguohe.net/wp-content/uploads/.../He_Kelly_Manela_Factors_*.csv`
- 用途: 章 6 Fama-MacBeth の標準コントロール変数

### Liu-Wu (2021) Treasury yield curve
- Loader: `fi_research.data.liu_wu` (`load_liu_wu("monthly"/"daily")`)
- 月次 775 行 (1961-06 ~ 2025-12), 1m-360m の 360 maturity zero coupon yield
- 連続複利、年率%
- URL: Google Drive 経由（Cynthia Wu サイト）
- 用途: GSW の代替、Fama-Bliss 風 CP factor 再現

### ACM term premium (Adrian-Crump-Moench 2013)
- Loader: `fi_research.data.acm_term_premium` (`load_acm()`)
- 日次 16,199 行 (1961-06 ~ 2026-05)
- 列: `ACMY01..10`（zero yields）, `ACMTP01..10`（term premia）, `ACMRNY01..10`（risk-neutral yields）
- URL: `https://www.newyorkfed.org/medialibrary/media/research/data_indicators/ACMTermPremium.xls`
- 用途: term premium 分解の標準データ

## ② Cross-country

### ECB SDW Euro area yields + macro
- Loader: `fi_research.data.ecb` (`fetch_ecb_yield_curve()`, `fetch_ecb_macro()`)
- AAA Euro 政府債 zero coupon curve: 5549 行 × 11 maturity (2004-09 ~ 現在)
- Macro: HICP YoY, UR, IndPro (1990+)
- API: `data-api.ecb.europa.eu/service/data/`
- 用途: 章 7 cross-country、Bund vs US curve

### MoF Japan JGB yields
- Loader: `fi_research.data.mof_japan` (`load_jgb_yields()`)
- 日次 13,208 行 (1974-09 ~ 2026-04), 16 maturity (1Y-40Y)
- 利付債利回り（zero ではない）、年率%
- URL: `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv`
- 用途: 章 7 Japan extension の核

### OECD 10y bond yields (cross-country)
- Loader: `fi_research.data.oecd_bond_yields` (`load_oecd_bond_yields()`)
- 月次 878 行 × 15 countries (1953+, 各国により開始時期異なる)
- USA / JPN / DEU / GBR / FRA / ITA / ESP / CAN / AUS / KOR / EZ / CHE / SWE / NOR / NLD
- Sources via FRED `IRLTLT01XXXM156N` 系列（OECD MEI 経由）
- 用途: 章 7 cross-country curve comparison

### 日証協 公社債店頭参考値 (個別社債)
- **未実装** — daily HTML/CSV scraping 必要。2008+ で per-bond daily reference price。
  WRDS の TRACE Enhanced equivalent for Japan。実装は別タスク。

## ③ マクロ不確実性

### JLN macro/financial/real uncertainty (Jurado-Ludvigson-Ng 2015)
- Loader: `fi_research.data.jln_uncertainty` (`load_jln("macro"/"financial"/"real")`)
- 月次 786 行 × 3 horizons (h=1, 3, 12), 1960-07 ~ 2025-12
- ZIP archive, 3 XLSX
- URL: `https://www.sydneyludvigson.com/s/MacroFinanceUncertainty_*Update-*.zip`
- 用途: 章 7 robustness — uncertainty channel と regime-MP の競合検定

### EPU (Baker-Bloom-Davis 2016)
- Loader: `fi_research.data.epu` (`load_epu_us()`, `load_epu_global()`)
- US news-based: 1516 月 (1900-01 ~ 2026-04)
- All Country: 491 月 × 26 countries (Japan 含む, 1985-01 ~ 2025-11)
- URL: `policyuncertainty.com/media/{US_Policy_Uncertainty_Data,All_Country_Data}.xlsx`
- 用途: 章 7 robustness、章 8 Japan 拡張のマクロコンテクスト

## ④ AQR / JKP クロスアセット

### AQR 公開ファクター
- Loader: `fi_research.data.aqr` (`load_aqr("bab_equity"/"qmj"/"century_premia"/"tsmom")`)
- BAB Equity: 1144 月 (1930-12+), 30 列 (各国 + global aggregate)
- Quality-Minus-Junk: 825 月 (1957-07+)
- Century of Factor Premia: 1196 月 (1926-07+), 45 ファクター
- Time-Series Momentum: 481 月 (1985+)
- URL: `aqr.com/-/media/AQR/Documents/Insights/Data-Sets/*.xlsx`
- 用途: 章 7 robustness — 株式 / クロスアセットファクターと社債 α の独立性

### JKP Global Factor Data (Jensen-Kelly-Pedersen 2023)
- Loader: `fi_research.data.jkp_factors` (`fetch_jkp_factors()`)
- **⚠️ 手動 download 必要**: jkpfactors.com で free account 登録 → CSV download
  → `data/raw/jkp_factors/` に配置 → loader が parquet 化
- 153 ファクター × 93 国 (coverage 次第)
- 用途: 章 7 global factor zoo との比較

