"""跟练 02：把“看起来赚钱”拆成样本内、样本外、成本和基准。"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "02_hypothesis_results.csv"


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    results: dict[str, dict[str, float]] = {}
    for row in rows:
        net = float(row["gross_return"]) - float(row["turnover"]) * float(row["cost_rate"])
        excess = net - float(row["benchmark_return"])
        results.setdefault(row["experiment"], {})[row["period"]] = excess

    for name, periods in results.items():
        print(
            f"{name}: in_sample_excess={periods['in_sample']:.2%} "
            f"out_of_sample_excess={periods['out_of_sample']:.2%}"
        )
    assert results["random_rule"]["out_of_sample"] < 0
    print("lesson=样本内最好不等于样本外最好；先写失败条件再看结果")
    print("LAB_OK")


if __name__ == "__main__":
    main()
