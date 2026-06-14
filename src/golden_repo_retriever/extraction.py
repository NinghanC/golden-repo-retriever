from __future__ import annotations

import re


ExtractedFacts = dict[str, dict[str, float | str]]
Evidence = dict[str, list[dict[str, float | str]]]


def extract_financial_facts_with_evidence(report_text: str, companies: list[str]) -> tuple[ExtractedFacts, Evidence]:
    facts: ExtractedFacts = {}
    evidence: Evidence = {}
    if not report_text.strip():
        return facts, evidence

    for company in companies:
        company_facts, company_evidence = _extract_company_facts_with_evidence(report_text, company)
        if company_facts:
            facts[company] = company_facts
        if company_evidence:
            evidence[company] = company_evidence
    return facts, evidence


def extract_financial_facts(report_text: str, companies: list[str]) -> ExtractedFacts:
    """Extract simple structured finance facts from report text."""
    facts, _ = extract_financial_facts_with_evidence(report_text, companies)
    return facts


def _extract_company_facts(report_text: str, company: str) -> dict[str, float | str]:
    facts, _ = _extract_company_facts_with_evidence(report_text, company)
    return facts


def _extract_company_facts_with_evidence(report_text: str, company: str) -> tuple[dict[str, float | str], list[dict[str, float | str]]]:
    text = _company_context(report_text, company)
    facts: dict[str, float | str] = {}
    evidence: list[dict[str, float | str]] = []

    _record_money_fact(facts, evidence, text, "revenue", ["revenue", "sales"])
    _record_money_fact(facts, evidence, text, "ebitda", ["ebitda"])
    _record_percent_fact(facts, evidence, text, "ebitda_margin", ["ebitda margin", "adjusted ebitda margin"])
    _record_money_fact(facts, evidence, text, "r_and_d", ["r&d", "research and development"])
    _record_percent_fact(
        facts,
        evidence,
        text,
        "r_and_d_intensity",
        ["r&d intensity", "research and development intensity"],
    )
    risk_result = _extract_supply_chain_risk(text)
    if risk_result is not None:
        value, snippet = risk_result
        facts["supply_chain_risk"] = value
        evidence.append({"field": "supply_chain_risk", "value": value, "snippet": snippet})

    return facts, evidence


def _record_money_fact(
    facts: dict[str, float | str],
    evidence: list[dict[str, float | str]],
    text: str,
    field: str,
    labels: list[str],
) -> None:
    result = _extract_money(text, labels)
    if result is None:
        return
    value, snippet = result
    facts[field] = value
    evidence.append({"field": field, "value": value, "snippet": snippet})


def _record_percent_fact(
    facts: dict[str, float | str],
    evidence: list[dict[str, float | str]],
    text: str,
    field: str,
    labels: list[str],
) -> None:
    result = _extract_percent(text, labels)
    if result is None:
        return
    value, snippet = result
    facts[field] = value
    evidence.append({"field": field, "value": value, "snippet": snippet})


def _company_context(report_text: str, company: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", report_text)
    matches = [sentence for sentence in sentences if company.lower() in sentence.lower()]
    return " ".join(matches) or report_text


def _extract_money(text: str, labels: list[str]) -> tuple[float, str] | None:
    for label in labels:
        escaped = re.escape(label)
        patterns = [
            rf"{escaped}\s+(?:was|were|is|of|at|totaled|totalled|reached)?\s*\$?\s*({_NUMBER_RE})\s*(billion|million|bn|m)?",
            rf"\$?\s*({_NUMBER_RE})\s*(billion|million|bn|m)?\s+(?:in|of)?\s*{escaped}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return _normalize_number(match.group(1), match.group(2)), _sentence_for_match(text, match)
    return None


def _extract_percent(text: str, labels: list[str]) -> tuple[float, str] | None:
    for label in labels:
        escaped = re.escape(label)
        patterns = [
            rf"{escaped}\s+(?:was|were|is|of|at)?\s*({_NUMBER_RE})\s*%",
            rf"({_NUMBER_RE})\s*%\s+{escaped}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return round(float(match.group(1).replace(",", "")) / 100, 4), _sentence_for_match(text, match)
    return None


def _extract_supply_chain_risk(text: str) -> tuple[str, str] | None:
    match = re.search(
        r"supply chain risk\s+(?:was|were|is|remains|remained|rated)?\s*(low|medium|moderate|high)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    risk = match.group(1).lower()
    value = "medium" if risk == "moderate" else risk
    return value, _sentence_for_match(text, match)


def _normalize_number(raw_value: str, raw_unit: str | None) -> float:
    value = float(raw_value.replace(",", ""))
    unit = (raw_unit or "").lower()
    if unit in {"million", "m"}:
        return round(value / 1000, 4)
    return value


def _sentence_for_match(text: str, match: re.Match[str]) -> str:
    sentence_start = text.rfind(".", 0, match.start()) + 1
    sentence_end = text.find(".", match.end())
    if sentence_end == -1:
        sentence_end = len(text)
    else:
        sentence_end += 1
    return " ".join(text[sentence_start:sentence_end].split())


_NUMBER_RE = r"\d+(?:,\d{3})*(?:\.\d+)?"
