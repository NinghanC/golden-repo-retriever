from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from golden_repo_retriever.config import PROJECT_ROOT, Settings


class ConfigTestCase(unittest.TestCase):
    def test_settings_defaults(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings.from_env()

        self.assertEqual(settings.app_name, "Golden Repo Retriever")
        self.assertEqual(settings.app_version, "0.1.0")
        self.assertEqual(settings.database_path, PROJECT_ROOT / "data" / "golden_repo_retriever.db")
        self.assertEqual(settings.api_host, "127.0.0.1")
        self.assertEqual(settings.api_port, 8000)
        self.assertEqual(settings.worker_poll_seconds, 2.0)
        self.assertEqual(settings.default_llm_provider, "local")
        self.assertEqual(settings.log_level, "INFO")

    def test_settings_use_environment_overrides(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "APP_NAME": "Custom App",
                "APP_VERSION": "9.9.9",
                "DATABASE_PATH": "custom.db",
                "API_HOST": "0.0.0.0",
                "API_PORT": "9000",
                "WORKER_POLL_SECONDS": "0.5",
                "LLM_PROVIDER": "mistral",
                "LOG_LEVEL": "debug",
            },
            clear=True,
        ):
            settings = Settings.from_env()

        self.assertEqual(settings.app_name, "Custom App")
        self.assertEqual(settings.app_version, "9.9.9")
        self.assertEqual(settings.database_path, Path("custom.db"))
        self.assertEqual(settings.api_host, "0.0.0.0")
        self.assertEqual(settings.api_port, 9000)
        self.assertEqual(settings.worker_poll_seconds, 0.5)
        self.assertEqual(settings.default_llm_provider, "mistral")
        self.assertEqual(settings.log_level, "DEBUG")


if __name__ == "__main__":
    unittest.main()
