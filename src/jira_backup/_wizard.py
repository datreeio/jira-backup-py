from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import yaml
from pydantic import ValidationError

from ._config import Config, ConfigUploadToS3, _format_validation_errors


def _input_config() -> Config:
    prompts: dict[str, Callable[[], object]] = {
        "host_url": lambda: input("What is your Jira host name? "),
        "user_email": lambda: input("What is your Jira account email address? "),
        "api_token": lambda: input("Paste your Jira API token: "),
        "include_attachments": lambda: input_boolean(
            "Do you want to include attachments?"
        ),
        "download_locally": lambda: input_boolean(
            "Do you want to download the backup file locally?"
        ),
    }
    values = {field_name: prompt() for field_name, prompt in prompts.items()}

    while True:
        try:
            return Config.model_validate(values)
        except ValidationError as error:
            print(
                f"-> Invalid configuration:\n{_format_validation_errors(error)}",
                file=sys.stderr,
            )
            invalid_fields = {
                details["loc"][0]
                for details in error.errors(include_input=False)
                if details["loc"] and isinstance(details["loc"][0], str)
            }
            retry_fields = {
                field_name for field_name in invalid_fields if field_name in prompts
            }
            if not retry_fields:
                raise

            for field_name, prompt in prompts.items():
                if field_name in retry_fields:
                    values[field_name] = prompt()


def create_config(*, config_path: Path) -> None:
    custom_config = _input_config()

    if input_boolean("Do you want to upload the backup file to S3?"):
        s3_config = ConfigUploadToS3(
            aws_endpoint_url=input("What is your AWS endpoint url? "),
            aws_region=input("What is your AWS region? "),
            s3_bucket=input("What is the S3 bucket name? "),
            s3_dir=input("What is the S3 directory for upload? (example Atlassian/) "),
            aws_access_key=input("What is your AWS access key? "),
            aws_secret_key=input("What is your AWS secret key? "),
            aws_is_secure=input_boolean("Do you want to use SSL?"),
        )
        custom_config = Config.model_validate(
            {**custom_config.model_dump(), "upload_to_s3": s3_config}
        )

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as config_file:
        yaml.safe_dump(
            custom_config.model_dump(exclude_none=True),
            config_file,
            default_flow_style=False,
            sort_keys=False,
        )

    print(f"-> Wrote configuration to {config_path.resolve()}")


def parse_boolean(s: str) -> bool:
    return s.lower() in ("yes", "true", "t", "1", "y")


def input_boolean(q: str) -> bool:
    return parse_boolean(input(f"{q} (y/n) "))
