from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


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
