from __future__ import annotations

from .sample_data import SAMPLE_FINANCIAL_DATA


def extract_companies(query: str) -> list[str]:
    """Find known companies mentioned in the query."""
    lowered = query.lower()
    companies = [name for name in SAMPLE_FINANCIAL_DATA if name.lower() in lowered]
    return companies or ["Apple", "Microsoft"]


def calculate_metrics(company: str) -> dict[str, float | str]:
    """Calculate the first useful finance ratios from sample data."""
    data = SAMPLE_FINANCIAL_DATA[company]
    revenue = data["revenue"]
    ebitda = data["ebitda"]
    r_and_d = data["r_and_d"]
    return {
        "ebitda_margin": round(ebitda / revenue, 4),
        "r_and_d_intensity": round(r_and_d / revenue, 4),
        "supply_chain_risk": data["supply_chain_risk"],
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
