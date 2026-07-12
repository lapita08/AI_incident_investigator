import csv
import io
import json
import re
from collections import Counter
from typing import Any

from app.domain.enums import EvidenceType
from app.schemas.evidence import ParsingStats

LOG_RE = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T?[^\s]+)?\s*(?P<severity>ERROR|WARN|INFO|DEBUG|FATAL)?\s*(?P<service>[A-Za-z0-9_-]+)?\s*(?P<message>.*)",
    re.IGNORECASE,
)


def parse_alert(raw: str) -> tuple[dict[str, Any], ParsingStats]:
    try:
        payload = json.loads(raw)
        labels = payload.get("labels", {})
        annotations = payload.get("annotations", {})
        starts_at = payload.get("startsAt") or payload.get("start_time") or payload.get("timestamp")
        normalized = {
            "alert_name": labels.get("alertname") or payload.get("alert") or payload.get("name", "Alert"),
            "service": labels.get("service") or payload.get("service"),
            "severity": labels.get("severity") or payload.get("severity"),
            "start_time": starts_at,
            "state": payload.get("status") or payload.get("state", "firing"),
            "labels": labels,
            "annotations": annotations,
            "threshold": payload.get("threshold") or annotations.get("threshold"),
            "observed_value": payload.get("value") or annotations.get("observed_value"),
        }
        return normalized, ParsingStats(total_lines=1, parsed_lines=1)
    except json.JSONDecodeError:
        fields = dict(re.findall(r"([A-Za-z_]+)=([^,\s]+)", raw))
        return {
            "alert_name": fields.get("alert") or fields.get("alertname") or raw.splitlines()[0][:120],
            "service": fields.get("service"),
            "severity": fields.get("severity"),
            "start_time": fields.get("startsAt") or fields.get("timestamp"),
            "state": fields.get("state", "firing"),
            "labels": fields,
            "annotations": {},
        }, ParsingStats(total_lines=len(raw.splitlines()), parsed_lines=1, warning_count=1, warnings=["plain text alert parsed with limited structure"])


def parse_logs(raw: str) -> tuple[dict[str, Any], ParsingStats]:
    parsed: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            parsed.append(
                {
                    "timestamp": item.get("timestamp") or item.get("time") or item.get("@timestamp"),
                    "severity": item.get("level") or item.get("severity"),
                    "service": item.get("service"),
                    "host": item.get("host") or item.get("pod"),
                    "correlation_id": item.get("correlation_id") or item.get("request_id"),
                    "trace_id": item.get("trace_id"),
                    "message": item.get("message") or item.get("msg") or json.dumps(item, sort_keys=True),
                    "exception_type": item.get("exception") or item.get("exception_type"),
                    "error_code": item.get("error_code") or item.get("code"),
                    "latency_ms": item.get("latency_ms"),
                    "raw": line,
                }
            )
            continue
        except json.JSONDecodeError:
            pass
        match = LOG_RE.match(line)
        if match and match.group("message"):
            data = match.groupdict()
            parsed.append({**data, "raw": line})
        else:
            unparsed.append(line[:500])
    services = sorted({str(entry.get("service")) for entry in parsed if entry.get("service")})
    severities = Counter(str(entry.get("severity") or "unknown").upper() for entry in parsed)
    stats = ParsingStats(
        total_lines=len([line for line in raw.splitlines() if line.strip()]),
        parsed_lines=len(parsed),
        unparsed_lines=len(unparsed),
        warning_count=len(unparsed),
        warnings=[f"{len(unparsed)} malformed log line(s) preserved but not parsed"] if unparsed else [],
    )
    return {"entries": parsed, "unparsed_examples": unparsed[:10], "services": services, "severity_counts": dict(severities)}, stats


def parse_metrics(raw: str) -> tuple[dict[str, Any], ParsingStats]:
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        payload = json.loads(raw)
        rows = payload if isinstance(payload, list) else payload.get("metrics", [])
        for row in rows:
            records.append(_metric_record(row))
        return {"records": records}, ParsingStats(total_lines=len(records), parsed_lines=len(records))
    except (json.JSONDecodeError, AttributeError):
        pass
    reader = csv.DictReader(io.StringIO(raw))
    for row in reader:
        try:
            records.append(_metric_record(row))
        except ValueError as exc:
            warnings.append(str(exc))
    total = max(len(raw.splitlines()) - 1, 0)
    return {"records": records}, ParsingStats(total_lines=total, parsed_lines=len(records), unparsed_lines=max(total - len(records), 0), warning_count=len(warnings), warnings=warnings[:20])


def _metric_record(row: dict[str, Any]) -> dict[str, Any]:
    raw_value = row.get("value") if row.get("value") is not None else row.get("metric_value")
    if raw_value is None:
        raise ValueError("metric value is required")
    value = float(raw_value)
    return {
        "timestamp": row.get("timestamp") or row.get("time"),
        "metric_name": row.get("metric_name") or row.get("name"),
        "value": value,
        "service": row.get("service"),
        "labels": row.get("labels") if isinstance(row.get("labels"), dict) else {},
    }


def parse_structured_list(raw: str, key: str) -> tuple[dict[str, Any], ParsingStats]:
    try:
        payload = json.loads(raw)
        values = payload if isinstance(payload, list) else payload.get(key, payload)
        return {key: values}, ParsingStats(total_lines=1, parsed_lines=1)
    except json.JSONDecodeError:
        return {key: [], "text": raw}, ParsingStats(total_lines=len(raw.splitlines()), unparsed_lines=len(raw.splitlines()), warning_count=1, warnings=["expected JSON but received plain text"])


def parse_runbook(raw: str) -> tuple[dict[str, Any], ParsingStats]:
    sections: list[dict[str, str]] = []
    current = {"heading": "Runbook", "content": ""}
    for line in raw.splitlines():
        if line.startswith("#"):
            if current["content"].strip():
                sections.append(current)
            current = {"heading": line.lstrip("#").strip(), "content": ""}
        else:
            current["content"] += line + "\n"
    if current["content"].strip():
        sections.append(current)
    return {"sections": sections}, ParsingStats(total_lines=len(raw.splitlines()), parsed_lines=len(sections))


def normalize_evidence(evidence_type: EvidenceType, raw: str) -> tuple[dict[str, Any], ParsingStats]:
    match evidence_type:
        case EvidenceType.alert:
            return parse_alert(raw)
        case EvidenceType.log:
            return parse_logs(raw)
        case EvidenceType.metric:
            return parse_metrics(raw)
        case EvidenceType.deployment:
            return parse_structured_list(raw, "deployments")
        case EvidenceType.dependency:
            return parse_structured_list(raw, "dependencies")
        case EvidenceType.runbook:
            return parse_runbook(raw)
        case EvidenceType.observation:
            return {"text": raw}, ParsingStats(total_lines=len(raw.splitlines()), parsed_lines=1)
