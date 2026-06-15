from pathlib import Path
from typing import TypedDict, NotRequired

import yaml


class ConfigUploadToS3(TypedDict):
    AWS_ENDPOINT_URL: str
    AWS_REGION: str
    S3_BUCKET: str
    S3_DIR: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_IS_SECURE: bool


class ConfigUploadToGCP(TypedDict):
    GCP_PROJECT_ID: str
    GCS_BUCKET: str
    GCS_DIR: str
    GCP_SERVICE_ACCOUNT_KEY: NotRequired[str | None]


class ConfigUploadToAzure(TypedDict):
    AZURE_ACCOUNT_NAME: str
    AZURE_CONTAINER: str
    AZURE_DIR: str
    AZURE_CONNECTION_STRING: str
    AZURE_ACCOUNT_KEY: str


class ConfigCustomFilename(TypedDict, total=False):
    CONFLUENCE: str
    JIRA: str


class Config(TypedDict):
    HOST_URL: str
    USER_EMAIL: str
    API_TOKEN: str
    INCLUDE_ATTACHMENTS: bool
    DOWNLOAD_LOCALLY: bool
    UPLOAD_TO_S3: NotRequired[ConfigUploadToS3]
    UPLOAD_TO_GCP: NotRequired[ConfigUploadToGCP]
    UPLOAD_TO_AZURE: NotRequired[ConfigUploadToAzure]
    CUSTOM_FILENAME: NotRequired[ConfigCustomFilename]


def read_config(*, config_path: Path) -> Config:
    # TODO: Validate the loaded config before returning.
    return yaml.safe_load(config_path.read_text())  # type: ignore[no-any-return]
