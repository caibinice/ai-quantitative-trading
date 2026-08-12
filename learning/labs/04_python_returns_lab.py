"""跟练 04：用函数、列表与类型提示实现收益和最大回撤。"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "04_python_returns.csv"


def simple_returns(prices: list[float]) -> list[float]:
    return [current / previous - 1 for previous, current in zip(prices, prices[1:])]


def equity_curve(returns: list[float], initial: float = 100_000) -> list[float]:
    curve = [initial]
    for value in returns:
        curve.append(curve[-1] * (1 + value))
    return curve


def maximum_drawdown(curve: list[float]) -> float:
    peak, worst = curve[0], 0.0
    for value in curve:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return worst


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        prices = [float(row["close"]) for row in csv.DictReader(file)]
    returns = simple_returns(prices)
    curve = equity_curve(returns)
    print(f"observations={len(prices)} final_equity={curve[-1]:.2f}")
    print(f"maximum_drawdown={maximum_drawdown(curve):.2%}")
    assert round(curve[-1], 2) == 108000.00
    print("LAB_OK")


if __name__ == "__main__":
    main()
