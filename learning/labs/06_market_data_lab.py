"""跟练 06：区分原始价格、复权价格、报告期和真正可得日。"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "06_market_data.csv"


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    raw_return = float(rows[2]["raw_close"]) / float(rows[1]["raw_close"]) - 1
    adjusted = [float(row["raw_close"]) * float(row["adjustment_factor"]) for row in rows]
    adjusted_return = adjusted[2] / adjusted[1] - 1

    score_date = date.fromisoformat("2026-03-30")
    usable = [row for row in rows if date.fromisoformat(row["available_at"]) <= score_date]
    latest_roe = float(usable[-1]["roe"])
    print(f"raw_return_on_action_day={raw_return:.2%}")
    print(f"adjusted_return_on_action_day={adjusted_return:.2%}")
    print(f"roe_available_on_{score_date}={latest_roe:.3f}")
    assert raw_return < -0.45 and abs(adjusted_return - 0.0098) < 0.001
    assert latest_roe == 0.112
    print("LAB_OK")


if __name__ == "__main__":
    main()
