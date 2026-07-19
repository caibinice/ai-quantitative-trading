from __future__ import annotations

import httpx

from app.core.config import Settings
from app.services.sentiment import SentimentAnalyzer, _extract_json


def test_extract_json_from_markdown_fence() -> None:
    result = _extract_json('```json\n{"label":"利好","score":0.7}\n```')
    assert result["label"] == "利好"
    assert result["score"] == 0.7


def test_heuristic_fallback_is_deterministic() -> None:
    analyzer = SentimentAnalyzer(
        Settings(database_url="sqlite://", llm_enabled=False, credentials_file="missing.ini")
    )
    result = analyzer.analyze("公司中标并计划回购", "业务增长，盈利上调")

    assert result.label == "利好"
    assert result.score > 0
    assert result.model == "heuristic-v1"


def test_deepseek_thinking_request_uses_backup_key_after_quota_error(monkeypatch) -> None:
    calls: list[dict] = []
    responses = [
        httpx.Response(
            429,
            json={"error": {"message": "quota exhausted"}},
            request=httpx.Request("POST", "https://api.deepseek.com/chat/completions"),
        ),
        httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"label":"利好","score":0.6,"confidence":0.8,'
                                '"summary":"订单增长","rationale":"公告披露新增订单"}'
                            )
                        }
                    }
                ]
            },
            request=httpx.Request("POST", "https://api.deepseek.com/chat/completions"),
        ),
    ]

    def fake_post(url, *, headers, json, timeout):
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return responses.pop(0)

    monkeypatch.setattr(httpx, "post", fake_post)
    analyzer = SentimentAnalyzer(
        Settings(
            database_url="sqlite://",
            credentials_file="missing.ini",
            llm_enabled=True,
            llm_base_url="https://api.deepseek.com",
            llm_api_key="primary-key",
            llm_api_key_backup="backup-key",
            llm_model="deepseek-v4-pro",
            llm_thinking_enabled=True,
            llm_reasoning_effort="high",
        )
    )

    result = analyzer.analyze("公司中标", "公告披露新增订单")

    assert result.label == "利好"
    assert result.model == "deepseek-v4-pro"
    assert len(calls) == 2
    assert calls[0]["headers"]["Authorization"] == "Bearer primary-key"
    assert calls[1]["headers"]["Authorization"] == "Bearer backup-key"
    assert calls[0]["json"]["thinking"] == {"type": "enabled"}
    assert calls[0]["json"]["reasoning_effort"] == "high"
    assert "temperature" not in calls[0]["json"]
