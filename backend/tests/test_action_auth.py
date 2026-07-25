from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import action_auth
from app.main import app
from app.middleware.action_auth import is_sensitive_request


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        action_password="test-password",
        action_token_secret="test-secret-that-is-long-enough-for-tests",
        action_token_ttl_minutes=30,
    )


def test_sensitive_request_policy() -> None:
    assert is_sensitive_request("POST", "/api/pipeline/analyze")
    assert is_sensitive_request("PUT", "/api/automation/settings")
    assert not is_sensitive_request("GET", "/api/strategy")
    assert not is_sensitive_request("PUT", "/api/learning/progress")
    assert not is_sensitive_request("POST", "/api/blog/comments")
    assert not is_sensitive_request("POST", "/api/action-auth/verify")


def test_password_issues_token_and_middleware_rejects_missing_token(monkeypatch) -> None:
    monkeypatch.setattr(action_auth, "get_settings", _settings)
    client = TestClient(app)

    rejected = client.post("/api/action-auth/verify", json={"password": "wrong"})
    assert rejected.status_code == 401

    verified = client.post(
        "/api/action-auth/verify",
        json={"password": "test-password"},
    )
    assert verified.status_code == 200
    token = verified.json()["token"]
    assert action_auth.valid_action_token(f"Bearer {token}")

    blocked = client.post("/api/tasks", json={"task_type": "market_sync", "payload": {}})
    assert blocked.status_code == 401
    assert blocked.json()["detail"] == "此操作需要先验证操作密码"
