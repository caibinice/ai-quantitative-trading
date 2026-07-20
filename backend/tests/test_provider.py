from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from app.services.provider import AkshareProvider, _number, content_hash


def test_number_normalizes_commas_and_percent() -> None:
    assert _number("1,234.50") == 1234.5
    assert _number("12.3%") == 12.3
    assert _number("-") is None


def test_content_hash_is_stable_and_symbol_specific() -> None:
    published = datetime(2025, 1, 1)
    first = content_hash("000001", "公告", "https://example.test/1", published)
    same = content_hash("000001", "公告", "https://example.test/1", published)
    other = content_hash("600000", "公告", "https://example.test/1", published)

    assert first == same
    assert first != other


def test_tencent_price_fallback_normalization() -> None:
    frame = pd.DataFrame(
        [
            {
                "date": "2025-01-02",
                "open": 10,
                "close": 10.5,
                "high": 10.6,
                "low": 9.9,
                "amount": 1234,
            }
        ]
    )
    rows = AkshareProvider()._normalize_tencent_prices(frame, "000001", "qfq")

    assert rows[0]["trade_date"].isoformat() == "2025-01-02"
    assert rows[0]["close"] == 10.5
    assert rows[0]["source"] == "akshare-tencent"


def test_cninfo_notice_mapping(monkeypatch) -> None:
    class FakeAk:
        @staticmethod
        def stock_zh_a_disclosure_report_cninfo(**_kwargs):
            return pd.DataFrame(
                [
                    {
                        "代码": "600519",
                        "简称": "贵州茅台",
                        "公告标题": "年度报告",
                        "公告时间": "2026-04-01",
                        "公告链接": "https://www.cninfo.com.cn/demo",
                    }
                ]
            )

    provider = AkshareProvider()
    monkeypatch.setattr(provider, "_ak", lambda: FakeAk())

    rows = provider.cninfo_notices(
        "600519", date(2026, 3, 1), date(2026, 4, 2)
    )

    assert rows[0]["source"] == "巨潮资讯"
    assert rows[0]["kind"] == "notice"
    assert rows[0]["published_at"].isoformat() == "2026-04-01T00:00:00"
