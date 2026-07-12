from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analyzers.parsers import normalize_evidence
from app.analyzers.time_utils import parse_timestamp
from app.domain.enums import EvidenceType
from app.models.entities import EvidenceItem
from app.observability.metrics import EVIDENCE_INGESTION_COUNT, PARSING_FAILURES
from app.schemas.evidence import EvidenceCreate, EvidenceIngestResponse, EvidenceRead
from app.security.input_validation import validate_upload_text
from app.security.redaction import redact_sensitive_text

PREFIX = {
    EvidenceType.alert: "ALERT",
    EvidenceType.log: "LOG",
    EvidenceType.metric: "METRIC",
    EvidenceType.deployment: "DEPLOY",
    EvidenceType.runbook: "RUNBOOK",
    EvidenceType.dependency: "DEP",
    EvidenceType.observation: "OBS",
}


class EvidenceIngestionService:
    def __init__(self, db: Session, *, redact_ips: bool = False) -> None:
        self.db = db
        self.redact_ips = redact_ips

    def ingest(self, incident_id: str, payload: EvidenceCreate) -> EvidenceIngestResponse:
        validate_upload_text(payload.raw_content)
        raw_content = redact_sensitive_text(payload.raw_content, redact_ips=self.redact_ips)
        normalized, stats = normalize_evidence(payload.evidence_type, raw_content)
        if stats.unparsed_lines:
            PARSING_FAILURES.labels(type=payload.evidence_type.value).inc()
        display_id = self._next_display_id(incident_id, payload.evidence_type)
        timestamp = payload.timestamp or self._infer_timestamp(payload.evidence_type, normalized)
        service = payload.service or self._infer_service(payload.evidence_type, normalized)
        item = EvidenceItem(
            incident_id=incident_id,
            display_id=display_id,
            evidence_type=payload.evidence_type.value,
            source=payload.source,
            service=service,
            environment=payload.environment,
            timestamp=timestamp,
            raw_content=raw_content,
            normalized_content=normalized,
            metadata_=payload.metadata,
            ingestion_status="parsed" if stats.unparsed_lines == 0 else "partially_parsed",
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        EVIDENCE_INGESTION_COUNT.labels(type=payload.evidence_type.value).inc()
        return EvidenceIngestResponse(evidence=EvidenceRead.model_validate(item), parsing_stats=stats)

    def _next_display_id(self, incident_id: str, evidence_type: EvidenceType) -> str:
        count = self.db.scalar(select(func.count()).select_from(EvidenceItem).where(EvidenceItem.incident_id == incident_id, EvidenceItem.evidence_type == evidence_type.value)) or 0
        return f"{PREFIX[evidence_type]}-{count + 1:03d}"

    @staticmethod
    def _infer_timestamp(evidence_type: EvidenceType, normalized: dict) -> object:
        if evidence_type == EvidenceType.alert:
            return parse_timestamp(normalized.get("start_time"))
        if evidence_type == EvidenceType.metric:
            records = normalized.get("records", [])
            timestamps: list[datetime] = [ts for row in records if (ts := parse_timestamp(row.get("timestamp")))]
            return min(timestamps) if timestamps else None
        if evidence_type == EvidenceType.deployment:
            deployments = normalized.get("deployments")
            if isinstance(deployments, list) and deployments:
                return parse_timestamp(deployments[0].get("timestamp") or deployments[0].get("deployed_at"))
        return None

    @staticmethod
    def _infer_service(evidence_type: EvidenceType, normalized: dict) -> str | None:
        if evidence_type == EvidenceType.alert:
            return normalized.get("service")
        if evidence_type == EvidenceType.log:
            services = normalized.get("services", [])
            return services[0] if len(services) == 1 else None
        return None
