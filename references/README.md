# references/ — 先行研究マスターリスト

このディレクトリは **先行研究のピュアなアーカイブ**。新研究（`projects/`）とは独立。

## 運用ルール
- 1 論文 1 PDF を `references/<first_author>_<year>_<keyword>.pdf` で保存
- すべての論文（PDF 有無に関わらず）を下記マスターリストに登録
- APA 簡略形式の citation + URL/DOI + 手元 PDF の有無 + 1 行メモ
- 詳細な引用文脈は `docs/handover.md` や notebook 側に書く（このファイルはあくまで index）
- 再配布禁止のもの（例: Robeco の XLSX）は PDF を入れない — citation と URL のみ
- **PDF は合法的に無料公開されている版のみ**（NBER / SSRN / 著者サイト / Fed working paper / オープンアクセス）。出版社の有料版・ペイウォール回避は使わない。掲載誌が canonical な場合でも実体は working paper 版のことがある

凡例: **PDF ✓** = ローカル保存済 / **−** = リンクのみ（無料版なし or 未取得）

最終取得: **2026-05-26**　/　28 件中 **27 件 PDF 取得済**（未取得は #10 Campisi のみ）

---

## 1. A2 コア — 社債ファクター・post-BBW

| # | Citation | Outlet | PDF | URL/DOI |
|---|---|---|---|---|
| 1 | Houweling, P., & van Zundert, J. (2017). Factor Investing in the Corporate Bond Market. | *FAJ* 73(2): 100-115 | **✓** `houweling_vanzundert_2017_factor_investing.pdf` | https://doi.org/10.2469/faj.v73.n2.1 |
| 2 | Bai, J., Bali, T. G., & Wen, Q. (2019). Common risk factors in the cross-section of corporate bond returns. | *JFE* 131(3): 619-642 ⚠️ **2023 撤回** | **✓** `bai_bali_wen_2019_common_risk_factors.pdf` | https://doi.org/10.1016/j.jfineco.2018.08.002 |
| 3 | van Binsbergen, J. H., & Schwert, M. (2021). Reexamining corporate bond risk premia. | working paper (Wharton Rodney White WP) | **✓** `vanbinsbergen_schwert_2021_reexamining.pdf` | https://rodneywhitecenter.wharton.upenn.edu/ |
| 4 | Feng, G., Giglio, S., & Xiu, D. (2020). Taming the Factor Zoo: A Test of New Factors. | *JF* 75(3): 1327-1370 | **✓** `feng_giglio_xiu_2020_taming_factor_zoo.pdf` | https://doi.org/10.1111/jofi.12883 |
| 5 | Kozak, S., Nagel, S., & Santosh, S. (2020). Shrinking the Cross-Section. | *JFE* 135(2): 271-292 | **✓** `kozak_nagel_santosh_2020_shrinking.pdf` | https://doi.org/10.1016/j.jfineco.2019.06.008 |
| 6 | Dick-Nielsen, J., Feldhütter, P., & Lando, D. (2012). Corporate bond liquidity before and after the onset of the subprime crisis. | *JFE* 103(3): 471-492 | **✓** `dicknielsen_feldhutter_lando_2012_bond_liquidity.pdf` | https://doi.org/10.1016/j.jfineco.2011.10.009 |
| 7 | Israel, R., Palhares, D., & Richardson, S. A. (2018). Common factors in corporate bond returns. | *Journal of Investment Management* 16(2) | **✓** `israel_palhares_richardson_2018_common_factors.pdf` | https://www.aqr.com/ |
| 8 | Jensen, T. I., Kelly, B. T., & Pedersen, L. H. (2023). Is There a Replication Crisis in Finance? | *JF* 78(5): 2465-2518 (Global Factor Data Repository) | **✓** `jensen_kelly_pedersen_2023_replication_crisis.pdf` | https://doi.org/10.1111/jofi.13249 |
| 9 | Asvanunt, A., & Richardson, S. (2017). The Credit Risk Premium. | *Journal of Fixed Income* 26(3) | **✓** `asvanunt_richardson_2017_credit_risk_premium.pdf` | https://www.aqr.com/ |

## 2. A1 補助 — SHAP × 機械学習 × 債券アトリビューション

| # | Citation | Outlet | PDF | URL/DOI |
|---|---|---|---|---|
| 10 | Campisi, S. (2000). Primer on Fixed Income Performance Attribution. | *Journal of Performance Measurement* 4(4) | − | — （有料誌、無料版なし） |
| 11 | Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning. | *RFS* 33(5): 2223-2273 | **✓** `gu_kelly_xiu_2020_empirical_ml.pdf` | https://doi.org/10.1093/rfs/hhaa009 |
| 12 | Bianchi, D., Büchner, M., & Tamoni, A. (2021). Bond Risk Premiums with Machine Learning. | *RFS* 34(2): 1046-1089 | **✓** `bianchi_buchner_tamoni_2021_bond_ml.pdf` | https://doi.org/10.1093/rfs/hhaa062 |
| 13 | Bryzgalova, S., Pelger, M., & Zhu, J. (2023). Forest Through the Trees: Building Cross-Sections of Stock Returns. | *JF* (forthcoming) | **✓** `bryzgalova_pelger_zhu_2023_forest.pdf` | https://fass.nus.edu.sg/ecs/ |

## 3. マクロ・クレジット・規制背景

