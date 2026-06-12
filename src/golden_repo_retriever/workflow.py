from __future__ import annotations

from .agents import analyst_agent, retrieval_agent, synthesizer_agent
from .documents import parse_report_file
from .state import AnalysisState, record_event


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
    retrieval_agent(state)
    analyst_agent(state)
    synthesizer_agent(state)
    state["checkpoint_count"] = len(state["audit_log"])
    return state


def load_report(state: AnalysisState, report_path: str) -> None:
    text, source = parse_report_file(report_path)
    state["report_source"] = source
    state["report_text"] = text
    record_event(state, "load_report", "ok", f"Loaded report text from {source}.")


def load_report_text(state: AnalysisState, report_text: str) -> None:
    state["report_source"] = "request"
    state["report_text"] = report_text
    record_event(state, "load_report", "ok", "Loaded report text from request.")

