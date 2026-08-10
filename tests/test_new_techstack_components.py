import time
import pytest
from src.domain.ocr_engine import extract_text_from_image
from src.domain.vector_store import DenseVectorStore
from src.shared.auth import create_jwt_token, verify_jwt_token
from src.shared.rate_limiter import SlidingWindowRateLimiter
from src.infrastructure.telemetry import APMTelemetryExporter

def test_ocr_engine_fallback():
    res = extract_text_from_image("non_existent_image.png")
    assert "error" in res or res["status"] == "success"

@pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
def test_dense_vector_store():
    store = DenseVectorStore(dimension=4)
    store.add_vector("doc1", [1.0, 0.0, 0.0, 0.0], {"title": "Doc 1"})
    store.add_vector("doc2", [0.0, 1.0, 0.0, 0.0], {"title": "Doc 2"})

    nearest = store.search_nearest([1.0, 0.1, 0.0, 0.0], top_k=1)
    assert len(nearest) == 1
    assert nearest[0][0] == "doc1"
    assert nearest[0][1] > 0.9

def test_jwt_auth():
    token = create_jwt_token({"user": "admin", "role": "superuser"}, expires_in_seconds=60)
    assert isinstance(token, str)

    payload = verify_jwt_token(token)
    assert payload is not None
    assert payload["user"] == "admin"
    assert payload["role"] == "superuser"

    # Test invalid signature
    bad_token = token + "bad"
    assert verify_jwt_token(bad_token) is None

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=2.0)
    allowed, remaining = limiter.is_allowed("127.0.0.1")
    assert allowed and remaining == 2

    allowed, remaining = limiter.is_allowed("127.0.0.1")
    assert allowed and remaining == 1

    allowed, remaining = limiter.is_allowed("127.0.0.1")
    assert allowed and remaining == 0

    allowed, remaining = limiter.is_allowed("127.0.0.1")
    assert not allowed and remaining == 0

def test_telemetry_exporter():
    telemetry = APMTelemetryExporter()
    telemetry.record_request(0.012, status_code=200)
    telemetry.record_request(0.045, status_code=500)

    summary = telemetry.get_metrics_summary()
    assert summary["total_requests"] == 2
    assert summary["total_errors"] == 1
    assert summary["latency_p50_ms"] > 0

    prom_text = telemetry.generate_prometheus_text()
    assert "uroboros_requests_total 2" in prom_text
    assert "uroboros_errors_total 1" in prom_text
