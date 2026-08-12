# AI Quant Research Cockpit

**English | [简体中文](./README_CN.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](./LICENSE)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Research_API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Research_UI-61DAFB?logo=react&logoColor=111827)

An end-to-end A-share research project for quantitative-finance beginners. It uses Tushare Pro as the primary source for structured market and financial data, supplements news and disclosures with AKShare, Eastmoney, and CNINFO, converts events into structured sentiment scores through an OpenAI-compatible LLM, and produces explainable stock rankings and strictly delayed historical backtests.

> This project is for learning, research, and simulated backtesting only. It has no brokerage integration, never places real orders, and does not constitute investment advice.

**[Live Demo](https://101.132.78.217/quant/) · [Project Story](https://101.132.78.217/articles/ai-quant-system) · [中文说明](./README_CN.md)**

<p align="center">
  <a href="https://101.132.78.217/quant/">
    <img src="docs/images/dashboard.png" alt="AI Quant Research Cockpit dashboard" width="100%">
  </a>
  <br>
  <sub>The research overview brings the universe, market data, sentiment, AI coverage, rankings, and pipeline health into one auditable workspace.</sub>
</p>

## Product tour

| Explainable AI ranking | Strategy laboratory |
| --- | --- |
| [![AI factor ranking](docs/images/ai-rankings.png)](https://101.132.78.217/quant/rankings) | [![Strategy laboratory](docs/images/strategy-lab.png)](https://101.132.78.217/quant/strategy) |
| Inspect momentum, financial quality, and sentiment separately, together with the scoring date, source, and anomaly warnings. | Configure the universe, factor weights, costs, execution delay, and backtest period from one page. |

| Learning academy | Why this project exists |
| --- | --- |
| [![Quant learning academy](docs/images/learning-academy.png)](https://101.132.78.217/quant/learn) | [![Project story](docs/images/project-story.png)](https://101.132.78.217/articles/ai-quant-system) |
| Five stages, 11 chapters, and 33 concept pages turn the codebase into a practical quant-learning path. | Read **From an Engineering Loop to Trustworthy Research: My AI Quant System** for the design rationale behind the evidence-first workflow. |

## What it can do

- **Research overview:** monitor the stock universe, daily bars, sentiment-event volume, AI-analysis coverage, leading scores, and pipeline status.
- **Market and fundamentals:** inspect candlesticks, volume, daily snapshots, and financial metrics stored by reporting period.
- **Explainable AI ranking:** combine market momentum, financial quality, and sentiment as visible sub-scores with a composite ranking.
- **Sentiment radar:** browse a news-and-disclosure timeline with positive/neutral/negative labels, confidence, summaries, and rationales. The automated pipeline runs every six hours by default, and interval changes made in the task center take effect immediately.
- **Cross-source event deduplication:** exact records are blocked by content hashes. Reposts are matched by normalized URL, title, body summary, and a 72-hour window at a 90% threshold. The same event can still retain stock-specific judgments when it concerns multiple companies, while the all-stocks view merges the display and lists every related ticker.
- **Strategy laboratory:** visually configure the universe, factor weights, windows, thresholds, number of holdings, fees, and slippage.
- **Dynamic universe:** start from 15 cross-industry large caps, resize automatically from 1 to 30 stocks, or edit ticker symbols directly.
- **Light and dark themes:** switch themes from the header; the choice persists in the browser and ECharts follows the active palette.
- **Two-factor backtest:** combine sentiment and market factors, enforce a one-bar signal delay, and report equity, benchmark, return, drawdown, Sharpe ratio, and turnover.
- **Trading calendar and index benchmark:** store the A-share trading calendar and use real indices such as CSI 300 instead of presenting equal-weight universe returns as the default benchmark.
- **Point-in-time fundamentals:** keep the reporting period and actual announcement time separately, so a score can only access data that was public on that scoring date.
- **Walk-forward validation:** select parameters in rolling training windows and stitch only the subsequent out-of-sample returns into the final curve.
- **MySQL-backed task queue:** run collection, LLM analysis, quality checks, and out-of-sample experiments in independent workers with progress, retry, cancellation, and persistent state.
- **Data-quality alerts:** check OHLC consistency, abnormal jumps, trading-day gaps, stale data, point-in-time coverage, benchmark coverage, and sentiment-score ranges.
- **Learning academy:** follow five stages, 11 chapters, and 33 clickable concept lessons from stock and candlestick basics through Python time series, factors, sentiment, walk-forward validation, and a capstone study. Every concept includes plain-language terminology, mistake analysis, guided exercises, annotated code, expected output, and a verification checklist. The academy also contains 11 downloadable teaching datasets and 11 offline labs. Progress syncs to MySQL for cross-device continuation, unchecking, and full reset.
- **Scheduling:** run market data, scores, infrastructure data, and quality checks by cron. News, disclosures, deduplication, LLM sentiment, and scoring use a persistent MySQL interval setting, defaulting to every six hours. “Run full pipeline now” executes the sequence strictly and does not redundantly fetch market or financial data.
- **Demo mode:** generate clearly labeled synthetic data and explore the complete workflow without live providers.

## Architecture

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

- **Backend:** Python, FastAPI, SQLAlchemy, pandas, and APScheduler.
- **Database:** MySQL by default, with a local SQLite fallback when no database is configured.
- **Frontend:** React, TypeScript, Vite, and ECharts.
- **LLM:** an OpenAI Chat Completions-compatible endpoint; deterministic dictionary rules provide a reproducible fallback.
- **Queue:** row-lock-based job claiming with no Redis dependency. The current MariaDB-compatible mode is intended for a single worker.
- **Production:** Nginx, systemd, and a Python virtual environment without Docker. The frontend is built locally and uploaded, making the deployment suitable for a 2-core, 2 GB server.

## Five-minute setup

Requirements: PowerShell 7, 64-bit Python 3.11+, Node.js 20+, and an available MySQL database.

The complete production version is currently maintained on the `agent/research-infrastructure` branch. When developing this project independently, clone that branch and place a private `credentials.txt` in the repository root. The sibling `ai-blog` project is not required.

```powershell
# 1. Install dependencies and seed demo data.
pwsh -File scripts/setup.ps1 -SeedDemo

# 2. Start the API and web app together.
pwsh -File scripts/dev.ps1
```

Open:

- Web app: [http://127.0.0.1:5173/quant/](http://127.0.0.1:5173/quant/)
- Learning academy: [http://127.0.0.1:5173/quant/learn](http://127.0.0.1:5173/quant/learn)
- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Press `Ctrl+C` in the running terminal to stop the development stack.

## Using the learning academy

Open `/quant/learn` for the complete roadmap. Start with **Stocks and Candlesticks for Absolute Beginners**: read the textbook, terminology, worked example, and flowchart; open the concept cards; and follow the sequence of mental model, deep dive, project example, common mistakes, and hands-on exercise. Return to the chapter to run its demo, complete the checklist and three-question quiz, and use the previous/next controls to continue.

| Stage | Chapters | Outcome |
| --- | --- | --- |
| 1. Build the map | Stock and candlestick basics; Quant map; Project tour | Understand market basics and the research loop |
| 2. Learn the data language | Python bridge; NumPy/pandas | Move from Java, JavaScript, or MATLAB to scientific Python |
| 3. Build a trustworthy strategy | Market and fundamentals; Factor backtesting | Understand return, risk, point-in-time data, costs, and signal delay |
| 4. Add AI and validation | LLM sentiment; Walk-forward | Turn text into an auditable factor and inspect overfitting |
| 5. Complete a research system | Engineering governance; Capstone | Deliver a reproducible, falsifiable two-factor study |

Progress behavior:

- The browser caches progress locally and synchronizes it to `aq_learning_progress` in MySQL whenever the API is available.
- During the first upgrade from an earlier release, local progress migrates to MySQL if the remote table has no record yet.
- Opening the same site from another device or browser reloads checklist state and best quiz scores from MySQL.
- Checklist items can be unchecked; every chapter can navigate backward; **Reset progress** clears both MySQL and the browser cache.
- Only **Synced to MySQL** confirms remote persistence. The UI displays **Offline cache** when the network is unavailable.

The examples can also be run from the repository root:

```powershell
.\.venv\Scripts\python.exe learning\examples\00_kline_basics.py
.\.venv\Scripts\python.exe learning\examples\01_python_bridge.py
.\.venv\Scripts\python.exe learning\examples\02_pandas_timeseries.py
.\.venv\Scripts\python.exe learning\examples\03_signal_delay.py
.\.venv\Scripts\python.exe learning\examples\04_sentiment_factor.py
.\.venv\Scripts\python.exe learning\examples\05_walk_forward.py
```

See the standalone [Learning Guide](learning/README.md) for the suggested eight-to-ten-week curriculum.

## One-command remote deployment

The production profile targets a 2-core, 2 GB Linux server and uses Nginx, a single-process FastAPI service, a lightweight resident worker, and systemd. The worker loads only the queue layer while idle. After a pandas or collection-heavy task, it exits after 30 idle seconds and systemd launches a clean lightweight process, avoiding persistent memory growth. The server does not need Node.js and does not run Docker.

Create a private, untracked `credentials.txt` based on `credentials.example.txt`. The file may use either unscoped project sections or shared `quant.*` sections. A sibling blog credentials file is used only as a compatibility fallback when the project file does not exist.

```ini
[remote.ssh]
host=public-server-ip
port=22
user=regular-ssh-user
password=ssh-password
root_password=root-password-for-su
```

The first deployment reads the operation password from `[platform.action] password` in `credentials.txt`. The script generates and stores an untracked signing key; subsequent deployments reuse `.deploy/action-auth.json`. An environment variable may temporarily override the password:

```powershell
$env:AI_PLATFORM_ACTION_PASSWORD='<your-operation-password>'
pwsh -File scripts/deploy.ps1
Remove-Item Env:AI_PLATFORM_ACTION_PASSWORD
```

The deployment script:

1. runs Ruff, pytest, the frontend production build, and related checks;
2. packages only source code and `frontend/dist`, excluding `.env`, `credentials.txt`, and `.deploy`;
3. installs native Python 3.11 and Nginx, creates a low-priority 1 GB OOM-protection swap file, and isolates the app under `/quant`;
4. writes systemd API and worker services and connects to the same remote MySQL database defined in `credentials.txt`;
5. obtains a trusted short-lived Let’s Encrypt certificate for the public IP and redirects port 80 to HTTPS;
6. checks certificate renewal twice a day and hot-reloads Nginx after success;
7. runs an API health check and automatically restores the previous release on failure.

Let’s Encrypt IP certificates are valid for approximately six days, so keep `ai-quant-cert-renew.timer` enabled. The operation password and short-lived signing key stay in the untracked local file:

```text
.deploy/action-auth.json
```

Build, deploy, and selectively push from this repository:

```powershell
pwsh -File scripts/deploy.ps1 -BuildOnly
pwsh -File scripts/deploy.ps1
pwsh -File scripts/github-push.ps1 `
  -Message 'fix: describe the change' `
  -Files @('path/to/changed-file')
```

The GitHub helper reads only `[github]` from this repository’s `credentials.txt`. It uses the `127.0.0.1:20808` proxy and token only for the current process and does not change the remote URL or global Git configuration.

Open `https://public-server-ip/quant/` to access market data, research results, and courses. Write actions such as collection, AI analysis, scoring, backtesting, task management, walk-forward validation, quality checks, and automation configuration request an operation password. FastAPI validates it and issues a 30-minute token; the password is never written to frontend storage. APScheduler and the worker call service-layer functions directly, so background schedules do not require browser authentication. The API listens only on `127.0.0.1:8000` on the server.

Production builds disable source maps, split React and ECharts into `vendor-*` chunks, and conservatively obfuscate only first-party business chunks. Obfuscation raises the cost of casual reading but does not replace backend authorization.

Common operations:

```powershell
pwsh -File scripts/status.ps1   # Inspect services and logs.
pwsh -File scripts/restart.ps1  # Restart the deployment.
pwsh -File scripts/stop.ps1     # Stop the web, API, worker, and renewal timer.
pwsh -File scripts/start.ps1    # Restore all services.
```

Only ports 80 and 443 need to be open. Port 8080 is unused. Releases are stored under `/opt/ai-quantitative-trading`, the latest five are retained, and application secrets exist only in the server-side `shared/app.env`.

Blog comments and the AI-news feed reuse this FastAPI service through `/api/blog/comments` and `/api/blog/news`. Email addresses remain private in `aq_blog_comments`. Admin endpoints use a separate Bearer token of at least 32 random bytes, synchronized to untracked `.deploy/blog-admin.json` files in this repository and the sibling blog repository. The browser admin page keeps it only in the current tab’s `sessionStorage`. The AI-news service aggregates official feeds from OpenAI, Google DeepMind, Hugging Face, Google AI, MIT AI, NVIDIA Developer, and AWS Machine Learning every six hours and returns only the latest seven days. `/api/blog/news` supports `page`, `pageSize`, and `source`.

## Database and LLM configuration

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

Key settings:

```dotenv
DATABASE_URL=mysql+pymysql://user:password@host:3306/database?charset=utf8mb4
LLM_ENABLED=true
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your-key
LLM_API_KEY_BACKUP=your-backup-key
LLM_MODEL=deepseek-v4-pro
LLM_THINKING_ENABLED=true
LLM_REASONING_EFFORT=high
BLOG_ADMIN_TOKEN=replace-with-at-least-32-random-bytes
```

The workspace can also read an untracked `credentials.txt` from the repository root:

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
model=deepseek-v4-pro

[tushare]
token=your-tushare-token
```

If the sibling `ai-blog` project centrally manages credentials, run `D:\codes\ai-blog\scripts\sync-shared-credentials.ps1` to store the Tushare section as `[quant.tushare]`. Local development and deployment recognize this scoped section. The token never enters a release archive, frontend bundle, or Git history.

All project tables use the `aq_` prefix, so they can safely share an existing database. Real secrets belong only in `.env`, system environment variables, or `credentials.txt`, all of which are ignored by Git.

## Data sources

### Tushare Pro: primary structured provider

After a token is configured, the backend calls the official HTTP API directly and does not require an additional SDK. The following endpoints have been read-only tested with a 2,000-point account:

| Data | Tushare API | Current use |
| --- | --- | --- |
| Stock master | `stock_basic` | Ticker, name, industry, and market |
| A-share daily bars | `daily` | Raw unadjusted OHLCV |
| Adjustment factors | `adj_factor` | Forward-adjusted prices merged with daily bars |
| Daily indicators | `daily_basic` | Turnover and other daily metrics |
| Trading calendar | `trade_cal` | Open/closed state synchronized in ten-year chunks |
| Index daily bars | `index_daily` | Backtest benchmarks such as CSI 300 |
| Financial indicators | `fina_indicator` | Six years of ROE, gross margin, and revenue/profit growth |
| Income statement | `income` | Revenue, operating profit, total profit, and attributable net profit |
| Balance sheet | `balancesheet` | Total assets, liabilities, and attributable equity |
| Cash-flow statement | `cashflow` | Operating, investing, financing, and ending cash flow |

Forward-adjusted price is calculated as `raw price × current adjustment factor ÷ final adjustment factor in the selected range`. Tushare amount values are converted from thousands of CNY to CNY before storage. Every record retains `source=tushare-pro`, and the UI exposes the real source. Financial rows keep both reporting dates and announcement dates; quality scoring can only read information announced by the scoring date.

The tested account can also access `stk_limit`, `moneyflow`, `dividend`, and `index_weight`. These are candidates for price-limit, capital-flow, dividend, and constituent modules, but they are not mixed into the ranking merely to increase the feature count. `ths_daily` requires more points, while `news` and `anns_d` require separate permissions unavailable to the tested 2,000-point account.

The client enforces a minimum 0.35-second interval for the corresponding 200-requests-per-minute allowance. If daily bars, fundamentals, calendars, or indices fail or return no data, that component falls back to AKShare without placing tokens, request bodies, or secrets in errors.

Official references: [API directory](https://tushare.pro/document/2), [point permissions](https://tushare.pro/document/2?doc_id=290), [daily bars](https://tushare.pro/document/2?doc_id=27), [financial indicators](https://tushare.pro/document/2?doc_id=79), [news](https://tushare.pro/document/2?doc_id=143), and [company disclosures](https://tushare.pro/document/2?doc_id=176).

### AKShare and public sources: sentiment and fallback providers

| Data | AKShare API | Purpose |
| --- | --- | --- |
| Full-market snapshot | `stock_zh_a_spot_em` | Ticker, name, valuation, and market-cap snapshot |
| Daily-bar fallback | `stock_zh_a_hist` | Eastmoney forward-adjusted bars when Tushare is unavailable |
| Secondary daily fallback | `stock_zh_a_hist_tx` | Tencent data when Eastmoney has network failures |
| Trading-calendar fallback | `tool_trade_date_hist_sina` | Historical and current-year A-share trading days |
| Index benchmark | `index_zh_a_hist` | Falls back to `stock_zh_index_daily_tx` |
| Point-in-time fundamentals | `stock_yjbb_em` | Uses latest announcement date as the availability time |
| Financial indicators | `stock_financial_abstract_new_ths` | Falls back to Sina’s wide financial table |
| Stock news | `stock_news_em` | Recent news, body summary, source, and URL |
| Company disclosures | `stock_individual_notice_report` | Disclosures by stock and date range |
| Statutory cross-source disclosures | `stock_zh_a_disclosure_report_cninfo` | CNINFO disclosures collected alongside Eastmoney and deduplicated |

AKShare is open source, but upstream sites can change, rate-limit, or delay their interfaces. This project preserves source attribution, isolates component failures, and maintains fallback paths. Material conclusions should still be cross-checked against exchange disclosures or paid data. CNINFO is integrated through [AKShare’s public wrapper](https://akshare.akfamily.xyz/data/stock/stock.html) and requires no additional account.

The sentiment page also documents candidate sources and registration requirements:

- Eastmoney stock news, Eastmoney disclosures, and CNINFO disclosures are integrated without extra accounts.
- [Tushare Pro news](https://tushare.pro/document/2?doc_id=143) still needs separate authorization even when a token is configured; it is not a dependency for the current pipeline.
- The legacy [GDELT DOC 2.0](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) full-text API requires no key, while the newer GDELT Cloud developer API requires an account and API key. Its international coverage is broad, but A-share Chinese entity matching and noise need further evaluation, so it remains an optional candidate.

## From data to strategy

### 1. AI sentiment analysis

Each event produces a structured record:

```json
{
  "label": "利好",
  "score": 0.6,
  "confidence": 0.82,
  "summary": "A concise summary within 80 Chinese characters",
  "rationale": "Why the event received this label"
}
```

The model is instructed to use only the supplied text, add no external facts, and provide no trading recommendation. The default is `deepseek-v4-pro` Thinking Mode with `thinking.type=enabled` and `reasoning_effort=high`. Quota, authentication, timeout, and server failures on the primary key trigger the backup key; deterministic dictionary rules are used only after both keys fail. The database stores the actual model name so a fallback result is never presented as LLM output. See the [DeepSeek Thinking Mode documentation](https://api-docs.deepseek.com/guides/thinking_mode).

### 2. Explainable stock ranking

- **Market momentum:** combine 5-, 20-, and 60-day returns and subtract an annualized volatility penalty. Demo rows are excluded from real series, and jumps above 35% block momentum and fall back to neutral.
- **Financial quality:** use the latest available comparable ratios such as ROE, revenue growth, net-profit growth, and gross margin. Absolute revenue and profit are never treated as percentage scores.
- **Sentiment:** weight the latest 30 days of events by model confidence and time decay.
- **Composite:** combine the three 0–100 sub-scores with the weights configured in the strategy laboratory.

The ranking is a research filter, not a probability of return. The page exposes the market-data cutoff, source, 5/20/60-day returns, volatility, event count, and anomaly warnings instead of presenting contaminated data as “AI bullishness.” Rankings, market data, sentiment, and governance pages read the current strategy-lab universe. Saving a new ticker automatically queues synchronization when its market history is missing.

### 3. Sentiment + market two-factor backtest

Each trading day can use only events published by that day. The strategy selects the top N stocks that pass the momentum and rolling-sentiment thresholds, then equal-weights them. The critical leakage guard is:

```python
# A signal calculated after the close on day T is held only from T+1.
applied_weights = targets.shift(1).fillna(0.0)
```

Rebalancing deducts `turnover × (fee_rate + slippage_rate)`. The base backtest is explicitly a sentiment-plus-market strategy and does not mix in fundamentals. Financial quality appears in the research ranking only and reads point-in-time data whose announcement time is not later than the scoring date.

### 4. Point-in-time fundamentals and index benchmarks

`aq_pit_financials` stores both `report_date` and `available_at`. Every score requested with `as_of=T` applies `available_at <= T`. The base backtest reads the selected index from `aq_index_prices`; an equal-weight universe benchmark is used only when that index has not yet been synchronized.

### 5. Walk-forward out-of-sample validation

Every rolling window has a training segment followed immediately by a test segment. Momentum windows and sentiment thresholds are compared only in training. The selected fixed parameters are then applied to the test segment, and only those test returns enter the final equity curve. Each window’s dates, selected parameters, training metrics, and test metrics are stored for auditability.

## Real-data workflow

1. Start from the default 15-stock A-share universe. When validating free providers for the first time, reduce it to three to five stocks, then expand after stability is confirmed.
2. Synchronize the trading calendar, indices, and point-in-time fundamentals from **Data Governance**.
3. Save the universe in **Strategy Laboratory**, then select **Run full pipeline now** in **Task Center**. It fetches news and disclosures, deduplicates events, runs LLM analysis, and generates scores in strict order. The four quick-action buttons below it run independent tasks and do not chain automatically.
4. LLM sentiment tasks consume the configured API quota.
5. Select the sample period, index benchmark, and transaction costs, then run a historical backtest.
6. Run walk-forward validation from **Out-of-sample Validation**, then execute quality checks in **Data Governance**.
7. Before expanding the universe, inspect warnings, upstream rate limits, and database capacity.

## Scheduling

Scheduling is disabled by default in development. Enable it after confirming the universe:

```dotenv
SCHEDULER_ENABLED=true
PRICE_SYNC_CRON=20 18 * * 1-5
SCORE_CRON=40 19 * * 1-5
INFRASTRUCTURE_CRON=10 8 * * 6
DATA_QUALITY_CRON=10 20 * * 1-5
```

Schedules use `Asia/Shanghai`. Internal task timestamps are stored as UTC and returned with an explicit `Z`; Chinese news and disclosure timestamps use an explicit `+08:00`; the frontend always formats them as Beijing time. News, disclosures, deduplication, LLM sentiment, and stock scoring form one strict serial pipeline that runs every six hours by default. Its interval and enabled state are persisted in `aq_automation_settings`; save an interval from 1 to 48 hours in **Task Center**, and APScheduler reschedules immediately without a restart. Manual full-pipeline execution creates the same job type and reuses an already queued or running pipeline to avoid duplicate quota usage. Do not enable the scheduler with development auto-reload because multiple processes may start. The remote profile runs one scheduler instance that only enqueues MySQL jobs; the independent worker executes them.

## Validation

Run the complete check suite:

```powershell
pwsh -File scripts/check.ps1
```

It runs Ruff, pytest, ESLint, TypeScript, and the Vite production build. Backend coverage focuses on:

- one-trading-day signal delay;
- preventing future sentiment from affecting the past;
- fees and slippage reducing the equity curve;
- momentum and sentiment-decay calculations;
- model JSON parsing and rule fallback;
- Tencent market-data fallback format;
- point-in-time visibility by actual announcement date and index fallbacks;
- MySQL queue priority, cancellation, retry, and state transitions;
- OHLC and trading-calendar-gap quality rules;
- final walk-forward curves containing test windows only;
- all six learning demos running independently;
- the six-hour default sentiment schedule and MySQL persistence;
- DeepSeek Thinking requests and primary/backup key fallback;
- learning-source download allowlists, secret-file blocking, and traversal protection.

After starting the local API and frontend, run the browser regression suite:

```powershell
Set-Location frontend
npm run test:e2e
```

Playwright verifies the light theme, dynamic page titles, all 11 chapters and 33 concept pages, source downloads, sentiment-label colors, and automation configuration.

## Repository layout

```text
ai-quantitative-trading/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI routes
│   │   ├── core/                # Configuration and database
│   │   ├── services/            # Collection, sentiment, ranking, backtest, scheduling
│   │   ├── worker.py            # Persistent MySQL task worker
│   │   ├── models.py            # aq_ database tables
│   │   └── main.py
│   ├── scripts/seed_demo.py
│   └── tests/
├── frontend/src/
│   ├── components/
│   └── pages/                   # Includes validation, tasks, and data governance
├── learning/                    # Guide, capstone template, datasets, and runnable labs
├── docs/images/                 # README screenshots captured from the live deployment
├── deploy/                      # Nginx, systemd, and remote installation templates
├── scripts/                     # Local development, checks, deployment, and operations
├── .env.example
├── README.md                    # English documentation
└── README_CN.md                 # 简体中文说明
```

## Known limitations

- Free web data is neither exchange-grade nor low-latency and is unsuitable for high-frequency or live execution.
- Upstream limits such as “the latest 100 records for the day” do not replace a complete historical news archive.
- The current backtest approximates close-to-close execution and does not model price limits, suspensions, unfillable orders, stamp-duty differences, or capacity impact.
- Free financial-report endpoints fetch the full market by reporting period before filtering the universe. Queue these jobs and limit the number of historical quarters.
- The remote MariaDB profile uses ordinary row locks for job claiming. It defaults to one worker; additional workers wait safely, but throughput does not scale linearly.
- The site is public, while sensitive write actions use short-lived backend tokens. Multi-user collaboration would require accounts, RBAC, and a stronger audit model.
- Public-IP certificates are short-lived and depend on a systemd renewal timer. Changing the public IP requires redeployment and a new certificate.
- Synthetic demo data validates the interface and workflow only; it must not be used to judge strategy performance.
- Sentiment models make mistakes. Sample-review outputs and retain model versions, prompts, and source URLs.

Future work includes stricter forward/backward adjustment consistency, industry and style exposures, suspension and price-limit execution constraints, versioned data snapshots, and research experiment tracking. Direct connection to live trading is intentionally outside the current scope.

## License

Released under the [MIT License](LICENSE).
