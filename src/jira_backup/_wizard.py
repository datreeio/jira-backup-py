from pathlib import Path

import yaml

from ._config import ConfigUploadToS3, Config


def create_config(*, config_path: Path) -> None:
    custom_config = Config(
        HOST_URL=input("What is your Jira host name? "),
        USER_EMAIL=input("What is your Jira account email address? "),
        API_TOKEN=input("Paste your Jira API token: "),
        INCLUDE_ATTACHMENTS=input_boolean("Do you want to include attachments?"),
        DOWNLOAD_LOCALLY=input_boolean(
            "Do you want to download the backup file locally?"
        ),
    )

    if input_boolean("Do you want to upload the backup file to S3?"):
        custom_config["UPLOAD_TO_S3"] = ConfigUploadToS3(
            AWS_ENDPOINT_URL=input("What is your AWS endpoint url? "),
            AWS_REGION=input("What is your AWS region? "),
            S3_BUCKET=input("What is the S3 bucket name? "),
            S3_DIR=input("What is the S3 directory for upload? (example Atlassian/) "),
            AWS_ACCESS_KEY=input("What is your AWS access key? "),
            AWS_SECRET_KEY=input("What is your AWS secret key? "),
            AWS_IS_SECURE=input_boolean("Do you want to use SSL?"),
        )

    with config_path.open("w+") as config_file:
        yaml.dump(custom_config, config_file, default_flow_style=False)


def parse_boolean(s: str) -> bool:
    return s.lower() in ("yes", "true", "t", "1", "y")


def input_boolean(q: str) -> bool:
    return parse_boolean(input(f"{q} (y/n) "))
