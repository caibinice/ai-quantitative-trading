from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.services.provider import AkshareProvider, _number, content_hash


def test_number_normalizes_commas_and_percent() -> None:
    assert _number("1,234.50") == 1234.5
    assert _number("12.3%") == 12.3
    assert _number("-") is None


def test_content_hash_is_stable_and_symbol_specific() -> None:
    published = datetime(2025, 1, 1)
    first = content_hash("000001", "公告", "https://example.test/1", published)
    same = content_hash("000001", "公告", "https://example.test/1", published)
    other = content_hash("600000", "公告", "https://example.test/1", published)

    assert first == same
    assert first != other


def test_tencent_price_fallback_normalization() -> None:
    frame = pd.DataFrame(
        [
            {
                "date": "2025-01-02",
                "open": 10,
                "close": 10.5,
                "high": 10.6,
                "low": 9.9,
                "amount": 1234,
            }
        ]
    )
    rows = AkshareProvider()._normalize_tencent_prices(frame, "000001", "qfq")

    assert rows[0]["trade_date"].isoformat() == "2025-01-02"
    assert rows[0]["close"] == 10.5
    assert rows[0]["source"] == "akshare-tencent"
