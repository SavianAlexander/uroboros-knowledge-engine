"""
Automated Test Suite: Host Hardware Acceleration & Resource Governor Engine.
Standard: Pure Python Standard Library + pytest + FastAPI TestClient.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

from src.infrastructure.hardware_accelerator import (
    HardwareAccelerator,
    apply_os_environment_optimizations,
    apply_sqlite_hardware_tuning
)
from src.infrastructure.database import reset_db_connections, DB_FILE
from src.app.main import app


@pytest.fixture(autouse=True)
def cleanup_connections():
    yield
    reset_db_connections()


class TestHardwareAccelerationEngine:
    """Validate CPU multi-threading, SQLite 4GB mmap, 256MB RAM cache & hardware profile discovery."""

    def test_apply_os_environment_optimizations(self):
        res = apply_os_environment_optimizations(thread_count=16)
        assert res["logical_threads_configured"] == 16
        assert os.environ.get("OPENBLAS_NUM_THREADS") in ("8", "16")
        assert os.environ.get("OMP_NUM_THREADS") in ("8", "16")
        assert os.environ.get("MKL_NUM_THREADS") in ("8", "16")
        assert os.environ.get("OLLAMA_NUM_PARALLEL") == "4"

    def test_apply_sqlite_hardware_tuning(self):
        res = apply_sqlite_hardware_tuning(DB_FILE)
        assert res["status"] == "success"
        # Maximum memory mapped I/O (up to 2GB-4GB clamped by SQLite compile-time limit)
        assert res["mmap_size_bytes"] >= 2147418112
        # 256MB RAM page cache
        assert res["cache_size_kb"] == 262144

        # Temp store in RAM (numeric value 2 is MEMORY)
        assert res["temp_store"] in (2, "MEMORY")
        # Synchronous NORMAL (numeric value 1 is NORMAL)
        assert res["synchronous"] in (1, "NORMAL")
        # Auto-checkpoint 2000 pages
        assert res["wal_autocheckpoint"] == 2000

    def test_hardware_profile_telemetry(self):
        profile = HardwareAccelerator.get_hardware_profile()
        assert "cpu" in profile
        assert "AMD Ryzen 7 5800X3D" in profile["cpu"]["model"]
        assert profile["cpu"]["l3_cache_mb"] == 96.0

        assert "gpu" in profile
        assert "AMD Radeon RX 7900 XTX" in profile["gpu"]["model"]
        assert profile["gpu"]["vram_gb"] == 24.0

        assert "ram" in profile
        assert profile["ram"]["total_gb"] == 32.0
        assert profile["ram"]["speed_mhz"] == 3600

        assert "storage" in profile
        assert "WD_BLACK SN850X" in profile["storage"]["model"]
        assert profile["storage"]["max_read_mb_s"] == 7300

    def test_apply_full_hardware_tuning(self):
        res = HardwareAccelerator.apply_full_hardware_tuning()
        assert res["status"] == "success"
        assert "elapsed_ms" in res
        assert "environment_threads" in res
        assert "sqlite_pragmas" in res


class TestHardwareFastAPIEndpoints:
    """Validate FastAPI REST endpoints for hardware profile and tuning."""

    def test_hardware_api_endpoints(self):
        client = TestClient(app)

        # 1. GET /api/system/hardware/profile
        resp = client.get("/api/system/hardware/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert "cpu" in data
        assert "gpu" in data
        assert "ram" in data
        assert "storage" in data

        # 2. POST /api/system/hardware/apply-tuning
        tune_resp = client.post("/api/system/hardware/apply-tuning")
        assert tune_resp.status_code == 200
        tune_data = tune_resp.json()
        assert tune_data["status"] == "success"
        assert "profile" in tune_data
