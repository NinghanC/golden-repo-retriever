from __future__ import annotations

import unittest

from golden_repo_retriever.extraction import extract_financial_facts, extract_financial_facts_with_evidence


class ExtractionTestCase(unittest.TestCase):
    def test_extracts_financial_facts_from_report_text(self) -> None:
        text = (
            "Microsoft revenue was $245.1 billion. "
            "Microsoft EBITDA margin was 53%. "
            "Microsoft R&D was $29.5 billion. "
            "Microsoft supply chain risk remains low."
        )

        facts = extract_financial_facts(text, ["Microsoft"])

        self.assertEqual(facts["Microsoft"]["revenue"], 245.1)
        self.assertEqual(facts["Microsoft"]["ebitda_margin"], 0.53)
        self.assertEqual(facts["Microsoft"]["r_and_d"], 29.5)
        self.assertEqual(facts["Microsoft"]["supply_chain_risk"], "low")

    def test_extracts_evidence_snippets(self) -> None:
        text = "Microsoft revenue was $245.1 billion. Microsoft supply chain risk remains low."

        facts, evidence = extract_financial_facts_with_evidence(text, ["Microsoft"])

        self.assertEqual(facts["Microsoft"]["revenue"], 245.1)
        self.assertEqual(evidence["Microsoft"][0]["field"], "revenue")
        self.assertEqual(evidence["Microsoft"][0]["snippet"], "Microsoft revenue was $245.1 billion.")

    def test_converts_millions_to_billions(self) -> None:
        text = "Apple revenue was $412,000 million. Apple supply chain risk is medium."

        facts = extract_financial_facts(text, ["Apple"])

        self.assertEqual(facts["Apple"]["revenue"], 412.0)
        self.assertEqual(facts["Apple"]["supply_chain_risk"], "medium")

    def test_returns_empty_facts_without_report_text(self) -> None:
        facts = extract_financial_facts("", ["Apple"])

        self.assertEqual(facts, {})


if __name__ == "__main__":
    unittest.main()
