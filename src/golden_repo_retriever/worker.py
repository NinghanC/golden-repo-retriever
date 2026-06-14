from __future__ import annotations

import time
from pathlib import Path

from .queueing import JobQueue
from .storage import AnalysisStore, DEFAULT_DATABASE_PATH
from .workflow import run_analysis


class JobWorker:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.store = AnalysisStore(database_path)
        self.queue = JobQueue(database_path)

    def process_next(self) -> bool:
        job = self.queue.claim_next()
        if job is None:
            return False
        try:
            result = self._run_job(job)
            analysis_id = self.store.save(result)
            self.queue.mark_completed(job["id"], analysis_id)
        except Exception as exc:
            self.queue.mark_failed(job["id"], str(exc))
        return True

    def run_forever(self, poll_seconds: float = 2.0) -> None:
        while True:
            processed = self.process_next()
            if not processed:
                time.sleep(poll_seconds)

    def _run_job(self, job: dict[str, object]) -> dict[str, object]:
        report_text = job.get("report_text")
        report_id = job.get("report_id")
        if report_id is not None:
            report = self.store.get_report(int(report_id))
            if report is None:
                raise ValueError("Report not found.")
            report_text = report["text"]

        result = run_analysis(
            str(job["query"]),
            report_text=str(report_text) if report_text is not None else None,
            llm_provider=str(job["llm_provider"]) if job.get("llm_provider") is not None else None,
        )
        if report_id is not None:
            result["report_source"] = f"report:{report_id}"
        return result


def main() -> None:
    JobWorker().run_forever()
