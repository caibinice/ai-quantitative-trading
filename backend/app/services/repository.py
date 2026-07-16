from __future__ import annotations

from collections.abc import Iterable
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DailyPrice,
    FinancialMetric,
    IndexPrice,
    NewsItem,
    PointInTimeFinancial,
    Stock,
    TradingCalendar,
)

ModelT = TypeVar("ModelT")


def ensure_stock(db: Session, symbol: str, name: str = "") -> Stock:
    stock = db.get(Stock, symbol)
    if stock is None:
        stock = Stock(symbol=symbol, name=name or symbol)
        db.add(stock)
    elif name and (not stock.name or stock.name == stock.symbol):
        stock.name = name
    return stock


def upsert_prices(db: Session, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        existing = db.scalar(
            select(DailyPrice).where(
                DailyPrice.symbol == row["symbol"], DailyPrice.trade_date == row["trade_date"]
            )
        )
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            db.add(DailyPrice(**row))
        count += 1
    return count


def upsert_financials(db: Session, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        existing = db.scalar(
            select(FinancialMetric).where(
                FinancialMetric.symbol == row["symbol"],
                FinancialMetric.report_date == row["report_date"],
                FinancialMetric.metric_name == row["metric_name"],
            )
        )
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            db.add(FinancialMetric(**row))
        count += 1
    return count


def upsert_news(db: Session, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        existing = db.scalar(select(NewsItem).where(NewsItem.content_hash == row["content_hash"]))
        if existing is None:
            db.add(NewsItem(**row))
            count += 1
    return count


def upsert_calendar(db: Session, rows: Iterable[dict[str, Any]]) -> int:
    items = list(rows)
    existing_by_date: dict = {}
    dates = [row["trade_date"] for row in items]
    for start in range(0, len(dates), 1000):
        existing_rows = db.scalars(
            select(TradingCalendar).where(
                TradingCalendar.trade_date.in_(dates[start : start + 1000])
            )
        ).all()
        existing_by_date.update({item.trade_date: item for item in existing_rows})
    for row in items:
        existing = existing_by_date.get(row["trade_date"])
        if existing:
            existing.is_open = row.get("is_open", True)
            existing.source = row.get("source", existing.source)
        else:
            db.add(TradingCalendar(**row))
    return len(items)


def upsert_index_prices(db: Session, rows: Iterable[dict[str, Any]]) -> int:
    items = list(rows)
    existing_by_key: dict = {}
    symbols = {row["symbol"] for row in items}
    for symbol in symbols:
        symbol_dates = [row["trade_date"] for row in items if row["symbol"] == symbol]
        for start in range(0, len(symbol_dates), 1000):
            existing_rows = db.scalars(
                select(IndexPrice).where(
                    IndexPrice.symbol == symbol,
                    IndexPrice.trade_date.in_(symbol_dates[start : start + 1000]),
                )
            ).all()
            existing_by_key.update(
                {(item.symbol, item.trade_date): item for item in existing_rows}
            )
    for row in items:
        existing = existing_by_key.get((row["symbol"], row["trade_date"]))
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            db.add(IndexPrice(**row))
    return len(items)


def upsert_pit_financials(db: Session, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        existing = db.scalar(
            select(PointInTimeFinancial).where(
                PointInTimeFinancial.symbol == row["symbol"],
                PointInTimeFinancial.report_date == row["report_date"],
                PointInTimeFinancial.available_at == row["available_at"],
                PointInTimeFinancial.metric_name == row["metric_name"],
            )
        )
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            db.add(PointInTimeFinancial(**row))
        count += 1
    return count
