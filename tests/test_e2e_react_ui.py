"""
E2E & Integration Verification Suite for React UI Static Asset Serving.
Verifies React root mount, HTML hydration shell, bundled assets, and MIME headers.
"""

import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.server import app


class TestReactUIStaticServing(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_react_root_mount_html(self):
        """Verify GET / serves HTML containing the React root mount container."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div id="root"></div>', resp.text)
        self.assertIn("<title>Uroboros Knowledge Engine</title>", resp.text)

    def test_react_bundled_javascript_serving(self):
        """Verify GET /app.js serves bundled JavaScript with correct content type."""
        resp = self.client.get("/app.js")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("javascript" in resp.headers.get("content-type", "").lower())

    def test_react_stylesheet_serving(self):
        """Verify GET /style.css serves CSS stylesheet with correct content type."""
        resp = self.client.get("/style.css")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("css" in resp.headers.get("content-type", "").lower())


if __name__ == "__main__":
    unittest.main()