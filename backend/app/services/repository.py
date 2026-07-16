from __future__ import annotations

from collections.abc import Iterable
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DailyPrice, FinancialMetric, NewsItem, Stock

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
