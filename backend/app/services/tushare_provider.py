from __future__ import annotations

import threading
import time
from datetime import date
from typing import Any

import httpx

from app.services.provider import _date, _number


class TushareError(RuntimeError):
    """A sanitized Tushare error that never includes the configured token."""


class TushareClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.tushare.pro",
        timeout_seconds: float = 15,
        min_interval_seconds: float = 0.35,
        client: httpx.Client | None = None,
    ) -> None:
        if not token.strip():
            raise ValueError("Tushare token is required.")
        self._token = token.strip()
        self._base_url = base_url
        self._min_interval_seconds = max(0.0, min_interval_seconds)
        self._client = client or httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=True,
        )
        self._lock = threading.Lock()
        self._last_request_at = 0.0

    def query(
        self,
        api_name: str,
        params: dict[str, Any] | None = None,
        fields: list[str] | tuple[str, ...] = (),
    ) -> list[dict[str, Any]]:
        with self._lock:
            elapsed = time.monotonic() - self._last_request_at
            delay = self._min_interval_seconds - elapsed
            if delay > 0:
                time.sleep(delay)
            try:
                response = self._client.post(
                    self._base_url,
                    json={
                        "api_name": api_name,
                        "token": self._token,
                        "params": params or {},
                        "fields": ",".join(fields),
                    },
                )
                self._last_request_at = time.monotonic()
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise TushareError(f"Tushare {api_name} request failed.") from exc

        code = payload.get("code")
        if code != 0:
            message = str(payload.get("msg") or "unknown API error").strip()
            message = message.replace(self._token, "***")
            raise TushareError(f"Tushare {api_name} rejected the request: {message}")
        data = payload.get("data") or {}
        response_fields = data.get("fields") or []
        return [
            dict(zip(response_fields, values, strict=False))
            for values in (data.get("items") or [])
        ]


