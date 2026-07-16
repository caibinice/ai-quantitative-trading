# AI 量化研究舱

一个面向量化初学者的 A 股全栈研究项目：用 AKShare 采集行情、财务、新闻与公告，用 OpenAI 兼容大模型把事件转换为结构化情绪分数，再做可解释选股排名和严格延迟信号的历史回测。

> 仅用于学习、研究和模拟回测。系统不包含券商接口，不会执行真实交易，也不构成投资建议。

## 现在能做什么

- 研究总览：股票池、日线、舆情数量、AI 分析覆盖率、领先评分和流水线状态。
- 行情财务：日 K、成交量、当日切片和按报告期保存的财务指标。
- AI 选股：行情动量、财务质量、舆情情绪三个可解释分项及综合排名。
- 舆情雷达：新闻/公告时间线、利好/中性/利空、置信度、摘要和判断理由。
- 策略实验室：可视化配置股票池、因子权重、窗口、门槛、持仓数量、手续费和滑点。
- 双因子回测：情绪 + 行情，强制信号延迟一根 K 线，输出资金曲线、基准、收益、回撤、夏普和换手率。
- 交易日历与指数基准：保存 A 股交易日，回测可使用沪深 300 等真实指数，不再默认用股票池等权收益冒充基准。
- 点时财务：报告期和真实公告日分开保存，评分日只能读取当时已经发布的指标。
- Walk-forward：滚动训练窗口选择参数，最终只拼接下一测试窗口的样本外收益。
- MySQL 任务队列：采集、AI 分析、质量检查和样本外实验由独立 Worker 执行，支持进度、重试和取消。
- 数据质量告警：检查 OHLC、价格跳变、交易日缺口、过期数据、点时财务/基准覆盖和情绪分数范围。
- 定时任务：可按 Cron 配置行情、舆情、评分、基础数据和质量检查；默认关闭，避免初次启动就请求外部数据。
- 演示模式：可生成明确标注的合成数据，不依赖实时源也能学习完整流程。

## 技术结构

```mermaid
flowchart LR
    A["AKShare<br/>行情 / 财务 / 新闻 / 公告"] --> B["FastAPI 数据流水线"]
    C["OpenAI 兼容 LLM<br/>DeepSeek 等"] --> D["结构化情绪分析"]
    B --> H["MySQL 持久化任务队列"]
    H --> I["独立 Worker"]
    I --> E["MySQL<br/>aq_ 前缀研究表"]
    D --> E
    E --> F["点时评分 / 回测 / Walk-forward / 质量规则"]
    F --> G["React + ECharts<br/>可视研究工作台"]
    E --> G
```

- 后端：Python、FastAPI、SQLAlchemy、pandas、APScheduler。
- 数据库：MySQL 为主；没有配置时可回退到本地 SQLite。
- 前端：React、TypeScript、Vite、ECharts。
- 大模型：直接调用 OpenAI Chat Completions 兼容接口；模型失败时回退到可复现的词典规则。
- 队列：数据库行锁认领，不要求额外部署 Redis；当前 MariaDB 兼容模式适合单 Worker。

## 五分钟启动

要求：PowerShell 7、64 位 Python 3.11+、Node.js 20+，以及一个可用的 MySQL 数据库。

```powershell
# 1. 安装依赖，并生成演示数据
pwsh -File scripts/setup.ps1 -SeedDemo

# 2. 同时启动 API 与网页
pwsh -File scripts/dev.ps1
```

打开：

