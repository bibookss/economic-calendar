from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProxyConfig:
    """HTTP proxy configuration."""

    http_proxy: str | None = None
    https_proxy: str | None = None


