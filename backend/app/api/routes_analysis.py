from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_incident_or_404, llm_provider_dep
from app.llm.provider import LLMProvider
from app.models.entities import Hypothesis, Incident, RecommendedAction, TimelineEvent
from app.repositories.incidents import IncidentRepository
from app.schemas.analysis import HypothesisRead, HypothesisUpdate, RecommendedActionRead, TimelineEventRead
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1/incidents/{incident_id}", tags=["analysis"])


@router.post("/analyze")
def analyze_incident(
    incident: Incident = Depends(get_incident_or_404),
    db: Session = Depends(db_session),
    llm_provider: LLMProvider = Depends(llm_provider_dep),
) -> dict:
    updated = AnalysisService(db, llm_provider).analyze(incident)
    return {"status": updated.analysis_status, "report": updated.report}


@router.get("/timeline", response_model=list[TimelineEventRead])
def timeline(incident: Incident = Depends(get_incident_or_404), db: Session = Depends(db_session)) -> list[TimelineEvent]:
    return IncidentRepository(db).timeline(incident.id)


@router.get("/hypotheses", response_model=list[HypothesisRead])
def hypotheses(incident: Incident = Depends(get_incident_or_404), db: Session = Depends(db_session)) -> list[Hypothesis]:
    return IncidentRepository(db).hypotheses(incident.id)


@router.patch("/hypotheses/{hypothesis_id}", response_model=HypothesisRead)
def update_hypothesis(
    hypothesis_id: str,
    payload: HypothesisUpdate,
    incident: Incident = Depends(get_incident_or_404),
    db: Session = Depends(db_session),
) -> Hypothesis:
    hypothesis = db.get(Hypothesis, hypothesis_id)
    if not hypothesis or hypothesis.incident_id != incident.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hypothesis not found")
    if payload.status not in {"proposed", "investigating", "confirmed", "rejected"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hypothesis status")
    hypothesis.status = payload.status
    conclusions = incident.user_conclusions or {}
    conclusions[hypothesis_id] = payload.status
    incident.user_conclusions = conclusions
    db.commit()
    db.refresh(hypothesis)
    return hypothesis


@router.get("/actions", response_model=list[RecommendedActionRead])
def actions(incident: Incident = Depends(get_incident_or_404), db: Session = Depends(db_session)) -> list[RecommendedAction]:
    return IncidentRepository(db).actions(incident.id)

