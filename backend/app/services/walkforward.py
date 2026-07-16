from __future__ import annotations

from datetime import timedelta
from itertools import product
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DailyPrice,
    IndexPrice,
    NewsItem,
    SentimentAnalysis,
    WalkForwardRun,
)
from app.schemas import WalkForwardRequest
from app.services.backtest import performance_from_returns, run_dual_factor_backtest


def run_walk_forward(
    price_frames: dict[str, pd.Series],
    sentiment_events: dict[str, list[tuple[pd.Timestamp, float]]],
    benchmark_prices: pd.Series | None,
    request: WalkForwardRequest,
) -> dict[str, Any]:
    if not price_frames:
        raise ValueError("没有可用于 Walk-forward 的行情数据")
    all_dates = pd.DatetimeIndex(
        sorted(set().union(*(set(series.index) for series in price_frames.values())))
    )
    if len(all_dates) < request.train_days + request.test_days:
        raise ValueError("样本长度不足，至少需要一个完整训练窗口和测试窗口")

    out_returns: list[pd.Series] = []
    out_benchmark: list[pd.Series] = []
    windows: list[dict[str, Any]] = []
    cursor = request.train_days
    while cursor < len(all_dates):
        test_end_index = min(cursor + request.test_days, len(all_dates))
        train_dates = all_dates[cursor - request.train_days : cursor]
        test_dates = all_dates[cursor:test_end_index]
        if len(test_dates) < 5:
            break

        best_score = float("-inf")
        best_parameters = request.parameters
        best_train_metrics: dict[str, Any] = {}
        for momentum_window, sentiment_threshold in product(
            request.momentum_windows, request.sentiment_thresholds
        ):
            candidate = request.parameters.model_copy(
                update={
                    "momentum_window": momentum_window,
                    "sentiment_threshold": sentiment_threshold,
                }
            )
            train_prices = {
                symbol: series.reindex(train_dates).dropna()
                for symbol, series in price_frames.items()
            }
            train_benchmark = (
                benchmark_prices.reindex(train_dates).dropna()
                if benchmark_prices is not None
                else None
            )
            result = run_dual_factor_backtest(
                train_prices, sentiment_events, candidate, train_benchmark
            )
            metrics = result["metrics"]
            score = (
                float(metrics["sharpe_ratio"])
                + float(metrics["annualized_return"])
                - abs(float(metrics["max_drawdown"])) * 0.25
            )
            if score > best_score:
                best_score = score
                best_parameters = candidate
                best_train_metrics = metrics

        warmup = max(
            best_parameters.momentum_window + 2,
            best_parameters.sentiment_lookback_days + 2,
        )
        evaluation_start = max(0, cursor - warmup)
        evaluation_dates = all_dates[evaluation_start:test_end_index]
        evaluation_prices = {
            symbol: series.reindex(evaluation_dates).dropna()
            for symbol, series in price_frames.items()
        }
        evaluation_benchmark = (
            benchmark_prices.reindex(evaluation_dates).dropna()
            if benchmark_prices is not None
            else None
        )
        evaluation = run_dual_factor_backtest(
            evaluation_prices,
            sentiment_events,
            best_parameters,
            evaluation_benchmark,
        )
        test_returns = evaluation["net_returns"].reindex(test_dates).fillna(0.0)
        test_benchmark = evaluation["benchmark_returns"].reindex(test_dates).fillna(0.0)
        test_performance = performance_from_returns(
            test_returns,
            test_benchmark,
            request.parameters.initial_capital,
        )
        out_returns.append(test_returns)
        out_benchmark.append(test_benchmark)
        windows.append(
            {
                "train_start": train_dates[0].date().isoformat(),
                "train_end": train_dates[-1].date().isoformat(),
                "test_start": test_dates[0].date().isoformat(),
                "test_end": test_dates[-1].date().isoformat(),
                "selected_momentum_window": best_parameters.momentum_window,
                "selected_sentiment_threshold": best_parameters.sentiment_threshold,
                "selection_score": round(best_score, 6),
                "train_metrics": best_train_metrics,
                "test_metrics": test_performance["metrics"],
            }
        )
        cursor = test_end_index

    if not out_returns:
        raise ValueError("没有生成有效的样本外窗口")
    combined_returns = pd.concat(out_returns).sort_index()
    combined_benchmark = pd.concat(out_benchmark).sort_index()
    performance = performance_from_returns(
        combined_returns,
        combined_benchmark,
        request.parameters.initial_capital,
    )
    return {**performance, "windows": windows}


def run_walk_forward_from_db(db: Session, request: WalkForwardRequest) -> WalkForwardRun:
    price_frames: dict[str, pd.Series] = {}
    sentiment_events: dict[str, list[tuple[pd.Timestamp, float]]] = {}
    for symbol in request.symbols:
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
                dtype=float,
            )
        event_rows = db.execute(
            select(NewsItem.published_at, SentimentAnalysis.score)
            .join(SentimentAnalysis, SentimentAnalysis.news_id == NewsItem.id)
            .where(
                NewsItem.symbol == symbol,
                NewsItem.published_at
                >= request.start_date
                - timedelta(days=request.parameters.sentiment_lookback_days),
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
    result = run_walk_forward(
        price_frames, sentiment_events, benchmark_prices, request
    )
    run = WalkForwardRun(
        name=request.name,
        start_date=request.start_date,
        end_date=request.end_date,
        benchmark_symbol=request.parameters.benchmark_symbol,
        parameters={
            "symbols": request.symbols,
            "train_days": request.train_days,
            "test_days": request.test_days,
            "momentum_windows": request.momentum_windows,
            "sentiment_thresholds": request.sentiment_thresholds,
            **request.parameters.model_dump(),
        },
        windows=result["windows"],
        metrics=result["metrics"],
        equity_curve=result["equity_curve"],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
