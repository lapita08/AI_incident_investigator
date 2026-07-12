from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_incident_or_404
from app.models.entities import Incident
from app.repositories.incidents import IncidentRepository
from app.services.export_service import export_json, export_markdown

router = APIRouter(prefix="/api/v1/incidents/{incident_id}", tags=["outputs"])


@router.post("/communications")
def communications(incident: Incident = Depends(get_incident_or_404)) -> dict:
    drafts = (incident.report or {}).get("communication_update", {})
    return {"drafts_require_review": True, **drafts}


@router.post("/postmortem")
def postmortem(incident: Incident = Depends(get_incident_or_404)) -> dict:
    return {"draft_requires_review": True, "postmortem": (incident.report or {}).get("postmortem_draft", {})}


@router.get("/export", response_model=None)
def export(incident: Incident = Depends(get_incident_or_404), db: Session = Depends(db_session), format: str = "json"):
    repo = IncidentRepository(db)
    payload = export_json(incident, repo.evidence(incident.id), repo.timeline(incident.id), repo.hypotheses(incident.id), repo.actions(incident.id))
    if format == "markdown":
        return Response(content=export_markdown(payload), media_type="text/markdown")
    return payload
