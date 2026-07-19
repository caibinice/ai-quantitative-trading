from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import AutomationSetting
from app.schemas import AutomationSettingsPayload

AUTOMATION_SETTINGS_ID = 1


def get_automation_settings(db: Session) -> AutomationSetting:
    settings = db.get(AutomationSetting, AUTOMATION_SETTINGS_ID)
    if settings is None:
        settings = AutomationSetting(id=AUTOMATION_SETTINGS_ID)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def save_automation_settings(
    db: Session, payload: AutomationSettingsPayload
) -> AutomationSetting:
    settings = get_automation_settings(db)
    settings.news_analysis_enabled = payload.news_analysis_enabled
    settings.news_analysis_interval_hours = payload.news_analysis_interval_hours
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
