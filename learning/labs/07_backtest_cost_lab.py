"""跟练 07：信号延迟一日执行，并从每次换仓中扣除成本。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path(__file__).parents[1] / "datasets" / "07_backtest_costs.csv"


def evaluate(cost_rate: float) -> tuple[float, float, float]:
    frame = pd.read_csv(DATA, parse_dates=["date"]).set_index("date")
    returns = frame["close"].pct_change(fill_method=None).fillna(0.0)
    position = frame["signal"].shift(1).fillna(0.0)
    turnover = position.diff().abs().fillna(position.abs())
    gross = position * returns
    net = gross - turnover * cost_rate
    return float((1 + gross).prod() - 1), float((1 + net).prod() - 1), float(turnover.sum())


def main() -> None:
    gross, net, turnover = evaluate(cost_rate=0.001)
    _, expensive_net, _ = evaluate(cost_rate=0.005)
    print(f"gross_return={gross:.2%} net_return={net:.2%} turnover={turnover:.1f}")
    print(f"net_return_when_cost_is_5x={expensive_net:.2%}")
    assert net < gross and expensive_net < net
    print("LAB_OK")


if __name__ == "__main__":
    main()
