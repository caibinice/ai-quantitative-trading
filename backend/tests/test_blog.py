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
            blog_news_cache_seconds=1800,
            blog_news_stale_seconds=86400,
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
        return [item]

    monkeypatch.setattr(cache, "_fetch_all", fetched)
    first = asyncio.run(
        cache.get(limit=12, ttl_seconds=1800, stale_seconds=86400)
    )
    assert first["cacheStatus"] == "refreshed"
    assert first["items"][0]["title"] == "A release"

    cache._updated_at = datetime.now(UTC) - timedelta(hours=1)

    async def failed():
        return []

    monkeypatch.setattr(cache, "_fetch_all", failed)
    stale = asyncio.run(
        cache.get(limit=12, ttl_seconds=1800, stale_seconds=86400)
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
            limit=12,
            ttl_seconds=1800,
            stale_seconds=86400,
            seed_file=str(seed),
        )
    )
    assert {item["source"] for item in response["items"]} == {
        "OpenAI",
        "Google DeepMind",
        "Hugging Face",
    }
