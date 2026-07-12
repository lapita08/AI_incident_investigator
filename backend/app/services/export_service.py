import json

from app.models.entities import Incident


def export_json(incident: Incident, evidence: list, timeline: list, hypotheses: list, actions: list) -> dict:
    return {
        "incident": _incident(incident),
        "evidence": [_evidence(item) for item in evidence],
        "timeline": [_timeline(item) for item in timeline],
        "hypotheses": [_hypothesis(item) for item in hypotheses],
        "actions": [_action(item) for item in actions],
        "report": incident.report,
    }


def export_markdown(payload: dict) -> str:
    incident = payload["incident"]
    lines = [
        f"# Investigation Report: {incident['title']}",
        "",
        f"- Severity: {incident['severity']}",
        f"- Status: {incident['status']}",
        f"- Affected services: {', '.join(incident.get('affected_services') or []) or 'Unknown'}",
        "",
        "## Executive Summary",
        payload["report"].get("executive_summary", "No report generated."),
        "",
        "## Confirmed Facts",
        *[f"- {fact}" for fact in payload["report"].get("confirmed_facts", [])],
        "",
        "## Hypotheses",
    ]
    for hypothesis in payload["hypotheses"]:
        lines.extend(
            [
                f"### {hypothesis['rank']}. {hypothesis['title']} ({hypothesis['confidence']})",
                hypothesis["description"],
                f"- Supports: {', '.join(hypothesis['supporting_evidence_ids']) or 'None'}",
                f"- Contradicts: {', '.join(hypothesis['contradicting_evidence_ids']) or 'None'}",
                f"- Missing: {', '.join(hypothesis['missing_evidence']) or 'None'}",
            ]
        )
    lines.extend(["", "## Evidence Index"])
    for item in payload["evidence"]:
        lines.append(f"- {item['display_id']}: {item['evidence_type']} from {item['source']} ({item.get('service') or 'unknown service'})")
    lines.extend(["", "## Machine-readable JSON", "```json", json.dumps(payload, indent=2, default=str), "```"])
    return "\n".join(lines)


def _incident(item: Incident) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "severity": item.severity,
        "status": item.status,
        "started_at": item.started_at.isoformat() if item.started_at else None,
        "detected_at": item.detected_at.isoformat() if item.detected_at else None,
        "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
        "affected_services": item.affected_services,
        "customer_impact": item.customer_impact,
    }


def _evidence(item) -> dict:
    return {
        "id": item.id,
        "display_id": item.display_id,
        "evidence_type": item.evidence_type,
        "source": item.source,
        "service": item.service,
        "environment": item.environment,
        "timestamp": item.timestamp.isoformat() if item.timestamp else None,
        "normalized_content": item.normalized_content,
        "metadata": item.metadata_,
        "ingestion_status": item.ingestion_status,
    }


def _timeline(item) -> dict:
    return {
        "id": item.id,
        "timestamp": item.timestamp.isoformat() if item.timestamp else None,
        "event_type": item.event_type,
        "service": item.service,
        "title": item.title,
        "description": item.description,
        "evidence_ids": item.evidence_ids,
        "confidence": item.confidence,
        "source": item.source,
    }


def _hypothesis(item) -> dict:
    return {
        "id": item.id,
        "rank": item.rank,
        "title": item.title,
        "description": item.description,
        "confidence": item.confidence,
        "status": item.status,
        "supporting_evidence_ids": item.supporting_evidence_ids,
        "contradicting_evidence_ids": item.contradicting_evidence_ids,
        "missing_evidence": item.missing_evidence,
        "validation_steps": item.validation_steps,
        "generated_by": item.generated_by,
    }


def _action(item) -> dict:
    return {
        "id": item.id,
        "hypothesis_id": item.hypothesis_id,
        "action_type": item.action_type,
        "title": item.title,
        "description": item.description,
        "risk_level": item.risk_level,
        "expected_result": item.expected_result,
        "prerequisites": item.prerequisites,
        "validation": item.validation,
        "rollback_considerations": item.rollback_considerations,
        "requires_approval": item.requires_approval,
        "command_example": item.command_example,
        "status": item.status,
    }

