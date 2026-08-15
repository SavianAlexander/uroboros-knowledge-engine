import unittest
from fastapi.testclient import TestClient
from src.app.server import app
from src.infrastructure.database import init_db, get_db
from src.infrastructure.crawler_repository import init_crawler_schema, create_job, save_crawled_document
from src.domain.universal_crawler.models import CrawlJob, CrawlConfig, CrawledDocument

class TestCrawlerAPI(unittest.TestCase):
    """
    Unit test suite for Enterprise FastAPI Crawler & Intelligence Router.
    """

    @classmethod
    def setUpClass(cls):
        init_db()
        with get_db() as conn:
            init_crawler_schema(conn)
            # Create a sample test job
            job = CrawlJob(
                name="API Test Job",
                seed_urls=["https://example.com/api_test"],
                config=CrawlConfig(max_pages=5, stealth_mode="omni")
            )
            cls.job_id = create_job(conn, job)

            # Add a sample document
            doc = CrawledDocument(
                job_id=cls.job_id,
                url="https://example.com/api_test",
                title="Ley de Salud Integral",
                content_type="text/html",
                content_text="El Departamento de Salud deberá emitir el reglamento a los 30 días bajo pena de multa de $5,000. Véase 120 D.P.R. 300.",
                merkle_sha256="abc123merkle",
                merkle_dag_root="abc123dagroot"
            )
            save_crawled_document(conn, doc)

        cls.client = TestClient(app)
        # Mock auth header for tests
        cls.headers = {"X-API-Key": "test-key"}

    def test_list_jobs_endpoint(self):
        """Verify GET /api/crawler/jobs returns job list."""
        res = self.client.get("/api/crawler/jobs", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["total_jobs"], 1)

    def test_create_job_endpoint(self):
        """Verify POST /api/crawler/jobs creates job with omni default."""
        payload = {
            "name": "Endpoint Created Job",
            "seed_urls": ["https://sutra.oslpr.org/api/medidas"],
            "max_pages": 50
        }
        res = self.client.post("/api/crawler/jobs", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["stealth_mode"], "omni")

    def test_get_job_detail_endpoint(self):
        """Verify GET /api/crawler/jobs/{id} returns telemetry."""
        res = self.client.get(f"/api/crawler/jobs/{self.job_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["job"]["id"], self.job_id)

    def test_get_certificate_endpoint(self):
        """Verify GET /api/crawler/jobs/{id}/certificate returns FRE 902 affidavit."""
        res = self.client.get(f"/api/crawler/jobs/{self.job_id}/certificate", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("CERTIFICATE OF AUTHENTICITY", data["markdown_certificate"])
        self.assertIn("FRE 902(13)", data["markdown_certificate"])

    def test_get_dossier_endpoint(self):
        """Verify GET /api/crawler/jobs/{id}/dossier returns deposition dossier."""
        res = self.client.get(f"/api/crawler/jobs/{self.job_id}/dossier?topic=Salud", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("CROSS-EXAMINATION DEPOSITION DOSSIER", data["dossier_markdown"])
        self.assertIn("multa de $5,000", data["dossier_markdown"])

    def test_get_visualizer_endpoint(self):
        """Verify GET /api/crawler/jobs/{id}/visualizer returns standalone HTML5 page."""
        res = self.client.get(f"/api/crawler/jobs/{self.job_id}/visualizer", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("<!DOCTYPE html>", res.text)
        self.assertIn("<canvas id=\"canvas\"></canvas>", res.text)

    def test_semantic_search_endpoint(self):
        """Verify POST /api/crawler/jobs/{id}/search returns ranked results."""
        payload = {"query": "reglamento de salud", "top_k": 3}
        res = self.client.post(f"/api/crawler/jobs/{self.job_id}/search", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(len(data["results"]), 1)

if __name__ == "__main__":
    unittest.main()
