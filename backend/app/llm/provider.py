from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class LLMHypothesis(BaseModel):
    title: str
    description: str
    confidence: str = Field(pattern="^(low|medium|high)$")
    supporting_evidence_ids: list[str]
    contradicting_evidence_ids: list[str] = []
    missing_evidence: list[str] = []
    validation_steps: list[str] = []


class LLMAction(BaseModel):
    action_type: str
    title: str
    description: str
    risk_level: str
    expected_result: str
    prerequisites: list[str] = []
    validation: list[str] = []
    rollback_considerations: str = ""
    requires_approval: bool = False
    command_example: str | None = None


class LLMReport(BaseModel):
    executive_summary: str
    confirmed_facts: list[str]
    unknowns: list[str]
    hypotheses: list[LLMHypothesis]
    actions: list[LLMAction]
    communication_update: dict[str, str]
    postmortem_draft: dict[str, Any]


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate_report(self, evidence_package: dict[str, Any]) -> LLMReport:
        """Generate structured analysis from trusted deterministic facts."""

