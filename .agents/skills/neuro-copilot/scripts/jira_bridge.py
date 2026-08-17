"""
Neuro Co-Pilot Jira Issue & QA Test Case Management Bridge (Xray & Zephyr Standards).
Standard: Pure Python Standard Library (json, sys, os, time, argparse).
Ponytail Senior Dev Principle: Dedicated zero-dependency bridge for synthesizing Jira Test Cases,
generating Xray/Zephyr specifications, and validating requirements-to-test traceability across any domain.
"""

import sys
import os
import json
import time
import argparse
from typing import Dict, Any, List

# Ensure repository root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from src.domain.jira_engine import JiraTestCaseGenerator

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def generate_jira_tests_cli(domain: str = "MEDICAID_MAGI", format_type: str = "json") -> str:
    """Generate formal Jira/Xray/Zephyr test case specifications."""
    try:
        cases = JiraTestCaseGenerator.generate_suite_for_domain(domain)
        if format_type.lower() == "markdown":
            return JiraTestCaseGenerator.export_jira_markdown(cases)
        return json.dumps({
            "status": "success",
            "domain": domain,
            "total_test_cases": len(cases),
            "test_cases": cases
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def export_jira_spec_file(domain: str = "MEDICAID_MAGI", out_dir: str = None) -> str:
    """Save formatted Jira test case specification to markdown file in docs/jira/."""
    try:
        cases = JiraTestCaseGenerator.generate_suite_for_domain(domain)
        md = JiraTestCaseGenerator.export_jira_markdown(cases)
        target_dir = out_dir or os.path.join(BASE_DIR, "docs", "jira")
        os.makedirs(target_dir, exist_ok=True)
        out_file = os.path.join(target_dir, f"{domain.lower()}_jira_test_spec.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md)
        return json.dumps({
            "status": "success",
            "file_path": out_file,
            "total_cases": len(cases)
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def execute_contract(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute contract for parallel Contract Bus integration."""
    t0 = time.time()
    med_cases = JiraTestCaseGenerator.generate_suite_for_domain("MEDICAID_MAGI")
    snap_cases = JiraTestCaseGenerator.generate_suite_for_domain("SNAP")
    tanf_cases = JiraTestCaseGenerator.generate_suite_for_domain("TANF")
    total = len(med_cases) + len(snap_cases) + len(tanf_cases)
    duration_ms = round((time.time() - t0) * 1000.0, 2)

    return {
        "status": "SUCCESS",
        "bridge": "jira_bridge",
        "duration_ms": duration_ms,
        "total_test_cases_managed": total,
        "xray_zephyr_ready": True,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def self_test():
    """Assert-based self-test suite for jira_bridge.py."""
    print("=== Running Jira Test Case & QA Bridge Self-Test Suite ===")

    # 1. Test suite generation for Medicaid
    med_cases = JiraTestCaseGenerator.generate_suite_for_domain("MEDICAID_MAGI")
    assert len(med_cases) >= 3, f"Expected >=3 cases for Medicaid, got {len(med_cases)}"
    first = med_cases[0]
    assert first["issueType"] == "Test", "Invalid Jira issueType"
    assert "testSteps" in first and len(first["testSteps"]) > 0, "Missing test steps"
    assert "preconditions" in first, "Missing preconditions"
    assert "requirementLinks" in first, "Missing requirements traceability"
    print(f"  [Pass] Medicaid Jira Xray/Zephyr test suite verified ({len(med_cases)} test cases)")

    # 2. Test suite generation for SNAP
    snap_cases = JiraTestCaseGenerator.generate_suite_for_domain("SNAP")
    assert len(snap_cases) >= 1, "Missing SNAP test cases"
    print("  [Pass] SNAP Jira test case synthesis verified")

    # 3. Test Markdown exporter
    md = JiraTestCaseGenerator.export_jira_markdown(med_cases)
    assert "# 📋 Jira Test Case Specification" in md, "Invalid markdown header"
    assert "Step-by-Step Test Procedure" in md, "Missing procedure table"
    print("  [Pass] Jira Xray/Zephyr markdown export verified")

    # 4. Contract execution check
    contract = execute_contract()
    assert contract["status"] == "SUCCESS", "Contract execution failed"
    print("  [Pass] Inter-Bridge Contract interface clean")

    print("=========================================================")
    print("Jira Test Case & QA Bridge Self-Test: 100% PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot Jira Issue & QA Test Case Bridge")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    p_gen = subparsers.add_parser("generate", help="Generate Jira test cases for domain")
    p_gen.add_argument("--domain", default="MEDICAID_MAGI", help="Domain or program name")
    p_gen.add_argument("--format", default="json", choices=["json", "markdown"], help="Output format")

    p_export = subparsers.add_parser("export", help="Export test specification to docs/jira/")
    p_export.add_argument("--domain", default="MEDICAID_MAGI", help="Domain or program name")

    subparsers.add_parser("self_test", help="Execute bridge self-test assertions")

    args = parser.parse_args()

    if args.command == "generate":
        print(generate_jira_tests_cli(args.domain, args.format))
    elif args.command == "export":
        print(export_jira_spec_file(args.domain))
    elif args.command == "self_test":
        sys.exit(self_test())
    else:
        sys.exit(self_test())


if __name__ == "__main__":
    main()
