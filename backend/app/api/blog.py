from __future__ import annotations

import hmac
import re
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.time import utc_iso
from app.models import BlogComment
from app.services.blog_news import blog_news_cache

router = APIRouter(prefix="/blog", tags=["blog"])
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CommentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    displayName: str = Field(default="", max_length=40)  # noqa: N815
    email: str = Field(min_length=3, max_length=254)
    content: str = Field(min_length=2, max_length=1000)
    website: str = Field(default="", max_length=200)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        normalized = value.casefold()
        if not EMAIL_RE.fullmatch(normalized):
            raise ValueError("请输入有效邮箱地址")
        return normalized


def _public_comment(item: BlogComment) -> dict[str, object]:
    return {
        "id": item.id,
        "displayName": item.display_name,
        "content": item.content,
        "createdAt": utc_iso(item.created_at),
    }


def _admin_comment(item: BlogComment) -> dict[str, object]:
    return {**_public_comment(item), "email": item.email}


def require_admin(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    expected = get_settings().blog_admin_token
    supplied = ""
    if authorization and authorization.startswith("Bearer "):
        supplied = authorization[7:].strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="留言管理尚未配置",
        )
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理令牌无效",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/comments")
def list_comments(
    cursor: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    query = select(BlogComment).order_by(BlogComment.id.desc()).limit(limit + 1)
    if cursor is not None:
        query = query.where(BlogComment.id < cursor)
    rows = list(db.scalars(query).all())
    has_more = len(rows) > limit
    visible = rows[:limit]
    return {
        "items": [_public_comment(item) for item in visible],
        "nextCursor": visible[-1].id if has_more and visible else None,
    }


@router.post("/comments", status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if payload.website:
        raise HTTPException(status_code=400, detail="留言未通过验证")
    item = BlogComment(
        display_name=payload.displayName or "Anonymous",
        email=payload.email,
        content=payload.content,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _public_comment(item)


@router.get("/admin/comments", dependencies=[Depends(require_admin)])
def list_admin_comments(
    cursor: int | None = Query(default=None, ge=1),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    query = select(BlogComment).order_by(BlogComment.id.desc()).limit(limit + 1)
    if cursor is not None:
        query = query.where(BlogComment.id < cursor)
    rows = list(db.scalars(query).all())
    visible = rows[:limit]
    return {
        "items": [_admin_comment(item) for item in visible],
        "nextCursor": visible[-1].id if len(rows) > limit and visible else None,
    }


@router.delete(
    "/admin/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_comment(comment_id: int, db: Session = Depends(get_db)) -> Response:
    item = db.get(BlogComment, comment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="留言不存在")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/news")
async def list_news(
    limit: int = Query(default=12, ge=1, le=30),
) -> dict[str, object]:
    settings = get_settings()
    return await blog_news_cache.get(
        limit=limit,
        ttl_seconds=settings.blog_news_cache_seconds,
        stale_seconds=settings.blog_news_stale_seconds,
        seed_file=settings.blog_news_seed_file,
    )
