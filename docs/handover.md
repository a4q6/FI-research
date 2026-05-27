# 社会人博士研究 - 引き継ぎドキュメント

このドキュメント1つで、Claude Code 等の新環境で議論を継続できる。

---

## 1. 研究者プロフィール

- **現職**: 債券のアトリビューション分析
- **前職**: 為替のアルゴリズミックトレード
- **保有スキル**: SQLite による市場データ管理、Jupyter ノートブックでの分析、Python での定量分析
- **言語**: 日本語・英語ともに可
- **検討中**: 社会人博士進学。実務と接続する研究テーマを探索中

## 2. 制約・前提

- **時間**: 社会人なので分析時間は限定的。再現性と自動化を重視
- **データアクセス**: 業務環境のデータは持ち出さない。研究は公開データ + 大学経由 WRDS を想定
- **教員探し**: WRDS アクセスがある大学を優先（一橋ICS、東大、京大、早慶、神戸大 等）
- **コンプライアンス**: 業務データの研究流用は厳禁。情報遮断を徹底

---

## 3. 議論の経緯サマリー

Claude.ai のチャットで行ったテーマ探索の流れ:

1. **方向性の3軸提示**: (a) アトリビューションの理論深掘り (b) FXアルゴ×債券の接続点 (c) マルチエージェントAI
2. **興味の絞り込み**: 軸1・2 + 信用リスク/社債/証券化商品に強い興味
3. **6テーマ案提示**: 社債アトリビューション×EBP、証券化商品、マルチアセット統合、CIPデビエーション×クレジット、金利サプライズ×クレジット伝播、キャリー×信用リスク
4. **データ・教員観点でフィルタ**: 案5・案1を当初有力に
5. **ML系テーマ追加**: 案7（アルファpersistence）、案8（SHAP）、案9（社債factor zoo）、案10（レジーム依存）、案11（マルチエージェントLLM）
6. **新規性詳細議論**: 案8と案9を最終有力候補に
7. **構造的議論**: 「なぜ債券にバリュー・グロースが無いのか」を整理（後述）
8. **先行研究レビュー**: web検索で確認、Bai-Bali-Wen (2019) の撤回を発見

---

## 4. 最有力候補 2 テーマ

### 案 A1: SHAP値ベースの債券アトリビューション

**問題意識**
従来の債券アトリビューション（Campisi型、キーレート型）は線形分解を前提とするが、コンベクシティ・オプション性が強い証券では非線形要因が無視できない。機械学習＋SHAP値で非線形分解を行い、線形手法では「アルファ」と誤分類されていた系統的要因への露出を識別する。

**新規性ポイント**
- 「予測モデルの解釈」ではなく「実現リターンの事後分解ツール」としてSHAPを位置づける視点転換
- 線形アトリビューション（Campisi型）と非線形SHAPアトリビューションの整合性条件を理論的に定式化
- コンベクシティ・オプション性が強い証券（MBS、Callable、CoCo債）でこそ非線形分解の価値が出る、という実証

**リサーチクエスチョン**
- SHAPベースのアトリビューションは、線形分解と比較してout-of-sampleでどの程度「残差」を縮小できるか？
- 縮小された残差は、線形モデルでは「アルファ」と誤分類されていた系統的要因への露出か？
- 非線形寄与が大きい銘柄・期間の特徴は何か（コンベクシティ、credit option性、liquidity stress期）？

**手法詳細**
1. ベンチマーク: Campisi 型アトリビューション（金利・スプレッド・キャリー・銘柄選択）
2. ML モデル: XGBoost / LightGBM で月次リターンを要因群（duration, KRD, OAS, OAS変化, 格付ダミー, セクターダミー, マクロ変数）で予測
3. SHAP 値で個別銘柄・個別月のリターン寄与を分解、ポートフォリオレベルに集計
4. Shapley 値の公理（efficiency, symmetry, additivity）がポートフォリオ集計後も保たれることを示す
5. レジーム別（金利上昇/下降、credit stress/calm）で線形 vs SHAP の説明力比較

**評価**
- 理論+実証のバランスが良く、博士論文として枠組みを作りやすい
- ML色が強くキャッチー
- 債券アトリビューション文脈ではほぼ未開拓
- 実務インパクト高い

### 案 A2: 社債ファクター構造の再評価（ポストBBW）

