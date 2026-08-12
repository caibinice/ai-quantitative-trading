"""跟练 03：用事件日志理解 queued -> running -> success 与失败重试。"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parents[1] / "datasets" / "03_task_lifecycle.csv"
ALLOWED = {
    "queued": {"queued", "running"},
    "running": {"running", "queued", "success", "failed"},
    "success": set(),
    "failed": {"queued"},
}


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    histories: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        histories[row["task_id"]].append(row)

    for task_id, events in histories.items():
        statuses = [event["status"] for event in events]
        for previous, current in zip(statuses, statuses[1:]):
            assert current in ALLOWED[previous], f"非法状态迁移: {previous} -> {current}"
        print(
            f"task={task_id} events={len(events)} final={statuses[-1]} "
            f"attempts={events[-1]['attempt']}"
        )
    print("lesson=HTTP 返回任务号不等于后台任务已经成功")
    print("LAB_OK")


if __name__ == "__main__":
    main()
