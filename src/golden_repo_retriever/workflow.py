from __future__ import annotations

from pathlib import Path

from .state import AnalysisState, checkpoint, record_event
from .tools import build_summary, calculate_metrics, extract_companies


def run_analysis(query: str, report_path: str | None = None, report_text: str | None = None) -> AnalysisState:
    """Run the analysis workflow with state tracking.

    Each phase reads and updates one shared state object.
    """
    state: AnalysisState = {
        "query": query,
        "audit_log": [],
    }

    if report_path:
        load_report(state, report_path)
    elif report_text:
        load_report_text(state, report_text)
    detect_companies(state)
    compute_metrics(state)
    write_summary(state)
    state["checkpoint_count"] = len(state["audit_log"])
    return state


def load_report(state: AnalysisState, report_path: str) -> None:
    path = Path(report_path)
    text = path.read_text(encoding="utf-8")
    state["report_source"] = str(path)
    state["report_text"] = text
    record_event(state, "load_report", "ok", f"Loaded report text from {path.name}.")


def load_report_text(state: AnalysisState, report_text: str) -> None:
    state["report_source"] = "request"
    state["report_text"] = report_text
    record_event(state, "load_report", "ok", "Loaded report text from request.")


def detect_companies(state: AnalysisState) -> None:
    companies = extract_companies(state["query"], state.get("report_text", ""))
    state["companies"] = companies
    record_event(state, "detect_companies", "ok", f"Detected companies: {', '.join(companies)}")


def compute_metrics(state: AnalysisState) -> None:
    metrics = {company: calculate_metrics(company) for company in state["companies"]}
    state["metrics"] = metrics
    snapshot = checkpoint(state)
    record_event(state, "compute_metrics", "ok", f"Calculated {snapshot['metric_count']} metric values.")


def write_summary(state: AnalysisState) -> None:
    summary = build_summary(state["companies"], state["metrics"])
    state["summary"] = summary
    record_event(state, "write_summary", "ok", "Summary assembled.")
