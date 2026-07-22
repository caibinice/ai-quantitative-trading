from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from typing import Any, TypeVar

from sqlalchemy import delete, select
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
from app.services.news_dedup import is_duplicate_news

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
    items = list(rows)
    real_rows = [row for row in items if row.get("source") != "demo"]
    for symbol in {row["symbol"] for row in real_rows}:
        symbol_rows = [row for row in real_rows if row["symbol"] == symbol]
        first_date = min(row["trade_date"] for row in symbol_rows)
        last_date = max(row["trade_date"] for row in symbol_rows)
        # Demo rows are useful before the first real sync, but must never remain
        # beside a sufficiently long real history: synthetic points can corrupt
        # returns and create false mixed-source quality alerts.
        conditions = [
            DailyPrice.symbol == symbol,
            DailyPrice.source == "demo",
        ]
        if len(symbol_rows) < 21:
            conditions.extend(
                [
                    DailyPrice.trade_date >= first_date,
                    DailyPrice.trade_date <= last_date,
                ]
            )
        db.execute(delete(DailyPrice).where(*conditions))
    count = 0
    for row in items:
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
    items = list(rows)
    if not items:
        return 0
    symbols = {row.get("symbol") for row in items}
    first_time = min(row["published_at"] for row in items) - timedelta(days=3)
    last_time = max(row["published_at"] for row in items) + timedelta(days=3)
    existing_items = list(
        db.scalars(
            select(NewsItem).where(
                NewsItem.symbol.in_(symbols),
                NewsItem.published_at >= first_time,
                NewsItem.published_at <= last_time,
            )
        ).all()
    )
    existing_hashes = {item.content_hash for item in existing_items}
    candidates: dict[tuple[str | None, str], list[NewsItem]] = {}
    for item in existing_items:
        candidates.setdefault((item.symbol, item.kind), []).append(item)

    count = 0
    for row in items:
        if row["content_hash"] in existing_hashes:
            continue
        bucket = candidates.setdefault((row.get("symbol"), row.get("kind", "news")), [])
        if any(is_duplicate_news(row, existing) for existing in bucket):
            continue
        item = NewsItem(**row)
        db.add(item)
        bucket.append(item)
        existing_hashes.add(row["content_hash"])
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
