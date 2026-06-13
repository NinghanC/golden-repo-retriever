from __future__ import annotations

import re


ExtractedFacts = dict[str, dict[str, float | str]]


def extract_financial_facts(report_text: str, companies: list[str]) -> ExtractedFacts:
    """Extract simple structured finance facts from report text."""
    facts: ExtractedFacts = {}
    if not report_text.strip():
        return facts

    for company in companies:
        company_facts = _extract_company_facts(report_text, company)
        if company_facts:
            facts[company] = company_facts
    return facts


def _extract_company_facts(report_text: str, company: str) -> dict[str, float | str]:
    text = _company_context(report_text, company)
    facts: dict[str, float | str] = {}

    revenue = _extract_money(text, ["revenue", "sales"])
    if revenue is not None:
        facts["revenue"] = revenue

    ebitda = _extract_money(text, ["ebitda"])
    if ebitda is not None:
        facts["ebitda"] = ebitda

    ebitda_margin = _extract_percent(text, ["ebitda margin", "adjusted ebitda margin"])
    if ebitda_margin is not None:
        facts["ebitda_margin"] = ebitda_margin

    r_and_d = _extract_money(text, ["r&d", "research and development"])
    if r_and_d is not None:
        facts["r_and_d"] = r_and_d

    r_and_d_intensity = _extract_percent(text, ["r&d intensity", "research and development intensity"])
    if r_and_d_intensity is not None:
        facts["r_and_d_intensity"] = r_and_d_intensity

    risk = _extract_supply_chain_risk(text)
    if risk is not None:
        facts["supply_chain_risk"] = risk

    return facts


def _company_context(report_text: str, company: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", report_text)
    matches = [sentence for sentence in sentences if company.lower() in sentence.lower()]
    return " ".join(matches) or report_text


def _extract_money(text: str, labels: list[str]) -> float | None:
    for label in labels:
        escaped = re.escape(label)
        patterns = [
            rf"{escaped}\s+(?:was|were|is|of|at|totaled|totalled|reached)?\s*\$?\s*({_NUMBER_RE})\s*(billion|million|bn|m)?",
            rf"\$?\s*({_NUMBER_RE})\s*(billion|million|bn|m)?\s+(?:in|of)?\s*{escaped}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return _normalize_number(match.group(1), match.group(2))
    return None


def _extract_percent(text: str, labels: list[str]) -> float | None:
    for label in labels:
        escaped = re.escape(label)
        patterns = [
            rf"{escaped}\s+(?:was|were|is|of|at)?\s*({_NUMBER_RE})\s*%",
            rf"({_NUMBER_RE})\s*%\s+{escaped}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return round(float(match.group(1).replace(",", "")) / 100, 4)
    return None


def _extract_supply_chain_risk(text: str) -> str | None:
    match = re.search(
        r"supply chain risk\s+(?:was|were|is|remains|remained|rated)?\s*(low|medium|moderate|high)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    risk = match.group(1).lower()
    return "medium" if risk == "moderate" else risk


def _normalize_number(raw_value: str, raw_unit: str | None) -> float:
    value = float(raw_value.replace(",", ""))
    unit = (raw_unit or "").lower()
    if unit in {"million", "m"}:
        return round(value / 1000, 4)
    return value


_NUMBER_RE = r"\d+(?:,\d{3})*(?:\.\d+)?"
