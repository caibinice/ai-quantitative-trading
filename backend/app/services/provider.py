from __future__ import annotations

import hashlib
from datetime import date, datetime
from typing import Any, Protocol

import pandas as pd


def _number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _date(value: Any) -> date:
    return pd.to_datetime(value).date()


def _datetime(value: Any) -> datetime:
    parsed = pd.to_datetime(value)
    return parsed.to_pydatetime().replace(tzinfo=None)


def content_hash(symbol: str | None, title: str, url: str, published_at: datetime) -> str:
    value = f"{symbol or ''}|{title}|{url}|{published_at.isoformat()}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class AkshareProvider:
    """Small, replaceable adapter around public AKShare interfaces."""

    source = "akshare"

    @staticmethod
    def _ak():
        import akshare as ak

        return ak

    def stock_snapshot(self) -> list[dict[str, Any]]:
        df = self._ak().stock_zh_a_spot_em()
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            rows.append(
                {
                    "symbol": str(record.get("代码", "")).zfill(6),
                    "name": str(record.get("名称", "")),
                    "latest": _number(record.get("最新价")),
                    "change_percent": _number(record.get("涨跌幅")),
                    "pe": _number(record.get("市盈率-动态")),
                    "pb": _number(record.get("市净率")),
                    "market_cap": _number(record.get("总市值")),
                }
            )
        return rows

    def trading_calendar(self) -> list[dict[str, Any]]:
        df = self._ak().tool_trade_date_hist_sina()
        return [
            {
                "trade_date": _date(record.get("trade_date")),
                "is_open": True,
                "source": "akshare-sina",
            }
            for record in df.to_dict("records")
            if record.get("trade_date") is not None
        ]

    def index_prices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        ak = self._ak()
        try:
            df = ak.index_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            )
            records = [
                {
                    "symbol": symbol,
                    "name": self._index_name(symbol),
                    "trade_date": _date(record.get("日期")),
                    "open": _number(record.get("开盘")),
                    "high": _number(record.get("最高")),
                    "low": _number(record.get("最低")),
                    "close": _number(record.get("收盘")),
                    "volume": _number(record.get("成交量")) or 0,
                    "amount": _number(record.get("成交额")) or 0,
                    "source": "akshare-eastmoney",
                }
                for record in df.to_dict("records")
            ]
        except Exception:
            market_symbol = self._index_market_symbol(symbol)
            df = ak.stock_zh_index_daily_tx(
                symbol=market_symbol,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            )
            records = [
                {
                    "symbol": symbol,
                    "name": self._index_name(symbol),
                    "trade_date": _date(record.get("date")),
                    "open": _number(record.get("open")),
                    "high": _number(record.get("high")),
                    "low": _number(record.get("low")),
                    "close": _number(record.get("close")),
                    "volume": _number(record.get("amount")) or 0,
                    "amount": 0,
                    "source": "akshare-tencent",
                }
                for record in df.to_dict("records")
            ]
        return [
            row
            for row in records
            if row["close"] is not None
            and row["close"] > 0
            and row["open"] is not None
            and row["high"] is not None
            and row["low"] is not None
        ]

    def point_in_time_financials(
        self, report_date: date, symbols: list[str]
    ) -> list[dict[str, Any]]:
        df = self._ak().stock_yjbb_em(date=report_date.strftime("%Y%m%d"))
        wanted = set(symbols)
        metric_columns = {
            "每股收益": "每股收益",
            "营业总收入": "营业总收入-营业总收入",
            "营业总收入同比增长": "营业总收入-同比增长",
            "净利润": "净利润-净利润",
            "净利润同比增长": "净利润-同比增长",
            "每股净资产": "每股净资产",
            "净资产收益率": "净资产收益率",
            "每股经营现金流量": "每股经营现金流量",
            "销售毛利率": "销售毛利率",
        }
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            symbol = str(record.get("股票代码", "")).zfill(6)
            if symbol not in wanted or pd.isna(record.get("最新公告日期")):
                continue
            available_at = _date(record.get("最新公告日期"))
            for metric_name, column in metric_columns.items():
                value = _number(record.get(column))
                if value is None:
                    continue
                rows.append(
                    {
                        "symbol": symbol,
                        "report_date": report_date,
                        "available_at": available_at,
                        "metric_name": metric_name,
                        "metric_value": value,
                        "source": "akshare-yjbb",
                        "is_estimated": False,
                    }
                )
        return rows

    @staticmethod
    def _index_market_symbol(symbol: str) -> str:
        return f"{'sz' if symbol.startswith('399') else 'sh'}{symbol}"

    @staticmethod
    def _index_name(symbol: str) -> str:
        return {
            "000300": "沪深300",
            "000905": "中证500",
            "000852": "中证1000",
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
        }.get(symbol, symbol)

    def daily_prices(
        self, symbol: str, start_date: date, end_date: date, adjustment: str = "qfq"
    ) -> list[dict[str, Any]]:
        ak = self._ak()
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust=adjustment,
            )
            return self._normalize_eastmoney_prices(df, symbol, adjustment)
        except Exception:
            # Eastmoney occasionally blocks a network route. Tencent provides a
            # second public daily endpoint for the common Shanghai/Shenzhen symbols.
            market_symbol = f"{'sh' if symbol.startswith(('5', '6', '9')) else 'sz'}{symbol}"
            df = ak.stock_zh_a_hist_tx(
                symbol=market_symbol,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust=adjustment,
            )
            return self._normalize_tencent_prices(df, symbol, adjustment)

    def _normalize_eastmoney_prices(
        self, df: pd.DataFrame, symbol: str, adjustment: str
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            close = _number(record.get("收盘"))
            if close is None or close <= 0:
                continue
            rows.append(
                {
                    "symbol": symbol,
                    "trade_date": _date(record.get("日期")),
                    "open": _number(record.get("开盘")) or close,
                    "high": _number(record.get("最高")) or close,
                    "low": _number(record.get("最低")) or close,
                    "close": close,
                    "volume": _number(record.get("成交量")) or 0,
                    "amount": _number(record.get("成交额")) or 0,
                    "turnover_rate": _number(record.get("换手率")),
                    "adjustment": adjustment,
                    "source": self.source,
                }
            )
        return rows

    def _normalize_tencent_prices(
        self, df: pd.DataFrame, symbol: str, adjustment: str
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            close = _number(record.get("close"))
            if close is None or close <= 0:
                continue
            rows.append(
                {
                    "symbol": symbol,
                    "trade_date": _date(record.get("date")),
                    "open": _number(record.get("open")) or close,
                    "high": _number(record.get("high")) or close,
                    "low": _number(record.get("low")) or close,
                    "close": close,
                    "volume": _number(record.get("amount")) or 0,
                    "amount": 0,
                    "turnover_rate": None,
                    "adjustment": adjustment,
                    "source": "akshare-tencent",
                }
            )
        return rows

    def financial_metrics(self, symbol: str) -> list[dict[str, Any]]:
        ak = self._ak()
        try:
            df = ak.stock_financial_abstract_new_ths(symbol=symbol, indicator="按报告期")
            rows: list[dict[str, Any]] = []
            for record in df.to_dict("records"):
                report_date = record.get("report_date")
                metric_name = str(record.get("metric_name", "")).strip()
                if not report_date or not metric_name:
                    continue
                rows.append(
                    {
                        "symbol": symbol,
                        "report_date": _date(report_date),
                        "report_period": str(record.get("report_period", "")),
                        "metric_name": metric_name,
                        "metric_value": _number(record.get("value")),
                        "yoy": _number(record.get("yoy")),
                        "source": self.source,
                    }
                )
            return rows
        except Exception:
            # Sina's wide table is a useful fallback when the THS interface changes.
            df = ak.stock_financial_abstract(symbol=symbol)
            rows = []
            date_columns = [column for column in df.columns if str(column).isdigit()]
            for record in df.to_dict("records"):
                metric_name = str(record.get("指标", "")).strip()
                for column in date_columns:
                    value = _number(record.get(column))
                    if not metric_name or value is None:
                        continue
                    rows.append(
                        {
                            "symbol": symbol,
                            "report_date": _date(str(column)),
                            "report_period": str(record.get("选项", "")),
                            "metric_name": metric_name,
                            "metric_value": value,
                            "yoy": None,
                            "source": self.source,
                        }
                    )
            return rows

    def news(self, symbol: str) -> list[dict[str, Any]]:
        df = self._ak().stock_news_em(symbol=symbol)
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            title = str(record.get("新闻标题", "")).strip()
            if not title:
                continue
            published_at = _datetime(record.get("发布时间"))
            url = str(record.get("新闻链接", ""))
            rows.append(
                {
                    "symbol": symbol,
                    "kind": "news",
                    "title": title,
                    "content": str(record.get("新闻内容", "")),
                    "source": str(record.get("文章来源", "东方财富")),
                    "source_url": url,
                    "published_at": published_at,
                    "content_hash": content_hash(symbol, title, url, published_at),
                }
            )
        return rows

    def notices(self, symbol: str, start_date: date, end_date: date) -> list[dict[str, Any]]:
        df = self._ak().stock_individual_notice_report(
            security=symbol,
            symbol="全部",
            begin_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            title = str(record.get("公告标题", "")).strip()
            if not title:
                continue
            published_at = datetime.combine(_date(record.get("公告日期")), datetime.min.time())
            url = str(record.get("网址", ""))
            rows.append(
                {
                    "symbol": symbol,
                    "kind": "notice",
                    "title": title,
                    "content": str(record.get("公告类型", "")),
                    "source": "东方财富公告",
                    "source_url": url,
                    "published_at": published_at,
                    "content_hash": content_hash(symbol, title, url, published_at),
                }
            )
        return rows

    def cninfo_notices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        """Fetch official disclosure announcements exposed by CNINFO via AKShare."""
        df = self._ak().stock_zh_a_disclosure_report_cninfo(
            symbol=symbol,
            market="沪深京",
            keyword="",
            category="",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
        rows: list[dict[str, Any]] = []
        for record in df.to_dict("records"):
            title = str(record.get("公告标题", "")).strip()
            if not title or pd.isna(record.get("公告时间")):
                continue
            published_at = datetime.combine(
                _date(record.get("公告时间")), datetime.min.time()
            )
            url = str(record.get("公告链接", ""))
            rows.append(
                {
                    "symbol": symbol,
                    "kind": "notice",
                    "title": title,
                    "content": "巨潮资讯法定信息披露公告",
                    "source": "巨潮资讯",
                    "source_url": url,
                    "published_at": published_at,
                    "content_hash": content_hash(symbol, title, url, published_at),
                }
            )
        return rows


class ResearchDataProvider(Protocol):
    def stock_snapshot(self) -> list[dict[str, Any]]: ...

    def trading_calendar(self) -> list[dict[str, Any]]: ...

    def index_prices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]: ...

    def point_in_time_financials(
        self, report_date: date, symbols: list[str]
    ) -> list[dict[str, Any]]: ...

    def daily_prices(
        self, symbol: str, start_date: date, end_date: date, adjustment: str = "qfq"
    ) -> list[dict[str, Any]]: ...

    def financial_metrics(self, symbol: str) -> list[dict[str, Any]]: ...

    def news(self, symbol: str) -> list[dict[str, Any]]: ...

    def notices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]: ...

    def cninfo_notices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]: ...


class HybridDataProvider:
    """Prefer Tushare structured data while keeping public news and fallbacks."""

    def __init__(
        self,
        primary: ResearchDataProvider,
        fallback: AkshareProvider | None = None,
    ) -> None:
        self.primary = primary
        self.fallback = fallback or AkshareProvider()

    def _structured(self, method: str, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        try:
            rows = getattr(self.primary, method)(*args, **kwargs)
            if rows:
                return rows
        except Exception:
            pass
        return getattr(self.fallback, method)(*args, **kwargs)

    def stock_snapshot(self) -> list[dict[str, Any]]:
        return self._structured("stock_snapshot")

    def trading_calendar(self) -> list[dict[str, Any]]:
        return self._structured("trading_calendar")

    def index_prices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        return self._structured("index_prices", symbol, start_date, end_date)

    def point_in_time_financials(
        self, report_date: date, symbols: list[str]
    ) -> list[dict[str, Any]]:
        return self._structured("point_in_time_financials", report_date, symbols)

    def daily_prices(
        self, symbol: str, start_date: date, end_date: date, adjustment: str = "qfq"
    ) -> list[dict[str, Any]]:
        return self._structured(
            "daily_prices", symbol, start_date, end_date, adjustment
        )

    def financial_metrics(self, symbol: str) -> list[dict[str, Any]]:
        return self._structured("financial_metrics", symbol)

    def news(self, symbol: str) -> list[dict[str, Any]]:
        return self.fallback.news(symbol)

    def notices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        return self.fallback.notices(symbol, start_date, end_date)

    def cninfo_notices(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        return self.fallback.cninfo_notices(symbol, start_date, end_date)


def build_data_provider() -> ResearchDataProvider:
    from app.core.config import get_settings
    from app.services.tushare_provider import TushareProvider

    settings = get_settings()
    fallback = AkshareProvider()
    if not settings.tushare_enabled or not settings.tushare_token:
        return fallback
    primary = TushareProvider(
        token=settings.tushare_token,
        base_url=settings.tushare_base_url,
        timeout_seconds=settings.tushare_timeout_seconds,
        min_interval_seconds=settings.tushare_min_interval_seconds,
    )
    return HybridDataProvider(primary, fallback)
