# Data Model

## Incident

Stores incident metadata, severity, status, timing, affected services, customer impact, analysis status, report JSON, and user conclusions.

## Evidence Item

Stores stable display ID, evidence type, source, service, environment, timestamp, raw content, normalized content, parsing metadata, and ingestion status.

## Timeline Event

Stores normalized incident events with timestamp, type, service, title, description, cited evidence IDs, confidence, and source.

## Hypothesis

Stores ranked AI/deterministic hypotheses separately from user-confirmed conclusions. Each hypothesis includes supporting evidence, contradicting evidence, missing evidence, and validation steps.

## Recommended Action

Stores diagnostic, mitigation, and recovery actions. Risk level, prerequisites, validation, rollback considerations, approval requirements, and command examples are explicit.

## Investigation Report

Stored as JSON on the incident for reproducible export. It contains executive summary, confirmed facts, unknowns, timeline, affected components, blast radius, hypotheses, next steps, mitigations, communications, postmortem draft, and deterministic findings.