class TushareProvider:
    """Tushare Pro adapter for structured market and financial data."""

    source = "tushare-pro"
    _INDICATOR_FIELDS = {
        "eps": "每股收益",
        "bps": "每股净资产",
        "ocfps": "每股经营现金流量",
        "roe": "净资产收益率",
        "roa": "总资产收益率",
        "or_yoy": "营业总收入同比增长",
        "netprofit_yoy": "净利润同比增长",
        "grossprofit_margin": "销售毛利率",
        "debt_to_assets": "资产负债率",
    }
    _STATEMENT_FIELDS = {
        "income": {
            "total_revenue": "营业总收入",
            "revenue": "营业收入",
            "operate_profit": "营业利润",
            "total_profit": "利润总额",
            "n_income_attr_p": "归母净利润",
        },
        "balancesheet": {
            "total_assets": "资产总计",
            "total_liab": "负债合计",
            "total_hldr_eqy_exc_min_int": "归母股东权益合计",
        },
        "cashflow": {
            "n_cashflow_act": "经营活动现金流量净额",
            "n_cashflow_inv_act": "投资活动现金流量净额",
            "n_cash_flows_fnc_act": "筹资活动现金流量净额",
            "c_cash_equ_end_period": "期末现金及现金等价物余额",
        },
    }

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.tushare.pro",
        timeout_seconds: float = 15,
        min_interval_seconds: float = 0.35,
        client: TushareClient | None = None,
    ) -> None:
        self.client = client or TushareClient(
            token=token,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            min_interval_seconds=min_interval_seconds,
        )

    @staticmethod
    def _stock_ts_code(symbol: str) -> str:
        clean = symbol.split(".", 1)[0].zfill(6)
        if clean.startswith(("4", "8")):
            exchange = "BJ"
        elif clean.startswith(("5", "6", "9")):
            exchange = "SH"
        else:
            exchange = "SZ"
        return f"{clean}.{exchange}"

    @staticmethod
    def _index_ts_code(symbol: str) -> str:
        clean = symbol.split(".", 1)[0].zfill(6)
        return f"{clean}.{'SZ' if clean.startswith('399') else 'SH'}"

    @staticmethod
    def _report_period(report_date: date) -> str:
        return {
            (3, 31): "一季报",
            (6, 30): "半年报",
            (9, 30): "三季报",
            (12, 31): "年报",
        }.get((report_date.month, report_date.day), "")

    def stock_snapshot(self) -> list[dict[str, Any]]:
        records = self.client.query(
            "stock_basic",
            {"exchange": "", "list_status": "L"},
            ("symbol", "name", "industry", "market"),
        )
        return [
            {
                "symbol": str(record.get("symbol", "")).zfill(6),
                "name": str(record.get("name", "")),
                "industry": str(record.get("industry") or ""),
                "market": str(record.get("market") or "A"),
                "latest": None,
                "change_percent": None,
                "pe": None,
                "pb": None,
                "market_cap": None,
            }
            for record in records
            if record.get("symbol")
        ]

    def trading_calendar(self) -> list[dict[str, Any]]:
        end_year = date.today().year + 1
        ranges = ((1990, 1999), (2000, 2009), (2010, 2019), (2020, end_year))
        records: list[dict[str, Any]] = []
        for start_year, range_end_year in ranges:
            records.extend(
                self.client.query(
                    "trade_cal",
                    {
                        "exchange": "SSE",
                        "start_date": f"{start_year}0101",
                        "end_date": f"{range_end_year}1231",
                    },
                    ("cal_date", "is_open"),
                )
            )
        rows = [
            {
                "trade_date": _date(record.get("cal_date")),
                "is_open": str(record.get("is_open")) == "1",
                "source": self.source,
            }
            for record in records
            if record.get("cal_date")
        ]
        return sorted(rows, key=lambda row: row["trade_date"])

    def index_prices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        records = self.client.query(
            "index_daily",
            {
                "ts_code": self._index_ts_code(symbol),
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d"),
            },
            ("trade_date", "open", "high", "low", "close", "vol", "amount"),
        )
        names = {
            "000300": "沪深300",
            "000905": "中证500",
            "000852": "中证1000",
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
        }
        rows = []
        for record in records:
            close = _number(record.get("close"))
            if close is None or close <= 0:
                continue
            rows.append(
                {
                    "symbol": symbol,
                    "name": names.get(symbol, symbol),
                    "trade_date": _date(record.get("trade_date")),
                    "open": _number(record.get("open")) or close,
                    "high": _number(record.get("high")) or close,
                    "low": _number(record.get("low")) or close,
                    "close": close,
                    "volume": _number(record.get("vol")) or 0,
                    "amount": (_number(record.get("amount")) or 0) * 1000,
                    "source": self.source,
                }
            )
        return sorted(rows, key=lambda row: row["trade_date"])

    def daily_prices(
        self, symbol: str, start_date: date, end_date: date, adjustment: str = "qfq"
    ) -> list[dict[str, Any]]:
        ts_code = self._stock_ts_code(symbol)
        params = {
            "ts_code": ts_code,
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
        }
        prices = self.client.query(
            "daily",
            params,
            ("trade_date", "open", "high", "low", "close", "vol", "amount"),
        )
        basics = self.client.query(
            "daily_basic",
            params,
            ("trade_date", "turnover_rate"),
        )
        turnover_by_date = {
            str(record.get("trade_date")): _number(record.get("turnover_rate"))
            for record in basics
        }
        factors: dict[str, float] = {}
        latest_factor = 1.0
        if adjustment == "qfq":
            factor_rows = self.client.query(
                "adj_factor",
                params,
                ("trade_date", "adj_factor"),
            )
            factors = {
                str(record.get("trade_date")): value
                for record in factor_rows
                if (value := _number(record.get("adj_factor"))) is not None
            }
            if factors:
                latest_date = max(factors)
                latest_factor = factors[latest_date]

        rows = []
        for record in prices:
            trade_date = str(record.get("trade_date"))
            close = _number(record.get("close"))
            if not trade_date or close is None or close <= 0:
                continue
            ratio = factors.get(trade_date, latest_factor) / latest_factor
            rows.append(
                {
                    "symbol": symbol,
                    "trade_date": _date(trade_date),
                    "open": (_number(record.get("open")) or close) * ratio,
                    "high": (_number(record.get("high")) or close) * ratio,
                    "low": (_number(record.get("low")) or close) * ratio,
                    "close": close * ratio,
                    "volume": _number(record.get("vol")) or 0,
                    "amount": (_number(record.get("amount")) or 0) * 1000,
                    "turnover_rate": turnover_by_date.get(trade_date),
                    "adjustment": adjustment,
                    "source": self.source,
                }
            )
        return sorted(rows, key=lambda row: row["trade_date"])

    def _indicator_records(
        self, symbol: str, period: date | None = None
    ) -> list[dict[str, Any]]:
        params = {"ts_code": self._stock_ts_code(symbol)}
        if period is not None:
            params["period"] = period.strftime("%Y%m%d")
        else:
            today = date.today()
            params["start_date"] = f"{today.year - 6}0101"
            params["end_date"] = today.strftime("%Y%m%d")
        fields = (
            "ann_date",
            "end_date",
            *self._INDICATOR_FIELDS.keys(),
        )
        return self.client.query("fina_indicator", params, fields)

    def financial_metrics(self, symbol: str) -> list[dict[str, Any]]:
        rows = self._normalize_financial_records(
            symbol,
            self._indicator_records(symbol),
            self._INDICATOR_FIELDS,
        )
        for api_name, field_map in self._STATEMENT_FIELDS.items():
            try:
                today = date.today()
                records = self.client.query(
                    api_name,
                    {
                        "ts_code": self._stock_ts_code(symbol),
                        "start_date": f"{today.year - 6}0101",
                        "end_date": today.strftime("%Y%m%d"),
                    },
                    ("ann_date", "f_ann_date", "end_date", *field_map.keys()),
                )
            except TushareError:
                continue
            rows.extend(self._normalize_financial_records(symbol, records, field_map))
        unique: dict[tuple[date, str], dict[str, Any]] = {}
        for row in sorted(
            rows,
            key=lambda item: (item["report_date"], item.get("_ann_date") or date.min),
            reverse=True,
        ):
            unique.setdefault((row["report_date"], row["metric_name"]), row)
        for row in unique.values():
            row.pop("_ann_date", None)
        return sorted(
            unique.values(),
            key=lambda item: (item["report_date"], item["metric_name"]),
            reverse=True,
        )

    def _normalize_financial_records(
        self,
        symbol: str,
        records: list[dict[str, Any]],
        field_map: dict[str, str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for record in records:
            if not record.get("end_date"):
                continue
            report_date = _date(record.get("end_date"))
            announcement = record.get("ann_date") or record.get("f_ann_date")
            for field, metric_name in field_map.items():
                value = _number(record.get(field))
                if value is None:
                    continue
                rows.append(
                    {
                        "symbol": symbol,
                        "report_date": report_date,
                        "report_period": self._report_period(report_date),
                        "metric_name": metric_name,
                        "metric_value": value,
                        "yoy": None,
                        "source": self.source,
                        "_ann_date": _date(announcement) if announcement else date.min,
                    }
                )
        return rows

    def point_in_time_financials(
        self, report_date: date, symbols: list[str]
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in symbols:
            for record in self._indicator_records(symbol, report_date):
                if not record.get("end_date") or not record.get("ann_date"):
                    continue
                actual_report_date = _date(record.get("end_date"))
                if actual_report_date != report_date:
                    continue
                for field, metric_name in self._INDICATOR_FIELDS.items():
                    value = _number(record.get(field))
                    if value is None:
                        continue
                    rows.append(
                        {
                            "symbol": symbol,
                            "report_date": report_date,
                            "available_at": _date(record.get("ann_date")),
                            "metric_name": metric_name,
                            "metric_value": value,
                            "source": self.source,
                            "is_estimated": False,
                        }
                    )
        return rows
