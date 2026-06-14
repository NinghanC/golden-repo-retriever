from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import fitz
from fastapi.testclient import TestClient

from golden_repo_retriever.api.app import create_app
from golden_repo_retriever.worker import JobWorker


class ApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.tmp_dir.name) / "api-test.db"
        self.client = TestClient(create_app(database_path=self.database_path))
        self.worker = JobWorker(database_path=self.database_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_config_reports_llm_provider(self) -> None:
        response = self.client.get("/api/v1/config")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["features"]["llm_provider"], "local")
        self.assertFalse(payload["features"]["llm_enabled"])

    def test_root_redirects_to_frontend(self) -> None:
        response = self.client.get("/", follow_redirects=False)

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/static/index.html")

    def test_analyze_returns_summary(self) -> None:
        response = self.client.post("/api/v1/analyze", json={"query": "Compare Apple and Microsoft."})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload["analysis_id"], int)
        self.assertEqual(payload["companies"], ["Apple", "Microsoft"])
        self.assertEqual(payload["llm_provider"], "local")
        self.assertIn("summary", payload)

    def test_analysis_history_returns_saved_result(self) -> None:
        created = self.client.post("/api/v1/analyze", json={"query": "Compare Apple."}).json()

        list_response = self.client.get("/api/v1/analyses")

        self.assertEqual(list_response.status_code, 200)
        history = list_response.json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], created["analysis_id"])
        self.assertEqual(history[0]["companies"], "Apple")

        detail_response = self.client.get(f"/api/v1/analyses/{created['analysis_id']}")

        self.assertEqual(detail_response.status_code, 200)
        detail = detail_response.json()
        self.assertEqual(detail["analysis_id"], created["analysis_id"])
        self.assertEqual(detail["companies"], ["Apple"])

    def test_missing_analysis_returns_404(self) -> None:
        response = self.client.get("/api/v1/analyses/999")

        self.assertEqual(response.status_code, 404)

    def test_job_runs_analysis_and_links_result(self) -> None:
        response = self.client.post("/api/v1/jobs", json={"query": "Compare Microsoft."})

        self.assertEqual(response.status_code, 202)
        job = response.json()
        self.assertEqual(job["status"], "queued")

        completed = self.process_job(job["id"])

        self.assertEqual(completed["status"], "completed")
        self.assertIsInstance(completed["analysis_id"], int)

        detail_response = self.client.get(f"/api/v1/analyses/{completed['analysis_id']}")

        self.assertEqual(detail_response.status_code, 200)
        detail = detail_response.json()
        self.assertEqual(detail["companies"], ["Microsoft"])

    def test_jobs_can_be_listed(self) -> None:
        created = self.client.post("/api/v1/jobs", json={"query": "Compare Apple."}).json()
        self.process_job(created["id"])

        response = self.client.get("/api/v1/jobs")

        self.assertEqual(response.status_code, 200)
        jobs = response.json()
        self.assertEqual(jobs[0]["id"], created["id"])

    def test_missing_job_returns_404(self) -> None:
        response = self.client.get("/api/v1/jobs/999")

        self.assertEqual(response.status_code, 404)

    def process_job(self, job_id: int) -> dict[str, object]:
        processed = self.worker.process_next()
        self.assertTrue(processed)
        response = self.client.get(f"/api/v1/jobs/{job_id}")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_analyze_uses_report_text(self) -> None:
        response = self.client.post(
            "/api/v1/analyze",
            json={
                "query": "Read this report.",
                "report_text": "Microsoft revenue was $245.1 billion. Microsoft supply chain risk remains low.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["companies"], ["Microsoft"])
        self.assertEqual(payload["extracted_facts"]["Microsoft"]["revenue"], 245.1)
        self.assertEqual(payload["evidence"]["Microsoft"][0]["snippet"], "Microsoft revenue was $245.1 billion.")
        self.assertEqual(payload["audit_log"][0]["step"], "load_report")

    def test_reports_can_be_saved_and_used_for_analysis(self) -> None:
        created = self.client.post(
            "/api/v1/reports",
            files={
                "file": (
                    "microsoft.txt",
                    b"Microsoft revenue was $245.1 billion. Microsoft supply chain risk remains low.",
                    "text/plain",
                )
            },
        )

        self.assertEqual(created.status_code, 201)
        report = created.json()
        self.assertEqual(report["filename"], "microsoft.txt")

        listed = self.client.get("/api/v1/reports")

        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()[0]["id"], report["id"])
        self.assertNotIn("text", listed.json()[0])

        analyzed = self.client.post(
            "/api/v1/analyze",
            json={"query": "Read this report.", "report_id": report["id"]},
        )

        self.assertEqual(analyzed.status_code, 200)
        payload = analyzed.json()
        self.assertEqual(payload["report_source"], f"report:{report['id']}")
        self.assertEqual(payload["extracted_facts"]["Microsoft"]["revenue"], 245.1)

    def test_report_backed_job_runs_analysis(self) -> None:
        report = self.client.post(
            "/api/v1/reports",
            files={"file": ("apple.txt", b"Apple revenue was $412.0 billion.", "text/plain")},
        ).json()

        created = self.client.post(
            "/api/v1/jobs",
            json={"query": "Read this report.", "report_id": report["id"]},
        ).json()
        completed = self.process_job(created["id"])

        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["report_id"], report["id"])
        analysis = self.client.get(f"/api/v1/analyses/{completed['analysis_id']}").json()
        self.assertEqual(analysis["companies"], ["Apple"])
        self.assertEqual(analysis["extracted_facts"]["Apple"]["revenue"], 412.0)

    def test_missing_report_returns_404(self) -> None:
        response = self.client.get("/api/v1/reports/999")

        self.assertEqual(response.status_code, 404)

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

    def test_analyze_upload_text_report(self) -> None:
        response = self.client.post(
            "/api/v1/analyze-upload",
            data={"query": "Read this report."},
            files={"file": ("report.txt", b"Microsoft supply chain risk remains low.", "text/plain")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["companies"], ["Microsoft"])
        self.assertEqual(payload["report_source"], "report.txt")

    def test_analyze_upload_pdf_report(self) -> None:
        pdf = fitz.open()
        page = pdf.new_page()
        page.insert_text((72, 72), "Apple R&D investment remains strong.")
        content = pdf.tobytes()
        pdf.close()

        response = self.client.post(
            "/api/v1/analyze-upload",
            data={"query": "Read this report."},
            files={"file": ("apple_report.pdf", content, "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["companies"], ["Apple"])
        self.assertEqual(payload["report_source"], "apple_report.pdf")


if __name__ == "__main__":
    unittest.main()
