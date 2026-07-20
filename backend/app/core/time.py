from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")


def utc_iso(value: datetime | None) -> str | None:
    """Serialize the project's naive-UTC database timestamps unambiguously."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def beijing_iso(value: datetime | None, *, naive_is_beijing: bool = False) -> str | None:
    """Serialize a datetime with an explicit Asia/Shanghai offset.

    Upstream Chinese news/announcement timestamps are stored as Beijing wall
    time for backward compatibility. Internal job timestamps are stored as
    naive UTC and should use the default conversion path.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=SHANGHAI if naive_is_beijing else UTC)
    return value.astimezone(SHANGHAI).isoformat()
