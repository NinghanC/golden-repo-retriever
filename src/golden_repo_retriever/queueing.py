from __future__ import annotations

from pathlib import Path
from typing import Any

from .storage import AnalysisStore, DEFAULT_DATABASE_PATH


class JobQueue:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.store = AnalysisStore(database_path)

    def enqueue(
        self,
        query: str,
        report_text: str | None = None,
        report_id: int | None = None,
        llm_provider: str | None = None,
    ) -> int:
        return self.store.create_job(
            query=query,
            report_text=report_text,
            report_id=report_id,
            llm_provider=llm_provider,
        )

    def claim_next(self) -> dict[str, Any] | None:
        return self.store.claim_next_job()

    def mark_completed(self, job_id: int, analysis_id: int) -> None:
        self.store.complete_job(job_id, analysis_id)

    def mark_failed(self, job_id: int, error: str) -> None:
        self.store.fail_job(job_id, error)
