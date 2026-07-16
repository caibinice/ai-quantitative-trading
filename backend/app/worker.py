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


def run_worker(poll_seconds: float = 2.0, once: bool = False) -> None:
    create_tables()
    worker_id = f"{socket.gethostname()}:{os.getpid()}"
    while running:
        with SessionLocal() as db:
            task = claim_next_task(db, worker_id)
            if task:
                execute_task(db, task.id)
        if once:
            return
        if task is None:
            time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 量化研究任务 Worker")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    run_worker(args.poll_seconds, args.once)


if __name__ == "__main__":
    main()
