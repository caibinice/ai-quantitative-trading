from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import DailyPrice, Stock
from app.services.repository import upsert_prices


def _row(day: date, close: float, source: str) -> dict:
    return {
        "symbol": "600519",
        "trade_date": day,
        "open": close,
        "high": close,
        "low": close,
        "close": close,
        "volume": 1,
        "amount": 1,
        "adjustment": "qfq",
        "source": source,
    }


def test_real_sync_purges_demo_rows_inside_provider_range() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Stock(symbol="600519", name="贵州茅台"))
        db.add(DailyPrice(**_row(date(2026, 6, 19), 35.76, "demo")))
        db.commit()

        upsert_prices(
            db,
            [
                _row(date(2026, 6, 18), 1186.98, "akshare"),
                _row(date(2026, 6, 22), 1213.39, "akshare"),
            ],
        )
        db.commit()

        rows = list(
            db.scalars(
                select(DailyPrice)
                .where(DailyPrice.symbol == "600519")
                .order_by(DailyPrice.trade_date)
            )
        )
        assert [(row.trade_date, row.source) for row in rows] == [
            (date(2026, 6, 18), "akshare"),
            (date(2026, 6, 22), "akshare"),
        ]
