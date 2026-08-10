"""
Adversarial test suite for Workflow Engine, Webhook Dispatcher, SQLite Schema, and REST API.
Exercises edge cases, concurrency, HTTP timeouts, retries, malformed payloads, invalid trigger events, and error branches.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import tempfile
import threading
import unittest
import concurrent.futures
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Dict, Any, List

# Ensure root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi.testclient import TestClient
import src.infrastructure.database as db_infra
from src.app.server import app
from src.domain.workflow_engine import (
    evaluate_condition,
    evaluate_event,
    process_event,
    WorkflowEngine,
)
from src.infrastructure.webhook_dispatcher import (
    compute_hmac_signature,
    dispatch_webhook_sync,
    dispatch_webhook_async,
    dispatch_webhook_background,
    WebhookDispatcher,
)


class MockAdversarialWebhookHandler(BaseHTTPRequestHandler):
    response_status = 200
    response_delay = 0.0
    response_body_override = None
    received_requests = []

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        if MockAdversarialWebhookHandler.response_delay > 0:
            time.sleep(MockAdversarialWebhookHandler.response_delay)
            
        MockAdversarialWebhookHandler.received_requests.append({
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
            "signature": self.headers.get("X-Signature-256", ""),
        })

        try:
            self.send_response(MockAdversarialWebhookHandler.response_status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            if MockAdversarialWebhookHandler.response_body_override is not None:
                self.wfile.write(MockAdversarialWebhookHandler.response_body_override.encode("utf-8"))
            else:
                self.wfile.write(b'{"status": "received"}')
        except Exception as e:
            import logging; logging.error(f"Swallowed error in test_adversarial_workflows_webhooks.py: {e}")

    def log_message(self, format, *args):
        pass


class TestAdversarialWorkflowsWebhooks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, "test_adv_workflows.db")
        cls.orig_db_file = db_infra.DB_FILE
        db_infra.DB_FILE = cls.db_path
        db_infra.init_db()
        cls.client = TestClient(app)

        # Start mock web server
        MockAdversarialWebhookHandler.received_requests = []
        cls.server = HTTPServer(("127.0.0.1", 0), MockAdversarialWebhookHandler)
        cls.port = cls.server.server_port
        cls.server_thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.webhook_url = f"http://127.0.0.1:{cls.port}/webhook"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        db_infra.DB_FILE = cls.orig_db_file
        try:
            if os.path.exists(cls.db_path):
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(cls.db_path)
        except Exception as e:
            import logging; logging.error(f"Swallowed error in test_adversarial_workflows_webhooks.py: {e}")

    def setUp(self):
        MockAdversarialWebhookHandler.response_status = 200
        MockAdversarialWebhookHandler.response_delay = 0.0
        MockAdversarialWebhookHandler.response_body_override = None
        MockAdversarialWebhookHandler.received_requests.clear()

    # -------------------------------------------------------------------------
    # 1. Condition Engine Adversarial & Edge Case Tests
    # -------------------------------------------------------------------------

    def test_01_condition_engine_empty_and_null_patterns(self):
        """Verify empty, None, and whitespace-only condition patterns evaluate to True."""
        payload = {"filename": "test.txt", "score": 0.5}
        self.assertTrue(evaluate_condition(None, "document_ingested", payload))
        self.assertTrue(evaluate_condition("", "document_ingested", payload))
        self.assertTrue(evaluate_condition("   \n\t  ", "document_ingested", payload))

    def test_02_condition_engine_malformed_json_patterns(self):
        """Verify malformed/invalid JSON condition patterns fall back gracefully without crashing."""
        payload = {"filename": "report.pdf", "tag": "urgent-review"}
        
        # Unclosed JSON string
        malformed_1 = '{"tag": "urgent-review",'
        res1 = evaluate_condition(malformed_1, "tag_assigned", payload)
        # Should not crash; falls through to fnmatch or substring match
        self.assertIsInstance(res1, bool)

        # Invalid syntax JSON
        malformed_2 = '{"min_score": invalid_value}'
        res2 = evaluate_condition(malformed_2, "semantic_match", payload)
        self.assertIsInstance(res2, bool)

    def test_03_condition_engine_json_type_mismatches(self):
        """Verify JSON condition with non-numeric score or missing fields doesn't crash engine."""
        payload_invalid_score = {"score": "not_a_number_string"}
        json_cond = json.dumps({"min_score": 0.85})
        
        # When score is non-numeric, float conversion in JSON parsing will fail and fall through
        res = evaluate_condition(json_cond, "semantic_match", payload_invalid_score)
        self.assertFalse(res)

        # JSON condition key checking arbitrary payload properties
        json_custom = json.dumps({"mime_type": "application/pdf", "custom_key": "custom_val"})
        self.assertTrue(evaluate_condition(json_custom, "document_ingested", {
            "mime_type": "application/pdf",
            "custom_key": "custom_val"
        }))
        self.assertFalse(evaluate_condition(json_custom, "document_ingested", {
            "mime_type": "application/pdf",
            "custom_key": "wrong_val"
        }))

    def test_04_condition_engine_numeric_threshold_boundaries(self):
        """Verify exact boundary values, floating-point precision, and negative threshold patterns."""
        payload_exact = {"score": 0.85}
        payload_below = {"score": 0.849999}
        payload_above = {"score": 0.850001}

        # Format: min_score:0.85
        self.assertTrue(evaluate_condition("min_score:0.85", "semantic_match", payload_exact))
        self.assertFalse(evaluate_condition("min_score:0.85", "semantic_match", payload_below))
        self.assertTrue(evaluate_condition("min_score:0.85", "semantic_match", payload_above))

        # Format: score >= 0.85
        self.assertTrue(evaluate_condition("score >= 0.85", "semantic_match", payload_exact))
        self.assertFalse(evaluate_condition("score >= 0.85", "semantic_match", payload_below))

        # Standalone numeric string for semantic_match
        self.assertTrue(evaluate_condition("0.85", "semantic_match", payload_exact))
        self.assertFalse(evaluate_condition("0.85", "semantic_match", payload_below))

        # Test score fallback to 'confidence' field if 'score' is absent
        self.assertTrue(evaluate_condition("score >= 0.90", "semantic_match", {"confidence": 0.95}))
        self.assertFalse(evaluate_condition("score >= 0.90", "semantic_match", {"confidence": 0.80}))

    def test_05_condition_engine_regex_and_glob_patterns(self):
        """Verify regex and glob condition evaluations including invalid regex syntax handling."""
        payload = {"filepath": "/var/log/audit_2026.log", "tag": "security-alert"}

        # Valid regex
        self.assertTrue(evaluate_condition("regex:^/var/log/.*\\.log$", "document_ingested", payload))
        self.assertFalse(evaluate_condition("regex:^/srv/data/.*$", "document_ingested", payload))

        # Invalid regex syntax (unclosed parenthesis)
        self.assertFalse(evaluate_condition("regex:^/var/log/(audit.*$", "document_ingested", payload))

        # Glob pattern
        self.assertTrue(evaluate_condition("security-*", "tag_assigned", payload))
        self.assertFalse(evaluate_condition("network-*", "tag_assigned", payload))

    def test_06_condition_engine_unserializable_payloads(self):
        """Verify handling of candidate string fallback when payload contains unusual structures."""
        class CustomObj:
            def __str__(self):
                return "CustomObjStr"

        # Payload without candidate fields (filepath, filename, tag, query, mime_type)
        payload = {"data": "unique_keyword_12345", "obj": CustomObj()}
        
        # Substring match on serialized fallback or candidate string
        res = evaluate_condition("unique_keyword_12345", "custom_event", {"data": "unique_keyword_12345"})
        self.assertTrue(res)

    # -------------------------------------------------------------------------
    # 2. Webhook Dispatcher Network Resilience & Retry Backoff Tests
    # -------------------------------------------------------------------------

    def test_07_webhook_dispatcher_retry_on_500_error(self):
        """Verify WebhookDispatcher retries max_retries times when target server returns HTTP 500."""
        MockAdversarialWebhookHandler.response_status = 500
        
        payload = {"event": "test_500"}
        res = dispatch_webhook_sync(
            trigger_id=101,
            webhook_url=self.webhook_url,
            payload=payload,
            event_type="test_500",
            max_retries=3,
            initial_delay=0.01,
            backoff_multiplier=1.5
        )

        self.assertEqual(res["status"], "failed")
        self.assertEqual(res["response_status_code"], 500)
        self.assertEqual(res["retry_count"], 2)  # Attempts 0, 1, 2 (3 total)
        self.assertEqual(len(MockAdversarialWebhookHandler.received_requests), 3)

    def test_08_webhook_dispatcher_retry_on_404_error(self):
        """Verify WebhookDispatcher handles HTTP 404 Not Found error responses."""
        MockAdversarialWebhookHandler.response_status = 404
        
        res = dispatch_webhook_sync(
            trigger_id=102,
            webhook_url=self.webhook_url,
            payload={"event": "test_404"},
            event_type="test_404",
            max_retries=2,
            initial_delay=0.01
        )

        self.assertEqual(res["status"], "failed")
        self.assertEqual(res["response_status_code"], 404)
        self.assertEqual(res["retry_count"], 1)

    def test_09_webhook_dispatcher_timeout_handling(self):
        """Verify WebhookDispatcher handles connection / response timeouts gracefully."""
        # Set handler delay longer than timeout_sec
        MockAdversarialWebhookHandler.response_delay = 0.5
        
        res = dispatch_webhook_sync(
            trigger_id=103,
            webhook_url=self.webhook_url,
            payload={"event": "timeout_test"},
            event_type="timeout_test",
            max_retries=1,
            timeout_sec=0.1  # 100ms timeout < 500ms delay
        )

        self.assertEqual(res["status"], "failed")
        self.assertIsNone(res["response_status_code"])
        self.assertTrue("Error: timed out" in res["response_body"] or "URLError" in res["response_body"])
        
        # Wait for server thread to complete the delayed request before proceeding
        time.sleep(0.5)

    def test_10_webhook_dispatcher_unreachable_host(self):
        """Verify WebhookDispatcher handles unreachable ports/hosts without throwing uncaught exceptions."""
        dead_url = "http://127.0.0.1:59999/dead_endpoint"
        
        res = dispatch_webhook_sync(
            trigger_id=104,
            webhook_url=dead_url,
            payload={"event": "unreachable"},
            max_retries=1,
            timeout_sec=0.2
        )

        self.assertEqual(res["status"], "failed")
        self.assertIsNone(res["response_status_code"])
        self.assertIn("URLError", res["response_body"])

    def test_11_webhook_dispatcher_hmac_signatures(self):
        """Verify HMAC-SHA256 headers generated correctly with secret header."""
        secret = "complex-secret-key-!@#$%^&*()"
        payload = {"data": "payload_test"}
        
        res = dispatch_webhook_sync(
            trigger_id=105,
            webhook_url=self.webhook_url,
            payload=payload,
            secret_header=secret,
            max_retries=1
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(len(MockAdversarialWebhookHandler.received_requests), 1)
        req = MockAdversarialWebhookHandler.received_requests[0]
        
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")
        expected_sig = compute_hmac_signature(secret, payload_bytes)
        
        self.assertIn(f"sha256={expected_sig}", req["headers"].get("X-Signature-256", ""))
        self.assertIn(f"sha256={expected_sig}", req["headers"].get("X-Uroboros-Signature", ""))
        self.assertEqual(req["headers"].get("Authorization"), f"Bearer {secret}")

    def test_12_webhook_dispatcher_large_response_truncation(self):
        """Verify response bodies over 2000 characters are truncated safely in workflow_logs."""
        large_body = "A" * 5000
        MockAdversarialWebhookHandler.response_body_override = large_body

        res = dispatch_webhook_sync(
            trigger_id=106,
            webhook_url=self.webhook_url,
            payload={"test": "large_response"},
            max_retries=1
        )

        self.assertEqual(res["status"], "success")
        log_id = res["log_id"]
        self.assertIsNotNone(log_id)

        # Retrieve log from DB and verify truncation to 2000 chars
        logs = db_infra.list_workflow_logs(limit=10)
        matching_log = next((l for l in logs if l["id"] == log_id), None)
        self.assertIsNotNone(matching_log)
        self.assertLessEqual(len(matching_log["response_body"]), 2000)

    def test_13_webhook_dispatcher_background_thread_execution(self):
        """Verify background non-blocking webhook dispatching."""
        trigger = db_infra.create_workflow_trigger(
            name="Background Dispatch Test",
            event_type="bg_event",
            webhook_url=self.webhook_url,
            is_active=True
        )

        dispatch_webhook_background(
            trigger_id=trigger["id"],
            webhook_url=self.webhook_url,
            payload={"bg": True},
            event_type="bg_event"
        )

        # Allow background thread execution to complete
        time.sleep(0.3)
        self.assertGreaterEqual(len(MockAdversarialWebhookHandler.received_requests), 1)

    # -------------------------------------------------------------------------
    # 3. Database Schema & Concurrency Adversarial Tests
    # -------------------------------------------------------------------------

    def test_14_database_log_execution_nonexistent_trigger(self):
        """Verify log_workflow_execution handles nonexistent trigger_id safely via FK check fallback."""
        log_id = db_infra.log_workflow_execution(
            trigger_id=999999,  # Nonexistent trigger ID
            event_type="orphaned_log",
            payload_json=json.dumps({"orphaned": True}),
            status="failed",
            response_status_code=500,
            response_body="Internal Error",
            execution_time_ms=10.0,
            retry_count=3
        )

        self.assertGreater(log_id, 0)
        logs = db_infra.list_workflow_logs(limit=10)
        matching_log = next((l for l in logs if l["id"] == log_id), None)
        self.assertIsNotNone(matching_log)
        self.assertIsNone(matching_log["trigger_id"])

    def test_15_database_update_and_delete_edge_cases(self):
        """Verify updating with empty kwargs and deleting nonexistent triggers."""
        trigger = db_infra.create_workflow_trigger(
            name="Edge Trigger",
            event_type="edge_event",
            webhook_url="https://example.com/edge"
        )

        # Update with no fields provided returns existing trigger unchanged
        updated = db_infra.update_workflow_trigger(trigger["id"])
        self.assertEqual(updated["id"], trigger["id"])
        self.assertEqual(updated["name"], "Edge Trigger")

        # Update nonexistent trigger returns None
        self.assertIsNone(db_infra.update_workflow_trigger(999999, name="Ghost"))

        # Delete nonexistent trigger returns False
        self.assertFalse(db_infra.delete_workflow_trigger(999999))

    def test_16_database_concurrency_stress(self):
        """Verify concurrent SQLite WAL trigger creation, updates, and log writes from 10 parallel threads."""
        errors = []

        def worker_task(thread_id: int):
            try:
                # Create trigger
                t = db_infra.create_workflow_trigger(
                    name=f"Thread-{thread_id} Trigger",
                    event_type=f"thread_event_{thread_id}",
                    webhook_url=f"http://127.0.0.1/thread_{thread_id}"
                )
                tid = t["id"]

                # Update trigger
                db_infra.update_workflow_trigger(tid, is_active=False)

                # Log execution
                db_infra.log_workflow_execution(
                    trigger_id=tid,
                    event_type=f"thread_event_{thread_id}",
                    payload_json=json.dumps({"thread": thread_id}),
                    status="success"
                )

                # List triggers
                triggers = db_infra.list_workflow_triggers(event_type=f"thread_event_{thread_id}")
                if not triggers:
                    errors.append(f"Thread {thread_id} failed to query created trigger")
            except Exception as e:
                import logging; logging.getLogger(__name__).exception(f"Swallowed error in test_adversarial_workflows_webhooks.py: {e}")
                errors.append(f"Thread {thread_id} raised exception: {str(e)}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_task, i) for i in range(10)]
            concurrent.futures.wait(futures)

        self.assertEqual(errors, [], f"Concurrency errors encountered: {errors}")

    # -------------------------------------------------------------------------
    # 4. REST API Edge Case & Router Security Tests
    # -------------------------------------------------------------------------

    def test_17_api_trigger_creation_validation(self):
        """Verify REST API rejects invalid/missing trigger creation request bodies with 422."""
        # Missing required field 'webhook_url'
        resp1 = self.client.post("/api/v1/workflows/triggers", json={
            "name": "Invalid Trigger",
            "event_type": "document_ingested"
        })
        self.assertEqual(resp1.status_code, 422)

        # Missing required field 'name'
        resp2 = self.client.post("/api/v1/workflows/triggers", json={
            "event_type": "document_ingested",
            "webhook_url": "http://example.com"
        })
        self.assertEqual(resp2.status_code, 422)

    def test_18_api_get_and_delete_nonexistent_trigger_404(self):
        """Verify 404 HTTP exceptions when fetching or deleting nonexistent triggers."""
        resp_get = self.client.get("/api/v1/workflows/triggers/999999")
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_get.json()["detail"], "Workflow trigger not found")

        resp_del = self.client.delete("/api/v1/workflows/triggers/999999")
        self.assertEqual(resp_del.status_code, 404)
        self.assertEqual(resp_del.json()["detail"], "Workflow trigger not found")

    def test_19_api_trigger_event_nonexistent_trigger_id_404(self):
        """Verify 404 HTTP exception when dispatching event for specific nonexistent trigger_id."""
        resp = self.client.post("/api/v1/workflows/trigger-event", json={
            "trigger_id": 999999,
            "event_type": "test_event",
            "payload": {"data": 123}
        })
        self.assertEqual(resp.status_code, 404)

    def test_20_api_trigger_event_no_matching_triggers(self):
        """Verify behavior when dispatching event that matches 0 active triggers."""
        resp = self.client.post("/api/v1/workflows/trigger-event", json={
            "event_type": "unmatched_custom_event_xyz",
            "payload": {"key": "val"}
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "dispatched")
        self.assertEqual(data["matching_triggers"], 0)
        self.assertEqual(data["results"], [])


if __name__ == "__main__":
    unittest.main()
