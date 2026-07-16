from __future__ import annotations

from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import StrategyConfig
from app.schemas import StrategyParameters
from app.services.pipeline import sync_market_data
from app.services.scoring import calculate_scores
from app.services.sentiment import SentimentAnalyzer

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def _active_config(db):
    return db.scalar(
        select(StrategyConfig).where(StrategyConfig.enabled.is_(True)).order_by(StrategyConfig.id)
    )


def scheduled_market_sync() -> None:
    with SessionLocal() as db:
        config = _active_config(db)
        symbols = config.watchlist if config else get_settings().watchlist
        today = date.today()
        sync_market_data(
            db,
            symbols,
            today - timedelta(days=15),
            today,
            include_financials=True,
            include_news=False,
            include_notices=False,
        )


def scheduled_news_analysis() -> None:
    with SessionLocal() as db:
        config = _active_config(db)
        symbols = config.watchlist if config else get_settings().watchlist
        today = date.today()
        sync_market_data(
            db,
            symbols,
            today - timedelta(days=7),
            today,
            include_financials=False,
            include_news=True,
            include_notices=True,
        )
        SentimentAnalyzer().analyze_pending(db, limit=200)


def scheduled_scoring() -> None:
    with SessionLocal() as db:
        config = _active_config(db)
        symbols = config.watchlist if config else get_settings().watchlist
        parameters = StrategyParameters(**(config.parameters if config else {}))
        calculate_scores(db, symbols, date.today(), parameters)


def start_scheduler() -> None:
    settings = get_settings()
    if not settings.scheduler_enabled or scheduler.running:
        return
    scheduler.add_job(
        scheduled_market_sync,
        CronTrigger.from_crontab(settings.price_sync_cron, timezone="Asia/Shanghai"),
        id="market_sync",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        scheduled_news_analysis,
        CronTrigger.from_crontab(settings.news_sync_cron, timezone="Asia/Shanghai"),
        id="news_analysis",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        scheduled_scoring,
        CronTrigger.from_crontab(settings.score_cron, timezone="Asia/Shanghai"),
        id="factor_scoring",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
