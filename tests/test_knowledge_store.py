from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from golden_repo_retriever.knowledge_store import KnowledgeStore


class KnowledgeStoreTestCase(unittest.TestCase):
    def test_save_from_analysis_persists_facts_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = KnowledgeStore(Path(tmp_dir) / "knowledge.db")
            result = {
                "report_source": "report:1",
                "extracted_facts": {"Microsoft": {"revenue": 245.1}},
                "evidence": {
                    "Microsoft": [
                        {
                            "field": "revenue",
                            "value": 245.1,
                            "snippet": "Microsoft revenue was $245.1 billion.",
                        }
                    ]
                },
            }

            saved_count = store.save_from_analysis(analysis_id=7, result=result)
            facts = store.list_company_facts("Microsoft")

        self.assertEqual(saved_count, 1)
        self.assertEqual(facts[0]["company"], "Microsoft")
        self.assertEqual(facts[0]["field"], "revenue")
        self.assertEqual(facts[0]["value"], "245.1")
        self.assertEqual(facts[0]["source"], "report:1")
        self.assertEqual(facts[0]["snippet"], "Microsoft revenue was $245.1 billion.")
        self.assertEqual(facts[0]["analysis_id"], 7)

    def test_list_facts_returns_recent_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = KnowledgeStore(Path(tmp_dir) / "knowledge.db")
            store.save_fact("Apple", "revenue", 412.0, "analysis")
            store.save_fact("Microsoft", "revenue", 245.1, "analysis")

            facts = store.list_facts()

        self.assertEqual(facts[0]["company"], "Microsoft")
        self.assertEqual(facts[1]["company"], "Apple")


if __name__ == "__main__":
    unittest.main()
