"""跟练 10：让质量规则给出证据，而不是只返回“数据有问题”。"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "10_data_quality_cases.csv"


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    date_counts = Counter(row["date"] for row in rows)
    duplicate_dates = sorted(date for date, count in date_counts.items() if count > 1)
    invalid_ohlc = []
    negative_volume = []
    extreme_returns = []
    previous_close: float | None = None
    for row in rows:
        open_price, high = float(row["open"]), float(row["high"])
        low, close = float(row["low"]), float(row["close"])
        if not (low <= min(open_price, close) <= max(open_price, close) <= high):
            invalid_ohlc.append(row["row_id"])
        if float(row["volume"]) < 0:
            negative_volume.append(row["row_id"])
        if previous_close and abs(close / previous_close - 1) > 0.25:
            extreme_returns.append(row["row_id"])
        previous_close = close
    print(f"duplicate_dates={duplicate_dates}")
    print(f"invalid_ohlc_rows={invalid_ohlc} negative_volume_rows={negative_volume}")
    print(f"extreme_return_rows={extreme_returns}")
    assert duplicate_dates and invalid_ohlc == ["4"] and negative_volume == ["5"]
    print("LAB_OK")


if __name__ == "__main__":
    main()
