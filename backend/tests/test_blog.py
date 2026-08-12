from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api import blog
from app.core.database import Base, get_db
from app.services.blog_news import BlogNewsCache, FeedItem, parse_feed

ADMIN_TOKEN = "test-token-with-at-least-thirty-two-characters"


def _client(monkeypatch) -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def test_db():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    monkeypatch.setattr(
        blog,
        "get_settings",
        lambda: SimpleNamespace(
            blog_admin_token=ADMIN_TOKEN,
            blog_news_cache_seconds=21600,
            blog_news_stale_seconds=604800,
            blog_news_seed_file="",
        ),
    )
    app = FastAPI()
    app.include_router(blog.router, prefix="/api")
    app.dependency_overrides[get_db] = test_db
    return TestClient(app)


def test_comment_email_stays_private_and_admin_can_delete(monkeypatch) -> None:
    client = _client(monkeypatch)
    created = client.post(
        "/api/blog/comments",
        json={
            "displayName": "Fish Friend",
            "email": " Friend@Example.COM ",
            "content": "写得很清楚。",
            "website": "",
        },
    )
    assert created.status_code == 201
    assert "email" not in created.json()

    public = client.get("/api/blog/comments").json()
    assert public["items"][0]["displayName"] == "Fish Friend"
    assert "email" not in public["items"][0]

    assert client.get("/api/blog/admin/comments").status_code == 401
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    private = client.get("/api/blog/admin/comments", headers=headers)
    assert private.status_code == 200
    assert private.json()["items"][0]["email"] == "friend@example.com"

    comment_id = private.json()["items"][0]["id"]
    assert (
        client.delete(f"/api/blog/admin/comments/{comment_id}", headers=headers).status_code
        == 204
    )
    assert client.get("/api/blog/comments").json()["items"] == []


def test_comment_validation_and_honeypot(monkeypatch) -> None:
    client = _client(monkeypatch)
    invalid = client.post(
        "/api/blog/comments",
        json={"email": "not-an-email", "content": "ok"},
    )
    assert invalid.status_code == 422
    trapped = client.post(
        "/api/blog/comments",
        json={
            "email": "real@example.com",
            "content": "looks human",
            "website": "https://spam.example",
        },
    )
    assert trapped.status_code == 400


def test_parse_rss_and_atom() -> None:
    rss = """
    <rss><channel><item><title>AI &amp; systems</title>
    <link>https://example.com/a</link><pubDate>Fri, 24 Jul 2026 10:00:00 GMT</pubDate>
    </item></channel></rss>
    """
    atom = """
    <feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Model update</title>
    <link href="https://example.com/b"/><updated>2026-07-24T11:00:00Z</updated>
    </entry></feed>
    """
    assert parse_feed(rss, "RSS")[0].title == "AI & systems"
    assert parse_feed(atom, "Atom")[0].url == "https://example.com/b"


def test_news_cache_serves_fresh_then_stale(monkeypatch) -> None:
    cache = BlogNewsCache()
    item = FeedItem(
        title="A release",
        source="Source",
        url="https://example.com/release",
        published_at=datetime.now(UTC),
    )

    async def fetched():
        return {"Source": [item]}

    monkeypatch.setattr(cache, "_fetch_all", fetched)
    first = asyncio.run(
        cache.get(
            page=1,
            page_size=12,
            source="",
            ttl_seconds=21600,
            stale_seconds=604800,
        )
    )
    assert first["cacheStatus"] == "refreshed"
    assert first["items"][0]["title"] == "A release"

    cache._updated_at = datetime.now(UTC) - timedelta(hours=7)

    async def failed():
        return {}

    monkeypatch.setattr(cache, "_fetch_all", failed)
    stale = asyncio.run(
        cache.get(
            page=1,
            page_size=12,
            source="",
            ttl_seconds=21600,
            stale_seconds=604800,
        )
    )
    assert stale["cacheStatus"] == "stale"
    assert stale["items"][0]["url"] == "https://example.com/release"


