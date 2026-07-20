from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.time import utc_iso
from app.models import ResearchTask
from app.schemas import TaskCreateRequest
from app.services.task_queue import cancel_task, enqueue_task, retry_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


def task_payload(task: ResearchTask) -> dict[str, Any]:
    return {
        "id": task.id,
        "task_type": task.task_type,
        "status": task.status,
        "priority": task.priority,
        "payload": task.payload,
        "result": task.result,
        "error": task.error,
        "progress": task.progress,
        "attempts": task.attempts,
        "max_attempts": task.max_attempts,
        "worker_id": task.worker_id,
        "created_at": utc_iso(task.created_at),
        "started_at": utc_iso(task.started_at),
        "finished_at": utc_iso(task.finished_at),
    }


@router.get("")
def list_tasks(
    status: str = "",
    task_type: str = "",
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = select(ResearchTask).order_by(ResearchTask.created_at.desc())
    if status:
        query = query.where(ResearchTask.status == status)
    if task_type:
        query = query.where(ResearchTask.task_type == task_type)
    return [task_payload(item) for item in db.scalars(query.limit(limit)).all()]


@router.post("")
def create_task(
    payload: TaskCreateRequest, db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        task = enqueue_task(
            db,
            payload.task_type,
            payload.payload,
            payload.priority,
            payload.max_attempts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return task_payload(task)


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    task = db.get(ResearchTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task_payload(task)


@router.post("/{task_id}/retry")
def retry(task_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return task_payload(retry_task(db, task_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{task_id}/cancel")
def cancel(task_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return task_payload(cancel_task(db, task_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
