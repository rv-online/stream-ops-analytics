# Stream Ops Analytics

Python streaming-analytics style CLI for SLA reporting, breach scoring, and noisy-service detection from operational events.

## Why This Exists

Built to resemble the kind of lightweight reliability analytics utility teams use when they need operational signal quickly without standing up full infra.

## What This Demonstrates

- stream-style event processing from NDJSON inputs
- SLO breach rate, incident scoring, and noisiest-service summaries
- deterministic CLI output with unit tests

## Architecture

1. event streams are ingested and grouped by service and time window
1. analytics logic computes breach and noise-oriented metrics
1. reports summarize operational hotspots for triage

## Run It

```bash
python -m unittest tests.test_analytics
python src/analytics.py --input data/events.ndjson --output out/report.json
```

## Verification

Use the explicit test module and rerun the CLI to refresh the report artifact.
