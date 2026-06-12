from __future__ import annotations

import unittest
from unittest.mock import patch

from golden_repo_retriever import run_analysis
from golden_repo_retriever.llm import BaseLLMClient, LLMSettings, LocalFallbackLLMClient, build_llm_client


class MockLLMClient(BaseLLMClient):
    provider = "mock"

    def summarize(self, summary: str, context: dict[str, object]) -> str:
        return f"LLM summary: {summary}"


class LLMTestCase(unittest.TestCase):
    def test_local_fallback_returns_input_summary(self) -> None:
        client = LocalFallbackLLMClient()

        self.assertEqual(client.summarize("plain summary", {}), "plain summary")

    def test_default_provider_is_local(self) -> None:
        with patch.dict("os.environ", {"LLM_PROVIDER": "local"}, clear=True):
            settings = LLMSettings.from_env()
            client = build_llm_client(settings=settings)

        self.assertEqual(settings.provider, "local")
        self.assertEqual(client.provider, "local")

    def test_openai_without_key_falls_back_to_local(self) -> None:
        with patch.dict("os.environ", {"LLM_PROVIDER": "openai"}, clear=True):
            client = build_llm_client()
            result = client.summarize("plain summary", {})

        self.assertEqual(client.provider, "local")
        self.assertEqual(result, "plain summary")

    def test_workflow_accepts_mock_llm_client(self) -> None:
        result = run_analysis("Compare Apple.", llm_client=MockLLMClient())

        self.assertEqual(result["llm_provider"], "mock")
        self.assertTrue(result["summary"].startswith("LLM summary:"))


if __name__ == "__main__":
    unittest.main()
