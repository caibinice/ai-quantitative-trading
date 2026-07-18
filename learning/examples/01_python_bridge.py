"""Hello Quant: plain Python returns, compounding, and drawdown."""

from __future__ import annotations


def simple_returns(prices: list[float]) -> list[float]:
    if len(prices) < 2:
        return []
    return [
        current / previous - 1
        for previous, current in zip(prices, prices[1:])
    ]


def equity_curve(returns: list[float], initial_capital: float = 100_000) -> list[float]:
    curve = [initial_capital]
    for daily_return in returns:
        curve.append(curve[-1] * (1 + daily_return))
    return curve


def maximum_drawdown(curve: list[float]) -> float:
    peak = curve[0]
    worst = 0.0
    for value in curve:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return worst


def main() -> None:
    prices = [100.0, 102.0, 99.0, 105.0]
    returns = simple_returns(prices)
    curve = equity_curve(returns)
    print("prices:", prices)
    print("returns:", [round(value, 4) for value in returns])
    print("final equity:", round(curve[-1], 2))
    print("maximum drawdown:", f"{maximum_drawdown(curve):.2%}")
    print("DEMO_OK")


if __name__ == "__main__":
    main()
