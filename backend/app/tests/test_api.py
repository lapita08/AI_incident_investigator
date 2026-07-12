from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app
from app.models.database import Base, engine


def test_incident_creation_evidence_analysis_and_export(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "sample_data_dir", Path("../sample-data"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client = TestClient(create_app())

    loaded = client.post("/api/v1/incidents/sample/db-latency-incident")
    assert loaded.status_code == 200
    incident_id = loaded.json()["id"]

    analyzed = client.post(f"/api/v1/incidents/{incident_id}/analyze")
    assert analyzed.status_code == 200
    assert analyzed.json()["status"] == "completed"

    hypotheses = client.get(f"/api/v1/incidents/{incident_id}/hypotheses").json()
    assert hypotheses
    assert hypotheses[0]["supporting_evidence_ids"]

    exported = client.get(f"/api/v1/incidents/{incident_id}/export")
    assert exported.status_code == 200
    assert exported.json()["hypotheses"][0]["supporting_evidence_ids"]

