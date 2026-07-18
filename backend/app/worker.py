from __future__ import annotations

import argparse
import os
import signal
import socket
import time

from app.core.database import SessionLocal, create_tables
from app.services.task_queue import claim_next_task, execute_task

running = True


def _stop(*_args) -> None:
    global running
    running = False


def run_worker(
    poll_seconds: float = 2.0,
    once: bool = False,
    idle_exit_seconds: float | None = None,
) -> None:
    create_tables()
    worker_id = f"{socket.gethostname()}:{os.getpid()}"
    idle_since = time.monotonic()
    processed_task = False
    while running:
        with SessionLocal() as db:
            task = claim_next_task(db, worker_id)
            if task:
                execute_task(db, task.id)
                idle_since = time.monotonic()
                processed_task = True
        if once:
            return
        if task is None:
            if (
                idle_exit_seconds is not None
                and processed_task
                and time.monotonic() - idle_since >= idle_exit_seconds
            ):
                return
            time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 量化研究任务 Worker")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    parser.add_argument(
        "--idle-exit-seconds",
        type=float,
        default=None,
        help="连续空闲指定秒数后退出，适合由 systemd timer 按需拉起。",
    )
    args = parser.parse_args()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    run_worker(args.poll_seconds, args.once, args.idle_exit_seconds)


if __name__ == "__main__":
    main()
