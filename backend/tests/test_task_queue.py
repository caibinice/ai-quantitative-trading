from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.services.task_queue import cancel_task, claim_next_task, enqueue_task, retry_task


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
