"""
Unit and Integration Test Suite for Standalone Windows Desktop Release Packaging.
Standard: Pure Python standard library with unittest/pytest assertions.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil

# Ensure root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.build_windows_dist import (
    generate_launcher_batch_script,
    generate_stop_batch_script,
    build_windows_distribution,
    calculate_file_sha256
)


class TestWindowsDistPackaging(unittest.TestCase):
    """Test suite verifying Windows distribution bundle packaging."""

    def test_generate_launcher_batch_script(self):
        script = generate_launcher_batch_script(port=8080)
        self.assertIn("8080", script)
        self.assertIn("main.py", script)
        self.assertIn("stop_uroboros.bat", script)
        self.assertIn("PYTHONIOENCODING", script)

    def test_generate_stop_batch_script(self):
        script = generate_stop_batch_script(port=8080)
        self.assertIn("8080", script)
        self.assertIn("taskkill", script)

    def test_build_windows_distribution_spec_only(self):
        temp_dist = tempfile.mkdtemp(prefix="uroboros_dist_test_")
        try:
            scorecard = build_windows_distribution(output_dir=temp_dist, spec_only=True, clean=True)
            self.assertEqual(scorecard["status"], "SUCCESS")
            self.assertTrue(scorecard["spec_only"])
            self.assertGreater(scorecard["total_bundled_files"], 0)
            self.assertTrue(os.path.exists(scorecard["manifest_path"]))
            self.assertTrue(os.path.exists(scorecard["launcher_path"]))

            with open(scorecard["manifest_path"], "r", encoding="utf-8") as f:
                manifest = json.load(f)
            self.assertEqual(manifest["release_version"], "2026.1-RELEASE")
            self.assertIn("files", manifest)
            self.assertGreater(len(manifest["files"]), 0)
        finally:
            shutil.rmtree(temp_dist, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
