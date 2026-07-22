"""跟练 01：读取 OHLCV，验证 K 线关系并计算复利收益。"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "01_market_basics.csv"


def load_rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def valid_ohlc(row: dict[str, str]) -> bool:
    open_price, high = float(row["open"]), float(row["high"])
    low, close = float(row["low"]), float(row["close"])
    return 0 < low <= min(open_price, close) <= max(open_price, close) <= high


def main() -> None:
    rows = load_rows()
    assert rows and all(valid_ohlc(row) for row in rows)
    daily_returns = [float(row["close"]) / float(row["prev_close"]) - 1 for row in rows]
    cumulative = 1.0
    for daily_return in daily_returns:
        cumulative *= 1 + daily_return

    first = rows[0]
    direction = "阳线" if float(first["close"]) >= float(first["open"]) else "阴线"
    print(f"rows={len(rows)} first_candle={direction}")
    print("daily_returns=", [f"{value:.2%}" for value in daily_returns])
    print(f"compounded_return={cumulative - 1:.2%}")
    print("LAB_OK")


if __name__ == "__main__":
    main()
