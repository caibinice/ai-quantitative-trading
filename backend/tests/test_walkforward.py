from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from app.schemas import StrategyParameters, WalkForwardRequest
from app.services.walkforward import run_walk_forward


def test_walk_forward_curve_contains_only_test_windows() -> None:
    dates = pd.bdate_range("2024-01-02", periods=240)
    price_frames = {
        f"00000{index}": pd.Series(
            10 * np.exp(np.cumsum(np.full(len(dates), 0.0005 + index * 0.0001))),
            index=dates,
        )
        for index in range(1, 4)
    }
    benchmark = pd.Series(3000 * np.exp(np.cumsum(np.full(len(dates), 0.0003))), index=dates)
    request = WalkForwardRequest(
        symbols=list(price_frames),
        start_date=date(2024, 1, 2),
        end_date=dates[-1].date(),
        train_days=80,
        test_days=40,
        momentum_windows=[10, 20],
        sentiment_thresholds=[-1.0, 0.0],
        parameters=StrategyParameters(
            momentum_weight=0.7,
            quality_weight=0.0,
            sentiment_weight=0.3,
        ),
    )
    result = run_walk_forward(
        price_frames,
        {symbol: [] for symbol in price_frames},
        benchmark,
        request,
    )

    assert len(result["windows"]) == 4
    assert result["equity_curve"][0]["date"] == dates[80].date().isoformat()
    assert all(window["test_start"] > window["train_start"] for window in result["windows"])
