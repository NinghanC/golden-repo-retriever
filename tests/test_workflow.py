from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from golden_repo_retriever import run_analysis


class WorkflowTestCase(unittest.TestCase):
    def test_run_analysis_returns_summary(self) -> None:
        result = run_analysis("Compare Apple and Microsoft.")

        self.assertEqual(result["companies"], ["Apple", "Microsoft"])
        self.assertIn("Apple", result["summary"])
        self.assertIn("Microsoft", result["summary"])
        self.assertIn("ebitda_margin", result["metrics"]["Apple"])
        self.assertEqual(result["checkpoint_count"], 3)
        self.assertEqual(
            [event["step"] for event in result["audit_log"]],
            ["retrieval_agent", "analyst_agent", "synthesizer_agent"],
        )

    def test_run_analysis_uses_report_text_for_company_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "report.txt"
            report_path.write_text("Microsoft supply chain risk remains low.", encoding="utf-8")

            result = run_analysis("Read this finance report.", report_path=str(report_path))

        self.assertEqual(result["companies"], ["Microsoft"])
        self.assertIn("Microsoft", result["summary"])
        self.assertEqual(result["audit_log"][0]["step"], "load_report")
        self.assertEqual(result["checkpoint_count"], 4)


if __name__ == "__main__":
    unittest.main()
