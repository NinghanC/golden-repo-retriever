from __future__ import annotations

from .llm import BaseLLMClient
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


def synthesizer_agent(state: AnalysisState, llm_client: BaseLLMClient | None = None) -> None:
    summary = build_summary(state["companies"], state["metrics"])
    if llm_client is not None:
        summary = llm_client.summarize(
            summary,
            {
                "query": state["query"],
                "companies": state["companies"],
                "metrics": state["metrics"],
            },
        )
        state["llm_provider"] = llm_client.provider
    else:
        state["llm_provider"] = "local"
    state["summary"] = summary
    record_event(state, "synthesizer_agent", "ok", f"Summary assembled with {state['llm_provider']} provider.")
