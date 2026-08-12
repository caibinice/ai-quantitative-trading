from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.services.provider import HybridDataProvider
from app.services.tushare_provider import TushareClient, TushareError, TushareProvider


class FakeQueryClient:
    def __init__(self, responses: dict[str, list[dict[str, Any]]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def query(
        self,
        api_name: str,
        params: dict[str, Any] | None = None,
        fields: tuple[str, ...] = (),
    ) -> list[dict[str, Any]]:
        del fields
        self.calls.append((api_name, params or {}))
        return self.responses.get(api_name, [])


def test_tushare_client_maps_rows_and_never_exposes_token() -> None:
    token = "secret-test-token"

    def handler(request: httpx.Request) -> httpx.Response:
        if b"failing_api" in request.content:
            return httpx.Response(
                200,
                json={"code": 40203, "msg": f"permission denied for {token}", "data": None},
            )
        return httpx.Response(
            200,
            json={
                "code": 0,
                "msg": None,
                "data": {"fields": ["symbol", "name"], "items": [["000001", "平安银行"]]},
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = TushareClient(
        token,
        client=http_client,
        min_interval_seconds=0,
    )

    assert client.query("stock_basic")[0]["name"] == "平安银行"

    try:
        client.query("failing_api")
    except TushareError as exc:
        assert token not in str(exc)
        assert "***" in str(exc)
    else:
        raise AssertionError("Expected a sanitized TushareError.")


def test_daily_prices_apply_qfq_and_normalize_amount_units() -> None:
    client = FakeQueryClient(
        {
            "daily": [
                {
                    "trade_date": "20260724",
                    "open": 100,
                    "high": 110,
                    "low": 90,
                    "close": 105,
                    "vol": 20,
                    "amount": 30,
                },
                {
                    "trade_date": "20260725",
                    "open": 52,
                    "high": 55,
                    "low": 50,
                    "close": 54,
                    "vol": 40,
                    "amount": 60,
                },
            ],
            "daily_basic": [
                {"trade_date": "20260724", "turnover_rate": 1.2},
                {"trade_date": "20260725", "turnover_rate": 1.5},
            ],
            "adj_factor": [
                {"trade_date": "20260724", "adj_factor": 1},
                {"trade_date": "20260725", "adj_factor": 2},
            ],
        }
    )
    provider = TushareProvider(token="unused", client=client)  # type: ignore[arg-type]

    rows = provider.daily_prices(
        "600519", date(2026, 7, 24), date(2026, 7, 25)
    )

    assert [row["trade_date"] for row in rows] == [
        date(2026, 7, 24),
        date(2026, 7, 25),
    ]
    assert rows[0]["close"] == 52.5
    assert rows[1]["close"] == 54
    assert rows[0]["amount"] == 30_000
    assert rows[1]["turnover_rate"] == 1.5
    assert rows[1]["source"] == "tushare-pro"


def test_financial_metrics_and_point_in_time_use_announcement_date() -> None:
    client = FakeQueryClient(
        {
            "fina_indicator": [
                {
                    "ann_date": "20260420",
                    "end_date": "20260331",
                    "roe": 8.2,
                    "or_yoy": 6.5,
                    "netprofit_yoy": 7.1,
                    "grossprofit_margin": 42.0,
                }
            ],
            "income": [
                {
                    "ann_date": "20260420",
                    "end_date": "20260331",
                    "total_revenue": 12_000,
                    "n_income_attr_p": 2_000,
                }
            ],
            "balancesheet": [
                {
                    "ann_date": "20260420",
                    "end_date": "20260331",
                    "total_assets": 30_000,
                    "total_liab": 10_000,
                }
            ],
            "cashflow": [
                {
                    "ann_date": "20260420",
                    "end_date": "20260331",
                    "n_cashflow_act": 1_800,
                }
            ],
        }
    )
    provider = TushareProvider(token="unused", client=client)  # type: ignore[arg-type]

    metrics = provider.financial_metrics("000001")
    metric_names = {row["metric_name"] for row in metrics}
    pit = provider.point_in_time_financials(date(2026, 3, 31), ["000001"])

    assert {"净资产收益率", "营业总收入", "资产总计", "经营活动现金流量净额"} <= metric_names
    assert {row["source"] for row in metrics} == {"tushare-pro"}
    assert {row["available_at"] for row in pit} == {date(2026, 4, 20)}
    assert {row["symbol"] for row in pit} == {"000001"}


def test_hybrid_provider_falls_back_for_structured_data_and_keeps_public_news() -> None:
    class Primary:
        @staticmethod
        def daily_prices(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
            raise TushareError("temporarily unavailable")

    class Fallback:
        @staticmethod
        def daily_prices(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
            return [{"source": "akshare"}]

        @staticmethod
        def news(symbol: str) -> list[dict[str, Any]]:
            return [{"symbol": symbol, "source": "东方财富"}]

    provider = HybridDataProvider(Primary(), Fallback())  # type: ignore[arg-type]

    assert provider.daily_prices("000001", date.today(), date.today())[0]["source"] == "akshare"
    assert provider.news("000001")[0]["source"] == "东方财富"
