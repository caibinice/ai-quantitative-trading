from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import NewsItem, SentimentAnalysis
from app.services.news_dedup import (
    deduplicate_persisted_news,
    group_news_for_display,
    is_duplicate_news,
    news_signature,
    news_similarity,
    normalize_source_url,
)
from app.services.repository import upsert_news

PUBLISHED = datetime(2026, 7, 21, 22, 6)
TITLE = "判若两基！张坤、刘彦春、朱少醒二季度集体“破圈”调仓"


def _row(symbol: str, *, title: str = TITLE, source: str = "来源A", suffix: str = "a"):
    return {
        "symbol": symbol,
        "kind": "news",
        "title": title,
        "content": "明星基金经理集体调仓，减持消费股并增持制造业股票。",
        "source": source,
        "source_url": f"https://news.example.com/story?id=88&utm_source={suffix}",
        "published_at": PUBLISHED,
        "content_hash": f"hash-{symbol}-{suffix}",
    }


def test_url_and_cross_source_similarity_reach_duplicate_threshold() -> None:
    first = _row("000333", suffix="eastmoney")
    second = _row(
        "000333",
        title="判若两基：张坤 刘彦春 朱少醒二季度集体破圈调仓",
        source="来源B",
        suffix="cninfo",
    )

    assert normalize_source_url(first["source_url"]) == normalize_source_url(
        second["source_url"]
    )
    assert news_similarity(news_signature(first), news_signature(second)) >= 0.90
    assert is_duplicate_news(first, second)


def test_different_events_are_not_collapsed() -> None:
    first = _row("000333")
    second = _row("000333", title="美的集团发布季度业绩预告", suffix="b")
    second["source_url"] = "https://news.example.com/earnings?id=99"
    second["published_at"] = PUBLISHED + timedelta(hours=1)

    assert not is_duplicate_news(first, second)


def test_cross_source_near_duplicate_without_shared_url() -> None:
    first = _row("000333")
    second = _row(
        "000333",
        title="判若两基：张坤、刘彦春、朱少醒二季度集体破圈调仓",
        source="来源B",
    )
    second["source_url"] = "https://another.example.cn/article/20260721/88"
    second["content"] = "明星基金经理集体调仓：减持消费股，同时增持制造业股票。"
    second["published_at"] = PUBLISHED + timedelta(minutes=40)

    assert news_similarity(news_signature(first), news_signature(second)) >= 0.90
    assert is_duplicate_news(first, second)


def test_upsert_deduplicates_per_stock_but_preserves_cross_stock_analysis() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        inserted = upsert_news(
            db,
            [
                _row("000333", suffix="first"),
                _row("000333", source="来源B", suffix="second"),
                _row("601899", suffix="third"),
            ],
        )
        db.commit()

        assert inserted == 2
        assert db.scalar(select(func.count(NewsItem.id))) == 2
        assert {item.symbol for item in db.scalars(select(NewsItem)).all()} == {
            "000333",
            "601899",
        }


def test_cleanup_keeps_analyzed_record_and_all_stock_view_collapses_title() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        pending = NewsItem(**_row("000333", suffix="pending"))
        analyzed = NewsItem(**_row("000333", source="来源B", suffix="analyzed"))
        other_stock = NewsItem(**_row("601899", suffix="other"))
        db.add_all([pending, analyzed, other_stock])
        db.flush()
        db.add(
            SentimentAnalysis(
                news_id=analyzed.id,
                label="利空",
                score=-0.5,
                confidence=0.7,
                summary="调仓事件",
                rationale="影响消费持仓",
                model="test-model",
            )
        )
        db.commit()

        removed = deduplicate_persisted_news(db, commit=True)
        remaining = list(db.scalars(select(NewsItem).order_by(NewsItem.id)).all())
        groups = group_news_for_display(remaining, collapse_across_symbols=True)

        assert removed == 1
        assert len(remaining) == 2
        assert next(item for item in remaining if item.symbol == "000333").sentiment is not None
        assert len(groups) == 1
        assert set(groups[0].related_symbols) == {"000333", "601899"}
