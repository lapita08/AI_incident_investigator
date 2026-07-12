# Threat Model

## Scope

Version 1 is a local single-user MVP. Authentication, authorization, production multi-tenancy, and remote integrations are not implemented.

## Key Threats

### Prompt Injection

Logs, alerts, metrics, runbooks, and observations are untrusted data. The LLM workflow receives explicit instructions not to follow evidence text as commands. Tests cover malicious log content such as instructions to delete a database.

### Sensitive Log Exposure

The ingestion layer redacts common email addresses, API-key-like values, bearer tokens, password-like fields, credit-card-like numbers, and database URLs. IP redaction is configurable. Raw evidence is not logged by default.

### Malicious File Upload

V1 accepts text payloads through APIs. It enforces size limits, validates non-empty content, and includes safe filename utilities for future file upload adapters.

### Cross-Site Scripting

The React UI renders evidence as text and JSON, not HTML. Evidence content must not be injected with `dangerouslySetInnerHTML`.

### Hallucinated Remediation

LLM output must validate against structured schemas and cite existing evidence IDs. Risky actions are labeled and require human approval.

### Excessive Data Retention

Local SQLite storage is persistent until deleted by the operator. Future versions should support retention policies and encrypted storage.

### Supply-Chain Risks

Dependencies are pinned by ecosystem manifests and monitored with Dependabot and CI. Production deployments should add SBOM generation and signed releases.

### Future Unauthorized Access

A future multi-user version must add authentication, RBAC/ABAC, incident-scoped authorization, audit logging, and tenant isolation before production use.

