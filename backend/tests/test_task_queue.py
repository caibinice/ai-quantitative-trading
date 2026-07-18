from __future__ import annotations

from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.services.task_queue import cancel_task, claim_next_task, enqueue_task, retry_task
from app.worker import run_worker


def test_database_queue_transitions() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        first = enqueue_task(db, "data_quality", priority=20)
        second = enqueue_task(db, "factor_scoring", priority=10)

        claimed = claim_next_task(db, "test-worker")
        assert claimed is not None
        assert claimed.id == second.id
        assert claimed.status == "running"
        assert claimed.attempts == 1

        cancelled = cancel_task(db, first.id)
        assert cancelled.status == "cancelled"
        retried = retry_task(db, first.id)
        assert retried.status == "queued"


def test_worker_can_exit_after_idle_window(monkeypatch) -> None:
    times = iter([10.0, 10.0, 11.0])
    tasks = iter([SimpleNamespace(id=1), None])
    monkeypatch.setattr("app.worker.create_tables", lambda: None)
    monkeypatch.setattr("app.worker.SessionLocal", lambda: Session(create_engine("sqlite://")))
    monkeypatch.setattr("app.worker.claim_next_task", lambda _db, _worker_id: next(tasks))
    monkeypatch.setattr("app.worker.execute_task", lambda _db, _task_id: None)
    monkeypatch.setattr("app.worker.time.monotonic", lambda: next(times))
    monkeypatch.setattr("app.worker.time.sleep", lambda _seconds: None)

    run_worker(poll_seconds=0.01, idle_exit_seconds=1.0)
