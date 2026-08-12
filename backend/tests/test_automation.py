from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.schemas import AutomationSettingsPayload
from app.services.automation import get_automation_settings, save_automation_settings
from app.services.scheduler import scheduled_news_analysis


def test_automation_settings_default_to_six_hours_and_persist() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as db:
        defaults = get_automation_settings(db)
        assert defaults.news_analysis_enabled is True
        assert defaults.news_analysis_interval_hours == 6

        updated = save_automation_settings(
            db,
            AutomationSettingsPayload(
                news_analysis_enabled=True,
                news_analysis_interval_hours=12,
            ),
        )
        assert updated.news_analysis_interval_hours == 12

    with Session(engine, expire_on_commit=False) as db:
        persisted = get_automation_settings(db)
        assert persisted.news_analysis_interval_hours == 12


def test_scheduled_news_analysis_enqueues_one_composite_task(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    calls: list[tuple[str, dict]] = []

    monkeypatch.setattr("app.services.scheduler.SessionLocal", lambda: Session(engine))
    monkeypatch.setattr(
        "app.services.scheduler.enqueue_task",
        lambda _db, task_type, payload: calls.append((task_type, payload)),
    )

    scheduled_news_analysis()

    assert calls == [("sentiment_pipeline", {"analysis_limit": 200})]
