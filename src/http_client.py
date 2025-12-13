import logging
import time
from typing import cast

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import ProxyConfig

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with retry logic, rate limiting, and proxy support."""

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
        rate_limit_delay: float = 1.0,
        proxy_config: ProxyConfig | None = None,
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_base: Base for exponential backoff (seconds)
            rate_limit_delay: Delay between requests in seconds
            proxy_config: Optional proxy configuration
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base
        self.rate_limit_delay = rate_limit_delay
        self.proxy_config = proxy_config
        self._last_request_time: float = 0.0

        proxies = self._convert_proxy_config_to_httpx(proxy_config)
        self._client = httpx.Client(
            proxy=cast("httpx.Proxy | None", proxies),
            timeout=timeout,
        )

    @staticmethod
    def _convert_proxy_config_to_httpx(
        proxy_config: ProxyConfig | None,
    ) -> dict[str, str] | None:
        """
        Convert ProxyConfig to httpx proxy format.

        Args:
            proxy_config: Proxy configuration to convert

        Returns:
            Dictionary with 'http://' and 'https://' keys,
            or None if no proxy configured
        """
        if not proxy_config:
            return None

        if not proxy_config.http_proxy and not proxy_config.https_proxy:
            return None

        proxies: dict[str, str] = {}
        if proxy_config.http_proxy:
            proxies["http://"] = proxy_config.http_proxy
        if proxy_config.https_proxy:
            proxies["https://"] = proxy_config.https_proxy

        return proxies if proxies else None

    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting by sleeping if necessary."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug("Rate limiting: sleeping for %.2f seconds", sleep_time)
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    @retry(
        retry=retry_if_exception_type(
            (httpx.NetworkError, httpx.TimeoutException, httpx.HTTPStatusError)
        ),
        stop=stop_after_attempt(4),  # 1 initial + 3 retries
        wait=wait_exponential(multiplier=2, min=1, max=60),
        reraise=True,
    )
    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        ignore_codes: list[int] | None = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic and rate limiting.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            ignore_codes: List of HTTP status codes to ignore (don't raise)
            **kwargs: Additional arguments passed to httpx request

        Returns:
            httpx.Response object
        """
        self._enforce_rate_limit()

        response = self._client.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs,
        )

        if ignore_codes and response.status_code in ignore_codes:
            return response

        response.raise_for_status()

        return response
