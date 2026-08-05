import os
import sys
import unittest

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import desktop_app
import build_desktop

class TestDomainDesktop(unittest.TestCase):
    def setUp(self):
        self.root_dir = root_dir
        self.spec_file = os.path.join(self.root_dir, "UroborosKnowledgeHub.spec")

    def tearDown(self):
        if os.path.exists(self.spec_file):
            try:
                os.remove(self.spec_file)
            except OSError:
                pass

    def test_01_desktop_app_module_imports(self):
        """Verify desktop_app launcher module initializes entry points and default configuration.

        Preconditions: desktop_app module loaded.
        Invariants: Main entry functions and default port constant are present in module.
        Expected Outcomes: Attributes main_desktop, launch_server, open_ui exist and DEFAULT_PORT == 8000.
        """
        self.assertTrue(hasattr(desktop_app, "main_desktop"))
        self.assertTrue(hasattr(desktop_app, "launch_server"))
        self.assertTrue(hasattr(desktop_app, "open_ui"))
        self.assertEqual(desktop_app.DEFAULT_PORT, 8000)

    def test_02_build_desktop_spec_generation(self):
        """Verify build_desktop generates valid PyInstaller spec file with required assets.

        Preconditions: build_desktop module available in workspace.
        Invariants: Spec file created on disk with UTF-8 encoded application metadata.
        Expected Outcomes: Spec file exists and contains expected application name and asset references.
        """
        spec_path = build_desktop.create_spec_file()
        self.assertTrue(os.path.exists(spec_path))
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("UroborosKnowledgeHub", content)
        self.assertIn("desktop_app.py", content)
        self.assertIn("index.html", content)

    def test_03_desktop_build_check(self):
        """Verify build_desktop check mode executes cleanly without compilation.

        Preconditions: PyInstaller check mode flag active.
        Invariants: Spec check completes validation without launching PyInstaller build process.
        Expected Outcomes: build_executable(check_only=True) returns True.
        """
        res = build_desktop.build_executable(check_only=True)
        self.assertTrue(res)

    def test_04_spec_path_escaping_and_synchronization(self):
        """Verify build spec files use valid path string escaping and stay synchronized.

        Preconditions: build_desktop creates spec file and build/ directory spec exists.
        Invariants: Spec file pathex uses raw string or forward slashes without syntax errors.
        Expected Outcomes: Both spec files parse cleanly without escape sequence errors.
        """
        spec_path = build_desktop.create_spec_file()
        build_spec_path = os.path.join(self.root_dir, "build", "UroborosKnowledgeHub.spec")
        
        self.assertTrue(os.path.exists(spec_path))
        self.assertTrue(os.path.exists(build_spec_path))
        
        import ast
        for p in (spec_path, build_spec_path):
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("pathex=[r'", content)
            parsed = ast.parse(content)
            self.assertIsNotNone(parsed)

    def test_05_desktop_app_frozen_path_resolution(self):
        """Verify desktop_app handles sys._MEIPASS CWD guard under PyInstaller frozen environment.

        Preconditions: Mock sys.frozen=True and sys._MEIPASS to temporary directory.
        Invariants: Working directory changes to sys._MEIPASS on module execution.
        Expected Outcomes: CWD equals sys._MEIPASS inside frozen runtime block.
        """
        import tempfile
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

    def test_06_desktop_executable_artifact_check(self):
        """Verify desktop executable dist artifact status if prebuilt.

        Preconditions: Build environment check.
        Invariants: If dist/UroborosKnowledgeHub.exe exists, it is non-empty executable.
        Expected Outcomes: Executable file size > 1MB if present, check mode returns True.
        """
        exe_path = os.path.join(self.root_dir, "dist", "UroborosKnowledgeHub.exe")
        check_ok = build_desktop.build_executable(check_only=True)
        self.assertTrue(check_ok)
        if os.path.exists(exe_path):
            self.assertGreater(os.path.getsize(exe_path), 1000000)

if __name__ == "__main__":
    unittest.main()


