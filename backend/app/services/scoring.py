from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DailyPrice,
    FactorScore,
    FinancialMetric,
    NewsItem,
    PointInTimeFinancial,
    SentimentAnalysis,
)
from app.schemas import StrategyParameters
from app.services.news_dedup import is_duplicate_news

SENTIMENT_HALF_LIFE_DAYS = 7.0


def _bounded_score(value: float, scale: float = 1.0) -> float:
    return round(50 + 50 * math.tanh(value * scale), 2)


def momentum_component(closes: list[float]) -> tuple[float, dict[str, Any]]:
    if len(closes) < 21:
        return 50.0, {
            "return_5d": 0.0,
            "return_20d": 0.0,
            "return_60d": 0.0,
            "volatility_20d": 0.0,
            "status": "insufficient_history",
            "anomaly_count": 0,
        }
    values = np.asarray(closes, dtype=float)
    all_daily = np.diff(values) / values[:-1]
    anomaly_count = int(np.sum(np.abs(all_daily) > 0.35))
    if anomaly_count:
        return 50.0, {
            "return_5d": 0.0,
            "return_20d": 0.0,
            "return_60d": 0.0,
            "volatility_20d": 0.0,
            "status": "blocked_by_price_anomaly",
            "anomaly_count": anomaly_count,
        }
    return_5 = values[-1] / values[-6] - 1 if len(values) >= 6 else 0.0
    return_20 = values[-1] / values[-21] - 1
    return_60 = values[-1] / values[-61] - 1 if len(values) >= 61 else return_20
    daily = np.diff(values[-21:]) / values[-21:-1]
    volatility = float(np.std(daily, ddof=1) * math.sqrt(252)) if len(daily) > 1 else 0.0
    raw = 0.25 * return_5 + 0.45 * return_20 + 0.30 * return_60 - 0.10 * volatility
    return _bounded_score(raw, 4.0), {
        "return_5d": round(float(return_5), 6),
        "return_20d": round(float(return_20), 6),
        "return_60d": round(float(return_60), 6),
        "volatility_20d": round(volatility, 6),
        "status": "ok",
        "anomaly_count": 0,
    }


def quality_component(
    metrics: list[FinancialMetric | PointInTimeFinancial],
) -> tuple[float, dict[str, float]]:
    selected: dict[str, float] = {}
    scales = {
        "净资产收益率": 20.0,
        "营业总收入同比增长": 30.0,
        "净利润同比增长": 30.0,
        "销售毛利率": 40.0,
    }
    for metric in metrics:
        metric_name = metric.metric_name
        if metric_name not in scales:
            continue
        value = metric.metric_value
        if isinstance(metric, FinancialMetric) and metric.yoy is not None:
            value = metric.yoy
        if value is not None and metric_name not in selected:
            selected[metric_name] = float(value)
    if not selected:
        return 50.0, {}
    normalized = [
        math.tanh(max(-100.0, min(100.0, value)) / scales[name])
        for name, value in selected.items()
    ]
    return _bounded_score(float(np.mean(normalized)), 1.0), selected


def sentiment_component(
    events: list[tuple[float, float, datetime]],
    as_of: date,
    lookback_days: int = 7,
    half_life_days: float = SENTIMENT_HALF_LIFE_DAYS,
) -> tuple[float, int]:
    if not events or lookback_days < 1 or half_life_days <= 0:
        return 50.0, 0
    weighted = 0.0
    weights = 0.0
    included = 0
    as_of_dt = datetime.combine(as_of, datetime.max.time())
    for score, confidence, published_at in events:
        age_days = max(0.0, (as_of_dt - published_at).total_seconds() / 86400)
        if age_days > lookback_days:
            continue
        weight = max(0.05, min(1.0, confidence)) * 0.5 ** (age_days / half_life_days)
        weighted += score * weight
        weights += weight
        included += 1
    # A neutral prior prevents one low-confidence or nearly expired event from
    # producing an artificially strong directional score.
    aggregate = weighted / max(1.0, weights) if weights else 0.0
    return _bounded_score(aggregate, 1.3), included


