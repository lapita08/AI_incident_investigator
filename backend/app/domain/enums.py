from enum import StrEnum


class Severity(StrEnum):
    sev1 = "sev1"
    sev2 = "sev2"
    sev3 = "sev3"
    sev4 = "sev4"


class IncidentStatus(StrEnum):
    investigating = "investigating"
    identified = "identified"
    monitoring = "monitoring"
    resolved = "resolved"


class EvidenceType(StrEnum):
    alert = "alert"
    log = "log"
    metric = "metric"
    deployment = "deployment"
    runbook = "runbook"
    dependency = "dependency"
    observation = "observation"


class AnalysisStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Confidence(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class HypothesisStatus(StrEnum):
    proposed = "proposed"
    investigating = "investigating"
    confirmed = "confirmed"
    rejected = "rejected"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