**問題意識**
社債クロスセクション・ファクターモデルの代表的論文 Bai-Bali-Wen (2019, JFE) が2023年に撤回された。社債ファクター文献は再構築期にある。Feng-Giglio-Xiu (2020) の double-selection LASSO を社債に体系的に適用し、米欧日でファクター構造を比較する。

**新規性ポイント**
- Bai-Bali-Wen (2019) 撤回後の文脈で「社債版 Taming the Factor Zoo」を構築
- Feng-Giglio-Xiu (2020) の double-selection LASSO を社債に体系的適用
- 日本社債市場への適用（先行研究は米国中心）

**リサーチクエスチョン**
- アトリビューションで識別される「銘柄選択アルファ」は、既知＋新規候補ファクターを統制した後、どの程度残るか？
- 残ったアルファは、運用者のスキルなのか、未観測のリスクファクターへの露出なのか？
- 米国・欧州・日本社債市場でのファクター構造の共通性と相違は？

**手法詳細**
1. 候補ファクター群: 既存研究+新規候補 15-20 個
2. Kozak-Nagel-Santosh (2020) の SDF アプローチで、社債リターン横断面の pricing kernel を推定
3. Feng-Giglio-Xiu の double-selection LASSO:
   - Step 1: アルファをファクター群で LASSO 選択
   - Step 2: 各候補ファクターを残りのファクターで LASSO 選択
   - Step 3: 両方で選ばれたファクターのみ統制してアルファ有意性検定
4. クロスセクションの pricing test（GRS test、Fama-MacBeth）
5. 米国・欧州・日本での比較

**評価**
- アカデミック新規性が最も高い
- BBW撤回というタイミング的な追い風
- 実装はやや重いが、Robeco の公開データセットで予備分析可能

### 意思決定マトリクス

| 評価軸 | A1 (SHAP) | A2 (Post-BBW) |
|---|---|---|
| アカデミック新規性 | 中-高 | 高 |
| 実務インパクト | 高 | 中 |
| キャッチーさ | 高 | 中 |
| データ入手性 | 中（自前+WRDS） | 中-高（公開+WRDS） |
| 指導教員探しやすさ | 中（ML×Finance必要） | 高（アセットプライシング系） |
| 論文化難易度 | 中 | 中-高 |
| 完成形のイメージ | 明確 | やや探索的 |

---

## 5. 補助テーマ（本論文の章として組み込み可能）

- **B1. レジーム依存アトリビューション**: HMM・change-point detection でレジーム識別 → レジーム別係数推定
- **B2. アルファ persistence**: Fama-MacBeth クロスセクション回帰で selection alpha の持続性検証
- **B3. マルチエージェント LLM**: アトリビューション結果の自動解釈・異常検知（実装力勝負）

## 6. 検討したが優先度を下げたテーマ

- **C1. 証券化商品アトリビューション**: データ入手性が厳しい
- **C2. CIPデビエーション×クレジット**: 興味深いが Liao (2020) の延長になりやすい
- **C3. 金利サプライズ×クレジット伝播**: 当初有力だったが、ML色を強めたA1/A2に軍配

---

## 7. 構造的議論: 債券スタイル投資が無い理由

議論の中で整理した、研究の問題意識の背景。

1. **リターン構造の違い**: 株式は凸（無限アップサイド）、債券は凹（キャップ付きアップサイド、満期保有でクーポン+額面）→ バリュー戦略が機能しにくい。割安に見える社債は大抵デフォルト懸念が織り込まれていて、本当にデフォルトする確率も高い（fallen angel問題）
2. **ファクターは存在するが名前が違う**: Carry ≈ Value、Defensive/Low-risk ≈ Quality、Momentum、DTS調整Value
3. **市場構造**: OTC取引・流動性不均一 → スマートベータの実装コストが高い。同じ発行体の異なるシリーズで日次取引が無いことも普通
4. **インデックス構造**: 債券インデックスは負債加重（発行残高加重）。「最も借金している主体」が最大ウェイトになるため、「ベンチマーク逸脱＝スタイル」の整理が綺麗に効かない
5. **デュレーション支配**: IG債リターン分散の70-80%が金利要因。スタイル/ファクター効果は残り20-30%の中の話なので相対的に目立たない

この問題意識は案A2と直結する。

---

## 8. 先行研究レビュー

### マクロファイナンス系

