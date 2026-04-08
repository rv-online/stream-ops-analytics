import json
import unittest
from pathlib import Path

from src.analytics import build_report, run


class AnalyticsTests(unittest.TestCase):
    def test_build_report_flags_services_with_high_error_rate(self) -> None:
        report = build_report(
            [
                {"service": "api", "latency_ms": 100, "status": "ok"},
                {"service": "api", "latency_ms": 1500, "status": "error"},
            ]
        )
        self.assertEqual(report["candidate_incidents"][0]["service"], "api")
        self.assertEqual(report["noisiest_service"], "api")

    def test_run_writes_report(self) -> None:
        output_path = Path("out/test-report.json")
        report = run(Path("data/events.ndjson"), output_path)
        on_disk = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertIn("search-api", on_disk["service_summary"])
        self.assertEqual(report["service_summary"]["billing-worker"]["events"], 3)
        self.assertIn("incident_score", report["service_summary"]["ingest-api"])


if __name__ == "__main__":
    unittest.main()
