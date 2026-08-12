"""pandas time series: alignment, rolling indicators, and missing dates."""

from __future__ import annotations

import math

import pandas as pd


def main() -> None:
    calendar = pd.bdate_range("2026-01-05", periods=8)
    observed_dates = calendar.delete(4)
    prices = pd.Series(
        [100.0, 101.5, 100.8, 103.2, 104.1, 102.7, 105.4],
        index=observed_dates,
        name="close",
    )
    aligned = prices.reindex(calendar)
    missing_dates = aligned[aligned.isna()].index.strftime("%Y-%m-%d").tolist()
    returns = prices.pct_change(fill_method=None)
    momentum = prices / prices.shift(3) - 1
    volatility = returns.std(ddof=1) * math.sqrt(252)

    print(pd.DataFrame({"close": prices, "return": returns, "momentum_3d": momentum}).round(4))
    print("missing trading dates:", missing_dates)
    print("annualized volatility:", f"{volatility:.2%}")
    print("DEMO_OK")


if __name__ == "__main__":
    main()
