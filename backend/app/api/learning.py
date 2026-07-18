from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import LearningProgressPayload, LearningProgressResponse
from app.services.learning import (
    get_learning_progress,
    reset_learning_progress,
    save_learning_progress,
)

router = APIRouter(prefix="/learning", tags=["learning"])


def _response(progress) -> LearningProgressResponse:
    if progress is None:
        return LearningProgressResponse()
    return LearningProgressResponse(
        completed=progress.completed or [],
        quiz_scores=progress.quiz_scores or {},
        updated_at=progress.updated_at,
    )


@router.get("/progress", response_model=LearningProgressResponse)
def read_progress(db: Session = Depends(get_db)) -> LearningProgressResponse:
    return _response(get_learning_progress(db))


@router.put("/progress", response_model=LearningProgressResponse)
def update_progress(
    payload: LearningProgressPayload, db: Session = Depends(get_db)
) -> LearningProgressResponse:
    return _response(save_learning_progress(db, payload))


@router.delete("/progress", response_model=LearningProgressResponse)
def clear_progress(db: Session = Depends(get_db)) -> LearningProgressResponse:
    return _response(reset_learning_progress(db))
