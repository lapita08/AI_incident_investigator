from app.core.config import Settings
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.provider import LLMProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    return MockLLMProvider()

