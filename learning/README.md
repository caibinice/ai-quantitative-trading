# AI 量化学习手册

这套手册与项目代码一一对应，不是独立于项目的理论目录。网页入口是
`http://127.0.0.1:5173/quant/learn`。学习进度和测验成绩先写入浏览器
`localStorage`，API 可用时同步到 MySQL，因此可以跨设备继续学习。

## 建议节奏

| 阶段 | 章节 | 建议时间 | 阶段成果 |
|---|---|---:|---|
| 1. 建立地图 | 量化地图、项目导览 | 1 周 | 能启动系统并解释研究闭环 |
| 2. 数据语言 | Python 迁移、NumPy/pandas | 2 周 | 能独立处理时间序列 |
| 3. 可信策略 | 市场数据、因子回测 | 2 周 | 能实现没有未来数据的回测 |
| 4. AI 与验证 | 舆情因子、Walk-forward | 2 周 | 能审计文本因子和样本外结果 |
| 5. 研究系统 | 工程治理、毕业项目 | 1–2 周 | 交付一份可复现研究报告 |

建议每周投入 5–8 小时。每章按下面顺序：

1. 点击三个“知识梗概”卡片，依次阅读详情页的心智模型、深度讲解和流程图。
2. 阅读每条误区的“为什么会错 / 正确做法 / 自查问题”，不要只背结论。
3. 下载详情页提供的教学 CSV 和跟练脚本，按“怎么做 / 预期结果”逐步运行。
4. 对照代码逐段解读，确认输出与页面列出的预期值一致，再只修改一个参数。
5. 完成 Checklist。
6. 完成 3 道小测验，至少答对 2 道。
7. 把命令、输出、改动和不理解的点记录到自己的研究日志。

十一章共包含 33 个详情页。每页都有白话术语、完整讲解、可视流程、具体误区、逐步跟练、代码解读、预期输出、验证清单和有原文链接的延伸阅读。章节页与详情页列出的源码、测试、教学数据和实验脚本都可以点击下载；下载接口只开放教学相关目录，不会提供凭证、环境文件或 Git 元数据。

## 运行五个实验

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe learning\examples\01_python_bridge.py
.\.venv\Scripts\python.exe learning\examples\02_pandas_timeseries.py
.\.venv\Scripts\python.exe learning\examples\03_signal_delay.py
.\.venv\Scripts\python.exe learning\examples\04_sentiment_factor.py
.\.venv\Scripts\python.exe learning\examples\05_walk_forward.py
```

每个脚本最后都应输出 `DEMO_OK`。它们同时被 pytest 调用，防止学习资料随项目演进而失效。

## 运行十一组零基础跟练

每章还有一份位于 `learning/datasets/` 的人工教学 CSV，以及一份位于
`learning/labs/` 的可运行脚本。它们不联网、不调用大模型、不连接券商，最后应输出
`LAB_OK`。先在网页详情页阅读步骤和预期结果，再运行对应命令。例如：

```powershell
.\.venv\Scripts\python.exe learning\labs\01_market_basics_lab.py
.\.venv\Scripts\python.exe learning\labs\07_backtest_cost_lab.py
.\.venv\Scripts\python.exe learning\labs\11_capstone_lab.py
```

教学数据刻意包含日期缺口、除权断层、未来公告、重复新闻和异常行情。不要直接“修好”后
再运行；先观察测试怎样暴露问题，然后每次只修改一个字段或参数。

## 毕业研究模板

最终成果不是一条漂亮曲线，而是一条完整证据链：

1. **假设**：为什么这个因子可能有效？什么结果会否定它？
2. **数据**：来源、股票池、区间、复权、缺失和真实可得时间。
3. **方法**：因子、门槛、排序、权重、执行延迟、成本和基准。
4. **样本内结果**：收益、回撤、夏普、换手，以及参数选择方法。
5. **样本外结果**：Walk-forward 每个窗口和最终拼接曲线。
6. **稳健性**：替代参数、市场阶段、数据异常和模型版本。
7. **局限**：停牌、涨跌停、冲击成本、容量、舆情误判和幸存者偏差。
8. **结论**：继续研究、修改假设或停止投入，并说明理由。

## 课程结构参考

手册只参考课程组织方式并链接原始资料，不复制第三方课程正文：

- [Python Tutorial](https://docs.python.org/3/tutorial/)：有其他语言经验者的官方语法入口。
- [CS50P](https://cs50.harvard.edu/python/)：讲解、练习、测试和最终项目的课程节奏。
- [NumPy Learn](https://numpy.org/learn/)：科学计算基础。
- [pandas Getting Started](https://pandas.pydata.org/docs/getting_started/intro_tutorials/)：表格和时间序列。
- [Georgia Tech CS 7646](https://omscs.gatech.edu/cs-7646-machine-learning-trading)：
  金融数据、计算投资和机器学习交易的三段式结构。
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)：
  时间顺序数据的样本外验证。
- [QuantEcon Lectures](https://quantecon.org/lectures/)：后续补充概率、经济和金融计算。
- [上交所投资者教育](https://edu.sse.com.cn/)：证券、交易规则、风险和定期报告基础。
- [巨潮资讯](https://www.cninfo.com.cn/)：核对上市公司法定公告及披露时间。
- [Backtest Overfitting](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659)：
  Bailey、Borwein、López de Prado 与 Zhu 对多次试验和回测过拟合的讨论。
- [AQR Insights](https://www.aqr.com/Insights)：因子、组合构建、成本和回测折扣的公开从业观点。
- [Robot Wealth](https://robotwealth.com/backtesting-bias-feels-good-until-you-blow-up/)：
  从业者对简单规则、样本外验证和回测偏差的经验总结。

网页中的从业者内容均为摘要并链接原文。它们用于训练“比较观点与证据”的能力，
不被当成事实定律，也不构成对任何股票或策略的推荐。

> 本学习资料和项目只用于研究，不构成投资建议，也不包含真实下单能力。
