"""跟练 08：过滤未来事件、合并 72 小时转载并计算置信度加权情绪。"""

from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "08_sentiment_events.csv"
AS_OF = datetime.fromisoformat("2026-05-10T00:00:00+08:00")


def canonical_event(title: str) -> str:
    if "业绩预增" in title:
        return "业绩预增"
    return title


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    usable = [row for row in rows if datetime.fromisoformat(row["published_at"]) <= AS_OF]
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for row in usable:
        key = (row["symbol"], canonical_event(row["title"]))
        first = unique.get(key)
        if first is None:
            unique[key] = row
            continue
        gap = abs(
            datetime.fromisoformat(row["published_at"])
            - datetime.fromisoformat(first["published_at"])
        )
        if gap.total_seconds() > 72 * 3600:
            unique[(row["symbol"], row["title"])] = row

    weighted_sum = total_weight = 0.0
    for row in unique.values():
        age = (AS_OF - datetime.fromisoformat(row["published_at"])).total_seconds() / 86400
        weight = float(row["confidence"]) * math.exp(-math.log(2) * age / 7)
        weighted_sum += float(row["score"]) * weight
        total_weight += weight
    print(f"raw_events={len(rows)} usable={len(usable)} unique={len(unique)}")
    print(f"weighted_sentiment={weighted_sum / total_weight:.4f}")
    assert len(rows) == 7 and len(usable) == 6 and len(unique) == 4
    print("LAB_OK")


if __name__ == "__main__":
    main()
