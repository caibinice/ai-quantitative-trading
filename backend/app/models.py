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


class LearningProgress(Base):
    __tablename__ = "aq_learning_progress"

    profile_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    completed: Mapped[list[str]] = mapped_column(JSON, default=list)
    quiz_scores: Mapped[dict[str, int]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class AutomationSetting(Base):
    __tablename__ = "aq_automation_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    news_analysis_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    news_analysis_interval_hours: Mapped[int] = mapped_column(Integer, default=6)
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


class TradingCalendar(Base):
    __tablename__ = "aq_trading_calendar"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    source: Mapped[str] = mapped_column(String(48), default="akshare-sina")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class IndexPrice(Base):
    __tablename__ = "aq_index_prices"
    __table_args__ = (
        UniqueConstraint("symbol", "trade_date", name="uq_aq_index_symbol_date"),
        Index("ix_aq_index_symbol_date", "symbol", "trade_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(16))
    name: Mapped[str] = mapped_column(String(80), default="")
    trade_date: Mapped[date] = mapped_column(Date)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    source: Mapped[str] = mapped_column(String(48), default="akshare")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class PointInTimeFinancial(Base):
    __tablename__ = "aq_pit_financials"
    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "report_date",
            "available_at",
            "metric_name",
            name="uq_aq_pit_financial",
        ),
        Index("ix_aq_pit_symbol_available", "symbol", "available_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(ForeignKey("aq_stocks.symbol"), index=True)
    report_date: Mapped[date] = mapped_column(Date)
    available_at: Mapped[date] = mapped_column(Date, index=True)
    metric_name: Mapped[str] = mapped_column(String(120))
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(48), default="akshare-yjbb")
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ResearchTask(Base):
    __tablename__ = "aq_research_tasks"
    __table_args__ = (
        Index("ix_aq_task_queue", "status", "priority", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(24), default="queued", index=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    result: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error: Mapped[str] = mapped_column(Text, default="")
    progress: Mapped[float] = mapped_column(Float, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=2)
    worker_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class WalkForwardRun(Base):
    __tablename__ = "aq_walk_forward_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    benchmark_symbol: Mapped[str] = mapped_column(String(16), default="000300")
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    windows: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON)
    equity_curve: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DataQualityRun(Base):
    __tablename__ = "aq_data_quality_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(24), default="running")
    checks_count: Mapped[int] = mapped_column(Integer, default=0)
    issues_count: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DataQualityIssue(Base):
    __tablename__ = "aq_data_quality_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    entity_type: Mapped[str] = mapped_column(String(32))
    entity_id: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(300))
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BlogComment(Base):
    __tablename__ = "aq_blog_comments"
    __table_args__ = (Index("ix_aq_blog_comments_created", "created_at", "id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    display_name: Mapped[str] = mapped_column(String(40), default="Anonymous")
    email: Mapped[str] = mapped_column(String(254))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
