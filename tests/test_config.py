from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jira_backup._config import read_config


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
