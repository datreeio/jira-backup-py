from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jira_backup._config import read_config
from jira_backup._wizard import create_config


class CreateConfigTests(unittest.TestCase):
    def test_invalid_values_show_errors_and_reprompt_only_invalid_fields(self) -> None:
        answers = [
            "https://example.atlassian.net",
            "",
            "",
            "y",
            "n",
            "example.atlassian.net",
            "backup@example.com",
            "api-token",
            "n",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with patch("builtins.input", side_effect=answers) as input_mock:
                with redirect_stderr(io.StringIO()) as stderr:
                    with redirect_stdout(io.StringIO()):
                        create_config(config_path=config_path)

            config = read_config(config_path=config_path)

        self.assertEqual(input_mock.call_count, len(answers))
        self.assertEqual(config.host_url, "example.atlassian.net")
        self.assertEqual(config.user_email, "backup@example.com")
        self.assertEqual(config.api_token, "api-token")
        self.assertTrue(config.include_attachments)
        self.assertFalse(config.download_locally)

        error_output = stderr.getvalue()
        self.assertIn("-> Invalid configuration:", error_output)
        self.assertIn("host_url: Value error", error_output)
        self.assertIn("user_email: Value error, must not be blank", error_output)
        self.assertIn("api_token: Value error, must not be blank", error_output)
        self.assertNotIn("Traceback", error_output)


if __name__ == "__main__":
    unittest.main()
