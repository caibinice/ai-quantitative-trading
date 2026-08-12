from __future__ import annotations

import asyncio
import html
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

import httpx

FEEDS = (
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("MIT AI", "https://news.mit.edu/rss/topic/artificial-intelligence2"),
    ("NVIDIA Developer", "https://developer.nvidia.com/blog/tag/generative-ai/feed/"),
    ("AWS Machine Learning", "https://aws.amazon.com/blogs/machine-learning/feed/"),
)
NEWS_WINDOW_DAYS = 7
TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class FeedItem:
    title: str
    source: str
    url: str
    published_at: datetime

    def as_dict(self) -> dict[str, str]:
        published = self.published_at.astimezone(UTC)
        return {
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "publishedAt": published.isoformat().replace("+00:00", "Z"),
        }


def _child_text(element: ElementTree.Element, names: set[str]) -> str:
    for child in element.iter():
        if child.tag.rsplit("}", 1)[-1].lower() in names and child.text:
            return child.text.strip()
    return ""


def _parse_date(raw: str) -> datetime:
    if not raw:
        return datetime.now(UTC)
    try:
        value = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def parse_feed(payload: str, source: str) -> list[FeedItem]:
    root = ElementTree.fromstring(payload)
    result: list[FeedItem] = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1].lower() not in {"item", "entry"}:
            continue
        title = html.unescape(TAG_RE.sub("", _child_text(node, {"title"}))).strip()
        link = _child_text(node, {"link"})
        if not link:
            for child in node.iter():
                if child.tag.rsplit("}", 1)[-1].lower() == "link":
                    link = child.attrib.get("href", "").strip()
                    if link:
                        break
        published = _child_text(node, {"pubdate", "published", "updated"})
        if title and link.startswith(("https://", "http://")):
            result.append(
                FeedItem(
                    title=title[:500],
                    source=source,
                    url=link,
                    published_at=_parse_date(published),
                )
            )
    return result


