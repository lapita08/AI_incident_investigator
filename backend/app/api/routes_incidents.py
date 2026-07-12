from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_incident_or_404, settings_dep
from app.core.config import Settings
from app.models.entities import Incident
from app.repositories.incidents import IncidentRepository
from app.schemas.incidents import IncidentCreate, IncidentRead, IncidentUpdate
from app.services.sample_loader import SampleLoader

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead)
def create_incident(payload: IncidentCreate, db: Session = Depends(db_session)) -> Incident:
    incident = Incident(**payload.model_dump())
    return IncidentRepository(db).add(incident)


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(db_session)) -> list[Incident]:
    return IncidentRepository(db).list_incidents()


@router.get("/{incident_id}", response_model=IncidentRead)
def read_incident(incident: Incident = Depends(get_incident_or_404)) -> Incident:
    return incident


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(payload: IncidentUpdate, incident: Incident = Depends(get_incident_or_404), db: Session = Depends(db_session)) -> Incident:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, key, value)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/sample/{scenario_id}", response_model=IncidentRead)
def load_sample(scenario_id: str, db: Session = Depends(db_session), settings: Settings = Depends(settings_dep)) -> Incident:
    return SampleLoader(db, settings.sample_data_dir, redact_ips=settings.redact_ip_addresses).load(scenario_id)
