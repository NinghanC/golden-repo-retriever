from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from uuid import UUID

from golden_repo_retriever import run_analysis


class WorkflowTestCase(unittest.TestCase):
    def test_run_analysis_returns_summary(self) -> None:
        result = run_analysis("Compare Apple and Microsoft.")

        UUID(result["run_id"])
        self.assertIn("T", result["started_at"])
        self.assertIn("T", result["completed_at"])
        self.assertEqual(result["companies"], ["Apple", "Microsoft"])
        self.assertIn("Apple", result["summary"])
        self.assertIn("Microsoft", result["summary"])
        self.assertIn("AAPL", result["summary"])
        self.assertIn("ebitda_margin", result["metrics"]["Apple"])
        self.assertEqual(result["market_data"]["Apple"]["ticker"], "AAPL")
        self.assertEqual(result["checkpoint_count"], 3)
        self.assertEqual(
            [event["step"] for event in result["audit_log"]],
            ["retrieval_agent", "analyst_agent", "synthesizer_agent"],
        )
        self.assertIn("timestamp", result["audit_log"][0])

    def test_run_analysis_uses_report_text_for_company_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "report.txt"
            report_path.write_text("Microsoft supply chain risk remains low.", encoding="utf-8")

            result = run_analysis("Read this finance report.", report_path=str(report_path))

        self.assertEqual(result["companies"], ["Microsoft"])
        self.assertIn("Microsoft", result["summary"])
        self.assertEqual(result["audit_log"][0]["step"], "load_report")
        self.assertEqual(result["checkpoint_count"], 4)

    def test_run_analysis_uses_extracted_report_metrics(self) -> None:
        result = run_analysis(
            "Read this finance report.",
            report_text=(
                "Microsoft revenue was $245.1 billion. "
                "Microsoft EBITDA margin was 53%. "
                "Microsoft R&D was $29.5 billion. "
                "Microsoft supply chain risk remains low."
            ),
        )

        self.assertEqual(result["companies"], ["Microsoft"])
        self.assertEqual(result["extracted_facts"]["Microsoft"]["revenue"], 245.1)
        self.assertEqual(result["evidence"]["Microsoft"][0]["field"], "revenue")
        self.assertEqual(result["evidence"]["Microsoft"][0]["snippet"], "Microsoft revenue was $245.1 billion.")
        self.assertEqual(result["metrics"]["Microsoft"]["ebitda_margin"], 0.53)
        self.assertEqual(result["metrics"]["Microsoft"]["r_and_d_intensity"], 0.1204)
        self.assertEqual(result["metrics"]["Microsoft"]["supply_chain_risk"], "low")


if __name__ == "__main__":
    unittest.main()
