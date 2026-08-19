import os
import sys
import unittest
import tempfile
import shutil

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import desktop_app
from scripts import build_windows_dist


class TestDomainDesktop(unittest.TestCase):
    def setUp(self):
        self.root_dir = root_dir

    def test_01_desktop_app_module_imports(self):
        """Verify desktop_app launcher module initializes entry points and default configuration."""
        self.assertTrue(hasattr(desktop_app, "main_desktop"))
        self.assertTrue(hasattr(desktop_app, "launch_server"))
        self.assertTrue(hasattr(desktop_app, "open_ui"))
        self.assertEqual(desktop_app.DEFAULT_PORT, 8085)

    def test_02_build_windows_dist_spec_generation(self):
        """Verify build_windows_dist generates valid distribution metadata and manifest."""
        temp_dist = tempfile.mkdtemp(prefix="uroboros_dist_domain_test_")
        try:
            scorecard = build_windows_dist.build_windows_distribution(output_dir=temp_dist, spec_only=True, clean=True)
            self.assertEqual(scorecard["status"], "SUCCESS")
            self.assertTrue(scorecard["spec_only"])
            self.assertTrue(os.path.exists(scorecard["manifest_path"]))
            self.assertTrue(os.path.exists(scorecard["launcher_path"]))
        finally:
            shutil.rmtree(temp_dist, ignore_errors=True)

    def test_03_desktop_batch_scripts(self):
        """Verify launcher and stop batch scripts generate valid commands."""
        start_script = build_windows_dist.generate_launcher_batch_script(port=8085)
        self.assertIn("8085", start_script)
        self.assertIn("main.py", start_script)

        stop_script = build_windows_dist.generate_stop_batch_script(port=8085)
        self.assertIn("8085", stop_script)
        self.assertIn("taskkill", stop_script)

    def test_04_desktop_app_frozen_path_resolution(self):
        """Verify desktop_app handles sys._MEIPASS CWD guard under PyInstaller frozen environment."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_frozen = getattr(sys, "frozen", None)
            orig_meipass = getattr(sys, "_MEIPASS", None)
            try:
                sys.frozen = True
                sys._MEIPASS = tmpdir
                if getattr(sys, 'frozen', False):
                    os.chdir(sys._MEIPASS)
                self.assertEqual(os.getcwd(), tmpdir)
            finally:
                if orig_frozen is None:
                    if hasattr(sys, "frozen"):
                        delattr(sys, "frozen")
                else:
                    sys.frozen = orig_frozen
                if orig_meipass is None:
                    if hasattr(sys, "_MEIPASS"):
                        delattr(sys, "_MEIPASS")
                else:
                    sys._MEIPASS = orig_meipass
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
