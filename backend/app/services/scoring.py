from __future__ import annotations

import math
from datetime import date, datetime, timedelta

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DailyPrice, FactorScore, FinancialMetric, NewsItem, SentimentAnalysis
from app.schemas import StrategyParameters


def _bounded_score(value: float, scale: float = 1.0) -> float:
    return round(50 + 50 * math.tanh(value * scale), 2)


def momentum_component(closes: list[float]) -> tuple[float, dict[str, float]]:
    if len(closes) < 21:
        return 50.0, {"return_20d": 0.0, "return_60d": 0.0, "volatility_20d": 0.0}
    values = np.asarray(closes, dtype=float)
    return_20 = values[-1] / values[-21] - 1
    return_60 = values[-1] / values[-61] - 1 if len(values) >= 61 else return_20
    daily = np.diff(values[-21:]) / values[-21:-1]
    volatility = float(np.std(daily, ddof=1) * math.sqrt(252)) if len(daily) > 1 else 0.0
    raw = 0.6 * return_20 + 0.4 * return_60 - 0.15 * volatility
    return _bounded_score(raw, 4.0), {
        "return_20d": round(float(return_20), 6),
        "return_60d": round(float(return_60), 6),
        "volatility_20d": round(volatility, 6),
    }


def quality_component(metrics: list[FinancialMetric]) -> tuple[float, dict[str, float]]:
    selected: dict[str, float] = {}
    keywords = ("净资产收益率", "营业总收入", "归母净利润")
    for metric in metrics:
        if any(keyword in metric.metric_name for keyword in keywords):
            value = metric.yoy if metric.yoy is not None else metric.metric_value
            if value is not None and metric.metric_name not in selected:
                selected[metric.metric_name] = float(value)
    if not selected:
        return 50.0, {}
    normalized = [max(-100, min(100, value)) / 100 for value in selected.values()]
    return _bounded_score(float(np.mean(normalized)), 1.2), selected


def sentiment_component(
    events: list[tuple[float, float, datetime]], as_of: date
) -> tuple[float, int]:
    if not events:
        return 50.0, 0
    weighted = 0.0
    weights = 0.0
    as_of_dt = datetime.combine(as_of, datetime.max.time())
    for score, confidence, published_at in events:
        age_days = max(0.0, (as_of_dt - published_at).total_seconds() / 86400)
        weight = max(0.05, confidence) * math.exp(-age_days / 7)
        weighted += score * weight
        weights += weight
    return _bounded_score(weighted / weights if weights else 0.0, 1.3), len(events)


def calculate_scores(
    db: Session,
    symbols: list[str],
    as_of: date,
    parameters: StrategyParameters,
) -> list[FactorScore]:
    results: list[FactorScore] = []
    start_news = datetime.combine(as_of - timedelta(days=30), datetime.min.time())
    for symbol in symbols:
        prices = list(
            db.scalars(
                select(DailyPrice)
                .where(DailyPrice.symbol == symbol, DailyPrice.trade_date <= as_of)
                .order_by(DailyPrice.trade_date.desc())
                .limit(120)
            ).all()
        )
        prices.reverse()
        momentum, momentum_detail = momentum_component([item.close for item in prices])

        financials = list(
            db.scalars(
                select(FinancialMetric)
                .where(FinancialMetric.symbol == symbol, FinancialMetric.report_date <= as_of)
                .order_by(FinancialMetric.report_date.desc())
                .limit(100)
            ).all()
        )
        quality, quality_detail = quality_component(financials)

        event_rows = db.execute(
            select(SentimentAnalysis.score, SentimentAnalysis.confidence, NewsItem.published_at)
            .join(NewsItem, NewsItem.id == SentimentAnalysis.news_id)
            .where(
                NewsItem.symbol == symbol,
                NewsItem.published_at >= start_news,
                NewsItem.published_at
                < datetime.combine(as_of + timedelta(days=1), datetime.min.time()),
            )
        ).all()
        sentiment, event_count = sentiment_component(list(event_rows), as_of)

        total = round(
            momentum * parameters.momentum_weight
            + quality * parameters.quality_weight
            + sentiment * parameters.sentiment_weight,
            2,
        )
        existing = db.scalar(
            select(FactorScore).where(
                FactorScore.symbol == symbol, FactorScore.score_date == as_of
            )
        )
        item = existing or FactorScore(symbol=symbol, score_date=as_of)
        item.momentum_score = momentum
        item.quality_score = quality
        item.sentiment_score = sentiment
        item.total_score = total
        item.explanation = {
            "momentum": momentum_detail,
            "quality": quality_detail,
            "sentiment_event_count": event_count,
            "warning": "评分仅用于研究排序，不代表投资建议。",
        }
        db.add(item)
        results.append(item)
    db.commit()
    return sorted(results, key=lambda item: item.total_score, reverse=True)
