import json
import logging
from datetime import date

import boto3
from botocore.exceptions import ClientError

from src.config import FXStreetConfig
from src.resources.fxstreet import FXStreetResource

logger = logging.getLogger("root")


class FXStreetWorker:
    def __init__(self, fxstreet_config: FXStreetConfig) -> None:
        self.fxstreet_config = fxstreet_config
        self.fxstreet_resource = FXStreetResource(fxstreet_config.http_client)
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=fxstreet_config.s3_config.endpoint,
            aws_access_key_id=fxstreet_config.s3_config.access_key,
            aws_secret_access_key=fxstreet_config.s3_config.secret_key,
            use_ssl=fxstreet_config.s3_config.use_ssl,
        )

        self._create_bucket()

    def run(self, start_date: date, end_date: date, mode: str = "raw") -> None:
        if mode == "raw":
            self._run_raw(start_date, end_date)
        else:
            msg = f"Invalid mode: {mode}"
            raise ValueError(msg)

    def _run_raw(self, start_date: date, end_date: date) -> None:
        logger.info(
            "Running FXStreet raw mode worker for %s to %s ...", start_date, end_date
        )
        events = self.fxstreet_resource.get_calendar_events(start_date, end_date)

        logger.info(
            "Uploading events to S3 bucket %s ...",
            self.fxstreet_config.s3_config.bucket_name,
        )

        key = self.fxstreet_config.raw_output_name_template.format(
            start_date=start_date,
            end_date=end_date,
        )
        self.s3_client.put_object(
            Bucket=self.fxstreet_config.s3_config.bucket_name,
            Key=key,
            Body=json.dumps(events).encode("utf-8"),
        )

        logger.info("Job completed successfully")

    def _create_bucket(self) -> None:
        try:
            logger.info(
                "Creating bucket %s ...", self.fxstreet_config.s3_config.bucket_name
            )
            self.s3_client.create_bucket(
                Bucket=self.fxstreet_config.s3_config.bucket_name
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "BucketAlreadyOwnedByYou":
                logger.info(
                    "Bucket %s already exists and is owned by you",
                    self.fxstreet_config.s3_config.bucket_name,
                )
            else:
                logger.exception(
                    "Failed to create bucket %s",
                    self.fxstreet_config.s3_config.bucket_name,
                )
                raise
        except Exception:
            logger.exception(
                "Failed to create bucket %s",
                self.fxstreet_config.s3_config.bucket_name,
            )
            raise
