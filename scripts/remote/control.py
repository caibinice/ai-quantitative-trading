from __future__ import annotations

import argparse

from remote_client import RemoteClient

APP_ROOT = "/opt/ai-quantitative-trading"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=["start", "restart", "stop", "status", "resources"],
    )
    args = parser.parse_args()

    remote = RemoteClient()
    try:
        remote.run(
            f"/bin/bash {APP_ROOT}/current/deploy/remote/control.sh {args.action}",
            root=True,
            timeout=180,
        )
    finally:
        remote.close()


if __name__ == "__main__":
    main()
