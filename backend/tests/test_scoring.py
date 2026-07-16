from __future__ import annotations

from datetime import date, datetime, timedelta

from app.services.scoring import momentum_component, sentiment_component


def test_momentum_rewards_a_stable_uptrend() -> None:
    rising_score, _ = momentum_component([100 + index for index in range(80)])
    falling_score, _ = momentum_component([180 - index for index in range(80)])

    assert rising_score > 50
    assert falling_score < 50
    assert rising_score > falling_score


def test_recent_sentiment_has_more_weight() -> None:
    as_of = date(2025, 6, 30)
    events = [
        (-1.0, 1.0, datetime.combine(as_of - timedelta(days=25), datetime.min.time())),
        (1.0, 1.0, datetime.combine(as_of, datetime.min.time())),
    ]
    score, count = sentiment_component(events, as_of)

    assert count == 2
    assert score > 50
