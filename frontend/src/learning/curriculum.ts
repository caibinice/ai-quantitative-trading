export interface LearningStage {
  id: number
  title: string
  subtitle: string
  goal: string
}

export interface LearningResource {
  title: string
  provider: string
  url: string
  note: string
}

export interface LearningConcept {
  title: string
  summary: string
  points: string[]
}

export interface QuizQuestion {
  question: string
  options: string[]
  answer: number
  explanation: string
}

export interface LearningChapter {
  id: string
  order: number
  stage: number
  title: string
  subtitle: string
  duration: string
  level: string
  objective: string
  outcomes: string[]
  concepts: LearningConcept[]
  checklist: string[]
  projectFiles: Array<{ path: string; reason: string }>
  demo: {
    file: string
    command: string
    summary: string
    snippet: string
  }
  quiz: QuizQuestion[]
  resources: LearningResource[]
}

export const learningStages: LearningStage[] = [
  {
    id: 1,
    title: '建立地图',
    subtitle: '从软件工程走向金融市场',
    goal: '理清量化交易、AI 大模型与软件系统的边界，掌握金融市场交易机制与全流程数据流。',
  },
  {
    id: 2,
    title: '掌握数据语言',
    subtitle: '科学计算与时间序列底座',
    goal: '掌握 Python 科学计算栈、NumPy 向量化与 pandas 时间序列切片、对齐及滞后算子。',
  },
  {
    id: 3,
    title: '构建可信策略',
    subtitle: '因子工程、交易成本与历史回测',
    goal: '理解因子构造与仓位映射，杜绝未来函数，构建包含真实手续费与滑点的可信回测。',
  },
  {
    id: 4,
    title: '加入 AI 与验证',
    subtitle: '大模型舆情因子与样本外验证',
    goal: '使用大模型将非结构化新闻转化为结构化情绪因子，并通过滚动 Walk-forward 检验过拟合。',
  },
  {
    id: 5,
    title: '完成研究系统',
    subtitle: '工程化治理与毕业实战',
    goal: '构建自动化数据质量监控、任务幂等执行体系，独立交付完整的双因子量化研究报告。',
  },
]

const pythonResources: LearningResource[] = [
  {
    title: 'Python Tutorial',
    provider: 'Python 官方文档',
    url: 'https://docs.python.org/3/tutorial/',
    note: '适合具备通用编程经验的开发者快速查阅语法与标准库。',
  },
  {
    title: 'CS50’s Introduction to Programming with Python',
    provider: 'Harvard OpenCourseWare',
    url: 'https://cs50.harvard.edu/python/',
    note: '哈佛经典编程入门课，覆盖基础语法、数据结构、测试与综合项目。',
  },
]

const dataResources: LearningResource[] = [
  {
    title: 'NumPy Learn',
    provider: 'NumPy 官方',
    url: 'https://numpy.org/learn/',
    note: '从连续数组、向量化计算到广播机制的官方精选路径。',
  },
  {
    title: 'Getting started tutorials',
    provider: 'pandas 官方',
    url: 'https://pandas.pydata.org/docs/getting_started/intro_tutorials/',
    note: '覆盖表格读写、多维切片、时间索引、分组聚合与数据对齐。',
  },
]

