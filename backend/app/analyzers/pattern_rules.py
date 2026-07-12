from typing import Any

RULES: list[dict[str, Any]] = [
    {"id": "latency_spike", "name": "Latency spike", "metric_keywords": ["latency", "duration"], "threshold_pct": 75},
    {"id": "error_rate_spike", "name": "Error-rate spike", "metric_keywords": ["error_rate", "5xx"], "threshold_pct": 75},
    {"id": "cpu_saturation", "name": "CPU saturation", "metric_keywords": ["cpu"], "threshold_value": 85},
    {"id": "memory_growth", "name": "Memory growth", "metric_keywords": ["memory", "rss"], "threshold_pct": 75},
    {"id": "db_connection_exhaustion", "name": "Database connection exhaustion", "metric_keywords": ["db_connections", "connection"], "threshold_pct": 75},
    {"id": "db_query_slowdown", "name": "Database query slowdown", "metric_keywords": ["db_query_latency", "query_latency"], "threshold_pct": 75},
    {"id": "timeout_propagation", "name": "Timeout propagation", "log_keywords": ["timeout", "deadline exceeded"]},
    {"id": "retry_storm", "name": "Retry storm", "log_keywords": ["retry", "backoff"]},
    {"id": "queue_backlog", "name": "Queue backlog", "metric_keywords": ["queue_depth", "backlog"], "threshold_pct": 75},
    {"id": "pod_restart_loop", "name": "Pod restart loop", "log_keywords": ["oomkilled", "restart", "crashloop"]},
    {"id": "recent_deployment_correlation", "name": "Recent deployment correlation"},
    {"id": "certificate_expiration", "name": "Certificate-expiration warning", "log_keywords": ["certificate", "expired", "x509"]},
    {"id": "dns_resolution_failure", "name": "DNS-resolution failure", "log_keywords": ["dns", "no such host", "name resolution"]},
]


def detect_patterns(anomalies: list[dict[str, Any]], log_clusters: list[dict[str, Any]], deployments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for rule in RULES:
        evidence_ids: set[str] = set()
        reasons: list[str] = []
        for anomaly in anomalies:
            metric = str(anomaly.get("metric_name", "")).lower()
            if any(keyword in metric for keyword in rule.get("metric_keywords", [])):
                if abs(float(anomaly.get("percentage_change", 0))) >= rule.get("threshold_pct", 0) or float(anomaly.get("value", 0)) >= rule.get("threshold_value", 0):
                    reasons.append(f"{anomaly.get('metric_name')} changed {anomaly.get('percentage_change')}% for {anomaly.get('service')}")
                    evidence_ids.update(anomaly.get("evidence_ids", []))
        for cluster in log_clusters:
            signature = cluster.get("cluster_signature", "").lower()
            if any(keyword in signature for keyword in rule.get("log_keywords", [])):
                reasons.append(f"Log cluster matched: {cluster.get('cluster_signature')}")
                evidence_ids.update(cluster.get("evidence_ids", []))
        if rule["id"] == "recent_deployment_correlation" and deployments:
            reasons.extend([item["statement"] for item in deployments])
            for item in deployments:
                evidence_ids.update(item.get("evidence_ids", []))
        if reasons:
            matches.append({"rule_id": rule["id"], "name": rule["name"], "reasons": reasons, "evidence_ids": sorted(evidence_ids)})
    return matches
