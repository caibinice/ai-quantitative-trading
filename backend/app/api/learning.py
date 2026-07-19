from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import ROOT_DIR
from app.core.database import get_db
from app.schemas import LearningProgressPayload, LearningProgressResponse
from app.services.learning import (
    get_learning_progress,
    reset_learning_progress,
    save_learning_progress,
)

router = APIRouter(prefix="/learning", tags=["learning"])
DOWNLOAD_FILES = {"README.md", ".env.example"}
DOWNLOAD_PREFIXES = (
    "backend/app",
    "backend/tests",
    "backend/scripts",
    "frontend/src",
    "learning",
    "scripts",
    "deploy",
)


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


def _resolve_download_path(file_path: str) -> Path:
    relative = Path(file_path.replace("\\", "/"))
    normalized = relative.as_posix()
    allowed = normalized in DOWNLOAD_FILES or any(
        normalized == prefix or normalized.startswith(f"{prefix}/")
        for prefix in DOWNLOAD_PREFIXES
    )
    if (
        relative.is_absolute()
        or not relative.parts
        or not allowed
        or (
            normalized not in DOWNLOAD_FILES
            and any(part.startswith(".") for part in relative.parts)
        )
    ):
        raise HTTPException(status_code=404, detail="学习文件不存在")
    target = (ROOT_DIR / relative).resolve()
    if not target.is_relative_to(ROOT_DIR.resolve()) or not target.is_file():
        raise HTTPException(status_code=404, detail="学习文件不存在")
    if target.stat().st_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="学习文件超过下载大小限制")
    return target


@router.get("/files/{file_path:path}", response_class=FileResponse)
def download_learning_file(file_path: str) -> FileResponse:
    target = _resolve_download_path(file_path)
    return FileResponse(
        path=target,
        filename=target.name,
        media_type="application/octet-stream",
    )
