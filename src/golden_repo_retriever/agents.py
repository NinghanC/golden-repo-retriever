from __future__ import annotations

from .state import AnalysisState, checkpoint, record_event
from .tools import build_summary, calculate_metrics, extract_companies


def retrieval_agent(state: AnalysisState) -> None:
    companies = extract_companies(state["query"], state.get("report_text", ""))
    state["companies"] = companies
    record_event(state, "retrieval_agent", "ok", f"Detected companies: {', '.join(companies)}")


def analyst_agent(state: AnalysisState) -> None:
    metrics = {company: calculate_metrics(company) for company in state["companies"]}
    state["metrics"] = metrics
    snapshot = checkpoint(state)
    record_event(state, "analyst_agent", "ok", f"Calculated {snapshot['metric_count']} metric values.")


def synthesizer_agent(state: AnalysisState) -> None:
    summary = build_summary(state["companies"], state["metrics"])
    state["summary"] = summary
    record_event(state, "synthesizer_agent", "ok", "Summary assembled.")
