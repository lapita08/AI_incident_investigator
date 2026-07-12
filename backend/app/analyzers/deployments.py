from datetime import timedelta
from typing import Any

from app.analyzers.time_utils import parse_timestamp


def deployment_correlations(evidence_items: list[Any], incident_start: object, window_minutes: int = 60) -> list[dict[str, Any]]:
    start = parse_timestamp(incident_start)
    if not start:
        starts = []
        for item in evidence_items:
            if item.timestamp:
                starts.append(item.timestamp)
        start = min(starts) if starts else None
    if not start:
        return []
    correlated: list[dict[str, Any]] = []
    for item in evidence_items:
        if item.evidence_type != "deployment":
            continue
        deployments = item.normalized_content.get("deployments")
        if isinstance(deployments, dict):
            deployments = [deployments]
        for deploy in deployments or []:
            deployed_at = parse_timestamp(deploy.get("timestamp") or deploy.get("deployed_at"))
            if not deployed_at:
                continue
            delta = start - deployed_at
            if timedelta(minutes=0) <= delta <= timedelta(minutes=window_minutes):
                correlated.append(
                    {
                        "service": deploy.get("service"),
                        "version": deploy.get("version"),
                        "commit_sha": deploy.get("commit_sha"),
                        "timestamp": deployed_at.isoformat(),
                        "minutes_before_first_signal": round(delta.total_seconds() / 60, 1),
                        "statement": f"A deployment occurred {round(delta.total_seconds() / 60, 1)} minutes before the first detected signal; this is correlation, not causation.",
                        "evidence_ids": [item.display_id],
                    }
                )
    return sorted(correlated, key=lambda row: row["minutes_before_first_signal"])

