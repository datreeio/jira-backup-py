from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jira_backup._config import Config, read_config


def make_config(*, host_url: str) -> Config:
    return Config.model_validate(
        {
            "host_url": host_url,
            "user_email": "backup@example.com",
            "api_token": "token",
            "include_attachments": True,
            "download_locally": True,
        }
    )


class ConfigTests(unittest.TestCase):
    def test_host_url_accepts_bare_hostname(self) -> None:
        for hostname in (
            "example.atlassian.net",
            "EXAMPLE.atlassian.net",
            "jira-backup.internal",
            "localhost",
        ):
            with self.subTest(hostname=hostname):
                self.assertEqual(make_config(host_url=hostname).host_url, hostname)

    def test_host_url_rejects_url_components_and_whitespace(self) -> None:
        for value in (
            "http://example.atlassian.net",
            "HTTPS://example.atlassian.net",
            "example.atlassian.net/path",
            "example.atlassian.net?path=wrong",
            "example.atlassian.net#fragment",
            "user@example.atlassian.net",
            "example.atlassian.net@evil.example",
            "example.atlassian.net:443",
            " example.atlassian.net",
            "example.atlassian.net ",
            "example .atlassian.net",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    make_config(host_url=value)

    def test_host_url_rejects_invalid_hostname_syntax(self) -> None:
        for value in (
            "-example.atlassian.net",
            "example-.atlassian.net",
            "example..atlassian.net",
            "example_atlassian.net",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    make_config(host_url=value)


class ReadConfigTests(unittest.TestCase):
    def test_validation_errors_omit_rejected_credential_values(self) -> None:
        api_token = "super-secret-api-token"
        aws_secret_key = "super-secret-aws-key"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "host_url: example.atlassian.net",
                        "user_email: backup@example.com",
                        f"api_tokn: {api_token}",
                        "include_attachments: true",
                        "download_locally: true",
                        "upload_to_s3:",
                        f"  aws_secret_keey: {aws_secret_key}",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as raised:
                read_config(config_path=config_path)

        message = str(raised.exception)
        self.assertIn("api_token: Field required [type=missing]", message)
        self.assertIn(
            "api_tokn: Extra inputs are not permitted [type=extra_forbidden]",
            message,
        )
        self.assertIn(
            "upload_to_s3.aws_secret_keey: "
            "Extra inputs are not permitted [type=extra_forbidden]",
            message,
        )
        self.assertNotIn(api_token, message)
        self.assertNotIn(aws_secret_key, message)
        self.assertNotIn("input_value", message)


if __name__ == "__main__":
    unittest.main()