**Gilchrist & Zakrajšek (2012)** "Credit Spreads and Business Cycle Fluctuations" *AER 102(4)*
- クレジットスプレッドを (a) 予想デフォルト成分と (b) 残差 = excess bond premium (EBP) に分解
- EBP は景気変動の予測力を持つ
- データ: 米国非金融企業（Compustat、CRSP）、Lehman/Warga・Merrill Lynch DB、1973年〜
- 公開データ: FRB が毎月更新（https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv）

**Favara, Gilchrist, Lewis, & Zakrajšek (2016)** "Updating the Recession Risk and the Excess Bond Premium" *FEDS Notes*
- EBP の更新版データ提供開始

### 高頻度識別・金融政策

**Nakamura & Steinsson (2018)** "High-Frequency Identification of Monetary Non-Neutrality: The Information Effect" *QJE 133(3)*
- FOMC 公表周辺の30分窓での金利変化を金融政策ニュースに帰属する識別戦略
- データ: FOMC 会合周辺の金利先物 tick データ。Replication package あり

**IMF WP/2024/224** "A New Dataset of High-Frequency Monetary Policy Shocks"
- 20中央銀行・3,545イベント（2000-2022）

### 社債ファクター投資

**Houweling & van Zundert (2017)** "Factor Investing in the Corporate Bond Market" *FAJ 73(2)*
- size, low-risk, value, momentum の4ファクターが社債で有意なアルファを生成
- データ: Bloomberg Barclays インデックス
- 公開データ: Robeco がファクターポートフォリオ月次リターンを無料公開

**Bai, Bali, & Wen (2019)** "Common risk factors in the cross-section of corporate bond returns" *JFE 131(3)* ⚠️ **2023年撤回**
- van Binsbergen & Schwert (2021) 等で頑健性問題が指摘
- データ: TRACE + Mergent FISD（2002-2016、124万観測）
- 案A2 の問題意識の起点

### ファクター乱立問題

**Feng, Giglio, & Xiu (2020)** "Taming the Factor Zoo: A Test of New Factors" *JF 75(3)*
- 高次元の既存ファクターを統制した上で新ファクターの寄与を評価する double-selection LASSO 手法
- 案A2 のメイン手法。社債への適用が新規性

**Kozak, Nagel, & Santosh (2020)** "Shrinking the Cross-Section" *JFE 135(2)*
- SDF アプローチでファクター次元削減
- 案A2 の補完手法

### 機械学習×アセットプライシング

**Gu, Kelly, & Xiu (2020)** "Empirical Asset Pricing via Machine Learning" *RFS 33(5)*
- 株式リターン予測のML手法の体系的比較
- 案A1 の方法論基盤

**Bianchi, Büchner, & Tamoni (2021)** "Bond Risk Premiums with Machine Learning" *RFS 34(2)*
- 国債リスクプレミアムへのML適用
- 案A1 の債券版先行研究

**Bryzgalova, Pelger, & Zhu (2023)** "Forest Through the Trees" *JF*
- 決定木による資産価格付け
- 案A1 で対比対象

### アトリビューション実務系

**Campisi (2000)** "Primer on Fixed Income Performance Attribution" *Journal of Performance Measurement*
- 債券アトリビューションの実務標準
- 案A1 のベンチマーク手法

### 流動性・信用リスク

**Dick-Nielsen, Feldhütter, & Lando (2012)** "Corporate bond liquidity before and after the onset of the subprime crisis" *JFE 103(3)*
- 社債流動性プレミアムの計測

### 追加で読むべき文献（TODO）

- Israel, Palhares, & Richardson (2018) AQR の社債ファクター論文
- Jensen, Kelly, & Pedersen (2023) Global Factor Data Repository
- He, Kelly, & Manela (2017) 仲介金融機関の制約とリスクプレミアム
- Asvanunt & Richardson (2017) The Credit Risk Premium
- Frazzini & Pedersen (2014) Betting Against Beta
- Lustig, Roussanov, & Verdelhan (2011) Common Risk Factors in Currency Markets（FXキャリーのRP構造）
- Liao (2020) Credit migration and covered interest rate parity

---

## 9. データソース一覧

### 公開・無料

