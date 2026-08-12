from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models import NewsItem, SentimentAnalysis
from app.services.news_dedup import deduplicate_persisted_news

POSITIVE_WORDS = (
    "增长",
    "增持",
    "中标",
    "盈利",
    "扭亏",
    "回购",
    "突破",
    "分红",
    "上调",
    "签约",
)
NEGATIVE_WORDS = (
    "下滑",
    "减持",
    "亏损",
    "处罚",
    "调查",
    "诉讼",
    "风险",
    "终止",
    "下调",
    "违约",
)


@dataclass
class SentimentResult:
    label: str
    score: float
    confidence: float
    summary: str
    rationale: str
    model: str


def _clamp(value: Any, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I | re.S)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("模型没有返回 JSON 对象")
    return json.loads(cleaned[start : end + 1])


class SentimentAnalyzer:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def analyze(self, title: str, content: str, kind: str = "news") -> SentimentResult:
        if not self.settings.llm_enabled or not self.settings.llm_api_key:
            return self._heuristic(title, content)
        try:
            return self._llm(title, content, kind)
        except Exception as exc:
            result = self._heuristic(title, content)
            result.rationale = f"LLM 调用失败，已回退规则分析：{type(exc).__name__}"
            return result

    def _llm(self, title: str, content: str, kind: str) -> SentimentResult:
        prompt = f"""你是一名谨慎的 A 股事件研究助手。请判断下面{kind}对相关上市公司的短期影响。
只基于给定文本，不补充外部事实，不给出买卖建议。必须返回一个 JSON 对象：
{{"label":"利好|中性|利空","score":-1到1,"confidence":0到1,
"summary":"不超过80字","rationale":"不超过120字"}}

标题：{title[:500]}
正文：{content[:6000]}
"""
        url = f"{self.settings.llm_base_url.rstrip('/')}/chat/completions"
        body: dict[str, Any] = {
            "model": self.settings.llm_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "你输出严格 JSON，结论保持克制。"},
                {"role": "user", "content": prompt},
            ],
        }
        if self.settings.llm_thinking_enabled:
            body["thinking"] = {"type": "enabled"}
            body["reasoning_effort"] = self.settings.llm_reasoning_effort
        else:
            body["temperature"] = 0

        try:
            response = self._post_llm(url, body, self.settings.llm_api_key)
        except httpx.HTTPError as exc:
            backup = self.settings.llm_api_key_backup
            if not backup or backup == self.settings.llm_api_key or not _can_retry_with_backup(exc):
                raise
            response = self._post_llm(url, body, backup)
        payload = _extract_json(response.json()["choices"][0]["message"]["content"])
        score = _clamp(payload.get("score", 0), -1, 1)
        label = str(payload.get("label", "中性"))
        if label not in {"利好", "中性", "利空"}:
            label = "利好" if score > 0.15 else "利空" if score < -0.15 else "中性"
        return SentimentResult(
            label=label,
            score=score,
            confidence=_clamp(payload.get("confidence", 0.5), 0, 1),
            summary=str(payload.get("summary", ""))[:500],
            rationale=str(payload.get("rationale", ""))[:1000],
            model=self.settings.llm_model,
        )

    def _post_llm(
        self, url: str, body: dict[str, Any], api_key: str
    ) -> httpx.Response:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=body,
            timeout=self.settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        return response

    def _heuristic(self, title: str, content: str) -> SentimentResult:
        text = f"{title} {content}"
        positive = sum(text.count(word) for word in POSITIVE_WORDS)
        negative = sum(text.count(word) for word in NEGATIVE_WORDS)
        raw = positive - negative
        score = max(-1.0, min(1.0, raw / max(3, positive + negative)))
        label = "利好" if score > 0.15 else "利空" if score < -0.15 else "中性"
        return SentimentResult(
            label=label,
            score=score,
            confidence=min(0.75, 0.35 + 0.08 * (positive + negative)),
            summary=title[:80],
            rationale=f"教学回退规则：正向词 {positive} 个，负向词 {negative} 个。",
            model="heuristic-v1",
        )

    def analyze_pending(
        self,
        db: Session,
        limit: int = 50,
        force: bool = False,
        write_batch_size: int = 10,
    ) -> int:
        if write_batch_size < 1:
            raise ValueError("write_batch_size 必须大于 0")
        # Clean legacy same-stock duplicates before selecting pending work so
        # one event never consumes multiple model calls for the same company.
        deduplicate_persisted_news(db, commit=True)
        query = select(NewsItem).order_by(NewsItem.published_at.desc())
        if not force:
            query = query.where(~NewsItem.sentiment.has())
        items = list(db.scalars(query.limit(limit)).all())
        pending = [(item.id, item.title, item.content, item.kind) for item in items]

        # The LLM phase can take many minutes. End the read transaction now so
        # the worker does not keep a remote MySQL connection checked out and
        # discover that it was reset only when the final INSERT starts.
        db.commit()

        for offset in range(0, len(pending), write_batch_size):
            batch = pending[offset : offset + write_batch_size]
            results = [
                (news_id, self.analyze(title, content, kind))
                for news_id, title, content, kind in batch
            ]

            news_ids = [news_id for news_id, _result in results]
            existing = {
                item.news_id: item
                for item in db.scalars(
                    select(SentimentAnalysis).where(SentimentAnalysis.news_id.in_(news_ids))
                ).all()
            }
            for news_id, result in results:
                analysis = existing.get(news_id) or SentimentAnalysis(news_id=news_id)
                analysis.label = result.label
                analysis.score = result.score
                analysis.confidence = result.confidence
                analysis.summary = result.summary
                analysis.rationale = result.rationale
                analysis.model = result.model
                db.add(analysis)
            # Save partial progress in small statements. If a later upstream or
            # database call fails, earlier analyzed batches remain available.
            db.commit()
        return len(items)


def _can_retry_with_backup(exc: Exception) -> bool:
    if isinstance(exc, httpx.TimeoutException | httpx.NetworkError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {401, 402, 403, 408, 409, 429} or (
            exc.response.status_code >= 500
        )
    return False
