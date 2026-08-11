import pytest
import unittest
import os
import sys
import subprocess
import json

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

class TestDomainArchitecture(unittest.TestCase):
    def setUp(self):
        self.root_dir = root_dir
        self.cli_path = os.path.join(self.root_dir, "scripts", "architecture_cli.py")

    def tearDown(self):
        pass

    @pytest.mark.skip(reason="Legacy Test - Obsolete due to Architecture/React Refactor")
    @unittest.skip("Legacy UI test skipped")
    def test_01_architecture_compliance_score(self):
        """Verify Universal Architecture compliance score reaches 100.0% with zero secrets detected.

        Preconditions: scripts/architecture_cli.py script exists in root directory.
        Invariants: Architecture CLI audit execution evaluates repository structure.
        Expected Outcomes: Subprocess stdout contains 'Compliance Score: 100.0%' and 'Secrets Detected: 0'.
        """
        self.assertTrue(os.path.exists(self.cli_path), "scripts/architecture_cli.py not found")

        res = subprocess.run(
            [sys.executable, self.cli_path, "audit", self.root_dir],
            capture_output=True,
            text=True,
            check=True
        )
        output = res.stdout
        self.assertIn("Compliance Score: 100.0%", output)
        self.assertIn("Secrets Detected: 0", output)

if __name__ == "__main__":
    unittest.main()
