from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import LearningProgress
from app.schemas import LearningProgressPayload

DEFAULT_PROFILE_ID = "default"


def get_learning_progress(
    db: Session, profile_id: str = DEFAULT_PROFILE_ID
) -> LearningProgress | None:
    return db.get(LearningProgress, profile_id)


def save_learning_progress(
    db: Session,
    payload: LearningProgressPayload,
    profile_id: str = DEFAULT_PROFILE_ID,
) -> LearningProgress:
    progress = db.get(LearningProgress, profile_id)
    if progress is None:
        progress = LearningProgress(profile_id=profile_id)
    progress.completed = payload.completed
    progress.quiz_scores = payload.quiz_scores
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def reset_learning_progress(
    db: Session, profile_id: str = DEFAULT_PROFILE_ID
) -> LearningProgress:
    return save_learning_progress(db, LearningProgressPayload(), profile_id)
