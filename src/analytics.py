from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * pct))
    return ordered[index]


def build_report(events: list[dict[str, object]]) -> dict[str, object]:
    service_latencies: dict[str, list[int]] = defaultdict(list)
    service_errors: dict[str, int] = defaultdict(int)
    service_total: dict[str, int] = defaultdict(int)

    for event in events:
        service = str(event["service"])
        latency_ms = int(event["latency_ms"])
        status = str(event["status"])
        service_total[service] += 1
        service_latencies[service].append(latency_ms)
        if status != "ok":
            service_errors[service] += 1

    services: dict[str, dict[str, object]] = {}
    incidents: list[dict[str, object]] = []
    for service, total in sorted(service_total.items()):
        error_rate = round(service_errors[service] / total, 3)
        p95 = percentile(service_latencies[service], 0.95)
        services[service] = {
            "events": total,
            "error_rate": error_rate,
            "p95_latency_ms": p95,
        }
        if error_rate >= 0.2 or p95 >= 900:
            incidents.append(
                {
                    "service": service,
                    "severity": "high" if error_rate >= 0.3 or p95 >= 1200 else "medium",
                    "reason": f"error_rate={error_rate}, p95_latency_ms={p95}",
                }
            )

    return {"service_summary": services, "candidate_incidents": incidents}


def run(input_path: Path, output_path: Path) -> dict[str, object]:
    events = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = build_report(events)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming analytics")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
