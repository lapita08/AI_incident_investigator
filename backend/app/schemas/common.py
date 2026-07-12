from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIError(BaseModel):
    error: str
    detail: str | dict[str, Any] | None = None


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimestampedModel(ORMModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EvidenceRef(BaseModel):
    evidence_id: str
    label: str = Field(description="Human readable evidence display ID")

