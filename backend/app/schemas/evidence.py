from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import EvidenceType
from app.schemas.common import ORMModel


class EvidenceCreate(BaseModel):
    evidence_type: EvidenceType
    raw_content: str = Field(min_length=1)
    source: str = "manual"
    service: str | None = None
    environment: str | None = None
    timestamp: datetime | None = None
    metadata: dict[str, Any] = {}


class EvidenceRead(ORMModel):
    id: str
    display_id: str
    incident_id: str
    evidence_type: str
    source: str
    service: str | None
    environment: str | None
    timestamp: datetime | None
    raw_content: str
    normalized_content: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    ingestion_status: str
    created_at: datetime | None = None


class ParsingStats(BaseModel):
    total_lines: int = 0
    parsed_lines: int = 0
    unparsed_lines: int = 0
    warning_count: int = 0
    warnings: list[str] = []


class EvidenceIngestResponse(BaseModel):
    evidence: EvidenceRead
    parsing_stats: ParsingStats

