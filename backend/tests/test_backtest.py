from __future__ import annotations

import pandas as pd

from app.schemas import StrategyParameters
from app.services.backtest import run_dual_factor_backtest


def _prices(values: list[float]) -> dict[str, pd.Series]:
    dates = pd.bdate_range("2025-01-02", periods=len(values))
    return {"000001": pd.Series(values, index=dates, dtype=float)}


def _parameters(**overrides) -> StrategyParameters:
    values = {
        "momentum_window": 5,
        "sentiment_threshold": -1,
        "minimum_momentum": -1,
        "top_n": 1,
        "momentum_weight": 0.7,
        "quality_weight": 0.0,
        "sentiment_weight": 0.3,
        "fee_rate": 0,
        "slippage_rate": 0,
    }
    values.update(overrides)
    return StrategyParameters(**values)


def test_signal_is_delayed_one_bar() -> None:
    result = run_dual_factor_backtest(
        _prices([10, 11, 12, 13, 14, 15, 16, 17]), {"000001": []}, _parameters()
    )
    weights = result["weights"]["000001"]

    # The first valid 5-day momentum exists on bar 6, but cannot be held until bar 7.
    assert weights.iloc[5] == 0
    assert weights.iloc[6] == 1


def test_transaction_costs_reduce_equity() -> None:
    no_cost = run_dual_factor_backtest(
        _prices([10, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7]),
        {"000001": []},
        _parameters(),
    )
    with_cost = run_dual_factor_backtest(
        _prices([10, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7]),
        {"000001": []},
        _parameters(fee_rate=0.005, slippage_rate=0.005),
    )

    assert with_cost["equity_curve"][-1]["equity"] < no_cost["equity_curve"][-1]["equity"]
    assert with_cost["metrics"]["turnover"] > 0


def test_future_sentiment_does_not_enter_earlier_dates() -> None:
    dates = pd.bdate_range("2025-01-02", periods=10)
    result = run_dual_factor_backtest(
        {"000001": pd.Series(range(10, 20), index=dates, dtype=float)},
        {"000001": [(dates[-1], 1.0)]},
        _parameters(sentiment_threshold=0.5),
    )

    # The only positive event arrives on the final date, whose signal would apply after the sample.
    assert result["weights"]["000001"].sum() == 0


def test_explicit_index_replaces_equal_weight_benchmark() -> None:
    dates = pd.bdate_range("2025-01-02", periods=8)
    index_prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 108], index=dates)
    result = run_dual_factor_backtest(
        {"000001": pd.Series([10] * 8, index=dates, dtype=float)},
        {"000001": []},
        _parameters(),
        index_prices,
    )

    assert result["metrics"]["benchmark_return"] == 0.08
