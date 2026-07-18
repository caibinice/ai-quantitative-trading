"""Build a reproducible time-decayed sentiment factor."""

from __future__ import annotations

import math
from datetime import date


def sentiment_factor(
    events: list[tuple[date, float, float]],
    as_of: date,
    half_life_days: float = 7,
) -> float:
    usable = [event for event in events if event[0] <= as_of]
    if not usable:
        return 0.0
    weighted_score = 0.0
    total_weight = 0.0
    for published_at, score, confidence in usable:
        age = (as_of - published_at).days
        weight = confidence * math.exp(-math.log(2) * age / half_life_days)
        weighted_score += score * weight
        total_weight += weight
    return weighted_score / total_weight


def main() -> None:
    as_of = date(2026, 3, 20)
    events = [
        (date(2026, 3, 1), -0.6, 0.8),
        (date(2026, 3, 18), 0.7, 0.9),
        (date(2026, 3, 22), 1.0, 1.0),  # Future event: intentionally excluded.
    ]
    sentiment = sentiment_factor(events, as_of)
    momentum_score = 0.2
    combined = 0.7 * momentum_score + 0.3 * sentiment

    print("as of:", as_of)
    print("time-decayed sentiment:", round(sentiment, 4))
    print("combined momentum + sentiment:", round(combined, 4))
    print("DEMO_OK")


if __name__ == "__main__":
    main()
