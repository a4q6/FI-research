# データカタログ（FI-research）

> ⚙️ **このファイルは自動生成**です。手で編集せず、`docs/catalog/catalog_meta.yaml` を更新して
> `python -m fi_research.catalog build` を実行してください。インタラクティブ版は
> [`docs/catalog/data_catalog.html`](catalog/data_catalog.html)。

最終ビルド: **2026-05-27**　｜　公開・半公開データのみで構築する固定収益研究データ基盤のマスタカタログ。 取得経路・スキーマ詳細は docs/data_sources.md、隠れた制約は memory/data_source_caveats.md を参照。

**合計**: データセット 31／parquet 332／総行数 189,295,477／サイズ 4.9 GB

## マスタ表

| カテゴリ | データセット | 提供者 | 頻度 | 期間 | 行数 | サイズ | A1 | A2 |
|---|---|---|---|---|---:|---:|:--:|:--:|
| 金利・期間構造 | GSW 名目ゼロクーポンイールドカーブ (`gsw_nominal`) | FRB Board (staff) | 営業日次 | 1961-06-14→2026-05-15 | 16,938 | 10.6 MB | ◎核 | ◎核 |
| 金利・期間構造 | GSW 実質(TIPS)ゼロクーポンイールドカーブ (`gsw_real`) | FRB Board (staff) | 営業日次 | 1999-01-04→2026-05-15 | 7,140 | 6.4 MB | ○補助 | △周辺 |
| 金利・期間構造 | FRED 金利（CMT・政策金利・期間スプレッド） (`fred_rates`) | FRED (St. Louis Fed) | 日次 | 1954-07-01→2026-05-20 | 201,044 | 2.1 MB | ◎核 | ○補助 |
| 金利・期間構造 | ACM Term Premium（Adrian-Crump-Moench 2013） (`acm_term_premium`) | NY Fed | 営業日次 | 1961-06-14→2026-05-21 | 16,199 | 4.7 MB | ○補助 | △周辺 |
| 金利・期間構造 | Liu-Wu (2021) Treasury イールドカーブ (`liu_wu`) | Cynthia Wu (著者公開) | 月次 | 1961-06-30→2025-12-31 | 775 | 2.1 MB | ○補助 | △周辺 |
| クレジット | FRB Excess Bond Premium / GZ スプレッド (`frb_ebp`) | FRB Board | 月次 | 1973-01-01→2026-04-01 | 640 | 25.9 KB | ◎核 | ◎核 |
| クレジット | FRED クレジット OAS（ICE BofA）+ Moody レガシー (`fred_credit_oas`) | FRED (ICE BofA / Moody's) | 日次 | 1983-01-03→2026-05-20 | 28,997 | 317.1 KB | ○補助 | ○補助 |
| インフレ・実質金利 | FRED インフレ・実質金利（TIPS / breakeven / 物価指数） (`fred_inflation`) | FRED | 日次/月次 | 1947-01-01→2026-05-20 | 48,289 | 518.7 KB | ○補助 | △周辺 |
| マクロ・金融政策 | FRED マクロ実体（生産・労働・GDP・NBER） (`fred_macro`) | FRED | 月次/四半期/週次 | 1854-12-01→2026-05-20 | 6,873 | 104.4 KB | ◎核 | ○補助 |
| マクロ・金融政策 | Bauer-Swanson 金融政策サプライズ（MPS） (`mp_shocks`) | SF Fed (Bauer-Swanson) | FOMC / 月次 | 1988-02-01→2023-12-13 | 1,681 | 197.3 KB | ◎核 | ○補助 |
| マクロ・金融政策 | JLN マクロ/金融/実体 不確実性指数 (`jln_uncertainty`) | Sydney Ludvigson (著者公開) | 月次 | 1960-07-01→2025-12-01 | 2,358 | 93.4 KB | ○補助 | △周辺 |
| マクロ・金融政策 | EPU 経済政策不確実性指数（Baker-Bloom-Davis） (`epu`) | policyuncertainty.com | 月次 | 1900-01-31→2026-04-30 | 2,007 | 131.3 KB | △周辺 | △周辺 |
| ボラティリティ | FRED ボラティリティ（VIX / OVX） (`fred_vol`) | FRED (CBOE) | 日次 | 1990-01-02→2026-05-20 | 14,457 | 176.5 KB | ◎核 | ○補助 |
| ボラティリティ | ICE BofA MOVE Index（金利ボラティリティ） (`move`) | ICE BofA (Yahoo Finance 経由) | 営業日次 | 2002-11-12→2026-05-22 | 5,817 | 81.5 KB | ◎核 | ○補助 |
| 金融ストレス | OFR Financial Stress Index（総合+5カテゴリ+3地域） (`ofr_fsi`) | OFR (US Treasury) | 営業日次 | 2000-01-03→2026-05-20 | 6,675 | 291.9 KB | ◎核 | ◎核 |
| 金融ストレス | FRED 金融状況指数（NFCI / ANFCI / STLFSI4） (`fred_fin_conditions`) | FRED (Chicago / St. Louis Fed) | 週次 | 1971-01-08→2026-05-15 | 7,468 | 109.7 KB | ○補助 | ○補助 |
| 株式・クロスアセット | Kenneth French FF5 + Momentum (`kf_factors`) | Kenneth French Data Library | 月次/日次 | 1926-11-03→2026-03-31 | 43,847 | 562.3 KB | ○補助 | ◎核 |
| 株式・クロスアセット | Kenneth French 業種ポートフォリオ（12/30/49 業種） (`kf_industries`) | Kenneth French Data Library | 月次/日次 | 1926-07-01→2026-03-31 | 82,227 | 4.7 MB | △周辺 | ○補助 |
| 株式・クロスアセット | AQR 公開ファクター（BAB / QMJ / Century / TSMOM） (`aqr_factors`) | AQR Capital Management | 月次 | 1926-07-30→2026-03-31 | 3,646 | 775.1 KB | △周辺 | ○補助 |
| ディーラー・建玉 | NY Fed Primary Dealer Statistics (FR2004) (`ny_fed_pd`) | NY Fed Markets | 週次 | 1998-01-28→2026-05-13 | 739,119 | 2.7 MB | ○補助 | ◎核 |
| ディーラー・建玉 | CFTC Traders in Financial Futures (TFF) (`cftc_tff`) | U.S. CFTC | 週次 | 2010-07-20→2026-05-19 | 38,306 | 9.8 MB | ○補助 | ○補助 |
| ディーラー・建玉 | He-Kelly-Manela 仲介資本ファクター (`hkm_intermediary`) | Zhiguo He (著者公開) | 月次/四半期/日次 | 1970-01-01→2025-05-31 | 7,468 | 311.7 KB | ○補助 | ○補助 |
| 発行体ファンダ・識別子 | SEC EDGAR Financial Statement Data Sets (`edgar`) | SEC DERA | 四半期 | — | 186,561,181 | 4.9 GB | ○補助 | ◎核 |
| 発行体ファンダ・識別子 | SEC Company Tickers（CIK ↔ ticker） (`sec_tickers`) | SEC | 随時 | — | 10,371 | 263.9 KB | ○補助 | ◎核 |
| 発行体ファンダ・識別子 | OpenFIGI Mapping（ticker → FIGI） (`openfigi_mapping`) | OpenFIGI (Bloomberg) | 随時 | — | 10,374 | 502.6 KB | △周辺 | ◎核 |
| 社債ファクター | Robeco 社債ファクターリターン（IG + HY） (`robeco_credit_factors`) | Robeco | 月次 | 1994-01-31→2025-12-31 | 768 | 44.6 KB | ○補助 | ◎核 |
| 海外・国際比較 | 財務省 JGB 利回り（日本国債） (`mof_japan_jgb`) | 財務省 (MoF Japan) | 営業日次 | 1974-09-24→2026-04-30 | 13,208 | 668.7 KB | △周辺 | ◎核 |
| 海外・国際比較 | 日証協 公社債店頭売買参考統計値（月末スナップショット） (`jsda_monthend`) | 日本証券業協会 | 月末日次（日次原データを月末抽出） | 2020-01-31→2025-12-30 | 1,366,357 | 39.7 MB | △周辺 | ◎核 |
| 海外・国際比較 | 日証協 格付マトリクス表（月末スナップショット） (`jsda_matrix_monthend`) | 日本証券業協会 | 月末日次 | 2020-01-20→2025-12-18 | 34,560 | 113.6 KB | △周辺 | ○補助 |
| 海外・国際比較 | ECB ユーロ圏イールドカーブ + マクロ (`ecb`) | ECB | 営業日次/月次 | 1995-01-01→2026-05-22 | 5,924 | 585.2 KB | △周辺 | ○補助 |
| 海外・国際比較 | OECD 10y 国債利回り（クロスカントリー） (`oecd_bond_yields`) | OECD (FRED 経由) | 月次 | 1953-04-01→2026-05-01 | 10,763 | 260.1 KB | △周辺 | ○補助 |

## データセット詳細

### GSW 名目ゼロクーポンイールドカーブ — `gsw_nominal`

- **カテゴリ**: 金利・期間構造
- **提供者 / 頻度**: FRB Board (staff) ／ 営業日次
- **期間 / 行数 / 列数**: 1961-06-14 → 2026-05-15 ／ 16,938 ／ 100
- **loader**: `fi_research.data.treasury.load_gsw_nominal`
- **取得元**: https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv
- **引用**: Gürkaynak, Sack & Wright (2007), JME 54(8).
- **ライセンス**: public
- ⚠️ BETA3 / TAU2 は 1980-01 以降のみ。1961-1979 は 4 パラメータ NS。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日（営業日） |
| `BETA0` | double | Nelson-Siegel-Svensson パラメータ（level/slope/curvature/2nd hump） |
| `BETA1` | double | Nelson-Siegel-Svensson パラメータ（level/slope/curvature/2nd hump） |
| `BETA2` | double | Nelson-Siegel-Svensson パラメータ（level/slope/curvature/2nd hump） |
| `BETA3` | double | Nelson-Siegel-Svensson パラメータ（level/slope/curvature/2nd hump） |
| `SVEN1F01` | double | 1 年先フォワード（利付債等価, %） |
| `SVEN1F04` | double | 1 年先フォワード（利付債等価, %） |
| `SVEN1F09` | double | 1 年先フォワード（利付債等価, %） |
| `SVENF01` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF02` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF03` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF04` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF05` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF06` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF07` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF08` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF09` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF10` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF11` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF12` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF13` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF14` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF15` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF16` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF17` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF18` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF19` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF20` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF21` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF22` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF23` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF24` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF25` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF26` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF27` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF28` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF29` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENF30` | double | 瞬間フォワードレート 満期 1-30y（連続複利, %） |
| `SVENPY01` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY02` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY03` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY04` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY05` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY06` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY07` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY08` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY09` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY10` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY11` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY12` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY13` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY14` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY15` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY16` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY17` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY18` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY19` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY20` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY21` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY22` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY23` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY24` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY25` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY26` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY27` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY28` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY29` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENPY30` | double | パー利回り 満期 1-30y（利付債等価, %） |
| `SVENY01` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY02` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY03` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY04` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY05` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY06` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY07` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY08` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY09` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY10` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY11` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY12` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY13` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY14` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY15` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY16` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY17` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY18` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY19` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY20` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY21` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY22` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY23` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY24` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY25` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY26` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY27` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY28` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY29` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `SVENY30` | double | ゼロクーポン利回り 満期 1-30y（連続複利, %） |
| `TAU1` | double | NSS 減衰パラメータ 1 |
| `TAU2` | double | NSS 減衰パラメータ 2（1980- のみ） |

### GSW 実質(TIPS)ゼロクーポンイールドカーブ — `gsw_real`

- **カテゴリ**: 金利・期間構造
- **提供者 / 頻度**: FRB Board (staff) ／ 営業日次
- **期間 / 行数 / 列数**: 1999-01-04 → 2026-05-15 ／ 7,140 ／ 127
- **loader**: `fi_research.data.treasury.load_gsw_real`
- **取得元**: https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv
- **引用**: Gürkaynak, Sack & Wright (2010), AEJ:Macro 2(1).
- **ライセンス**: public
- ⚠️ breakeven は流動性・インフレリスクプレミアムを含み『期待インフレ』ではない（公式注記）。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日（営業日） |
| `BETA0` | double | NSS パラメータ |
| `BETA1` | double | NSS パラメータ |
| `BETA2` | double | NSS パラメータ |
| `BETA3` | double | NSS パラメータ |
| `BKEVEN02` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN03` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN04` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN05` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN06` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN07` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN08` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN09` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN10` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN11` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN12` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN13` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN14` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN15` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN16` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN17` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN18` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN19` | double | 名目−実質のインフレ補償（breakeven） |
| `BKEVEN20` | double | 名目−実質のインフレ補償（breakeven） |
| `TAU1` | double | NSS 減衰パラメータ 1 |
| `TAU2` | double | NSS 減衰パラメータ 2 |
| `TIPS1F04` | double | 実質 1 年先フォワード |
| `TIPS1F09` | double | 実質 1 年先フォワード |
| `TIPSF02` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF03` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF04` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF05` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF06` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF07` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF08` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF09` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF10` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF11` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF12` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF13` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF14` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF15` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF16` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF17` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF18` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF19` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSF20` | double | 実質瞬間フォワード 満期 2-20y |
| `TIPSPY02` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY03` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY04` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY05` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY06` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY07` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY08` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY09` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY10` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY11` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY12` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY13` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY14` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY15` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY16` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY17` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY18` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY19` | double | 実質パー利回り 満期 2-20y |
| `TIPSPY20` | double | 実質パー利回り 満期 2-20y |
| `TIPSY02` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY03` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY04` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY05` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY06` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY07` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY08` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY09` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY10` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY11` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY12` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY13` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY14` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY15` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY16` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY17` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY18` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY19` | double | 実質ゼロ利回り 満期 2-20y |
| `TIPSY20` | double | 実質ゼロ利回り 満期 2-20y |

### FRED 金利（CMT・政策金利・期間スプレッド） — `fred_rates`

- **カテゴリ**: 金利・期間構造
- **提供者 / 頻度**: FRED (St. Louis Fed) ／ 日次
- **期間 / 行数 / 列数**: 1954-07-01 → 2026-05-20 ／ 201,044 ／ 3
- **loader**: `fi_research.data.fred.load_panel`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: Federal Reserve Bank of St. Louis, FRED.
- **ライセンス**: public (要 API key)
- メンバー: メンバー = 各 FRED シリーズ。DGS3MO-DGS30=国債 CMT、T10Y2Y/T10Y3M=期間スプレッド、DFF/SOFR=政策金利。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `value` | double | 値（`.` は NaN 変換済） |
| `series_id` | string | FRED シリーズ ID |

### FRB Excess Bond Premium / GZ スプレッド — `frb_ebp`

- **カテゴリ**: クレジット
- **提供者 / 頻度**: FRB Board ／ 月次
- **期間 / 行数 / 列数**: 1973-01-01 → 2026-04-01 ／ 640 ／ 4
- **loader**: `fi_research.data.frb_ebp.load_ebp`
- **取得元**: https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv
- **引用**: Favara, Gilchrist, Lewis & Zakrajšek (2016) FEDS Notes / Gilchrist & Zakrajšek (2012) AER 102(4).
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 月初日付 |
| `gz_spread` | double | GZ スプレッド（社債利回り − リスクフリー） |
| `ebp` | double | Excess Bond Premium（GZ から予想デフォルト成分を控除した残差） |
| `est_prob` | double | 12ヶ月先リセッション確率の推定値 |

### FRED クレジット OAS（ICE BofA）+ Moody レガシー — `fred_credit_oas`

- **カテゴリ**: クレジット
- **提供者 / 頻度**: FRED (ICE BofA / Moody's) ／ 日次
- **期間 / 行数 / 列数**: 1983-01-03 → 2026-05-20 ／ 28,997 ／ 3
- **loader**: `fi_research.data.fred.load_panel`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: ICE BofA Indices via FRED / Moody's Seasoned Corporate.
- **ライセンス**: ICE BofA OAS は過去 5 年のみ（ライセンス制約）
- ⚠️ BAMLC* / BAMLH* は ICE ライセンスで直近 5 年だけ。長期は BAA10Y / AAA10Y で proxy。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `value` | double | OAS / スプレッド（bp 系, %） |
| `series_id` | string | BAMLC0A0CM=IG全体, BAMLC0A1CAAA..4CBBB=IG格付別, BAMLH0A0HYM2=HY全体, BAMLH0A1..3=HY格付別, BAA10Y/AAA10Y=Moody'sレガシー |

### FRED インフレ・実質金利（TIPS / breakeven / 物価指数） — `fred_inflation`

- **カテゴリ**: インフレ・実質金利
- **提供者 / 頻度**: FRED ／ 日次/月次
- **期間 / 行数 / 列数**: 1947-01-01 → 2026-05-20 ／ 48,289 ／ 3
- **loader**: `fi_research.data.fred.load_panel`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: Federal Reserve Bank of St. Louis, FRED.
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `value` | double | 値 |
| `series_id` | string | DFII5..30=TIPS CMT, T5YIE/T10YIE=breakeven, T5YIFR=5y5y forward, CPIAUCSL/PCEPI=物価指数(SA) |

### FRED マクロ実体（生産・労働・GDP・NBER） — `fred_macro`

- **カテゴリ**: マクロ・金融政策
- **提供者 / 頻度**: FRED ／ 月次/四半期/週次
- **期間 / 行数 / 列数**: 1854-12-01 → 2026-05-20 ／ 6,873 ／ 3
- **loader**: `fi_research.data.fred.load_panel`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: Federal Reserve Bank of St. Louis, FRED.
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `value` | double | 値 |
| `series_id` | string | INDPRO=鉱工業生産, UNRATE=失業率, PAYEMS=非農業雇用, GDPC1=実質GDP, USREC=NBERリセッションダミー(0/1), WALCL=FRB総資産(QE) |

### Bauer-Swanson 金融政策サプライズ（MPS） — `mp_shocks`

- **カテゴリ**: マクロ・金融政策
- **提供者 / 頻度**: SF Fed (Bauer-Swanson) ／ FOMC / 月次
- **期間 / 行数 / 列数**: 1988-02-01 → 2023-12-13 ／ 1,681 ／ 23
- **loader**: `fi_research.data.mp_shocks.load_mp_shocks`
- **取得元**: https://www.frbsf.org/wp-content/uploads/monetary-policy-surprises-data.xlsx
- **引用**: Bauer & Swanson (2023), NBER Macro Annual.
- **ライセンス**: public
- メンバー: fomc_2023update / monthly_2023update（更新版）, fomc_original / monthly_original（元論文版・SVAR用マクロ込み）。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | イベント日 / 月 |
| `ff1` | double | Fed Funds 第 1/2 contract のサプライズ |
| `ff2` | double | Fed Funds 第 1/2 contract のサプライズ |
| `ed1` | double | Eurodollar 1-4 quarter ahead サプライズ |
| `ed2` | double | Eurodollar 1-4 quarter ahead サプライズ |
| `ed3` | double | Eurodollar 1-4 quarter ahead サプライズ |
| `ed4` | double | Eurodollar 1-4 quarter ahead サプライズ |
| `sp500` | double | 株式サプライズ |
| `tnote02` | double | 国債利回り変化 |
| `tnote05` | double | 国債利回り変化 |
| `tnote10` | double | 国債利回り変化 |
| `tbond` | double | 国債利回り変化 |
| `mps` | double | MPS = FF1/FF2/ED1-4 の第一主成分（標準的 MP shock） |
| `mps_orth` | double | MPS から CB info effect を直交化した残差（推奨ショック） |
| `nfp_surp` | double | 直前の payrolls サプライズ |

### FRED ボラティリティ（VIX / OVX） — `fred_vol`

- **カテゴリ**: ボラティリティ
- **提供者 / 頻度**: FRED (CBOE) ／ 日次
- **期間 / 行数 / 列数**: 1990-01-02 → 2026-05-20 ／ 14,457 ／ 3
- **loader**: `fi_research.data.fred.load_panel`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: CBOE via FRED.
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `value` | double | インデックス値 |
| `series_id` | string | VIXCLS=株式 vol, OVXCLS=原油 vol |

### ICE BofA MOVE Index（金利ボラティリティ） — `move`

- **カテゴリ**: ボラティリティ
- **提供者 / 頻度**: ICE BofA (Yahoo Finance 経由) ／ 営業日次
- **期間 / 行数 / 列数**: 2002-11-12 → 2026-05-22 ／ 5,817 ／ 2
- **loader**: `fi_research.data.move.load_move`
- **取得元**: https://query2.finance.yahoo.com/v8/finance/chart/%5EMOVE
- **引用**: ICE BofA MOVE Index.
- **ライセンス**: Yahoo 配信。論文 reproducibility では ICE 公式へ移行推奨。
- ⚠️ Yahoo chart API は仕様変更が時々入る（v7 CSV は 2025 年に 401 化）。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `close` | double | MOVE Index 終値（金利 implied vol, bp 換算） |

### OFR Financial Stress Index（総合+5カテゴリ+3地域） — `ofr_fsi`

- **カテゴリ**: 金融ストレス
- **提供者 / 頻度**: OFR (US Treasury) ／ 営業日次
- **期間 / 行数 / 列数**: 2000-01-03 → 2026-05-20 ／ 6,675 ／ 10
- **loader**: `fi_research.data.ofr_fsi.load_ofr_fsi`
- **取得元**: https://www.financialresearch.gov/financial-stress-index/data/fsi.csv
- **引用**: Monin (2019), 'The OFR Financial Stress Index', Risks 7(1):25.
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日（営業日） |
| `ofr_fsi` | double | 総合指数（z-score, ~0 が長期平均, 正で stress 上昇） |
| `credit` | double | クレジット系サブインデックス（OAS, CDS 等） |
| `equity_valuation` | double | 株式バリュエーション（P/E, ERP 等） |
| `safe_assets` | double | 安全資産需要（実質金利, term premium 等） |
| `funding` | double | 短期ファンディング（LIBOR-OIS, TED 等） |
| `volatility` | double | 暗黙ボラ（VIX, MOVE 等） |
| `united_states` | double | 地域別寄与 |
| `other_advanced_economies` | double | 地域別寄与 |
| `emerging_markets` | double | 地域別寄与 |

### FRED 金融状況指数（NFCI / ANFCI / STLFSI4） — `fred_fin_conditions`

- **カテゴリ**: 金融ストレス
- **提供者 / 頻度**: FRED (Chicago / St. Louis Fed) ／ 週次
- **期間 / 行数 / 列数**: 1971-01-08 → 2026-05-15 ／ 7,468 ／ 3
- **loader**: `fi_research.data.fred.load_panel`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: Chicago Fed (NFCI/ANFCI), St. Louis Fed (STLFSI4).
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `value` | double | 指数値 |
| `series_id` | string | NFCI=Chicago金融状況, ANFCI=調整版, STLFSI4=St.Louis金融ストレス |

### Kenneth French FF5 + Momentum — `kf_factors`

- **カテゴリ**: 株式・クロスアセット
- **提供者 / 頻度**: Kenneth French Data Library ／ 月次/日次
- **期間 / 行数 / 列数**: 1926-11-03 → 2026-03-31 ／ 43,847 ／ 7
- **loader**: `fi_research.data.kenneth_french.load_dataset`
- **取得元**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/
- **引用**: Fama & French (1993, 2015); Carhart (1997).
- **ライセンス**: public
- メンバー: 値はパーセント単位（-0.39 = -0.39%）。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 月初日付 / 取引日 |
| `Mkt-RF` | double | 市場超過リターン（%） |
| `SMB` | double | Size / Value / Profitability / Investment（%） |
| `HML` | double | Size / Value / Profitability / Investment（%） |
| `RMW` | double | Size / Value / Profitability / Investment（%） |
| `CMA` | double | Size / Value / Profitability / Investment（%） |
| `RF` | double | 1ヶ月 T-bill（%, FF5 データセット） |

### Kenneth French 業種ポートフォリオ（12/30/49 業種） — `kf_industries`

- **カテゴリ**: 株式・クロスアセット
- **提供者 / 頻度**: Kenneth French Data Library ／ 月次/日次
- **期間 / 行数 / 列数**: 1926-07-01 → 2026-03-31 ／ 82,227 ／ 13
- **loader**: `fi_research.data.kenneth_french.load_dataset`
- **取得元**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/
- **引用**: Kenneth R. French Data Library.
- **ライセンス**: public
- メンバー: EDGAR の SIC コードと組み合わせて業種コントロール。ラベル対応は KF の Detail PDF 参照。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 月初日付 / 取引日 |
| `NoDur` | double | 各業種の value-weighted リターン（%） |
| `Durbl` | double | 各業種の value-weighted リターン（%） |
| `Manuf` | double | 各業種の value-weighted リターン（%） |
| `Enrgy` | double | 各業種の value-weighted リターン（%） |
| `Chems` | double | 各業種の value-weighted リターン（%） |
| `BusEq` | double | 各業種の value-weighted リターン（%） |
| `Telcm` | double | 各業種の value-weighted リターン（%） |
| `Utils` | double | 各業種の value-weighted リターン（%） |
| `Shops` | double | 各業種の value-weighted リターン（%） |
| `Hlth` | double | 各業種の value-weighted リターン（%） |
| `Money` | double | 各業種の value-weighted リターン（%） |
| `Other` | double | 各業種の value-weighted リターン（%） |

### AQR 公開ファクター（BAB / QMJ / Century / TSMOM） — `aqr_factors`

- **カテゴリ**: 株式・クロスアセット
- **提供者 / 頻度**: AQR Capital Management ／ 月次
- **期間 / 行数 / 列数**: 1926-07-30 → 2026-03-31 ／ 3,646 ／ 30
- **loader**: `fi_research.data.aqr.load_aqr`
- **取得元**: https://www.aqr.com/Insights/Datasets
- **引用**: Frazzini & Pedersen (2014); Asness, Frazzini & Pedersen (2019).
- **ライセンス**: public (研究利用)
- メンバー: BAB Equity(各国+global), Quality-Minus-Junk, Century of Factor Premia(45 factor), Time-Series Momentum。章7 robustness で社債 α の独立性検定に。

### NY Fed Primary Dealer Statistics (FR2004) — `ny_fed_pd`

- **カテゴリ**: ディーラー・建玉
- **提供者 / 頻度**: NY Fed Markets ／ 週次
- **期間 / 行数 / 列数**: 1998-01-28 → 2026-05-13 ／ 739,119 ／ 3
- **loader**: `fi_research.data.ny_fed_pd.load_pd_timeseries`
- **取得元**: https://markets.newyorkfed.org/api/pd/
- **引用**: FRBNY, Primary Dealer Statistics (FR2004).
- **ライセンス**: public (User-Agent 必須)
- ⚠️ catalog は現行 SBN2024 のみ。旧 seriesbreak の 751 keyid は description 欠落。
- メンバー: timeseries=本体(long), catalog=keyid説明, asofs=日付→seriesbreak。3 テーブルで構成。

| カラム | 型 | 定義 |
|---|---|---|
| `as_of_date` | timestamp[ns] | 報告対象日（通常水曜） |
| `keyid` | string | シリーズ ID（PDPOS*=net position, PDTRAN*=取引高, PDFTR*=repo, PDFTD*=fails） |
| `value_millions` | double | 金額（百万ドル, ポジション系は long-short） |

### CFTC Traders in Financial Futures (TFF) — `cftc_tff`

- **カテゴリ**: ディーラー・建玉
- **提供者 / 頻度**: U.S. CFTC ／ 週次
- **期間 / 行数 / 列数**: 2010-07-20 → 2026-05-19 ／ 38,306 ／ 84
- **loader**: `fi_research.data.cftc_tff.load_all`
- **取得元**: https://www.cftc.gov/files/dea/history/
- **引用**: CFTC, Commitments of Traders — Traders in Financial Futures.
- **ライセンス**: public
- メンバー: 年次 XLS shard（2010-）。cftc_tff.parquet は全結合済。5 区分でポジション公開。

| カラム | 型 | 定義 |
|---|---|---|
| `market` | string | 市場名（例 10-YEAR U.S. TREASURY NOTES） |
| `report_date` | timestamp[ns] | 報告対象日（火曜） |
| `Open_Interest_All` | int64 | 総建玉 |
| `Dealer_Positions_Long_All` | int64 | ディーラー建玉 |
| `Dealer_Positions_Short_All` | int64 | ディーラー建玉 |
| `Dealer_Positions_Spread_All` | int64 | ディーラー建玉 |
| `Asset_Mgr_Positions_Long_All` | int64 | アセットマネージャー（real money） |
| `Asset_Mgr_Positions_Short_All` | int64 | アセットマネージャー（real money） |
| `Asset_Mgr_Positions_Spread_All` | int64 | アセットマネージャー（real money） |
| `Lev_Money_Positions_Long_All` | int64 | レバレッジマネー（ヘッジファンド） |
| `Lev_Money_Positions_Short_All` | int64 | レバレッジマネー（ヘッジファンド） |
| `Lev_Money_Positions_Spread_All` | int64 | レバレッジマネー（ヘッジファンド） |
| `Other_Rept_Positions_Long_All` | int64 | その他 / 非報告 |
| `Other_Rept_Positions_Short_All` | int64 | その他 / 非報告 |
| `Other_Rept_Positions_Spread_All` | int64 | その他 / 非報告 |
| `NonRept_Positions_Long_All` | int64 | その他 / 非報告 |
| `NonRept_Positions_Short_All` | int64 | その他 / 非報告 |

### SEC EDGAR Financial Statement Data Sets — `edgar`

- **カテゴリ**: 発行体ファンダ・識別子
- **提供者 / 頻度**: SEC DERA ／ 四半期
- **期間 / 行数 / 列数**: — →  ／ 186,561,181 ／ 36
- **loader**: `fi_research.data.edgar.load_concat`
- **取得元**: https://www.sec.gov/dera/data/financial-statement-data-sets
- **引用**: U.S. SEC, Financial Statement Data Sets.
- **ライセンス**: public (User-Agent 必須)
- ⚠️ num.txt は 100MB+/quarter。69 quarters 全結合は数 GB。必要四半期だけ filter 推奨。
- メンバー: 69 四半期 × {sub, num, tag} の 3 テーブル。sub=filing メタ, num=XBRL 数値ファクト, tag=タグ辞書。
- 🔗 `sec_tickers` (cik ↔ cik)

| カラム | 型 | 定義 |
|---|---|---|
| `adsh` | string | accession number（filing 一意 ID, num/tag と join） |
| `cik` | int64 | 企業 CIK（sec_tickers と join） |
| `name` | string | 企業名 |
| `sic` | int64 | SIC code（業種, 6000-6999=金融） |
| `form` | string | 10-K / 10-Q / 8-K 等 |
| `period` | timestamp[ns] | 報告対象期間末日 |
| `fy` | int64 | 会計年度 / 期 |
| `fp` | string | 会計年度 / 期 |
| `filed` | timestamp[ns] | SEC 提出日 |

### SEC Company Tickers（CIK ↔ ticker） — `sec_tickers`

- **カテゴリ**: 発行体ファンダ・識別子
- **提供者 / 頻度**: SEC ／ 随時
- **期間 / 行数 / 列数**: — →  ／ 10,371 ／ 3
- **loader**: `fi_research.data.sec_tickers.load_tickers`
- **取得元**: https://www.sec.gov/files/company_tickers.json
- **引用**: U.S. SEC.
- **ライセンス**: public (User-Agent 必須)
- 🔗 `edgar` (cik ↔ cik)
- 🔗 `openfigi_mapping` (ticker ↔ ticker)

| カラム | 型 | 定義 |
|---|---|---|
| `cik` | int64 | SEC CIK（EDGAR sub.cik と共通キー） |
| `ticker` | string | 米国ティッカー（大文字） |
| `name` | string | 企業名 |

### OpenFIGI Mapping（ticker → FIGI） — `openfigi_mapping`

- **カテゴリ**: 発行体ファンダ・識別子
- **提供者 / 頻度**: OpenFIGI (Bloomberg) ／ 随時
- **期間 / 行数 / 列数**: — →  ／ 10,374 ／ 11
- **loader**: `fi_research.data.openfigi.load_mapping`
- **取得元**: https://api.openfigi.com/v3/mapping
- **引用**: OpenFIGI (Bloomberg L.P.), Open Symbology Mapping API v3.
- **ライセンス**: public (無料 key で rate-limit 緩和)
- ⚠️ Mapping endpoint は ISIN を返さない（仕様）。社債データと繋ぐには別経路（WRDS / search API）が必要。
- 🔗 `sec_tickers` (ticker ↔ ticker)

| カラム | 型 | 定義 |
|---|---|---|
| `ticker` | string | 入力ティッカー（sec_tickers と join） |
| `figi` | string | FIGI（個別 share class） |
| `composite_figi` | string | 取引所横断 composite FIGI |
| `share_class_figi` | string | share class identifier |
| `name` | string | 発行体名 |
| `exch_code` | string | 取引所コード |
| `security_type` | string | 証券種別 |
| `security_type_2` | string | 証券種別 |
| `market_sector` | string | Equity / Govt / Corp 等 |
| `isin` | null | ISIN（仕様上ほぼ空） |
| `warning` | string | 一致が返らなかった理由 |

### Robeco 社債ファクターリターン（IG + HY） — `robeco_credit_factors`

- **カテゴリ**: 社債ファクター
- **提供者 / 頻度**: Robeco ／ 月次
- **期間 / 行数 / 列数**: 1994-01-31 → 2025-12-31 ／ 768 ／ 6
- **loader**: `fi_research.data.robeco.load_robeco_credit_factors`
- **取得元**: https://www.robeco.com/
- **引用**: Houweling & van Zundert (2017), FAJ 73(2):100-115.
- **ライセンス**: 再配布禁止。学術利用・論文引用のみ可。raw XLSX を共有しない。
- ⚠️ duration-matched Treasury 控除済の超過リターン。クレジットβを含むため vol は論文比で高め。
- メンバー: IG / HY の 2 シート（各 384 ヶ月, 1994-2025）。A2 post-BBW の de-facto 公開ベンチマーク。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 月末日 |
| `Size` | double | サイズファクター超過リターン（decimal, 0.001=10bp） |
| `LowRisk` | double | 低リスク（low duration × low spread） |
| `Value` | double | バリュー（spread per fundamental） |
| `Momentum` | double | モメンタム（過去 6 ヶ月リターン） |
| `MultiFactor` | double | 4 ファクター等重み平均 |

### 財務省 JGB 利回り（日本国債） — `mof_japan_jgb`

- **カテゴリ**: 海外・国際比較
- **提供者 / 頻度**: 財務省 (MoF Japan) ／ 営業日次
- **期間 / 行数 / 列数**: 1974-09-24 → 2026-04-30 ／ 13,208 ／ 16
- **loader**: `fi_research.data.mof_japan.load_jgb_yields`
- **取得元**: https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv
- **引用**: Ministry of Finance Japan, JGB Interest Rate.
- **ライセンス**: public
- メンバー: A2『日本適用が新規性』の核データ（16 満期, 1974-）。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `y1y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y2y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y3y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y4y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y5y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y6y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y7y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y8y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y9y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y10y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y15y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y20y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y25y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y30y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |
| `y40y` | double | 各満期(1Y-40Y)の利付債利回り（zero ではない, 年率%） |

### 日証協 公社債店頭売買参考統計値（月末スナップショット） — `jsda_monthend`

- **カテゴリ**: 海外・国際比較
- **提供者 / 頻度**: 日本証券業協会 ／ 月末日次（日次原データを月末抽出）
- **期間 / 行数 / 列数**: 2020-01-31 → 2025-12-30 ／ 1,366,357 ／ 29
- **loader**: `fi_research.data.jsda.load_monthend`
- **取得元**: https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/{YYYY}/S{YYMMDD}.csv
- **引用**: 日本証券業協会 (JSDA), 公社債店頭売買参考統計値。
- **ライセンス**: public（再配布は出典明記要）
- ⚠️ CSV は cp932 (Shift-JIS) エンコーディング、ヘッダー無し 29 列。
- ⚠️ API 無し、daily CSV を直接スクレイピング。サーバ rate-limit (3+ sec sleep 必要)。
- ⚠️ S{YYMMDD}.csv 形式の URL は ~2019 年以降確認、それ以前は別形式の可能性（archive ページ参照）。
- ⚠️ 個別社債識別子 (col `code`) は 9 桁、ISIN/CUSIP 互換ではない JSDA 独自コード。
- メンバー: A2 横断面アルファ検定用の TRACE 等価データ（~12,000 銘柄 × 月末）。
- 🔗 `mof_japan_jgb` (date ↔ date)
- 🔗 `jsda_matrix_monthend` (date ↔ date)

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `issue_type` | string | 銘柄種別（01-99 コード, 02-04=国債, 13=事業債/社債, 12=金融債, 15=転換社債, 17=円建外債 等） |
| `code` | string | 銘柄コード（JSDA 独自 9 桁） |
| `name` | string | 銘柄名（cp932 decode 済 UTF-8） |
| `due_date` | timestamp[ns] | 償還期日 |
| `coupon` | double | 利率（%） |
| `avg_compound_yield` | double | 平均値（複利/単利/単価/前日比） |
| `avg_price` | double | 平均値（複利/単利/単価/前日比） |
| `avg_price_change` | double | 平均値（複利/単利/単価/前日比） |
| `avg_simple_yield` | double | 平均値（複利/単利/単価/前日比） |
| `high_price` | double | 最高値・最低値・中央値の各指標 |
| `high_simple_yield` | double | 最高値・最低値・中央値の各指標 |
| `low_price` | double | 最高値・最低値・中央値の各指標 |
| `low_simple_yield` | double | 最高値・最低値・中央値の各指標 |
| `invalid_flag` | string | チェックフラグ |
| `n_reporters` | int64 | 報告社数 |
| `high_compound_yield` | double | 最高値・最低値・中央値の各指標 |
| `high_price_change` | double | 最高値・最低値・中央値の各指標 |
| `low_compound_yield` | double | 最高値・最低値・中央値の各指標 |
| `low_price_change` | double | 最高値・最低値・中央値の各指標 |
| `median_compound_yield` | double | 最高値・最低値・中央値の各指標 |
| `median_simple_yield` | double | 最高値・最低値・中央値の各指標 |
| `median_price` | double | 最高値・最低値・中央値の各指標 |
| `median_price_change` | double | 最高値・最低値・中央値の各指標 |

### 日証協 格付マトリクス表（月末スナップショット） — `jsda_matrix_monthend`

- **カテゴリ**: 海外・国際比較
- **提供者 / 頻度**: 日本証券業協会 ／ 月末日次
- **期間 / 行数 / 列数**: 2020-01-20 → 2025-12-18 ／ 34,560 ／ 9
- **loader**: `fi_research.data.jsda.load_monthend(kind='R')`
- **取得元**: https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/files/{YYYY}/R{YYMMDD}.csv
- **引用**: 日本証券業協会 (JSDA), 格付マトリクス表。
- **ライセンス**: public（再配布は出典明記要）
- ⚠️ 格付 × 残存期間バケットの代表複利利回り集約表。1 月末あたり 80 行（rating agency × maturity bucket）。
- ⚠️ CSV は cp932 (Shift-JIS) エンコーディング、ヘッダー無し 39 列。loader が long format に整形。
- ⚠️ Moody's は小文字格付 (Aaa, Aa, A, Baa, Ba) を返す。他社 (R&I, JCR, S&P) は大文字 (AAA, AA, A, BBB, BB, B)。
- メンバー: S-file の格付別ベンチマーク曲線として併用（個別社債リターン分解 / α テストの discount curve）。
- 🔗 `jsda_monthend` (date ↔ date)

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `rating_agency_code` | int64 | 格付機関コード (1=R&I, 3=JCR, 4=Moody's, 5=S&P) |
| `rating_agency` | string | 格付機関名 (cp932 → UTF-8 decode 済) |
| `maturity_year` | int64 | 残存期間バケット (1-20 年) |
| `rating` | string | 格付ラベル (AAA/AA/A/BBB/BB/B または Moody's の Aaa/Aa/A/Baa/Ba) |
| `mean_yield` | double | 代表複利利回り 平均（%） |
| `std_yield` | double | 同 標準偏差 |
| `n_bonds` | double | バケット内銘柄数 |
| `face_value_oku` | double | バケット内総額面（億円） |

### ECB ユーロ圏イールドカーブ + マクロ — `ecb`

- **カテゴリ**: 海外・国際比較
- **提供者 / 頻度**: ECB ／ 営業日次/月次
- **期間 / 行数 / 列数**: 1995-01-01 → 2026-05-22 ／ 5,924 ／ 11
- **loader**: `fi_research.data.ecb.fetch_ecb_yield_curve`
- **取得元**: https://data-api.ecb.europa.eu/service/data/
- **引用**: European Central Bank, Statistical Data Warehouse.
- **ライセンス**: public
- メンバー: AAA ユーロ政府債 zero curve（11 満期, 2004-）+ HICP/UR/IndPro。章7 cross-country。

### OECD 10y 国債利回り（クロスカントリー） — `oecd_bond_yields`

- **カテゴリ**: 海外・国際比較
- **提供者 / 頻度**: OECD (FRED 経由) ／ 月次
- **期間 / 行数 / 列数**: 1953-04-01 → 2026-05-01 ／ 10,763 ／ 16
- **loader**: `fi_research.data.oecd_bond_yields.load_oecd_bond_yields`
- **取得元**: https://fred.stlouisfed.org/
- **引用**: OECD Main Economic Indicators via FRED (IRLTLT01*).
- **ライセンス**: public
- メンバー: 15 ヶ国の 10y 利回り（USA/JPN/DEU/GBR/FRA/ITA/ESP/CAN/AUS/KOR/EZ/CHE/SWE/NOR/NLD）。fred_IRLTLT01*=国別生系列。

### ACM Term Premium（Adrian-Crump-Moench 2013） — `acm_term_premium`

- **カテゴリ**: 金利・期間構造
- **提供者 / 頻度**: NY Fed ／ 営業日次
- **期間 / 行数 / 列数**: 1961-06-14 → 2026-05-21 ／ 16,199 ／ 31
- **loader**: `fi_research.data.acm_term_premium.load_acm`
- **取得元**: https://www.newyorkfed.org/research/data_indicators/term-premia-tabs
- **引用**: Adrian, Crump & Moench (2013), JFE 110(1).
- **ライセンス**: public

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `ACMY01` | double | モデル zero yield（満期 1-10y） |
| `ACMY02` | double | モデル zero yield（満期 1-10y） |
| `ACMY03` | double | モデル zero yield（満期 1-10y） |
| `ACMY04` | double | モデル zero yield（満期 1-10y） |
| `ACMY05` | double | モデル zero yield（満期 1-10y） |
| `ACMY06` | double | モデル zero yield（満期 1-10y） |
| `ACMY07` | double | モデル zero yield（満期 1-10y） |
| `ACMY08` | double | モデル zero yield（満期 1-10y） |
| `ACMY09` | double | モデル zero yield（満期 1-10y） |
| `ACMY10` | double | モデル zero yield（満期 1-10y） |
| `ACMTP01` | double | term premium（満期 1-10y） |
| `ACMTP02` | double | term premium（満期 1-10y） |
| `ACMTP03` | double | term premium（満期 1-10y） |
| `ACMTP04` | double | term premium（満期 1-10y） |
| `ACMTP05` | double | term premium（満期 1-10y） |
| `ACMTP06` | double | term premium（満期 1-10y） |
| `ACMTP07` | double | term premium（満期 1-10y） |
| `ACMTP08` | double | term premium（満期 1-10y） |
| `ACMTP09` | double | term premium（満期 1-10y） |
| `ACMTP10` | double | term premium（満期 1-10y） |
| `ACMRNY01` | double | risk-neutral yield |
| `ACMRNY02` | double | risk-neutral yield |
| `ACMRNY03` | double | risk-neutral yield |
| `ACMRNY04` | double | risk-neutral yield |
| `ACMRNY05` | double | risk-neutral yield |
| `ACMRNY06` | double | risk-neutral yield |
| `ACMRNY07` | double | risk-neutral yield |
| `ACMRNY08` | double | risk-neutral yield |
| `ACMRNY09` | double | risk-neutral yield |
| `ACMRNY10` | double | risk-neutral yield |

### Liu-Wu (2021) Treasury イールドカーブ — `liu_wu`

- **カテゴリ**: 金利・期間構造
- **提供者 / 頻度**: Cynthia Wu (著者公開) ／ 月次
- **期間 / 行数 / 列数**: 1961-06-30 → 2025-12-31 ／ 775 ／ 361
- **loader**: `fi_research.data.liu_wu.load_liu_wu`
- **取得元**: https://sites.google.com/view/jingcynthiawu/yield-data
- **引用**: Liu & Wu (2021), JFE 142(3).
- **ライセンス**: public
- メンバー: 1m-360m の 360 満期 zero（連続複利, 年率%）。GSW 代替 / Fama-Bliss 風 CP factor 再現用。

### He-Kelly-Manela 仲介資本ファクター — `hkm_intermediary`

- **カテゴリ**: ディーラー・建玉
- **提供者 / 頻度**: Zhiguo He (著者公開) ／ 月次/四半期/日次
- **期間 / 行数 / 列数**: 1970-01-01 → 2025-05-31 ／ 7,468 ／ 5
- **loader**: `fi_research.data.hkm_intermediary.load_hkm`
- **取得元**: https://zhiguohe.net/data-and-empirical-patterns/
- **引用**: He, Kelly & Manela (2017), JFE 126(1).
- **ライセンス**: public
- メンバー: monthly / quarterly / daily。Fama-MacBeth の標準コントロール。NY Fed PD と接続。

| カラム | 型 | 定義 |
|---|---|---|
| `date` | timestamp[ns] | 観測日 |
| `intermediary_capital_ratio` | double | 仲介資本比率 |
| `intermediary_capital_risk_factor` | double | 資本リスクファクター |
| `intermediary_value_weighted_investment_return` | double | VW 投資リターン |
| `intermediary_leverage_ratio_squared` | double | レバレッジ比率の二乗 |

### JLN マクロ/金融/実体 不確実性指数 — `jln_uncertainty`

- **カテゴリ**: マクロ・金融政策
- **提供者 / 頻度**: Sydney Ludvigson (著者公開) ／ 月次
- **期間 / 行数 / 列数**: 1960-07-01 → 2025-12-01 ／ 2,358 ／ 4
- **loader**: `fi_research.data.jln_uncertainty.load_jln`
- **取得元**: https://www.sydneyludvigson.com/data-and-appendixes
- **引用**: Jurado, Ludvigson & Ng (2015), AER 105(3).
- **ライセンス**: public
- メンバー: macro / financial / real × 3 horizon (h=1,3,12), 1960-。uncertainty channel の robustness。

### EPU 経済政策不確実性指数（Baker-Bloom-Davis） — `epu`

- **カテゴリ**: マクロ・金融政策
- **提供者 / 頻度**: policyuncertainty.com ／ 月次
- **期間 / 行数 / 列数**: 1900-01-31 → 2026-04-30 ／ 2,007 ／ 2
- **loader**: `fi_research.data.epu.load_epu_us`
- **取得元**: https://www.policyuncertainty.com/
- **引用**: Baker, Bloom & Davis (2016), QJE 131(4).
- **ライセンス**: public
- メンバー: US news-based(1900-) + All Country(26ヶ国, 日本含む, 1985-)。章7/8 のマクロコンテクスト。

## 未取得データ（取得可 / 取得困難）

| 優先 | データ | 提供者 | 状態 | テーマ | メモ |
|---|---|---|---|:--:|---|
| ★★ | CDX IG / HY index spreads | Markit | 取得可 | A2 | OAS と独立したクレジット信号 |
| ★★ | CIK ↔ ISIN マッピング | OpenFIGI Search / 別 DB | 取得可 | A2 | Mapping API は ISIN を返さない。社債リターンとの橋に別経路が必要 |
| ★ | FFIEC bank Call Reports (031/041) | FFIEC CDR | 取得可 | A2 | 銀行発行体に絞った社債分析時 |
| ★ | MOVE 公式ソース移行 (ICE/Cboe) | ICE | 取得可 | A1 | 現在 Yahoo 経由。論文 reproducibility で公式へ |
| ★ | JKP Global Factor Data | jkpfactors.com | 取得可(手動DL) | A2 | 153 factor × 93 国。free account 登録要 |
| ★ | FRED-MD 132 系列 | McCracken-Ng | 取得可(手動DL) | A1 | Akamai anti-bot で自動 fetch ブロック。FGX 候補ファクター拡張用 |
| ★★ | TRACE Standard / Enhanced | FINRA / WRDS | 取得困難 | A2 | 個別約定。WRDS（大学アカウント）待ち。A2 横断回帰・BBW 直接再現に必須 |
| ★★ | Mergent FISD | WRDS | 取得困難 | A2 | 社債マスター（発行体/発行条件/格付履歴） |
| ★ | 格付け別 OAS 長期 (1996-2023) | ICE/BofA | 取得困難 | A2 | 商用ライセンス。BAA10Y/AAA10Y で proxy |
| ★★ | 日証協 公社債店頭参考値 | 日証協 | 取得可(scraping) | A2 | 日本の per-bond daily 参考価格。A2 日本拡張の TRACE 相当 |

## 未整備 / ドリフト

- [cols] 'gsw_real': 42/127 columns undocumented
- [cols] 'mp_shocks': 8/23 columns undocumented
- [cols] 'aqr_factors': no column definitions yet (30 columns)
- [cols] 'cftc_tff': 67/84 columns undocumented
- [cols] 'edgar': 27/36 columns undocumented
- [cols] 'jsda_monthend': 5/29 columns undocumented
- [cols] 'ecb': no column definitions yet (11 columns)
- [cols] 'oecd_bond_yields': no column definitions yet (16 columns)
- [cols] 'liu_wu': no column definitions yet (361 columns)
- [cols] 'jln_uncertainty': no column definitions yet (4 columns)
- [cols] 'epu': no column definitions yet (2 columns)
- [orphan] 1 parquet not in any dataset: cftc_tff.parquet

## 関連ドキュメント

- [`data_sources.md`](data_sources.md) — 各 loader の取得・スキーマ詳細
- [`catalog/catalog_meta.yaml`](catalog/catalog_meta.yaml) — 知識層（編集する真実源）
- [`catalog/data_catalog.html`](catalog/data_catalog.html) — インタラクティブ版
