from typing import Any

from app.llm.provider import LLMAction, LLMHypothesis, LLMProvider, LLMReport


class MockLLMProvider(LLMProvider):
    name = "mock"

    def generate_report(self, evidence_package: dict[str, Any]) -> LLMReport:
        patterns = {pattern["rule_id"] for pattern in evidence_package.get("patterns", [])}
        anomalies = evidence_package.get("metric_anomalies", [])
        logs = evidence_package.get("log_clusters", [])
        deployments = evidence_package.get("deployment_correlations", [])
        all_refs = sorted({ref for group in (anomalies + logs + deployments) for ref in group.get("evidence_ids", [])})

        if {"db_query_slowdown", "db_connection_exhaustion", "timeout_propagation"} & patterns:
            hypotheses = [
                LLMHypothesis(
                    title="Reporting workload likely created database contention",
                    description=(
                        "Database latency, connection pressure, and downstream timeout evidence align with resource contention. "
                        "The nearby deployment remains a correlation and is contradicted by recovery evidence after reporting activity stopped."
                    ),
                    confidence="high",
                    supporting_evidence_ids=_refs(evidence_package, ["METRIC", "LOG", "ALERT", "RUNBOOK"]),
                    contradicting_evidence_ids=_refs(evidence_package, ["DEPLOY"])[:1],
                    missing_evidence=["Database wait-event breakdown", "Active session sample during peak latency"],
                    validation_steps=[
                        "Compare report-generation query fingerprints with the latency window.",
                        "Check database wait events and connection pool saturation for the affected interval.",
                        "Confirm timeout rates fall after reporting workload is throttled or stopped.",
                    ],
                ),
                LLMHypothesis(
                    title="Recent deployment changed API/database behavior",
                    description=(
                        "A deployment occurred near the incident window, but deterministic analysis does not show causation. "
                        "Treat this as an alternate hypothesis until code-path or deploy-specific evidence is found."
                    ),
                    confidence="low",
                    supporting_evidence_ids=_refs(evidence_package, ["DEPLOY"]),
                    contradicting_evidence_ids=_refs(evidence_package, ["METRIC", "LOG"])[:3],
                    missing_evidence=["Diff of database query behavior in the deployed version", "Per-version error-rate comparison"],
                    validation_steps=["Compare pods by version if both old and new versions are running.", "Review deployment diff for query-plan or timeout changes."],
                ),
            ]
            actions = [
                LLMAction(
                    action_type="diagnostic",
                    title="Capture database wait events and top query fingerprints",
                    description="Collect read-only database diagnostics for the incident window before taking remediation.",
                    risk_level="low",
                    expected_result="Confirms whether contention is from long-running reporting queries, connection pressure, or another wait class.",
                    prerequisites=["Read-only database observability access"],
                    validation=["Evidence references should align with the first latency spike and timeout cluster."],
                ),
                LLMAction(
                    action_type="mitigation",
                    title="Temporarily pause or throttle report generation",
                    description="Reduce the suspected expensive workload while preserving customer-facing request capacity.",
                    risk_level="medium",
                    expected_result="Database query latency and downstream timeouts should decline within one to two metric intervals.",
                    prerequisites=["Human incident commander approval", "Known owner for report-generation workflow"],
                    validation=["Watch db_query_latency, db_connections, API p95 latency, and 5xx rate."],
                    rollback_considerations="Restore report generation once database pressure normalizes and missed jobs are queued safely.",
                    requires_approval=True,
                ),
            ]
        elif {"memory_growth", "pod_restart_loop", "recent_deployment_correlation"} & patterns:
            hypotheses = [
                LLMHypothesis(
                    title="Deployment introduced sustained memory growth",
                    description="Memory rises after deployment and is followed by restarts and request failures for one service. This supports a deployment-related leak but still needs runtime validation.",
                    confidence="high",
                    supporting_evidence_ids=_refs(evidence_package, ["METRIC", "LOG", "DEPLOY", "ALERT"]),
                    missing_evidence=["Heap profile or allocation summary", "Comparison against previous version under similar traffic"],
                    validation_steps=["Capture heap profile from an affected replica.", "Compare memory slope before and after deployment.", "Check whether rollback stops the growth."],
                )
            ]
            actions = [
                LLMAction(
                    action_type="diagnostic",
                    title="Capture heap and allocation profile from affected replicas",
                    description="Use read-only runtime diagnostics to identify dominant allocations before considering rollback.",
                    risk_level="low",
                    expected_result="Identifies whether memory growth is associated with a new code path.",
                    validation=["Profile timestamp should overlap with rising memory trend."],
                ),
                LLMAction(
                    action_type="mitigation",
                    title="Prepare a controlled rollback of the affected service",
                    description="Rollback is potentially service-impacting and must be approved. Use only after validating the deployed version is implicated.",
                    risk_level="high",
                    expected_result="Memory growth and restart rate should stop after the old version stabilizes.",
                    prerequisites=["Approval from incident commander", "Rollback artifact verified", "Current traffic and error budget assessed"],
                    validation=["Monitor memory slope, restart count, and error rate after rollback."],
                    rollback_considerations="If rollback worsens errors, redeploy the current version and continue leak isolation.",
                    requires_approval=True,
                    command_example="kubectl rollout undo deployment/<service>",
                ),
            ]
        else:
            hypotheses = [
                LLMHypothesis(
                    title="Insufficient evidence for a specific root-cause hypothesis",
                    description="The deterministic package lacks enough correlated alerts, metrics, logs, deployments, or dependency data to identify a strong cause.",
                    confidence="low",
                    supporting_evidence_ids=all_refs[:3],
                    missing_evidence=["More timestamped metrics", "Representative error logs", "Deployment history", "Dependency graph"],
                    validation_steps=["Add missing evidence and rerun analysis.", "Prefer timestamped data so correlation can be evaluated."],
                )
            ]
            actions = [
                LLMAction(
                    action_type="diagnostic",
                    title="Collect missing timestamped operational evidence",
                    description="Add alerts, metrics, logs, deployment records, and a service graph for the affected window.",
                    risk_level="low",
                    expected_result="Improves timeline correlation and reduces speculation.",
                    validation=["Rerun analysis and confirm each hypothesis cites evidence IDs."],
                )
            ]

        return LLMReport(
            executive_summary="[Mock output] Evidence was analyzed with deterministic rules before hypothesis generation. Review and validate before taking action.",
            confirmed_facts=evidence_package.get("confirmed_facts", []),
            unknowns=evidence_package.get("unknowns", []),
            hypotheses=hypotheses,
            actions=actions,
            communication_update={
                "technical": "Draft: We are investigating elevated errors/latency. Current findings are evidence-backed but not yet confirmed. Next update after validation steps complete.",
                "executive": "Draft: The team is actively investigating customer impact and prioritizing the safest mitigation. Root cause is not confirmed yet.",
                "status_page": "Draft: Some users may be experiencing degraded performance. We are investigating and will provide another update shortly.",
            },
            postmortem_draft={
                "summary": "Draft summary pending confirmed root cause.",
                "impact": evidence_package.get("incident", {}).get("customer_impact", "Impact under assessment."),
                "detection": "Detected from ingested alerts and metric/log evidence.",
                "timeline": evidence_package.get("timeline", []),
                "root_cause": "Unconfirmed until a hypothesis is marked confirmed by the responder.",
                "contributing_factors": [],
                "resolution": "Pending responder validation.",
                "what_went_well": [],
                "what_went_poorly": [],
                "action_items": _action_items(patterns),
                "open_questions": evidence_package.get("unknowns", []),
            },
        )


