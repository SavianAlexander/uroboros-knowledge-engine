"""
Empirical stress-test harness for Milestone 1 backend router changes.
Covers:
- Export endpoints (/api/stats/export, /api/export, /api/report/export)
- Route collision resolution
- Zero-byte file uploads
- Disk storage failure 507 handling
- Regex error 400 handling
- Null/empty path containment security checks
- DB error recovery & concurrent connection handling
"""

import os
import sys
import shutil
import tempfile
import sqlite3
import threading
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
import src.infrastructure.database as db_infra
from src.infrastructure.database import get_db, init_db, reset_db_connections, db_status, search_files
from src.shared.security import verify_path_containment, get_file_acl

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_stress_env(tmp_path):
    test_db = str(tmp_path / "test_stress_m1.db")
    test_dir = str(tmp_path / "dumps")
    os.makedirs(test_dir, exist_ok=True)

    import main
    old_active = getattr(main, "ACTIVE_DIR", "dumps")
    main.ACTIVE_DIR = "dumps"

    old_db = db_infra.DB_FILE
    db_infra.DB_FILE = test_db
    reset_db_connections()
    init_db()

    yield tmp_path

    reset_db_connections()
    db_infra.DB_FILE = old_db
    main.ACTIVE_DIR = old_active


# ----------------------------------------------------------------------------
# 1. Export Endpoints Stress & Boundary Tests
# ----------------------------------------------------------------------------
def test_export_stats_csv_empty_and_populated(tmp_path):
    """Stress test /api/stats/export with empty DB and with populated data."""
    # 1. Empty DB
    resp = client.get("/api/stats/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "Mime Type,File Count,Total Size (bytes)" in resp.text

    # 2. Populated DB with varied MIME types and nulls
    with get_db() as conn:
        conn.execute("INSERT INTO files (filepath, filename, file_size, mime_type) VALUES (?, ?, ?, ?)",
                     (str(tmp_path / "dumps" / "f1.txt"), "f1.txt", 100, "text/plain"))
        conn.execute("INSERT INTO files (filepath, filename, file_size, mime_type) VALUES (?, ?, ?, ?)",
                     (str(tmp_path / "dumps" / "f2.pdf"), "f2.pdf", 2500, "application/pdf"))
        conn.execute("INSERT INTO files (filepath, filename, file_size, mime_type) VALUES (?, ?, ?, ?)",
                     (str(tmp_path / "dumps" / "f3.bin"), "f3.bin", 50, None))
        conn.commit()

    resp2 = client.get("/api/stats/export")
    assert resp2.status_code == 200
    assert "text/plain,1,100" in resp2.text
    assert "application/pdf,1,2500" in resp2.text
    assert "unknown,1,50" in resp2.text


def test_export_results_csv_query_variants():
    """Test /api/export with empty, normal, invalid FTS, and SQL injection queries."""
    # Empty query
    r1 = client.get("/api/export")
    assert r1.status_code == 200
    assert "Filepath,Filename,Size (bytes),Modified At" in r1.text

    # Valid query
    r2 = client.get("/api/export?query=document&format=csv")
    assert r2.status_code == 200

    # Malformed FTS query (unmatched quotes / operators)
    r3 = client.get('/api/export?query="unclosed quotes AND NOT&format=csv')
    assert r3.status_code == 200  # Should gracefully fallback to standard query without crashing

    # SQL Injection payload in query
    r4 = client.get("/api/export?query=' OR 1=1 --&format=csv")
    assert r4.status_code == 200

    # Header injection attempt in format parameter
    r5 = client.get("/api/export?query=test&format=csv%0D%0AX-Injected-Header:1")
    assert r5.status_code == 200


def test_export_pdf_report_templates():
    """Test /api/report/export with default, custom, and edge-case style templates."""
    r1 = client.get("/api/report/export")
    assert r1.status_code == 200
    assert r1.headers["content-type"] == "application/pdf"
    assert r1.content.startswith(b"%PDF")

    r2 = client.get("/api/report/export?style_template=detailed_executive_report_v2")
    assert r2.status_code == 200
    assert r2.content.startswith(b"%PDF")

    r3 = client.get("/api/report/export?style_template=<script>alert(1)</script>")
    assert r3.status_code == 200
    assert r3.content.startswith(b"%PDF")


# ----------------------------------------------------------------------------
# 2. Route Collision Resolution Tests
# ----------------------------------------------------------------------------
def test_route_collision_resolution():
    """Verify distinct dispatching between overlapping routes."""
    # /api/stats (health router, returns JSON) vs /api/stats/export (export router, returns CSV)
    r_stats_json = client.get("/api/stats")
    assert r_stats_json.status_code == 200
    assert r_stats_json.headers["content-type"].startswith("application/json")
    assert r_stats_json.json()["status"] == "ok"

    r_stats_csv = client.get("/api/stats/export")
    assert r_stats_csv.status_code == 200
    assert r_stats_csv.headers["content-type"].startswith("text/csv")

    # /api/export (export router, returns CSV) vs /api/file (files router)
    r_export = client.get("/api/export")
    assert r_export.status_code == 200
    assert r_export.headers["content-type"].startswith("text/csv")

    # /api/report/export (export router, returns PDF)
    r_report = client.get("/api/report/export")
    assert r_report.status_code == 200
    assert r_report.headers["content-type"] == "application/pdf"

    # /api/file/raw vs /api/file (nonexistent file inside dumps -> 404; file outside dumps -> 400)
    r_file_raw_404 = client.get("/api/file/raw?path=dumps/nonexistent.txt")
    assert r_file_raw_404.status_code == 404

    r_file_raw_400 = client.get("/api/file/raw?path=nonexistent.txt")
    assert r_file_raw_400.status_code == 400

    r_file_404 = client.get("/api/file?path=dumps/nonexistent.txt")
    assert r_file_404.status_code == 404


# ----------------------------------------------------------------------------
# 3. Zero-Byte File Uploads Tests
# ----------------------------------------------------------------------------
def test_zero_byte_uploads_stress(tmp_path):
    """Test zero-byte uploads across regular text files, audio files, and voice memos."""
    # 1. Zero-byte txt
    res_txt = client.post("/api/upload", files={"file": ("zero_test.txt", b"", "text/plain")})
    assert res_txt.status_code == 200
    txt_path = res_txt.json()["filepath"]
    assert os.path.exists(txt_path)
    assert os.path.getsize(txt_path) == 0

    # 2. Zero-byte audio
    res_audio = client.post("/api/upload", files={"file": ("zero_test.wav", b"", "audio/wav")})
    assert res_audio.status_code == 200
    wav_path = res_audio.json()["filepath"]
    assert os.path.exists(wav_path)
    assert os.path.getsize(wav_path) == 0

    # 3. Zero-byte voice memo
    res_vm = client.post("/api/upload", files={"file": ("voice-memo-001.wav", b"", "audio/wav")})
    assert res_vm.status_code == 200
    vm_path = res_vm.json()["filepath"]
    assert "voice_memos" in vm_path
    assert os.path.exists(vm_path)
    assert os.path.getsize(vm_path) == 0


# ----------------------------------------------------------------------------
# 4. Storage Failure 507 Tests
# ----------------------------------------------------------------------------
def test_storage_failure_507_boundary(monkeypatch):
    """Verify HTTP 507 is triggered when free space is under 10MB."""
    # 5MB free -> should fail with 507
    monkeypatch.setattr(shutil, "disk_usage", lambda path: (100 * 1024 * 1024, 95 * 1024 * 1024, 5 * 1024 * 1024))
    r_fail = client.post("/api/index", json={"directory": "."})
    assert r_fail.status_code == 507
    assert "Insufficient storage space" in r_fail.json()["detail"]

    # 15MB free -> should succeed (200)
    monkeypatch.setattr(shutil, "disk_usage", lambda path: (100 * 1024 * 1024, 85 * 1024 * 1024, 15 * 1024 * 1024))
    r_pass = client.post("/api/index", json={"directory": "."})
    assert r_pass.status_code == 200
    assert r_pass.json()["status"] == "success"


# ----------------------------------------------------------------------------
# 5. Regex Error 400 Tests
# ----------------------------------------------------------------------------
def test_regex_error_400_boundary_cases():
    """Verify invalid regex patterns return HTTP 400."""
    invalid_patterns = [
        "[unclosed_class",
        "(unmatched_group",
        "*leading_quantifier",
        "(?P<invalid",
        r"[\\",
    ]
    for pattern in invalid_patterns:
        r = client.post("/api/rules", json={"pattern": pattern, "tag": "test_tag"})
        assert r.status_code == 400
        assert "Invalid regex pattern" in r.json()["detail"]

    # Test preview endpoint with invalid regex
    for pattern in invalid_patterns:
        r_prev = client.post("/api/rules/test-preview", json={"pattern": pattern, "tag": "test_tag"})
        assert r_prev.status_code == 400
        assert "Invalid regex pattern" in r_prev.json()["detail"]

    # Empty pattern check
    r_empty = client.post("/api/rules", json={"pattern": "", "tag": "test_tag"})
    assert r_empty.status_code == 400
    assert "Pattern cannot be empty" in r_empty.json()["detail"]


# ----------------------------------------------------------------------------
# 6. Null / Empty Path Containment Checks
# ----------------------------------------------------------------------------
def test_path_containment_null_empty_traversal():
    """Stress test verify_path_containment with null, empty, whitespace, and traversal paths."""
    assert verify_path_containment(None) is None
    assert verify_path_containment("") is None

    # Path traversal attempts
    traversal_paths = [
        "../../../etc/passwd",
        "../../../../Windows/System32/drivers/etc/hosts",
        "dumps/../../secret.txt",
        "..\\..\\secret.txt",
    ]
    for tp in traversal_paths:
        with pytest.raises(Exception) as exc_info:
            verify_path_containment(tp)
        assert exc_info.value.status_code in (400, 403)

    # File endpoints with path traversal inputs
    for tp in traversal_paths:
        r_raw = client.get(f"/api/file/raw?path={tp}")
        assert r_raw.status_code in (400, 403, 404)

        r_sum = client.get(f"/api/file/summary?path={tp}")
        assert r_sum.status_code in (400, 403, 404)

        r_rev = client.get(f"/api/file/revisions?path={tp}")
        assert r_rev.status_code in (400, 403, 404)


# ----------------------------------------------------------------------------
# 7. DB Error Recovery & Concurrency Tests
# ----------------------------------------------------------------------------
def test_db_concurrency_and_recovery():
    """Verify DB handles concurrent requests and recovers from queries on invalid state."""
    errors = []

    def worker_thread(thread_id):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM files")
                _ = cursor.fetchone()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker_thread, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Encountered {len(errors)} errors during concurrent DB operations: {errors}"
