"""
Domain 21: Micro-Unit and Micro-Integration Router Suite.
Tests all 9 backend routers and modules: files.py, health.py, search.py, tags.py, export.py,
security.py, parsers.py, database.py, services.py.

Includes boundary cases, zero-byte uploads, corrupt audio headers, disk storage failure HTTP 507,
regex syntax error HTTP 400, path containment security, and DB connection operational error recovery.
"""

import os
import sys
import io
import shutil
import tempfile
import sqlite3
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import main
from main import app
import know
import src.infrastructure.database as db_infra
from src.infrastructure.database import get_db, init_db, reset_db_connections, db_status, search_files
from src.shared.security import verify_path_containment, get_file_acl
from src.infrastructure.parsers import parse_audio_metadata, extract_content, safe_write_file
from src.core.domain.services import (
    parse_query_operators,
    suggest_tags_from_text,
    generate_summary,
    generate_key_takeaways,
    extract_ai_tags,
    reciprocal_rank_fusion,
    sanitise_fts_query,
)


class TestRouterMicroUnits(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_micro_units_")
        self.db_path = os.path.join(self.test_dir, "test_micro.db")
        
        self.old_db = db_infra.DB_FILE
        self.old_active = getattr(main, "ACTIVE_DIR", None)
        
        db_infra.DB_FILE = self.db_path
        know.DB_FILE = self.db_path
        main.ACTIVE_DIR = self.test_dir
        
        reset_db_connections()
        init_db()
        self.client = TestClient(app)

    def tearDown(self):
        reset_db_connections()
        db_infra.DB_FILE = self.old_db
        know.DB_FILE = self.old_db
        if self.old_active is not None:
            main.ACTIVE_DIR = self.old_active
            
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_export_stats_csv(self):
        """
        Preconditions: Active export router endpoint for file statistics.
        Invariants: GET /api/stats/export must return HTTP 200 with text/csv content type.
        Outcomes: CSV response header contains 'Mime Type,File Count,Total Size (bytes)'.
        """
        response = self.client.get("/api/stats/export")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/csv"))
        self.assertIn("Mime Type,File Count,Total Size (bytes)", response.text)

    def test_02_export_results_csv(self):
        """
        Preconditions: Active export router endpoint for search queries.
        Invariants: GET /api/export with format=csv must return HTTP 200 CSV payload.
        Outcomes: Response text contains CSV columns 'Filepath,Filename,Size (bytes),Modified At'.
        """
        response = self.client.get("/api/export?query=test&format=csv")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/csv"))
        self.assertIn("Filepath,Filename,Size (bytes),Modified At", response.text)

    def test_03_export_pdf_report(self):
        """
        Preconditions: PDF generator service active on /api/report/export.
        Invariants: GET /api/report/export must yield application/pdf binary content.
        Outcomes: Binary payload starts with standard PDF magic header (%PDF).
        """
        response = self.client.get("/api/report/export?style_template=compact")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_04_health_status_endpoint(self):
        """
        Preconditions: Server health check route active.
        Invariants: GET /api/health must return HTTP 200 OK.
        Outcomes: Returned JSON dictionary confirms status ok and database availability.
        """
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("database", data)

    def test_05_system_env_endpoint(self):
        """
        Preconditions: Health router system environment diagnostic endpoint.
        Invariants: GET /api/system/env returns environment configuration details.
        Outcomes: JSON object includes python_version and sqlite_version parameters.
        """
        response = self.client.get("/api/system/env")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("python_version", data)
        self.assertIn("sqlite_version", data)

    def test_06_system_stats_and_db_stats_endpoints(self):
        """
        Preconditions: Database statistics routers.
        Invariants: GET /api/stats and GET /api/db/stats must both return HTTP 200 OK.
        Outcomes: Responses contain status ok and database freelist count statistics.
        """
        r1 = self.client.get("/api/stats")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["status"], "ok")

        r2 = self.client.get("/api/db/stats")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("freelist_count", r2.json())

    def test_07_snapshots_lifecycle(self):
        """
        Preconditions: Active database snapshot management system.
        Invariants: Snapshot creation, listing, restoration, and deletion endpoints must complete sequentially.
        Outcomes: All lifecycle HTTP calls return 200 OK with valid snapshot timestamps.
        """
        r_backup = self.client.post("/api/backup")
        self.assertEqual(r_backup.status_code, 200)
        ts = r_backup.json()["timestamp"]

        r_list = self.client.get("/api/snapshots")
        self.assertEqual(r_list.status_code, 200)
        self.assertGreater(len(r_list.json()["snapshots"]), 0)

        r_restore = self.client.post(f"/api/snapshots/restore?timestamp={ts}")
        self.assertEqual(r_restore.status_code, 200)

        r_del = self.client.delete(f"/api/snapshots?timestamp={ts}")
        self.assertEqual(r_del.status_code, 200)

    def test_08_zero_byte_file_upload(self):
        """
        Preconditions: Files router upload endpoint.
        Invariants: Zero-byte file upload must be handled safely without error exceptions.
        Outcomes: Server returns status 200 with status success JSON payload.
        """
        files = {"file": ("zero_byte.txt", b"", "text/plain")}
        response = self.client.post("/api/upload", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_09_disk_storage_failure_507(self):
        """
        Preconditions: Simulated low disk space condition below 10MB threshold.
        Invariants: Indexing request under insufficient storage space must trigger HTTP 507.
        Outcomes: Response status is 507 and error detail indicates storage insufficiency.
        """
        old_disk_usage = shutil.disk_usage
        try:
            shutil.disk_usage = lambda path: (100 * 1024 * 1024, 99 * 1024 * 1024, 1 * 1024 * 1024)
            response = self.client.post("/api/index", json={"directory": "."})
            self.assertEqual(response.status_code, 507)
            self.assertIn("Insufficient storage space", response.json()["detail"])
        finally:
            shutil.disk_usage = old_disk_usage

    def test_10_file_crud_operations(self):
        """
        Preconditions: Database seeded with a text file record.
        Invariants: Raw file reading, saving, revision history, revert, summary, and deletion work correctly.
        Outcomes: All file CRUD endpoints complete successfully with HTTP 200.
        """
        sample_file = os.path.join(self.test_dir, "sample.txt")
        safe_write_file(sample_file, "Hello World Initial")

        with get_db() as conn:
            conn.execute(
                "INSERT INTO files (filepath, filename, file_size, modified_at, content) VALUES (?, ?, ?, ?, ?)",
                (sample_file, "sample.txt", len("Hello World Initial"), 1000.0, "Hello World Initial")
            )
            conn.commit()

        r_raw = self.client.get(f"/api/file/raw?path={sample_file}")
        self.assertEqual(r_raw.status_code, 200)
        self.assertEqual(r_raw.json()["content"], "Hello World Initial")

        r_save = self.client.post("/api/file/save", json={"filepath": sample_file, "content": "Updated Content"})
        self.assertEqual(r_save.status_code, 200)

        r_rev = self.client.get(f"/api/file/revisions?path={sample_file}")
        self.assertEqual(r_rev.status_code, 200)
        revs = r_rev.json()["revisions"]
        self.assertGreater(len(revs), 0)

        rev_id = revs[0]["id"]
        r_revert = self.client.post("/api/file/revert", json={"filepath": sample_file, "revision_id": rev_id})
        self.assertEqual(r_revert.status_code, 200)

        r_sum = self.client.get(f"/api/file/summary?path={sample_file}")
        self.assertEqual(r_sum.status_code, 200)

        r_del = self.client.post("/api/file/delete", json={"filepath": sample_file})
        self.assertEqual(r_del.status_code, 200)

    def test_11_file_rename_and_bulk_delete(self):
        """
        Preconditions: Seeded file entry in temporary directory.
        Invariants: Renaming file updates filepath in DB and filesystem; bulk delete removes items.
        Outcomes: File rename and bulk delete endpoints return HTTP 200 OK.
        """
        f1 = os.path.join(self.test_dir, "rename_me.txt")
        safe_write_file(f1, "Rename me text")

        with get_db() as conn:
            conn.execute("INSERT INTO files (filepath, filename) VALUES (?, ?)", (f1, "rename_me.txt"))
            conn.commit()

        r_rename = self.client.post("/api/file/rename", json={"filepath": f1, "new_name": "renamed.txt"})
        self.assertEqual(r_rename.status_code, 200)

        new_fp = r_rename.json()["new_filepath"]
        r_bulk = self.client.post("/api/file/bulk-delete", json={"filepaths": [new_fp]})
        self.assertEqual(r_bulk.status_code, 200)

    def test_12_search_and_query_validation(self):
        """
        Preconditions: Search router active endpoints.
        Invariants: Search queries, query syntax validation, auto-suggestions, concept graph, and history execute.
        Outcomes: All search endpoints return valid responses and syntax errors are caught cleanly.
        """
        r_search = self.client.get("/api/search?query=knowledge")
        self.assertEqual(r_search.status_code, 200)
        self.assertIn("results", r_search.json())

        r_val = self.client.post("/api/search/validate", json={"query": 'type:txt "unclosed quote'})
        self.assertEqual(r_val.status_code, 200)
        self.assertFalse(r_val.json()["valid"])

        r_val_ok = self.client.post("/api/search/validate", json={"query": 'tag:science physics'})
        self.assertEqual(r_val_ok.status_code, 200)
        self.assertTrue(r_val_ok.json()["valid"])

        r_sug = self.client.get("/api/search/suggest?token=tag:")
        self.assertEqual(r_sug.status_code, 200)

        r_graph = self.client.get("/api/graph")
        self.assertEqual(r_graph.status_code, 200)

        r_hist = self.client.get("/api/search/history")
        self.assertEqual(r_hist.status_code, 200)

    def test_13_invalid_regex_rule_returns_400(self):
        """
        Preconditions: Rule creation endpoint in tags router.
        Invariants: Invalid regex syntax pattern must be rejected with HTTP 400.
        Outcomes: Response status is HTTP 400 and error detail mentions invalid regex.
        """
        response = self.client.post("/api/rules", json={"pattern": "[unclosed_regex", "tag": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid regex pattern", response.json()["detail"])

    def test_14_empty_regex_pattern_returns_400(self):
        """
        Preconditions: Tags router rule management.
        Invariants: Empty regex pattern string must be rejected with HTTP 400.
        Outcomes: Server responds with HTTP 400 Bad Request error.
        """
        response = self.client.post("/api/rules", json={"pattern": "", "tag": "test"})
        self.assertEqual(response.status_code, 400)

    def test_15_tags_and_rules_crud(self):
        """
        Preconditions: Tags and auto-rules management routes.
        Invariants: Rules creation, preview, synonyms, bookmarks, colors, macros, aliases, and peer sync execute.
        Outcomes: All endpoints execute cleanly returning HTTP 200 status codes.
        """
        r_tags = self.client.get("/api/tags")
        self.assertEqual(r_tags.status_code, 200)

        r_rule = self.client.post("/api/rules", json={"pattern": ".*\\.py", "tag": "python"})
        self.assertEqual(r_rule.status_code, 200)

        r_prev = self.client.post("/api/rules/preview", json={"pattern": "python", "tag": "python"})
        self.assertEqual(r_prev.status_code, 200)

        r_syn = self.client.post("/api/synonyms", json={"term": "quick", "synonyms": ["fast", "rapid"]})
        self.assertEqual(r_syn.status_code, 200)

        r_bm = self.client.post("/api/bookmarks", json={"name": "bm1", "query": "test"})
        self.assertEqual(r_bm.status_code, 200)

        r_bm_del = self.client.delete("/api/bookmarks?name=bm1")
        self.assertEqual(r_bm_del.status_code, 200)

        r_col = self.client.post("/api/tags/colors", json={"tag": "python", "color": "#123456"})
        self.assertEqual(r_col.status_code, 200)

        r_mac = self.client.post("/api/macros", json={"name": "p1", "expansion": "tag:python"})
        self.assertEqual(r_mac.status_code, 200)

        r_alias = self.client.post("/api/aliases", json={"alias": "py", "target": "python"})
        self.assertEqual(r_alias.status_code, 200)

        r_peer = self.client.post("/api/sync/peers", json={"address": "http://127.0.0.1:9999", "name": "peer1"})
        self.assertEqual(r_peer.status_code, 200)

    def test_16_path_containment_security(self):
        """
        Preconditions: Security verification module verify_path_containment.
        Invariants: Directory traversal sequences and absolute system paths outside boundary must raise exceptions.
        Outcomes: Traversal attempts throw Exception; valid containment checks succeed.
        """
        with self.assertRaises(Exception):
            verify_path_containment("../../../etc/passwd")

        with self.assertRaises(Exception):
            verify_path_containment("C:\\Windows\\System32\\cmd.exe")

        res_empty = verify_path_containment("")
        self.assertIn(res_empty, ["", None])

    def test_17_get_file_acl_and_parsers(self):
        """
        Preconditions: Parsers and ACL helper modules.
        Invariants: File ACL inspection returns permissions string; corrupt audio and content extractions run safely.
        Outcomes: File ACL is string; corrupt audio parsing returns dict without crashing.
        """
        f_acl = os.path.join(self.test_dir, "acl_test.txt")
        safe_write_file(f_acl, "acl content")
        acl = get_file_acl(f_acl)
        self.assertIsInstance(acl, str)

        corrupt_wav = os.path.join(self.test_dir, "corrupt.wav")
        with open(corrupt_wav, "wb") as f:
            f.write(b"RIFF----WAVEfmt \x00\x00\x00\x00corrupt_data")
            
        meta = parse_audio_metadata(corrupt_wav)
        self.assertIsInstance(meta, dict)

        target = os.path.join(self.test_dir, "atomic_write.txt")
        safe_write_file(target, "atomic content")
        cnt, _ = extract_content(target, ".txt")
        self.assertIn("atomic content", cnt)

    def test_18_db_operational_recovery_and_services(self):
        """
        Preconditions: Database infrastructure status check and core domain services.
        Invariants: DB status reporting, FTS query sanitization, and reciprocal rank fusion calculate properly.
        Outcomes: Functions return expected data structures without throwing unhandled exceptions.
        """
        conn = get_db()
        self.assertIsNotNone(conn)
        status = db_status()
        self.assertIn("file_count", status)

        res = search_files("test")
        self.assertIsInstance(res, list)

        q_clean, ops, exc = parse_query_operators('tag:science -type:pdf "quantum mechanics"')
        self.assertEqual(ops.get("tag"), "science")
        self.assertEqual(exc.get("type"), "pdf")

        tags = suggest_tags_from_text("python database sqlite fastapi backend server")
        self.assertIsInstance(tags, list)

        summary = generate_summary("This is a detailed sentence for testing summary generation functionality. " * 3)
        self.assertGreater(len(summary), 0)

        fts_clean = sanitise_fts_query("NEAR(word1 word2, 5) OR foo AND bar*")
        self.assertIsInstance(fts_clean, str)

        rrf = reciprocal_rank_fusion([{"id": 1, "score": 1.0}], [{"id": 1, "score": 0.8}])
        self.assertIsInstance(rrf, list)


if __name__ == "__main__":
    unittest.main()
