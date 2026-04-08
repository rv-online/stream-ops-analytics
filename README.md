# Stream Ops Analytics

Streaming analytics CLI for newline-delimited operational events. The code reads an NDJSON stream, aggregates service-level metrics, and highlights candidate incidents.

## Run

```bash
python -m src.analytics --input data/events.ndjson --output out/report.json
```

## Test

```bash
python -m unittest discover -s tests
```

## Hiring Signal

This project demonstrates event-oriented thinking, operational metrics design, and a clean separation between parsing, aggregation, and alert logic. The report now includes SLO breach rate, incident scoring, and a noisiest-service signal so it reads more like internal reliability tooling.