export const learningChapters: LearningChapter[] = [
  {
    id: 'market-basics',
    order: 1,
    stage: 1,
    title: '股票与 K 线零基础',
    subtitle: '先看懂股票、OHLCV、成交量、复权与收益率',
    duration: '3–4 小时',
    level: '零基础',
    objective: '不依赖“炒股黑话”，从一笔交易如何形成日 K 线讲起，能够正确阅读本项目的行情页并手算基础收益。',
    outcomes: [
      '能区分股票、指数、ETF 和基准，知道股票价格不等于公司价值本身。',
      '能指出一根 K 线的开盘、最高、最低、收盘、实体和影线。',
      '能解释成交量、成交额、换手率、前复权和简单收益率。',
      '看到异常跳变时会先核对数据源和复权口径，而不是立即解释成交易信号。',
    ],
    concepts: [
      {
        title: '股票、指数、ETF 与交易',
        summary: '先理解你买的是什么、指数衡量什么，以及订单价格为什么不一定等于屏幕最后价。',
        points: [
          '股票代表公司所有权份额，收益和本金都不保证。',
          '指数是市场温度计，ETF 是可交易的一篮子基金。',
          '流动性、买卖价差和滑点决定理论价格能否成交。',
        ],
      },
      {
        title: '一根 K 线的 OHLCV',
        summary: 'K 线只是把一个周期的开盘、最高、最低、收盘与成交量压缩成图形，不是预言符号。',
        points: [
          '实体连接开盘与收盘，影线连接最高和最低。',
          '上涨色与下跌色取决于软件约定，要看图例。',
          '单根形态不能脱离前后价格、成交量与市场环境。',
        ],
      },
      {
        title: '复权、收益与风险',
        summary: '分红送股会制造机械价格断层；统一复权口径后，才能正确计算复利、波动和回撤。',
        points: [
          '前复权用于保持历史序列相对连续。',
          '累计收益需要连乘，涨跌百分比并不对称。',
          '收益必须与回撤、波动、成本和基准一起看。',
        ],
      },
    ],
    checklist: [
      '在行情页任选一根 K 线，写出开盘、最高、最低和收盘。',
      '用自己的话解释股票、指数与 ETF 的差别。',
      '手算 100 元涨 10% 再跌 10% 后的价格。',
      '说明为什么未复权和前复权价格不能混合计算动量。',
      '找到成交量、成交额和换手率，并解释单位。',
      '运行 00_kline_basics.py 教学 Demo。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'frontend/src/pages/Market.tsx', reason: '查看 K 线和成交量如何在 ECharts 中组合。' },
      { path: 'backend/app/services/provider.py', reason: '查看 AKShare OHLCV 字段怎样标准化。' },
      { path: 'backend/app/services/data_quality.py', reason: '查看 OHLC 关系、缺口和异常收益检查。' },
    ],
    demo: {
      file: 'learning/examples/00_kline_basics.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\00_kline_basics.py',
      summary: '输入两天 OHLC，检查 K 线关系并计算单日与累计收益。',
      snippet: `bars = [
    {"open": 10.20, "high": 10.80, "low": 9.90, "close": 10.50},
    {"open": 10.45, "high": 10.60, "low": 10.20, "close": 10.29},
]
returns = [bars[1]["close"] / bars[0]["close"] - 1]
assert all(bar["low"] <= min(bar["open"], bar["close"])
           <= max(bar["open"], bar["close"]) <= bar["high"] for bar in bars)`,
    },
    quiz: [
      {
        question: '一根日 K 线的实体连接哪两个价格？',
        options: ['最高价与最低价', '开盘价与收盘价', '前收盘价与成交均价'],
        answer: 1,
        explanation: '实体连接开盘和收盘；最高、最低通过上下影线表示。',
      },
      {
        question: '100 元先涨 10%，再跌 10%，最终是多少？',
        options: ['100 元', '99 元', '101 元'],
        answer: 1,
        explanation: '100×1.10×0.90=99；百分比作用在不同基数上。',
      },
      {
        question: '看到单日上涨 3000% 的前复权大盘股，第一步应做什么？',
        options: ['立即买入', '先核对数据源、复权和异常行', '把因子上限改得更高'],
        answer: 1,
        explanation: '这远超正常波动范围，首先应视作潜在数据污染并阻断评分。',
      },
    ],
    resources: [
      {
        title: '证券基础知识专题',
        provider: '上海证券交易所投资者教育',
        url: 'https://edu.sse.com.cn/',
        note: '从证券基础、风险教育、年报和 ETF 等官方投教栏目开始。',
      },
      {
        title: 'Stocks - FAQs',
        provider: 'Investor.gov',
        url: 'https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks',
        note: '用通俗语言解释股票所有权、收益来源、风险和交易费用。',
      },
      {
        title: 'Types of Orders',
        provider: 'Investor.gov',
        url: 'https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/types-orders',
        note: '理解市价单与限价单为何不能同时保证成交与成交价格。',
      },
    ],
  },
  {
    id: 'quant-map',
    order: 2,
    stage: 1,
    title: '量化、AI 量化与 Web3',
    subtitle: '先建立正确的问题地图',
    duration: '2–3 小时',
    level: '入门',
    objective: '理解这个项目究竟解决什么问题，以及为什么它不是预测明天涨跌的魔法。',
    outcomes: [
      '能用自己的话解释量化研究的“数据→信号→组合→回测→验证”闭环。',
      '能区分量化交易、AI 辅助量化、机器学习交易和 Web3。',
      '知道研究系统、模拟交易和真实交易之间的安全边界。',
    ],
    concepts: [
      {
        title: '量化究竟做什么',
        summary: '量化研究是把可重复的投资假设写成数据规则，再用历史和样本外数据检验。',
        points: [
          '策略不是一段买卖代码，而是一组可证伪的假设。',
          '收益之外还要看回撤、波动、换手、容量与稳定性。',
          '结果必须能追溯到当时可获得的数据和明确的执行时点。',
        ],
      },
      {
        title: 'AI 在系统中的三种角色',
        summary: 'AI 可以辅助开发、提取非结构化信息，也可以成为预测模型，但三者风险不同。',
        points: [
          'Codex 帮你写代码和测试，不证明策略有效。',
          '大模型把新闻与公告转换成结构化情绪，是本项目的 AI 主线。',
          '预测模型必须接受样本外验证，不能只比较训练期准确率。',
        ],
      },
      {
        title: 'Web3 与量化不是同一维度',
        summary: 'Web3 描述区块链资产和去中心化基础设施；量化描述研究和交易的方法。',
        points: [
          '可以做加密资产量化，但量化并不等于 Web3。',
          '本项目研究 A 股日线、财务和新闻，不涉及链、钱包或智能合约。',
          '先掌握低频研究闭环，再考虑市场和资产类别扩展。',
        ],
      },
    ],
    checklist: [
      '画出本项目从 AKShare 到前端页面的数据流。',
      '解释“相关性不等于可交易信号”。',
      '列出研究模式与实盘系统至少 3 个差异。',
      '找到页面上的“不连接券商”提示。',
      '写下一个可以被历史数据否定的策略假设。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'README.md', reason: '先读能力边界、技术架构和真实数据工作流。' },
      { path: 'backend/app/services/pipeline.py', reason: '观察数据采集、情绪分析和评分如何组成流水线。' },
      { path: 'frontend/src/pages/Dashboard.tsx', reason: '理解研究结果如何被组织成可读界面。' },
    ],
    demo: {
      file: 'learning/examples/01_python_bridge.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\01_python_bridge.py',
      summary: '第一个 Hello Quant：计算单期收益、累计收益和最大回撤。',
      snippet: `prices = [100.0, 102.0, 99.0, 105.0]
returns = [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]
equity = 100_000
for daily_return in returns:
    equity *= 1 + daily_return`,
    },
    quiz: [
      {
        question: '量化研究最核心的产物是什么？',
        options: ['一只保证上涨的股票', '可重复、可证伪的研究流程', '越复杂越好的模型'],
        answer: 1,
        explanation: '量化的价值首先是让假设、数据、规则和结果可重复、可审计。',
      },
      {
        question: '本项目中的大模型主要负责什么？',
        options: ['直接下单', '保证收益', '把新闻公告转换为结构化情绪信息'],
        answer: 2,
        explanation: '大模型输出情绪标签、分数和理由，后续仍需规则与回测验证。',
      },
      {
        question: 'Web3 和量化的关系更接近哪一种？',
        options: ['两者完全等价', '资产/基础设施与研究方法的不同维度', '量化是 Web3 的子语言'],
        answer: 1,
        explanation: 'Web3 更偏资产和技术生态，量化是一套数据研究与交易方法。',
      },
    ],
    resources: [
      {
        title: 'CS 7646: Machine Learning for Trading',
        provider: 'Georgia Tech OMSCS',
        url: 'https://omscs.gatech.edu/cs-7646-machine-learning-trading',
        note: '课程按金融数据、计算投资和机器学习交易三个部分组织。',
      },
      {
        title: 'Python Programming for Economics and Finance',
        provider: 'QuantEcon',
        url: 'https://python-programming.quantecon.org/',
        note: '科研计算与经济金融 Python 的开放课程。',
      },
    ],
  },
  {
    id: 'project-tour',
    order: 3,
    stage: 1,
    title: '项目架构导览与研究闭环',
    subtitle: '把软件工程经验映射到量化系统',
    duration: '3–4 小时',
    level: '入门',
    objective: '理解全栈量化系统的分层架构，掌握前端交互、API 路由、异步任务队列、领域服务与 MySQL 数据库之间的端到端数据流。',
    outcomes: [
      '能说明 React、FastAPI、Worker、MySQL 和外部数据源的职责划分。',
      '能从前端按钮追踪到 API 路由、任务队列与领域服务函数。',
      '能运行演示数据并清晰分辨模拟测试数据与真实行情源。',
    ],
    concepts: [
      {
        title: '全栈量化系统的分层架构映射',
        summary: 'FastAPI 提供路由分发与依赖注入，Pydantic 承担入参校验，service 模块封装核心量化算法。',
        points: [
          'Pydantic Schema 承担强类型的请求与响应数据契约。',
          'React 页面专注于交互与可视化展示，不直接在浏览器端执行密集计算。',
          '独立异步 Worker 消费持久化队列任务，保障长耗时计算不阻塞 HTTP 响应。',
        ],
      },
      {
        title: '异步研究任务的生命周期与状态机',
        summary: '前端触发入队，Worker 通过行锁认领任务、实时上报进度、调用领域算法并保存结果。',
        points: [
          '任务流转遵循 queued → running → success / failed / cancelled 明确状态机。',
          '任务 payload 记录不可变的输入参数快照，确保任何历史实验均可复查。',
          '支持任务安全重试与取消，需注意保持下游副作用的幂等性。',
        ],
      },
      {
        title: '量化研究的数据分层治理',
        summary: '原始行情、点时财务、新闻文本、AI 情绪标签与回测结果实行分层持久化。',
        points: [
          '原始数据层完整保留来源标识（source）与入库时间戳。',
          '派生特征层绑定计算参数、Prompt 模板、模型版本与生成环境。',
          '数据展示层仅读取持久化结果，不擅自修改底层研究数据。',
        ],
      },
    ],
    checklist: [
      '执行 setup 脚本并确认依赖安装成功。',
      '启动 API、Worker 和前端。',
      '打开 /quant/docs 并找到 tasks 接口（本地直连 API 时也可使用 /docs）。',
      '在任务中心观察一次任务状态变化。',
      '从 Strategy.tsx 追踪到 task_queue.py。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'scripts/setup.ps1', reason: '理解环境初始化和演示数据入口。' },
      { path: 'scripts/dev.ps1', reason: '查看 API、Worker 与 Vite 如何一起启动。' },
      { path: 'backend/app/services/task_queue.py', reason: '追踪任务认领、执行、重试和取消。' },
    ],
    demo: {
      file: 'README.md',
      command: 'pwsh -File scripts\\dev.ps1',
      summary: '启动完整研究舱，并通过 /docs 和任务中心追踪一次请求。',
      snippet: `前端操作
  → POST /quant/api/tasks
  → aq_research_tasks
  → python -m app.worker
  → service function
  → MySQL result
  → React polling`,
    },
    quiz: [
      {
        question: '为什么外部数据同步不直接在前端请求中同步完成？',
        options: ['React 不能发送 HTTP 请求', '长任务需要持久化、支持断点重试并实时上报进度', 'MySQL 只能由 Worker 独占访问'],
        answer: 1,
        explanation: '任务队列让耗时流程脱离 HTTP 请求生命周期，避免超时并保留审计状态与错误信息。',
      },
      {
        question: 'Pydantic Schema 在全栈架构中主要承担什么职责？',
        options: ['数据契约定义与运行时强校验', '编译为底层 JVM 字节码', '管理前端 CSS 模块样式'],
        answer: 0,
        explanation: 'Schema 严格描述输入输出数据结构，并在运行时自动完成类型转换与边界校验。',
      },
      {
        question: '研究结果若要满足可审计要求，至少需要保留什么？',
        options: ['只保留最终收益数字', '输入参数、数据时间戳与生成环境上下文', '只保留前端可视化截图'],
        answer: 1,
        explanation: '缺少输入参数与时点上下文，实验结果将无法科学复现或排查未来数据污染。',
      },
    ],
    resources: [
      {
        title: 'FastAPI Tutorial',
        provider: 'FastAPI 官方',
        url: 'https://fastapi.tiangolo.com/tutorial/',
        note: '用于理解依赖注入、请求模型校验和 API 路由设计。',
      },
      {
        title: 'SQLAlchemy Unified Tutorial',
        provider: 'SQLAlchemy 官方',
        url: 'https://docs.sqlalchemy.org/en/20/tutorial/',
        note: '掌握模型定义、Session 会话管理与现代查询构建。',
      },
    ],
  },
  {
    id: 'python-bridge',
    order: 4,
    stage: 2,
    title: '面向开发者的 Python 科学计算进阶',
    subtitle: '掌握动态类型、引用语义、切片与测试规范',
    duration: '1 周',
    level: '基础',
    objective: '快速掌握 Python 核心机制、引用语义、推导式与生成器，熟练运用 pytest 编写健壮的金融计算代码。',
    outcomes: [
      '深入理解动态类型、引用语义、可变对象陷阱、切片操作与上下文管理器。',
      '能规范使用虚拟环境、模块导入、异常处理和 pytest 测试框架。',
      '清晰识别 Python 原生循环与 NumPy/pandas 向量化计算的性能边界。',
    ],
    concepts: [
      {
        title: 'Python 对象模型与引用语义',
        summary: '重点掌握变量引用传递、可变默认参数陷阱、None 单例判断与类型提示机制。',
        points: [
          'list 与 dict 为可变对象，tuple 与 str 为不可变对象。',
          'is 比较对象内存身份，== 比较对象数据值；None 判断使用 is None。',
          '类型提示主要用于静态检查与代码可读性，在运行时需结合 Pydantic 等工具生效。',
        ],
      },
      {
        title: 'Pythonic 数据处理与资源管理',
        summary: '推导式、生成器、zip/enumerate 与 dataclass 能够大幅提升数据处理的简洁度与可读性。',
        points: [
          '简单映射筛选优先使用推导式，多层嵌套或复杂分支应提取为命名清晰的函数。',
          '大规模数据计算应优先采用向量化操作，避免逐行纯 Python 循环。',
          'with 上下文管理器确保数据库连接、文件句柄和锁资源的确定性释放。',
        ],
      },
      {
        title: '金融计算代码的测试与异常定位',
        summary: '通过 pytest 针对边界条件（空数据、NaN、除零、极端值）编写自动化回归测试。',
        points: [
          'pytest 支持使用纯函数与简单 assert 快速搭建单元测试用例。',
          '无副作用的纯函数最适合构造极端行情与边界样例。',
          '金融代码必须显式覆盖空数据、NaN 缺失值、除零与时序错位等场景。',
        ],
      },
    ],
    checklist: [
      '使用列表推导式和生成器重写一段数据映射与过滤逻辑。',
      '解释 list、tuple、dict、set 在不同场景下的选择依据。',
      '编写一个带有类型注解和 docstring 的收益率计算函数。',
      '制造并分析一次 IndexError 或 KeyError 的 traceback 堆栈。',
      '在本地运行 backend 的 pytest 单元测试套件。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/schemas.py', reason: '观察类型注解、默认值与 Pydantic 校验器。' },
      { path: 'backend/app/services/scoring.py', reason: '阅读小型纯函数与 NumPy 数值计算实现。' },
      { path: 'backend/tests/test_scoring.py', reason: '学习 pytest 的 Arrange–Act–Assert 测试组织模式。' },
    ],
    demo: {
      file: 'learning/examples/01_python_bridge.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\01_python_bridge.py',
      summary: '使用列表推导式与 zip 构建收益率计算函数。',
      snippet: `def simple_returns(prices: list[float]) -> list[float]:
    if len(prices) < 2:
        return []
    return [
        current / previous - 1
        for previous, current in zip(prices, prices[1:])
    ]`,
    },
    quiz: [
      {
        question: 'Python 类型注解（Type Hints）的标准运行机制是什么？',
        options: ['在运行前强制由解释器严格编译检查', '提升可读性并供静态检查工具使用，默认不阻止程序运行', '自动将错误类型强制转换为目标类型'],
        answer: 1,
        explanation: 'mypy 与 IDE 可利用注解进行静态检查，但标准 CPython 解释器在运行时不会强制拦截类型不符。',
      },
      {
        question: '在 Python 中判断一个变量是否为 None，推荐使用哪种写法？',
        options: ['value == None', 'value is None', 'Boolean(value)'],
        answer: 1,
        explanation: 'None 是全局唯一的单例对象，使用身份比较运算符 is 更加高效且符合 Pythonic 规范。',
      },
      {
        question: '在大规模时间序列数据上进行收益率计算时，优先选择哪种实现方式？',
        options: ['多层嵌套的纯 Python for 循环', 'pandas / NumPy 向量化算子', '深度递归函数'],
        answer: 1,
        explanation: '向量化算子底层使用 C/Fortran 实现连续内存批量计算，吞吐性能比纯 Python 循环高出数个数量级。',
      },
    ],
    resources: pythonResources,
  },
  {
    id: 'numpy-pandas',
    order: 5,
    stage: 2,
    title: 'NumPy、pandas 与时间序列',
    subtitle: '量化研究真正的基础语言',
    duration: '1–2 周',
    level: '基础',
    objective: '能清洗 OHLCV、计算收益与滚动指标，并明确处理索引对齐和缺失值。',
    outcomes: [
      '能区分 ndarray、Series 与 DataFrame。',
      '能使用 pct_change、shift、rolling、groupby、merge 和 reindex。',
      '能解释为什么自动索引对齐既强大又危险。',
    ],
    concepts: [
      {
        title: '数组、标签与向量化',
        summary: 'NumPy 管连续数组和数值运算，pandas 在其上增加行列标签与缺失值语义。',
        points: [
          'shape、dtype、axis 决定数组计算含义。',
          'Series 是带索引的一维向量，DataFrame 是列式二维表。',
          '向量化不等于没有循环，而是循环下沉到底层实现。',
        ],
      },
      {
        title: '时间索引与对齐',
        summary: '两个 Series 运算时会按标签对齐，不会按肉眼看到的行号强行相加。',
        points: [
          '日期必须解析、排序并去重。',
          'reindex 后出现 NaN 是正常信号，不应无脑 fillna。',
          '交易日历用于区分“休市”与“数据缺失”。',
        ],
      },
      {
        title: '滚动窗口与滞后',
        summary: 'rolling 描述过去窗口，shift(1) 把今天产生的信号推迟到下一交易日使用。',
        points: [
          '收益率通常是 price.pct_change()。',
          '滚动统计前几期自然没有足够观察值。',
          '任何使用当日收盘产生的信号都不能假设按同一收盘价成交。',
        ],
      },
    ],
    checklist: [
      '构造一个 DatetimeIndex 的价格 Series。',
      '计算单期收益和 20 日滚动波动率。',
      '演示两个不同日期索引 Series 的自动对齐。',
      '用交易日历找出缺失行情。',
      '解释 shift(1) 对信号执行的意义。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/services/provider.py', reason: '观察外部表格如何规范化为标准字段。' },
      { path: 'backend/app/services/backtest.py', reason: '阅读 concat、pct_change、reindex、shift 和 cumprod。' },
      { path: 'backend/app/services/data_quality.py', reason: '理解时间序列质量检查。' },
    ],
    demo: {
      file: 'learning/examples/02_pandas_timeseries.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\02_pandas_timeseries.py',
      summary: '构建交易日价格序列，计算动量、波动率并故意制造一个缺口。',
      snippet: `prices = pd.Series([100, 102, 101, 105], index=dates, dtype=float)
returns = prices.pct_change()
momentum = prices / prices.shift(2) - 1
applied_signal = (momentum > 0).astype(float).shift(1).fillna(0.0)`,
    },
    quiz: [
      {
        question: '两个 pandas Series 相加时默认按什么对齐？',
        options: ['物理行号', '索引标签', '内存地址'],
        answer: 1,
        explanation: 'pandas 使用索引标签对齐，因此日期不一致时会产生 NaN。',
      },
      {
        question: 'rolling(20) 前 19 行通常为什么是 NaN？',
        options: ['程序错误', '观察数不足', '价格必须为整数'],
        answer: 1,
        explanation: '默认需要完整窗口，前 19 行没有 20 个历史观察。',
      },
      {
        question: '信号 shift(1) 的主要目的是什么？',
        options: ['提高收益', '降低内存', '避免用产生信号的同一价格执行'],
        answer: 2,
        explanation: '它把信息产生和可交易执行分开，是避免未来数据的基础。',
      },
    ],
    resources: dataResources,
  },
  {
    id: 'market-data',
    order: 6,
    stage: 3,
    title: '行情、财务与收益风险',
    subtitle: '从数据字段走向金融含义',
    duration: '1 周',
    level: '基础进阶',
    objective: '理解股票数据、公司行动、财务可得时间和常用绩效指标。',
    outcomes: [
      '能解释 OHLCV、复权、停牌、涨跌停和基准。',
      '能计算简单/对数收益、年化收益、波动率、最大回撤和夏普。',
      '能解释报告期与公告日为什么必须分开。',
    ],
    concepts: [
      {
        title: '价格不是一个简单数字',
        summary: '原始价、前复权、后复权服务不同目的，混用会制造虚假跳变。',
        points: [
          '研究收益通常需要一致的复权口径。',
          '停牌不是收益为零这么简单，实盘还涉及不可成交。',
          '指数基准必须和策略区间、频率、币种一致。',
        ],
      },
      {
        title: '风险收益指标',
        summary: '累计收益回答赚了多少，回撤回答过程中最痛苦的损失，夏普衡量单位波动的超额收益。',
        points: [
          '年化不能简单把短期收益乘 252。',
          '最大回撤来自资金曲线相对历史峰值的跌幅。',
          '夏普对分布、频率和无风险利率假设敏感。',
        ],
      },
      {
        title: '点时财务',
        summary: '2025 年年报的报告期是 2025-12-31，但市场只能在公告日之后使用。',
        points: [
          'report_date 描述业绩归属期。',
          'available_at 描述研究者首次可见日期。',
          '回测必须查询 available_at <= as_of。',
        ],
      },
    ],
    checklist: [
      '解释前复权与后复权用途。',
      '手算 4 个价格点的累计收益。',
      '画出一条资金曲线并标记最大回撤。',
      '在数据库中找到沪深 300 指数表。',
      '检查点时财务查询是否限制 available_at。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/models.py', reason: '查看 DailyPrice、IndexPrice 与 PointInTimeFinancial。' },
      { path: 'backend/app/services/infrastructure.py', reason: '理解日历、指数与财务同步。' },
      { path: 'frontend/src/pages/DataQuality.tsx', reason: '查看数据覆盖与质量如何展示。' },
    ],
    demo: {
      file: 'learning/examples/02_pandas_timeseries.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\02_pandas_timeseries.py',
      summary: '输出累计收益、年化波动和数据缺口。',
      snippet: `equity = 100_000 * (1 + returns.fillna(0)).cumprod()
drawdown = equity / equity.cummax() - 1
max_drawdown = drawdown.min()
annualized_volatility = returns.std(ddof=1) * (252 ** 0.5)`,
    },
    quiz: [
      {
        question: '财务因子历史回测应按什么时间判断可用？',
        options: ['报告期末', '真实公告日', '数据库插入日'],
        answer: 1,
        explanation: '只有公告发布后，市场参与者才可能获得该信息。',
      },
      {
        question: '最大回撤衡量什么？',
        options: ['最低单日收益', '资金曲线从历史峰值到后续谷底的最大跌幅', '收益标准差'],
        answer: 1,
        explanation: '最大回撤是路径相关风险，不等同于单日亏损。',
      },
      {
        question: '策略基准最重要的要求是什么？',
        options: ['一定上涨', '与策略可比较且数据真实', '名称好听'],
        answer: 1,
        explanation: '基准应匹配市场和时间区间，不能用不相关序列替代。',
      },
    ],
    resources: [
      {
        title: 'AKShare 股票数据',
        provider: 'AKShare 官方文档',
        url: 'https://akshare.akfamily.xyz/data/stock/stock.html',
        note: '查看行情、财务、新闻和公告接口字段。',
      },
      {
        title: 'AKShare 指数数据',
        provider: 'AKShare 官方文档',
        url: 'https://akshare.akfamily.xyz/data/index/index.html',
        note: '了解指数历史行情接口和代码格式。',
      },
    ],
  },
  {
    id: 'factor-backtest',
    order: 7,
    stage: 3,
    title: '因子、信号与可信回测',
    subtitle: '漂亮曲线之前先证明没有作弊',
    duration: '1–2 周',
    level: '进阶',
    objective: '从经济假设构造因子，把分数转换为仓位，并正确计入执行延迟与成本。',
    outcomes: [
      '能区分特征、因子、信号、权重和收益。',
      '能识别未来函数、幸存者偏差、参数挖掘和重复计算成本。',
      '能读懂当前双因子回测实现。',
    ],
    concepts: [
      {
        title: '从因子到仓位',
        summary: '动量或情绪先形成分数，再通过门槛、排序和 top_n 转换为目标权重。',
        points: [
          '因子值不是直接收益。',
          '横截面排名回答“相对谁更好”，时间序列门槛回答“现在是否参与”。',
          '权重总和、单票上限和空仓规则必须明确。',
        ],
      },
      {
        title: '交易成本与换手',
        summary: '目标仓位变化产生换手，换手乘手续费与滑点会直接减少净收益。',
        points: [
          '频繁调仓可能把毛收益全部吃掉。',
          '买入和卖出都可能产生成本。',
          '实盘成本还包括冲击、涨跌停和容量。',
        ],
      },
      {
        title: '回测四大泄漏',
        summary: '未来数据、幸存者偏差、数据修订和参数过拟合会让历史结果虚高。',
        points: [
          '信号至少延迟一根 K 线。',
          '股票池不能只保留今天还存在的赢家。',
          '调参使用的数据不能再次充当最终测试集。',
        ],
      },
    ],
    checklist: [
      '画出因子→信号→目标权重→执行权重。',
      '找到 applied_weights 的 shift(1)。',
      '手算一次换仓成本。',
      '写一个未来数据泄漏的反例。',
      '运行回测测试并解释每个断言。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/services/scoring.py', reason: '理解动量、质量与情绪分数组合。' },
      { path: 'backend/app/services/backtest.py', reason: '核心回测、延迟、成本与绩效。' },
      { path: 'backend/tests/test_backtest.py', reason: '未来舆情、信号延迟和成本回归测试。' },
    ],
    demo: {
      file: 'learning/examples/03_signal_delay.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\03_signal_delay.py',
      summary: '对比“同日执行”的错误回测与延迟一日的可交易回测。',
      snippet: `signal = (prices > prices.rolling(3).mean()).astype(float)
wrong_position = signal
tradable_position = signal.shift(1).fillna(0.0)
net_return = tradable_position * prices.pct_change() - turnover * cost_rate`,
    },
    quiz: [
      {
        question: '因子和仓位的关系是什么？',
        options: ['因子天然等于仓位', '需要经过规则映射和风险约束', '仓位只由随机数决定'],
        answer: 1,
        explanation: '因子表达信息，组合规则才把它转换为可执行权重。',
      },
      {
        question: '当日收盘产生的信号为什么要 shift(1)？',
        options: ['否则图不好看', '当日收盘价已知后通常无法再按同一收盘成交', '为了减少数据量'],
        answer: 1,
        explanation: '信息可用时点必须早于执行时点。',
      },
      {
        question: '换手提高通常带来什么？',
        options: ['成本上升', '成本自动下降', '最大回撤必然为零'],
        answer: 0,
        explanation: '换手越高，手续费、滑点和冲击成本通常越高。',
      },
    ],
    resources: [
      {
        title: 'CS 7646: Machine Learning for Trading',
        provider: 'Georgia Tech OMSCS',
        url: 'https://omscs.gatech.edu/cs-7646-machine-learning-trading',
        note: '参考其金融数据、计算投资和机器学习交易的递进组织。',
      },
      {
        title: 'pandas Time Series',
        provider: 'pandas 官方',
        url: 'https://pandas.pydata.org/docs/user_guide/timeseries.html',
        note: '深入理解 shift、窗口、频率和时间索引。',
      },
    ],
  },
  {
    id: 'sentiment-llm',
    order: 8,
    stage: 4,
    title: '舆情因子与大模型',
    subtitle: '把文本判断变成可审计数据',
    duration: '1 周',
    level: '进阶',
    objective: '理解新闻采集、结构化情绪输出、时间衰减、降级策略和模型风险。',
    outcomes: [
      '能定义情绪标签、连续分数、置信度、摘要和理由。',
      '能解释为什么保存原文、发布时间、模型名和分析结果。',
      '能设计无 API 时可复现的规则降级。',
    ],
    concepts: [
      {
        title: '文本到结构化因子',
        summary: '大模型不是返回一段散文，而是返回符合 Schema 的可验证字段。',
        points: [
          'label ∈ 利好/中性/利空。',
          'score 使用固定区间，confidence 表达模型自信而非正确概率。',
          'rationale 要能回到原文复核，不能凭空补充事实。',
        ],
      },
      {
        title: '事件时间与衰减',
        summary: '舆情影响通常随时间衰减，未来发布的事件不能进入过去的评分。',
        points: [
          'published_at 是核心时间边界。',
          '指数衰减让近期事件权重更高。',
          '同一股票的重复事件先用 hash 精确去重，再按链接、标题、梗概和时间做约 90% 近似去重。',
        ],
      },
      {
        title: '模型风险与评估',
        summary: '情绪标签可能受提示词、模型版本、文本缺失和市场语境影响。',
        points: [
          '抽样人工复核混淆矩阵。',
          '模型升级后应保留旧版本结果或重新建立基线。',
          'API 失败时应明确降级，不应静默生成伪结果。',
        ],
      },
    ],
    checklist: [
      '阅读情绪输出 Schema。',
      '解释 score 与 confidence 的差异。',
      '找到未来新闻过滤条件。',
      '对 10 条事件做一次人工复核。',
      '关闭 LLM 并验证规则降级可重复。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/services/sentiment.py', reason: '结构化输出、JSON 提取和规则降级。' },
      { path: 'backend/app/models.py', reason: 'NewsItem 与 SentimentAnalysis 的审计字段。' },
      { path: 'frontend/src/pages/Sentiment.tsx', reason: '查看标签、分数、置信度和理由。' },
    ],
    demo: {
      file: 'learning/examples/04_sentiment_factor.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\04_sentiment_factor.py',
      summary: '用固定事件构造带时间衰减的情绪分数，再与动量组合。',
      snippet: `age_days = (as_of - published_at).days
weight = confidence * math.exp(-age_days / 7)
weighted_sentiment = sum(score * weight for score, weight in events) / sum(weights)
total_score = 0.7 * momentum_score + 0.3 * sentiment_score`,
    },
    quiz: [
      {
        question: '为什么情绪分析要输出结构化 JSON？',
        options: ['为了文本更长', '便于校验、存储、比较和回测', '为了绕过数据库'],
        answer: 1,
        explanation: '稳定字段才能成为可重复的数据资产和因子输入。',
      },
      {
        question: 'confidence=0.9 是否意味着 90% 一定正确？',
        options: ['是', '不是，它只是模型自报置信度，需要校准', '表示收益 90%'],
        answer: 1,
        explanation: '模型置信度不是天然校准后的真实概率。',
      },
      {
        question: '昨天发布的新闻能否影响上周的回测信号？',
        options: ['可以', '不可以', '只要是利好就可以'],
        answer: 1,
        explanation: 'published_at 晚于评分日的数据属于未来信息。',
      },
    ],
    resources: [
      {
        title: 'Pydantic Models',
        provider: 'Pydantic 官方',
        url: 'https://docs.pydantic.dev/latest/concepts/models/',
        note: '学习如何定义和验证结构化模型输出。',
      },
      {
        title: 'Natural Language Processing',
        provider: 'scikit-learn 官方',
        url: 'https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html',
        note: '理解文本特征与传统分类基线，避免只依赖大模型。',
      },
    ],
  },
  {
    id: 'walk-forward',
    order: 9,
    stage: 4,
    title: 'Walk-forward 与过拟合',
    subtitle: '最终只相信未参与选择的数据',
    duration: '1 周',
    level: '进阶',
    objective: '能设计训练、验证、测试的时间顺序，并解释每个滚动窗口的参数选择。',
    outcomes: [
      '理解普通 KFold 为什么不适合有时间顺序的数据。',
      '能区分样本内优化与样本外评价。',
      '能审计每个 Walk-forward 窗口的训练和测试区间。',
    ],
    concepts: [
      {
        title: '时间序列验证',
        summary: '训练只能使用过去，测试必须发生在参数选择之后。',
        points: [
          '不能随机打乱时间样本。',
          '必要时在训练与测试之间留 gap 防止标签重叠。',
          '每个窗口只将样本外收益拼入最终曲线。',
        ],
      },
      {
        title: '参数选择与数据窥探',
        summary: '如果看过测试结果再改参数，测试集就已经变成训练的一部分。',
        points: [
          '参数网格应在实验前定义。',
          '选择目标要同时考虑收益、夏普和回撤。',
          '反复尝试的实验次数本身也是过拟合来源。',
        ],
      },
      {
        title: '结果解释',
        summary: '样本外亏损并不等于代码失败，它可能诚实地否定了策略假设。',
        points: [
          '比较不同市场阶段和窗口稳定性。',
          '记录参数漂移而不是只看最终收益。',
          '先检查数据和实现，再讨论经济原因。',
        ],
      },
    ],
    checklist: [
      '画出一个训练 126 日、测试 42 日的滚动窗口。',
      '解释随机 KFold 的时间泄漏。',
      '运行一次 Walk-forward。',
      '检查每个测试起点都晚于训练终点。',
      '说明样本外亏损为何仍是有价值结果。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/services/walkforward.py', reason: '参数网格、窗口切分和样本外拼接。' },
      { path: 'backend/tests/test_walkforward.py', reason: '验证最终曲线从第一个测试窗口开始。' },
      { path: 'frontend/src/pages/WalkForward.tsx', reason: '审计每个窗口的参数与绩效。' },
    ],
    demo: {
      file: 'learning/examples/05_walk_forward.py',
      command: '.\\.venv\\Scripts\\python.exe learning\\examples\\05_walk_forward.py',
      summary: '在训练段选择移动平均窗口，再只报告下一段测试收益。',
      snippet: `for train_start, train_end, test_end in windows:
    best_window = max(candidates, key=lambda n: train_score(prices, n))
    test_return = evaluate(prices[train_end:test_end], best_window)
    out_of_sample_returns.append(test_return)`,
    },
    quiz: [
      {
        question: '为什么不能对时间序列随机 KFold？',
        options: ['运行太慢', '可能用未来训练、过去测试', '不能计算平均值'],
        answer: 1,
        explanation: '随机打乱会破坏信息可得顺序。',
      },
      {
        question: '测试集看完后再调参会发生什么？',
        options: ['测试集被污染', '模型自动更稳健', '没有影响'],
        answer: 0,
        explanation: '测试结果参与决策后，它就不再是独立样本外评价。',
      },
      {
        question: '最终 Walk-forward 曲线应包含什么？',
        options: ['所有训练期和测试期', '只包含各窗口样本外测试收益', '只包含最好窗口'],
        answer: 1,
        explanation: '训练期用于选参数，不应计入最终样本外绩效。',
      },
    ],
    resources: [
      {
        title: 'TimeSeriesSplit',
        provider: 'scikit-learn 官方',
        url: 'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html',
        note: '官方说明时间顺序数据为什么需要专用切分。',
      },
      {
        title: 'Cross-validation: evaluating estimator performance',
        provider: 'scikit-learn 官方',
        url: 'https://scikit-learn.org/stable/modules/cross_validation.html',
        note: '理解训练、验证、测试与交叉验证。',
      },
    ],
  },
  {
    id: 'research-engineering',
    order: 10,
    stage: 5,
    title: '研究工程化与数据治理',
    subtitle: '让实验明天还能重复运行',
    duration: '1 周',
    level: '工程进阶',
    objective: '掌握数据库、任务队列、幂等、质量规则、配置和可观测性在研究系统中的作用。',
    outcomes: [
      '能解释为什么任务和研究结果需要持久化。',
      '能设计幂等的数据 upsert 与可重试任务。',
      '能新增一条数据质量规则并测试。',
    ],
    concepts: [
      {
        title: '幂等与可重试',
        summary: '同一同步任务执行两次不应产生重复数据或破坏真实数据。',
        points: [
          '业务唯一键比自增 id 更能描述重复。',
          'upsert 前要明确哪些字段可以被更新。',
          '演示种子不能覆盖真实源记录。',
        ],
      },
      {
        title: '质量不是一个布尔值',
        summary: '质量规则应记录类别、实体、严重性、证据、首次/最近发现和解决时间。',
        points: [
          'OHLC 合法性、日期缺口和价格跳变是不同问题。',
          '告警要能去重并在问题消失后解决。',
          '阈值应配置化并接受误报复核。',
        ],
      },
      {
        title: '配置与秘密',
        summary: '参数进环境变量或配置，凭证永远不进入仓库、日志和截图。',
        points: [
          '.env.example 只放占位符。',
          '任务 payload 不应携带 API key。',
          '日志要记录上下文，但必须脱敏。',
        ],
      },
    ],
    checklist: [
      '解释任务认领时为什么需要行锁。',
      '验证 seed_demo 连续运行不会重复污染。',
      '查看一个质量告警 fingerprint。',
      '新增或修改一条纯函数质量规则。',
      '运行敏感信息扫描。',
      '完成本章测验且得分不低于 2/3。',
    ],
    projectFiles: [
      { path: 'backend/app/services/repository.py', reason: '学习批量预取和幂等 upsert。' },
      { path: 'backend/app/services/task_queue.py', reason: '学习数据库任务状态机。' },
      { path: 'backend/app/services/data_quality.py', reason: '质量规则、告警去重和解决。' },
    ],
    demo: {
      file: 'backend/scripts/seed_demo.py',
      command: '.\\.venv\\Scripts\\python.exe backend\\scripts\\seed_demo.py',
      summary: '连续运行两次，观察真实基础数据不会被演示数据覆盖。',
      snippet: `existing = db.scalar(
    select(PointInTimeFinancial.id).where(
        PointInTimeFinancial.symbol == symbol,
        PointInTimeFinancial.source != "demo",
    )
)
if not existing:
    seed_demo_financials()`,
    },
    quiz: [
      {
        question: '幂等同步的含义是什么？',
        options: ['只能运行一次', '重复执行得到一致状态且不产生重复副作用', '每次生成随机数据'],
        answer: 1,
        explanation: '网络任务会重试，幂等是安全重试的基础。',
      },
      {
        question: 'API key 应该放在哪里？',
        options: ['提交到 README', '环境变量或受控凭证存储', '任务错误消息'],
        answer: 1,
        explanation: '仓库、日志和任务 payload 都不应包含真实凭证。',
      },
      {
        question: '质量告警为什么需要 fingerprint？',
        options: ['用于画图', '用于识别同一问题并去重/更新', '用于替代数据库主键'],
        answer: 1,
        explanation: '稳定指纹让同一实体同一问题更新 last_seen，而不是无限新增。',
      },
    ],
    resources: [
      {
        title: 'SQLAlchemy ORM Quick Start',
        provider: 'SQLAlchemy 官方',
        url: 'https://docs.sqlalchemy.org/en/20/orm/quickstart.html',
        note: '复习模型、Session、查询和事务。',
      },
      {
        title: 'pytest documentation',
        provider: 'pytest 官方',
        url: 'https://docs.pytest.org/en/stable/',
        note: '为数据规则、任务状态机和边界条件编写测试。',
      },
    ],
  },
  {
    id: 'capstone',
    order: 11,
    stage: 5,
    title: '毕业项目：一份可信的策略研究',
    subtitle: '成果不是收益数字，而是完整证据链',
    duration: '1–2 周',
    level: '综合实战',
    objective: '独立完成一个从假设、数据、舆情、回测到样本外验证的研究报告。',
    outcomes: [
      '能提出一个具有经济逻辑且可证伪的双因子假设。',
      '能运行全流程并保存参数、数据范围、指标和局限。',
      '能在结果不理想时给出诚实、可行动的结论。',
    ],
    concepts: [
      {
        title: '毕业项目标准',
        summary: '选择 3–10 只股票和一个明确区间，避免通过扩大搜索空间寻找漂亮答案。',
        points: [
          '事先写下假设和成功/失败判据。',
          '固定交易成本、基准、参数候选和样本外方案。',
          '所有结论区分事实、推断和待验证假设。',
        ],
      },
      {
        title: '研究报告结构',
        summary: '报告应让另一个开发者在不知道答案的情况下复现实验。',
        points: [
          '摘要、假设、数据、方法、结果、稳健性、局限、下一步。',
          '同时展示策略与基准、收益与回撤、训练与样本外。',
          '附上失败实验与参数变化记录。',
        ],
      },
      {
        title: '最终成果',
        summary: '完成后你拥有的是一个可持续迭代的研究平台，而不是实盘承诺。',
        points: [
          '能扩展数据源、因子和质量规则。',
          '能判断结果是否值得继续研究。',
          '进入模拟盘前仍需补撮合、风险、监控与合规。',
        ],
      },
    ],
    checklist: [
      '提交一页研究假设与预注册参数。',
      '完成真实数据同步和质量检查。',
      '完成情绪分析与因子评分。',
      '完成含成本和真实基准的历史回测。',
      '完成 Walk-forward 并解释每个窗口。',
      '提交研究报告并列出至少 5 个局限。',
      '运行全部自动化测试与前端构建。',
      '完成本章测验且得分 3/3。',
    ],
    projectFiles: [
      { path: 'frontend/src/pages/Strategy.tsx', reason: '配置和运行主实验。' },
      { path: 'frontend/src/pages/WalkForward.tsx', reason: '样本外审计与参数漂移。' },
      { path: 'frontend/src/pages/DataQuality.tsx', reason: '记录数据覆盖和未解决问题。' },
    ],
    demo: {
      file: 'learning/README.md',
      command: 'pwsh -File scripts\\check.ps1',
      summary: '按毕业清单运行全流程，把结果和局限写成可复现研究报告。',
      snippet: `研究结论模板
1. 假设：为什么动量 + 舆情可能有效？
2. 数据：何时可得？缺失和偏差是什么？
3. 方法：如何从因子得到仓位？
4. 结果：扣费后是否优于基准？
5. 样本外：结论是否跨窗口稳定？
6. 局限：哪些现实约束尚未建模？`,
    },
    quiz: [
      {
        question: '毕业项目最重要的成果是什么？',
        options: ['最高历史收益', '可复现、可审计的证据链', '最多参数'],
        answer: 1,
        explanation: '研究能力体现在方法和证据，而不是一次历史曲线。',
      },
      {
        question: '样本外结果不理想应该怎么做？',
        options: ['删除窗口', '如实报告并检查假设、数据和实现', '把测试集改成训练集'],
        answer: 1,
        explanation: '诚实的否定结果能避免错误投入，并指导下一轮研究。',
      },
      {
        question: '完成本课程后可以直接实盘吗？',
        options: ['可以保证盈利', '仍不可以，还缺真实撮合、风控、监控和合规', '只要提高杠杆就可以'],
        answer: 1,
        explanation: '研究平台不是生产交易系统，实盘需要新的工程与风险阶段。',
      },
    ],
    resources: [
      {
        title: 'CS 7646: Machine Learning for Trading',
        provider: 'Georgia Tech OMSCS',
        url: 'https://omscs.gatech.edu/cs-7646-machine-learning-trading',
        note: '用其课程范围检查自己的金融数据与机器学习基础。',
      },
      {
        title: 'Lectures',
        provider: 'QuantEcon',
        url: 'https://quantecon.org/lectures/',
        note: '完成主线后继续补概率、时间序列和资产定价。',
      },
    ],
  },
]

export const chapterById = Object.fromEntries(
  learningChapters.map((chapter) => [chapter.id, chapter]),
) as Record<string, LearningChapter>

export const totalChecklistItems = learningChapters.reduce(
  (total, chapter) => total + chapter.checklist.length,
  0,
)
