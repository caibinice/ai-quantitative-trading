from __future__ import annotations

import math
from datetime import timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BacktestRun, DailyPrice, IndexPrice, NewsItem, SentimentAnalysis
from app.schemas import BacktestRequest, StrategyParameters


def _rolling_sentiment(
    dates: pd.DatetimeIndex,
    events: list[tuple[pd.Timestamp, float]],
    lookback_days: int,
) -> pd.Series:
    values: list[float] = []
    for current in dates:
        start = current - pd.Timedelta(days=lookback_days)
        scores = [score for published, score in events if start <= published <= current]
        values.append(float(np.mean(scores)) if scores else 0.0)
    return pd.Series(values, index=dates, dtype=float)


def run_dual_factor_backtest(
    price_frames: dict[str, pd.Series],
    sentiment_events: dict[str, list[tuple[pd.Timestamp, float]]],
    parameters: StrategyParameters,
    benchmark_prices: pd.Series | None = None,
) -> dict[str, Any]:
    """Run a close-to-close research backtest with a mandatory one-bar signal delay."""
    if not price_frames:
        raise ValueError("没有可用于回测的行情数据")
    closes = pd.concat(price_frames, axis=1).sort_index().ffill()
    closes.columns = list(price_frames.keys())
    closes = closes.dropna(how="all")
    returns = closes.pct_change(fill_method=None).fillna(0.0)
    momentum = closes.pct_change(parameters.momentum_window, fill_method=None)

    sentiments = pd.DataFrame(index=closes.index, columns=closes.columns, dtype=float)
    for symbol in closes.columns:
        events = sorted(sentiment_events.get(symbol, []), key=lambda row: row[0])
        sentiments[symbol] = _rolling_sentiment(
            closes.index, events, parameters.sentiment_lookback_days
        )

    factor_weight = parameters.momentum_weight + parameters.sentiment_weight
    momentum_weight = parameters.momentum_weight / factor_weight if factor_weight else 0.5
    sentiment_weight = parameters.sentiment_weight / factor_weight if factor_weight else 0.5
    combined = momentum.rank(axis=1, pct=True) * momentum_weight + (
        (sentiments + 1) / 2
    ) * sentiment_weight
    eligible = (momentum > parameters.minimum_momentum) & (
        sentiments >= parameters.sentiment_threshold
    )

    targets = pd.DataFrame(0.0, index=closes.index, columns=closes.columns)
    for trade_date in closes.index:
        candidates = combined.loc[trade_date][eligible.loc[trade_date]].dropna()
        selected = candidates.nlargest(parameters.top_n).index
        if len(selected):
            targets.loc[trade_date, selected] = 1.0 / len(selected)

    # Critical anti-lookahead rule: a signal computed after close T is held from T+1.
    applied_weights = targets.shift(1).fillna(0.0)
    turnover = applied_weights.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = applied_weights.iloc[0].abs().sum()
    costs = turnover * (parameters.fee_rate + parameters.slippage_rate)
    gross_return = (applied_weights * returns).sum(axis=1)
    net_return = gross_return - costs
    if benchmark_prices is not None and not benchmark_prices.empty:
        benchmark_close = benchmark_prices.reindex(closes.index).ffill()
        benchmark_return = benchmark_close.pct_change(fill_method=None).fillna(0.0)
    else:
        benchmark_return = returns.mean(axis=1)

    performance = performance_from_returns(
        net_return,
        benchmark_return,
        parameters.initial_capital,
        turnover,
    )
    return {
        **performance,
        "weights": applied_weights,
        "net_returns": net_return,
        "benchmark_returns": benchmark_return,
    }


