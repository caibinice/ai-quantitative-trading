"""A minimal walk-forward experiment that reports test windows only."""

from __future__ import annotations

import numpy as np
import pandas as pd


def strategy_returns(prices: pd.Series, window: int) -> pd.Series:
    signal = (prices > prices.rolling(window).mean()).astype(float).shift(1).fillna(0.0)
    return signal * prices.pct_change(fill_method=None).fillna(0.0)


def compounded_return(returns: pd.Series) -> float:
    return float((1 + returns).prod() - 1)


def main() -> None:
    dates = pd.bdate_range("2025-01-02", periods=240)
    regime = np.concatenate([
        np.full(80, 0.0010),
        np.full(80, -0.0004),
        np.full(80, 0.0007),
    ])
    noise = np.sin(np.arange(240) / 4) * 0.003
    prices = pd.Series(100 * np.exp(np.cumsum(regime + noise)), index=dates)
    candidates = [5, 10, 20]
    train_days = 80
    test_days = 40
    out_of_sample: list[pd.Series] = []

    start = 0
    while start + train_days + test_days <= len(prices):
        train_slice = slice(start, start + train_days)
        test_slice = slice(start + train_days, start + train_days + test_days)
        all_candidate_returns = {
            window: strategy_returns(prices, window) for window in candidates
        }
        best_window = max(
            candidates,
            key=lambda window: compounded_return(all_candidate_returns[window].iloc[train_slice]),
        )
        test_returns = all_candidate_returns[best_window].iloc[test_slice]
        out_of_sample.append(test_returns)
        print(
            f"train={dates[train_slice.start].date()}..{dates[train_slice.stop - 1].date()} "
            f"test={dates[test_slice.start].date()}..{dates[test_slice.stop - 1].date()} "
            f"window={best_window} oos={compounded_return(test_returns):.2%}"
        )
        start += test_days

    stitched = pd.concat(out_of_sample)
    print("out-of-sample points:", len(stitched))
    print("stitched out-of-sample return:", f"{compounded_return(stitched):.2%}")
    print("DEMO_OK")


if __name__ == "__main__":
    main()
