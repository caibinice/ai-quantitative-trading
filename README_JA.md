# AIクオンツ・リサーチ・コックピット

**[English](./README.md) | [简体中文](./README_CN.md) | 日本語**

[![ライセンス: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](./LICENSE)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Research_API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Research_UI-61DAFB?logo=react&logoColor=111827)

クオンツ金融の初学者に向けた、中国A株のエンドツーエンド研究プロジェクトです。Tushare Proを構造化された市場・財務データの主ソースとし、AKShare、Eastmoney、CNINFOでニュースと開示資料を補完します。さらに、OpenAI互換LLMでイベントを構造化センチメント・スコアへ変換し、説明可能な銘柄ランキングとシグナル遅延を厳守した履歴バックテストを提供します。

> 本プロジェクトは学習、研究、シミュレーション・バックテスト専用です。証券会社との連携や実注文の機能はなく、投資助言を目的とするものではありません。

**[ライブデモ](https://caibinice.com/quant/) · [プロジェクトストーリー](https://caibinice.com/articles/ai-quant-system) · [中文说明](./README_CN.md)**

<p align="center">
  <a href="https://caibinice.com/quant/">
<img src="docs/images/dashboard.png" alt="AI Quant Research Cockpit dashboard" width="100%">
</a>
<br>
  <sub>研究概要では、銘柄ユニバース、市場データ、センチメント、AI分析カバレッジ、ランキング、パイプラインの稼働状況を、監査可能な一つのワークスペースに集約します。</sub>
</p>

## プロダクトツアー

| 説明可能なAIランキング | 戦略ラボ |
| --- | --- |
| [![AI 因子ランキング](docs/images/ai-rankings.png)](https://caibinice.com/quant/rankings) | [![戦略研究所](docs/images/strategy-lab.png)](https://caibinice.com/quant/strategy) |
| モメンタム、財務品質、センチメントを個別に確認でき、評価日、データソース、異常警告も追跡できます。 | 銘柄ユニバース、ファクターの重み、コスト、約定遅延、バックテスト期間を一画面で設定できます。 |

| 学習アカデミー | このプロジェクトを作った理由 |
| --- | --- |
| [![クオンツ学習アカデミー](docs/images/learning-academy.png)](https://caibinice.com/quant/learn) | [![プロジェクト ストーリー](docs/images/project-story.png)](https://caibinice.com/articles/ai-quant-system) |
| 5ステージ、11章、33の概念ページを通じて、コードベースそのものを実践的なクオンツ学習コースとして活用できます。 | 証拠を重視する設計思想は、**From an Engineering Loop to Trustworthy Research: My AI Quant System** で詳しく説明しています。 |

## 主な機能

- **研究概要：** 銘柄ユニバース、日足、センチメント・イベント数、AI分析カバレッジ、上位スコア、パイプライン状態を一覧できます。
- **市場・財務：** ローソク足、出来高、日次スナップショット、報告期間別に保存された財務指標を確認できます。
- **説明可能なAIランキング：** 市場モメンタム、財務品質、センチメントを個別スコアとして表示し、総合順位へ統合します。
- **センチメント・レーダー：** ニュース／開示の時系列を、ポジティブ・中立・ネガティブのラベル、信頼度、要約、判定理由とともに閲覧できます。自動パイプラインは既定で6時間ごとに実行され、タスクセンターで変更した間隔は直ちに反映されます。
- **ソース間のイベント重複排除:** 正確なレコードはコンテンツ ハッシュによってブロックされます。再投稿は、正規化された URL、タイトル、本文の概要、および 90% のしきい値で 72 時間のウィンドウによって照合されます。同じイベントが複数の企業に関係する場合でも、株式固有の判断を保持できますが、全株式ビューでは表示が統合され、関連するすべてのティッカーがリストされます。
- **戦略ラボ：** 銘柄ユニバース、ファクターの重み、期間、しきい値、保有銘柄数、手数料、スリッページを画面上で設定できます。
- **ダイナミックユニバース:** 業界をまたがる大型株 15 銘柄から開始し、1 株から 30 銘柄まで自動的にサイズ変更するか、ティッカー シンボルを直接編集します。
- **ライト／ダークテーマ：** ヘッダーから切り替えられ、選択はブラウザに保存されます。EChartsも現在の配色へ連動します。
- **多言語UI：** すべての画面をEnglish、简体中文、日本語へ切り替えられます。保存済みCookieを優先し、未選択時は対応するブラウザ言語を自動検出します。既定言語はEnglishです。
- **2ファクター・バックテスト：** センチメントと市場ファクターを組み合わせ、シグナルを必ず1本遅延させた上で、資産曲線、ベンチマーク、リターン、ドローダウン、シャープレシオ、売買回転率を出力します。
- **取引カレンダーと指数ベンチマーク:** 中国A株 取引カレンダーを保存し、デフォルトのベンチマークとして均等加重ユニバース リターンを提示する代わりに、CSI 300 などの実際の指数を使用します。
- **Point-in-Time ファンダメンタルズ:** レポート期間と実際の発表時刻を別々に保持するため、スコアはそのスコアリング日に公開されたデータのみにアクセスできます。
- **ウォークフォワード 検証:** ローリング トレーニング ウィンドウでパラメーターを選択し、後続の アウト・オブ・サンプル リターンのみを最終カーブにステッチします。
- **MySQL ベースのタスク キュー:** 収集、LLM 分析、品質チェック、進行状況、再試行、キャンセル、永続状態を含む独立したワーカーでの アウト・オブ・サンプル 実験を実行します。
- **データ品質アラート:** OHLC の一貫性、異常なジャンプ、取引日のギャップ、古いデータ、Point-in-Time カバレッジ、ベンチマーク カバレッジ、センチメント スコア範囲をチェックします。
- **ラーニング アカデミー:** は、株式および ローソク足 の基本から、Python 時系列、因子、センチメント、ウォークフォワード 検証、キャップストーン スタディまで、5 つのステージ、11 章、および 33 のクリック可能なコンセプト レッスンに従います。すべての概念には、平易な用語、間違い分析、ガイド付き演習、注釈付きコード、予想される出力、検証チェックリストが含まれています。アカデミーには、11 のダウンロード可能な教育データセットと 11 のオフライン ラボも含まれています。進行状況は MySQL に同期され、クロスデバイスの継続、チェック解除、および完全なリセットが行われます。
- **スケジューリング:** 市場データ、スコア、インフラストラクチャ データ、および cron による品質チェックを実行します。ニュース、開示、重複排除、LLM センチメント、およびスコアリングでは、永続的な MySQL 間隔設定が使用され、デフォルトは 6 時間ごとです。 「今すぐパイプライン全体を実行」はシーケンスを厳密に実行し、市場データや財務データを冗長にフェッチしません。
- **デモ モード:** 明確にラベル付けされた合成データを生成し、ライブ プロバイダーを使用せずに完全なワークフローを探索します。

## アーキテクチャ

```mermaid
flowchart LR
    A["Tushare Pro<br/>Market / Adjustment / Financials / Calendar / Indices"] --> B["FastAPI hybrid data pipeline"]
    J["AKShare + public sources<br/>News / Disclosures / Fallbacks"] --> B
    C["OpenAI-compatible LLM<br/>DeepSeek and others"] --> D["Structured sentiment analysis"]
    B --> H["MySQL-backed task queue"]
    H --> I["Independent worker"]
    I --> E["MySQL<br/>aq_ research tables"]
    D --> E
    E --> F["Point-in-time scoring / Backtest / Walk-forward / Quality rules"]
    F --> G["React + ECharts<br/>Visual research workspace"]
    E --> G
```

- **バックエンド:** Python、FastAPI、SQLAlchemy、pandas、および APScheduler。
- **データベース:** デフォルトでは MySQL、データベースが構成されていない場合はローカル SQLite フォールバックを使用します。
- **フロントエンド:** React、TypeScript、Vite、および ECharts。
- **LLM:** OpenAI Chat Completions 互換エンドポイント。決定的な辞書ルールにより、再現可能なフォールバックが提供されます。
- **キュー:** Redis 依存関係のない行ロックベースのジョブ要求。現在の MariaDB 互換モードは、単一のワーカーを対象としています。
- **本番環境:** Nginx、systemd、および Docker を使用しない Python 仮想環境。フロントエンドはローカルに構築されてアップロードされるため、展開は 2 コア、2 GB サーバーに適しています。

## 5分でセットアップ

要件: PowerShell 7、64 ビット Python 3.11 以降、Node.js 20 以降、および利用可能な MySQL データベース。

完全な製品バージョンは現在、`main` ブランチで保守されています。このプロジェクトを個別に開発する場合は、そのブランチを複製し、プライベート `credentials.txt` をリポジトリ ルートに配置します。兄弟の `ai-blog` プロジェクトは必要ありません。

```powershell
# 1. Install dependencies and seed demo data.
pwsh -File scripts/setup.ps1 -SeedDemo

# 2. Start the API and web app together.
pwsh -File scripts/dev.ps1
```

以下を開きます：

- ウェブアプリ：[http://127.0.0.1:5173/quant/](http://127.0.0.1:5173/quant/)
- 学習アカデミー：[http://127.0.0.1:5173/quant/learn](http://127.0.0.1:5173/quant/learn)
- APIドキュメント：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

実行中のターミナルで `Ctrl+C` を押して、開発スタックを停止します。

## 学習アカデミーの使い方

完全なロードマップについては、`/quant/learn` を開いてください。 **完全初心者向けの株式と ローソク足** から始めてください。教科書、用語、実際の例、フローチャートを読んでください。コンセプトカードを開きます。そして、メンタル モデル、詳細な調査、プロジェクトの例、よくある間違い、実践的な演習の順序に従います。この章に戻ってデモを実行し、チェックリストと 3 つの質問からなるクイズを完了し、前/次のコントロールを使用して続行します。

|ステージ |章 |結果 |
| --- | --- | --- |
| 1. マップを構築する |株式と ローソク足 の基本。クオンツマップ;プロジェクトツアー |市場の基本と調査ループを理解する |
| 2. データ言語を学ぶ | Python ブリッジ。 NumPy/パンダ | Java、JavaScript、または MATLAB から科学的な Python への移行 |
| 3. 信頼できる戦略を構築する | 市場・財務、ファクター・バックテスト | リターン、リスク、Point-in-Timeデータ、コスト、シグナル遅延を理解する |
| 4. AI と検証を追加 | LLM センチメント; ウォークフォワード |テキストを監査可能な要素に変換し、過剰適合を検査する |
| 5. リサーチシステムを完成させる | エンジニアリング・ガバナンス、最終課題 | 再現可能・反証可能な2ファクター研究を完成させる |

進行状況の動作:

- ブラウザーは進行状況をローカルにキャッシュし、API が利用可能になるたびに MySQL の `aq_learning_progress` に同期します。
- 以前のリリースからの最初のアップグレード中に、リモート テーブルにまだレコードがない場合、ローカルの進行状況が MySQL に移行されます。
- 別のデバイスまたはブラウザから同じサイトを開くと、チェックリストの状態とクイズの最高スコアが MySQL から再ロードされます。
- チェックリストの項目はチェックを外すことができます。どの章でも前に戻ることができます。 **進行状況をリセット**すると、MySQL とブラウザのキャッシュの両方がクリアされます。
- **MySQL に同期** のみがリモート永続性を確認します。ネットワークが利用できない場合、UI には **オフライン キャッシュ** が表示されます。

この例は、リポジトリ ルートから実行することもできます。

```powershell
.\.venv\Scripts\python.exe learning\examples\00_kline_basics.py
.\.venv\Scripts\python.exe learning\examples\01_python_bridge.py
.\.venv\Scripts\python.exe learning\examples\02_pandas_timeseries.py
.\.venv\Scripts\python.exe learning\examples\03_signal_delay.py
.\.venv\Scripts\python.exe learning\examples\04_sentiment_factor.py
.\.venv\Scripts\python.exe learning\examples\05_walk_forward.py
```

推奨される 8 ～ 10 週間のカリキュラムについては、スタンドアロンの [学習ガイド](learning/README.md) を参照してください。

## ワンコマンドでリモート展開

運用プロファイルは 2 コア、2 GB の Linux サーバーをターゲットにしており、Nginx、単一プロセスの FastAPI サービス、軽量の常駐ワーカー、および systemd を使用します。ワーカーはアイドル状態の間、キュー層のみをロードします。 pandas またはコレクション負荷の高いタスクの後、アイドル状態で 30 秒後に終了し、systemd がクリーンな軽量プロセスを起動して、永続的なメモリの増加を回避します。サーバーは Node.js を必要とせず、Docker を実行しません。

`credentials.example.txt` に基づいて、プライベートの追跡されていない `credentials.txt` を作成します。ファイルでは、スコープ外のプロジェクト セクションまたは共有 `quant.*` セクションのいずれかを使用できます。兄弟ブログ資格情報ファイルは、プロジェクト ファイルが存在しない場合の互換性フォールバックとしてのみ使用されます。

```ini
[remote.ssh]
host=caibinice.com
port=22
user=regular-ssh-user
password=ssh-password
root_password=root-password-for-su
```

最初のデプロイメントでは、`credentials.txt` の `[platform.action] password` から操作パスワードを読み取ります。スクリプトは追跡されていない署名キーを生成して保存します。後続のデプロイメントでは `.deploy/action-auth.json` が再利用されます。環境変数はパスワードを一時的に上書きする場合があります。

```powershell
$env:AI_PLATFORM_ACTION_PASSWORD='<your-operation-password>'
pwsh -File scripts/deploy.ps1
Remove-Item Env:AI_PLATFORM_ACTION_PASSWORD
```

デプロイメントスクリプト:

1. Ruff、pytest、フロントエンド実稼働ビルド、および関連するチェックを実行します。
2. ソース コードと `frontend/dist` のみをパッケージします。ただし、`.env`、`credentials.txt`、および `.deploy` は除きます。
3. ネイティブ Python 3.11 と Nginx をインストールし、優先度の低い 1 GB OOM 保護スワップ ファイルを作成し、アプリを `/quant` の下に分離します。
4. systemd API とワーカー サービスを書き込み、`credentials.txt` で定義されている同じリモート MySQL データベースに接続します。
5. `caibinice.com` および `www.caibinice.com` の信頼できる Let’s Encrypt 証明書を取得し、ポート 80 を HTTPS にリダイレクトします。
6. 北京時間の 03:17 と 12:17 に証明書の更新をチェックし、成功後に Nginx をホットリロードします。
7. API ヘルスチェックを実行し、失敗した場合には以前のリリースを自動的に復元します。

`ai-quant-cert-renew.timer` を有効にしておきます。操作パスワードと有効期限の短い署名キーは、追跡されていないローカル ファイルに残ります。

```text
.deploy/action-auth.json
```

このリポジトリからビルド、デプロイ、および選択的にプッシュします。

```powershell
pwsh -File scripts/deploy.ps1 -BuildOnly
pwsh -File scripts/deploy.ps1
pwsh -File scripts/github-push.ps1 `
  -Message 'fix: describe the change' `
  -Files @('path/to/changed-file')
```

GitHub ヘルパーは、このリポジトリの `credentials.txt` から `[github]` のみを読み取ります。 `127.0.0.1:20808` プロキシとトークンは現在のプロセスにのみ使用され、リモート URL やグローバル Git 構成は変更されません。

`https://caibinice.com/quant/` を開くと、市場データ、研究結果、コースを利用できます。データ取得、AI分析、スコアリング、バックテスト、タスク管理、ウォークフォワード検証、品質チェック、自動化設定などの更新操作には、操作パスワードが必要です。FastAPIがパスワードを検証して30分間有効なトークンを発行し、パスワード自体はフロントエンドのストレージに保存しません。APSchedulerとWorkerはサービス層の関数を直接呼び出すため、バックグラウンド処理にブラウザ認証は不要です。サーバー上のAPIは `127.0.0.1:8000` だけで待ち受けます。

運用ビルドでは、ソース マップが無効になり、React と ECharts が `vendor-*` チャンクに分割され、ファーストパーティ ビジネス チャンクのみが慎重に難読化されます。難読化はカジュアルな読み取りのコストを高めますが、バックエンドの承認に代わるものではありません。

一般的な操作:

```powershell
pwsh -File scripts/status.ps1   # Inspect services and logs.
pwsh -File scripts/restart.ps1  # Restart the deployment.
pwsh -File scripts/stop.ps1     # Stop the web, API, worker, and renewal timer.
pwsh -File scripts/start.ps1    # Restore all services.
```

ポート 80 と 443 のみを開く必要があります。ポート 8080 は使用されていません。リリースは `/opt/ai-quantitative-trading` に保存され、最新の 5 つが保持され、アプリケーション シークレットはサーバー側の `shared/app.env` にのみ存在します。

ブログのコメントと AI ニュース フィードは、`/api/blog/comments` および `/api/blog/news` を通じてこの FastAPI サービスを再利用します。電子メール アドレスは、`aq_blog_comments` では非公開のままです。管理エンドポイントは、少なくとも 32 ランダム バイトの個別のベアラー トークンを使用し、このリポジトリと兄弟ブログ リポジトリ内の追跡されていない `.deploy/blog-admin.json` ファイルに同期されます。ブラウザ管理ページでは、現在のタブの `sessionStorage` にのみ保持されます。 AI ニュース サービスは、OpenAI、Google DeepMind、Hugging Face、Google AI、MIT AI、NVIDIA Developer、AWS Machine Learning からの公式フィードを 6 時間ごとに集約し、最新の 7 日間のみを返します。 `/api/blog/news` は、`page`、`pageSize`、および `source` をサポートします。

## データベースとLLMの設定

環境テンプレートをコピーします。

```powershell
Copy-Item .env.example .env
```

主要な設定:

```dotenv
DATABASE_URL=mysql+pymysql://user:password@host:3306/database?charset=utf8mb4
LLM_ENABLED=true
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your-key
LLM_API_KEY_BACKUP=your-backup-key
LLM_MODEL=deepseek-v4-flash
LLM_THINKING_ENABLED=true
LLM_REASONING_EFFORT=max
BLOG_ADMIN_TOKEN=replace-with-at-least-32-random-bytes
```

ワークスペースは、追跡されていない `credentials.txt` をリポジトリ ルートから読み取ることもできます。

```ini
[mysql.remote]
host=127.0.0.1
port=3306
database=your_database
user=your_user
password=your_password
charset=utf8mb4

[deepseek.api]
base-url=https://api.deepseek.com
api-key=your-key
api-key-backup=your-backup-key
model=deepseek-v4-flash

[tushare]
token=your-tushare-token
```

兄弟の `ai-blog` プロジェクトが資格情報を一元管理している場合は、`D:\codes\ai-blog\scripts\sync-shared-credentials.ps1` を実行して、Tushare セクションを `[quant.tushare]` として保存します。ローカルの開発と展開では、この範囲指定されたセクションが認識されます。トークンがリリース アーカイブ、フロントエンド バンドル、または Git 履歴に入ることはありません。

すべてのプロジェクト テーブルは `aq_` プレフィックスを使用するため、既存のデータベースを安全に共有できます。実際のシークレットは、`.env`、システム環境変数、または `credentials.txt` にのみ属し、Git ではすべて無視されます。

## データソース

### Tushare Pro：主要な構造化データプロバイダー

トークンが構成された後、バックエンドは公式 HTTP API を直接呼び出すため、追加の SDK は必要ありません。次のエンドポイントは、2,000 ポイントのアカウントを使用して読み取り専用でテストされています。

|データ | Tushare API |現在の使用状況 |
| --- | --- | --- |
|ストックマスター | `stock_basic` |ティッカー、名前、業界、市場 |
| 中国A株 日足バー | `daily` |生の未調整OHLCV |
|調整係数 | `adj_factor` |日足バーと統合された将来調整価格 |
|日次指標 | `daily_basic` |売上高とその他の毎日の指標 |
|取引カレンダー | `trade_cal` |オープン/クローズ状態を 10 年単位で同期 |
|日足バーのインデックス | `index_daily` | CSI 300 などの バックテスト ベンチマーク |
|財務指標 | `fina_indicator` | 6 年間にわたる ROE、売上総利益率、売上/利益の成長 |
|損益計算書 | `income` |売上高、営業利益、総利益、帰属純利益 |
|貸借対照表 | `balancesheet` |総資産、負債および帰属資本 |
|キャッシュフロー計算書 | `cashflow` |営業、投資、財務、期末キャッシュフロー |

将来調整後の価格は、`raw price × current adjustment factor ÷ final adjustment factor in the selected range` として計算されます。 Tushare の金額値は、保管前に数千 CNY から CNY に変換されます。すべてのレコードは `source=tushare-pro` を保持し、UI は実際のソースを公開します。財務行には、報告日と発表日の両方が保持されます。品質スコアリングでは、スコアリング日までに発表された情報のみを読み取ることができます。

テストされたアカウントは、`stk_limit`、`moneyflow`、`dividend`、および `index_weight` にもアクセスできます。これらは、価格制限、資本フロー、配当、および構成モジュールの候補ですが、単に機能数を増やすためにランキングに組み込まれるわけではありません。 `ths_daily` にはより多くのポイントが必要ですが、`news` および `anns_d` には、テストされた 2,000 ポイントのアカウントでは使用できない別のアクセス許可が必要です。

クライアントは、対応する 1 分あたり 200 リクエストの許容値に対して、最小 0.35 秒の間隔を強制します。日次バー、ファンダメンタルズ、カレンダー、またはインデックスが失敗するか、データを返さない場合、そのコンポーネントはトークン、リクエスト本文、またはシークレットをエラーにせずに AKShare にフォールバックします。

公式参照: [API ディレクトリ](https://tushare.pro/document/2)、[ポイント権限](https://tushare.pro/document/2?doc_id=290)、[日足](https://tushare.pro/document/2?doc_id=27)、[財務指標](https://tushare.pro/document/2?doc_id=79)、[ニュース](https://tushare.pro/document/2?doc_id=143)、[会社]開示](https://tushare.pro/document/2?doc_id=176)。

### AKShareと公開ソース：センチメント分析とフォールバック

|データ | AKShare API |目的 |
| --- | --- | --- |
|フルマーケットのスナップショット | `stock_zh_a_spot_em` |ティッカー、名前、評価額、時価総額のスナップショット |
|日足バーのフォールバック | `stock_zh_a_hist` | Tushare が利用できない場合の Eastmoney のバーの将来調整 |
|二次的な毎日のフォールバック | `stock_zh_a_hist_tx` | Eastmoney にネットワーク障害が発生した場合の Tencent データ |
|取引カレンダーのフォールバック | `tool_trade_date_hist_sina` |過去および今年の 中国A株 営業日 |
|インデックスベンチマーク | `index_zh_a_hist` | `stock_zh_index_daily_tx` にフォールバックします |
| Point-in-Time | ファンダメンタルズ | `stock_yjbb_em` |最新の発表日を利用可能時間として使用します |
|財務指標 | `stock_financial_abstract_new_ths` | Sina の広範な財務表にフォールバック |
|株式ニュース | `stock_news_em` |最近のニュース、本文の概要、ソース、URL |
|会社情報 | `stock_individual_notice_report` |株式および日付範囲ごとの開示 |
|法定のクロスソース開示 | `stock_zh_a_disclosure_report_cninfo` | CNINFO の開示情報は Eastmoney とともに収集され、重複が排除されます。

AKShare自体はオープンソースですが、上流サイトではAPI仕様の変更、レート制限、配信遅延が起こり得ます。本プロジェクトは出所情報を保持し、障害をコンポーネント単位で分離し、フォールバック経路を用意しています。それでも重要な結論は、取引所の開示資料または有料データと照合してください。CNINFOは [AKShareの公開ラッパー](https://akshare.akfamily.xyz/data/stock/stock.html) 経由で統合しており、追加アカウントは不要です。

センチメント ページには、候補ソースと登録要件も記載されています。

- Eastmoney の株式ニュース、Eastmoney の開示、および CNINFO の開示は、追加のアカウントなしで統合されています。
- [Tushare Pro ニュース](https://tushare.pro/document/2?doc_id=143) トークンが構成されている場合でも、依然として個別の認証が必要です。現在のパイプラインの依存関係ではありません。
- 従来の [GDELT DOC 2.0](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) フルテキスト API にはキーは必要ありませんが、新しい GDELT Cloud 開発者 API にはアカウントと API キーが必要です。国際的にカバーする範囲は広いですが、中国A株 中国のエンティティ マッチングとノイズについてはさらなる評価が必要なため、オプションの候補のままです。

## データから戦略まで

### 1. AIセンチメント分析

各イベントは構造化されたレコードを生成します。

```json
{
  "label": "利好",
  "score": 0.6,
  "confidence": 0.82,
  "summary": "A concise summary within 80 Chinese characters",
  "rationale": "Why the event received this label"
}
```

モデルは、提供されたテキストのみを使用し、外部事実を追加せず、取引推奨を提供しないように指示されます。デフォルトは、`deepseek-v4-flash` 思考モード (`thinking.type=enabled` および `reasoning_effort=max`) です。クォータ、認証、タイムアウト、および主キーのサーバー障害が発生すると、バックアップ キーがトリガーされます。決定的辞書ルールは、両方のキーが失敗した場合にのみ使用されます。データベースには実際のモデル名が保存されるため、フォールバック結果が LLM 出力として表示されることはありません。 [DeepSeek 思考モードのドキュメント](https://api-docs.deepseek.com/guides/thinking_mode) を参照してください。

### 2. 説明可能な銘柄ランキング

- **市場モメンタム：** 5日、20日、60日のリターンを組み合わせ、年率換算ボラティリティによるペナルティを差し引きます。デモ行は実データ系列から除外し、35%を超える価格急変がある場合はモメンタムを中立に戻します。
- **財務品質：** ROE、売上高成長率、純利益成長率、粗利益率など、最新の比較可能な比率を使用します。売上高や利益の絶対額を割合スコアとして扱うことはありません。
- **センチメント:** モデルの信頼性と時間減衰によって、最新 30 日間のイベントを重み付けします。
- **複合:** 3 つの 0 ～ 100 のサブスコアを、戦略ラボで設定された重みと組み合わせます。

ランキングは調査フィルターであり、収益の確率ではありません。このページでは、汚染されたデータを「AI の強気」として提示するのではなく、市場データのカットオフ、ソース、5/20/60 日のリターン、ボラティリティ、イベント数、異常警告を公開しています。ランキング、市場データ、センチメント、ガバナンスのページでは、現在の戦略ラボの世界がわかります。新しいティッカーを保存すると、市場履歴が欠落している場合に自動的に同期のキューに入れられます。

### 3. センチメント＋市場の2ファクター・バックテスト

各取引日は、その日までに公開されたイベントのみを使用できます。この戦略は、モメンタムとローリング センチメント のしきい値を通過する上位 N 銘柄を選択し、それらを均等に加重します。重要な漏洩ガードは次のとおりです。

```python
# A signal calculated after the close on day T is held only from T+1.
applied_weights = targets.shift(1).fillna(0.0)
```

リバランスにより `turnover × (fee_rate + slippage_rate)` が差し引かれます。基本の バックテスト は、明示的に センチメント プラス市場戦略であり、ファンダメンタルズ とは混合しません。財務的品質は調査ランキングにのみ表示され、発表時刻がスコア付け日以降である Point-in-Time データを読み取ります。

### 4. Point-in-Time財務データと指数ベンチマーク

`aq_pit_financials` は、`report_date` と `available_at` の両方を格納します。 `as_of=T` でリクエストされたすべてのスコアには、`available_at <= T` が適用されます。ベース バックテスト は、選択されたインデックスを `aq_index_prices` から読み取ります。等重みユニバース ベンチマークは、インデックスがまだ同期されていない場合にのみ使用されます。

### 5. ウォークフォワード方式のアウト・オブ・サンプル検証

すべてのローリング ウィンドウにはトレーニング セグメントがあり、その直後にテスト セグメントが続きます。運動量ウィンドウと センチメント しきい値はトレーニング中にのみ比較されます。選択した固定パラメータはテスト セグメントに適用され、それらのテスト結果のみが最終的な エクイティカーブ に入力されます。各ウィンドウの日付、選択されたパラメータ、トレーニング メトリクス、およびテスト メトリクスは、監査可能にするために保存されます。

## 実データ運用フロー

1. デフォルトの 15 株の 中国A株 ユニバースから開始します。無料プロバイダーを初めて検証する場合は、3 ～ 5 銘柄に減らし、安定性が確認された後に拡張します。
2. **データ ガバナンス**から取引カレンダー、指数、および Point-in-Time ファンダメンタルズ を同期します。
3. **Strategy Laboratory** にユニバースを保存し、**タスク センター**で **今すぐ完全なパイプラインを実行** を選択します。ニュースと開示情報を取得し、イベントの重複を排除し、LLM 分析を実行して、厳密な順序でスコアを生成します。その下の 4 つのクイックアクション ボタンは独立したタスクを実行し、自動的に連鎖しません。
4. LLM センチメント タスクは、構成された API クォータを消費します。
5. サンプル期間、インデックス ベンチマーク、およびトランザクション コストを選択し、履歴 バックテスト を実行します。
6. **アウト・オブ・サンプル 検証**から ウォークフォワード 検証を実行し、**データ ガバナンス**で品質チェックを実行します。
7. ユニバースを拡張する前に、警告、アップストリーム レート制限、およびデータベース容量を検査します。

## スケジューリング

開発では、スケジュールはデフォルトで無効になっています。ユニバースを確認した後、有効にします。

```dotenv
SCHEDULER_ENABLED=true
PRICE_SYNC_CRON=20 18 * * 1-5
SCORE_CRON=40 19 * * 1-5
INFRASTRUCTURE_CRON=10 8 * * 6
DATA_QUALITY_CRON=10 20 * * 1-5
```

スケジュールは `Asia/Shanghai` を使用します。内部タスクのタイムスタンプは UTC として保存され、明示的な `Z` とともに返されます。中国のニュースと開示のタイムスタンプは明示的な `+08:00` を使用します。フロントエンドは常に北京時間としてフォーマットします。ニュース、開示、重複排除、LLM センチメント、および株式スコアリングは、デフォルトで 6 時間ごとに実行される 1 つの厳密なシリアル パイプラインを形成します。その間隔と有効な状態は `aq_automation_settings` に保持されます。 **タスク センター**で 1 ～ 48 時間の間隔を保存すると、APScheduler は再起動せずにすぐに再スケジュールされます。手動によるフル パイプラインの実行では、同じジョブ タイプが作成され、すでにキューに入れられているパイプラインまたは実行中のパイプラインが再利用され、クォータの重複使用が回避されます。複数のプロセスが開始される可能性があるため、開発自動リロードを備えたスケジューラを有効にしないでください。リモート プロファイルは、MySQL ジョブのみをキューに入れる 1 つのスケジューラ インスタンスを実行します。独立したワーカーがそれらを実行します。

## 検証

完全なチェック スイートを実行します。

```powershell
pwsh -File scripts/check.ps1
```

Ruff、pytest、ESLint、TypeScript、および Vite 本番ビルドを実行します。バックエンドの範囲は次のことに重点を置いています。

- 1取引日のシグナル遅延。
- 将来の センチメント が過去に影響を与えるのを防ぎます。
- 手数料と スリッページ が エクイティカーブ を削減します。
- 運動量と センチメント 減衰の計算;
- モデルの JSON 解析とルールのフォールバック。
- Tencent 市場データのフォールバック形式。
- 実際の発表日とインデックスフォールバックによる Point-in-Time の可視性。
- MySQL キューの優先順位、キャンセル、再試行、および状態遷移。
- OHLC および取引カレンダーギャップの品質ルール。
- テスト ウィンドウのみを含む最終的な ウォークフォワード 曲線。
- 6 つの学習デモはすべて独立して実行されます。
- 6 時間のデフォルトの センチメント スケジュールと MySQL 永続性。
- DeepSeek Thinking リクエストと主キー/バックアップ キーのフォールバック。
- 学習ソースのダウンロード許可リスト、秘密ファイルのブロック、およびトラバーサル保護。

ローカル API とフロントエンドを開始した後、ブラウザー回帰スイートを実行します。

```powershell
Set-Location frontend
npm run test:e2e
```

Playwrightでは、英語・中国語・日本語の自動検出とCookie保存、デスクトップ／モバイルのレイアウト、ライトテーマ、動的なページタイトル、全11章と33の概念ページ、ソースダウンロード、センチメント・ラベルの色、自動化設定を検証します。

## リポジトリ構成

```text
ai-quantitative-trading/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPIルート
│   │   ├── core/                # 設定とデータベース
│   │   ├── services/            # 取得、センチメント、ランキング、バックテスト、スケジューリング
│   │   ├── worker.py            # MySQL永続タスクWorker
│   │   ├── models.py            # aq_データベーステーブル
│   │   └── main.py
│   ├── scripts/seed_demo.py
│   └── tests/
├── frontend/src/
│   ├── components/
│   ├── i18n/                    # UIと学習コンテンツの翻訳
│   └── pages/                   # 検証、タスク、データガバナンスを含む
├── learning/                    # ガイド、最終課題テンプレート、データセット、実行可能な実験
├── docs/images/                 # 公開サイトで取得したREADME用スクリーンショット
├── deploy/                      # Nginx、systemd、リモート導入テンプレート
├── scripts/                     # ローカル開発、検証、展開、運用
├── .env.example
├── README.md                    # Englishドキュメント
├── README_CN.md                 # 简体中文ドキュメント
└── README_JA.md                 # 日本語ドキュメント
```

## 既知の制約

- 無料の Web データは交換グレードでも低遅延でもないため、高頻度の実行やライブ実行には適していません。
- 「その日の最新 100 レコード」などのアップストリーム制限は、完全な過去のニュース アーカイブに代わるものではありません。
- 現在の バックテスト は約定に近いものであり、価格制限、一時停止、約定不可能な注文、印紙税の違い、生産能力への影響などはモデル化されていません。
- 無料の財務レポート エンドポイントは、ユニバースをフィルタリングする前に、レポート期間ごとに市場全体を取得します。これらのジョブをキューに入れ、履歴四半期の数を制限します。
- リモートの MariaDB プロファイルは、ジョブの要求に通常の行ロックを使用します。デフォルトでは 1 人のワーカーになります。追加のワーカーは安全に待機しますが、スループットは直線的に増加しません。
- サイトは公開されていますが、機密書き込みアクションでは有効期間の短いバックエンド トークンが使用されます。マルチユーザーのコラボレーションには、アカウント、RBAC、および強力な監査モデルが必要です。
- ドメイン証明書は systemd 更新タイマーに依存します。ドメインまたは DNS を変更するには、再展開と新しい証明書が必要です。
- 合成デモ データはインターフェイスとワークフローのみを検証します。戦略のパフォーマンスを判断するために使用してはなりません。
- センチメント モデルは間違いを犯します。出力をサンプルレビューし、モデルのバージョン、プロンプト、ソース URL を保持します。

今後の作業には、より厳密な順方向/逆方向調整の一貫性、業界とスタイルのエクスポージャー、一時停止と価格制限による執行制約、バージョン管理されたデータのスナップショット、研究実験の追跡などが含まれます。ライブ取引への直接の接続は、意図的に現在の範囲外にあります。

## ライセンス

[MIT ライセンス](LICENSE) に基づいてリリースされました。
