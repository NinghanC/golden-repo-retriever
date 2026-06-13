from __future__ import annotations

from .extraction import extract_financial_facts
from .llm import BaseLLMClient
from .state import AnalysisState, checkpoint, record_event
from .tools import build_summary, calculate_metrics, extract_companies


def retrieval_agent(state: AnalysisState) -> None:
    companies = extract_companies(state["query"], state.get("report_text", ""))
    state["companies"] = companies
    record_event(state, "retrieval_agent", "ok", f"Detected companies: {', '.join(companies)}")


def analyst_agent(state: AnalysisState) -> None:
    extracted_facts = extract_financial_facts(state.get("report_text", ""), state["companies"])
    metrics = {company: calculate_metrics(company, extracted_facts.get(company)) for company in state["companies"]}
    state["extracted_facts"] = extracted_facts
    state["metrics"] = metrics
    snapshot = checkpoint(state)
    fact_count = sum(len(facts) for facts in extracted_facts.values())
    record_event(
        state,
        "analyst_agent",
        "ok",
        f"Calculated {snapshot['metric_count']} metric values using {fact_count} extracted facts.",
    )


def synthesizer_agent(state: AnalysisState, llm_client: BaseLLMClient | None = None) -> None:
    summary = build_summary(state["companies"], state["metrics"])
    if llm_client is not None:
        summary = llm_client.summarize(
            summary,
            {
                "query": state["query"],
                "companies": state["companies"],
                "extracted_facts": state.get("extracted_facts", {}),
                "metrics": state["metrics"],
            },
        )
        state["llm_provider"] = llm_client.provider
    else:
        state["llm_provider"] = "local"
    state["summary"] = summary
    record_event(state, "synthesizer_agent", "ok", f"Summary assembled with {state['llm_provider']} provider.")
