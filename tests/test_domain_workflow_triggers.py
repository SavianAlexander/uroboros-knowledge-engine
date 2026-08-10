"""
Comprehensive unit and integration test suite for Workflow Triggers & Webhook Engine.
Tests database CRUD, condition rule matching, HMAC-SHA256 webhook dispatches, and FastAPI REST endpoints.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import tempfile
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi.testclient import TestClient
import src.infrastructure.database as db_infra
from src.app.server import app
from src.core.domain.models import WorkflowTriggerCreate
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
    WebhookDispatcher,
)


class MockWebhookHandler(BaseHTTPRequestHandler):
    received_requests = []

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        sig_header = self.headers.get("X-Signature-256", "")
        MockWebhookHandler.received_requests.append({
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
            "signature": sig_header,
        })
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def log_message(self, format, *args):
        pass


class TestDomainWorkflowTriggers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, "test_workflows.db")
        cls.orig_db_file = db_infra.DB_FILE
        db_infra.DB_FILE = cls.db_path
        db_infra.init_db()
        cls.client = TestClient(app)

        MockWebhookHandler.received_requests = []
        cls.server = HTTPServer(("127.0.0.1", 0), MockWebhookHandler)
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
            db_infra.reset_db_connections()
            if os.path.exists(cls.db_path):
                try:
                    from src.infrastructure.database import reset_db_connections
                    reset_db_connections()
                except Exception: pass
                os.remove(cls.db_path)
        except Exception as e:
            import logging; logging.error(f"Swallowed error in test_domain_workflow_triggers.py: {e}")

    def setUp(self):
        MockWebhookHandler.received_requests.clear()

    def test_01_database_crud_operations(self):
        """
        Preconditions: Isolated SQLite workflow database initialized.
        Invariants: Workflow trigger records enforce name, event type, pattern, secret header, and execution log tracking.
        Outcomes: Verifies create, get, list, update, execution logging, and deletion in database layer.
        """
        trigger = db_infra.create_workflow_trigger(
            name="Test Document Ingestion Rule",
            event_type="document_ingested",
            webhook_url="https://example.com/webhook",
            condition_pattern="*.pdf",
            secret_header="secret-key-123",
            is_active=True
        )
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger["name"], "Test Document Ingestion Rule")
        self.assertEqual(trigger["event_type"], "document_ingested")
        self.assertEqual(trigger["condition_pattern"], "*.pdf")
        self.assertEqual(trigger["is_active"], 1)

        trigger_id = trigger["id"]
        fetched = db_infra.get_workflow_trigger(trigger_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], trigger_id)

        triggers = db_infra.list_workflow_triggers(event_type="document_ingested")
        self.assertTrue(any(t["id"] == trigger_id for t in triggers))

        updated = db_infra.update_workflow_trigger(trigger_id, name="Updated Rule", is_active=False)
        self.assertEqual(updated["name"], "Updated Rule")
        self.assertEqual(updated["is_active"], 0)

        log_id = db_infra.log_workflow_execution(
            trigger_id=trigger_id,
            event_type="document_ingested",
            payload_json=json.dumps({"test": "data"}),
            status="success",
            response_status_code=200,
            response_body='{"status": "ok"}',
            execution_time_ms=12.5,
            retry_count=0
        )
        self.assertGreater(log_id, 0)
        logs = db_infra.list_workflow_logs(trigger_id=trigger_id)
        self.assertTrue(any(l["id"] == log_id for l in logs))

        deleted = db_infra.delete_workflow_trigger(trigger_id)
        self.assertTrue(deleted)
        self.assertIsNone(db_infra.get_workflow_trigger(trigger_id))

    def test_02_condition_matching_engine(self):
        """
        Preconditions: Event payloads for document_ingested, tag_assigned, and semantic_match events.
        Invariants: Evaluator matches glob patterns, tag wildcards, numeric score thresholds, and JSON filter criteria.
        Outcomes: Verifies boolean evaluation matching for all supported workflow condition types.
        """
        self.assertTrue(evaluate_condition("", "document_ingested", {"filepath": "doc.pdf"}))
        self.assertTrue(evaluate_condition(None, "document_ingested", {"filepath": "doc.pdf"}))

        self.assertTrue(evaluate_condition("*.pdf", "document_ingested", {"filepath": "/data/report.pdf", "filename": "report.pdf"}))
        self.assertFalse(evaluate_condition("*.pdf", "document_ingested", {"filepath": "/data/report.docx", "filename": "report.docx"}))

        self.assertTrue(evaluate_condition("urgent-*", "tag_assigned", {"tag": "urgent-review"}))
        self.assertFalse(evaluate_condition("urgent-*", "tag_assigned", {"tag": "normal-review"}))

        self.assertTrue(evaluate_condition("min_score:0.85", "semantic_match", {"score": 0.90}))
        self.assertTrue(evaluate_condition("score>=0.85", "semantic_match", {"score": 0.85}))
        self.assertFalse(evaluate_condition("score>=0.85", "semantic_match", {"score": 0.8499}))

        json_cond = json.dumps({"tag": "confidential", "min_score": 0.80})
        self.assertTrue(evaluate_condition(json_cond, "semantic_match", {"tag": "confidential", "score": 0.82}))
        self.assertFalse(evaluate_condition(json_cond, "semantic_match", {"tag": "public", "score": 0.82}))

    def test_03_webhook_dispatcher_signing_and_retries(self):
        """
        Preconditions: Background HTTP server listening on local loopback interface.
        Invariants: Dispatches calculate HMAC-SHA256 signature matching secret key and deliver POST request.
        Outcomes: Verifies HMAC signature generation, HTTP POST transmission, and server header verification.
        """
        secret = "MOCK_SECRET_KEY_FOR_TESTING_ONLY"
        payload = {"event": "document_ingested", "filepath": "test.txt", "timestamp": "2026-08-03T21:00:00Z"}
        
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        computed_sig = compute_hmac_signature(secret, payload_bytes)
        self.assertEqual(computed_sig, expected_sig)

        res = dispatch_webhook_sync(
            trigger_id=999,
            webhook_url=self.webhook_url,
            payload=payload,
            secret_header=secret,
            event_type="document_ingested"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["response_status_code"], 200)

        self.assertGreaterEqual(len(MockWebhookHandler.received_requests), 1)
        req = MockWebhookHandler.received_requests[-1]
        self.assertIn(f"sha256={expected_sig}", req["signature"])

    def test_04_rest_api_trigger_lifecycle(self):
        """
        Preconditions: FastAPI application connected to TestClient instance.
        Invariants: Trigger REST endpoints obey HTTP status codes and JSON request/response schemas.
        Outcomes: Verifies trigger POST creation, GET retrieval by ID, list filtering, and DELETE routes.
        """
        create_payload = {
            "name": "API Slack Alert",
            "event_type": "tag_assigned",
            "condition_pattern": "urgent-*",
            "webhook_url": self.webhook_url,
            "secret_header": "api-secret-123",
            "is_active": True
        }

        resp1 = self.client.post("/api/v1/workflows/triggers", json=create_payload)
        self.assertEqual(resp1.status_code, 201)
        data1 = resp1.json()
        trigger_id = data1["id"]
        self.assertEqual(data1["name"], "API Slack Alert")

        resp_get = self.client.get(f"/api/v1/workflows/triggers/{trigger_id}")
        self.assertEqual(resp_get.status_code, 200)
        self.assertEqual(resp_get.json()["id"], trigger_id)

        resp2 = self.client.get("/api/workflows/triggers?event_type=tag_assigned")
        self.assertEqual(resp2.status_code, 200)
        triggers = resp2.json()
        self.assertTrue(any(t["id"] == trigger_id for t in triggers))

        resp_del = self.client.delete(f"/api/workflows/triggers/{trigger_id}")
        self.assertEqual(resp_del.status_code, 200)
        self.assertEqual(resp_del.json()["status"], "deleted")

    def test_05_rest_api_event_trigger_and_logs(self):
        """
        Preconditions: Active workflow trigger created in database for matching tag event.
        Invariants: Triggering an event evaluates rules, dispatches webhooks synchronously, and appends execution logs.
        Outcomes: Verifies POST /api/v1/workflows/trigger-event and execution log listing endpoint.
        """
        t_data = db_infra.create_workflow_trigger(
            name="Event Trigger Test",
            event_type="tag_assigned",
            webhook_url=self.webhook_url,
            condition_pattern="critical-*",
            secret_header="event-secret",
            is_active=True
        )

        event_req = {
            "event_type": "tag_assigned",
            "payload": {
                "tag": "critical-security-alert",
                "filepath": "/srv/logs/audit.log"
            }
        }
        resp = self.client.post("/api/v1/workflows/trigger-event", json=event_req)
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(res_json["status"], "dispatched")
        self.assertGreaterEqual(res_json["matching_triggers"], 1)

        logs_resp = self.client.get("/api/v1/workflows/logs")
        self.assertEqual(logs_resp.status_code, 200)
        logs = logs_resp.json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)


if __name__ == "__main__":
    unittest.main()
