from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMModel


class TimelineEventRead(ORMModel):
    id: str
    incident_id: str
    timestamp: datetime | None
    event_type: str
    service: str | None
    title: str
    description: str
    evidence_ids: list[str]
    confidence: str
    source: str


class HypothesisRead(ORMModel):
    id: str
    incident_id: str
    rank: int
    title: str
    description: str
    confidence: str
    status: str
    supporting_evidence_ids: list[str]
    contradicting_evidence_ids: list[str]
    missing_evidence: list[str]
    validation_steps: list[str]
    generated_by: str
    created_at: datetime | None = None


class HypothesisUpdate(BaseModel):
    status: str


class RecommendedActionRead(ORMModel):
    id: str
    incident_id: str
    hypothesis_id: str | None
    action_type: str
    title: str
    description: str
    risk_level: str
    expected_result: str
    prerequisites: list[str]
    validation: list[str]
    rollback_considerations: str
    requires_approval: bool
    command_example: str | None
    status: str


class InvestigationReport(BaseModel):
    executive_summary: str
    confirmed_facts: list[str]
    unknowns: list[str]
    timeline: list[dict[str, Any]]
    affected_components: list[str]
    blast_radius: dict[str, Any]
    hypotheses: list[dict[str, Any]]
    next_steps: list[dict[str, Any]]
    mitigations: list[dict[str, Any]]
    communication_update: dict[str, str]
    postmortem_draft: dict[str, Any]
    deterministic_findings: dict[str, Any]

