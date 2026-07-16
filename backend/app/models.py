from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Stock(Base):
    __tablename__ = "aq_stocks"

    symbol: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), default="")
    market: Mapped[str] = mapped_column(String(16), default="A")
    industry: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class DailyPrice(Base):
    __tablename__ = "aq_daily_prices"
    __table_args__ = (
        UniqueConstraint("symbol", "trade_date", name="uq_aq_price_symbol_date"),
        Index("ix_aq_prices_date", "trade_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(ForeignKey("aq_stocks.symbol"), index=True)
    trade_date: Mapped[date] = mapped_column(Date)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    turnover_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    adjustment: Mapped[str] = mapped_column(String(8), default="qfq")
    source: Mapped[str] = mapped_column(String(32), default="akshare")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class FinancialMetric(Base):
    __tablename__ = "aq_financial_metrics"
    __table_args__ = (
        UniqueConstraint(
            "symbol", "report_date", "metric_name", name="uq_aq_financial_metric"
        ),
        Index("ix_aq_financial_symbol_date", "symbol", "report_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(ForeignKey("aq_stocks.symbol"), index=True)
    report_date: Mapped[date] = mapped_column(Date)
    report_period: Mapped[str | None] = mapped_column(String(32), nullable=True)
    metric_name: Mapped[str] = mapped_column(String(120))
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    yoy: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="akshare")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class NewsItem(Base):
    __tablename__ = "aq_news_items"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_aq_news_hash"),
        Index("ix_aq_news_symbol_time", "symbol", "published_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(24), default="news")
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(120), default="")
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    sentiment: Mapped[SentimentAnalysis | None] = relationship(
        back_populates="news", uselist=False, cascade="all, delete-orphan"
    )


class SentimentAnalysis(Base):
    __tablename__ = "aq_sentiment_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("aq_news_items.id"), unique=True)
    label: Mapped[str] = mapped_column(String(16))
    score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(Text, default="")
    rationale: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str] = mapped_column(String(120), default="heuristic")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    news: Mapped[NewsItem] = relationship(back_populates="sentiment")


class StrategyConfig(Base):
    __tablename__ = "aq_strategy_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    watchlist: Mapped[list[str]] = mapped_column(JSON, default=list)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class FactorScore(Base):
    __tablename__ = "aq_factor_scores"
    __table_args__ = (
        UniqueConstraint("symbol", "score_date", name="uq_aq_factor_symbol_date"),
        Index("ix_aq_factor_date_total", "score_date", "total_score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(ForeignKey("aq_stocks.symbol"), index=True)
    score_date: Mapped[date] = mapped_column(Date)
    momentum_score: Mapped[float] = mapped_column(Float)
    quality_score: Mapped[float] = mapped_column(Float)
    sentiment_score: Mapped[float] = mapped_column(Float)
    total_score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class BacktestRun(Base):
    __tablename__ = "aq_backtest_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON)
    equity_curve: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class JobRun(Base):
    __tablename__ = "aq_job_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(24), default="running")
    message: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
