from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.core.time import beijing_iso, utc_iso


class StrategyParameters(BaseModel):
    momentum_window: int = Field(default=20, ge=5, le=250)
    sentiment_lookback_days: int = Field(default=7, ge=1, le=90)
    sentiment_threshold: float = Field(default=-0.1, ge=-1, le=1)
    minimum_momentum: float = Field(default=0.0, ge=-1, le=2)
    top_n: int = Field(default=3, ge=1, le=50)
    momentum_weight: float = Field(default=0.55, ge=0, le=1)
    quality_weight: float = Field(default=0.15, ge=0, le=1)
    sentiment_weight: float = Field(default=0.30, ge=0, le=1)
    fee_rate: float = Field(default=0.0003, ge=0, le=0.02)
    slippage_rate: float = Field(default=0.0005, ge=0, le=0.02)
    initial_capital: float = Field(default=100_000, gt=0)
    benchmark_symbol: str = Field(default="000300", min_length=6, max_length=16)

    @field_validator("sentiment_weight")
    @classmethod
    def validate_weights(cls, value: float, info):
        values = info.data
        total = values.get("momentum_weight", 0) + values.get("quality_weight", 0) + value
        if abs(total - 1.0) > 1e-6:
            raise ValueError("momentum_weight + quality_weight + sentiment_weight 必须等于 1")
        return value


class StrategyConfigPayload(BaseModel):
    name: str = Field(default="默认情绪行情双因子", min_length=1, max_length=120)
    description: str = "价格动量、财务质量与新闻情绪的教学型组合策略"
    enabled: bool = True
    watchlist: list[str]
    parameters: StrategyParameters = Field(default_factory=StrategyParameters)

    @field_validator("watchlist")
    @classmethod
    def normalize_symbols(cls, value: list[str]) -> list[str]:
        symbols = list(dict.fromkeys(symbol.strip() for symbol in value if symbol.strip()))
        if not symbols:
            raise ValueError("股票池不能为空")
        return symbols


class SyncRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    start_date: date | None = None
    end_date: date | None = None
    include_financials: bool = True
    include_news: bool = True
    include_notices: bool = True


class AnalyzeRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=500)
    force: bool = False


class ScoreRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    as_of: date | None = None


class BacktestRequest(BaseModel):
    name: str = "情绪行情双因子回测"
    symbols: list[str] = Field(default_factory=list)
    start_date: date
    end_date: date
    parameters: StrategyParameters = Field(default_factory=StrategyParameters)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, value: date, info):
        start = info.data.get("start_date")
        if start and value <= start:
            raise ValueError("end_date 必须晚于 start_date")
        return value


class TaskCreateRequest(BaseModel):
    task_type: str = Field(min_length=1, max_length=64)
    payload: dict = Field(default_factory=dict)
    priority: int = Field(default=100, ge=1, le=1000)
    max_attempts: int = Field(default=2, ge=1, le=5)


class WalkForwardRequest(BaseModel):
    name: str = "Walk-forward 样本外验证"
    symbols: list[str] = Field(default_factory=list)
    start_date: date
    end_date: date
    train_days: int = Field(default=126, ge=60, le=1000)
    test_days: int = Field(default=63, ge=20, le=250)
    momentum_windows: list[int] = Field(default_factory=lambda: [10, 20, 40])
    sentiment_thresholds: list[float] = Field(default_factory=lambda: [-0.2, 0.0, 0.2])
    parameters: StrategyParameters = Field(default_factory=StrategyParameters)

    @field_validator("end_date")
    @classmethod
    def validate_walk_forward_dates(cls, value: date, info):
        start = info.data.get("start_date")
        if start and value <= start:
            raise ValueError("end_date 必须晚于 start_date")
        return value

    @field_validator("momentum_windows")
    @classmethod
    def validate_momentum_windows(cls, value: list[int]) -> list[int]:
        values = sorted(set(value))
        if not values or any(item < 5 or item > 250 for item in values):
            raise ValueError("动量窗口必须在 5 到 250 之间")
        return values

    @field_validator("sentiment_thresholds")
    @classmethod
    def validate_sentiment_thresholds(cls, value: list[float]) -> list[float]:
        values = sorted(set(value))
        if not values or any(item < -1 or item > 1 for item in values):
            raise ValueError("舆情阈值必须在 -1 到 1 之间")
        return values


class InfrastructureSyncRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    benchmark_symbol: str = "000300"
    start_date: date | None = None
    end_date: date | None = None
    report_dates: list[date] = Field(default_factory=list)


class DataQualityRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    benchmark_symbol: str = "000300"


class LearningProgressPayload(BaseModel):
    completed: list[str] = Field(default_factory=list, max_length=500)
    quiz_scores: dict[str, int] = Field(default_factory=dict)

    @field_validator("completed")
    @classmethod
    def normalize_completed(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in value if item.strip()))

    @field_validator("quiz_scores")
    @classmethod
    def validate_quiz_scores(cls, value: dict[str, int]) -> dict[str, int]:
        if len(value) > 100:
            raise ValueError("测验成绩数量不能超过 100")
        normalized: dict[str, int] = {}
        for key, score in value.items():
            chapter_id = key.strip()
            if not chapter_id:
                raise ValueError("章节 ID 不能为空")
            if score < 0 or score > 100:
                raise ValueError("测验成绩必须在 0 到 100 之间")
            normalized[chapter_id] = score
        return normalized


class LearningProgressResponse(LearningProgressPayload):
    updated_at: datetime | None = None

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime | None) -> str | None:
        return utc_iso(value)


class AutomationSettingsPayload(BaseModel):
    news_analysis_enabled: bool = True
    news_analysis_interval_hours: int = Field(default=6, ge=1, le=48)


class AutomationSettingsResponse(AutomationSettingsPayload):
    next_run_at: datetime | None = None
    model: str
    thinking_enabled: bool
    reasoning_effort: str
    backup_key_configured: bool
    updated_at: datetime | None = None

    @field_serializer("next_run_at")
    def serialize_next_run_at(self, value: datetime | None) -> str | None:
        return beijing_iso(value)

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime | None) -> str | None:
        return utc_iso(value)
