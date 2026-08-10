"""
Empirical Test Harness for Milestone 2 (Workflow Triggers & Webhook Engine).
Written by Challenger 1 (challenger_m2_1).

Tests:
1. Non-blocking async execution (`dispatch_webhook_background`) under mock delay (in both sync/thread mode and asyncio loop mode).
2. HMAC-SHA256 signature generation (`X-Signature-256` and `X-Uroboros-Signature`).
3. Rejection of invalid secret keys and corrupted payloads.
4. Concurrent background dispatches stress test.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import asyncio
import tempfile
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.infrastructure.database as db_infra
from src.infrastructure.webhook_dispatcher import (
    compute_hmac_signature,
    dispatch_webhook_sync,
    dispatch_webhook_async,
    dispatch_webhook_background,
    WebhookDispatcher,
)


class DelayedWebhookHandler(BaseHTTPRequestHandler):
    received_requests = []
    delay_seconds = 0.0
    return_status = 200

    def do_POST(self):
        if DelayedWebhookHandler.delay_seconds > 0:
            time.sleep(DelayedWebhookHandler.delay_seconds)
            
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        req_info = {
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
            "signature_256": self.headers.get("X-Signature-256", ""),
            "uroboros_signature": self.headers.get("X-Uroboros-Signature", ""),
            "authorization": self.headers.get("Authorization", ""),
            "received_at": time.time(),
        }
        DelayedWebhookHandler.received_requests.append(req_info)

        self.send_response(DelayedWebhookHandler.return_status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')

    def log_message(self, format, *args):
        pass


class TestChallengerM2Harness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, "challenger_m2_test.db")
        cls.orig_db_file = db_infra.DB_FILE
        db_infra.DB_FILE = cls.db_path
        db_infra.init_db()

        DelayedWebhookHandler.received_requests = []
        DelayedWebhookHandler.delay_seconds = 0.0
        DelayedWebhookHandler.return_status = 200

        cls.server = HTTPServer(("127.0.0.1", 0), DelayedWebhookHandler)
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
            import logging; logging.error(f"Swallowed error in test_challenger_m2_1_harness.py: {e}")

    def setUp(self):
        DelayedWebhookHandler.received_requests.clear()
        DelayedWebhookHandler.delay_seconds = 0.0
        DelayedWebhookHandler.return_status = 200

    def test_01_non_blocking_async_execution_without_event_loop(self):
        """
        Verify dispatch_webhook_background returns immediately (< 50ms)
        when receiver delays response by 1.5 seconds (Thread mode).
        """
        # Create a real trigger in DB first
        trigger = db_infra.create_workflow_trigger(
            name="Async Thread Test Rule",
            event_type="document_ingested",
            webhook_url=self.webhook_url,
            secret_header="secret-key-async-1"
        )
        trigger_id = trigger["id"]

        DelayedWebhookHandler.delay_seconds = 1.5
        payload = {"event": "document_ingested", "file": "heavy_report.pdf"}
        secret = "secret-key-async-1"

        start_time = time.time()
        dispatch_webhook_background(
            trigger_id=trigger_id,
            webhook_url=self.webhook_url,
            payload=payload,
            secret_header=secret,
            event_type="document_ingested"
        )
        elapsed_call_time = (time.time() - start_time) * 1000.0

        # Assert caller returned almost instantly (well under 100ms, vs 1500ms server delay)
        self.assertLess(
            elapsed_call_time,
            100.0,
            f"dispatch_webhook_background blocked calling thread! Took {elapsed_call_time:.2f}ms"
        )

        # Wait for background thread to deliver payload
        time.sleep(2.0)

        # Verify receiver got the request
        self.assertEqual(len(DelayedWebhookHandler.received_requests), 1)
        req = DelayedWebhookHandler.received_requests[0]
        self.assertEqual(json.loads(req["body"].decode("utf-8")), payload)

        # Verify log entry was recorded in DB
        logs = db_infra.list_workflow_logs(trigger_id=trigger_id)
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0]["status"], "success")

    def test_02_non_blocking_async_execution_with_running_event_loop(self):
        """
        Verify dispatch_webhook_background returns immediately when called inside
        a running asyncio event loop (asyncio loop mode).
        """
        trigger = db_infra.create_workflow_trigger(
            name="Async Loop Test Rule",
            event_type="tag_assigned",
            webhook_url=self.webhook_url,
            secret_header="secret-key-async-2"
        )
        trigger_id = trigger["id"]

        DelayedWebhookHandler.delay_seconds = 1.0
        payload = {"event": "tag_assigned", "tag": "urgent"}
        secret = "secret-key-async-2"

        async def run_in_loop():
            start_time = time.time()
            dispatch_webhook_background(
                trigger_id=trigger_id,
                webhook_url=self.webhook_url,
                payload=payload,
                secret_header=secret,
                event_type="tag_assigned"
            )
            elapsed_ms = (time.time() - start_time) * 1000.0
            
            # Non-blocking check inside event loop
            self.assertLess(
                elapsed_ms,
                50.0,
                f"dispatch_webhook_background blocked asyncio loop! Took {elapsed_ms:.2f}ms"
            )

            # Give background asyncio task time to execute
            await asyncio.sleep(2.0)

        asyncio.run(run_in_loop())

        # Verify receiver got the request
        self.assertEqual(len(DelayedWebhookHandler.received_requests), 1)
        req = DelayedWebhookHandler.received_requests[0]
        self.assertEqual(json.loads(req["body"].decode("utf-8")), payload)

        # Verify DB log
        logs = db_infra.list_workflow_logs(trigger_id=trigger_id)
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0]["status"], "success")

    def test_03_hmac_sha256_signature_headers_validation(self):
        """
        Validate HMAC-SHA256 signature generation (X-Signature-256 and X-Uroboros-Signature)
        matches reference hmac.new(secret, payload_bytes, sha256).hexdigest().
        """
        secret = "my-ultra-secure-webhook-secret-999"
        payload = {
            "trigger_name": "Semantic Match Workflow",
            "event_type": "semantic_match",
            "document": "research_paper_v2.pdf",
            "score": 0.945,
            "metadata": {"author": "Uroboros AI", "version": 2}
        }

        # Format payload bytes exactly as dispatcher formats them
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")
        expected_hex = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

        res = dispatch_webhook_sync(
            trigger_id=None,
            webhook_url=self.webhook_url,
            payload=payload,
            secret_header=secret,
            event_type="semantic_match"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(DelayedWebhookHandler.received_requests), 1)

        req = DelayedWebhookHandler.received_requests[0]
        
        # Check X-Signature-256 header format
        sig_256 = req["signature_256"]
        self.assertTrue(sig_256.startswith("sha256="), f"X-Signature-256 header missing sha256= prefix: {sig_256}")
        raw_sig_256 = sig_256.split("sha256=")[1]
        self.assertEqual(raw_sig_256, expected_hex, f"X-Signature-256 mismatch! Got {raw_sig_256}, expected {expected_hex}")

        # Check X-Uroboros-Signature header format
        uro_sig = req["uroboros_signature"]
        self.assertTrue(uro_sig.startswith("sha256="), f"X-Uroboros-Signature header missing sha256= prefix: {uro_sig}")
        raw_uro_sig = uro_sig.split("sha256=")[1]
        self.assertEqual(raw_uro_sig, expected_hex, f"X-Uroboros-Signature mismatch! Got {raw_uro_sig}, expected {expected_hex}")

        # Verify signature against received body bytes directly
        received_body = req["body"]
        computed_from_body = hmac.new(secret.encode("utf-8"), received_body, hashlib.sha256).hexdigest()
        self.assertEqual(computed_from_body, expected_hex)
        self.assertTrue(hmac.compare_digest(raw_sig_256, computed_from_body))

    def test_04_verification_failure_cases(self):
        """
        Verify that invalid secret keys, tampered headers, or corrupted payloads fail verification.
        """
        sender_secret = "correct-sender-secret"
        wrong_receiver_secret = "wrong-receiver-secret"
        payload = {"alert": "security_breach_detected", "severity": "CRITICAL"}

        res = dispatch_webhook_sync(
            trigger_id=None,
            webhook_url=self.webhook_url,
            payload=payload,
            secret_header=sender_secret,
            event_type="security_alert"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(DelayedWebhookHandler.received_requests), 1)

        req = DelayedWebhookHandler.received_requests[0]
        received_body = req["body"]
        received_sig = req["signature_256"].replace("sha256=", "")

        # 1. Verification with wrong secret key must FAIL
        wrong_hmac = hmac.new(wrong_receiver_secret.encode("utf-8"), received_body, hashlib.sha256).hexdigest()
        self.assertNotEqual(received_sig, wrong_hmac)
        self.assertFalse(hmac.compare_digest(received_sig, wrong_hmac), "Verification should FAIL when secret key is wrong!")

        # 2. Verification with corrupted payload body must FAIL
        corrupted_body = received_body + b" " # append trailing byte
        corrupted_hmac = hmac.new(sender_secret.encode("utf-8"), corrupted_body, hashlib.sha256).hexdigest()
        self.assertNotEqual(received_sig, corrupted_hmac)
        self.assertFalse(hmac.compare_digest(received_sig, corrupted_hmac), "Verification should FAIL when payload is corrupted!")

        # 3. Verification with tampered JSON content must FAIL
        corrupted_json_body = json.dumps({"alert": "security_breach_detected", "severity": "LOW"}).encode("utf-8")
        tampered_hmac = hmac.new(sender_secret.encode("utf-8"), corrupted_json_body, hashlib.sha256).hexdigest()
        self.assertNotEqual(received_sig, tampered_hmac)
        self.assertFalse(hmac.compare_digest(received_sig, tampered_hmac), "Verification should FAIL when JSON content is tampered!")

    def test_05_concurrent_background_dispatches_stress_test(self):
        """
        Stress test 30 concurrent background webhook dispatches to verify stability,
        zero thread blocking, and 100% receipt.
        """
        DelayedWebhookHandler.delay_seconds = 0.05
        count = 30
        secret = "stress-secret-key"

        start_time = time.time()
        for i in range(count):
            dispatch_webhook_background(
                trigger_id=None,
                webhook_url=self.webhook_url,
                payload={"index": i, "batch": "stress_test"},
                secret_header=secret,
                event_type="stress_event"
            )
        dispatch_loop_time = (time.time() - start_time) * 1000.0

        # Dispatching 30 background tasks must be nearly instantaneous (< 1000ms total)
        self.assertLess(
            dispatch_loop_time,
            1000.0,
            f"Dispatching 30 background tasks blocked for {dispatch_loop_time:.2f}ms"
        )

        # Wait for all background tasks to complete delivery
        time.sleep(5.0)

        self.assertEqual(len(DelayedWebhookHandler.received_requests), count)
        
        # Verify all signatures match
        for req in DelayedWebhookHandler.received_requests:
            body = req["body"]
            sig = req["signature_256"].replace("sha256=", "")
            expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
            self.assertEqual(sig, expected)


if __name__ == "__main__":
    unittest.main()
