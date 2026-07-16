from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import StrategyConfig, WalkForwardRun
from app.schemas import WalkForwardRequest
from app.services.task_queue import enqueue_task

router = APIRouter(prefix="/walk-forward", tags=["walk-forward"])


def _run_payload(item: WalkForwardRun, include_curve: bool = True) -> dict[str, Any]:
    payload = {
        "id": item.id,
        "name": item.name,
        "start_date": item.start_date,
        "end_date": item.end_date,
        "benchmark_symbol": item.benchmark_symbol,
        "parameters": item.parameters,
        "windows": item.windows,
        "metrics": item.metrics,
        "created_at": item.created_at,
    }
    if include_curve:
        payload["equity_curve"] = item.equity_curve
    return payload


@router.post("")
def enqueue_walk_forward(
    payload: WalkForwardRequest, db: Session = Depends(get_db)
) -> dict[str, Any]:
    if not payload.symbols:
        strategy = db.scalar(
            select(StrategyConfig)
            .where(StrategyConfig.enabled.is_(True))
            .order_by(StrategyConfig.id)
        )
        if strategy:
            payload.symbols = strategy.watchlist
    task = enqueue_task(db, "walk_forward", payload.model_dump(mode="json"), priority=70)
    return {"task_id": task.id, "status": task.status}


@router.get("")
def list_walk_forward_runs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(WalkForwardRun).order_by(WalkForwardRun.created_at.desc()).limit(20)
    ).all()
    return [_run_payload(item, include_curve=False) for item in rows]


@router.get("/{run_id}")
def get_walk_forward_run(
    run_id: int, db: Session = Depends(get_db)
) -> dict[str, Any]:
    item = db.get(WalkForwardRun, run_id)
    if item is None:
        raise HTTPException(status_code=404, detail="样本外实验不存在")
    return _run_payload(item)
