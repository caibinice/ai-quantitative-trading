from __future__ import annotations

from datetime import date, datetime, timedelta

from app.models import PointInTimeFinancial
from app.services.scoring import (
    deduplicate_sentiment_events,
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


def test_sentiment_excludes_events_outside_the_recent_window() -> None:
    as_of = date(2025, 6, 30)
    events = [
        (-1.0, 1.0, datetime.combine(as_of - timedelta(days=25), datetime.min.time())),
        (1.0, 1.0, datetime.combine(as_of, datetime.min.time())),
    ]
    score, count = sentiment_component(events, as_of)

    assert count == 1
    assert score > 50


def test_recent_negative_events_override_legacy_positive_history() -> None:
    as_of = date(2026, 8, 28)
    events = [
        (0.9, 0.9, datetime.combine(as_of - timedelta(days=20), datetime.min.time())),
        (0.7, 0.8, datetime.combine(as_of - timedelta(days=12), datetime.min.time())),
        (-0.6, 0.7, datetime.combine(as_of - timedelta(days=1), datetime.min.time())),
        (-0.5, 0.8, datetime.combine(as_of, datetime.min.time())),
    ]

    score, count = sentiment_component(events, as_of, lookback_days=7)

    assert count == 2
    assert score < 50


def test_sparse_sentiment_evidence_shrinks_toward_neutral() -> None:
    as_of = date(2026, 8, 28)
    events = [(1.0, 0.05, datetime.combine(as_of, datetime.max.time()))]

    score, count = sentiment_component(events, as_of)

    assert count == 1
    assert 50 < score < 55


def test_same_stock_news_is_counted_once_in_sentiment_factor() -> None:
    published = datetime(2025, 6, 30, 10)
    events = [
        (0.8, 0.9, published, "公司签署重大合同", "合同金额十亿元", "https://a/1", "news"),
        (0.8, 0.9, published, "公司签署重大合同！", "合同金额十亿元。", "https://b/2", "news"),
    ]

    unique = deduplicate_sentiment_events(events)

    assert len(unique) == 1


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
