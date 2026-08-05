"""
Standalone E2E UI Test Runner for Uroboros Knowledge Engine.
- Spawns FastAPI/Uvicorn test server bound dynamically to an OS ephemeral socket.
- Executes urllib.request.urlopen health polling loop against /api/health before running test suites.
- Executes test modules:
    1. tests/test_e2e_t1_feature_coverage.py
    2. tests/test_e2e_t2_boundary_corner.py
    3. tests/test_e2e_t3_cross_feature.py
    4. tests/test_e2e_t4_realworld_workloads.py
- Validates SHA-256 Bitwise Asset Parity between root UI files (index.html, style.css, app.js) and src/assets/.
- Returns exit code 0 when all test suites pass.
"""

import sys
import time
import socket
import urllib.request
import threading
import unittest
import hashlib
from pathlib import Path

import uvicorn
from src.app.server import app


def get_ephemeral_port() -> int:
    """Dynamically bind to an OS ephemeral port to avoid socket collisions."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class ServerThread(threading.Thread):
    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="error")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def poll_health(host: str, port: int, timeout: float = 10.0) -> bool:
    """Poll /api/health endpoint until HTTP 200 OK or timeout."""
    url = f"http://{host}:{port}/api/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def verify_asset_parity():
    """Verify 100% SHA-256 bitwise parity between root UI files and src/assets/."""
    files = ["index.html", "style.css", "app.js"]
    for fname in files:
        root_path = Path(fname)
        asset_path = Path(f"src/assets/{fname}")
        if not root_path.exists() or not asset_path.exists():
            raise RuntimeError(f"Missing file for parity check: {fname}")

        root_hash = hashlib.sha256(root_path.read_bytes()).hexdigest()
        asset_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
        if root_hash != asset_hash:
            raise RuntimeError(
                f"SHA-256 Asset Parity Mismatch for {fname}: root={root_hash} vs asset={asset_hash}"
            )
    print("SHA-256 Bitwise Asset Parity Check Passed: index.html, style.css, app.js match src/assets/ perfectly.")


def main_runner():
    print("=========================================================")
    print(" Uroboros Knowledge Engine — Standalone E2E Test Runner")
    print("=========================================================")

    # 1. Verify UI Asset Parity
    try:
        verify_asset_parity()
    except Exception as e:
        print(f"Asset Parity Verification Failed: {e}")
        sys.exit(1)

    # 2. Ephemeral Port Socket Binding
    host = "127.0.0.1"
    port = get_ephemeral_port()
    print(f"[E2E Runner] Dynamic Ephemeral Socket Bound to http://{host}:{port}")

    # 3. Start Background Server
    server_thread = ServerThread(host, port)
    server_thread.start()

    # 4. Health Polling Loop
    print(f"[E2E Runner] Polling /api/health at http://{host}:{port}/api/health...")
    healthy = poll_health(host, port, timeout=10.0)
    if not healthy:
        print("[E2E Runner] ERROR: Test server failed to start or respond to /api/health within timeout.")
        server_thread.stop()
        sys.exit(1)

    print("[E2E Runner] Server Health Check OK! Running 4-Tier Test Suite...")

    # 5. Load and Execute Test Modules
    test_modules = [
        "tests.test_e2e_t1_feature_coverage",
        "tests.test_e2e_t2_boundary_corner",
        "tests.test_e2e_t3_cross_feature",
        "tests.test_e2e_t4_realworld_workloads",
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod_name in test_modules:
        try:
            mod_suite = loader.loadTestsFromName(mod_name)
            suite.addTest(mod_suite)
            print(f"  + Loaded test suite module: {mod_name}")
        except Exception as e:
            print(f"  - ERROR loading test module {mod_name}: {e}")
            server_thread.stop()
            sys.exit(1)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 6. Server Cleanup & Exit Code Evaluation
    print("\n[E2E Runner] Cleaning up background test server...")
    server_thread.stop()

    if result.wasSuccessful():
        print("\n=========================================================")
        print(" SUCCESS: All 4-Tier E2E Test Suites Passed Cleanly! (Exit Code 0)")
        print("=========================================================")
        sys.exit(0)
    else:
        print("\n=========================================================")
        print(f" FAILURE: Test suite encountered {len(result.failures)} failures and {len(result.errors)} errors.")
        print("=========================================================")
        sys.exit(1)


if __name__ == "__main__":
    main_runner()
