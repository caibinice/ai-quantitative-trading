"""跟练 09：只拼接每个窗口的测试段，绝不把训练收益放进最终成绩。"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "09_walk_forward_windows.csv"


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    tests = [row for row in rows if row["phase"] == "test"]
    compounded = 1.0
    winning_windows = 0
    for row in tests:
        strategy = float(row["strategy_return"])
        benchmark = float(row["benchmark_return"])
        compounded *= 1 + strategy
        winning_windows += strategy > benchmark
        print(
            f"window={row['window']} test={row['start_date']}..{row['end_date']} "
            f"strategy={strategy:.2%} benchmark={benchmark:.2%}"
        )
    print(f"stitched_oos_return={compounded - 1:.2%} winning_windows={winning_windows}/{len(tests)}")
    assert len(tests) == 4
    print("LAB_OK")


if __name__ == "__main__":
    main()
