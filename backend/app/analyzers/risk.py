HIGH_RISK_TERMS = ["rollback", "restart", "kill", "delete", "flush", "write query", "firewall", "scale", "feature flag"]
CRITICAL_TERMS = ["drop table", "delete database", "delete the database", "deleting the database", "truncate", "disable auth"]


def classify_action_risk(text: str) -> tuple[str, bool]:
    lowered = text.lower()
    if any(term in lowered for term in CRITICAL_TERMS):
        return "critical", True
    if any(term in lowered for term in HIGH_RISK_TERMS):
        return "high", True
    if any(term in lowered for term in ["throttle", "disable job", "change limit"]):
        return "medium", True
    return "low", False
