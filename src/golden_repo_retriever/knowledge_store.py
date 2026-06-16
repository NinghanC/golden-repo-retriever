from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .logging_utils import get_logger
from .storage import DEFAULT_DATABASE_PATH

logger = get_logger(__name__)


class KnowledgeStore:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save_from_analysis(self, analysis_id: int, result: dict[str, Any]) -> int:
        saved_count = 0
        facts = result.get("extracted_facts", {})
        evidence = result.get("evidence", {})
        source = result.get("report_source") or "analysis"
        for company, company_facts in facts.items():
            company_evidence = evidence.get(company, [])
            for field, value in company_facts.items():
                snippet = _snippet_for_field(company_evidence, field)
                self.save_fact(
                    company=company,
                    field=field,
                    value=value,
                    source=source,
                    snippet=snippet,
                    analysis_id=analysis_id,
                )
                saved_count += 1
        logger.info("knowledge_saved analysis_id=%s facts=%s", analysis_id, saved_count)
        return saved_count

    def save_fact(
        self,
        company: str,
        field: str,
        value: float | str,
        source: str,
        snippet: str | None = None,
        analysis_id: int | None = None,
    ) -> int:
        created_at = _now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO knowledge (company, field, value, source, snippet, analysis_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (company, field, str(value), source, snippet, analysis_id, created_at),
            )
            return int(cursor.lastrowid)

    def list_facts(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, company, field, value, source, snippet, analysis_id, created_at
                FROM knowledge
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_company_facts(self, company: str, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, company, field, value, source, snippet, analysis_id, created_at
                FROM knowledge
                WHERE lower(company) = lower(?)
                ORDER BY id DESC
                LIMIT ?
                """,
                (company, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    field TEXT NOT NULL,
                    value TEXT NOT NULL,
                    source TEXT NOT NULL,
                    snippet TEXT,
                    analysis_id INTEGER,
                    created_at TEXT NOT NULL
                )
                """
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


def _snippet_for_field(evidence: list[dict[str, float | str]], field: str) -> str | None:
    for item in evidence:
        if item.get("field") == field:
            snippet = item.get("snippet")
            return str(snippet) if snippet is not None else None
    return None


def _now() -> str:
    return datetime.now(UTC).isoformat()
