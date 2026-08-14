# AI 量化研究舱

**[English](./README.md) | 简体中文**

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](./LICENSE)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Research_API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Research_UI-61DAFB?logo=react&logoColor=111827)

一个面向量化初学者的 A 股全栈研究项目：用 Tushare Pro 优先采集结构化行情与财务数据，用 AKShare、东方财富和巨潮资讯补充新闻公告及故障降级，再用 OpenAI 兼容大模型把事件转换为结构化情绪分数，完成可解释选股排名和严格延迟信号的历史回测。

> 仅用于学习、研究和模拟回测。系统不包含券商接口，不会执行真实交易，也不构成投资建议。

**[在线体验](https://caibinice.com/quant/) · [项目设计文章](https://caibinice.com/articles/ai-quant-system) · [English README](./README.md)**

<p align="center">
  <a href="https://caibinice.com/quant/">
    <img src="docs/images/dashboard.png" alt="AI 量化研究舱研究总览" width="100%">
  </a>
  <br>
  <sub>研究总览把股票池、行情、舆情、AI 分析覆盖率、排名和流水线状态集中在一个可追溯工作台中。</sub>
</p>

## 界面预览

| 可解释 AI 选股 | 策略实验室 |
| --- | --- |
| [![AI 选股排名](docs/images/ai-rankings.png)](https://caibinice.com/quant/rankings) | [![策略实验室](docs/images/strategy-lab.png)](https://caibinice.com/quant/strategy) |
| 行情动量、财务质量和舆情情绪拆分展示，保留评分日期、来源和异常提示。 | 在同一页面配置股票池、因子权重、成本、执行延迟与回测区间。 |

| 学习学院 | 项目设计文章 |
| --- | --- |
| [![学习学院](docs/images/learning-academy.png)](https://caibinice.com/quant/learn) | [![项目设计文章](docs/images/project-story.png)](https://caibinice.com/articles/ai-quant-system) |
| 五阶段、11 章、33 个知识详情，把项目源码变成一条可操作的量化学习路线。 | 阅读《从工程闭环到可信研究：我的 AI 量化系统》，了解为什么项目优先构建可复查证据链。 |

## 现在能做什么

- 研究总览：股票池、日线、舆情数量、AI 分析覆盖率、领先评分和流水线状态。
- 行情财务：日 K、成交量、当日切片和按报告期保存的财务指标。
- AI 选股：行情动量、财务质量、舆情情绪三个可解释分项及综合排名。
- 舆情雷达：新闻/公告时间线、利好/中性/利空、置信度、摘要和判断理由；自动流水线默认每 6 小时运行，任务中心修改间隔后即时生效。
- 舆情事件去重：完全相同记录使用内容哈希拦截；跨来源转载综合规范化链接、标题、正文梗概和 72 小时时窗按 90% 阈值去重，发布时间相隔不超过 72 小时统一视为相近，不再额外降权。同一事件涉及多只股票时仍为每只股票保留独立研判，“全部股票”视图仅合并展示并列出关联代码。
- 策略实验室：可视化配置股票池、因子权重、窗口、门槛、持仓数量、手续费和滑点。
- 动态股票池：默认 15 只跨行业大盘股，可用数量控件在 1–30 只间自动扩缩，也可直接编辑代码。
- 明暗主题：顶部一键切换明亮/暗黑风格，主题会保存在浏览器，ECharts 图表同步换色。
- 双因子回测：情绪 + 行情，强制信号延迟一根 K 线，输出资金曲线、基准、收益、回撤、夏普和换手率。
- 交易日历与指数基准：保存 A 股交易日，回测可使用沪深 300 等真实指数，不再默认用股票池等权收益冒充基准。
- 点时财务：报告期和真实公告日分开保存，评分日只能读取当时已经发布的指标。
- Walk-forward：滚动训练窗口选择参数，最终只拼接下一测试窗口的样本外收益。
- MySQL 任务队列：采集、AI 分析、质量检查和样本外实验由独立 Worker 执行，支持进度、重试和取消。
- 数据质量告警：检查 OHLC、价格跳变、交易日缺口、过期数据、点时财务/基准覆盖和情绪分数范围。
- 学习学院：五阶段 11 章、33 个可点击知识详情；从股票/K 线零基础进入 Python 时间序列、因子、舆情、Walk-forward 和毕业研究。每个知识点都有白话术语、误区的风险原因/正确做法/自查、分步跟练、代码逐段解释、预期输出和验证清单；另配 11 份可下载教学 CSV 与 11 个离线实验，并链接官方教程、论文和可追溯的量化从业经验。进度同步到 MySQL，可跨设备继续、取消勾选或一键重置。
- 定时任务：行情、评分、基础数据和质量检查按 Cron 运行；新闻公告 + AI 情绪流水线使用 MySQL 持久化间隔配置，默认每 6 小时运行。任务中心也提供“立即执行全流程”，严格串行执行新闻/公告抓取、去重、AI 分析和选股评分，不重复抓取行情与财务。
- 演示模式：可生成明确标注的合成数据，不依赖实时源也能学习完整流程。

## 技术结构

```mermaid
flowchart LR
    A["Tushare Pro<br/>行情 / 复权 / 财务 / 日历 / 指数"] --> B["FastAPI 混合数据流水线"]
    J["AKShare + 公开源<br/>新闻 / 公告 / 自动降级"] --> B
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
- 生产部署：Nginx + systemd + Python venv，不使用 Docker；前端在本机构建后上传，适合 2 核 2GB 小服务器。

## 五分钟启动

要求：PowerShell 7、64 位 Python 3.11+、Node.js 20+，以及一个可用的 MySQL 数据库。

完整生产版本当前固定使用 `main` 分支。单独开发
本项目时只需克隆该分支，并把私有 `credentials.txt` 放在本仓库根目录；
不要求同时下载 `ai-blog` 或其他展示项目。

```powershell
# 1. 安装依赖，并生成演示数据
pwsh -File scripts/setup.ps1 -SeedDemo

# 2. 同时启动 API 与网页
pwsh -File scripts/dev.ps1
```

打开：

- 网页：[http://127.0.0.1:5173/quant/](http://127.0.0.1:5173/quant/)
- 学习手册：[http://127.0.0.1:5173/quant/learn](http://127.0.0.1:5173/quant/learn)
- API 文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

停止时在运行窗口按 `Ctrl+C`。

## 学习手册怎么用

打开 `/quant/learn` 是总路线页。建议从新增的“股票与 K 线零基础”开始：先阅读“教材正文 → 名词翻译 → 逐步例题 → 流程图”，再点击“知识梗概”卡片进入独立详情页，沿“心智模型 → 深度讲解 → 流程图 → 项目例子 → 常见误区 → 动手练习”学习。对应源码和 Demo 可直接下载。回到章节后运行 Demo、勾选 Checklist、完成 3 题小测验，并用页面底部的“上一章 / 下一章”连续学习。

| 阶段 | 章节 | 目标 |
| --- | --- | --- |
| 1 建立地图 | 股票与 K 线零基础；量化地图；项目导览 | 看懂行情基础、分清概念并读懂研究闭环 |
| 2 掌握数据语言 | Python 迁移；NumPy/pandas | 从 Java/JS/MATLAB 迁移到科学 Python |
| 3 构建可信策略 | 行情财务；因子回测 | 掌握收益风险、时点、成本与信号延迟 |
| 4 加入 AI 与验证 | 舆情大模型；Walk-forward | 把文本变成可审计因子并检查过拟合 |
| 5 完成研究系统 | 工程治理；毕业项目 | 独立交付可复现、可证伪的双因子研究 |

进度保存逻辑：

- 浏览器先保留本地缓存，API 可用时同步到 MySQL 表 `aq_learning_progress`。
- 第一次从旧版本升级时，如果 MySQL 尚无记录，会把本地已有进度迁移到远程。
- 换电脑或浏览器登录同一个站点后，会读取 MySQL 中的 Checklist 和测验最高分。
- Checklist 可以再次点击取消；章节底部可返回上一章；总路线页“重置进度”会同时清空 MySQL 与本地缓存。
- 页面显示“已同步到 MySQL”才表示远程保存完成；断网时会显示“离线缓存”。

Demo 也可以在项目根目录直接运行：

```powershell
.\.venv\Scripts\python.exe learning\examples\00_kline_basics.py
.\.venv\Scripts\python.exe learning\examples\01_python_bridge.py
.\.venv\Scripts\python.exe learning\examples\02_pandas_timeseries.py
.\.venv\Scripts\python.exe learning\examples\03_signal_delay.py
.\.venv\Scripts\python.exe learning\examples\04_sentiment_factor.py
.\.venv\Scripts\python.exe learning\examples\05_walk_forward.py
```

## 远程一键部署

当前生产方案面向 2 核 2GB Linux 服务器，使用 Nginx、单进程 FastAPI、轻量常驻 Worker 和 systemd。Worker 空闲时只加载队列层；处理 pandas/数据采集重任务后空闲 30 秒会退出，再由 systemd 拉起一个干净的轻量进程，避免长期占用内存。服务器无需安装 Node.js，也不运行 Docker。

先按 `credentials.example.txt` 在不会提交到 Git 的项目
`credentials.txt` 中配置。它既可以使用无前缀项目段，也可以直接复制含
`quant.*` 段的通用凭据文件。只有项目文件不存在且兄弟目录刚好存在博客
凭据时，才会使用兼容回退：

```ini
[remote.ssh]
host=caibinice.com
port=22
user=普通 SSH 用户
password=SSH 密码
root_password=可通过 su 使用的 root 密码

```

首次发布从本项目 `credentials.txt` 的 `[platform.action] password` 读取操作
口令，脚本会生成并保存一个不提交 Git 的签名密钥；后续发布复用
`.deploy/action-auth.json`。进程环境变量仍可作为临时覆盖：

```powershell
$env:AI_PLATFORM_ACTION_PASSWORD='<your-operation-password>'
pwsh -File scripts/deploy.ps1
Remove-Item Env:AI_PLATFORM_ACTION_PASSWORD
```

它会依次完成：

1. 运行 Ruff、pytest 和前端生产构建；
2. 只打包源码与 `frontend/dist`，不会上传 `.env`、`credentials.txt` 或 `.deploy`；
3. 在服务器安装原生 Python 3.11 与 Nginx，创建 1GB 低优先级防 OOM swap，并把应用隔离在 `/quant`；
4. 写入 systemd API/Worker 服务并连接 `credentials.txt` 中的同一个远程 MySQL；
5. 为 `caibinice.com` 和 `www.caibinice.com` 申请 Let’s Encrypt 证书，80 自动跳转 443；
6. 每天在北京时间 03:17 和 12:17 检查证书续期，成功后热加载 Nginx；
7. 执行 API 健康检查；失败时自动恢复上一个 release。

不要停用 `ai-quant-cert-renew.timer` 太久。操作口令与短期签名密钥保存在本机、
不提交 Git 的：

```text
.deploy/action-auth.json
```

独立构建、部署和提交均从本仓库执行：

```powershell
pwsh -File scripts/deploy.ps1 -BuildOnly
pwsh -File scripts/deploy.ps1
pwsh -File scripts/github-push.ps1 `
  -Message 'fix: describe the change' `
  -Files @('path/to/changed-file')
```

GitHub 脚本只读取本仓库 `credentials.txt` 的 `[github]`，并只在当前进程
使用 `127.0.0.1:20808` 代理和 token，不修改 remote URL 或全局 Git 配置。

浏览器访问 `https://caibinice.com/quant/` 可直接查看行情、研究结果和
课程。采集、AI 分析、评分、回测、任务、Walk-forward、数据质量和自动化
配置等写操作会弹出密码框，由 FastAPI 验证后签发 30 分钟令牌；密码不写
入前端存储。APScheduler 和 Worker 直接调用服务层，不经过网页接口，因此
后台自动调度无需验证。API 只监听服务器 `127.0.0.1:8000`。

生产构建关闭 source map，将 React、ECharts 等拆为 `vendor-*`，只对自有
业务 chunk 做保守混淆。混淆仅增加直接阅读成本，不能代替后端鉴权。

常用运维命令：

```powershell
pwsh -File scripts/status.ps1   # 查看服务和日志
pwsh -File scripts/restart.ps1  # 一键重启
pwsh -File scripts/stop.ps1     # 停止网页、API、Worker 和续期定时器
pwsh -File scripts/start.ps1    # 一键恢复
```

服务器只需要安全组放行 80 和 443；8080 不使用。发布文件位于 `/opt/ai-quantitative-trading`，保留最近 5 个 release；应用密钥只保存在服务器 `shared/app.env`。

博客留言与 AI 动态复用这个 FastAPI 服务。公开接口位于
`/api/blog/comments` 与 `/api/blog/news`；邮箱只保存在
`aq_blog_comments`，不会出现在公开响应。管理接口使用独立 Bearer
令牌，发布脚本会生成至少 32 字节随机值，并同步保存到不提交 Git 的
`.deploy/blog-admin.json` 与相邻博客仓库的同名文件。浏览器管理页只把
令牌放进当前标签页的 `sessionStorage`。AI 动态聚合 OpenAI、Google
DeepMind、Hugging Face、Google AI、MIT AI、NVIDIA Developer 与 AWS
Machine Learning 的官方订阅源；服务端每 6 小时更新一次持久化快照，
仅返回最近 7 天内容。`/api/blog/news` 支持 `page`、`pageSize` 和
`source` 参数，供博客进行分页与来源筛选。

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
LLM_API_KEY_BACKUP=your-backup-key
LLM_MODEL=deepseek-v4-flash
LLM_THINKING_ENABLED=true
LLM_REASONING_EFFORT=max
BLOG_ADMIN_TOKEN=replace-with-at-least-32-random-bytes
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
api-key-backup=your-backup-key
model=deepseek-v4-flash

[tushare]
token=your-tushare-token
```

若由兄弟项目 `ai-blog` 统一维护凭证，运行
`D:\codes\ai-blog\scripts\sync-shared-credentials.ps1` 后会把本段保存为
`[quant.tushare]`。量化项目本地开发和发布脚本都能识别这个带作用域的段；
Token 不会进入 release、前端构建或 Git。

所有项目表统一使用 `aq_` 前缀，因此可以安全复用一个已有数据库。真实密钥只能放在 `.env`、系统环境变量或 `credentials.txt`，这些文件已加入 `.gitignore`。

## 数据源

### Tushare Pro（结构化主数据源）

本项目会在配置 Token 后自动启用 Tushare，不需要安装额外 SDK，后端通过
官方 HTTP API 调用。对当前 2000 积分账号已做只读实测：

| 数据 | Tushare API | 当前用途 |
| --- | --- | --- |
| 股票基础信息 | `stock_basic` | 股票代码、名称、行业和市场 |
| A 股日线 | `daily` | 未复权 OHLCV 原始行情 |
| 复权因子 | `adj_factor` | 与日线合并生成前复权价格 |
| 每日指标 | `daily_basic` | 换手率等日频指标 |
| 交易日历 | `trade_cal` | 开市/休市状态，按十年分段同步 |
| 指数日线 | `index_daily` | 沪深 300 等回测基准 |
| 财务指标 | `fina_indicator` | 近六年 ROE、毛利率、收入/利润同比等 |
| 利润表 | `income` | 近六年收入、营业利润、利润总额、归母净利润 |
| 资产负债表 | `balancesheet` | 近六年总资产、总负债、归母权益 |
| 现金流量表 | `cashflow` | 近六年经营/投资/筹资现金流及期末现金 |

前复权计算为 `原始价格 × 当日复权因子 ÷ 区间末复权因子`；成交额从
Tushare 的“千元”统一换算成数据库使用的“元”。每条记录保留
`source=tushare-pro`，页面会显示真实来源。财务数据同时保留报告期和公告日，
AI 质量评分只会读取评分日当时已经公告的数据。

实测账号还可以访问 `stk_limit`、`moneyflow`、`dividend` 和
`index_weight`。这些属于后续可增加的涨跌停、资金流、分红和指数成分模块，
当前没有为了“数据多”而直接混入选股分数。`ths_daily` 需要更高积分；`news`
和 `anns_d` 返回独立权限限制，不包含在 2000 积分里。

调用层按 2000 积分对应的 200 次/分钟额度设置了 0.35 秒最小间隔；日线、
财务、日历或指数若请求失败或返回空数据，会按组件自动降级到 AKShare，
不会把 Token、请求体或密钥写入错误信息。

官方说明：
[数据接口目录](https://tushare.pro/document/2)、
[积分权限](https://tushare.pro/document/2?doc_id=290)、
[日线行情](https://tushare.pro/document/2?doc_id=27)、
[财务指标](https://tushare.pro/document/2?doc_id=79)、
[新闻通讯](https://tushare.pro/document/2?doc_id=143)、
[上市公司公告](https://tushare.pro/document/2?doc_id=176)。

### AKShare 与公开源（舆情和自动降级）

| 数据 | AKShare 接口 | 说明 |
| --- | --- | --- |
| 全市场快照 | `stock_zh_a_spot_em` | 股票代码、名称、估值和市值等快照 |
| 日线行情降级 | `stock_zh_a_hist` | Tushare 不可用时使用东方财富前复权日线 |
| 日线降级 | `stock_zh_a_hist_tx` | 东方财富网络失败时自动切换腾讯 |
| 交易日历降级 | `tool_trade_date_hist_sina` | A 股历史与当年交易日 |
| 指数基准 | `index_zh_a_hist` | 失败时回退 `stock_zh_index_daily_tx` |
| 点时财务 | `stock_yjbb_em` | 使用“最新公告日期”作为真正可得日 |
| 财务指标 | `stock_financial_abstract_new_ths` | 失败时回退新浪宽表接口 |
| 个股新闻 | `stock_news_em` | 最近新闻、正文摘要、来源和 URL |
| 个股公告 | `stock_individual_notice_report` | 指定股票和日期区间公告 |
| 法定公告交叉源 | `stock_zh_a_disclosure_report_cninfo` | 巨潮资讯披露公告，与东方财富并行采集去重 |

AKShare 是开源接口库，但它聚合的源站接口可能变更、限流或延迟。项目会保存来源、按组件隔离失败并保留降级路径；重要结论仍应与交易所公告或付费数据交叉核验。巨潮资讯通过 [AKShare 的公开接口封装](https://akshare.akfamily.xyz/data/stock/stock.html) 接入，不需要额外注册。

舆情雷达页面同时列出候选数据源和注册要求：

- 东方财富个股新闻、东方财富公告、巨潮资讯公告：当前已接入，无需额外账号。
- [Tushare Pro 新闻通讯](https://tushare.pro/document/2?doc_id=143)：Token 已配置，但新闻仍需单独开通权限；2000 积分不包含该接口，因此不作为当前舆情依赖。
- [GDELT DOC 2.0](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)：旧版全文检索接口无需 Key；新版 GDELT Cloud 开发 API 需要账号/API Key。国际覆盖广，但 A 股中文实体映射和噪声仍需评估，因此暂列候选而未默认采集。

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

模型提示词要求只基于输入文本、不补充外部事实、不提供买卖建议。默认使用 `deepseek-v4-flash` Thinking Mode（`thinking.type=enabled`、`reasoning_effort=max`）；主 Key 在配额不足、鉴权失败、超时或服务端不可用时自动尝试备用 Key，两者均失败才使用词典规则。数据库会记录实际模型名，避免把降级结果误认为大模型输出。参数用法参见 [DeepSeek Thinking Mode 官方文档](https://api-docs.deepseek.com/guides/thinking_mode)。

### 2. AI 选股排名

- 行情动量：5/20/60 日收益组合，并扣除年化波动惩罚；真实序列中的 demo 行会被排除，超过 35% 的异常跳变会阻断动量并回退为中性。
- 财务质量：只使用最新可得的 ROE、收入同比、净利润同比和毛利率等可比比例；营业收入、净利润绝对金额不会再被错误当成百分比分数。
- 舆情情绪：近 30 日事件按模型置信度和时间衰减加权。
- 综合分：三个 0–100 分项按页面权重加权。

排名是研究筛选器，不是收益概率。排名页会直接显示行情截止日期、来源、5/20/60 日收益、波动率、舆情条数和异常警告，避免把数据污染包装成“AI 看多”。排名和行情、舆情、数据治理页默认只读取策略实验室当前股票池；保存新增代码后，缺少行情的股票会自动创建同步任务。

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

1. 默认股票池为 15 只真实 A 股代码；第一次验证免费源时可先缩小到 3–5 只，确认稳定后再恢复 15 只或继续扩展。
2. 在“数据治理”同步交易日历、指数和点时财务。
3. 在“策略实验室”保存股票池后，到“任务中心”点击“立即执行全流程”，按顺序完成舆情抓取、去重、AI 分析和评分；下方四个快捷按钮只是独立单项任务，不会自动串联。
4. 大模型情绪任务会消耗配置的 API 额度。
5. 设定样本期、指数基准和交易成本，运行历史回测。
6. 到“样本外验证”运行 Walk-forward，再到“数据治理”执行质量检查。
7. 扩大股票池前先检查告警、源站限制和数据库容量。

## 定时任务

开发环境默认关闭。确认股票池后在 `.env` 中启用：

```dotenv
SCHEDULER_ENABLED=true
PRICE_SYNC_CRON=20 18 * * 1-5
SCORE_CRON=40 19 * * 1-5
INFRASTRUCTURE_CRON=10 8 * * 6
DATA_QUALITY_CRON=10 20 * * 1-5
```

调度时间使用 `Asia/Shanghai`。数据库内部任务时间保存为 UTC，API 使用显式 `Z`；中国新闻/公告源时间使用显式 `+08:00`；前端无论从哪个时区访问，都固定格式化成北京时间并标注。新闻公告、去重、AI 情绪分析和选股评分组成一个严格串行的队列任务，默认为每 6 小时执行一次；间隔和启停状态保存在 `aq_automation_settings`，只在“任务中心”配置 1–48 小时，保存后 APScheduler 立即重新排期，不需要重启。任务中心的“立即执行全流程”会手动创建同一类流水线任务；若已有一项正在排队或运行，系统会复用现有任务，避免重复消耗额度。开发模式的自动重载可能启动多个进程，不建议在 `--reload` 下开启调度器；远程轻量部署默认开启单实例调度器，调度器只把任务放入 MySQL，独立 Worker 负责执行。

## 验证

```powershell
pwsh -File scripts/check.ps1
```

检查内容：Ruff、pytest、ESLint、TypeScript 和 Vite 生产构建。后端测试重点覆盖：

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
- 学习手册中的 6 个 Python Demo 均可独立运行。
- 自动舆情配置默认 6 小时并持久化到 MySQL；
- DeepSeek Thinking 请求和主/备用 Key 回退；
- 学习源码下载白名单、秘密文件与路径穿越拦截。

启动本地 API 和前端后，还可以执行真实浏览器回归：

```powershell
Set-Location frontend
npm run test:e2e
```

Playwright 会验证明亮主题关键页面、动态页签标题、全部 11 章/33 个知识详情、源码下载、舆情标签配色和自动化配置。

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
├── learning/                     # 学习手册、毕业模板和 6 个可运行实验
├── docs/images/                  # README 使用的线上站点截图
├── deploy/                       # Nginx、systemd 和远程安装模板
├── scripts/                      # 本地开发、检查及一键远程运维
├── .env.example
├── README.md                     # English documentation
└── README_CN.md                  # 简体中文说明
```

## 已知边界

- 免费网页数据不是交易所级低延迟数据，不适合高频或真实下单。
- 新闻“当日最近 100 条”等限制由源站接口决定，不能替代完整历史新闻库。
- 当前回测按收盘到收盘近似执行，未建模涨跌停、停牌、无法成交、印花税差异和容量冲击。
- 免费业绩报表接口按报告期抓取全市场后过滤股票池，建议放入队列并控制回溯季度数量。
- 当前远程 MariaDB 使用普通行锁认领任务；默认单 Worker，增加多个 Worker 会安全串行等待但吞吐不会线性提升。
- 页面公开，敏感网页操作使用后端短期令牌；若未来开放多人协作，需要升级为账号、RBAC 和审计系统。
- 域名证书依赖 systemd timer 自动续期；更换域名或 DNS 后需要重新发布并签发证书。
- 合成演示数据只用于验证界面和流程，绝不能用于评价策略有效性。
- 情绪模型会犯错；应抽样复核，并保存模型版本、提示词和原文链接。

后续适合继续补充前复权/后复权一致性、行业与风格暴露、停牌和涨跌停成交约束、数据快照版本及研究实验追踪；仍不建议直接连接实盘。