def performance_from_returns(
    net_return: pd.Series,
    benchmark_return: pd.Series,
    initial_capital: float,
    turnover: pd.Series | None = None,
) -> dict[str, Any]:
    if net_return.empty:
        raise ValueError("没有可用于计算绩效的收益序列")
    benchmark_return = benchmark_return.reindex(net_return.index).fillna(0.0)
    turnover = (
        turnover.reindex(net_return.index).fillna(0.0)
        if turnover is not None
        else pd.Series(0.0, index=net_return.index)
    )
    equity = initial_capital * (1 + net_return).cumprod()
    benchmark = initial_capital * (1 + benchmark_return).cumprod()
    drawdown = equity / equity.cummax() - 1
    periods = max(1, len(net_return) - 1)
    total_return = float(equity.iloc[-1] / initial_capital - 1)
    annualized = float((1 + total_return) ** (252 / periods) - 1) if total_return > -1 else -1.0
    std = float(net_return.std(ddof=1))
    sharpe = float(net_return.mean() / std * math.sqrt(252)) if std > 0 else 0.0

    metrics = {
        "total_return": round(total_return, 6),
        "annualized_return": round(annualized, 6),
        "max_drawdown": round(float(drawdown.min()), 6),
        "sharpe_ratio": round(sharpe, 4),
        "benchmark_return": round(float(benchmark.iloc[-1] / initial_capital - 1), 6),
        "turnover": round(float(turnover.sum()), 4),
        "trade_count": int((turnover > 1e-12).sum()),
        "bars": len(net_return),
    }
    curve = [
        {
            "date": index.date().isoformat(),
            "equity": round(float(equity.loc[index]), 2),
            "benchmark": round(float(benchmark.loc[index]), 2),
            "drawdown": round(float(drawdown.loc[index]), 6),
        }
        for index in equity.index
    ]
    return {"metrics": metrics, "equity_curve": curve}


def run_backtest_from_db(db: Session, request: BacktestRequest) -> BacktestRun:
    symbols = request.symbols
    price_frames: dict[str, pd.Series] = {}
    sentiment_events: dict[str, list[tuple[pd.Timestamp, float]]] = {}
    for symbol in symbols:
        price_rows = db.execute(
            select(DailyPrice.trade_date, DailyPrice.close)
            .where(
                DailyPrice.symbol == symbol,
                DailyPrice.trade_date >= request.start_date,
                DailyPrice.trade_date <= request.end_date,
            )
            .order_by(DailyPrice.trade_date)
        ).all()
        if price_rows:
            price_frames[symbol] = pd.Series(
                [row.close for row in price_rows],
                index=pd.to_datetime([row.trade_date for row in price_rows]),
                name=symbol,
                dtype=float,
            )
        event_rows = db.execute(
            select(NewsItem.published_at, SentimentAnalysis.score)
            .join(SentimentAnalysis, SentimentAnalysis.news_id == NewsItem.id)
            .where(
                NewsItem.symbol == symbol,
                NewsItem.published_at >= request.start_date - timedelta(
                    days=request.parameters.sentiment_lookback_days
                ),
                NewsItem.published_at < request.end_date + timedelta(days=1),
            )
            .order_by(NewsItem.published_at)
        ).all()
        sentiment_events[symbol] = [
            (pd.Timestamp(row.published_at).normalize(), float(row.score)) for row in event_rows
        ]

    benchmark_rows = db.execute(
        select(IndexPrice.trade_date, IndexPrice.close)
        .where(
            IndexPrice.symbol == request.parameters.benchmark_symbol,
            IndexPrice.trade_date >= request.start_date,
            IndexPrice.trade_date <= request.end_date,
        )
        .order_by(IndexPrice.trade_date)
    ).all()
    benchmark_prices = (
        pd.Series(
            [row.close for row in benchmark_rows],
            index=pd.to_datetime([row.trade_date for row in benchmark_rows]),
            dtype=float,
        )
        if benchmark_rows
        else None
    )
    result = run_dual_factor_backtest(
        price_frames,
        sentiment_events,
        request.parameters,
        benchmark_prices,
    )
    run = BacktestRun(
        name=request.name,
        start_date=request.start_date,
        end_date=request.end_date,
        parameters={"symbols": symbols, **request.parameters.model_dump()},
        metrics=result["metrics"],
        equity_curve=result["equity_curve"],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
