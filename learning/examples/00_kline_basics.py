"""股票与 K 线零基础：检查 OHLC 关系并计算收益。"""

bars = [
    {"date": "day-1", "open": 10.20, "high": 10.80, "low": 9.90, "close": 10.50},
    {"date": "day-2", "open": 10.45, "high": 10.60, "low": 10.20, "close": 10.29},
]


def valid_ohlc(bar: dict[str, float | str]) -> bool:
    open_price = float(bar["open"])
    high = float(bar["high"])
    low = float(bar["low"])
    close = float(bar["close"])
    return 0 < low <= min(open_price, close) <= max(open_price, close) <= high


for bar in bars:
    assert valid_ohlc(bar), f"OHLC 关系异常: {bar}"
    direction = "上涨 K 线" if bar["close"] >= bar["open"] else "下跌 K 线"
    print(bar["date"], direction, bar)

day_two_return = float(bars[1]["close"]) / float(bars[0]["close"]) - 1
print(f"第二天收盘收益: {day_two_return:.2%}")

start_price = 100.0
final_price = start_price * 1.10 * 0.90
print(f"100 元先涨 10% 再跌 10%: {final_price:.2f} 元")
