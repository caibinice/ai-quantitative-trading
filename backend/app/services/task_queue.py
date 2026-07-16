from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import ResearchTask, StrategyConfig, utcnow
from app.schemas import (
    AnalyzeRequest,
    BacktestRequest,
    DataQualityRequest,
    InfrastructureSyncRequest,
    ScoreRequest,
    StrategyParameters,
    SyncRequest,
    WalkForwardRequest,
)
from app.services.backtest import run_backtest_from_db
from app.services.data_quality import run_data_quality_checks
from app.services.infrastructure import quarter_ends, sync_research_infrastructure
from app.services.pipeline import sync_market_data
from app.services.scoring import calculate_scores
from app.services.sentiment import SentimentAnalyzer
from app.services.walkforward import run_walk_forward_from_db

SUPPORTED_TASKS = {
    "market_sync",
    "infrastructure_sync",
    "sentiment_analysis",
    "factor_scoring",
    "backtest",
    "walk_forward",
    "data_quality",
}


def enqueue_task(
    db: Session,
    task_type: str,
    payload: dict[str, Any] | None = None,
    priority: int = 100,
    max_attempts: int = 2,
) -> ResearchTask:
    if task_type not in SUPPORTED_TASKS:
        raise ValueError(f"不支持的任务类型：{task_type}")
    task = ResearchTask(
        task_type=task_type,
        status="queued",
        payload=payload or {},
        priority=priority,
        max_attempts=max_attempts,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def claim_next_task(db: Session, worker_id: str) -> ResearchTask | None:
    task = db.scalar(
        select(ResearchTask)
        .where(ResearchTask.status == "queued")
        .order_by(ResearchTask.priority, ResearchTask.created_at)
        # The configured remote server is MariaDB-compatible but does not support
        # SKIP LOCKED. A plain row lock keeps claiming correct; extra workers wait.
        .with_for_update()
        .limit(1)
    )
    if task is None:
        db.rollback()
        return None
    task.status = "running"
    task.worker_id = worker_id
    task.started_at = utcnow()
    task.finished_at = None
    task.attempts += 1
    task.progress = 0.01
    task.error = ""
    db.commit()
    db.refresh(task)
    return task


def _active_strategy(db: Session) -> tuple[list[str], StrategyParameters]:
    config = db.scalar(
        select(StrategyConfig).where(StrategyConfig.enabled.is_(True)).order_by(StrategyConfig.id)
    )
    if config:
        return config.watchlist, StrategyParameters(**config.parameters)
    settings = get_settings()
    return settings.watchlist, StrategyParameters()


def _set_progress(db: Session, task_id: int, value: float, message: str) -> None:
    task = db.get(ResearchTask, task_id)
    if task is None:
        return
    task.progress = max(0.0, min(1.0, value))
    task.result = {**(task.result or {}), "message": message}
    db.add(task)
    db.commit()


def execute_task(db: Session, task_id: int) -> ResearchTask:
    task = db.get(ResearchTask, task_id)
    if task is None:
        raise ValueError("任务不存在")
    try:
        result = _dispatch_task(db, task)
        task = db.get(ResearchTask, task_id)
        task.status = "success"
        task.progress = 1.0
        task.result = result
        task.finished_at = utcnow()
        db.add(task)
        db.commit()
        return task
    except Exception as exc:
        db.rollback()
        task = db.get(ResearchTask, task_id)
        if task is None:
            raise
        task.error = str(exc)[:2000]
        task.finished_at = utcnow()
        task.progress = 0
        if task.attempts < task.max_attempts:
            task.status = "queued"
            task.worker_id = None
        else:
            task.status = "failed"
        db.add(task)
        db.commit()
        return task


def _dispatch_task(db: Session, task: ResearchTask) -> dict[str, Any]:
    watchlist, parameters = _active_strategy(db)
    payload = task.payload or {}
    if task.task_type == "market_sync":
        request = SyncRequest(**payload)
        symbols = request.symbols or watchlist
        end_date = request.end_date or date.today()
        start_date = request.start_date or end_date - timedelta(days=400)
        _set_progress(db, task.id, 0.1, "正在同步行情与舆情")
        return sync_market_data(
            db,
            symbols,
            start_date,
            end_date,
            request.include_financials,
            request.include_news,
            request.include_notices,
        )
    if task.task_type == "infrastructure_sync":
        request = InfrastructureSyncRequest(**payload)
        symbols = request.symbols or watchlist
        end_date = request.end_date or date.today()
        start_date = request.start_date or end_date - timedelta(days=730)
        report_dates = request.report_dates or quarter_ends(start_date, end_date)
        return sync_research_infrastructure(
            db,
            symbols,
            request.benchmark_symbol,
            start_date,
            end_date,
            report_dates,
            progress=lambda value, message: _set_progress(db, task.id, value, message),
        )
    if task.task_type == "sentiment_analysis":
        request = AnalyzeRequest(**payload)
        _set_progress(db, task.id, 0.1, "正在分析待处理事件")
        count = SentimentAnalyzer().analyze_pending(db, request.limit, request.force)
        return {"analyzed": count}
    if task.task_type == "factor_scoring":
        request = ScoreRequest(**payload)
        symbols = request.symbols or watchlist
        as_of = request.as_of or date.today()
        _set_progress(db, task.id, 0.2, "正在计算点时因子")
        items = calculate_scores(db, symbols, as_of, parameters)
        return {"score_date": as_of.isoformat(), "count": len(items)}
    if task.task_type == "backtest":
        request = BacktestRequest(**payload)
        if not request.symbols:
            request.symbols = watchlist
        _set_progress(db, task.id, 0.2, "正在运行历史回测")
        run = run_backtest_from_db(db, request)
        return {"run_id": run.id, "metrics": run.metrics}
    if task.task_type == "walk_forward":
        request = WalkForwardRequest(**payload)
        if not request.symbols:
            request.symbols = watchlist
        _set_progress(db, task.id, 0.1, "正在执行滚动训练与样本外评估")
        run = run_walk_forward_from_db(db, request)
        return {"run_id": run.id, "metrics": run.metrics, "windows": len(run.windows)}
    if task.task_type == "data_quality":
        request = DataQualityRequest(**payload)
        symbols = request.symbols or watchlist
        _set_progress(db, task.id, 0.2, "正在执行数据质量规则")
        run = run_data_quality_checks(db, symbols, request.benchmark_symbol)
        return {
            "run_id": run.id,
            "checks_count": run.checks_count,
            "issues_count": run.issues_count,
        }
    raise ValueError(f"未实现的任务类型：{task.task_type}")


def retry_task(db: Session, task_id: int) -> ResearchTask:
    task = db.get(ResearchTask, task_id)
    if task is None:
        raise ValueError("任务不存在")
    if task.status not in {"failed", "cancelled"}:
        raise ValueError("只有失败或取消的任务可以重试")
    task.status = "queued"
    task.error = ""
    task.progress = 0
    task.finished_at = None
    task.worker_id = None
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def cancel_task(db: Session, task_id: int) -> ResearchTask:
    task = db.get(ResearchTask, task_id)
    if task is None:
        raise ValueError("任务不存在")
    if task.status != "queued":
        raise ValueError("只有排队中的任务可以取消")
    task.status = "cancelled"
    task.finished_at = utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
