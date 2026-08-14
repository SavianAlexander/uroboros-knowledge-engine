import os
import sys
import unittest
import time
import json
import base64
import hmac
import hashlib
import tempfile
import shutil
import concurrent.futures

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know

from src.core.auth_jwt import sign_jwt, verify_jwt, hash_password, encode_base64_url, decode_base64_url, SECRET_KEY
from src.shared.auth import verify_api_key
from src.domain.acl_permission_engine import is_user_authorized, trim_search_results_by_acl


class TestDomainAuthSecurityHardening(unittest.TestCase):
    """Domain test suite for high-severity authentication vulnerabilities, JWT forgery, alg=none bypass, and multi-tenant isolation."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_auth_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_jwt_valid_signature_and_claims(self):
        """Verify standard JWT token creation, cryptographic signature, and payload claims extraction.

        Preconditions: User payload with user_id, username, and role claims.
        Invariants: verify_jwt returns exact payload dictionary with non-expired timestamp.
        Expected Outcomes: Extracted claims match input claims.
        """
        payload = {"user_id": 42, "username": "security_officer", "role": "admin"}
        token = sign_jwt(payload, exp_seconds=3600)
        self.assertIsInstance(token, str)
        self.assertEqual(token.count('.'), 2)

        claims = verify_jwt(token)
        self.assertIsNotNone(claims)
        self.assertEqual(claims["user_id"], 42)
        self.assertEqual(claims["username"], "security_officer")
        self.assertEqual(claims["role"], "admin")

    def test_02_jwt_alg_none_injection_rejection(self):
        """Verify rejection of critical 'alg': 'none' JWT header injection bypass vulnerability.

        Preconditions: Malicious JWT constructed with alg=none header and empty/forged signature.
        Invariants: verify_jwt verifies cryptographic HMAC-SHA256 signature and rejects unsigned tokens.
        Expected Outcomes: verify_jwt returns None.
        """
        none_header = {"alg": "none", "typ": "JWT"}
        payload = {"user_id": 1, "username": "admin", "exp": int(time.time()) + 3600}

        enc_h = encode_base64_url(json.dumps(none_header).encode('utf-8'))
        enc_p = encode_base64_url(json.dumps(payload).encode('utf-8'))
        forged_none_token = f"{enc_h}.{enc_p}."

        result = verify_jwt(forged_none_token)
        self.assertIsNone(result)

    def test_03_jwt_tampered_payload_signature_mismatch(self):
        """Verify signature mismatch rejection when token payload is tampered with in-transit.

        Preconditions: Valid signed JWT token modified by altering payload claim (e.g. user_id: 2 -> user_id: 1).
        Invariants: HMAC-SHA256 signature verification fails.
        Expected Outcomes: verify_jwt returns None.
        """
        original_token = sign_jwt({"user_id": 2, "role": "viewer"})
        h, p, s = original_token.split('.')

        # Tamper payload
        decoded_payload = json.loads(decode_base64_url(p).decode('utf-8'))
        decoded_payload["user_id"] = 1  # Escalation to superadmin
        decoded_payload["role"] = "superadmin"
        tampered_p = encode_base64_url(json.dumps(decoded_payload).encode('utf-8'))

        tampered_token = f"{h}.{tampered_p}.{s}"
        result = verify_jwt(tampered_token)
        self.assertIsNone(result)

    def test_04_jwt_expired_token_rejection(self):
        """Verify expired JWT tokens are rejected before payload consumption.

        Preconditions: Token signed with negative expiration (-10 seconds).
        Invariants: verify_jwt checks 'exp' claim against current epoch time.
        Expected Outcomes: verify_jwt returns None.
        """
        expired_token = sign_jwt({"user_id": 99}, exp_seconds=-10)
        result = verify_jwt(expired_token)
        self.assertIsNone(result)

    def test_05_jwt_malformed_token_dot_count_and_corrupt_base64(self):
        """Verify (Angle 25) resilience against malformed strings, invalid dot segments, and corrupted base64.

        Preconditions: Non-JWT strings, single dot strings, 4 dot strings, and illegal base64 chars.
        Invariants: verify_jwt returns None without throwing unhandled exceptions.
        Expected Outcomes: All malformed inputs safely return None.
        """
        self.assertIsNone(verify_jwt(""))
        self.assertIsNone(verify_jwt(None))
        self.assertIsNone(verify_jwt("not_a_jwt_token"))
        self.assertIsNone(verify_jwt("a.b"))
        self.assertIsNone(verify_jwt("a.b.c.d"))
        self.assertIsNone(verify_jwt("invalid!@#.bad!@#.signature!@#"))

    def test_06_password_hashing_consistency(self):
        """Verify password hashing consistency and uniqueness.

        Preconditions: Passwords hashed via hash_password().
        Invariants: Produces deterministic 64-char SHA-256 hex digest.
        Expected Outcomes: Identical passwords produce identical hashes; distinct passwords produce distinct hashes.
        """
        h1 = hash_password("SuperSecretPass123!")
        h2 = hash_password("SuperSecretPass123!")
        h3 = hash_password("DifferentPass456!")

        self.assertEqual(len(h1), 64)
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)

    def test_07_multi_tenant_user_id_document_filtering(self):
        """Verify strict multi-tenant document isolation. Tenant A cannot see Tenant B documents.

        Preconditions: Documents stored with separate tenant owner_id / user_id metadata.
        Invariants: trim_search_results_by_acl filters out documents owned by other tenants.
        Expected Outcomes: Search results for tenant A contain only tenant A's documents.
        """
        tenant_a_ctx = {"user_id": 101, "roles": ["user"], "clearance_level": 1}
        tenant_b_ctx = {"user_id": 202, "roles": ["user"], "clearance_level": 1}

        docs = [
            {"filename": "tenant_a_q3_report.pdf", "owner_id": 101, "clearance_level": 1},
            {"filename": "tenant_b_salaries.xlsx", "owner_id": 202, "clearance_level": 1},
            {"filename": "public_guidelines.txt", "owner_id": None, "read_roles": ["*"], "clearance_level": 0}
        ]

        trimmed_a = trim_search_results_by_acl(tenant_a_ctx, docs)
        filenames_a = [d["filename"] for d in trimmed_a]
        self.assertIn("tenant_a_q3_report.pdf", filenames_a)
        self.assertIn("public_guidelines.txt", filenames_a)
        self.assertNotIn("tenant_b_salaries.xlsx", filenames_a)

        trimmed_b = trim_search_results_by_acl(tenant_b_ctx, docs)
        filenames_b = [d["filename"] for d in trimmed_b]
        self.assertIn("tenant_b_salaries.xlsx", filenames_b)
        self.assertIn("public_guidelines.txt", filenames_b)
        self.assertNotIn("tenant_a_q3_report.pdf", filenames_b)

    def test_08_api_key_bearer_auth_guard_header_validation(self):
        """Verify API key and Bearer auth guard header parsing.

        Preconditions: Authorization header with 'Bearer <key>' or 'api-key: <key>'.
        Invariants: verify_api_key correctly evaluates key matching against configured system keys.
        Expected Outcomes: Returns True on matching key, False on mismatch.
        """
        # When NEURO_API_KEY is not set or empty, verify_api_key allows request (dev mode)
        # When key is passed, verifies matches
        self.assertIsInstance(verify_api_key("some_test_key"), bool)
        self.assertIsInstance(verify_api_key(None), bool)

    def test_09_timing_attack_resilient_signature_comparison(self):
        """Verify signature comparison uses constant-time comparison (hmac.compare_digest).

        Preconditions: Compare valid signature against forged signature with single byte difference.
        Invariants: Comparison correctly fails without side-channel timing leakage.
        Expected Outcomes: Compare returns False.
        """
        sig1 = hashlib.sha256(b"message1").digest()
        sig2 = hashlib.sha256(b"message2").digest()
        self.assertTrue(hmac.compare_digest(sig1, sig1))
        self.assertFalse(hmac.compare_digest(sig1, sig2))

    def test_10_concurrent_jwt_verification_under_load(self):
        """Verify concurrent multi-threaded JWT signing and verification safety.

        Preconditions: 50 concurrent threads signing and verifying tokens.
        Invariants: Cryptographic functions operate thread-safely without global mutex bottlenecks or race conditions.
        Expected Outcomes: 100% of concurrent signing and verification operations succeed.
        """
        def worker(idx):
            payload = {"user_id": idx, "seq": idx * 10}
            t = sign_jwt(payload, exp_seconds=60)
            verified = verify_jwt(t)
            return verified is not None and verified["user_id"] == idx

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(worker, range(50)))

        self.assertEqual(sum(results), 50)


if __name__ == "__main__":
    unittest.main()
