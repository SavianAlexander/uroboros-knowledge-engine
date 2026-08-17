"""
Backward-compatibility facade forwarding to curam_bridge, jira_bridge, and uat_bridge.
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from curam_bridge import evaluate_cer_cli, self_test as curam_self_test
from jira_bridge import generate_jira_tests_cli, self_test as jira_self_test
from uat_bridge import run_uat_suite_cli, export_uat_certificate_cli, execute_contract, self_test as uat_self_test


def self_test():
    """Run all 3 sub-bridge self tests."""
    c = curam_self_test()
    j = jira_self_test()
    u = uat_self_test()
    return 0 if (c == 0 and j == 0 and u == 0) else 1


if __name__ == "__main__":
    sys.exit(self_test())
