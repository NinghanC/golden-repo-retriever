from __future__ import annotations

import unittest

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
            ["detect_companies", "compute_metrics", "write_summary"],
        )


if __name__ == "__main__":
    unittest.main()
