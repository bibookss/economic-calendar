from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProxyConfig:
    """HTTP proxy configuration."""

    http_proxy: str | None = None
    https_proxy: str | None = None


@dataclass(frozen=True, slots=True)
class S3Config:
    """S3-compatible storage configuration (MinIO)."""

    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    use_ssl: bool = False
    region: str = "us-east-1"


@dataclass(frozen=True, slots=True)
class FXStreetConfig:
    """FXStreet configuration."""

    http_client: "HTTPClient"
    s3_config: S3Config
    raw_output_name_template: str = "fxstreet/events/{start_date}_{end_date}.json"
