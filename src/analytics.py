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
    slo_breaches: dict[str, int] = defaultdict(int)

    for event in events:
        service = str(event["service"])
        latency_ms = int(event["latency_ms"])
        status = str(event["status"])
        service_total[service] += 1
        service_latencies[service].append(latency_ms)
        if status != "ok":
            service_errors[service] += 1
        if latency_ms >= 800:
            slo_breaches[service] += 1

    services: dict[str, dict[str, object]] = {}
    incidents: list[dict[str, object]] = []
    for service, total in sorted(service_total.items()):
        error_rate = round(service_errors[service] / total, 3)
        p95 = percentile(service_latencies[service], 0.95)
        breach_rate = round(slo_breaches[service] / total, 3)
        incident_score = round((error_rate * 100) + (breach_rate * 50) + (p95 / 100), 2)
        services[service] = {
            "events": total,
            "error_rate": error_rate,
            "p95_latency_ms": p95,
            "slo_breach_rate": breach_rate,
            "incident_score": incident_score,
        }
        if error_rate >= 0.2 or p95 >= 900:
            incidents.append(
                {
                    "service": service,
                    "severity": "high" if error_rate >= 0.3 or p95 >= 1200 else "medium",
                    "reason": f"error_rate={error_rate}, p95_latency_ms={p95}, slo_breach_rate={breach_rate}",
                }
            )

    noisiest_service = max(services, key=lambda item: services[item]["incident_score"], default=None)
    return {
        "service_summary": services,
        "candidate_incidents": incidents,
        "noisiest_service": noisiest_service,
    }


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
