from __future__ import annotations

from datetime import date, datetime, timedelta

from app.models import PointInTimeFinancial
from app.services.scoring import (
    momentum_component,
    quality_component,
    sentiment_component,
)


def test_momentum_rewards_a_stable_uptrend() -> None:
    rising_score, _ = momentum_component([100 + index for index in range(80)])
    falling_score, _ = momentum_component([180 - index for index in range(80)])

    assert rising_score > 50
    assert falling_score < 50
    assert rising_score > falling_score


def test_momentum_blocks_extreme_price_contamination() -> None:
    prices = [100 + index * 0.2 for index in range(30)]
    prices[15] = 3.0

    score, detail = momentum_component(prices)

    assert score == 50
    assert detail["status"] == "blocked_by_price_anomaly"
    assert detail["anomaly_count"] >= 2


def test_recent_sentiment_has_more_weight() -> None:
    as_of = date(2025, 6, 30)
    events = [
        (-1.0, 1.0, datetime.combine(as_of - timedelta(days=25), datetime.min.time())),
        (1.0, 1.0, datetime.combine(as_of, datetime.min.time())),
    ]
    score, count = sentiment_component(events, as_of)

    assert count == 2
    assert score > 50


def test_quality_accepts_real_profit_growth_metric() -> None:
    metric = PointInTimeFinancial(
        symbol="000001",
        report_date=date(2026, 3, 31),
        available_at=date(2026, 4, 25),
        metric_name="净利润同比增长",
        metric_value=25.0,
        source="akshare",
    )

    score, detail = quality_component([metric])

    assert score > 50
    assert detail == {"净利润同比增长": 25.0}


def test_quality_does_not_treat_absolute_revenue_as_a_ratio() -> None:
    metric = PointInTimeFinancial(
        symbol="000001",
        report_date=date(2026, 3, 31),
        available_at=date(2026, 4, 25),
        metric_name="营业总收入",
        metric_value=99_999_999_999.0,
        source="akshare",
    )

    score, detail = quality_component([metric])

    assert score == 50
    assert detail == {}