def _refs(evidence_package: dict[str, Any], prefixes: list[str]) -> list[str]:
    refs = []
    for evidence in evidence_package.get("evidence", []):
        if any(evidence["display_id"].startswith(prefix) for prefix in prefixes):
            refs.append(evidence["display_id"])
    return refs[:8]


def _action_items(patterns: set[str]) -> list[dict[str, str]]:
    if "db_query_slowdown" in patterns:
        return [
            {
                "title": "Limit concurrent report-generation jobs per tenant",
                "problem_addressed": "Unbounded reporting workloads can contend with customer-facing database queries.",
                "proposed_change": "Add a concurrency limit of two report jobs per tenant and expose rejected-job metrics.",
                "owner": "TBD",
                "priority": "P1",
                "target_date": "TBD",
                "verification_method": "Load test ten simultaneous report requests and verify customer API p95 remains within SLO.",
                "category": "prevention",
            }
        ]
    if "memory_growth" in patterns:
        return [
            {
                "title": "Add canary memory-slope gate for checkout-worker deployments",
                "problem_addressed": "Sustained memory growth reached restart thresholds before humans had enough warning.",
                "proposed_change": "Block promotion when memory slope exceeds the baseline by 50% for 20 minutes during canary.",
                "owner": "TBD",
                "priority": "P1",
                "target_date": "TBD",
                "verification_method": "Replay canary metrics from the incident and verify the gate fails the bad build.",
                "category": "detection",
            }
        ]
    return []
