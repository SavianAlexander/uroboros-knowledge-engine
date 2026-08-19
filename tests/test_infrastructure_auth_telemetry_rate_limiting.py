import unittest
import time
from src.domain.ocr_engine import extract_text_from_image
from src.domain.vector_store import DenseVectorStore
from src.shared.auth import create_jwt_token, verify_jwt_token
from src.shared.rate_limiter import SlidingWindowRateLimiter
from src.infrastructure.telemetry import APMTelemetryExporter


class TestInfrastructureAuthTelemetryRateLimiting(unittest.TestCase):
    def test_ocr_engine_fallback(self):
        res = extract_text_from_image("non_existent_image.png")
        self.assertTrue("error" in res or res.get("status") == "success")

    def test_dense_vector_store(self):
        store = DenseVectorStore(dimension=4)
        store.add_vector("doc1", [1.0, 0.0, 0.0, 0.0], {"title": "Doc 1"})
        store.add_vector("doc2", [0.0, 1.0, 0.0, 0.0], {"title": "Doc 2"})

        nearest = store.search_nearest([1.0, 0.1, 0.0, 0.0], top_k=1)
        self.assertEqual(len(nearest), 1)
        self.assertEqual(nearest[0][0], "doc1")
        self.assertGreater(nearest[0][1], 0.9)

    def test_jwt_auth(self):
        token = create_jwt_token({"user": "admin", "role": "superuser"}, expires_in_seconds=60)
        self.assertIsInstance(token, str)

        payload = verify_jwt_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["user"], "admin")
        self.assertEqual(payload["role"], "superuser")

        # Test invalid signature
        bad_token = token + "bad"
        self.assertIsNone(verify_jwt_token(bad_token))

    def test_rate_limiter(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=2.0)
        allowed, remaining = limiter.is_allowed("127.0.0.1")
        self.assertTrue(allowed)
        self.assertEqual(remaining, 2)

        allowed, remaining = limiter.is_allowed("127.0.0.1")
        self.assertTrue(allowed)
        self.assertEqual(remaining, 1)

        allowed, remaining = limiter.is_allowed("127.0.0.1")
        self.assertTrue(allowed)
        self.assertEqual(remaining, 0)

        allowed, remaining = limiter.is_allowed("127.0.0.1")
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)

    def test_telemetry_exporter(self):
        telemetry = APMTelemetryExporter()
        telemetry.record_request(0.012, status_code=200)
        telemetry.record_request(0.045, status_code=500)

        summary = telemetry.get_metrics_summary()
        self.assertEqual(summary["total_requests"], 2)
        self.assertEqual(summary["total_errors"], 1)
        self.assertGreater(summary["latency_p50_ms"], 0)

        prom_text = telemetry.generate_prometheus_text()
        self.assertIn("uroboros_requests_total 2", prom_text)
        self.assertIn("uroboros_errors_total 1", prom_text)


if __name__ == "__main__":
    unittest.main()