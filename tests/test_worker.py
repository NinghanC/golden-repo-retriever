from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from golden_repo_retriever.queueing import JobQueue
from golden_repo_retriever.storage import AnalysisStore
from golden_repo_retriever.worker import JobWorker


class WorkerTestCase(unittest.TestCase):
    def test_worker_returns_false_without_queued_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            worker = JobWorker(Path(tmp_dir) / "worker.db")

            processed = worker.process_next()

        self.assertFalse(processed)

    def test_worker_processes_queued_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            database_path = Path(tmp_dir) / "worker.db"
            store = AnalysisStore(database_path)
            queue = JobQueue(database_path)
            worker = JobWorker(database_path)
            job_id = queue.enqueue("Compare Microsoft.")

            processed = worker.process_next()
            job = store.get_job(job_id)

        self.assertTrue(processed)
        self.assertIsNotNone(job)
        assert job is not None
        self.assertEqual(job["status"], "completed")
        self.assertIsInstance(job["analysis_id"], int)

    def test_worker_marks_missing_report_job_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            database_path = Path(tmp_dir) / "worker.db"
            store = AnalysisStore(database_path)
            queue = JobQueue(database_path)
            worker = JobWorker(database_path)
            job_id = queue.enqueue("Read this report.", report_id=999)

            processed = worker.process_next()
            job = store.get_job(job_id)

        self.assertTrue(processed)
        self.assertIsNotNone(job)
        assert job is not None
        self.assertEqual(job["status"], "failed")
        self.assertEqual(job["error"], "Report not found.")


if __name__ == "__main__":
    unittest.main()
