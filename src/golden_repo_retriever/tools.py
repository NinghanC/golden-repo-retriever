from __future__ import annotations

from .sample_data import SAMPLE_FINANCIAL_DATA


def extract_companies(query: str, report_text: str = "") -> list[str]:
    """Find known companies mentioned in the query or report text."""
    lowered = f"{query}\n{report_text}".lower()
    companies = [name for name in SAMPLE_FINANCIAL_DATA if name.lower() in lowered]
    return companies or ["Apple", "Microsoft"]


def calculate_metrics(company: str, facts: dict[str, float | str] | None = None) -> dict[str, float | str]:
    """Calculate finance ratios from extracted facts, with sample data fallback."""
    facts = facts or {}
    data = SAMPLE_FINANCIAL_DATA[company]
    revenue = float(facts.get("revenue", data["revenue"]))
    ebitda = float(facts.get("ebitda", data["ebitda"]))
    r_and_d = float(facts.get("r_and_d", data["r_and_d"]))
    ebitda_margin = facts.get("ebitda_margin")
    r_and_d_intensity = facts.get("r_and_d_intensity")
    return {
        "ebitda_margin": round(float(ebitda_margin), 4) if ebitda_margin is not None else round(ebitda / revenue, 4),
        "r_and_d_intensity": (
            round(float(r_and_d_intensity), 4) if r_and_d_intensity is not None else round(r_and_d / revenue, 4)
        ),
        "supply_chain_risk": str(facts.get("supply_chain_risk", data["supply_chain_risk"])),
    }


def build_summary(companies: list[str], metrics: dict[str, dict[str, float | str]]) -> str:
    """Create a plain English summary without any cloud model."""
    lines = []
    for company in companies:
        company_metrics = metrics[company]
        ebitda_margin = float(company_metrics["ebitda_margin"])
        r_and_d_intensity = float(company_metrics["r_and_d_intensity"])
        risk = company_metrics["supply_chain_risk"]
        lines.append(
            f"{company}: EBITDA margin {ebitda_margin:.1%}, "
            f"R&D intensity {r_and_d_intensity:.1%}, supply chain risk {risk}."
        )
    return " ".join(lines)
