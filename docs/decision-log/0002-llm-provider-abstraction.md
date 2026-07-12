# ADR 0002: LLM Provider Abstraction

## Decision

Use a provider interface with a mock provider as the default.

## Rationale

The project should run without paid credentials and should not couple incident workflows to one model vendor. Structured schemas make provider behavior testable.