class BlogNewsCache:
    def __init__(self) -> None:
        self._items: list[FeedItem] = []
        self._updated_at: datetime | None = None
        self._lock = asyncio.Lock()

    async def get(
        self,
        *,
        page: int,
        page_size: int,
        source: str,
        ttl_seconds: int,
        stale_seconds: int,
        seed_file: str = "",
    ) -> dict[str, object]:
        now = datetime.now(UTC)
        if not self._updated_at and seed_file:
            self._load_seed(Path(seed_file), stale_seconds)
        if self._updated_at and now - self._updated_at < timedelta(seconds=ttl_seconds):
            return self._response(page, page_size, source, "fresh", ttl_seconds, now)

        async with self._lock:
            now = datetime.now(UTC)
            if self._updated_at and now - self._updated_at < timedelta(seconds=ttl_seconds):
                return self._response(page, page_size, source, "fresh", ttl_seconds, now)
            fetched = await self._fetch_all()
            if any(fetched.values()):
                previous = {
                    feed_source: [
                        item for item in self._items if item.source == feed_source
                    ]
                    for feed_source, _ in FEEDS
                }
                merged = [
                    item
                    for feed_source, _ in FEEDS
                    for item in (fetched.get(feed_source) or previous[feed_source])
                ]
                known_sources = {feed_source for feed_source, _ in FEEDS}
                merged.extend(
                    item
                    for feed_source, items in fetched.items()
                    if feed_source not in known_sources
                    for item in items
                )
                merged.extend(
                    item for item in self._items if item.source not in known_sources
                )
                self._items = self._recent(self._balanced(merged), now)
                self._updated_at = now
                if seed_file:
                    self._save_snapshot(Path(seed_file))
                return self._response(
                    page, page_size, source, "refreshed", ttl_seconds, now
                )
            if (
                self._updated_at
                and now - self._updated_at <= timedelta(seconds=stale_seconds)
                and self._items
            ):
                return self._response(
                    page, page_size, source, "stale", ttl_seconds, now
                )
            return self._response(
                page, page_size, source, "unavailable", ttl_seconds, now
            )

    async def _fetch_all(self) -> dict[str, list[FeedItem]]:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(5.0),
            follow_redirects=True,
            transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0"),
        ) as client:
            responses = await asyncio.gather(
                *(self._fetch_one(client, source, url) for source, url in FEEDS)
            )
        return {
            source: items
            for (source, _), items in zip(FEEDS, responses, strict=True)
        }

    @staticmethod
    async def _fetch_one(
        client: httpx.AsyncClient, source: str, url: str
    ) -> list[FeedItem]:
        try:
            response = await client.get(
                url,
                headers={"User-Agent": "Fish-AI-Blog/1.0 (+https://101.132.78.217/)"},
            )
            response.raise_for_status()
            return parse_feed(response.text, source)
        except (httpx.HTTPError, ElementTree.ParseError, ValueError):
            return []

    def _response(
        self,
        page: int,
        page_size: int,
        source: str,
        status: str,
        ttl_seconds: int,
        now: datetime,
    ) -> dict[str, object]:
        recent = self._recent(self._items, now)
        counts = {
            feed_source: sum(item.source == feed_source for item in recent)
            for feed_source, _ in FEEDS
        }
        source_filter = source.strip()
        visible = (
            [item for item in recent if item.source == source_filter]
            if source_filter
            else recent
        )
        total = len(visible)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        return {
            "items": [item.as_dict() for item in visible[start : start + page_size]],
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": total_pages,
            "source": source_filter or None,
            "sources": [
                {"name": feed_source, "count": counts[feed_source]}
                for feed_source, _ in FEEDS
                if counts[feed_source]
            ],
            "windowDays": NEWS_WINDOW_DAYS,
            "cacheStatus": status,
            "updatedAt": (
                self._updated_at.isoformat().replace("+00:00", "Z")
                if self._updated_at
                else None
            ),
            "nextUpdateAt": (
                (self._updated_at + timedelta(seconds=ttl_seconds))
                .isoformat()
                .replace("+00:00", "Z")
                if self._updated_at
                else None
            ),
        }

    @staticmethod
    def _recent(items: list[FeedItem], now: datetime) -> list[FeedItem]:
        cutoff = now - timedelta(days=NEWS_WINDOW_DAYS)
        latest = now + timedelta(hours=1)
        return [
            item
            for item in items
            if cutoff <= item.published_at.astimezone(UTC) <= latest
        ]

    @staticmethod
    def _balanced(items: list[FeedItem]) -> list[FeedItem]:
        unique = {item.url: item for item in items}
        groups = {
            source: sorted(
                (item for item in unique.values() if item.source == source),
                key=lambda item: item.published_at,
                reverse=True,
            )
            for source, _ in FEEDS
        }
        result: list[FeedItem] = []
        depth = 0
        while any(depth < len(group) for group in groups.values()):
            for source, _ in FEEDS:
                group = groups[source]
                if depth < len(group):
                    result.append(group[depth])
            depth += 1
        known_sources = set(groups)
        result.extend(
            sorted(
                (item for item in unique.values() if item.source not in known_sources),
                key=lambda item: item.published_at,
                reverse=True,
            )
        )
        return result

    def _load_seed(self, path: Path, stale_seconds: int) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            updated = datetime.fromisoformat(payload["updatedAt"].replace("Z", "+00:00"))
            if datetime.now(UTC) - updated > timedelta(seconds=stale_seconds):
                return
            items = [
                FeedItem(
                    title=item["title"],
                    source=item["source"],
                    url=item["url"],
                    published_at=datetime.fromisoformat(
                        item["publishedAt"].replace("Z", "+00:00")
                    ),
                )
                for item in payload["items"]
            ]
            self._items = self._recent(self._balanced(items), datetime.now(UTC))
            if not self._items:
                return
            self._updated_at = updated
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return

    def _save_snapshot(self, path: Path) -> None:
        if not self._updated_at:
            return
        payload = {
            "updatedAt": self._updated_at.isoformat().replace("+00:00", "Z"),
            "items": [item.as_dict() for item in self._items],
        }
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            temporary.replace(path)
        except OSError:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


blog_news_cache = BlogNewsCache()
