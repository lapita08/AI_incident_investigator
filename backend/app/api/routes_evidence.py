from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_incident_or_404, settings_dep
from app.core.config import Settings
from app.models.entities import EvidenceItem, Incident
from app.repositories.incidents import IncidentRepository
from app.schemas.evidence import EvidenceCreate, EvidenceIngestResponse, EvidenceRead
from app.services.evidence_ingestion import EvidenceIngestionService

router = APIRouter(prefix="/api/v1/incidents/{incident_id}/evidence", tags=["evidence"])


@router.post("", response_model=EvidenceIngestResponse)
def add_evidence(
    payload: EvidenceCreate,
    incident: Incident = Depends(get_incident_or_404),
    db: Session = Depends(db_session),
    settings: Settings = Depends(settings_dep),
) -> EvidenceIngestResponse:
    return EvidenceIngestionService(db, redact_ips=settings.redact_ip_addresses).ingest(incident.id, payload)


@router.get("", response_model=list[EvidenceRead])
def list_evidence(incident: Incident = Depends(get_incident_or_404), db: Session = Depends(db_session)) -> list[EvidenceItem]:
    return IncidentRepository(db).evidence(incident.id)

