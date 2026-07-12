from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.llm.factory import build_llm_provider
from app.llm.provider import LLMProvider
from app.models.database import get_db
from app.models.entities import Incident


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def settings_dep() -> Settings:
    return get_settings()


def llm_provider_dep(settings: Settings = Depends(settings_dep)) -> LLMProvider:
    return build_llm_provider(settings)


def get_incident_or_404(incident_id: str, db: Session = Depends(db_session)) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident

