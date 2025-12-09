# system_live/main.py

from __future__ import annotations

import argparse
from datetime import datetime
from time import sleep

from system.system_live.config import DEFAULT_CONFIG, SystemConfig
from system.system_live.execution.runner import run_once


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the system_live execution cycle."
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run continuously in a simple loop (not time-aligned).",
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=60 * 60,  # 1 hour default
        help="Loop interval in seconds when --loop is used.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config: SystemConfig = DEFAULT_CONFIG

    if not args.loop:
        print(f"[INFO] Running single cycle at {datetime.utcnow().isoformat()}Z")
        run_once(config)
    else:
        print(
            f"[INFO] Running in loop mode, interval={args.interval_seconds} seconds."
        )
        while True:
            print(f"[INFO] Loop tick at {datetime.utcnow().isoformat()}Z")
            run_once(config)
            sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
