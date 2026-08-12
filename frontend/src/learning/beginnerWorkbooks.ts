export interface PitfallDetail {
  why: string
  correction: string
  selfCheck: string
}
export interface ConceptCoach {
  focus: string
  pitfallDetails: PitfallDetail[]
  practiceEvidence: string
  challenge: string
}

export interface ChapterLab {
  title: string
  goal: string
  datasetPath: string
  datasetDescription: string
  scriptPath: string
  command: string
  steps: Array<{ title: string; action: string; expected: string }>
  codeWalkthrough: Array<{ code: string; explanation: string }>
  expectedOutput: string[]
  verification: string[]
}

export interface PublicReading {
  title: string
  provider: string
  url: string
  takeaway: string
  kind: '官方教程' | '论文' | '从业者经验'
}

export interface ChapterWorkbook {
  beginnerNote: string
  plainWords: Array<{ term: string; translation: string; projectUse: string }>
  concepts: ConceptCoach[]
  lab: ChapterLab
  readings: PublicReading[]
}

export const beginnerWorkbooks: Record<string, ChapterWorkbook> = {
  'market-basics': {
    beginnerNote: '这一章不要求你预测涨跌。目标只是把行情页上的每个数字翻译成人话，并能检查一行行情是否自洽。先会读数据，再谈指标。',
    plainWords: [
      { term: '证券', translation: '可以证明某种财产权利的凭证；股票是其中一种。', projectUse: '股票代码和名称来自 aq_stocks。' },
      { term: '盘口', translation: '当前尚未成交的买卖报价队列，不是未来价格。', projectUse: '本项目暂不使用实时盘口，只在回测中用滑点近似成交差异。' },
      { term: 'OHLCV', translation: '一个周期的开、高、低、收、成交量。', projectUse: '行情页 K 线与 aq_daily_prices 的核心字段。' },
      { term: '复权', translation: '把分红送股造成的机械断层调整成可比较序列。', projectUse: '动量计算必须统一使用同一种复权口径。' },
      { term: '基准', translation: '用来回答“是不是市场普涨”的参照组。', projectUse: '项目使用沪深 300 与策略同区间比较。' },
    ],
    concepts: [
      {
        focus: '先确认“买的是什么、价格怎样成交、拿什么比较”，不要把股票当成只会上涨的数字。',
        pitfallDetails: [
          { why: '股票本金没有存款保险，公司经营和市场估值变化都可能造成永久损失。', correction: '先写可承受损失、持有期限和基准，再讨论收益。', selfCheck: '若价格下跌 30%，你能说出是市场、行业还是公司风险吗？' },
          { why: '牛市中随便持有也可能赚钱，只和 0% 比会把市场收益误认成选股能力。', correction: '股票池偏大盘时至少同步比较沪深 300 的同区间收益和回撤。', selfCheck: '策略赚 8%、基准赚 15% 时，你还会称它有效吗？' },
          { why: '最后价只代表上一笔成交；市价单可能连续吃掉多个卖档，平均成交更贵。', correction: '回测加入手续费和滑点，真实研究还要考虑成交量、涨跌停和停牌。', selfCheck: '你能分别说出市价单“不保证价格”和限价单“不保证成交”吗？' },
        ],
        practiceEvidence: '能在行情页指出股票、指数基准、收盘价和成交量，并用一句话解释它们的角色。',
        challenge: '把滑点从 0.05% 改成 0.20%，写下为什么交易频繁的策略受影响更大。',
      },
      {
        focus: '把一根 K 线还原成四个价格；颜色只是软件约定，OHLC 数值才是事实。',
        pitfallDetails: [
          { why: 'A 股软件常用红涨绿跌，海外软件可能相反；背颜色会在切换平台时读反。', correction: '始终比较 close 与 open，并检查图例。', selfCheck: '不看颜色，只给 O=10、C=9.8，你能判断实体方向吗？' },
          { why: '一根 K 线只压缩已经发生的一段交易，样本太少且没有基准概率。', correction: '把形态写成可计算规则，再统计足够多次的后续分布。', selfCheck: '你有多少次独立样本，扣费后相对基准是否仍有差异？' },
          { why: '“阳线”比较收盘与开盘；日收益比较收盘与前收盘，参照点不同。', correction: '同时计算 close/open-1 与 close/prev_close-1，并标清名称。', selfCheck: '高开低走时能否出现阴线但日收益仍为正？请给数值例子。' },
        ],
        practiceEvidence: '能手画实体和影线，并通过 low ≤ open/close ≤ high 验证 OHLC。',
        challenge: '在 CSV 新增一行“高开低走但相对昨收上涨”的数据，验证两个方向指标不同。',
      },
      {
        focus: '先统一价格口径，再用复利、波动和回撤描述风险；异常跳变优先当数据问题调查。',
        pitfallDetails: [
          { why: '两种口径在除权日前后的基准不同，混用会制造不存在的暴涨暴跌。', correction: '同一条计算链统一 raw、qfq 或 hfq，并保存数据来源。', selfCheck: '你能说明策略为何使用前复权、实盘成交为何仍参考原始价格吗？' },
          { why: '收益作用在不断变化的本金上，+10% 后 -10% 的结果是 -1%。', correction: '累计收益使用 (1+r) 连乘或资金曲线 cumprod。', selfCheck: '100 元跌 20% 后要涨多少才能回到 100 元？' },
          { why: '数十倍跳变更可能来自复权、单位、重复日期或演示数据，不应直接解释成动量。', correction: '先查 source、复权、交易日和相邻记录，再决定保留、修复或隔离。', selfCheck: '数据治理告警出现 extreme_return 时，你先看哪四项证据？' },
        ],
        practiceEvidence: '能从 CSV 手算逐日收益与累计收益，并解释最大回撤为何从历史高点计算。',
        challenge: '把第二天收盘改成 9.00，重新运行并比较累计收益与最大回撤。',
      },
    ],
    lab: {
      title: '实验 01：从 CSV 读懂第一组 K 线',
      goal: '验证 OHLC 关系，区分 K 线方向和日收益，并用复利得到区间收益。',
      datasetPath: 'learning/datasets/01_market_basics.csv',
      datasetDescription: '5 个教学交易日，包含 OHLC、成交量和前收盘价。',
      scriptPath: 'learning/labs/01_market_basics_lab.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\labs\\01_market_basics_lab.py',
      steps: [
        { title: '看表头', action: '下载 CSV，用文本编辑器找到 open/high/low/close/prev_close。', expected: '能指出 K 线方向用 open，日收益用 prev_close。' },
        { title: '原样运行', action: '在项目根目录执行命令，不先改代码。', expected: '最后一行是 LAB_OK，第一根显示“阳线”。' },
        { title: '核对一笔', action: '手算第一天 10.50/10.00-1。', expected: '得到 5.00%，与输出第一项一致。' },
        { title: '制造错误', action: '临时把某行 high 改得低于 close 后运行。', expected: 'assert 失败，说明 OHLC 校验抓住了矛盾。' },
      ],
      codeWalkthrough: [
        { code: 'rows = list(csv.DictReader(file))', explanation: '把每一行变成以列名为键的字典；先保留原始文本，再按用途转 float。' },
        { code: 'low <= min(open_price, close) <= max(open_price, close) <= high', explanation: '这是 K 线必须满足的顺序关系，不是在预测方向。' },
        { code: 'close / prev_close - 1', explanation: '以昨日收盘为分母得到可跨股票比较的日收益率。' },
        { code: 'cumulative *= 1 + daily_return', explanation: '每天在前一天本金上增长，体现复利而非简单相加。' },
      ],
      expectedOutput: ['rows=5 first_candle=阳线', 'daily_returns 第一项为 5.00%', 'compounded_return=8.80%', 'LAB_OK'],
      verification: ['输出行数与 CSV 数据行一致', '手算第一天收益与程序一致', '故意破坏 OHLC 后程序必须失败'],
    },
    readings: [
      { title: '证券基础知识专题', provider: '上海证券交易所投教', url: 'https://edu.sse.com.cn/college/required/basicinfo/index.shtml', takeaway: '先掌握股票、交易、收益风险和信息披露，再接触复杂策略。', kind: '官方教程' },
      { title: 'Order Types', provider: 'Investor.gov', url: 'https://www.investor.gov/introduction-investing/investing-basics/glossary/order-types', takeaway: '不同订单在成交速度、价格控制和能否成交之间有取舍。', kind: '官方教程' },
      { title: 'What is diversification?', provider: 'Investor.gov', url: 'https://www.investor.gov/additional-resources/information/youth/teachers-classroom-resources/what-diversification', takeaway: '分散不能消灭市场风险，但能减少单一标的失败对组合的冲击。', kind: '官方教程' },
    ],
  },

  'quant-map': {
    beginnerNote: '量化的第一产物不是买卖信号，而是一份别人可以重复、也可以否定的实验说明。你要练的是把模糊直觉拆成数据、规则和失败条件。',
    plainWords: [
      { term: '假设', translation: '一个可以被数据判错的“如果……那么……”句子。', projectUse: '策略配置把窗口、门槛和股票池固定下来。' },
      { term: '因子', translation: '给每只股票计算的可比较特征。', projectUse: '动量、财务质量、舆情都是分项因子。' },
      { term: '信号', translation: '把因子变成持有、空仓或权重的规则。', projectUse: '评分排序后选择 Top N。' },
      { term: '样本外', translation: '没有参与挑参数的后续数据。', projectUse: 'Walk-forward 只拼接测试窗口。' },
      { term: '可复现', translation: '同样输入、版本和步骤能得到同样结果。', projectUse: '任务参数和结果保存在 MySQL。' },
    ],
    concepts: [
      {
        focus: '把“我觉得会涨”改写成能失败的实验，先定义股票池、日期、规则、成本和判定线。',
        pitfallDetails: [
          { why: '一笔交易可能只是运气、市场普涨或承担了更大风险，不能估计规则的稳定性。', correction: '看多次独立样本、基准、回撤、成本和样本外结果。', selfCheck: '换一个起点或市场阶段，结论是否仍成立？' },
          { why: '知道答案后写原因会产生后见偏差，任何曲线都能编出故事。', correction: '运行前把假设、参数范围和失败线写入研究日志。', selfCheck: 'Git 或实验记录能证明规则早于结果存在吗？' },
          { why: '高收益可能伴随无法承受的回撤和换手，扣费后甚至消失。', correction: '至少同时报告收益、最大回撤、夏普、换手和基准。', selfCheck: '如果收益高但回撤 60%，你是否仍能执行到底？' },
        ],
        practiceEvidence: '产出一条包含股票池、因子、持有期、成本、基准和失败线的完整假设。',
        challenge: '把同一假设的成本提高五倍，预先写下你预计哪类策略最先失效。',
      },
      {
        focus: '分清 AI 辅助写代码、AI 抽取文本和机器学习预测，越接近交易决策越需要验证。',
        pitfallDetails: [
          { why: '模型自报 80% confidence 只是生成字段，不等于历史上 80% 判断正确。', correction: '用人工标注集按置信度分桶，检查真实准确率与覆盖率。', selfCheck: '0.8 置信度的 100 条样本实际对了多少？' },
          { why: '直接问“买不买”会混入模型常识、过时信息和不可审计的主观判断。', correction: '只让模型对给定文本做固定 Schema 的标签、分数、摘要和理由。', selfCheck: '输出是否能逐字段追溯到输入原文？' },
          { why: '模型、提示词或供应商变化会改变标签分布，历史因子不再同口径。', correction: '保存 model/prompt 版本，并用固定样本集做升级前后对比。', selfCheck: '你能复现三个月前某条新闻为什么得到该分数吗？' },
        ],
        practiceEvidence: '能列出本项目 AI 模块与确定性模块，并说明每种失败后如何降级。',
        challenge: '设计一个不用 LLM 也能运行的中性回退规则，并说明它会损失什么信息。',
      },
      {
        focus: 'Web3 是资产与基础设施范畴，量化是研究方法；两者可组合但互不等价。',
        pitfallDetails: [
          { why: '技术叠加不会自动保证数据真实、合约安全或策略有效。', correction: '分别审计链上来源、模型输出和交易规则。', selfCheck: '每个“可信”结论由哪项独立证据支持？' },
          { why: '链上市场连续运行，A 股有交易日、停牌和集合竞价，时间切分方法不同。', correction: '先定义市场日历、时区和可交易时点。', selfCheck: '周日新闻对 A 股最早何时可以形成可执行仓位？' },
          { why: 'Token 的池深、Gas 和滑点机制与交易所股票订单簿不同。', correction: '执行成本模型必须匹配具体市场微观结构。', selfCheck: '成本由券商佣金还是 AMM 价格冲击主导？' },
        ],
        practiceEvidence: '能用两列对比 A 股与链上资产的数据、日历、交易成本和主要风险。',
        challenge: '删掉所有“AI/Web3”营销词，只用输入、规则、输出重写项目介绍。',
      },
    ],
    lab: {
      title: '实验 02：样本内冠军为何样本外落后',
      goal: '同时观察样本内/外、换手、成本和基准，理解“赚钱一次”不等于假设成立。',
      datasetPath: 'learning/datasets/02_hypothesis_results.csv',
      datasetDescription: '三个候选规则的样本内外收益、换手、成本率和基准。',
      scriptPath: 'learning/labs/02_quant_hypothesis_lab.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\labs\\02_quant_hypothesis_lab.py',
      steps: [
        { title: '先猜结果', action: '只看 in_sample，写下你会选哪个规则。', expected: '大多数人会被 random_rule 的高收益吸引。' },
        { title: '运行脚本', action: '执行命令，让程序扣除 turnover × cost_rate。', expected: '三条规则都打印样本内外超额收益。' },
        { title: '比较反转', action: '找出样本内第一与样本外第一。', expected: '排名不同，随机规则样本外为负。' },
        { title: '写失败线', action: '规定“样本外超额≤0 即未通过”。', expected: 'momentum_20 和 random_rule 被明确判为未通过。' },
      ],
      codeWalkthrough: [
        { code: 'net = gross_return - turnover * cost_rate', explanation: '先从毛收益扣掉由换手产生的简化成本。' },
        { code: 'excess = net - benchmark_return', explanation: '再扣除同区间市场基准，避免把牛市当能力。' },
        { code: "results[name][period] = excess", explanation: '把同一规则的样本内外结果并排保存，不能只展示好的一段。' },
      ],
      expectedOutput: ['momentum_20 样本外超额为负', 'random_rule 样本外超额约 -7.08%', 'momentum_60 样本外略高于基准', 'LAB_OK'],
      verification: ['能解释为何 random_rule 样本内最好却不应采用', '失败条件在查看新结果前写好', '能说出成本和基准各解决什么偏差'],
    },
    readings: [
      { title: 'CS 7646: Machine Learning for Trading', provider: 'Georgia Tech', url: 'https://omscs.gatech.edu/cs-7646-machine-learning-trading', takeaway: '课程把金融数据、市场模拟与机器学习串成完整研究链，而不是只教模型。', kind: '官方教程' },
      { title: 'Backtesting Bias: Feels Good, Until You Blow Up', provider: 'Robot Wealth / Kris Longmore', url: 'https://robotwealth.com/backtesting-bias-feels-good-until-you-blow-up/', takeaway: '从业经验强调简单、可解释、面向稳健性的规则，并把样本内成绩视为偏乐观。', kind: '从业者经验' },
    ],
  },

  'project-tour': {
    beginnerNote: '把本项目当成你熟悉的 Java/JS 分层系统：页面提交命令，API 校验并入队，Worker 干重活，MySQL 保存证据。先学会追踪一条任务，不需要立刻读完所有 Python。',
    plainWords: [
      { term: 'Router', translation: '接收 HTTP 请求的 Controller 层。', projectUse: 'backend/app/api 下定义接口。' },
      { term: 'Schema', translation: '请求和响应的数据契约。', projectUse: 'Pydantic 会拒绝非法权重和日期。' },
      { term: 'Worker', translation: '脱离网页请求执行长任务的后台进程。', projectUse: '采集、AI 分析和回测在 Worker 中运行。' },
      { term: '幂等', translation: '重复执行不会不断制造重复数据。', projectUse: '行情使用业务唯一键，新闻使用哈希与近似去重。' },
      { term: '状态机', translation: '对象只能按允许的顺序改变状态。', projectUse: '任务从 queued 到 running，再到 success/failed。' },
    ],
    concepts: [
      {
        focus: '沿一次按钮点击追踪 React、API、Service、Repository、MySQL，不把业务逻辑塞在页面或路由。',
        pitfallDetails: [
          { why: '浏览器逻辑可被绕过且难以复用，批处理和测试会出现另一套实现。', correction: '回测、评分和去重放在后端 service，前端只配置和展示。', selfCheck: '不启动 React，后端测试仍能验证回测语义吗？' },
          { why: '外部抓取和 LLM 可能耗时几分钟，HTTP 会超时且刷新页面丢状态。', correction: 'API 只创建持久化任务，Worker 后台执行。', selfCheck: '浏览器关闭后任务是否还能继续并被重新查询？' },
          { why: '路由同时做校验、抓取、计算和写库会难测试、难重试、难定位。', correction: 'Router 管协议，Service 管业务，Repository 管数据访问。', selfCheck: '替换 AKShare 时需要改 React 或回测算法吗？' },
        ],
        practiceEvidence: '能从前端按钮找到 /tasks 接口，再找到 enqueue_task 与 Worker dispatch。',
        challenge: '给“运行质量检查”画一张五节点调用图，并在每个节点写输入输出。',
      },
      {
        focus: '理解任务不是一个 loading 动画，而是一条可恢复、有尝试次数和证据的数据库记录。',
        pitfallDetails: [
          { why: '网络重试若直接 insert，会让同一新闻多次计入情绪因子。', correction: '用业务唯一键、内容哈希或流水线活动任务检查保证幂等。', selfCheck: '重复点两次全流程按钮会得到两个并发任务吗？' },
          { why: '日志会轮转且不便跨设备查询，用户只看到“没反应”。', correction: '把 error、result、progress、attempts 保存到任务表。', selfCheck: '服务重启后还能看到失败原因和重试次数吗？' },
          { why: '并发认领会重复消耗 API 额度并造成写冲突。', correction: '认领时使用数据库锁并原子更新状态和 worker_id。', selfCheck: '两个 Worker 同时查询 queued 时怎样保证只有一个拿到？' },
        ],
        practiceEvidence: '能解释 queued/running/success/failed，以及 attempts 与 max_attempts 的区别。',
        challenge: '在实验 CSV 添加第三次失败，观察状态机是否允许从 success 再回 queued。',
      },
      {
        focus: '原始数据、派生因子和实验结果分层保存，并为每层定义业务唯一键、来源和时间。',
        pitfallDetails: [
          { why: '覆盖后无法重新计算、比较算法版本或证明原始值未被修改。', correction: '原始行情只 upsert 原始字段，因子评分写独立表。', selfCheck: '改动评分权重时是否需要重新抓取新闻原文？' },
          { why: '没有来源和时间就无法判断可信度、时区和当时是否可得。', correction: '保存 source、source_url、published_at、fetched_at。', selfCheck: '你能回答这条数据何时被市场知道、何时被系统抓到吗？' },
          { why: '万能 JSON 表缺少约束、索引和清晰关系，错误只能运行时才发现。', correction: '稳定字段建列，灵活参数可用 JSON，并保留外键与唯一约束。', selfCheck: '最常查询的 symbol/date 是否有明确列和索引？' },
        ],
        practiceEvidence: '能为行情、新闻、评分分别写出唯一键和可得时间字段。',
        challenge: '为一个“模型版本”字段选择独立列还是 JSON，并写出理由。',
      },
    ],
    lab: {
      title: '实验 03：重放后台任务生命周期',
      goal: '从事件表验证状态迁移、失败重试和“入队不等于成功”。',
      datasetPath: 'learning/datasets/03_task_lifecycle.csv', datasetDescription: '两项任务的创建、认领、进度、超时和重试事件。',
      scriptPath: 'learning/labs/03_project_pipeline_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\03_project_pipeline_lab.py',
      steps: [
        { title: '按任务分组', action: '找出 task 101 和 102 的所有事件。', expected: '101 一次成功，102 经历一次超时后第二次成功。' },
        { title: '运行状态机', action: '执行脚本验证相邻状态是否在 ALLOWED 中。', expected: '两项任务 final 都是 success。' },
        { title: '理解重试', action: '比较任务 102 的 attempt 字段。', expected: '第一次失败回 queued，最终 attempts=2。' },
        { title: '制造非法迁移', action: '把某个 success 后追加 running。', expected: '脚本 assert 失败并指出非法状态迁移。' },
      ],
      codeWalkthrough: [
        { code: 'histories[task_id].append(row)', explanation: '用任务主键聚合完整历史，避免把不同任务的状态混在一起。' },
        { code: 'current in ALLOWED[previous]', explanation: '状态迁移规则可测试，success 不能无理由重新 running。' },
        { code: "events[-1]['attempt']", explanation: '最后事件保留总尝试次数，便于判断是否频繁失败。' },
      ],
      expectedOutput: ['task=101 final=success attempts=1', 'task=102 final=success attempts=2', 'HTTP 返回任务号不等于成功', 'LAB_OK'],
      verification: ['能沿代码指出任务写库与 Worker 认领位置', '能解释为何需要 progress/result/error', '非法状态迁移会被测试抓住'],
    },
    readings: [
      { title: 'FastAPI Tutorial', provider: 'FastAPI 官方', url: 'https://fastapi.tiangolo.com/tutorial/', takeaway: '用类型化请求、依赖注入和分层路由建立可测试 API。', kind: '官方教程' },
      { title: 'SQLAlchemy ORM Quick Start', provider: 'SQLAlchemy 官方', url: 'https://docs.sqlalchemy.org/en/20/orm/quickstart.html', takeaway: '理解模型、Session、事务和查询，映射你熟悉的 Java ORM 经验。', kind: '官方教程' },
    ],
  },

  'python-bridge': {
    beginnerNote: '你已经会 Java/JS，这章不从变量定义讲起，而是专门补 Python 会让老开发者踩坑的对象引用、可变默认值、迭代器、异常和测试。',
    plainWords: [
      { term: '绑定', translation: '变量名指向对象，而不是固定类型的存储槽。', projectUse: '两个变量可能指向同一个 list。' },
      { term: '可变对象', translation: '创建后内容还能改变的对象，如 list/dict。', projectUse: 'Pydantic 使用 default_factory 防共享。' },
      { term: '迭代器', translation: '按需逐个产出元素的对象。', projectUse: '处理大数据时避免一次全放内存。' },
      { term: '上下文管理器', translation: '进入/退出时自动申请与释放资源。', projectUse: 'with Session(...) 保证数据库会话关闭。' },
      { term: '类型提示', translation: '给工具和读者的契约，不会自动做运行时强校验。', projectUse: 'mypy/IDE/Pydantic/测试共同保证。' },
    ],
    concepts: [
      {
        focus: '掌握 == 与 is、可变对象和默认参数，避免从 Java 迁移时产生隐蔽共享状态。',
        pitfallDetails: [
          { why: 'is 比较是否同一个对象，小整数或字符串驻留会让错误偶尔“看似可用”。', correction: '业务值使用 ==，只有判断 None 时常用 is None。', selfCheck: '两个内容相同但分别创建的 list，== 和 is 各是什么？' },
          { why: '注解不会阻止错误类型进入普通函数，运行时仍可能在深处失败。', correction: '边界用 Pydantic，内部用类型检查和测试。', selfCheck: '把字符串传给标注 float 的普通函数会自动报错吗？' },
          { why: '默认 list 在函数定义时只创建一次，多次调用会共享内容。', correction: '默认用 None，函数内新建；Pydantic 用 default_factory。', selfCheck: '连续两次不传 bucket 调用，结果是否互相污染？' },
        ],
        practiceEvidence: '能用 id()、==、is 演示对象身份和值相等的区别。',
        challenge: '故意把函数默认参数改成 []，连续调用两次并解释异常结果。',
      },
      {
        focus: '用清楚的小函数、模块和上下文管理器组织代码，不追求“一行写完”。',
        pitfallDetails: [
          { why: '嵌套推导式难调试，代码短不等于维护成本低。', correction: '只对单一映射/筛选用推导式，复杂分支提取函数。', selfCheck: '新人能在 30 秒内说出这行的输入输出吗？' },
          { why: 'DataFrame 逐行 Python 循环慢且容易忽略对齐语义。', correction: '优先向量化、groupby、rolling 和显式 merge。', selfCheck: '这个循环能否写成列运算并保留索引？' },
          { why: '文件、连接和 Session 泄漏会耗尽资源或留下未提交事务。', correction: '使用 with，异常路径也必须 rollback/close。', selfCheck: '中间 raise 后资源是否仍会释放？' },
        ],
        practiceEvidence: '能把一段复杂推导式重构成命名函数，并用 with 读取 CSV。',
        challenge: '把收益计算改成生成器，再说明它为何只能消费一次。',
      },
      {
        focus: '学会从 traceback 最后一层回到根因，并写验证数值语义的 pytest。',
        pitfallDetails: [
          { why: '最后一行只有异常类型，调用栈中的文件和输入上下文才告诉你错误从哪来。', correction: '从底部异常向上找第一段自己的代码，保留完整堆栈。', selfCheck: '能指出错误值在哪个函数、哪一行被制造吗？' },
          { why: '吞掉异常会把失败伪装成空数据，后续评分可能仍成功但全是中性值。', correction: '只捕获能恢复的具体异常，否则记录上下文后重新抛出。', selfCheck: '调用者如何知道本次用了回退源？' },
          { why: 'HTTP 200 只能证明接口响应，不能证明收益错位、费用和回撤正确。', correction: '为已知小样本断言精确数值和边界情况。', selfCheck: '若 position 少 shift 一天，现有测试会失败吗？' },
        ],
        practiceEvidence: '能读懂一次 Pydantic 校验错误，并补一条会在数值错位时失败的测试。',
        challenge: '把 expected final equity 改错 1 元，观察 pytest/断言怎样定位回归。',
      },
    ],
    lab: {
      title: '实验 04：用纯 Python 计算资金曲线与回撤', goal: '把列表、函数、类型提示和断言连接到一个真实量化小任务。',
      datasetPath: 'learning/datasets/04_python_returns.csv', datasetDescription: '6 个交易日的教学收盘价。',
      scriptPath: 'learning/labs/04_python_returns_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\04_python_returns_lab.py',
      steps: [
        { title: '读取价格', action: '确认 close 被转换为 float，而不是字符串。', expected: 'prices 长度为 6。' },
        { title: '拆成函数', action: '依次阅读 simple_returns、equity_curve、maximum_drawdown。', expected: '每个函数只有一个职责并有明确输入输出。' },
        { title: '运行断言', action: '执行脚本。', expected: '最终资金 108000，最大回撤约 -2.94%。' },
        { title: '修改输入', action: '把 99 改为 90 再运行。', expected: '最终资金仍由首尾决定，但最大回撤明显变差。' },
      ],
      codeWalkthrough: [
        { code: 'zip(prices, prices[1:])', explanation: '把相邻两天配对，不需要手写索引边界。' },
        { code: 'curve.append(curve[-1] * (1 + value))', explanation: '后一天资金基于当前资金增长，得到复利曲线。' },
        { code: 'peak = max(peak, value)', explanation: '逐点保存到目前为止的历史高点。' },
        { code: 'worst = min(worst, value / peak - 1)', explanation: '每点相对历史高点计算回撤并保留最差值。' },
      ],
      expectedOutput: ['observations=6', 'final_equity=108000.00', 'maximum_drawdown=-2.94%', 'LAB_OK'],
      verification: ['每个函数可单独传入小列表测试', '首尾价格解释最终收益', '中间路径解释最大回撤'],
    },
    readings: [
      { title: 'Python Tutorial', provider: 'Python 官方', url: 'https://docs.python.org/3/tutorial/', takeaway: '适合有其他语言经验的开发者按模块补足 Python 语义。', kind: '官方教程' },
      { title: 'CS50P', provider: 'Harvard', url: 'https://cs50.harvard.edu/python/', takeaway: '用讲解、问题集、测试和最终项目形成练习闭环。', kind: '官方教程' },
    ],
  },

  'numpy-pandas': {
    beginnerNote: 'NumPy/pandas 最重要的不是 API 数量，而是数组形状、索引标签和时间顺序。金融错误经常不会抛异常，只会悄悄算出错位结果。',
    plainWords: [
      { term: 'shape', translation: '数组每个维度的长度。', projectUse: '先检查行数、列数是否符合预期。' },
      { term: 'dtype', translation: '一列底层保存的数值类型。', projectUse: 'object 可能意味着数字被读成字符串。' },
      { term: 'axis', translation: '沿哪个方向聚合：0 跨行，1 跨列。', projectUse: '因子通常按日期跨股票或按股票跨日期计算。' },
      { term: '索引对齐', translation: '运算按标签配对，不按肉眼看到的行号。', projectUse: '不同股票日期缺口会自动产生 NaN。' },
      { term: 'rolling', translation: '只看当前位置之前固定长度的数据窗口。', projectUse: '均线、波动率和动量窗口。' },
    ],
    concepts: [
      {
        focus: '先看 shape/dtype/axis，再做聚合；NaN 是“未知”，不是天然的 0。',
        pitfallDetails: [
          { why: 'object 列可能进行字符串拼接或无法比较，数值错误会延迟到深处出现。', correction: '读取后立即检查 dtypes，并用 to_numeric(errors="raise")。', selfCheck: 'close 列中混入“停牌”两个字会怎样？' },
          { why: 'axis=0 与 axis=1 得到完全不同的业务含义，却都能返回合法数字。', correction: '计算前用一句话说清“对每列跨日期”还是“每行跨股票”。', selfCheck: 'DataFrame.mean(axis=1) 的每个输出对应什么？' },
          { why: '缺失价格填 0 会制造 -100% 和随后无穷大的收益。', correction: '先判断缺失原因，再删除、保留或基于业务规则填充。', selfCheck: '停牌日和源站漏数能用同一种填充吗？' },
        ],
        practiceEvidence: '能打印 DataFrame 的 shape、dtypes 和缺失计数，并解释每项。',
        challenge: '在 close 列加入字符串，观察读取、计算和显式类型转换的不同报错位置。',
      },
      {
        focus: '日期先解析、排序、去重，再按索引合并；对齐产生的 NaN 是重要证据。',
        pitfallDetails: [
          { why: '两只股票第 5 行可能对应不同日期，按行号相加是在配错交易日。', correction: '把 DatetimeIndex 设为索引后 join/concat，并检查 missing。', selfCheck: '相加前两个 Series 的 index 是否完全一致？' },
          { why: '字符串“2026-10”与非零填充日期排序可能错，rolling 顺序随之错误。', correction: '先 to_datetime，再 sort_index，并验证单调递增。', selfCheck: 'index.is_monotonic_increasing 是否为 True？' },
          { why: '前向填充默认把上次价格当成今天可交易价格，可能掩盖停牌和缺口。', correction: '先用交易日历识别缺口类型，并限制填充范围与用途。', selfCheck: '填充值能用于计算收益还是只用于画图？' },
        ],
        practiceEvidence: '能构造日期错开的两个 Series，并解释对齐后 NaN 出现在哪里。',
        challenge: '改用 outer join 与 inner join，对比行数和被丢弃的信息。',
      },
      {
        focus: 'rolling 只使用过去窗口，shift 把信号移动到下一可交易日，NaN 代表历史不足。',
        pitfallDetails: [
          { why: '今天收盘生成的信号若乘今天收益，相当于提前知道收盘。', correction: '信号至少 shift(1)，并明确用次日开盘还是收盘成交。', selfCheck: '第 t 日收益使用的是第 t-1 日已知仓位吗？' },
          { why: 'center=True 会把未来数据放入当前窗口，曲线通常异常平滑。', correction: '交易特征使用右对齐历史窗口。', selfCheck: '窗口边界是否包含当前点之后的日期？' },
          { why: 'min_periods=1 让“20 日均线”前 19 天实际使用 1–19 天，定义悄悄改变。', correction: '研究规则需要完整窗口时保留 NaN 并不交易。', selfCheck: '第几个交易日开始第一次产生合法信号？' },
        ],
        practiceEvidence: '能手算四天 signal、shift 后 position 和策略收益的错位关系。',
        challenge: '去掉 shift 运行回测，对比差异并解释为何更漂亮反而更可疑。',
      },
    ],
    lab: {
      title: '实验 05：两个股票的日期为什么对不上', goal: '用 pivot、reindex 和 pct_change 观察索引对齐与缺失日期。',
      datasetPath: 'learning/datasets/05_pandas_alignment.csv', datasetDescription: 'AAA 与 BBB 各缺一个不同交易日的收盘价。',
      scriptPath: 'learning/labs/05_pandas_alignment_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\05_pandas_alignment_lab.py',
      steps: [
        { title: '转宽表', action: '用 pivot 让日期做行、股票做列。', expected: '得到两列，每列在不同日期有 NaN。' },
        { title: '补齐日历', action: '用 bdate_range 和 reindex 建立统一工作日。', expected: 'shape 为 (6, 2)。' },
        { title: '定位缺口', action: '分别筛选 isna。', expected: 'AAA 缺 03-05，BBB 缺 03-03。' },
        { title: '拒绝乱填', action: '保持 NaN 计算 pct_change(fill_method=None)。', expected: '缺失附近收益保持未知，不自动前填。' },
      ],
      codeWalkthrough: [
        { code: 'pivot(index="date", columns="symbol", values="close")', explanation: '建立“日期 × 股票”的矩阵，同一日期才会落在同一行。' },
        { code: 'wide.reindex(calendar)', explanation: '显式要求完整日历，原来不存在的观测变成 NaN。' },
        { code: 'aligned[symbol].isna()', explanation: '缺失本身是质量证据，应先定位而不是立刻填 0。' },
        { code: 'pct_change(fill_method=None)', explanation: '禁止 pandas 悄悄前填，保留缺失的真实影响。' },
      ],
      expectedOutput: ['shape=(6, 2)', "AAA 缺 ['2026-03-05']", "BBB 缺 ['2026-03-03']", 'LAB_OK'],
      verification: ['缺失日期与 CSV 肉眼检查一致', 'inner join 后行数减少', '收益没有跨缺失日错误连接'],
    },
    readings: [
      { title: 'NumPy absolute basics for beginners', provider: 'NumPy 官方', url: 'https://numpy.org/doc/stable/user/absolute_beginners.html', takeaway: '从数组、形状、聚合和 broadcasting 建立计算基础。', kind: '官方教程' },
      { title: 'pandas Getting Started Tutorials', provider: 'pandas 官方', url: 'https://pandas.pydata.org/docs/getting_started/intro_tutorials/', takeaway: '覆盖读取、筛选、合并、统计和时间序列的标准做法。', kind: '官方教程' },
    ],
  },

  'market-data': {
    beginnerNote: '行情和财务并不是“下载下来就能用”。你必须知道价格是否复权、日期是否可交易、财报何时真正公开，以及停牌时是否能成交。',
    plainWords: [
      { term: '除权除息', translation: '分红送股后交易所机械调整参考价。', projectUse: '原始价可能断层，因子用统一复权序列。' },
      { term: '停牌', translation: '交易日内该股票不可正常买卖。', projectUse: '回测不能假设停牌日按收盘价换仓。' },
      { term: '涨跌停', translation: '价格达到规则上限/下限，订单可能无法成交。', projectUse: '基础回测将其列为尚未完全模拟的限制。' },
      { term: '报告期', translation: '财务数字描述到哪一天。', projectUse: 'report_date 不等于市场知道它的日期。' },
      { term: '可得日', translation: '数据最早可以被研究者使用的时间。', projectUse: 'available_at ≤ score_date 才能进入历史评分。' },
    ],
    concepts: [
      {
        focus: '同一条价格链统一复权口径，并明确何时因停牌或涨跌停不能执行。',
        pitfallDetails: [
          { why: '开盘和收盘口径不同会让日内收益包含复权因子而非真实价格变化。', correction: '同一根 bar 的 OHLC 使用同源同口径数据。', selfCheck: 'high/low/open/close 的 adjustment factor 是否一致？' },
          { why: '横截面排名若各股口径不同，分数差异没有可比性。', correction: '在 Provider 层统一参数并把 adjustment 写入元数据。', selfCheck: '抽查三只股票在除权日前后的曲线是否连续？' },
          { why: '停牌时没有可成交报价，理论信号不能神奇换仓。', correction: '持有旧仓或延后成交，并记录未成交原因。', selfCheck: '目标权重变化但股票停牌时，现金和其他仓位怎么处理？' },
        ],
        practiceEvidence: '能解释 raw/qfq/hfq 的用途，并找到一个原始价格断层。',
        challenge: '用 raw_close 计算一次动量，再用 adjusted close 计算并比较。',
      },
      {
        focus: '收益、波动、回撤和夏普都从同一条净资金曲线与同一时间区间计算。',
        pitfallDetails: [
          { why: '短期总收益直接乘 252 忽略复利和样本长度，可能夸大结果。', correction: '用实际年数做几何年化，并对过短区间标注不稳定。', selfCheck: '只有 10 天数据时年化数字有多大解释力？' },
          { why: '最大回撤描述账户资金从高点跌多少，不是股票价格本身的任意跌幅。', correction: '先生成净收益资金曲线，再除以累计高点。', selfCheck: '成本扣在资金曲线之前还是之后？' },
          { why: '不同起止日期会经历不同市场，比较没有公平参照。', correction: '策略与基准使用相同日历、起点和缺失处理。', selfCheck: '两条曲线第一天和最后一天完全一致吗？' },
        ],
        practiceEvidence: '能手算五期资金曲线、累计高点和每期回撤。',
        challenge: '构造两条最终收益相同但路径不同的曲线，比较最大回撤。',
      },
      {
        focus: '财报数字只能从真实公告日开始使用，不能拿后来修订的最终值回填过去。',
        pitfallDetails: [
          { why: 'report_date 是业务覆盖期，不是投资者看到报告的日期；两者可能相差数月。', correction: '保存 available_at，并在每个 score_date 做 ≤ 过滤。', selfCheck: '12 月 31 日年报数据能在当天用于评分吗？' },
          { why: '数据库最终值可能包含后续更正，回填会让历史策略知道未来。', correction: '按披露版本保存快照或至少记录首次可得值和来源。', selfCheck: '历史评分能复原当时而非今天看到的财务吗？' },
          { why: '无条件前填会把过期财务无限延长并掩盖缺报。', correction: '设置最大陈旧期，缺失时回退中性并告警。', selfCheck: '这项财务距离评分日已经多少天？' },
        ],
        practiceEvidence: '能画 report_date、available_at、score_date 三点时间线并判断可用性。',
        challenge: '把 score_date 从 03-30 改为 03-31，观察 ROE 为什么刚好切换。',
      },
    ],
    lab: {
      title: '实验 06：50% 暴跌为何可能只是除权', goal: '同时验证复权价格和点时财务可得性。',
      datasetPath: 'learning/datasets/06_market_data.csv', datasetDescription: '包含一次 2:1 调整与两个不同公告日的 ROE。',
      scriptPath: 'learning/labs/06_market_data_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\06_market_data_lab.py',
      steps: [
        { title: '看原始跳变', action: '计算 03-31 raw_close / 03-30 raw_close - 1。', expected: '约 -49.51%，看起来像崩盘。' },
        { title: '统一复权', action: '计算 raw_close × adjustment_factor。', expected: '同一天真实可比收益约 +0.98%。' },
        { title: '卡住可得日', action: '评分日设为 03-30，筛 available_at ≤ score_date。', expected: '只能使用旧 ROE 0.112。' },
        { title: '推进一天', action: '把评分日改为 03-31。', expected: '新年报 ROE 0.126 才变为可用。' },
      ],
      codeWalkthrough: [
        { code: 'raw_close * adjustment_factor', explanation: '将机械价格断层放到同一比较基准，不代表真实成交价被改写。' },
        { code: 'available_at <= score_date', explanation: '这是点时过滤的核心：当时没公开的数据一律不可用。' },
        { code: 'usable[-1]["roe"]', explanation: '只在已可得记录里取最新值，而不是取数据库全表最后一行。' },
      ],
      expectedOutput: ['raw_return 约 -49.51%', 'adjusted_return 约 +0.98%', '03-30 可用 ROE=0.112', 'LAB_OK'],
      verification: ['能解释原始价与复权价各自用途', '评分日前没有使用 03-31 公告', '修改日期后结果按预期切换'],
    },
    readings: [
      { title: '上市公司信息披露与定期报告', provider: '上交所投教', url: 'https://edu.sse.com.cn/college/required/basicinfo/index.shtml', takeaway: '财务分析必须先理解报告、预告、快报和正式披露的时间与含义。', kind: '官方教程' },
      { title: '最新公告', provider: '巨潮资讯', url: 'https://www.cninfo.com.cn/new/commonUrl?url=disclosure%2Flist%2Fnotice', takeaway: '法定公告适合核对新闻事实与真实披露时间。', kind: '官方教程' },
    ],
  },

  'factor-backtest': {
    beginnerNote: '因子只是“打分依据”，策略还要决定标准化、排序、持仓、执行和成本。回测的任务是尽量诚实地模拟这些规则，而不是画出最漂亮的曲线。',
    plainWords: [
      { term: '横截面', translation: '同一天在多只股票之间比较。', projectUse: '把动量、质量、情绪标准化后排名。' },
      { term: '标准化', translation: '把不同量纲变成可组合的相对分数。', projectUse: '避免 ROE 与收益率直接相加。' },
      { term: '权重', translation: '组合资金在各标的上的比例。', projectUse: '因子权重与持仓权重是两件事。' },
      { term: '换手率', translation: '仓位改变了多少。', projectUse: '换手乘成本率得到简化交易成本。' },
      { term: '未来函数', translation: '历史时点使用了后来才知道的信息。', projectUse: '信号 shift、财务 available_at、新闻 published_at 都要防。' },
    ],
    concepts: [
      {
        focus: '把原始因子变成可比较分数，再由清晰门槛产生持仓；因子权重不是资金权重。',
        pitfallDetails: [
          { why: '因子分数表示相对偏好，不自动告诉你投入 0.7 还是 70% 资金。', correction: '评分层与组合层分开，组合层另定义 Top N、等权或风险权重。', selfCheck: '总分 0.8 是否意味着买入 80%？' },
          { why: 'ROE、收益率和情绪范围不同，直接加总会被数值尺度最大的项支配。', correction: '先排名、z-score 或稳健缩放，再组合。', selfCheck: '把 ROE 从小数改成百分数会不会改变排名？' },
          { why: '权重不闭合会隐含杠杆或未解释现金。', correction: '明确因子权重和持仓权重各自和为 1，或说明现金/杠杆。', selfCheck: '所有持仓加现金后的总权重是多少？' },
        ],
        practiceEvidence: '能给三只股票手算标准化分项、综合分和 Top 2 持仓。',
        challenge: '让全部股票低于情绪门槛，验证组合应空仓还是仍强制持有。',
      },
      {
        focus: '成本只在仓位改变时发生；策略规模越大，固定滑点模型越不可信。',
        pitfallDetails: [
          { why: '卖出也有费用和冲击，只扣买入会系统性高估高换手策略。', correction: '用权重绝对变化计算双边换手并统一扣费。', selfCheck: '从 100% A 切到 100% B 的换手是 100% 还是 200%？' },
          { why: '持仓不变意味着没有新交易，逐日扣费会低估长期持有。', correction: '成本基于 position.diff()/weights.diff()。', selfCheck: '连续两天目标权重相同，turnover 是否为 0？' },
          { why: '大订单会吃掉更多盘口，冲击成本随规模和流动性变化。', correction: '教学回测做成本敏感性；实盘前引入成交量参与率与容量限制。', selfCheck: '资金从 10 万变 1 亿时同一滑点仍合理吗？' },
        ],
        practiceEvidence: '能手算一次调仓的买卖换手和净收益。',
        challenge: '将成本提高五倍并解释净收益为何非线性变化。',
      },
      {
        focus: '系统检查价格、财务、成分股和参数选择四类泄漏，不只在代码里找一个 shift。',
        pitfallDetails: [
          { why: '价格延迟正确也可能使用尚未公布财报或未来新闻，泄漏不只一种。', correction: '为每类数据定义 event_time、available_time 和 execution_time。', selfCheck: '每个因子值在信号形成时真的已知吗？' },
          { why: '用今天的指数成分回测过去会删除后来退市/变差公司，产生幸存者偏差。', correction: '使用历史成分或明确声明固定股票池的局限。', selfCheck: '十年前的股票池是当时可知还是今天倒推？' },
          { why: '反复看测试集再改阈值，测试集已经参与训练。', correction: '锁定测试集；下一轮修改必须等待新的数据或另设验证层。', selfCheck: '这个测试区间被查看和调参多少次？' },
        ],
        practiceEvidence: '能为四类泄漏各指出代码防线、数据字段和一个失败测试。',
        challenge: '故意取消 shift，确认测试或结果能暴露同日交易偏差。',
      },
    ],
    lab: {
      title: '实验 07：延迟信号和交易成本怎样改变结果', goal: '从 signal 得到次日 position，并按换手扣除成本。',
      datasetPath: 'learning/datasets/07_backtest_costs.csv', datasetDescription: '8 个交易日的价格与教学信号。',
      scriptPath: 'learning/labs/07_backtest_cost_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\07_backtest_cost_lab.py',
      steps: [
        { title: '移动信号', action: '把 signal shift(1) 得到 position。', expected: '第一天仓位为 0，今天信号最早明天生效。' },
        { title: '计算换手', action: '对 position.diff().abs() 求和。', expected: '总换手为 6.0。' },
        { title: '比较毛净', action: '运行 0.1% 成本。', expected: 'net_return 小于 gross_return。' },
        { title: '压力测试', action: '把成本变成五倍。', expected: '净收益进一步下降，而毛收益不变。' },
      ],
      codeWalkthrough: [
        { code: 'position = signal.shift(1).fillna(0.0)', explanation: '信号形成和持仓生效分离，是防同日偷看收盘价的第一道防线。' },
        { code: 'turnover = position.diff().abs()', explanation: '只有目标仓位变化才产生交易。' },
        { code: 'net = gross - turnover * cost_rate', explanation: '净收益才是资金曲线应使用的收益。' },
        { code: '(1 + net).prod() - 1', explanation: '逐期净收益复利连乘得到区间结果。' },
      ],
      expectedOutput: ['gross_return 约 -13.24%', 'net_return 约 -13.77%', 'turnover=6.0', '五倍成本结果更差', 'LAB_OK'],
      verification: ['position 与 signal 相差一个交易日', '持仓不变日 turnover 为 0', '提高成本不会改变 gross_return'],
    },
    readings: [
      { title: 'The Alpha in Portfolio Construction', provider: 'AQR / Cliff Asness、Antti Ilmanen', url: 'https://www.aqr.com/Insights/Research/Trade-Publication/The-Alpha-in-Portfolio-Construction', takeaway: '公开从业观点强调组合构建、风险管理和成本控制本身就是重要价值来源。', kind: '从业者经验' },
      { title: 'You Can Have Your Momentum Factor and Eat it Too', provider: 'AQR / Cliff Asness', url: 'https://www.aqr.com/insights/perspectives/you-can-have-your-momentum-factor-and-eat-it-too', takeaway: '讨论动量的现实交易成本与实施方式，提醒学术组合不等于实际执行。', kind: '从业者经验' },
    ],
  },

  'sentiment-llm': {
    beginnerNote: '舆情因子不是让模型预测股价，而是把给定新闻转成可审计的结构化字段。来源、发布时间、去重、置信度和模型版本与分数同样重要。',
    plainWords: [
      { term: 'Schema', translation: '输出必须遵守的字段与类型。', projectUse: 'label/score/confidence/summary/rationale。' },
      { term: '结构化输出', translation: '让文本结果变成程序可校验的 JSON。', projectUse: '非法标签和范围会被后端拒绝或规范化。' },
      { term: '去重', translation: '识别同一事件的转载或洗稿。', projectUse: '链接、标题、正文和 72 小时时窗综合判断。' },
      { term: '半衰期', translation: '经过这段时间，事件权重减半。', projectUse: '旧新闻对当前评分影响逐渐下降。' },
      { term: '校准', translation: '模型说 80% 时，长期是否真的约 80% 正确。', projectUse: 'confidence 目前只是模型字段，必须人工评估。' },
    ],
    concepts: [
      {
        focus: '把模型限制成文本分类器：只依据输入，输出合法 JSON，并保留原文和版本。',
        pitfallDetails: [
          { why: '模型偶尔会加 Markdown、解释或截断，直接 float/JSON 解析会失败。', correction: '用 Schema 校验、有限重试和明确回退结果。', selfCheck: '缺少 score 或超出 [-1,1] 时系统怎么处理？' },
          { why: '模型可能补充训练记忆中的公司事实，造成无法知道的“外部信息”。', correction: '提示词明确只依据输入，并在 rationale 中要求引用文本证据。', selfCheck: '理由中的每个事实能在输入原文找到吗？' },
          { why: '自报 confidence 没有经过统计校准，不能直接当正确概率。', correction: '抽样人工标注，分桶比较置信度与真实一致率。', selfCheck: '高置信错误是否被单独统计和复盘？' },
        ],
        practiceEvidence: '能手工填写一条完整 Schema，并指出哪些字段来自模型、哪些来自抓取元数据。',
        challenge: '删除 JSON 的 label 字段，验证后端能拒绝或回退而不是静默写库。',
      },
      {
        focus: '先按真实发布时间过滤未来，再去重、按置信度和时间衰减聚合。',
        pitfallDetails: [
          { why: '抓取时间可能晚于发布数天，用它会错估事件年龄和信号可得时点。', correction: '优先解析 published_at，fetched_at 只用于审计采集延迟。', selfCheck: '原文时间缺失时采用了什么保守规则？' },
          { why: '同一事件被十家媒体转载会被当十票，夸大情绪。', correction: '同股票内综合链接、标题、摘要和 72 小时时窗去重。', selfCheck: '去重前后事件数和代表记录如何变化？' },
          { why: 'UTC/北京时间混淆可能让收盘后公告落到交易前，产生未来信息。', correction: '保存显式时区并统一转换到 Asia/Shanghai 判断交易日。', selfCheck: '18:30 公告最早在哪个交易日形成仓位？' },
        ],
        practiceEvidence: '能手算 0/3/6 天半衰期权重并解释 72 小时转载如何合并。',
        challenge: '把 as_of 改到未来事件之后，观察 usable 和 unique 数量变化。',
      },
      {
        focus: '用固定人工样本评估模型升级、回退和错误类型，不只展示看起来正确的案例。',
        pitfallDetails: [
          { why: '只挑正确例子会隐藏否定词、反讽、主体混淆和长公告失败。', correction: '固定随机抽样并保留所有错误，按类型统计。', selfCheck: '评估集中是否包含利好、利空、中性和难例？' },
          { why: '模型能力更强不保证金融标签更一致，也可能更爱推理出输入外内容。', correction: '同一黄金集比较准确率、格式成功率、成本和延迟。', selfCheck: '升级标准是否事先确定且包含业务指标？' },
          { why: '回退中性与真实模型中性含义不同，混在一起会污染因子。', correction: '保存 model/source/status，统计回退占比并触发告警。', selfCheck: '排名页能否区分模型结论和降级占位？' },
        ],
        practiceEvidence: '能设计 20 条黄金集表格，包括人工标签、模型版本、错误类型和是否回退。',
        challenge: '构造一条“看似利好但主体不是目标公司”的难例，并写判定依据。',
      },
    ],
    lab: {
      title: '实验 08：过滤未来、合并转载、聚合情绪', goal: '在不调用任何大模型的情况下理解舆情因子的确定性后处理。',
      datasetPath: 'learning/datasets/08_sentiment_events.csv', datasetDescription: '包含三条 72 小时内转载、一条未来事件和多种标签。',
      scriptPath: 'learning/labs/08_sentiment_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\08_sentiment_lab.py',
      steps: [
        { title: '过滤未来', action: '只保留 published_at ≤ AS_OF。', expected: '7 条中 6 条可用。' },
        { title: '识别转载', action: '同股票、同核心事件且间隔≤72小时视为一组。', expected: '三条业绩预增只留下一个代表事件。' },
        { title: '计算权重', action: 'confidence × 7 日半衰期衰减。', expected: '越新、置信度越高，权重越大。' },
        { title: '聚合分数', action: '加权平均 unique 事件。', expected: 'weighted_sentiment 约 0.1216。' },
      ],
      codeWalkthrough: [
        { code: 'published_at <= AS_OF', explanation: '先保证当时可得，未来事件即使分数很高也必须排除。' },
        { code: 'gap.total_seconds() <= 72 * 3600', explanation: '72 小时内发布时间都视为相近，时间不额外降权。' },
        { code: 'confidence * exp(-log(2) * age / 7)', explanation: '7 天后时间权重减半，再乘模型置信度。' },
        { code: 'weighted_sum / total_weight', explanation: '用总权重归一化，避免事件条数直接放大分数范围。' },
      ],
      expectedOutput: ['raw_events=7', 'usable=6', 'unique=4', 'weighted_sentiment=0.1216', 'LAB_OK'],
      verification: ['未来事件未进入因子', '三条转载只计一次', '修改 AS_OF 会改变可用集合'],
    },
    readings: [
      { title: '最新公告', provider: '巨潮资讯（深交所法定披露平台）', url: 'https://www.cninfo.com.cn/new/commonUrl?url=disclosure%2Flist%2Fnotice', takeaway: '新闻用于发现线索，法定公告用于核对主体、事实和披露时间。', kind: '官方教程' },
      { title: 'Text classification', provider: 'Hugging Face', url: 'https://huggingface.co/docs/transformers/main/en/tasks/sequence_classification', takeaway: '情绪分析本质是文本分类；训练、评估、标签映射和推理都需要明确契约。', kind: '官方教程' },
    ],
  },

  'walk-forward': {
    beginnerNote: 'Walk-forward 像按时间进行多次模拟考试：每次只用过去选参数，锁定后参加下一段测试。最终成绩只拼测试卷，训练卷不能混进去。',
    plainWords: [
      { term: '训练窗口', translation: '允许选择参数的过去数据。', projectUse: '比较候选动量窗口和阈值。' },
      { term: '测试窗口', translation: '锁定参数后第一次看到的数据。', projectUse: '只用于评估，不现场改规则。' },
      { term: '滚动', translation: '窗口按时间向前移动并重复实验。', projectUse: '观察不同市场阶段的稳定性。' },
      { term: '参数网格', translation: '运行前写好的有限候选组合。', projectUse: '候选窗口与情绪门槛。' },
      { term: 'OOS', translation: 'Out-of-sample，样本外测试。', projectUse: '最终资金曲线只拼接 OOS 收益。' },
    ],
    concepts: [
      {
        focus: '严格保持时间顺序，训练只能在测试之前，最终曲线只收集测试段。',
        pitfallDetails: [
          { why: '随机 KFold 会让未来样本进入训练，再预测过去，破坏真实时间方向。', correction: '使用 expanding/rolling split 或 TimeSeriesSplit。', selfCheck: '每个训练日期是否全部早于测试日期？' },
          { why: '训练收益已经参与选参数，拼入最终曲线会重复报告已见数据。', correction: '只 append test_returns，训练指标单独保存。', selfCheck: '最终 OOS 点数等于所有测试窗口点数之和吗？' },
          { why: '看到测试差就换参数，相当于把测试集变成训练集。', correction: '运行前固定候选集和判定规则，失败也如实记录。', selfCheck: '测试开始后是否修改过任何规则？' },
        ],
        practiceEvidence: '能画出训练/测试窗口时间轴，并指出最终曲线来自哪些段。',
        challenge: '把 CSV 的 train 行误加入拼接，比较夸大的总收益。',
      },
      {
        focus: '参数搜索次数也是实验成本；候选越多，碰巧挑中噪声的机会越大。',
        pitfallDetails: [
          { why: '不断扩大网格几乎总能找到更漂亮的历史参数，但它可能只匹配噪声。', correction: '依据经济逻辑设窄范围，并记录试验总数。', selfCheck: '每个候选值为何在运行前就合理？' },
          { why: '删除亏损窗口等于选择性报告，平均值不再代表真实流程。', correction: '展示每个窗口、失败比例和最差窗口。', selfCheck: '读者能看到策略在哪些阶段失效吗？' },
          { why: '同一测试集反复用于版本选择后已不再“样本外”。', correction: '保留最终锁箱数据，或等待新数据验证。', selfCheck: '该区间被多少个版本看过？' },
        ],
        practiceEvidence: '能计算窗口数 × 参数组合数，并写入实验登记表。',
        challenge: '把候选窗口从 3 个扩到 30 个，先解释多重比较风险再运行。',
      },
      {
        focus: '先报告事实，再区分推断和待验证问题；亏损既可能是策略失效，也可能是正常阶段差异。',
        pitfallDetails: [
          { why: '策略在某阶段亏损可能符合风险特征，自动归因代码错误会诱导事后修改。', correction: '先复核数据与交易，再按预设假设解释。', selfCheck: '没有发现实现错误时，你是否愿意保留负结果？' },
          { why: '总 OOS 正收益可能由一个窗口贡献，其余大多失败。', correction: '展示窗口分布、胜率、最差回撤和贡献集中度。', selfCheck: '去掉最好窗口后结论是否仍成立？' },
          { why: '为每次结果编新故事不可证伪，也不能预测下一段。', correction: '分成事实/推断/下一步实验三栏。', selfCheck: '哪句话是数据直接支持，哪句只是解释？' },
        ],
        practiceEvidence: '能为一组 OOS 结果写三栏结论，并与同区间基准比较。',
        challenge: '删除最好测试窗口，重新计算并说明策略是否依赖单一阶段。',
      },
    ],
    lab: {
      title: '实验 09：只拼接四个测试窗口', goal: '从混合 train/test 表中筛出 OOS 段并计算拼接收益与窗口胜率。',
      datasetPath: 'learning/datasets/09_walk_forward_windows.csv', datasetDescription: '4 个滚动窗口各一段训练和测试结果。',
      scriptPath: 'learning/labs/09_walk_forward_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\09_walk_forward_lab.py',
      steps: [
        { title: '筛测试段', action: '只保留 phase=test。', expected: '8 行中剩 4 行。' },
        { title: '逐窗比较', action: '比较 strategy_return 与 benchmark_return。', expected: '只有窗口 3 严格跑赢基准。' },
        { title: '拼接复利', action: '对四段测试收益连乘。', expected: 'stitched OOS 约 4.12%。' },
        { title: '拒绝美化', action: '同时报告 winning_windows。', expected: '结果为 1/4，提醒总收益掩盖稳定性问题。' },
      ],
      codeWalkthrough: [
        { code: 'rows if phase == "test"', explanation: '训练数据只负责参数选择，不能进入最终成绩。' },
        { code: 'compounded *= 1 + strategy', explanation: '按真实时间顺序拼接每段样本外收益。' },
        { code: 'winning_windows += strategy > benchmark', explanation: '统计跨阶段稳定性，而不是只看总数。' },
      ],
      expectedOutput: ['4 个 test 窗口', 'stitched_oos_return=4.12%', 'winning_windows=1/4', 'LAB_OK'],
      verification: ['没有 train 行进入最终计算', '每段测试都晚于对应训练', '总收益和窗口胜率同时报告'],
    },
    readings: [
      { title: 'TimeSeriesSplit', provider: 'scikit-learn 官方', url: 'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html', takeaway: '时间序列切分必须防止用未来训练、再评估过去。', kind: '官方教程' },
      { title: 'The Effects of Backtest Overfitting on OOS Performance', provider: 'Bailey、Borwein、López de Prado、Zhu', url: 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659', takeaway: '论文说明尝试越多策略配置，选中历史偶然性的风险越高。', kind: '论文' },
    ],
  },

  'research-engineering': {
    beginnerNote: '研究工程化的目标不是“服务能启动”，而是同一任务可重复、错误有证据、秘密不泄漏、数据异常不会悄悄变成交易信号。',
    plainWords: [
      { term: '幂等键', translation: '判断两次写入是否同一业务记录的键。', projectUse: 'symbol+trade_date、news content_hash。' },
      { term: '事务', translation: '一组写入要么一起成功，要么一起回滚。', projectUse: 'Worker 失败后 rollback 再重试。' },
      { term: '告警证据', translation: '规则触发时保存的具体行、值和阈值。', projectUse: '数据治理 evidence 字段。' },
      { term: '严重性', translation: '问题对研究可信度的影响等级。', projectUse: 'critical/warning/info。' },
      { term: '秘密', translation: '泄漏后可被滥用的认证信息。', projectUse: '数据库密码、GitHub token、模型 API key。' },
    ],
    concepts: [
      {
        focus: '为每类数据定义业务唯一键，重试前 rollback，重复执行只更新同一记录。',
        pitfallDetails: [
          { why: '自增 id 每次都不同，无法判断业务上是否同一交易日或同一新闻。', correction: '使用 symbol+date、hash 等自然业务键并建唯一约束。', selfCheck: '相同输入执行两次，表行数会增加吗？' },
          { why: '捕获冲突后全部忽略可能错过新字段和纠正值。', correction: '明确哪些字段允许 upsert 更新，并记录来源优先级。', selfCheck: '重复记录与新版本记录怎样区分？' },
          { why: '失败事务未回滚时 Session 仍处于错误状态，后续操作继续失败。', correction: 'except 中先 rollback，再决定重试或记录失败。', selfCheck: '数据库异常后下一条股票还能正常处理吗？' },
        ],
        practiceEvidence: '能在三个表中找到 UniqueConstraint，并解释重跑后行数应怎样变化。',
        challenge: '连续运行同一实验两次，比较前后计数与更新时间。',
      },
      {
        focus: '质量规则必须有阈值、严重性和具体证据，且能区分源站漏数与真实停牌。',
        pitfallDetails: [
          { why: '全部 critical 会造成告警疲劳，真正阻断研究的问题反而被忽略。', correction: '按是否会污染评分/回测定义 critical、warning、info。', selfCheck: '这项问题应阻断评分还是只提示复核？' },
          { why: '只写“数据异常”无法定位、复现或验证修复。', correction: '保存 symbol/date/value/threshold/source 等 evidence。', selfCheck: '别人仅看告警记录能找到原始行吗？' },
          { why: '无业务解释的硬编码阈值会误伤正常分红、停牌或波动。', correction: '阈值配置化并在文档写来源、单位和例外。', selfCheck: '为什么是 25% 而不是 20%？适用于所有板块吗？' },
        ],
        practiceEvidence: '能对重复日、非法 OHLC、负成交量和极端收益分别输出证据。',
        challenge: '为“成交量为 0”设计规则，区分停牌和源站缺失。',
      },
      {
        focus: '配置可以进环境或数据库，秘密只放受控凭证；日志、Git 和异常都不能泄漏认证信息。',
        pitfallDetails: [
          { why: 'Git 历史即使后来删除仍可能被克隆，token 需立即轮换。', correction: 'credentials/.env 加入 ignore，提交前做秘密扫描。', selfCheck: 'git ls-files 是否能看到 credentials.txt？' },
          { why: '完整请求头可能包含 Basic/Auth/API key，日志平台扩大泄漏范围。', correction: '日志只记录供应商、状态码和 request id，敏感值打码。', selfCheck: '异常字符串是否包含 Authorization 内容？' },
          { why: '网页可修改数据库地址或密钥会扩大攻击面并难审计。', correction: '网页只开放业务参数；基础设施秘密由服务器环境管理。', selfCheck: '这项配置改变会不会获得新权限或访问外部系统？' },
        ],
        practiceEvidence: '能列出业务配置、部署配置和秘密各三项，并说明存放位置。',
        challenge: '扫描暂存 diff，确认没有 token、密码、私钥或完整认证头。',
      },
    ],
    lab: {
      title: '实验 10：让数据质量问题带着证据说话', goal: '用确定性规则找出重复日期、OHLC 矛盾、负成交量和异常收益。',
      datasetPath: 'learning/datasets/10_data_quality_cases.csv', datasetDescription: '7 行数据中故意埋入四类质量问题。',
      scriptPath: 'learning/labs/10_data_quality_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\10_data_quality_lab.py',
      steps: [
        { title: '找重复键', action: '按 date 计数。', expected: '2026-06-02 出现两次。' },
        { title: '验证 OHLC', action: '检查 low ≤ open/close ≤ high。', expected: 'row 4 的 high 小于 open，被识别。' },
        { title: '验证业务范围', action: '检查 volume<0 和相邻收益绝对值>25%。', expected: 'row 5、row 6 分别触发。' },
        { title: '保留证据', action: '输出 row_id，而不是只输出 True/False。', expected: '可以回到 CSV 精确定位。' },
      ],
      codeWalkthrough: [
        { code: 'Counter(row["date"] for row in rows)', explanation: '业务键重复是第一类幂等/质量问题。' },
        { code: 'low <= min(open, close) <= max(open, close) <= high', explanation: '任何合法 K 线都必须满足的确定性约束。' },
        { code: 'abs(close / previous_close - 1) > 0.25', explanation: '阈值是调查触发器，不代表这条行情一定错误。' },
      ],
      expectedOutput: ['duplicate_dates 包含 2026-06-02', 'invalid_ohlc_rows=[4]', 'negative_volume_rows=[5]', 'extreme_return_rows=[6]', 'LAB_OK'],
      verification: ['每项告警能定位到 row_id', '修复对应行后告警消失', '阈值含义写入研究记录'],
    },
    readings: [
      { title: 'pytest documentation', provider: 'pytest 官方', url: 'https://docs.pytest.org/en/stable/', takeaway: '小而确定的测试是防止研究语义随重构悄悄改变的基础。', kind: '官方教程' },
      { title: 'SQLAlchemy Session Basics', provider: 'SQLAlchemy 官方', url: 'https://docs.sqlalchemy.org/en/20/orm/session_basics.html', takeaway: '理解事务边界、commit、rollback 和 Session 生命周期。', kind: '官方教程' },
    ],
  },

  'capstone': {
    beginnerNote: '毕业项目不是再加十个功能，而是交付一条可复查证据链：问题、数据、方法、版本、结果、失败、局限和下一步。能诚实停止一个无效策略也是成果。',
    plainWords: [
      { term: '研究问题', translation: '范围明确、能被结果回答的问题。', projectUse: '限定股票池、时期和因子。' },
      { term: '验收标准', translation: '运行前写好的通过/失败条件。', projectUse: 'OOS、回撤、换手和数据质量门槛。' },
      { term: '稳健性', translation: '小幅改变参数或市场阶段后结论不完全崩溃。', projectUse: '参数邻域、成本、窗口和股票池敏感性。' },
      { term: '研究日志', translation: '按时间记录尝试、原因和结果。', projectUse: '避免只留下最终冠军。' },
      { term: '可复现报告', translation: '别人能按数据、代码和版本重新得到结论。', projectUse: '提交 commit、配置、数据截止日和输出。' },
    ],
    concepts: [
      {
        focus: '选一个小问题，冻结股票池与区间，先写三项失败线再开始跑。',
        pitfallDetails: [
          { why: '题目越大，数据源、参数和解释空间越多，更容易无限延期和过拟合。', correction: '先用 10–15 只股票、一个因子问题和一个基准完成闭环。', selfCheck: '四周内能否独立复现并解释全部结果？' },
          { why: '最高收益会奖励杠杆、集中和数据错误，却忽略研究可信度。', correction: '验收同时包括 OOS、回撤、换手、质量告警和可复现性。', selfCheck: '收益降低但证据更可信是否仍算进步？' },
          { why: '结果不好就换区间会把时间选择也变成隐形参数。', correction: '区间运行前冻结，失败后保留原结果再设计新实验。', selfCheck: '报告中能看到所有尝试过的区间吗？' },
        ],
        practiceEvidence: '形成一页研究章程：问题、股票池、时间、数据、规则、基准、三条失败线。',
        challenge: '把题目压缩到一句话，并删掉任何无法在四周内验证的目标。',
      },
      {
        focus: '报告不仅放图，还要写数据截止日、版本、失败实验和事实/解释边界。',
        pitfallDetails: [
          { why: '最终曲线看不出参数怎么选、失败了多少次、是否有数据泄漏。', correction: '按问题、数据、方法、样本内外、稳健性、局限、结论组织。', selfCheck: '不看代码能否知道这条曲线如何生成？' },
          { why: '隐藏失败参数会低估多重尝试和选择偏差。', correction: '实验登记表保留每个版本、输入、结果和决策。', selfCheck: '读者能数出一共试了多少配置吗？' },
          { why: '没有截止日期和模型版本，新闻与评分会随重新抓取而变化。', correction: '记录 data_as_of、commit、模型、prompt 和配置快照。', selfCheck: '六个月后能否重建同一输入集合？' },
        ],
        practiceEvidence: '完成八节报告目录，并为每张图分别写“事实”和“解释”。',
        challenge: '选一张资金曲线，删掉所有形容词，只写可核对的数字事实。',
      },
      {
        focus: '以“能演示可信闭环”为完成标准，不以部署成功或功能数量代替研究成果。',
        pitfallDetails: [
          { why: '页面越多不代表数据时点、成本和样本外验证正确。', correction: '先证明一条最小策略证据链，再扩展功能。', selfCheck: '删掉 UI 后研究结论还能被测试和报告支持吗？' },
          { why: '服务可访问只是工程验收，不能证明因子有效。', correction: '分别报告系统可用性与研究有效性。', selfCheck: '线上健康检查与 OOS 指标回答的是同一个问题吗？' },
          { why: '历史回测尚未覆盖真实成交、容量和运营风险，直接实盘会放大错误。', correction: '先只读监控和模拟交易，建立更长期样本外记录。', selfCheck: '进入实盘前还有哪些执行、风控、合规和监控缺口？' },
        ],
        practiceEvidence: '能在 15 分钟内演示从数据、质量、舆情、评分、回测到报告的完整链路。',
        challenge: '列出进入模拟交易前仍缺少的五项能力，并按风险排序。',
      },
    ],
    lab: {
      title: '实验 11：按预先门槛评审毕业实验', goal: '让每个版本都留下结果和决策，而不是只挑最好看的一个。',
      datasetPath: 'learning/datasets/11_capstone_experiments.csv', datasetDescription: '四次实验的版本、股票池、OOS、回撤、换手和决策。',
      scriptPath: 'learning/labs/11_capstone_lab.py', command: '.\\.venv\\Scripts\\python.exe learning\\labs\\11_capstone_lab.py',
      steps: [
        { title: '冻结门槛', action: '先读 passes：OOS>0、回撤≥-15%、换手≤4。', expected: '三条标准在看单行结果前已确定。' },
        { title: '逐项评审', action: '执行脚本，让每个版本得到 PASS/REVIEW。', expected: 'EXP-002 与 EXP-004 通过。' },
        { title: '保留失败', action: '观察 EXP-003 的负 OOS 与停止调参决策。', expected: '失败记录没有被删除。' },
        { title: '做敏感性解释', action: '比较同版本不同股票池。', expected: '结果变化被记录为敏感性，而非自动宣称稳健。' },
      ],
      codeWalkthrough: [
        { code: 'oos_return > 0', explanation: '最低要求是在未参与调参的数据上没有负收益。' },
        { code: 'max_drawdown >= -0.15', explanation: '回撤门槛表达风险承受范围，负数越小越糟。' },
        { code: 'turnover <= 4.0', explanation: '限制交易频率，避免毛收益被成本吞掉。' },
        { code: 'PASS if passes(row) else REVIEW', explanation: '程序按事先标准执行，不按研究者喜好改判。' },
      ],
      expectedOutput: ['EXP-001 REVIEW', 'EXP-002 PASS', 'EXP-003 REVIEW', 'EXP-004 PASS', "passing_experiments=['EXP-002', 'EXP-004']", 'LAB_OK'],
      verification: ['标准早于结果存在', '所有失败版本仍在 CSV', '报告记录数据截止日、commit 和模型版本'],
    },
    readings: [
      { title: 'The Replication Crisis That Wasn’t', provider: 'AQR / Cliff Asness', url: 'https://www.aqr.com/insights/perspectives/the-replication-crisis-that-wasnt', takeaway: '公开从业观点提醒研究者考虑数据挖掘、比较基准、跨市场证据，并对回测成绩打折。', kind: '从业者经验' },
      { title: 'Backtesting Bias', provider: 'Robot Wealth / Kris Longmore', url: 'https://robotwealth.com/backtesting-bias-feels-good-until-you-blow-up/', takeaway: '把回测当作偏乐观的研究工具，而不是对未来收益的承诺。', kind: '从业者经验' },
    ],
  },
}
