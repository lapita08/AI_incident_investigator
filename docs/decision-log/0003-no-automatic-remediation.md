# ADR 0003: Exclude Automatic Remediation

## Decision

Version 1 never executes rollbacks, restarts, database changes, or infrastructure changes.

## Rationale

Incident tooling should assist responders without increasing blast radius. Recommendations are safer when they include risk, prerequisites, validation, and approval requirements.

