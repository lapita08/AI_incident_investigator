import re
from datetime import datetime
from typing import Any

from app.analyzers.time_utils import parse_timestamp

UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T[0-9:.+-Z]+")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
REQ_RE = re.compile(r"\b(req|request|trace|span|corr)[_-]?[A-Za-z0-9-]+\b", re.I)


def normalize_log_message(message: str) -> str:
    text = UUID_RE.sub("<uuid>", message)
    text = IP_RE.sub("<ip>", text)
    text = ISO_RE.sub("<timestamp>", text)
    text = REQ_RE.sub("<request-id>", text)
    text = NUMBER_RE.sub("<number>", text)
    return re.sub(r"\s+", " ", text).strip()


def cluster_logs(evidence_items: list[Any]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for item in evidence_items:
        if item.evidence_type != "log":
            continue
        for entry in item.normalized_content.get("entries", []):
            message = entry.get("message") or entry.get("raw") or ""
            signature = normalize_log_message(message)
            bucket = buckets.setdefault(
                signature,
                {"cluster_signature": signature, "count": 0, "first_occurrence": None, "last_occurrence": None, "affected_services": set(), "example_lines": [], "evidence_ids": set()},
            )
            ts = parse_timestamp(entry.get("timestamp"))
            bucket["count"] += 1
            bucket["evidence_ids"].add(item.display_id)
            if entry.get("service"):
                bucket["affected_services"].add(entry["service"])
            if len(bucket["example_lines"]) < 3:
                bucket["example_lines"].append(entry.get("raw", message))
            if ts:
                bucket["first_occurrence"] = min(filter(None, [bucket["first_occurrence"], ts]), default=ts)
                bucket["last_occurrence"] = max(filter(None, [bucket["last_occurrence"], ts]), default=ts)
    result = []
    for bucket in buckets.values():
        result.append(
            {
                **bucket,
                "first_occurrence": _iso(bucket["first_occurrence"]),
                "last_occurrence": _iso(bucket["last_occurrence"]),
                "affected_services": sorted(bucket["affected_services"]),
                "evidence_ids": sorted(bucket["evidence_ids"]),
            }
        )
    return sorted(result, key=lambda row: row["count"], reverse=True)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None

