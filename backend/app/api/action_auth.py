from __future__ import annotations

import base64
import hashlib
import hmac
import time

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(prefix="/action-auth", tags=["action-auth"])


class ActionAuthRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)


def _signature(expires_at: str, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        expires_at.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def issue_action_token() -> tuple[str, int]:
    settings = get_settings()
    if not settings.action_token_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="敏感操作验证尚未配置",
        )
    ttl_seconds = max(60, settings.action_token_ttl_minutes * 60)
    expires_at = str(int(time.time()) + ttl_seconds)
    return f"{expires_at}.{_signature(expires_at, settings.action_token_secret)}", ttl_seconds


def valid_action_token(authorization: str | None) -> bool:
    settings = get_settings()
    if not settings.action_token_secret or not authorization:
        return False
    if not authorization.startswith("Bearer "):
        return False
    token = authorization[7:].strip()
    try:
        expires_at, supplied_signature = token.split(".", 1)
        if int(expires_at) <= int(time.time()):
            return False
    except (TypeError, ValueError):
        return False
    expected = _signature(expires_at, settings.action_token_secret)
    return hmac.compare_digest(supplied_signature, expected)


@router.post("/verify")
def verify_action_password(payload: ActionAuthRequest) -> dict[str, object]:
    settings = get_settings()
    if not settings.action_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="敏感操作验证尚未配置",
        )
    if not hmac.compare_digest(payload.password, settings.action_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="操作密码错误",
        )
    token, ttl_seconds = issue_action_token()
    return {
        "token": token,
        "expiresIn": ttl_seconds,
        "tokenType": "Bearer",
    }
