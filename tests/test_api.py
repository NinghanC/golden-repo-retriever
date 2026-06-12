from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from golden_repo_retriever.api.app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_analyze_returns_summary(self) -> None:
        response = self.client.post("/api/v1/analyze", json={"query": "Compare Apple and Microsoft."})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["companies"], ["Apple", "Microsoft"])
        self.assertIn("summary", payload)

    def test_analyze_uses_report_text(self) -> None:
        response = self.client.post(
            "/api/v1/analyze",
            json={
                "query": "Read this report.",
                "report_text": "Microsoft supply chain risk remains low.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["companies"], ["Microsoft"])
        self.assertEqual(payload["audit_log"][0]["step"], "load_report")

    def test_analyze_can_export_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "api-result.json"
            response = self.client.post(
                "/api/v1/analyze",
                json={"query": "Compare Apple.", "export_path": str(output_path)},
            )

            self.assertEqual(response.status_code, 200)
            self.assertTrue(output_path.exists())
            exported = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(exported["companies"], ["Apple"])


if __name__ == "__main__":
    unittest.main()
