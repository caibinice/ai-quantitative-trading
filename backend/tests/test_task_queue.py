from __future__ import annotations

from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.services.task_queue import (
    cancel_task,
    claim_next_task,
    enqueue_task,
    execute_task,
    retry_task,
)
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


def test_sentiment_pipeline_does_not_enqueue_twice_while_active() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        first = enqueue_task(db, "sentiment_pipeline")
        second = enqueue_task(db, "sentiment_pipeline", {"analysis_limit": 10})

        assert second.id == first.id
        assert second.payload == {}


def test_sentiment_pipeline_runs_in_strict_order_without_price_sync(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    calls: list[tuple[str, object]] = []

    def fake_sync(*_args, **kwargs):
        calls.append(("sync", kwargs))
        return {"news": 3, "notices": 1, "deduplicated": 2, "errors": []}

    class FakeAnalyzer:
        def analyze_pending(self, _db, limit, force):
            calls.append(("analyze", (limit, force)))
            return 2

    def fake_scores(_db, symbols, as_of, _parameters):
        calls.append(("score", (symbols, as_of)))
        return [SimpleNamespace(), SimpleNamespace()]

    monkeypatch.setattr("app.services.pipeline.sync_market_data", fake_sync)
    monkeypatch.setattr("app.services.sentiment.SentimentAnalyzer", FakeAnalyzer)
    monkeypatch.setattr("app.services.scoring.calculate_scores", fake_scores)

    with Session(engine, expire_on_commit=False) as db:
        task = enqueue_task(
            db,
            "sentiment_pipeline",
            {"symbols": ["000333"], "analysis_limit": 25},
        )
        task.status = "running"
        task.attempts = 1
        db.commit()

        finished = execute_task(db, task.id)

        assert finished.status == "success"
        assert [name for name, _ in calls] == ["sync", "analyze", "score"]
        sync_options = calls[0][1]
        assert isinstance(sync_options, dict)
        assert sync_options["include_prices"] is False
        assert sync_options["include_financials"] is False
        assert finished.result["analyzed"] == 2
        assert finished.result["scored"] == 2
