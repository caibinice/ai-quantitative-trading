from __future__ import annotations

from datetime import date

import pandas as pd

from app.services.infrastructure import quarter_ends
from app.services.provider import AkshareProvider


def test_quarter_ends_stay_inside_requested_range() -> None:
    values = quarter_ends(date(2024, 5, 1), date(2025, 4, 1))
    assert values == [date(2024, 6, 30), date(2024, 9, 30), date(2024, 12, 31), date(2025, 3, 31)]


def test_point_in_time_financials_use_announcement_date() -> None:
    frame = pd.DataFrame(
        [
            {
                "股票代码": "000001",
                "最新公告日期": "2025-04-22",
                "净资产收益率": 8.5,
                "营业总收入-同比增长": 6.2,
            },
            {
                "股票代码": "600000",
                "最新公告日期": "2025-04-20",
                "净资产收益率": 7.0,
            },
        ]
    )

    class FakeAk:
        @staticmethod
        def stock_yjbb_em(date: str):
            return frame

    provider = AkshareProvider()
    provider._ak = lambda: FakeAk()  # type: ignore[method-assign]
    rows = provider.point_in_time_financials(date(2025, 3, 31), ["000001"])

    assert rows
    assert {row["symbol"] for row in rows} == {"000001"}
    assert {row["available_at"] for row in rows} == {date(2025, 4, 22)}


def test_index_prices_fall_back_to_tencent() -> None:
    frame = pd.DataFrame(
        [{"date": "2025-01-02", "open": 10, "close": 11, "high": 12, "low": 9, "amount": 99}]
    )

    class FakeAk:
        @staticmethod
        def index_zh_a_hist(**_kwargs):
            raise ConnectionError("blocked")

        @staticmethod
        def stock_zh_index_daily_tx(**_kwargs):
            return frame

    provider = AkshareProvider()
    provider._ak = lambda: FakeAk()  # type: ignore[method-assign]
    rows = provider.index_prices("000300", date(2025, 1, 1), date(2025, 1, 3))

    assert rows[0]["source"] == "akshare-tencent"
    assert rows[0]["name"] == "沪深300"
