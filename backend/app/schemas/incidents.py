from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import IncidentStatus, Severity
from app.schemas.common import TimestampedModel


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    description: str = ""
    severity: Severity = Severity.sev3
    status: IncidentStatus = IncidentStatus.investigating
    started_at: datetime | None = None
    detected_at: datetime | None = None
    affected_services: list[str] = []
    customer_impact: str = ""


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: Severity | None = None
    status: IncidentStatus | None = None
    resolved_at: datetime | None = None
    affected_services: list[str] | None = None
    customer_impact: str | None = None


class IncidentRead(TimestampedModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    started_at: datetime | None
    detected_at: datetime | None
    resolved_at: datetime | None
    affected_services: list[str]
    customer_impact: str
    analysis_status: str
    analysis_error: str | None = None
    report: dict = {}
    user_conclusions: dict = {}