| ソース | URL | 用途 |
|---|---|---|
| FRB EBP | federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv | A1のマクロ要因、A2の参照系統的成分 |
| Robeco社債ファクター | robeco.com の研究公開ページ | A2の予備分析・ファクター再現 |
| FRED | fred.stlouisfed.org | マクロ変数全般 |
| Kenneth French Library | mba.tuck.dartmouth.edu/.../ken.french | 株式ファクター |
| Global Factor Data (JKP) | jkpfactors.com | グローバル株式ファクター |
| IMF MP Shocks (2024) | IMF WP/2024/224 | 日本含む金融政策ショック |
| 日証協 公社債店頭参考値 | market.jsda.or.jp | 日本社債参考価格 |
| 財務省 国債金利情報 | mof.go.jp/jgbs/reference/interest_rate | 日本国債イールドカーブ |

### 大学経由（WRDS）

| ソース | 用途 |
|---|---|
| TRACE | 米国社債の全取引データ（2002年〜） |
| Mergent FISD | 社債発行体情報・発行条件・格付履歴 |
| Compustat / CRSP | 企業財務、株式リターン |

注意: Enhanced TRACE と Standard TRACE の違いに留意。BBW論文の頑健性問題はEnhanced TRACEの更新に絡む。

### 有料（業務環境にはあるが研究には使わない）

Bloomberg Terminal、Refinitiv Eikon、QUICK、日経NEEDS。
研究は公開データと大学経由データのみで完結させる。

### SQLite スキーマ案（暫定）

```sql
-- 銘柄マスタ
CREATE TABLE bonds_master (
    cusip TEXT PRIMARY KEY,
    issuer TEXT,
    sector TEXT,
    rating TEXT,
    coupon REAL,
    issue_date DATE,
    maturity_date DATE,
    currency TEXT
);

-- 月次リターン・属性
CREATE TABLE bonds_monthly (
    cusip TEXT,
    date DATE,
    price REAL,
    yield REAL,
    spread_oas REAL,
    duration REAL,
    convexity REAL,
    ret_total REAL,
    ret_excess REAL,
    PRIMARY KEY (cusip, date),
    FOREIGN KEY (cusip) REFERENCES bonds_master(cusip)
);

-- マクロ変数
CREATE TABLE macro_monthly (
    date DATE PRIMARY KEY,
    ebp REAL,
    gz_spread REAL,
    term_spread REAL,
    vix REAL
);

-- ファクターリターン
CREATE TABLE factor_returns (
    date DATE,
    factor_name TEXT,
    ret REAL,
    PRIMARY KEY (date, factor_name)
);
```

### 命名規則

- 日付列: `date` (DATE型、タイムゾーン明記)
- 銘柄ID: `cusip` (米国)、`isin` (グローバル)、`jp_secid` (日本独自)
- リターン: `ret_*` プレフィックス
- スプレッド: `spread_*` プレフィックス

---

## 10. 直近の TODO

1. **公開データ取得スクリプト**: FRB EBP、Robecoファクターデータ（即着手可能）
2. **A1 vs A2 のフィージビリティ確認**: 両テーマの予備分析を1つずつ走らせる
3. **日本社債データの取得可能性検証**: 日証協公開分の範囲確認
4. **指導教員候補リストアップ**: 公開論文・所属・最近の指導実績の調査
5. **WRDS アクセス確認**: 候補大学への問い合わせ

---

## 11. 作業指針

新環境（Claude Code等）で作業する際の指針:

1. **データ取得は再現可能に**: スクリプト化。URL・取得日・スキーマを必ず記録
2. **分析は Jupyter ノートブック**: 番号付きで配置（例: `01_ebp_exploration.ipynb`）
3. **重要な発見はMarkdown化**: 後で論文に転用できる形で日本語/英語で
4. **SQLite中心**: 取得データは正規化して保存
5. **コードは型ヒント + docstring**: 後で論文付随リポジトリとして公開できる品質
6. **先行研究の引用形式**: APA簡略形式
7. **業務データは絶対に研究目的で使わない**: 情報遮断徹底
8. **公開データであっても利用規約確認**: 特に WRDS、Bloomberg ライセンス

---

## 12. 次の会話の始め方

このドキュメントを読ませた上で、例えば以下のように指示する:

- 「このドキュメントを読んで、A1の予備分析を始めましょう。まずは FRB の EBP データ取得スクリプトから」
- 「A2 で進む前提で、Robecoの公開データを使ったファクター再現の計画を立てて」
- 「指導教員候補のリストアップを手伝って」
- 「SHAP値ベース・アトリビューションの理論的整合性条件を一緒に考えて」