def deduplicate_sentiment_events(
    events: list[tuple[float, float, datetime, str, str, str, str]],
) -> list[tuple[float, float, datetime]]:
    """Defensively prevent legacy duplicate articles from multiplying a factor."""
    kept: list[tuple[float, float, datetime, str, str, str, str]] = []
    for event in sorted(events, key=lambda row: row[2], reverse=True):
        signature = {
            "title": event[3],
            "content": event[4],
            "source_url": event[5],
            "published_at": event[2],
        }
        duplicate = any(
            event[6] == candidate[6]
            and is_duplicate_news(
                signature,
                {
                    "title": candidate[3],
                    "content": candidate[4],
                    "source_url": candidate[5],
                    "published_at": candidate[2],
                },
            )
            for candidate in kept
        )
        if not duplicate:
            kept.append(event)
    return [(score, confidence, published_at) for score, confidence, published_at, *_ in kept]


def calculate_scores(
    db: Session,
    symbols: list[str],
    as_of: date,
    parameters: StrategyParameters,
) -> list[FactorScore]:
    results: list[FactorScore] = []
    sentiment_lookback_days = parameters.sentiment_lookback_days
    start_news = datetime.combine(
        as_of - timedelta(days=sentiment_lookback_days), datetime.min.time()
    )
    for symbol in symbols:
        price_rows = list(
            db.scalars(
                select(DailyPrice)
                .where(DailyPrice.symbol == symbol, DailyPrice.trade_date <= as_of)
                .order_by(DailyPrice.trade_date.desc())
                .limit(120)
            ).all()
        )
        real_prices = [item for item in price_rows if item.source != "demo"]
        prices = real_prices if len(real_prices) >= 21 else price_rows
        prices.reverse()
        momentum, momentum_detail = momentum_component([item.close for item in prices])

        financials = list(
            db.scalars(
                select(PointInTimeFinancial)
                .where(
                    PointInTimeFinancial.symbol == symbol,
                    PointInTimeFinancial.available_at <= as_of,
                )
                .order_by(
                    PointInTimeFinancial.available_at.desc(),
                    PointInTimeFinancial.report_date.desc(),
                )
                .limit(100)
            ).all()
        )
        quality, quality_detail = quality_component(financials)

        event_rows = db.execute(
            select(
                SentimentAnalysis.score,
                SentimentAnalysis.confidence,
                NewsItem.published_at,
                NewsItem.title,
                NewsItem.content,
                NewsItem.source_url,
                NewsItem.kind,
            )
            .join(NewsItem, NewsItem.id == SentimentAnalysis.news_id)
            .where(
                NewsItem.symbol == symbol,
                NewsItem.published_at >= start_news,
                NewsItem.published_at
                < datetime.combine(as_of + timedelta(days=1), datetime.min.time()),
            )
        ).all()
        unique_events = deduplicate_sentiment_events(list(event_rows))
        sentiment, event_count = sentiment_component(
            unique_events,
            as_of,
            lookback_days=sentiment_lookback_days,
        )

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
            "quality_data_mode": "point_in_time",
            "data": {
                "price_latest_date": prices[-1].trade_date.isoformat() if prices else None,
                "price_source": prices[-1].source if prices else None,
                "price_rows": len(prices),
                "excluded_demo_rows": len(price_rows) - len(real_prices)
                if len(real_prices) >= 21
                else 0,
                "financial_report_date": financials[0].report_date.isoformat()
                if financials
                else None,
                "financial_available_at": financials[0].available_at.isoformat()
                if financials
                else None,
                "financial_source": financials[0].source if financials else None,
            },
            "sentiment_event_count": event_count,
            "sentiment_method": {
                "lookback_days": sentiment_lookback_days,
                "half_life_days": SENTIMENT_HALF_LIFE_DAYS,
                "weighting": "confidence_x_exponential_decay",
                "stale_policy": "excluded_after_lookback",
            },
            "warning": (
                "行情存在异常跳变，动量已回退为中性；请先处理数据质量告警。"
                if momentum_detail["status"] == "blocked_by_price_anomaly"
                else "评分仅用于研究排序，不代表投资建议。"
            ),
        }
        db.add(item)
        results.append(item)
    db.commit()
    return sorted(results, key=lambda item: item.total_score, reverse=True)
