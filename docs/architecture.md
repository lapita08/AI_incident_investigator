# Architecture

AI Incident Investigator is a modular monolith. The backend owns ingestion, persistence, deterministic analysis, optional LLM orchestration, report generation, export, and observability. The frontend is a React/Vite internal engineering UI that consumes the versioned REST API.

## Backend Flow

1. Incident metadata is stored in SQLite through SQLAlchemy models.
2. Evidence ingestion validates size and content, redacts common secrets, normalizes input, and assigns stable display IDs.
3. Deterministic analyzers build an evidence package:
   - timeline events
   - log clusters
   - metric anomalies
   - recent deployment correlations
   - dependency blast-radius analysis
   - visible pattern-rule matches
4. LLM orchestration receives only the structured evidence package and safety instructions. Evidence content is untrusted data, not instruction.
5. Hypotheses, actions, communications, and postmortem drafts are persisted separately from user confirmations.

## Extension Points

- `app/adapters`: future read-only source adapters.
- `app/llm/provider.py`: structured LLM provider interface.
- `app/analyzers/pattern_rules.py`: visible deterministic incident rules.
- `app/services/export_service.py`: report export formats.

## Operational Safety

The application recommends diagnostics and mitigations but never executes production actions. Risky actions include approval requirements, expected results, validation, and rollback considerations.

