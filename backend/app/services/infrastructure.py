from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models import IndexPrice, PointInTimeFinancial, TradingCalendar
from app.services.provider import AkshareProvider
from app.services.repository import upsert_calendar, upsert_index_prices, upsert_pit_financials

ProgressCallback = Callable[[float, str], None]


def quarter_ends(start_date: date, end_date: date) -> list[date]:
    results: list[date] = []
    for year in range(start_date.year, end_date.year + 1):
        for month, day in ((3, 31), (6, 30), (9, 30), (12, 31)):
            value = date(year, month, day)
            if start_date <= value <= end_date:
                results.append(value)
    return results


def sync_trading_calendar(
    db: Session, provider: AkshareProvider | None = None
) -> dict[str, Any]:
    provider = provider or AkshareProvider()
    rows = provider.trading_calendar()
    actual_dates = {row["trade_date"] for row in rows}
    for demo_row in db.query(TradingCalendar).filter(TradingCalendar.source == "demo").all():
        if demo_row.trade_date not in actual_dates:
            db.delete(demo_row)
    count = upsert_calendar(db, rows)
    db.commit()
    return {
        "calendar_rows": count,
        "first_date": rows[0]["trade_date"].isoformat() if rows else None,
        "last_date": rows[-1]["trade_date"].isoformat() if rows else None,
    }


def sync_index_data(
    db: Session,
    symbol: str,
    start_date: date,
    end_date: date,
    provider: AkshareProvider | None = None,
) -> dict[str, Any]:
    provider = provider or AkshareProvider()
    rows = provider.index_prices(symbol, start_date, end_date)
    actual_dates = {row["trade_date"] for row in rows}
    demo_rows = (
        db.query(IndexPrice)
        .filter(
            IndexPrice.symbol == symbol,
            IndexPrice.source == "demo",
            IndexPrice.trade_date >= start_date,
            IndexPrice.trade_date <= end_date,
        )
        .all()
    )
    for demo_row in demo_rows:
        if demo_row.trade_date not in actual_dates:
            db.delete(demo_row)
    count = upsert_index_prices(db, rows)
    upsert_calendar(
        db,
        [
            {
                "trade_date": row["trade_date"],
                "is_open": True,
                "source": f"{row['source']}-observed",
            }
            for row in rows
        ],
    )
    db.commit()
    return {
        "index_symbol": symbol,
        "index_rows": count,
        "source": rows[-1]["source"] if rows else None,
    }


def sync_pit_financials(
    db: Session,
    symbols: list[str],
    report_dates: list[date],
    provider: AkshareProvider | None = None,
    progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    provider = provider or AkshareProvider()
    total = 0
    errors: list[dict[str, str]] = []
    for index, report_date in enumerate(report_dates, 1):
        try:
            rows = provider.point_in_time_financials(report_date, symbols)
            total += upsert_pit_financials(db, rows)
            real_symbols = {row["symbol"] for row in rows}
            if real_symbols:
                demo_rows = (
                    db.query(PointInTimeFinancial)
                    .filter(
                        PointInTimeFinancial.source == "demo",
                        PointInTimeFinancial.symbol.in_(real_symbols),
                    )
                    .all()
                )
                for demo_row in demo_rows:
                    db.delete(demo_row)
            db.commit()
        except Exception as exc:
            db.rollback()
            errors.append({"report_date": report_date.isoformat(), "error": str(exc)[:300]})
        if progress:
            progress(index / max(1, len(report_dates)), f"已处理 {report_date.isoformat()}")
    return {
        "financial_rows": total,
        "report_dates": [item.isoformat() for item in report_dates],
        "errors": errors,
    }


def sync_research_infrastructure(
    db: Session,
    symbols: list[str],
    benchmark_symbol: str,
    start_date: date,
    end_date: date,
    report_dates: list[date] | None = None,
    progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    if progress:
        progress(0.05, "同步交易日历")
    results["calendar"] = sync_trading_calendar(db)
    if progress:
        progress(0.18, "同步指数基准")
    results["benchmark"] = sync_index_data(
        db, benchmark_symbol, start_date, end_date
    )
    dates = report_dates or quarter_ends(start_date, end_date)

    def financial_progress(value: float, message: str) -> None:
        if progress:
            progress(0.2 + value * 0.78, message)

    results["financials"] = sync_pit_financials(
        db, symbols, dates, progress=financial_progress
    )
    if progress:
        progress(1.0, "研究基础数据同步完成")
    return results
