from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.router import rankings, stocks
from app.core.database import Base
from app.models import FactorScore, Stock, StrategyConfig
from app.schemas import StrategyParameters


def test_stocks_and_rankings_follow_the_configured_watchlist() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    parameters = StrategyParameters().model_dump()
    with Session(engine, expire_on_commit=False) as db:
        db.add_all(
            [
                Stock(symbol="000001", name="平安银行"),
                Stock(symbol="600519", name="贵州茅台"),
                Stock(symbol="300750", name="宁德时代"),
                StrategyConfig(
                    name="默认情绪行情双因子",
                    watchlist=["300750", "000001"],
                    parameters=parameters,
                ),
                FactorScore(
                    symbol="000001",
                    score_date=date(2026, 7, 20),
                    momentum_score=50,
                    quality_score=50,
                    sentiment_score=50,
                    total_score=50,
                ),
                FactorScore(
                    symbol="600519",
                    score_date=date(2026, 7, 20),
                    momentum_score=99,
                    quality_score=99,
                    sentiment_score=99,
                    total_score=99,
                ),
            ]
        )
        db.commit()

        stock_rows = stocks(search="", scope="watchlist", limit=200, db=db)
        ranking_rows = rankings(db=db)

        assert [item["symbol"] for item in stock_rows] == ["300750", "000001"]
        assert [item["symbol"] for item in ranking_rows["items"]] == ["000001"]
