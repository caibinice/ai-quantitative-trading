from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.schemas import LearningProgressPayload
from app.services.learning import (
    get_learning_progress,
    reset_learning_progress,
    save_learning_progress,
)


def test_learning_progress_can_be_saved_and_reset() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as db:
        assert get_learning_progress(db) is None

        saved = save_learning_progress(
            db,
            LearningProgressPayload(
                completed=["foundation:0", "foundation:1"],
                quiz_scores={"foundation": 3},
            ),
        )
        assert saved.completed == ["foundation:0", "foundation:1"]
        assert saved.quiz_scores == {"foundation": 3}
        assert saved.updated_at is not None

        reset = reset_learning_progress(db)
        assert reset.completed == []
        assert reset.quiz_scores == {}


def test_learning_progress_payload_deduplicates_checklist_keys() -> None:
    payload = LearningProgressPayload(
        completed=["python:0", "python:0", " python:1 "],
        quiz_scores={"python": 2},
    )
    assert payload.completed == ["python:0", "python:1"]
