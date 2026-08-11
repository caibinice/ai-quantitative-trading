# AI 量化研究舱

一个面向量化初学者的 A 股全栈研究项目：用 AKShare 采集行情、财务、新闻与公告，用 OpenAI 兼容大模型把事件转换为结构化情绪分数，再做可解释选股排名和严格延迟信号的历史回测。

> 仅用于学习、研究和模拟回测。系统不包含券商接口，不会执行真实交易，也不构成投资建议。

[项目展示网页](https://101.132.78.217/quant/)

## 现在能做什么

- 研究总览：股票池、日线、舆情数量、AI 分析覆盖率、领先评分和流水线状态。
- 行情财务：日 K、成交量、当日切片和按报告期保存的财务指标。
- AI 选股：行情动量、财务质量、舆情情绪三个可解释分项及综合排名。
- 舆情雷达：新闻/公告时间线、利好/中性/利空、置信度、摘要和判断理由。
- 策略实验室：可视化配置股票池、因子权重、窗口、门槛、持仓数量、手续费和滑点。
- 双因子回测：情绪 + 行情，强制信号延迟一根 K 线，输出资金曲线、基准、收益、回撤、夏普和换手率。
- 定时任务：可按 Cron 配置行情、舆情和评分流水线；默认关闭，避免初次启动就请求外部数据。
- 演示模式：可生成明确标注的合成数据，不依赖实时源也能学习完整流程。

## 技术结构

```mermaid
flowchart LR
    A["AKShare<br/>行情 / 财务 / 新闻 / 公告"] --> B["FastAPI 数据流水线"]
    C["OpenAI 兼容 LLM<br/>DeepSeek 等"] --> D["结构化情绪分析"]
    B --> E["MySQL<br/>aq_ 前缀表"]
    D --> E
    E --> F["因子评分与双因子回测"]
    F --> G["React + ECharts<br/>可视研究工作台"]
    E --> G
```

- 后端：Python、FastAPI、SQLAlchemy、pandas、APScheduler。
- 数据库：MySQL 为主；没有配置时可回退到本地 SQLite。
- 前端：React、TypeScript、Vite、ECharts。
- 大模型：直接调用 OpenAI Chat Completions 兼容接口；模型失败时回退到可复现的词典规则。

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

换仓日扣除 `turnover × (fee_rate + slippage_rate)`。财务数据目前没有“原始披露可得时间”字段，所以历史回测刻意不使用财务因子；财务只用于当期排名，避免把后来公布的数据带回过去。

## 真实数据工作流

1. 在“策略实验室”先把股票池缩小到 1–5 只。
2. 点击“同步 AKShare 数据”。行情、财务、新闻和公告分别提交，单一源站失败不会回滚其他结果。
3. 点击“大模型情绪分析”。会消耗配置的大模型 API 额度。
4. 点击“生成 AI 评分”。
5. 设定样本期、交易成本，运行历史回测。
6. 扩大股票池前先检查任务状态、源站限制和数据库容量。

## 定时任务

默认关闭。确认股票池后在 `.env` 中启用：

```dotenv
SCHEDULER_ENABLED=true
PRICE_SYNC_CRON=20 18 * * 1-5
NEWS_SYNC_CRON=0 */2 * * *
SCORE_CRON=40 19 * * 1-5
```

时间使用 `Asia/Shanghai`。开发模式的自动重载可能启动多个进程，不建议在 `--reload` 下开启调度器；正式运行请用单实例进程或把调度器拆成独立 Worker。

## 验证

```powershell
pwsh -File scripts/check.ps1
```

检查内容：Ruff、pytest、TypeScript 和 Vite 生产构建。测试重点覆盖：

- 信号必须延迟一个交易日；
- 未来发布的舆情不能影响过去；
- 手续费和滑点确实降低资金曲线；
- 动量与情绪衰减计算；
- 模型 JSON 与规则降级；
- 腾讯行情降级格式。

## 目录

```text
ai-quantitative-trading/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI 路由
│   │   ├── core/                # 配置与数据库
│   │   ├── services/            # 采集、情绪、评分、回测、调度
│   │   ├── models.py            # aq_ 数据表
│   │   └── main.py
│   ├── scripts/seed_demo.py
│   └── tests/
├── frontend/src/
│   ├── components/
│   └── pages/
├── scripts/                     # PowerShell 安装、启动、检查
├── .env.example
└── README.md
```

## 已知边界

- 免费网页数据不是交易所级低延迟数据，不适合高频或真实下单。
- 新闻“当日最近 100 条”等限制由源站接口决定，不能替代完整历史新闻库。
- 当前回测按收盘到收盘近似执行，未建模涨跌停、停牌、无法成交、印花税差异和容量冲击。
- 合成演示数据只用于验证界面和流程，绝不能用于评价策略有效性。
- 情绪模型会犯错；应抽样复核，并保存模型版本、提示词和原文链接。

下一步适合增加：交易日历、点时财务数据、指数基准、Walk-forward 样本外测试、任务队列和数据质量告警，而不是直接接实盘。
