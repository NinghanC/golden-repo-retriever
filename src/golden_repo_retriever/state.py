from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypedDict


class AuditEvent(TypedDict):
    step: str
    status: str
    detail: str
    timestamp: str


class AnalysisState(TypedDict, total=False):
    run_id: str
    started_at: str
    completed_at: str
    query: str
    report_source: str
    report_text: str
    companies: list[str]
    extracted_facts: dict[str, dict[str, float | str]]
    evidence: dict[str, list[dict[str, float | str]]]
    metrics: dict[str, dict[str, float | str]]
    market_data: dict[str, dict[str, float | str]]
    summary: str
    llm_provider: str
    audit_log: list[AuditEvent]
    checkpoint_count: int


def record_event(state: AnalysisState, step: str, status: str, detail: str) -> None:
    event: AuditEvent = {"step": step, "status": status, "detail": detail, "timestamp": _now()}
    state.setdefault("audit_log", []).append(event)


def checkpoint(state: AnalysisState) -> dict[str, Any]:
    return {
        "companies": list(state.get("companies", [])),
        "metric_count": sum(len(metrics) for metrics in state.get("metrics", {}).values()),
        "audit_count": len(state.get("audit_log", [])),
    }


def _now() -> str:
    return datetime.now(UTC).isoformat()
