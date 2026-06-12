from __future__ import annotations

from typing import Any, TypedDict


class AuditEvent(TypedDict):
    step: str
    status: str
    detail: str


class AnalysisState(TypedDict, total=False):
    query: str
    report_source: str
    report_text: str
    companies: list[str]
    metrics: dict[str, dict[str, float | str]]
    summary: str
    audit_log: list[AuditEvent]
    checkpoint_count: int


def record_event(state: AnalysisState, step: str, status: str, detail: str) -> None:
    event: AuditEvent = {"step": step, "status": status, "detail": detail}
    state.setdefault("audit_log", []).append(event)


def checkpoint(state: AnalysisState) -> dict[str, Any]:
    return {
        "companies": list(state.get("companies", [])),
        "metric_count": sum(len(metrics) for metrics in state.get("metrics", {}).values()),
        "audit_count": len(state.get("audit_log", [])),
    }
