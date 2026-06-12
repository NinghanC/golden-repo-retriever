from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTestCase(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "golden_repo_retriever.cli", *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_cli_prints_json(self) -> None:
        result = self.run_cli("--query", "Compare Apple.", "--json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["companies"], ["Apple"])
        self.assertIn("summary", payload)
        self.assertEqual(payload["checkpoint_count"], 3)

    def test_cli_uses_report_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "report.txt"
            report_path.write_text("Microsoft supply chain risk remains low.", encoding="utf-8")

            result = self.run_cli("--query", "Read this report.", "--file", str(report_path), "--json")

        payload = json.loads(result.stdout)
        self.assertEqual(payload["companies"], ["Microsoft"])
        self.assertEqual(payload["audit_log"][0]["step"], "load_report")

    def test_cli_exports_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "analysis.json"
            result = self.run_cli("--query", "Compare Microsoft.", "--output", str(output_path))

            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIn("Saved:", result.stdout)
        self.assertEqual(payload["companies"], ["Microsoft"])


if __name__ == "__main__":
    unittest.main()
