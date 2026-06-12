from __future__ import annotations

import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    api_key: str | None
    base_url: str
    model: str
    timeout_seconds: float

    @classmethod
    def from_env(cls, provider: str | None = None) -> "LLMSettings":
        selected = (provider or os.getenv("LLM_PROVIDER") or "local").strip().lower()
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS") or "45")

        if selected == "openai":
            return cls(
                provider="openai",
                api_key=os.getenv("OPENAI_API_KEY") or None,
                base_url=os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1",
                model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
                timeout_seconds=timeout,
            )
        if selected == "mistral":
            return cls(
                provider="mistral",
                api_key=os.getenv("MISTRAL_API_KEY") or None,
                base_url=os.getenv("MISTRAL_BASE_URL") or "https://api.mistral.ai/v1",
                model=os.getenv("MISTRAL_MODEL") or "mistral-small-latest",
                timeout_seconds=timeout,
            )
        if selected == "custom":
            return cls(
                provider="custom",
                api_key=os.getenv("LLM_API_KEY") or None,
                base_url=os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1",
                model=os.getenv("LLM_MODEL") or "gpt-4o-mini",
                timeout_seconds=timeout,
            )
        return cls(
            provider="local",
            api_key=None,
            base_url="",
            model="local-fallback",
            timeout_seconds=timeout,
        )


class BaseLLMClient:
    provider = "unknown"

    def summarize(self, summary: str, context: dict[str, object]) -> str:
        raise NotImplementedError


class LocalFallbackLLMClient(BaseLLMClient):
    provider = "local"

    def summarize(self, summary: str, context: dict[str, object]) -> str:
        return summary


class OpenAICompatibleLLMClient(BaseLLMClient):
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self.provider = settings.provider

    def summarize(self, summary: str, context: dict[str, object]) -> str:
        url = f"{self.settings.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Rewrite the finance analysis summary in concise, professional English.",
                },
                {
                    "role": "user",
                    "content": f"Summary:\n{summary}\n\nContext:\n{context}",
                },
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        }
        with httpx.Client(timeout=self.settings.timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()


class ResilientLLMClient(BaseLLMClient):
    def __init__(self, primary: BaseLLMClient | None, fallback: BaseLLMClient | None = None) -> None:
        self.primary = primary
        self.fallback = fallback or LocalFallbackLLMClient()
        self.provider = primary.provider if primary else self.fallback.provider

    def summarize(self, summary: str, context: dict[str, object]) -> str:
        if self.primary is None:
            self.provider = self.fallback.provider
            return self.fallback.summarize(summary, context)
        try:
            self.provider = self.primary.provider
            return self.primary.summarize(summary, context)
        except Exception:
            self.provider = self.fallback.provider
            return self.fallback.summarize(summary, context)


def build_llm_client(provider: str | None = None, settings: LLMSettings | None = None) -> ResilientLLMClient:
    selected_settings = settings or LLMSettings.from_env(provider)
    primary: BaseLLMClient | None = None
    if selected_settings.provider != "local" and selected_settings.api_key:
        primary = OpenAICompatibleLLMClient(selected_settings)
    return ResilientLLMClient(primary=primary, fallback=LocalFallbackLLMClient())
