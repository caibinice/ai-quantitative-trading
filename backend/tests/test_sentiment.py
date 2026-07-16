from __future__ import annotations

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
