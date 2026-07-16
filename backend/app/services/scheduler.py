from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.task_queue import enqueue_task

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

def scheduled_market_sync() -> None:
    with SessionLocal() as db:
        enqueue_task(
            db,
            "market_sync",
            {"include_financials": True, "include_news": False, "include_notices": False},
        )


def scheduled_news_analysis() -> None:
    with SessionLocal() as db:
        enqueue_task(
            db,
            "market_sync",
            {"include_financials": False, "include_news": True, "include_notices": True},
        )
        enqueue_task(db, "sentiment_analysis", {"limit": 200}, priority=110)


def scheduled_scoring() -> None:
    with SessionLocal() as db:
        enqueue_task(db, "factor_scoring")


def scheduled_infrastructure_sync() -> None:
    with SessionLocal() as db:
        enqueue_task(db, "infrastructure_sync", priority=120)


def scheduled_data_quality() -> None:
    with SessionLocal() as db:
        enqueue_task(db, "data_quality", priority=130)


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
    scheduler.add_job(
        scheduled_infrastructure_sync,
        CronTrigger.from_crontab(settings.infrastructure_cron, timezone="Asia/Shanghai"),
        id="infrastructure_sync",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        scheduled_data_quality,
        CronTrigger.from_crontab(settings.data_quality_cron, timezone="Asia/Shanghai"),
        id="data_quality",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
