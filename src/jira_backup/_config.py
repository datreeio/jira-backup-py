from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    ValidationError,
    field_validator,
    model_validator,
)


def _is_valid_hostname(value: str) -> bool:
    try:
        parsed = urlsplit(f"//{value}")
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return False

    if (
        hostname is None
        or parsed.netloc != value
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        return False

    try:
        ascii_hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return False

    if len(ascii_hostname) > 253:
        return False

    labels = ascii_hostname.split(".")
    return all(
        1 <= len(label) <= 63
        and label[0].isalnum()
        and label[-1].isalnum()
        and all(character.isalnum() or character == "-" for character in label)
        for label in labels
    )


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_case_insensitive_keys(cls, data: object) -> object:
        if not isinstance(data, Mapping):
            return data

        key_map = cls.case_insensitive_key_map()
        normalized: dict[str, object] = {}
        original_keys: dict[str, str] = {}

        for key, value in data.items():
            if not isinstance(key, str):
                raise ValueError("config keys must be strings")

            normalized_key = key_map.get(key.casefold(), key)
            if normalized_key in normalized:
                original_key = original_keys[normalized_key]
                raise ValueError(
                    f"duplicate config keys {original_key!r} and {key!r} "
                    f"both map to {normalized_key!r}"
                )

            normalized[normalized_key] = value
            original_keys[normalized_key] = key

        return normalized

    @classmethod
    def case_insensitive_key_map(cls) -> dict[str, str]:
        key_map: dict[str, str] = {}

        for field_name, field_info in cls.model_fields.items():
            key_map[field_name.casefold()] = field_name
            validation_alias = field_info.validation_alias

            if isinstance(validation_alias, str):
                key_map[validation_alias.casefold()] = field_name
                continue

            if isinstance(validation_alias, AliasChoices):
                for alias in validation_alias.choices:
                    if isinstance(alias, str):
                        key_map[alias.casefold()] = field_name

        return key_map


class ConfigUploadToS3(ConfigModel):
    aws_endpoint_url: str = ""
    aws_region: str = Field(
        default="",
        validation_alias=AliasChoices("aws_region", "aws_s3_region"),
    )
    s3_bucket: str = ""
    s3_dir: str = ""
    aws_access_key: str = Field(
        default="",
        validation_alias=AliasChoices("aws_access_key", "aws_access_key_id"),
    )
    aws_secret_key: str = Field(
        default="",
        validation_alias=AliasChoices("aws_secret_key", "aws_secret_access_key"),
    )
    aws_is_secure: StrictBool = True


class ConfigUploadToGCP(ConfigModel):
    gcp_project_id: str = ""
    gcs_bucket: str = ""
    gcs_dir: str = ""
    gcp_service_account_key: str | None = None


class ConfigUploadToAzure(ConfigModel):
    azure_account_name: str = ""
    azure_container: str = ""
    azure_dir: str = ""
    azure_connection_string: str = ""
    azure_account_key: str = ""


class ConfigCustomFilename(ConfigModel):
    confluence: str = ""
    jira: str = ""


class Config(ConfigModel):
    host_url: str
    user_email: str
    api_token: str
    include_attachments: StrictBool
    download_locally: StrictBool
    upload_to_s3: ConfigUploadToS3 | None = None
    upload_to_gcp: ConfigUploadToGCP | None = None
    upload_to_azure: ConfigUploadToAzure | None = None
    custom_filename: ConfigCustomFilename | None = None

    @field_validator("user_email", "api_token")
    @classmethod
    def required_string_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("host_url")
    @classmethod
    def host_url_must_be_hostname(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")

        if not _is_valid_hostname(value):
            raise ValueError(
                "must be a valid hostname without a scheme or other URL components"
            )
        return value


def _format_validation_errors(error: ValidationError) -> str:
    formatted_errors: list[str] = []

    for details in error.errors(include_input=False):
        location = ".".join(str(part) for part in details["loc"]) or "<root>"
        formatted_errors.append(
            f"{location}: {details['msg']} [type={details['type']}]"
        )

    return "\n".join(formatted_errors)


def read_config(*, config_path: Path) -> Config:
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config_data = yaml.safe_load(config_file)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file {config_path}: {e}") from e
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Config file not found: {config_path}. "
            "Copy config.example.yaml to config.yaml or pass -C."
        ) from e

    if config_data is None:
        config_data = {}

    if not isinstance(config_data, dict):
        raise ValueError(f"Config file {config_path} must contain a YAML mapping.")

    try:
        return Config.model_validate(config_data)
    except ValidationError as e:
        validation_errors = _format_validation_errors(e)
        raise ValueError(
            f"Invalid config file {config_path}:\n{validation_errors}"
        ) from e
