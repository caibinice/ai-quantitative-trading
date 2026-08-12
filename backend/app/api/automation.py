from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas import AutomationSettingsPayload, AutomationSettingsResponse
from app.services.automation import get_automation_settings, save_automation_settings
from app.services.scheduler import news_scheduler_state, reschedule_news_analysis

router = APIRouter(prefix="/automation", tags=["automation"])


def _response(row) -> AutomationSettingsResponse:
    settings = get_settings()
    return AutomationSettingsResponse(
        news_analysis_enabled=row.news_analysis_enabled,
        news_analysis_interval_hours=row.news_analysis_interval_hours,
        next_run_at=news_scheduler_state(),
        model=settings.llm_model,
        thinking_enabled=settings.llm_thinking_enabled,
        reasoning_effort=settings.llm_reasoning_effort,
        backup_key_configured=bool(settings.llm_api_key_backup),
        updated_at=row.updated_at,
    )


@router.get("/settings", response_model=AutomationSettingsResponse)
def read_automation_settings(
    db: Session = Depends(get_db),
) -> AutomationSettingsResponse:
    return _response(get_automation_settings(db))


@router.put("/settings", response_model=AutomationSettingsResponse)
def update_automation_settings(
    payload: AutomationSettingsPayload,
    db: Session = Depends(get_db),
) -> AutomationSettingsResponse:
    row = save_automation_settings(db, payload)
    reschedule_news_analysis(
        row.news_analysis_interval_hours,
        row.news_analysis_enabled,
    )
    return _response(row)
