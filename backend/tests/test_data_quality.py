from __future__ import annotations

from datetime import date

from app.models import DailyPrice
from app.services.data_quality import detect_price_issues


def _row(day: int, open_price: float, high: float, low: float, close: float) -> DailyPrice:
    return DailyPrice(
        symbol="000001",
        trade_date=date(2025, 1, day),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=100,
        amount=1000,
    )


def test_quality_rules_detect_ohlc_and_calendar_gap() -> None:
    rows = [_row(2, 10, 9, 8, 11), _row(6, 11, 12, 10, 11.5)]
    calendar = {date(2025, 1, 2), date(2025, 1, 3), date(2025, 1, 6)}
    issues = detect_price_issues("000001", rows, calendar)
    categories = {item["category"] for item in issues}

    assert "ohlc_invalid" in categories
    assert "calendar_gap" in categories
