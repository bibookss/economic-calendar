from collections.abc import Callable, Mapping
from datetime import date
from typing import Any, Protocol

from src.config import FXStreetConfig, ProxyConfig, S3Config
from src.http_client import HTTPClient
from src.workers import FXStreetWorker


class Worker(Protocol):
    def run(self, start_date: date, end_date: date, mode: str) -> None: ...


def _build_fxstreet_worker(config_data: Mapping[str, Any]) -> Worker:
    """Build FXStreet worker from configuration dictionary."""

    proxy_url = config_data.get("proxy_url")
    proxy_config = (
        ProxyConfig(http_proxy=proxy_url, https_proxy=proxy_url) if proxy_url else None
    )

    http_cfg = config_data["http"]
    http_client = HTTPClient(
        timeout=http_cfg["timeout"],
        max_retries=http_cfg["max_retries"],
        retry_backoff_base=http_cfg["retry_backoff_base"],
        rate_limit_delay=http_cfg["rate_limit_delay"],
        proxy_config=proxy_config,
    )

    s3_cfg = config_data["s3"]
    s3_config = S3Config(
        endpoint=s3_cfg["endpoint"],
        access_key=s3_cfg["access_key"],
        secret_key=s3_cfg["secret_key"],
        bucket_name=s3_cfg["bucket_name"],
        use_ssl=s3_cfg.get("use_ssl", False),
        region=s3_cfg.get("region", "us-east-1"),
    )

    fxstreet_config = FXStreetConfig(
        http_client=http_client,
        s3_config=s3_config,
        raw_output_name_template=config_data["raw_output_name_template"],
    )

    return FXStreetWorker(fxstreet_config)


WORKER_MAPPING: dict[str, Callable[[Mapping[str, Any]], Worker]] = {
    "fxstreet": _build_fxstreet_worker,
}


def build_worker(config_data: Mapping[str, Any]) -> Worker:
    """Build worker from configuration dictionary."""

    worker_name = config_data.get("worker")
    if not isinstance(worker_name, str):
        msg = "`worker` must be a string"
        raise TypeError(msg)

    builder = WORKER_MAPPING.get(worker_name)
    if builder is None:
        msg = f"Unknown worker: {worker_name}"
        raise ValueError(msg)

    return builder(config_data)
