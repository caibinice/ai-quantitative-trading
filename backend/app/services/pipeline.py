from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import DEFAULT_STOCK_NAMES
from app.models import JobRun, utcnow
from app.services.provider import AkshareProvider
from app.services.repository import ensure_stock, upsert_financials, upsert_news, upsert_prices


def sync_market_data(
    db: Session,
    symbols: list[str],
    start_date: date,
    end_date: date,
    include_financials: bool = True,
    include_news: bool = True,
    include_notices: bool = True,
    provider: AkshareProvider | None = None,
) -> dict[str, Any]:
    provider = provider or AkshareProvider()
    job = JobRun(job_type="market_sync", status="running", details={"symbols": symbols})
    db.add(job)
    db.commit()
    totals = {
        "prices": 0,
        "financials": 0,
        "news": 0,
        "notices": 0,
        "cninfo_notices": 0,
        "errors": [],
    }
    try:
        try:
            names = {item["symbol"]: item["name"] for item in provider.stock_snapshot()}
        except Exception:
            names = {}
        for symbol in symbols:
            try:
                name = names.get(symbol) or DEFAULT_STOCK_NAMES.get(symbol, symbol)
                ensure_stock(db, symbol, name)
                db.commit()
            except Exception as exc:
                db.rollback()
                totals["errors"].append(
                    {"symbol": symbol, "component": "stock", "error": str(exc)[:300]}
                )
                continue

            operations = [
                (
                    "prices",
                    True,
                    lambda symbol=symbol: provider.daily_prices(symbol, start_date, end_date),
                    upsert_prices,
                ),
                (
                    "financials",
                    include_financials,
                    lambda symbol=symbol: provider.financial_metrics(symbol),
                    upsert_financials,
                ),
                (
                    "news",
                    include_news,
                    lambda symbol=symbol: provider.news(symbol),
                    upsert_news,
                ),
                (
                    "notices",
                    include_notices,
                    lambda symbol=symbol: provider.notices(
                        symbol,
                        max(start_date, end_date - timedelta(days=90)),
                        end_date,
                    ),
                    upsert_news,
                ),
                (
                    "cninfo_notices",
                    include_notices,
                    lambda symbol=symbol: provider.cninfo_notices(
                        symbol,
                        max(start_date, end_date - timedelta(days=90)),
                        end_date,
                    ),
                    upsert_news,
                ),
            ]
            for component, enabled, fetch, save in operations:
                if not enabled:
                    continue
                try:
                    totals[component] += save(db, fetch())
                    db.commit()
                except Exception as exc:
                    db.rollback()
                    totals["errors"].append(
                        {
                            "symbol": symbol,
                            "component": component,
                            "error": str(exc)[:300],
                        }
                    )
        job.status = "success" if not totals["errors"] else "partial"
        job.message = "数据同步完成"
        job.details = totals
        job.finished_at = utcnow()
        db.add(job)
        db.commit()
        return totals
    except Exception as exc:
        db.rollback()
        job.status = "failed"
        job.message = str(exc)[:1000]
        job.finished_at = utcnow()
        db.add(job)
        db.commit()
        raise
