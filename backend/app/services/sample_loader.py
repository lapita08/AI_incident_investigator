import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.entities import Incident
from app.schemas.evidence import EvidenceCreate
from app.schemas.incidents import IncidentCreate
from app.services.evidence_ingestion import EvidenceIngestionService


class SampleLoader:
    def __init__(self, db: Session, sample_root: Path, *, redact_ips: bool = False) -> None:
        self.db = db
        self.sample_root = sample_root
        self.redact_ips = redact_ips

    def load(self, scenario_id: str) -> Incident:
        path = self.sample_root / scenario_id / "scenario.json"
        payload = json.loads(path.read_text())
        incident_data = IncidentCreate(**payload["incident"])
        incident = Incident(**incident_data.model_dump())
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        ingestion = EvidenceIngestionService(self.db, redact_ips=self.redact_ips)
        for item in payload["evidence"]:
            ingestion.ingest(incident.id, EvidenceCreate(**item))
        self.db.refresh(incident)
        return incident

