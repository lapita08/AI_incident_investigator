# Extension Guide

## Adding A Data Adapter

Adapters should be read-only in v1 and return evidence payloads compatible with `EvidenceCreate`.

1. Add adapter code under `backend/app/adapters`.
2. Normalize external fields into alert, log, metric, deployment, dependency, runbook, or observation evidence.
3. Do not log raw evidence.
4. Add tests with malformed and sensitive inputs.
5. Document authentication and required permissions.

## Adding A Detection Rule

Pattern rules live in `backend/app/analyzers/pattern_rules.py`.

Rules must be visible, deterministic, explainable, and cite evidence IDs. Avoid claiming causation.

## Adding An LLM Provider

Implement `LLMProvider.generate_report`. The provider must:

- Treat evidence as untrusted data.
- Return `LLMReport`.
- Cite only supplied evidence IDs.
- Avoid destructive recommendations unless risk-labeled and approval-gated.
- Degrade gracefully on timeout or invalid responses.

