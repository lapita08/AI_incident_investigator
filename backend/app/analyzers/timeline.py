from datetime import UTC, datetime
from typing import Any

from app.analyzers.time_utils import parse_timestamp


def build_timeline(evidence_items: list[Any], anomalies: list[dict[str, Any]], deployments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for item in evidence_items:
        timestamp = item.timestamp
        normalized = item.normalized_content
        if item.evidence_type == "alert":
            timestamp = timestamp or parse_timestamp(normalized.get("start_time"))
            events.append(
                {
                    "timestamp": timestamp,
                    "event_type": "alert",
                    "service": item.service or normalized.get("service"),
                    "title": normalized.get("alert_name", "Alert fired"),
                    "description": f"Alert state: {normalized.get('state', 'unknown')}; observed value: {normalized.get('observed_value', 'unknown')}",
                    "evidence_ids": [item.display_id],
                    "confidence": "high",
                    "source": "deterministic",
                }
            )
        elif item.evidence_type == "log":
            for entry in normalized.get("entries", [])[:50]:
                ts = parse_timestamp(entry.get("timestamp")) or timestamp
                sev = str(entry.get("severity") or "").upper()
                if sev in {"ERROR", "FATAL", "WARN"}:
                    events.append(
                        {
                            "timestamp": ts,
                            "event_type": "log",
                            "service": item.service or entry.get("service"),
                            "title": f"{sev or 'log'} event",
                            "description": entry.get("message") or entry.get("raw", "")[:240],
                            "evidence_ids": [item.display_id],
                            "confidence": "medium",
                            "source": "deterministic",
                        }
                    )
    for anomaly in anomalies:
        events.append(
            {
                "timestamp": parse_timestamp(anomaly.get("timestamp")),
                "event_type": "metric_anomaly",
                "service": anomaly.get("service"),
                "title": f"{anomaly.get('metric_name')} {anomaly.get('direction')}",
                "description": f"Value {anomaly.get('value')} vs baseline {anomaly.get('baseline_mean')} ({anomaly.get('percentage_change')}%).",
                "evidence_ids": anomaly.get("evidence_ids", []),
                "confidence": "medium",
                "source": "deterministic",
            }
        )
    for deploy in deployments:
        events.append(
            {
                "timestamp": parse_timestamp(deploy.get("timestamp")),
                "event_type": "deployment",
                "service": deploy.get("service"),
                "title": f"Deployment {deploy.get('version')}",
                "description": deploy.get("statement"),
                "evidence_ids": deploy.get("evidence_ids", []),
                "confidence": "high",
                "source": "deterministic",
            }
        )
    return sorted(events, key=lambda row: (row["timestamp"] is None, _sort_timestamp(row["timestamp"])))


def _sort_timestamp(value):
    if value is None:
        return datetime.max.replace(tzinfo=UTC)
    return value if value.tzinfo else value.replace(tzinfo=UTC)
