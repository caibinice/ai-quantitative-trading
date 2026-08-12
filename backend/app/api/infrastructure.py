from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.time import utc_iso
from app.models import (
    DataQualityIssue,
    DataQualityRun,
    IndexPrice,
    PointInTimeFinancial,
    TradingCalendar,
    utcnow,
)
from app.schemas import DataQualityRequest, InfrastructureSyncRequest
from app.services.task_queue import enqueue_task

router = APIRouter(tags=["research-infrastructure"])


@router.get("/infrastructure/summary")
def infrastructure_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    calendar_count, first_date, last_date = db.execute(
        select(
            func.count(TradingCalendar.trade_date),
            func.min(TradingCalendar.trade_date),
            func.max(TradingCalendar.trade_date),
        ).where(TradingCalendar.is_open.is_(True))
    ).one()
    benchmark_rows = db.execute(
        select(
            IndexPrice.symbol,
            func.max(IndexPrice.name),
            func.count(IndexPrice.id),
            func.max(IndexPrice.trade_date),
        ).group_by(IndexPrice.symbol)
    ).all()
    pit_count, pit_latest = db.execute(
        select(
            func.count(PointInTimeFinancial.id),
            func.max(PointInTimeFinancial.available_at),
        )
    ).one()
    return {
        "calendar": {
            "count": calendar_count,
            "first_date": first_date,
            "last_date": last_date,
        },
        "benchmarks": [
            {"symbol": row[0], "name": row[1], "count": row[2], "latest_date": row[3]}
            for row in benchmark_rows
        ],
        "pit_financials": {"count": pit_count, "latest_available_at": pit_latest},
    }


@router.get("/calendar")
def calendar(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=400, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = select(TradingCalendar).where(TradingCalendar.is_open.is_(True))
    if start_date:
        query = query.where(TradingCalendar.trade_date >= start_date)
    if end_date:
        query = query.where(TradingCalendar.trade_date <= end_date)
    rows = db.scalars(query.order_by(TradingCalendar.trade_date.desc()).limit(limit)).all()
    return [
        {"trade_date": item.trade_date, "is_open": item.is_open, "source": item.source}
        for item in rows
    ]


@router.get("/benchmarks/{symbol}/prices")
def benchmark_prices(
    symbol: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = select(IndexPrice).where(IndexPrice.symbol == symbol)
    if start_date:
        query = query.where(IndexPrice.trade_date >= start_date)
    if end_date:
        query = query.where(IndexPrice.trade_date <= end_date)
    rows = db.scalars(query.order_by(IndexPrice.trade_date)).all()
    return [
        {
            "symbol": item.symbol,
            "name": item.name,
            "date": item.trade_date,
            "open": item.open,
            "high": item.high,
            "low": item.low,
            "close": item.close,
            "volume": item.volume,
            "source": item.source,
        }
        for item in rows
    ]


@router.get("/financials/pit/{symbol}")
def pit_financials(
    symbol: str,
    as_of: date | None = None,
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    as_of = as_of or date.today()
    rows = db.scalars(
        select(PointInTimeFinancial)
        .where(
            PointInTimeFinancial.symbol == symbol,
            PointInTimeFinancial.available_at <= as_of,
        )
        .order_by(
            PointInTimeFinancial.available_at.desc(),
            PointInTimeFinancial.report_date.desc(),
        )
        .limit(limit)
    ).all()
    return [
        {
            "report_date": item.report_date,
            "available_at": item.available_at,
            "metric_name": item.metric_name,
            "metric_value": item.metric_value,
            "source": item.source,
            "is_estimated": item.is_estimated,
        }
        for item in rows
    ]


@router.post("/infrastructure/sync")
def enqueue_infrastructure_sync(
    payload: InfrastructureSyncRequest, db: Session = Depends(get_db)
) -> dict[str, Any]:
    task = enqueue_task(db, "infrastructure_sync", payload.model_dump(mode="json"), priority=90)
    return {"task_id": task.id, "status": task.status}


@router.get("/data-quality/summary")
def data_quality_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    latest_run = db.scalar(select(DataQualityRun).order_by(DataQualityRun.id.desc()).limit(1))
    severity_rows = db.execute(
        select(DataQualityIssue.severity, func.count(DataQualityIssue.id))
        .where(DataQualityIssue.resolved_at.is_(None))
        .group_by(DataQualityIssue.severity)
    ).all()
    return {
        "active_by_severity": dict(severity_rows),
        "latest_run": (
            {
                "id": latest_run.id,
                "status": latest_run.status,
                "checks_count": latest_run.checks_count,
                "issues_count": latest_run.issues_count,
                "details": latest_run.details,
                "started_at": utc_iso(latest_run.started_at),
                "finished_at": utc_iso(latest_run.finished_at),
            }
            if latest_run
            else None
        ),
    }


@router.get("/data-quality/issues")
def data_quality_issues(
    active_only: bool = True,
    severity: str = "",
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = select(DataQualityIssue).order_by(
        DataQualityIssue.resolved_at.is_(None).desc(), DataQualityIssue.last_seen_at.desc()
    )
    if active_only:
        query = query.where(DataQualityIssue.resolved_at.is_(None))
    if severity:
        query = query.where(DataQualityIssue.severity == severity)
    rows = db.scalars(query.limit(limit)).all()
    return [
        {
            "id": item.id,
            "category": item.category,
            "severity": item.severity,
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "title": item.title,
            "detail": item.detail,
            "first_seen_at": utc_iso(item.first_seen_at),
            "last_seen_at": utc_iso(item.last_seen_at),
            "resolved_at": utc_iso(item.resolved_at),
        }
        for item in rows
    ]


@router.post("/data-quality/run")
def enqueue_data_quality(
    payload: DataQualityRequest, db: Session = Depends(get_db)
) -> dict[str, Any]:
    task = enqueue_task(db, "data_quality", payload.model_dump(mode="json"), priority=80)
    return {"task_id": task.id, "status": task.status}


@router.post("/data-quality/issues/{issue_id}/resolve")
def resolve_quality_issue(issue_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    issue = db.get(DataQualityIssue, issue_id)
    if issue is None:
        return {"resolved": False}
    issue.resolved_at = utcnow()
    db.add(issue)
    db.commit()
    return {"resolved": True}
