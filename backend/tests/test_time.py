from datetime import datetime

from app.core.time import beijing_iso, utc_iso


def test_internal_naive_utc_is_serialized_with_z() -> None:
    assert utc_iso(datetime(2026, 7, 20, 1, 30)) == "2026-07-20T01:30:00Z"


def test_internal_utc_can_be_rendered_as_beijing_time() -> None:
    assert beijing_iso(datetime(2026, 7, 20, 1, 30)) == "2026-07-20T09:30:00+08:00"


def test_chinese_upstream_wall_time_keeps_its_beijing_clock() -> None:
    assert (
        beijing_iso(datetime(2026, 7, 20, 9, 30), naive_is_beijing=True)
        == "2026-07-20T09:30:00+08:00"
    )
