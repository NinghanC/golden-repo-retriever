from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from golden_repo_retriever.storage import AnalysisStore


class AnalysisStoreTestCase(unittest.TestCase):
    def test_save_list_and_get_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = AnalysisStore(Path(tmp_dir) / "analyses.db")
            result = {
                "query": "Compare Apple.",
                "companies": ["Apple"],
                "metrics": {"Apple": {"ebitda_margin": 0.32}},
                "summary": "Apple has strong margins.",
                "llm_provider": "local",
                "audit_log": [],
                "checkpoint_count": 0,
            }

            analysis_id = store.save(result)
            history = store.list()
            saved = store.get(analysis_id)

        self.assertEqual(history[0]["id"], analysis_id)
        self.assertEqual(history[0]["companies"], "Apple")
        self.assertIsNotNone(saved)
        assert saved is not None
        self.assertEqual(saved["analysis_id"], analysis_id)
        self.assertEqual(saved["companies"], ["Apple"])

    def test_get_missing_analysis_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = AnalysisStore(Path(tmp_dir) / "analyses.db")

            saved = store.get(999)

        self.assertIsNone(saved)

    def test_job_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = AnalysisStore(Path(tmp_dir) / "analyses.db")
            job_id = store.create_job("Compare Microsoft.", report_text="Microsoft risk is low.")

            queued = store.get_job(job_id)
            store.start_job(job_id)
            running = store.get_job(job_id)
            analysis_id = store.save(
                {
                    "query": "Compare Microsoft.",
                    "companies": ["Microsoft"],
                    "metrics": {},
                    "summary": "ok",
                    "llm_provider": "local",
                    "audit_log": [],
                    "checkpoint_count": 0,
                }
            )
            store.complete_job(job_id, analysis_id)
            completed = store.get_job(job_id)
            history = store.list_jobs()

        self.assertIsNotNone(queued)
        assert queued is not None
        self.assertEqual(queued["status"], "queued")
        self.assertEqual(queued["report_text"], "Microsoft risk is low.")
        self.assertIsNotNone(running)
        assert running is not None
        self.assertEqual(running["status"], "running")
        self.assertIsNotNone(completed)
        assert completed is not None
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["analysis_id"], analysis_id)
        self.assertEqual(history[0]["id"], job_id)


if __name__ == "__main__":
    unittest.main()
