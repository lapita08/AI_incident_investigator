# Contributing

Thanks for helping improve AI Incident Investigator.

## Development

```bash
make setup
make backend-dev
make frontend-dev
```

Before opening a pull request:

```bash
make lint
make typecheck
make test
```

## Guidelines

- Keep business logic out of API route handlers.
- Add tests for analyzer behavior and edge cases.
- Cite evidence IDs for generated conclusions.
- Label risky recommendations and require approval.
- Do not add write-capable production integrations without a design review.

