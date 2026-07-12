from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import EvidenceItem, Hypothesis, Incident, RecommendedAction, TimelineEvent


class IncidentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, incident_id: str) -> Incident | None:
        return self.db.get(Incident, incident_id)

    def list_incidents(self) -> list[Incident]:
        return list(self.db.scalars(select(Incident).order_by(Incident.created_at.desc())).all())

    def add(self, incident: Incident) -> Incident:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def delete_analysis(self, incident_id: str) -> None:
        for model in (TimelineEvent, Hypothesis, RecommendedAction):
            for item in self.db.scalars(select(model).where(model.incident_id == incident_id)):
                self.db.delete(item)
        self.db.flush()

    def evidence(self, incident_id: str) -> list[EvidenceItem]:
        return list(self.db.scalars(select(EvidenceItem).where(EvidenceItem.incident_id == incident_id).order_by(EvidenceItem.created_at)).all())

    def hypotheses(self, incident_id: str) -> list[Hypothesis]:
        return list(self.db.scalars(select(Hypothesis).where(Hypothesis.incident_id == incident_id).order_by(Hypothesis.rank)).all())

    def actions(self, incident_id: str) -> list[RecommendedAction]:
        return list(self.db.scalars(select(RecommendedAction).where(RecommendedAction.incident_id == incident_id).order_by(RecommendedAction.action_type, RecommendedAction.risk_level)).all())

    def timeline(self, incident_id: str) -> list[TimelineEvent]:
        return list(self.db.scalars(select(TimelineEvent).where(TimelineEvent.incident_id == incident_id).order_by(TimelineEvent.timestamp)).all())