- 网页：[http://127.0.0.1:5173](http://127.0.0.1:5173)
- API 文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

停止时在运行窗口按 `Ctrl+C`。

## 配置数据库与大模型

复制示例配置：

```powershell
Copy-Item .env.example .env
```

最重要的字段：

```dotenv
DATABASE_URL=mysql+pymysql://user:password@host:3306/database?charset=utf8mb4
LLM_ENABLED=true
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your-key
LLM_MODEL=deepseek-chat
```

本工作区还支持读取根目录、不会被 Git 提交的 `credentials.txt`：

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
model=deepseek-chat
```

所有项目表统一使用 `aq_` 前缀，因此可以安全复用一个已有数据库。真实密钥只能放在 `.env`、系统环境变量或 `credentials.txt`，这些文件已加入 `.gitignore`。

## 数据源

默认提供方是 [AKShare](https://github.com/akfamily/akshare)，当前接入：

| 数据 | AKShare 接口 | 说明 |
| --- | --- | --- |
| 全市场快照 | `stock_zh_a_spot_em` | 股票代码、名称、估值和市值等快照 |
| 日线行情 | `stock_zh_a_hist` | 东方财富前复权日线 |
| 日线降级 | `stock_zh_a_hist_tx` | 东方财富网络失败时自动切换腾讯 |
| 交易日历 | `tool_trade_date_hist_sina` | A 股历史与当年交易日 |
| 指数基准 | `index_zh_a_hist` | 失败时回退 `stock_zh_index_daily_tx` |
| 点时财务 | `stock_yjbb_em` | 使用“最新公告日期”作为真正可得日 |
| 财务指标 | `stock_financial_abstract_new_ths` | 失败时回退新浪宽表接口 |
| 个股新闻 | `stock_news_em` | 最近新闻、正文摘要、来源和 URL |
| 个股公告 | `stock_individual_notice_report` | 指定股票和日期区间公告 |

AKShare 是开源接口库，但它聚合的源站接口可能变更、限流或延迟。项目会保存来源、按组件隔离失败并保留降级路径；重要结论仍应与交易所公告或付费数据交叉核验。AKShare 官方也将其定位为学术研究工具并提示商业使用风险。

## 从数据到策略

### 1. AI 情绪分析

每条事件会得到：

```json
{
  "label": "利好",
  "score": 0.6,
  "confidence": 0.82,
  "summary": "不超过 80 字的摘要",
  "rationale": "判断理由"
}
```

模型提示词要求只基于输入文本、不补充外部事实、不提供买卖建议。调用失败时使用词典规则，数据库会记录实际模型名，避免把降级结果误认为大模型输出。

### 2. AI 选股排名

- 行情动量：20/60 日收益组合，并扣除年化波动惩罚。
- 财务质量：最新可得的 ROE、收入增长、归母净利润增长等指标。
- 舆情情绪：近 30 日事件按模型置信度和时间衰减加权。
- 综合分：三个 0–100 分项按页面权重加权。

排名是研究筛选器，不是收益概率。

### 3. 情绪 + 行情双因子回测

每个交易日只使用当日及之前发布的新闻；根据动量和滚动舆情选出符合门槛的前 N 只股票并等权。关键防泄漏规则：

```python
# T 日收盘后得到信号，T+1 日才持有。
applied_weights = targets.shift(1).fillna(0.0)
```

换仓日扣除 `turnover × (fee_rate + slippage_rate)`。基础策略定义就是“情绪 + 行情”双因子，因此回测不混入财务；选股排名中的质量因子只读取公告日不晚于评分日的点时财务。

### 4. 点时财务与指数基准

`aq_pit_financials` 同时保存 `report_date` 和 `available_at`。任何 `as_of=T` 的评分都带有 `available_at <= T` 条件。基础回测从 `aq_index_prices` 读取页面选择的指数；只有指数尚未同步时才回退股票池等权基准。

### 5. Walk-forward 样本外验证

每个滚动窗口分为训练段和紧随其后的测试段。动量窗口和舆情门槛只在训练段比较；选出的固定参数应用到测试段后，测试收益才进入最终资金曲线。数据库保存每个窗口的训练/测试日期、选择参数和双方绩效，方便审计。

## 真实数据工作流

1. 在“策略实验室”先把股票池缩小到 1–5 只。
2. 在“数据治理”同步交易日历、指数和点时财务。
3. 在“策略实验室”把行情、新闻、AI 分析和评分任务放入队列，并在“任务中心”观察进度。
4. 大模型情绪任务会消耗配置的 API 额度。
5. 设定样本期、指数基准和交易成本，运行历史回测。
6. 到“样本外验证”运行 Walk-forward，再到“数据治理”执行质量检查。
7. 扩大股票池前先检查告警、源站限制和数据库容量。

## 定时任务

默认关闭。确认股票池后在 `.env` 中启用：

```dotenv
SCHEDULER_ENABLED=true
PRICE_SYNC_CRON=20 18 * * 1-5
NEWS_SYNC_CRON=0 */2 * * *
SCORE_CRON=40 19 * * 1-5
INFRASTRUCTURE_CRON=10 8 * * 6
DATA_QUALITY_CRON=10 20 * * 1-5
```

时间使用 `Asia/Shanghai`。开发模式的自动重载可能启动多个进程，不建议在 `--reload` 下开启调度器；正式运行请用单实例进程或把调度器拆成独立 Worker。

## 验证

```powershell
pwsh -File scripts/check.ps1
```

检查内容：Ruff、pytest、TypeScript 和 Vite 生产构建。当前 18 个后端测试重点覆盖：

- 信号必须延迟一个交易日；
- 未来发布的舆情不能影响过去；
- 手续费和滑点确实降低资金曲线；
- 动量与情绪衰减计算；
- 模型 JSON 与规则降级；
- 腾讯行情降级格式。
- 真实公告日点时可见性与指数接口降级；
- MySQL 队列优先级、取消和重试状态机；
- OHLC/交易日缺口质量规则；
- Walk-forward 最终曲线只包含测试窗口。

## 目录

```text
ai-quantitative-trading/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI 路由
│   │   ├── core/                # 配置与数据库
│   │   ├── services/            # 采集、情绪、评分、回测、调度
│   │   ├── worker.py            # MySQL 持久化任务 Worker
│   │   ├── models.py            # aq_ 数据表
│   │   └── main.py
│   ├── scripts/seed_demo.py
│   └── tests/
├── frontend/src/
│   ├── components/
│   └── pages/                    # 含样本外、任务中心和数据治理
├── scripts/                     # PowerShell 安装、启动、检查
├── .env.example
└── README.md
```

## 已知边界

- 免费网页数据不是交易所级低延迟数据，不适合高频或真实下单。
- 新闻“当日最近 100 条”等限制由源站接口决定，不能替代完整历史新闻库。
- 当前回测按收盘到收盘近似执行，未建模涨跌停、停牌、无法成交、印花税差异和容量冲击。
- 免费业绩报表接口按报告期抓取全市场后过滤股票池，建议放入队列并控制回溯季度数量。
- 当前远程 MariaDB 使用普通行锁认领任务；默认单 Worker，增加多个 Worker 会安全串行等待但吞吐不会线性提升。
- 合成演示数据只用于验证界面和流程，绝不能用于评价策略有效性。
- 情绪模型会犯错；应抽样复核，并保存模型版本、提示词和原文链接。

后续适合继续补充前复权/后复权一致性、行业与风格暴露、停牌和涨跌停成交约束、数据快照版本及研究实验追踪；仍不建议直接连接实盘。
