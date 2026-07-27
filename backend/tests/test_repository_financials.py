from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import FinancialMetric, Stock
from app.services.repository import upsert_financials


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_tushare_financials_remove_overlapping_demo_and_fallback_rows() -> None:
    db = _session()
    db.add(Stock(symbol="600519", name="贵州茅台"))
    db.add_all(
        [
            FinancialMetric(
                symbol="600519",
                report_date=date(2026, 6, 16),
                report_period="demo",
                metric_name="演示指标",
                metric_value=1,
                source="demo",
            ),
            FinancialMetric(
                symbol="600519",
                report_date=date(2025, 12, 31),
                report_period="年报",
                metric_name="净资产收益率",
                metric_value=1,
                source="akshare",
            ),
            FinancialMetric(
                symbol="600519",
                report_date=date(2018, 12, 31),
                report_period="年报",
                metric_name="历史指标",
                metric_value=1,
                source="akshare",
            ),
        ]
    )
    db.commit()

    upsert_financials(
        db,
        [
            {
                "symbol": "600519",
                "report_date": date(2025, 12, 31),
                "report_period": "年报",
                "metric_name": "净资产收益率",
                "metric_value": 31.0,
                "yoy": None,
                "source": "tushare-pro",
            },
            {
                "symbol": "600519",
                "report_date": date(2020, 3, 31),
                "report_period": "一季报",
                "metric_name": "净资产收益率",
                "metric_value": 8.0,
                "yoy": None,
                "source": "tushare-pro",
            },
        ],
    )
    db.commit()

    rows = list(
        db.scalars(
            select(FinancialMetric).order_by(FinancialMetric.report_date.desc())
        ).all()
    )

    assert not any(row.source == "demo" for row in rows)
    assert not any(
        row.source == "akshare" and row.report_date >= date(2020, 3, 31)
        for row in rows
    )
    assert any(
        row.source == "akshare" and row.report_date == date(2018, 12, 31)
        for row in rows
    )
    assert any(
        row.source == "tushare-pro" and row.metric_value == 31.0 for row in rows
    )


def test_fallback_financials_do_not_overwrite_existing_tushare_rows() -> None:
    db = _session()
    db.add(Stock(symbol="000001", name="平安银行"))
    db.add(
        FinancialMetric(
            symbol="000001",
            report_date=date(2025, 12, 31),
            report_period="年报",
            metric_name="净资产收益率",
            metric_value=10,
            source="tushare-pro",
        )
    )
    db.commit()

    count = upsert_financials(
        db,
        [
            {
                "symbol": "000001",
                "report_date": date(2025, 12, 31),
                "report_period": "年报",
                "metric_name": "净资产收益率",
                "metric_value": 99,
                "yoy": None,
                "source": "akshare",
            }
        ],
    )
    db.commit()
    row = db.scalar(select(FinancialMetric))

    assert count == 0
    assert row is not None
    assert row.metric_value == 10
    assert row.source == "tushare-pro"
