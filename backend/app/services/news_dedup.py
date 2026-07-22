from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import NewsItem

DEDUP_THRESHOLD = 0.90
MAX_EVENT_GAP_HOURS = 72
TRACKING_QUERY_KEYS = {
    "from",
    "source",
    "spm",
    "ref",
    "refer",
    "share",
    "share_source",
}


@dataclass(frozen=True)
class NewsSignature:
    title: str
    content: str
    source_url: str
    published_at: datetime


@dataclass
class DisplayNewsGroup:
    item: NewsItem
    related_symbols: list[str]


def normalize_news_text(value: str) -> str:
    """Normalize Chinese/Latin news text without changing its meaning."""
    value = html.unescape(unicodedata.normalize("NFKC", value or "")).lower()
    value = re.sub(r"https?://\S+", "", value)
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value)


def normalize_source_url(value: str) -> str:
    if not value:
        return ""
    try:
        parts = urlsplit(value.strip())
    except ValueError:
        return value.strip().lower().rstrip("/")
    query = [
        (key, item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
    ]
    path = re.sub(r"/+", "/", parts.path).rstrip("/")
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, urlencode(sorted(query)), "")
    )


def news_signature(item: NewsItem | dict[str, Any]) -> NewsSignature:
    def value(name: str, default: Any = "") -> Any:
        return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)

    return NewsSignature(
        title=normalize_news_text(str(value("title"))),
        content=normalize_news_text(str(value("content"))),
        source_url=normalize_source_url(str(value("source_url"))),
        published_at=value("published_at"),
    )


def news_similarity(first: NewsSignature, second: NewsSignature) -> float:
    """Return deterministic event similarity using URL, title, excerpt and time."""
    if first.source_url and first.source_url == second.source_url:
        return 1.0

    gap_hours = abs((first.published_at - second.published_at).total_seconds()) / 3600
    if gap_hours > MAX_EVENT_GAP_HOURS:
        return 0.0
    time_score = 1.0 if gap_hours <= 6 else 0.98 if gap_hours <= 24 else 0.94

    if first.title and first.title == second.title:
        return 1.0
    title_score = _text_similarity(first.title, second.title)
    if title_score < 0.72:
        return 0.0

    if len(first.content) >= 20 and len(second.content) >= 20:
        content_score = _text_similarity(first.content[:3000], second.content[:3000])
        score = 0.62 * title_score + 0.28 * content_score + 0.10 * time_score
    else:
        score = 0.90 * title_score + 0.10 * time_score
    return round(score, 4)


def is_duplicate_news(
    first: NewsItem | dict[str, Any],
    second: NewsItem | dict[str, Any],
    threshold: float = DEDUP_THRESHOLD,
) -> bool:
    return news_similarity(news_signature(first), news_signature(second)) >= threshold


def group_news_for_display(
    items: list[NewsItem], *, collapse_across_symbols: bool
) -> list[DisplayNewsGroup]:
    """Hide same-stock near duplicates and collapse exact titles in the all-stock view."""
    groups: list[DisplayNewsGroup] = []
    for item in items:
        normalized_title = normalize_news_text(item.title)
        matched: DisplayNewsGroup | None = None
        for group in groups:
            same_stock_duplicate = (
                item.symbol == group.item.symbol
                and item.kind == group.item.kind
                and is_duplicate_news(item, group.item)
            )
            same_title_across_stocks = (
                collapse_across_symbols
                and normalized_title
                and normalized_title == normalize_news_text(group.item.title)
            )
            if same_stock_duplicate or same_title_across_stocks:
                matched = group
                break
        if matched is None:
            groups.append(
                DisplayNewsGroup(item=item, related_symbols=[item.symbol] if item.symbol else [])
            )
        elif item.symbol and item.symbol not in matched.related_symbols:
            matched.related_symbols.append(item.symbol)
    return groups


def deduplicate_persisted_news(
    db: Session,
    symbols: list[str] | None = None,
    *,
    commit: bool = False,
) -> int:
    """Remove same-stock near duplicates while preserving cross-stock judgments."""
    query = select(NewsItem).options(selectinload(NewsItem.sentiment))
    if symbols:
        query = query.where(NewsItem.symbol.in_(symbols))
    items = list(db.scalars(query).all())
    items.sort(key=_keeper_priority, reverse=True)

    kept: dict[tuple[str | None, str], list[NewsItem]] = {}
    removed = 0
    for item in items:
        bucket = kept.setdefault((item.symbol, item.kind), [])
        canonical = next(
            (candidate for candidate in bucket if is_duplicate_news(item, candidate)), None
        )
        if canonical is None:
            bucket.append(item)
            continue
        _merge_news_fields(canonical, item)
        db.delete(item)
        removed += 1
    if commit:
        db.commit()
    return removed


def _text_similarity(first: str, second: str) -> float:
    if not first or not second:
        return 0.0
    if first == second:
        return 1.0
    sequence = SequenceMatcher(None, first, second, autojunk=False).ratio()
    first_grams = _ngrams(first)
    second_grams = _ngrams(second)
    union = first_grams | second_grams
    jaccard = len(first_grams & second_grams) / len(union) if union else 0.0
    return max(sequence, jaccard)


def _ngrams(value: str, size: int = 3) -> set[str]:
    if len(value) <= size:
        return {value}
    return {value[index : index + size] for index in range(len(value) - size + 1)}


def _keeper_priority(item: NewsItem) -> tuple[int, int, int, int, datetime]:
    official = int(any(name in item.source for name in ("巨潮", "上交所", "深交所")))
    return (
        int(item.sentiment is not None),
        official,
        len(item.content or ""),
        int(bool(item.source_url)),
        item.published_at,
    )


def _merge_news_fields(canonical: NewsItem, duplicate: NewsItem) -> None:
    if len(duplicate.content or "") > len(canonical.content or ""):
        canonical.content = duplicate.content
    if not canonical.source_url and duplicate.source_url:
        canonical.source_url = duplicate.source_url
    if not canonical.source and duplicate.source:
        canonical.source = duplicate.source
