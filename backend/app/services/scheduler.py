from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.automation import get_automation_settings
from app.services.task_queue import enqueue_task

SHANGHAI = ZoneInfo("Asia/Shanghai")
NEWS_JOB_ID = "news_analysis"
scheduler = BackgroundScheduler(timezone=SHANGHAI)

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


def _news_next_run(interval_hours: int) -> datetime:
    return datetime.now(SHANGHAI) + timedelta(hours=interval_hours)


def reschedule_news_analysis(
    interval_hours: int, enabled: bool, *, start_after_interval: bool = True
) -> datetime | None:
    existing = scheduler.get_job(NEWS_JOB_ID)
    if not enabled:
        if existing is not None:
            scheduler.remove_job(NEWS_JOB_ID)
        return None
    next_run = _news_next_run(interval_hours) if start_after_interval else datetime.now(SHANGHAI)
    scheduler.add_job(
        scheduled_news_analysis,
        IntervalTrigger(hours=interval_hours, timezone=SHANGHAI),
        id=NEWS_JOB_ID,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=next_run,
    )
    return next_run


def news_scheduler_state() -> datetime | None:
    job = scheduler.get_job(NEWS_JOB_ID)
    return job.next_run_time if job is not None else None


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
    with SessionLocal() as db:
        automation = get_automation_settings(db)
        reschedule_news_analysis(
            automation.news_analysis_interval_hours,
            automation.news_analysis_enabled,
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