def test_news_seed_keeps_all_official_sources(monkeypatch, tmp_path) -> None:
    cache = BlogNewsCache()
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    seed = tmp_path / "news.json"
    seed.write_text(
        json.dumps(
            {
                "updatedAt": now,
                "items": [
                    {
                        "title": source,
                        "source": source,
                        "url": f"https://example.com/{index}",
                        "publishedAt": now,
                    }
                    for index, source in enumerate(
                        ("OpenAI", "Google DeepMind", "Hugging Face")
                    )
                ],
            }
        ),
        encoding="utf-8",
    )

    async def should_not_fetch():
        raise AssertionError("fresh seed should be served from memory")

    monkeypatch.setattr(cache, "_fetch_all", should_not_fetch)
    response = asyncio.run(
        cache.get(
            page=1,
            page_size=12,
            source="",
            ttl_seconds=21600,
            stale_seconds=604800,
            seed_file=str(seed),
        )
    )
    assert {item["source"] for item in response["items"]} == {
        "OpenAI",
        "Google DeepMind",
        "Hugging Face",
    }


def test_news_cache_filters_recent_items_and_paginates_by_source(
    monkeypatch, tmp_path
) -> None:
    cache = BlogNewsCache()
    now = datetime.now(UTC)
    fresh_items = [
        FeedItem(
            title=f"OpenAI {index}",
            source="OpenAI",
            url=f"https://example.com/openai/{index}",
            published_at=now - timedelta(hours=index),
        )
        for index in range(3)
    ]
    fresh_items.append(
        FeedItem(
            title="MIT recent",
            source="MIT AI",
            url="https://example.com/mit/recent",
            published_at=now - timedelta(days=2),
        )
    )
    fresh_items.append(
        FeedItem(
            title="MIT old",
            source="MIT AI",
            url="https://example.com/mit/old",
            published_at=now - timedelta(days=8),
        )
    )

    async def fetched():
        return {"OpenAI": fresh_items[:3], "MIT AI": fresh_items[3:]}

    snapshot = tmp_path / "snapshot.json"
    monkeypatch.setattr(cache, "_fetch_all", fetched)
    response = asyncio.run(
        cache.get(
            page=2,
            page_size=1,
            source="OpenAI",
            ttl_seconds=21600,
            stale_seconds=604800,
            seed_file=str(snapshot),
        )
    )

    assert response["total"] == 3
    assert response["totalPages"] == 3
    assert response["page"] == 2
    assert response["items"][0]["title"] == "OpenAI 1"
    assert {item["name"] for item in response["sources"]} == {"OpenAI", "MIT AI"}
    assert all(item["title"] != "MIT old" for item in json.loads(snapshot.read_text())["items"])


def test_news_refresh_preserves_a_source_when_its_feed_temporarily_fails(
    monkeypatch,
) -> None:
    cache = BlogNewsCache()
    now = datetime.now(UTC)
    cache._items = [
        FeedItem("Old OpenAI", "OpenAI", "https://example.com/openai/old", now),
        FeedItem("Old MIT", "MIT AI", "https://example.com/mit/old", now),
    ]
    cache._updated_at = now - timedelta(hours=7)

    async def partially_fetched():
        return {
            "OpenAI": [
                FeedItem("New OpenAI", "OpenAI", "https://example.com/openai/new", now)
            ],
            "MIT AI": [],
        }

    monkeypatch.setattr(cache, "_fetch_all", partially_fetched)
    response = asyncio.run(
        cache.get(
            page=1,
            page_size=12,
            source="",
            ttl_seconds=21600,
            stale_seconds=604800,
        )
    )

    assert {item["title"] for item in response["items"]} == {
        "New OpenAI",
        "Old MIT",
    }


def test_news_endpoint_forwards_pagination_and_source(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_get(**kwargs):
        captured.update(kwargs)
        return {
            "items": [],
            "page": kwargs["page"],
            "pageSize": kwargs["page_size"],
            "total": 0,
            "totalPages": 0,
        }

    monkeypatch.setattr(blog.blog_news_cache, "get", fake_get)
    response = _client(monkeypatch).get(
        "/api/blog/news?page=2&pageSize=6&source=MIT%20AI"
    )

    assert response.status_code == 200
    assert captured["page"] == 2
    assert captured["page_size"] == 6
    assert captured["source"] == "MIT AI"
