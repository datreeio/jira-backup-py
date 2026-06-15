from pathlib import Path

import yaml

from ._config import Config, ConfigUploadToS3


def create_config(*, config_path: Path) -> None:
    host_url = input("What is your Jira host name? ")
    user_email = input("What is your Jira account email address? ")
    api_token = input("Paste your Jira API token: ")
    include_attachments = input_boolean("Do you want to include attachments?")
    download_locally = input_boolean("Do you want to download the backup file locally?")

    s3_config = None
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

    custom_config = Config(
        host_url=host_url,
        user_email=user_email,
        api_token=api_token,
        include_attachments=include_attachments,
        download_locally=download_locally,
        upload_to_s3=s3_config,
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
