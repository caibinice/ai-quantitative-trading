"""跟练 11：用事先写好的门槛评审实验，不按心情挑最好看的曲线。"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "11_capstone_experiments.csv"


def passes(row: dict[str, str]) -> bool:
    return (
        float(row["oos_return"]) > 0
        and float(row["max_drawdown"]) >= -0.15
        and float(row["turnover"]) <= 4.0
    )


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        status = "PASS" if passes(row) else "REVIEW"
        print(f"{row['experiment_id']} {row['version']} status={status} decision={row['decision']}")
    passing = [row["experiment_id"] for row in rows if passes(row)]
    print(f"passing_experiments={passing}")
    assert passing == ["EXP-002", "EXP-004"]
    print("LAB_OK")


if __name__ == "__main__":
    main()
