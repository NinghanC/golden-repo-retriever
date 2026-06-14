from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "golden_repo_retriever.db"


def _now() -> str:
    return datetime.now(UTC).isoformat()


class AnalysisStore:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(self, result: dict[str, Any]) -> int:
        created_at = _now()
        payload = json.dumps(result, ensure_ascii=True)
        companies = ", ".join(result.get("companies", []))
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO analyses (created_at, query, companies, summary, payload)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    result.get("query", ""),
                    companies,
                    result.get("summary", ""),
                    payload,
                ),
            )
            return int(cursor.lastrowid)

    def list(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, query, companies, summary
                FROM analyses
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, analysis_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, created_at, payload FROM analyses WHERE id = ?",
                (analysis_id,),
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(row["payload"])
        payload["analysis_id"] = row["id"]
        payload["created_at"] = row["created_at"]
        return payload

    def create_job(
        self,
        query: str,
        report_text: str | None = None,
        report_id: int | None = None,
        llm_provider: str | None = None,
    ) -> int:
        timestamp = _now()
        payload = json.dumps(
            {
                "query": query,
                "report_text": report_text,
                "report_id": report_id,
                "llm_provider": llm_provider,
            },
            ensure_ascii=True,
        )
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO jobs (status, query, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("queued", query, payload, timestamp, timestamp),
            )
            return int(cursor.lastrowid)

    def start_job(self, job_id: int) -> None:
        self._update_job(job_id, status="running")

    def complete_job(self, job_id: int, analysis_id: int) -> None:
        self._update_job(job_id, status="completed", analysis_id=analysis_id, error=None)

    def fail_job(self, job_id: int, error: str) -> None:
        self._update_job(job_id, status="failed", error=error)

    def list_jobs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, status, query, payload, created_at, updated_at, error, analysis_id
                FROM jobs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        jobs = []
        for row in rows:
            job = dict(row)
            payload = json.loads(job.pop("payload"))
            job.update(payload)
            jobs.append(job)
        return jobs

    def get_job(self, job_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, status, query, payload, created_at, updated_at, error, analysis_id
                FROM jobs
                WHERE id = ?
                """,
                (job_id,),
            ).fetchone()
        if row is None:
            return None
        job = dict(row)
        payload = json.loads(job.pop("payload"))
        job.update(payload)
        return job

    def save_report(
        self,
        filename: str,
        source: str,
        text: str,
        content_type: str | None = None,
    ) -> int:
        created_at = _now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO reports (filename, source, content_type, text, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (filename, source, content_type, text, created_at),
            )
            return int(cursor.lastrowid)

    def list_reports(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, filename, source, content_type, text, created_at
                FROM reports
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_report(self, report_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, filename, source, content_type, text, created_at
                FROM reports
                WHERE id = ?
                """,
                (report_id,),
            ).fetchone()
        return dict(row) if row is not None else None

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    query TEXT NOT NULL,
                    companies TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    query TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error TEXT,
                    analysis_id INTEGER,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content_type TEXT,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def _update_job(
        self,
        job_id: int,
        status: str,
        analysis_id: int | None = None,
        error: str | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, updated_at = ?, analysis_id = COALESCE(?, analysis_id), error = ?
                WHERE id = ?
                """,
                (status, _now(), analysis_id, error, job_id),
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()
