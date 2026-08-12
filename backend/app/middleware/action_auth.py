from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.action_auth import valid_action_token

EXEMPT_MUTATION_PREFIXES = (
    "/api/action-auth/",
    "/api/blog/",
    "/api/learning/",
)


def is_sensitive_request(method: str, path: str) -> bool:
    if method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False
    normalized = path if path.startswith("/") else f"/{path}"
    return not any(normalized.startswith(prefix) for prefix in EXEMPT_MUTATION_PREFIXES)


class ActionAuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and is_sensitive_request(
            scope.get("method", "GET"),
            scope.get("path", ""),
        ):
            headers = {
                key.decode("latin-1").lower(): value.decode("latin-1")
                for key, value in scope.get("headers", [])
            }
            if not valid_action_token(headers.get("authorization")):
                response = JSONResponse(
                    {"detail": "此操作需要先验证操作密码"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
