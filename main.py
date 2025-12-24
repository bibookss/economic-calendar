import argparse
from datetime import datetime
from logging.config import fileConfig
from pathlib import Path

import yaml

from src.worker_factory import build_worker


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    with config_path.open(encoding="utf-8") as file:
        config_data = yaml.safe_load(file)
    return config_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Economic calendar worker")
    parser.add_argument(
        "-s",
        "--start-date",
        type=str,
        required=True,
        help="Start date in YYYYMMDD format",
    )
    parser.add_argument(
        "-e",
        "--end-date",
        type=str,
        required=True,
        help="End date in YYYYMMDD format",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="raw",
        help="Worker mode (default: raw)",
    )

    args = parser.parse_args()

    config_path = Path("config/fxstreet.yaml")
    log_config_path = Path("config/log.conf")

    fileConfig(log_config_path)

    config_data = load_config(config_path)
    worker = build_worker(config_data)
    start_date = datetime.strptime(args.start_date, "%Y%m%d").date()
    end_date = datetime.strptime(args.end_date, "%Y%m%d").date()
    worker.run(start_date, end_date, mode=args.mode)


if __name__ == "__main__":
    main()
