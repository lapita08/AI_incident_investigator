from typing import Any

from app.llm.mock_provider import MockLLMProvider
from app.llm.provider import LLMProvider, LLMReport


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_report(self, evidence_package: dict[str, Any]) -> LLMReport:
        if not self.api_key:
            return MockLLMProvider().generate_report(evidence_package)
        # The extension point is intentionally isolated. The production implementation
        # should send only the deterministic evidence package, with evidence text marked
        # as untrusted data and structured output validated by LLMReport.
        return MockLLMProvider().generate_report(evidence_package)

