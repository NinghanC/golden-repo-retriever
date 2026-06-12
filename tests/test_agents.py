from __future__ import annotations

import unittest

from golden_repo_retriever.agents import analyst_agent, retrieval_agent, synthesizer_agent
from golden_repo_retriever.state import AnalysisState


class AgentsTestCase(unittest.TestCase):
    def test_agents_update_shared_state(self) -> None:
        state: AnalysisState = {
            "query": "Compare Apple.",
            "audit_log": [],
        }

        retrieval_agent(state)
        analyst_agent(state)
        synthesizer_agent(state)

        self.assertEqual(state["companies"], ["Apple"])
        self.assertIn("ebitda_margin", state["metrics"]["Apple"])
        self.assertIn("Apple", state["summary"])
        self.assertEqual(
            [event["step"] for event in state["audit_log"]],
            ["retrieval_agent", "analyst_agent", "synthesizer_agent"],
        )


if __name__ == "__main__":
    unittest.main()
