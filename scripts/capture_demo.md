# Demo Capture Guide

Use this guide to record a short demo or take screenshots for the README.

## Setup

Start the backend:

```bash
scripts/dev_backend.sh
```

Start the frontend in another terminal:

```bash
scripts/dev_frontend.sh
```

Open:

```text
http://127.0.0.1:5173
```

## Suggested Flow

1. Load the DB latency demo.
2. Open the Evidence tab and show `ALERT-001`, `LOG-001`, and `METRIC-001`.
3. Click Run investigation.
4. Open the Timeline tab.
5. Open the Hypotheses tab.
6. Click a cited evidence ID.
7. Open Recommended actions and point out risk labels.
8. Open Communications and Postmortem.
9. Export the report.

## Screenshots To Capture

- Dashboard with both demo buttons visible
- Incident overview after analysis
- Timeline with cited evidence IDs
- Leading hypothesis with supporting and contradicting evidence
- Recommended actions with risk labels
- Postmortem draft

## Notes

Keep the demo honest. Say that the mock provider is used by default and that the app does not execute remediation.
