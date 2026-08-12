from __future__ import annotations

import hashlib
from collections import Counter
from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    DailyPrice,
    DataQualityIssue,
    DataQualityRun,
    IndexPrice,
    PointInTimeFinancial,
    SentimentAnalysis,
    TradingCalendar,
    utcnow,
)


def _issue(
    category: str,
    severity: str,
    entity_type: str,
    entity_id: str,
    title: str,
    detail: dict[str, Any],
) -> dict[str, Any]:
    identity = f"{category}|{entity_type}|{entity_id}|{title}"
    return {
        "fingerprint": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
        "category": category,
        "severity": severity,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "title": title,
        "detail": detail,
    }


def detect_price_issues(
    symbol: str,
    rows: list[DailyPrice | IndexPrice],
    open_dates: set[date],
    entity_type: str = "stock",
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not rows:
        return [
            _issue("price_missing", "critical", entity_type, symbol, "没有日线行情", {})
        ]
    invalid_dates = [
        row.trade_date.isoformat()
        for row in rows
        if min(row.open, row.high, row.low, row.close) <= 0
        or row.high < max(row.open, row.close)
        or row.low > min(row.open, row.close)
        or row.high < row.low
    ]
    if invalid_dates:
        issues.append(
            _issue(
                "ohlc_invalid",
                "critical",
                entity_type,
                symbol,
                "OHLC 价格关系异常",
                {"count": len(invalid_dates), "sample_dates": invalid_dates[:10]},
            )
        )

    sorted_rows = sorted(rows, key=lambda item: item.trade_date)
    sources = {getattr(row, "source", "") for row in rows}
    if "demo" in sources and len(sources) > 1:
        demo_dates = [
            row.trade_date.isoformat()
            for row in rows
            if getattr(row, "source", "") == "demo"
        ]
        issues.append(
            _issue(
                "demo_contamination",
                "critical",
                entity_type,
                symbol,
                "真实行情序列混入演示数据",
                {"count": len(demo_dates), "sample_dates": demo_dates[:10]},
            )
        )
    extreme_dates: list[str] = []
    for previous, current in zip(sorted_rows, sorted_rows[1:], strict=False):
        change = current.close / previous.close - 1 if previous.close else 0
        if abs(change) > 0.25:
            extreme_dates.append(current.trade_date.isoformat())
    if extreme_dates:
        issues.append(
            _issue(
                "extreme_return",
                "warning",
                entity_type,
                symbol,
                "存在超过 25% 的单日价格跳变",
                {"count": len(extreme_dates), "sample_dates": extreme_dates[:10]},
            )
        )

    first_date, last_date = sorted_rows[0].trade_date, sorted_rows[-1].trade_date
    expected = {value for value in open_dates if first_date <= value <= last_date}
    actual = {row.trade_date for row in rows}
    missing = sorted(expected - actual)
    if missing:
        issues.append(
            _issue(
                "calendar_gap",
                "warning",
                entity_type,
                symbol,
                "交易日行情存在缺口",
                {
                    "count": len(missing),
                    "sample_dates": [item.isoformat() for item in missing[:10]],
                },
            )
        )
    past_open_dates = sorted(value for value in open_dates if value <= date.today())
    if past_open_dates:
        stale_days = sum(value > last_date for value in past_open_dates)
        if stale_days >= 3:
            issues.append(
                _issue(
                    "price_stale",
                    "critical",
                    entity_type,
                    symbol,
                    "行情数据已过期",
                    {"latest_date": last_date.isoformat(), "missing_open_days": stale_days},
                )
            )
    return issues


def run_data_quality_checks(
    db: Session, symbols: list[str], benchmark_symbol: str = "000300"
) -> DataQualityRun:
    run = DataQualityRun(status="running")
    db.add(run)
    db.commit()
    issues: list[dict[str, Any]] = []
    open_dates = set(
        db.scalars(
            select(TradingCalendar.trade_date).where(TradingCalendar.is_open.is_(True))
        ).all()
    )
    checks_count = 0
    for symbol in symbols:
        rows = list(
            db.scalars(
                select(DailyPrice)
                .where(DailyPrice.symbol == symbol)
                .order_by(DailyPrice.trade_date)
            ).all()
        )
        issues.extend(detect_price_issues(symbol, rows, open_dates))
        pit_count = db.scalar(
            select(func.count())
            .select_from(PointInTimeFinancial)
            .where(PointInTimeFinancial.symbol == symbol)
        )
        if not pit_count:
            issues.append(
                _issue(
                    "pit_financial_missing",
                    "warning",
                    "stock",
                    symbol,
                    "缺少点时财务数据",
                    {},
                )
            )
        checks_count += 2

    benchmark_rows = list(
        db.scalars(
            select(IndexPrice)
            .where(IndexPrice.symbol == benchmark_symbol)
            .order_by(IndexPrice.trade_date)
        ).all()
    )
    issues.extend(
        detect_price_issues(benchmark_symbol, benchmark_rows, open_dates, "index")
    )
    checks_count += 1

    invalid_sentiment = db.scalar(
        select(func.count())
        .select_from(SentimentAnalysis)
        .where(
            (SentimentAnalysis.score < -1)
            | (SentimentAnalysis.score > 1)
            | (SentimentAnalysis.confidence < 0)
            | (SentimentAnalysis.confidence > 1)
        )
    )
    if invalid_sentiment:
        issues.append(
            _issue(
                "sentiment_range",
                "critical",
                "dataset",
                "sentiment",
                "情绪分数超出允许范围",
                {"count": invalid_sentiment},
            )
        )
    checks_count += 1

    now = utcnow()
    active_fingerprints = {item["fingerprint"] for item in issues}
    for item in issues:
        existing = db.scalar(
            select(DataQualityIssue).where(
                DataQualityIssue.fingerprint == item["fingerprint"]
            )
        )
        if existing:
            existing.last_seen_at = now
            existing.resolved_at = None
            existing.detail = item["detail"]
            existing.severity = item["severity"]
        else:
            db.add(DataQualityIssue(**item))
    unresolved = db.scalars(
        select(DataQualityIssue).where(DataQualityIssue.resolved_at.is_(None))
    ).all()
    for existing in unresolved:
        if existing.fingerprint not in active_fingerprints:
            existing.resolved_at = now

    severity_counts = Counter(item["severity"] for item in issues)
    run.status = "success"
    run.checks_count = checks_count
    run.issues_count = len(issues)
    run.details = {
        "symbols": symbols,
        "benchmark_symbol": benchmark_symbol,
        "severity_counts": dict(severity_counts),
        "calendar_rows": len(open_dates),
    }
    run.finished_at = now
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