| # | Citation | Outlet | PDF | URL/DOI |
|---|---|---|---|---|
| 14 | Gilchrist, S., & Zakrajšek, E. (2012). Credit Spreads and Business Cycle Fluctuations. | *AER* 102(4): 1692-1720 | **✓** `gilchrist_zakrajsek_2012_credit_spreads.pdf` | https://doi.org/10.1257/aer.102.4.1692 |
| 15 | Favara, G., Gilchrist, S., Lewis, K. F., & Zakrajšek, E. (2016). Updating the Recession Risk and the Excess Bond Premium. | FEDS Notes | **✓** `favara_2016_updating_ebp.pdf` (HTML→PDF) | https://doi.org/10.17016/2380-7172.1836 |
| 16 | Bauer, M. D., & Swanson, E. T. (2023). A Reassessment of Monetary Policy Surprises and High-Frequency Identification. | *NBER Macroeconomics Annual* 37 | **✓** `bauer_swanson_2023_reassessment.pdf` | https://www.nber.org/papers/w29939 |
| 17 | Nakamura, E., & Steinsson, J. (2018). High-Frequency Identification of Monetary Non-Neutrality: The Information Effect. | *QJE* 133(3): 1283-1330 | **✓** `nakamura_steinsson_2018_info_effect.pdf` | https://doi.org/10.1093/qje/qjy004 |
| 18 | Monin, P. J. (2019). The OFR Financial Stress Index. | *Risks* 7(1): 25 | **✓** `monin_2019_ofr_fsi.pdf` (OFR WP 17-04) | https://doi.org/10.3390/risks7010025 |
| 19 | Hanson, S. G., Kashyap, A. K., & Stein, J. C. (2011). A Macroprudential Approach to Financial Regulation. | *JEP* 25(1): 3-28 | **✓** `hanson_kashyap_stein_2011_jep.pdf` | https://web.williams.edu/Economics/seminars/steinJEP.pdf |
| 20 | He, Z., Kelly, B., & Manela, A. (2017). Intermediary asset pricing: New evidence from many asset classes. | *JFE* 126(1): 1-35 | **✓** `he_kelly_manela_2017_intermediary.pdf` | https://doi.org/10.1016/j.jfineco.2017.08.002 |

## 4. 金利カーブ・ベンチマーク手法

| # | Citation | Outlet | PDF | URL/DOI |
|---|---|---|---|---|
| 21 | Gürkaynak, R. S., Sack, B., & Wright, J. H. (2007). The U.S. Treasury Yield Curve: 1961 to the Present. | *JME* 54(8): 2291-2304 | **✓** `gurkaynak_sack_wright_2007_treasury_curve.pdf` (FEDS 2006-28) | https://doi.org/10.1016/j.jmoneco.2007.06.029 |
| 22 | Gürkaynak, R. S., Sack, B., & Wright, J. H. (2010). The TIPS Yield Curve and Inflation Compensation. | *AEJ: Macro* 2(1): 70-92 | **✓** `gurkaynak_sack_wright_2010_tips.pdf` (FEDS 2008-05) | https://doi.org/10.1257/mac.2.1.70 |
| 23 | Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. | *JFE* 33(1): 3-56 | **✓** `fama_french_1993_common_risk_factors.pdf` | https://doi.org/10.1016/0304-405X(93)90023-5 |
| 24 | Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. | *JFE* 116(1): 1-22 | **✓** `fama_french_2015_five_factor.pdf` | https://doi.org/10.1016/j.jfineco.2014.10.010 |
| 25 | Carhart, M. M. (1997). On Persistence in Mutual Fund Performance. | *JF* 52(1): 57-82 | **✓** `carhart_1997_persistence.pdf` | https://doi.org/10.1111/j.1540-6261.1997.tb03808.x |

## 5. 関連・低優先度（C 群、他資産クラス類似ケース）

| # | Citation | Outlet | PDF | URL/DOI |
|---|---|---|---|---|
| 26 | Frazzini, A., & Pedersen, L. H. (2014). Betting against beta. | *JFE* 111(1): 1-25 | **✓** `frazzini_pedersen_2014_bab.pdf` (NBER w16601) | https://doi.org/10.1016/j.jfineco.2013.10.005 |
| 27 | Lustig, H., Roussanov, N., & Verdelhan, A. (2011). Common Risk Factors in Currency Markets. | *RFS* 24(11): 3731-3777 | **✓** `lustig_roussanov_verdelhan_2011_currency.pdf` (NBER w14082) | https://doi.org/10.1093/rfs/hhr068 |
| 28 | Liao, G. Y. (2020). Credit migration and covered interest rate parity. | *JFE* 138(2): 504-525 | **✓** `liao_2020_credit_migration_cip.pdf` (FRB IFDP 1255) | https://doi.org/10.1016/j.jfineco.2020.06.002 |

---

## 追加時のチェックリスト

1. PDF を `references/` に保存（命名は `<first_author>_<year>_<keyword>.pdf`）
2. 該当セクションの表に行を追加（# は連番でなく良い、欠番 OK）
3. APA citation、Outlet、PDF 有無、URL/DOI を埋める
4. 関連が複数セクションにまたがる場合は **メインのセクションに 1 回だけ**登録（横断は `docs/` 側のメモで）

## 取得メモ（2026-05-26）

- 27/28 を無料版から取得。実体は多くが working paper 版（NBER / FEDS / IFDP / 著者サイト / AQR / SSRN）で、本文・図表は出版版とほぼ同一だがページ番号・最終校正が異なる場合あり。引用時は上記 DOI（出版版）を使う。
- **#10 Campisi (2000)** は *Journal of Performance Measurement*（有料・ニッチ誌）で無料版が存在せず未取得。必要なら大学図書館 / 文献複写で。
- **#15 Favara (2016)** は FEDS Notes が HTML 記事のみのため、公式ページを PDF レンダリングして保存（2 ページ）。
- 再配布禁止の Robeco XLSX（Houweling-van Zundert のデータ）は引き続き PDF 化せず、citation のみ。
