from collections import defaultdict
from datetime import UTC, datetime
from statistics import mean, pstdev
from typing import Any

from app.analyzers.time_utils import parse_timestamp


def detect_metric_anomalies(evidence_items: list[Any]) -> list[dict[str, Any]]:
    series: dict[tuple[str, str | None], list[dict[str, Any]]] = defaultdict(list)
    evidence_by_series: dict[tuple[str, str | None], set[str]] = defaultdict(set)
    for item in evidence_items:
        if item.evidence_type != "metric":
            continue
        for record in item.normalized_content.get("records", []):
            key = (str(record.get("metric_name")), record.get("service"))
            series[key].append(record)
            evidence_by_series[key].add(item.display_id)
    anomalies: list[dict[str, Any]] = []
    for (metric_name, service), records in series.items():
        records = sorted(records, key=lambda row: parse_timestamp(row.get("timestamp")) or datetime.min.replace(tzinfo=UTC))
        if len(records) < 4:
            continue
        baseline_values = [float(row["value"]) for row in records[: max(3, len(records) // 2)]]
        baseline_mean = mean(baseline_values)
        baseline_std = pstdev(baseline_values) if len(baseline_values) > 1 else 0.0
        for row in records:
            value = float(row["value"])
            pct_change = ((value - baseline_mean) / baseline_mean * 100) if baseline_mean else 0
            crossed = value > baseline_mean + max(3 * baseline_std, baseline_mean * 0.5)
            if crossed or abs(pct_change) >= 75:
                direction = "increase" if value >= baseline_mean else "decrease"
                anomalies.append(
                    {
                        "metric_name": metric_name,
                        "service": service,
                        "timestamp": row.get("timestamp"),
                        "value": value,
                        "baseline_mean": round(baseline_mean, 3),
                        "baseline_stddev": round(baseline_std, 3),
                        "percentage_change": round(pct_change, 1),
                        "direction": direction,
                        "method": "baseline mean/stddev and percentage-change threshold",
                        "evidence_ids": sorted(evidence_by_series[(metric_name, service)]),
                    }
                )
                break
    return sorted(anomalies, key=lambda row: row.get("timestamp") or "")
