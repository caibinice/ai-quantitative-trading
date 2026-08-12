from __future__ import annotations

import hashlib
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import DEFAULT_STOCK_NAMES  # noqa: E402
from app.core.database import SessionLocal, create_tables  # noqa: E402
from app.models import (  # noqa: E402
    DailyPrice,
    FinancialMetric,
    IndexPrice,
    NewsItem,
    PointInTimeFinancial,
    SentimentAnalysis,
    Stock,
    StrategyConfig,
    TradingCalendar,
)
from app.schemas import StrategyParameters  # noqa: E402
from app.services.data_quality import run_data_quality_checks  # noqa: E402
from app.services.scoring import calculate_scores  # noqa: E402

STOCKS = DEFAULT_STOCK_NAMES


def seed() -> None:
    create_tables()
    rng = np.random.default_rng(20260716)
    end = pd.Timestamp(date.today())
    dates = pd.bdate_range(end=end, periods=320)
    with SessionLocal() as db:
        has_real_calendar = db.scalar(
            select(TradingCalendar.trade_date)
            .where(TradingCalendar.source != "demo")
            .limit(1)
        )
        if not has_real_calendar:
            for trade_date in dates:
                day = trade_date.date()
                if db.get(TradingCalendar, day) is None:
                    db.add(TradingCalendar(trade_date=day, is_open=True, source="demo"))

        has_real_benchmark = db.scalar(
            select(IndexPrice.trade_date)
            .where(IndexPrice.symbol == "000300", IndexPrice.source != "demo")
            .limit(1)
        )
        if not has_real_benchmark:
            benchmark_existing_dates = set(
                db.scalars(
                    select(IndexPrice.trade_date).where(IndexPrice.symbol == "000300")
                ).all()
            )
            benchmark_returns = rng.normal(0.00018, 0.009, len(dates))
            benchmark_closes = 3500 * np.exp(np.cumsum(benchmark_returns))
            for trade_date, close in zip(dates, benchmark_closes, strict=True):
                day = trade_date.date()
                if day in benchmark_existing_dates:
                    continue
                open_price = close * (1 + rng.normal(0, 0.002))
                db.add(
                    IndexPrice(
                        symbol="000300",
                        name="沪深300",
                        trade_date=day,
                        open=round(float(open_price), 2),
                        high=round(float(max(open_price, close) * 1.004), 2),
                        low=round(float(min(open_price, close) * 0.996), 2),
                        close=round(float(close), 2),
                        volume=float(rng.integers(80_000_000, 400_000_000)),
                        source="demo",
                    )
                )

        for index, (symbol, name) in enumerate(STOCKS.items()):
            stock = db.get(Stock, symbol) or Stock(symbol=symbol)
            stock.name = name
            db.add(stock)
            db.flush()

            existing_price_dates = set(
                db.scalars(
                    select(DailyPrice.trade_date).where(DailyPrice.symbol == symbol)
                ).all()
            )

            base = 10 + index * 22
            drift = 0.00015 + index * 0.00006
            returns = rng.normal(drift, 0.015 + index * 0.001, len(dates))
            closes = base * np.exp(np.cumsum(returns))
            for trade_date, close in zip(dates, closes, strict=True):
                day = trade_date.date()
                if day in existing_price_dates:
                    continue
                open_price = close * (1 + rng.normal(0, 0.004))
                high = max(open_price, close) * (1 + abs(rng.normal(0, 0.006)))
                low = min(open_price, close) * (1 - abs(rng.normal(0, 0.006)))
                db.add(
                    DailyPrice(
                        symbol=symbol,
                        trade_date=day,
                        open=round(float(open_price), 2),
                        high=round(float(high), 2),
                        low=round(float(low), 2),
                        close=round(float(close), 2),
                        volume=float(rng.integers(300_000, 8_000_000)),
                        amount=float(rng.integers(50_000_000, 2_000_000_000)),
                        turnover_rate=round(float(rng.uniform(0.2, 4.0)), 2),
                        source="demo",
                    )
                )

            existing_financial_keys = set(
                db.execute(
                    select(FinancialMetric.report_date, FinancialMetric.metric_name).where(
                        FinancialMetric.symbol == symbol
                    )
                ).all()
            )
            has_real_pit = db.scalar(
                select(PointInTimeFinancial.id)
                .where(
                    PointInTimeFinancial.symbol == symbol,
                    PointInTimeFinancial.source != "demo",
                )
                .limit(1)
            )
            for quarter in range(4):
                report_date = date.today() - timedelta(days=quarter * 90 + 30)
                metrics = {
                    "净资产收益率": 8 + index * 2 + rng.normal(0, 1),
                    "营业总收入同比增长": 5 + index * 3 + rng.normal(0, 3),
                    "归母净利润同比增长": 3 + index * 4 + rng.normal(0, 5),
                }
                for metric_name, value in metrics.items():
                    if (report_date, metric_name) not in existing_financial_keys:
                        db.add(
                            FinancialMetric(
                                symbol=symbol,
                                report_date=report_date,
                                report_period="演示数据",
                                metric_name=metric_name,
                                metric_value=round(float(value), 2),
                                yoy=round(float(value), 2),
                                source="demo",
                            )
                        )
                    if not has_real_pit:
                        available_at = min(date.today(), report_date + timedelta(days=20))
                        pit_exists = db.scalar(
                            select(PointInTimeFinancial).where(
                                PointInTimeFinancial.symbol == symbol,
                                PointInTimeFinancial.report_date == report_date,
                                PointInTimeFinancial.available_at == available_at,
                                PointInTimeFinancial.metric_name == metric_name,
                            )
                        )
                        if not pit_exists:
                            db.add(
                                PointInTimeFinancial(
                                    symbol=symbol,
                                    report_date=report_date,
                                    available_at=available_at,
                                    metric_name=metric_name,
                                    metric_value=round(float(value), 2),
                                    source="demo",
                                    is_estimated=False,
                                )
                            )

            templates = [
                ("发布经营增长公告，核心业务保持增长", 0.72, "利好"),
                ("提示行业需求波动与经营风险", -0.62, "利空"),
                ("召开年度股东大会并审议常规议案", 0.02, "中性"),
            ]
            for event_index in range(18):
                title, score, label = templates[(event_index + index) % len(templates)]
                published = datetime.combine(
                    date.today() - timedelta(days=event_index * 12 + index), datetime.min.time()
                )
                full_title = f"{name}：{title}"
                digest = hashlib.sha256(
                    f"demo|{symbol}|{published.isoformat()}|{full_title}".encode()
                ).hexdigest()
                news = db.scalar(select(NewsItem).where(NewsItem.content_hash == digest))
                if not news:
                    news = NewsItem(
                        symbol=symbol,
                        kind="notice" if event_index % 3 == 0 else "news",
                        title=full_title,
                        content="本条为界面演示用合成文本，不代表真实公司事件。",
                        source="演示数据",
                        source_url="",
                        published_at=published,
                        content_hash=digest,
                    )
                    db.add(news)
                    db.flush()
                analysis = db.scalar(
                    select(SentimentAnalysis).where(SentimentAnalysis.news_id == news.id)
                )
                if not analysis:
                    db.add(
                        SentimentAnalysis(
                            news_id=news.id,
                            label=label,
                            score=score,
                            confidence=0.86,
                            summary=title,
                            rationale="演示数据预设情绪标签。",
                            model="demo",
                        )
                    )

        config = db.scalar(
            select(StrategyConfig).where(StrategyConfig.name == "默认情绪行情双因子")
        )
        if not config:
            config = StrategyConfig(
                name="默认情绪行情双因子",
                description="价格动量、财务质量与新闻情绪的教学型组合策略",
                enabled=True,
                watchlist=list(STOCKS),
                parameters=StrategyParameters().model_dump(),
            )
            db.add(config)
        db.commit()
        calculate_scores(db, list(STOCKS), date.today(), StrategyParameters())
        run_data_quality_checks(db, list(STOCKS), "000300")
    print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed()
