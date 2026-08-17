#!/usr/bin/env python3
"""
Test Failure Audit Script.
Parses pytest log tracebacks for test failures and reports them for remediation
without modifying test source files or suppressing legitimate defects.
"""

import sys
import os
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def audit_failed_tests(log_path="pytest.log"):
    if not os.path.exists(log_path):
        print(f"Log path '{log_path}' not found. No test tracebacks to parse.")
        return 0

    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        log_text = f.read()

    # Find failing test function paths: e.g., tests/test_e2e.py::test_legacy_ui
    failed_tests = re.findall(r"(tests/[^\s:]+\.py)::([a-zA-Z0-9_]+)\s+FAILED", log_text)
    if not failed_tests:
        print("[OK] No failed tests detected in pytest log.")
        return 0

    print(f"[AUDIT] Detected {len(failed_tests)} failing test(s) requiring remediation:")
    for file_rel, func_name in failed_tests:
        print(f"  - {file_rel}::{func_name}")
    return len(failed_tests)

if __name__ == "__main__":
    audit_failed_tests()

