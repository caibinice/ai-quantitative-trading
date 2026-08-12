# AI Quant Learning Guide

**English | [简体中文](./README_CN.md)**

This guide maps directly to the project codebase rather than presenting a detached theory syllabus. Open it in the web app at `http://127.0.0.1:5173/quant/learn`. Progress and quiz scores are stored in browser `localStorage` first and synchronized to MySQL whenever the API is available, so the same course can continue across devices.

## Suggested pace

| Stage | Chapters | Suggested time | Outcome |
| --- | --- | ---: | --- |
| 1. Build the map | Stock and candlestick basics; Quant map; Project tour | 1 week | Start the system and explain the research loop |
| 2. Learn the data language | Python bridge; NumPy/pandas | 2 weeks | Process time series independently |
| 3. Build trustworthy strategies | Market data; Factor backtesting | 2 weeks | Implement a backtest without future information |
| 4. Add AI and validation | Sentiment factor; Walk-forward | 2 weeks | Audit text factors and out-of-sample results |
| 5. Complete a research system | Engineering governance; Capstone | 1–2 weeks | Deliver a reproducible research report |

Plan for five to eight hours per week. For every chapter:

1. Open its three concept cards and read the mental model, deep dive, and flowchart.
2. Study why each common mistake fails, the correct approach, and its self-check question instead of memorizing only the conclusion.
3. Download the teaching CSV and guided script, then follow the step-by-step instructions and expected output.
4. Read the annotated code section by section, confirm the output, and change only one parameter at a time.
5. Complete the checklist.
6. Take the three-question quiz and answer at least two correctly.
7. Record commands, output, changes, and open questions in a research journal.

The 11 chapters contain 33 detail pages. Each page includes plain-language terminology, a complete explanation, a visual flow, concrete failure modes, guided exercises, annotated code, expected output, a verification checklist, and further reading with original links. Source files, tests, teaching datasets, and labs listed by chapter can be downloaded from the UI. The download API is allowlisted to educational directories and never exposes credentials, environment files, or Git metadata.

## Run the six examples

From the repository root:

```powershell
.\.venv\Scripts\python.exe learning\examples\00_kline_basics.py
.\.venv\Scripts\python.exe learning\examples\01_python_bridge.py
.\.venv\Scripts\python.exe learning\examples\02_pandas_timeseries.py
.\.venv\Scripts\python.exe learning\examples\03_signal_delay.py
.\.venv\Scripts\python.exe learning\examples\04_sentiment_factor.py
.\.venv\Scripts\python.exe learning\examples\05_walk_forward.py
```

Each script ends with `DEMO_OK`. Pytest also runs these files so the learning material cannot silently drift away from the project implementation.

## Run the 11 beginner labs

Every chapter also has a hand-crafted CSV in `learning/datasets/` and a runnable script in `learning/labs/`. They work offline, do not call an LLM, do not connect to a brokerage, and end with `LAB_OK`. Read the steps and expected output in the web lesson before running the matching command. For example:

```powershell
.\.venv\Scripts\python.exe learning\labs\01_market_basics_lab.py
.\.venv\Scripts\python.exe learning\labs\07_backtest_cost_lab.py
.\.venv\Scripts\python.exe learning\labs\11_capstone_lab.py
```

The teaching datasets deliberately contain missing dates, adjustment discontinuities, future announcements, duplicate news, and abnormal prices. Do not “fix everything” before the first run. Observe how the checks expose each problem, then modify one field or parameter at a time.

## Capstone research template

The final deliverable is not merely an attractive equity curve; it is a complete evidence chain:

1. **Hypothesis:** why might the factor work, and what result would falsify it?
2. **Data:** sources, universe, period, adjustment, missing values, and true availability times.
3. **Method:** factors, thresholds, ranking, weights, execution delay, costs, and benchmark.
4. **In-sample results:** return, drawdown, Sharpe ratio, turnover, and the parameter-selection method.
5. **Out-of-sample results:** every walk-forward window and the final stitched equity curve.
6. **Robustness:** alternative parameters, market regimes, data anomalies, and model versions.
7. **Limitations:** suspensions, price limits, market impact, capacity, sentiment errors, and survivorship bias.
8. **Conclusion:** continue, revise the hypothesis, or stop, together with the reason.

## Curriculum references

The academy borrows course-organization ideas and links to original material; it does not reproduce third-party course text.

- [Python Tutorial](https://docs.python.org/3/tutorial/): the official syntax entry point for programmers coming from another language.
- [CS50P](https://cs50.harvard.edu/python/): a useful rhythm of explanation, exercises, tests, and a final project.
- [NumPy Learn](https://numpy.org/learn/): scientific-computing foundations.
- [pandas Getting Started](https://pandas.pydata.org/docs/getting_started/intro_tutorials/): tables and time series.
- [Georgia Tech CS 7646](https://omscs.gatech.edu/cs-7646-machine-learning-trading): a progression through financial data, computational investing, and machine learning for trading.
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html): out-of-sample validation for time-ordered data.
- [QuantEcon Lectures](https://quantecon.org/lectures/): additional probability, economics, and financial-computing material.
- [SSE Investor Education](https://edu.sse.com.cn/): securities, trading rules, risks, and periodic reports.
- [CNINFO](https://www.cninfo.com.cn/): statutory company disclosures and announcement times.
- [Backtest Overfitting](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659): Bailey, Borwein, López de Prado, and Zhu on repeated trials and backtest overfitting.
- [AQR Insights](https://www.aqr.com/Insights): public practitioner perspectives on factors, portfolio construction, costs, and backtest haircuts.
- [Robot Wealth](https://robotwealth.com/backtesting-bias-feels-good-until-you-blow-up/): practitioner experience with simple rules, out-of-sample validation, and backtest bias.

Practitioner material in the web academy is summarized and linked to the original source. It is used to practice comparing viewpoints and evidence, not as an immutable law or a recommendation for any stock or strategy.

> The academy and project are for research only, do not constitute investment advice, and contain no live-order capability.
