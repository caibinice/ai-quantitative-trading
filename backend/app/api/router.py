from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import (
    BacktestRun,
    DailyPrice,
    FactorScore,
    FinancialMetric,
    JobRun,
    NewsItem,
    SentimentAnalysis,
    Stock,
    StrategyConfig,
)
from app.schemas import (
    AnalyzeRequest,
    BacktestRequest,
    ScoreRequest,
    StrategyConfigPayload,
    SyncRequest,
)
from app.services.backtest import run_backtest_from_db
from app.services.pipeline import sync_market_data
from app.services.scoring import calculate_scores
from app.services.sentiment import SentimentAnalyzer

router = APIRouter()


def _strategy_payload(item: StrategyConfig) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "enabled": item.enabled,
        "watchlist": item.watchlist,
        "parameters": item.parameters,
        "updated_at": item.updated_at,
    }


def _default_strategy(db: Session) -> StrategyConfig:
    item = db.scalar(select(StrategyConfig).where(StrategyConfig.name == "默认情绪行情双因子"))
    if item is None:
        settings = get_settings()
        payload = StrategyConfigPayload(watchlist=settings.watchlist)
        item = StrategyConfig(
            name=payload.name,
            description=payload.description,
            enabled=True,
            watchlist=payload.watchlist,
            parameters=payload.parameters.model_dump(),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    counts = {
        "stocks": db.scalar(select(func.count()).select_from(Stock)) or 0,
        "price_rows": db.scalar(select(func.count()).select_from(DailyPrice)) or 0,
        "news": db.scalar(select(func.count()).select_from(NewsItem)) or 0,
        "analyzed": db.scalar(select(func.count()).select_from(SentimentAnalysis)) or 0,
    }
    latest_score_date = db.scalar(select(func.max(FactorScore.score_date)))
    top_scores = []
    if latest_score_date:
        rows = db.execute(
            select(FactorScore, Stock.name)
            .join(Stock, Stock.symbol == FactorScore.symbol)
            .where(FactorScore.score_date == latest_score_date)
            .order_by(FactorScore.total_score.desc())
            .limit(5)
        ).all()
        top_scores = [
            {
                "symbol": score.symbol,
                "name": name,
                "total_score": score.total_score,
                "sentiment_score": score.sentiment_score,
            }
            for score, name in rows
        ]
    sentiment_stats = dict(
        db.execute(
            select(SentimentAnalysis.label, func.count())
            .group_by(SentimentAnalysis.label)
        ).all()
    )
    latest_job = db.scalar(select(JobRun).order_by(JobRun.started_at.desc()).limit(1))
    return {
        "counts": counts,
        "latest_score_date": latest_score_date,
        "top_scores": top_scores,
        "sentiment_stats": sentiment_stats,
        "latest_job": (
            {
                "job_type": latest_job.job_type,
                "status": latest_job.status,
                "message": latest_job.message,
                "started_at": latest_job.started_at,
            }
            if latest_job
            else None
        ),
    }


@router.get("/stocks")
def stocks(
    search: str = "", limit: int = Query(default=200, ge=1, le=2000), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    query = select(Stock).where(Stock.is_active.is_(True)).order_by(Stock.symbol)
    if search:
        query = query.where((Stock.symbol.contains(search)) | (Stock.name.contains(search)))
    return [
        {"symbol": item.symbol, "name": item.name, "market": item.market, "industry": item.industry}
        for item in db.scalars(query.limit(limit)).all()
    ]


@router.get("/market/{symbol}/prices")
def market_prices(
    symbol: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    end_date = end_date or date.today()
    start_date = start_date or end_date - timedelta(days=365)
    rows = db.scalars(
        select(DailyPrice)
        .where(
            DailyPrice.symbol == symbol,
            DailyPrice.trade_date >= start_date,
            DailyPrice.trade_date <= end_date,
        )
        .order_by(DailyPrice.trade_date)
    ).all()
    return [
        {
            "date": row.trade_date,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
            "amount": row.amount,
            "turnover_rate": row.turnover_rate,
        }
        for row in rows
    ]


@router.get("/market/{symbol}/financials")
def market_financials(
    symbol: str, limit: int = Query(default=200, ge=1, le=1000), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(FinancialMetric)
        .where(FinancialMetric.symbol == symbol)
        .order_by(FinancialMetric.report_date.desc(), FinancialMetric.metric_name)
        .limit(limit)
    ).all()
    return [
        {
            "report_date": row.report_date,
            "report_period": row.report_period,
            "metric_name": row.metric_name,
            "metric_value": row.metric_value,
            "yoy": row.yoy,
        }
        for row in rows
    ]


@router.get("/sentiment/news")
def sentiment_news(
    symbol: str = "",
    kind: str = "",
    label: str = "",
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = (
        select(NewsItem, SentimentAnalysis)
        .outerjoin(SentimentAnalysis, SentimentAnalysis.news_id == NewsItem.id)
        .order_by(NewsItem.published_at.desc())
    )
    if symbol:
        query = query.where(NewsItem.symbol == symbol)
    if kind:
        query = query.where(NewsItem.kind == kind)
    if label:
        query = query.where(SentimentAnalysis.label == label)
    rows = db.execute(query.limit(limit)).all()
    return [
        {
            "id": item.id,
            "symbol": item.symbol,
            "kind": item.kind,
            "title": item.title,
            "source": item.source,
            "source_url": item.source_url,
            "published_at": item.published_at,
            "label": analysis.label if analysis else "待分析",
            "score": analysis.score if analysis else None,
            "confidence": analysis.confidence if analysis else None,
            "summary": analysis.summary if analysis else "",
            "rationale": analysis.rationale if analysis else "",
            "model": analysis.model if analysis else "",
        }
        for item, analysis in rows
    ]


@router.get("/rankings")
def rankings(as_of: date | None = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    score_date = as_of or db.scalar(select(func.max(FactorScore.score_date)))
    if score_date is None:
        return {"score_date": None, "items": []}
    rows = db.execute(
        select(FactorScore, Stock.name)
        .join(Stock, Stock.symbol == FactorScore.symbol)
        .where(FactorScore.score_date == score_date)
        .order_by(desc(FactorScore.total_score))
    ).all()
    return {
        "score_date": score_date,
        "items": [
            {
                "rank": index,
                "symbol": item.symbol,
                "name": name,
                "momentum_score": item.momentum_score,
                "quality_score": item.quality_score,
                "sentiment_score": item.sentiment_score,
                "total_score": item.total_score,
                "explanation": item.explanation,
            }
            for index, (item, name) in enumerate(rows, 1)
        ],
    }


@router.get("/strategy")
def get_strategy(db: Session = Depends(get_db)) -> dict[str, Any]:
    return _strategy_payload(_default_strategy(db))


@router.put("/strategy")
def update_strategy(
    payload: StrategyConfigPayload, db: Session = Depends(get_db)
) -> dict[str, Any]:
    item = db.scalar(select(StrategyConfig).where(StrategyConfig.name == payload.name))
    if item is None:
        item = StrategyConfig(name=payload.name)
    item.description = payload.description
    item.enabled = payload.enabled
    item.watchlist = payload.watchlist
    item.parameters = payload.parameters.model_dump()
    db.add(item)
    db.commit()
    db.refresh(item)
    return _strategy_payload(item)


@router.post("/pipeline/sync", status_code=status.HTTP_200_OK)
def sync_pipeline(payload: SyncRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    strategy = _default_strategy(db)
    symbols = payload.symbols or strategy.watchlist
    end_date = payload.end_date or date.today()
    start_date = payload.start_date or end_date - timedelta(days=400)
    return sync_market_data(
        db,
        symbols,
        start_date,
        end_date,
        payload.include_financials,
        payload.include_news,
        payload.include_notices,
    )


@router.post("/pipeline/analyze")
def analyze_pipeline(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> dict[str, int]:
    count = SentimentAnalyzer().analyze_pending(db, payload.limit, payload.force)
    return {"analyzed": count}


@router.post("/rankings/recompute")
def recompute_rankings(payload: ScoreRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    strategy = _default_strategy(db)
    config = StrategyConfigPayload(
        name=strategy.name,
        description=strategy.description,
        enabled=strategy.enabled,
        watchlist=strategy.watchlist,
        parameters=strategy.parameters,
    )
    symbols = payload.symbols or config.watchlist
    as_of = payload.as_of or date.today()
    items = calculate_scores(db, symbols, as_of, config.parameters)
    return {"score_date": as_of, "count": len(items)}


@router.post("/backtests")
def create_backtest(payload: BacktestRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not payload.symbols:
        payload.symbols = _default_strategy(db).watchlist
    try:
        run = run_backtest_from_db(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "id": run.id,
        "name": run.name,
        "start_date": run.start_date,
        "end_date": run.end_date,
        "metrics": run.metrics,
        "equity_curve": run.equity_curve,
        "parameters": run.parameters,
        "created_at": run.created_at,
    }


@router.get("/backtests")
def list_backtests(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(select(BacktestRun).order_by(BacktestRun.created_at.desc()).limit(20)).all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "start_date": item.start_date,
            "end_date": item.end_date,
            "metrics": item.metrics,
            "created_at": item.created_at,
        }
        for item in rows
    ]


@router.get("/backtests/{run_id}")
def get_backtest(run_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    item = db.get(BacktestRun, run_id)
    if item is None:
        raise HTTPException(status_code=404, detail="回测记录不存在")
    return {
        "id": item.id,
        "name": item.name,
        "start_date": item.start_date,
        "end_date": item.end_date,
        "parameters": item.parameters,
        "metrics": item.metrics,
        "equity_curve": item.equity_curve,
        "created_at": item.created_at,
    }


@router.get("/jobs")
def jobs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(select(JobRun).order_by(JobRun.started_at.desc()).limit(50)).all()
    return [
        {
            "id": item.id,
            "job_type": item.job_type,
            "status": item.status,
            "message": item.message,
            "details": item.details,
            "started_at": item.started_at,
            "finished_at": item.finished_at,
        }
        for item in rows
    ]
