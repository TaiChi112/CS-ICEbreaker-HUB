from __future__ import annotations

from app.core.config import Settings
from app.domain.llm import LlmProvider
from app.infrastructure.llm.mock_provider import MockLlmProvider
from app.infrastructure.llm.openai_provider import OpenAiLlmProvider


def create_llm_provider(settings: Settings) -> LlmProvider:
    provider = settings.llm_provider.strip().lower()

    if provider == "openai":
        if settings.openai_api_key:
            return OpenAiLlmProvider(api_key=settings.openai_api_key, model=settings.openai_model)
        if settings.llm_fallback_enabled:
            return MockLlmProvider()
        raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

    if provider == "anthropic":
        if settings.llm_fallback_enabled:
            return MockLlmProvider()
        raise ValueError("Anthropic provider is not implemented yet.")

    if provider == "mock":
        return MockLlmProvider()

    if settings.llm_fallback_enabled:
        return MockLlmProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
