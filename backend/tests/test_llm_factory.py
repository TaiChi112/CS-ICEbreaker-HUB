from app.core.config import Settings
from app.infrastructure.llm.factory import create_llm_provider
from app.infrastructure.llm.mock_provider import MockLlmProvider
from app.infrastructure.llm.openai_provider import OpenAiLlmProvider


def test_factory_returns_openai_provider_when_key_available() -> None:
    settings = Settings(openai_api_key="test-key", llm_provider="openai")

    provider = create_llm_provider(settings)

    assert isinstance(provider, OpenAiLlmProvider)


def test_factory_falls_back_to_mock_provider() -> None:
    settings = Settings(openai_api_key="", llm_provider="openai", llm_fallback_enabled=True)

    provider = create_llm_provider(settings)

    assert isinstance(provider, MockLlmProvider)
