"""
Neuro Co-Pilot User Acceptance Testing (UAT) & Sign-Off Certification Bridge.
Standard: Pure Python Standard Library (json, sys, os, time, argparse, hashlib).
Ponytail Senior Dev Principle: Dedicated zero-dependency bridge for executing business SME acceptance tests,
tracking defect severity triage, and issuing cryptographically verified SOC 2 Merkle Sign-Off Certificates.
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

from src.domain.uat_engine import UserAcceptanceTestRunner

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_uat_suite_cli(domains: List[str] = None) -> str:
    """Execute end-to-end UAT test scenario matrix."""
    try:
        suite_res = UserAcceptanceTestRunner.run_uat_suite(domains=domains)
        return json.dumps({"status": "success", "data": suite_res}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def export_uat_certificate_cli(approver: str = "Chief Information Officer / Product Owner SME") -> str:
    """Generate official Merkle-signed UAT Sign-Off Certificate."""
    try:
        suite_res = UserAcceptanceTestRunner.run_uat_suite()
        cert_md = UserAcceptanceTestRunner.generate_uat_certificate_markdown(suite_res, approver)
        
        out_dir = os.path.join(BASE_DIR, "docs", "uat")
        os.makedirs(out_dir, exist_ok=True)
        cert_path = os.path.join(out_dir, "uat_acceptance_certificate.md")
        with open(cert_path, "w", encoding="utf-8") as f:
            f.write(cert_md)

        return json.dumps({
            "status": "success",
            "acceptance_verdict": suite_res["acceptance_verdict"],
            "pass_rate": suite_res["pass_rate"],
            "merkle_provenance_hash": suite_res["merkle_provenance_hash"],
            "certificate_path": cert_path,
            "markdown_preview": cert_md[:500] + "..."
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def execute_contract(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute contract for parallel Contract Bus integration."""
    t0 = time.time()
    uat_res = UserAcceptanceTestRunner.run_uat_suite()
    duration_ms = round((time.time() - t0) * 1000.0, 2)
    
    return {
        "status": "SUCCESS",
        "bridge": "uat_bridge",
        "duration_ms": duration_ms,
        "total_uat_scenarios": uat_res["total_scenarios"],
        "passed_uat_scenarios": uat_res["passed_scenarios"],
        "pass_rate": uat_res["pass_rate"],
        "acceptance_verdict": uat_res["acceptance_verdict"],
        "merkle_provenance_hash": uat_res["merkle_provenance_hash"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def self_test():
    """Assert-based self-test suite for uat_bridge.py."""
    print("=== Running User Acceptance Testing (UAT) Bridge Self-Test Suite ===")

    # 1. Execute full UAT suite
    uat_res = UserAcceptanceTestRunner.run_uat_suite()
    assert uat_res["total_scenarios"] >= 5, f"Expected >=5 scenarios, got {uat_res['total_scenarios']}"
    assert uat_res["failed_scenarios"] == 0, f"UAT failures detected: {uat_res['failed_scenarios']}"
    assert uat_res["acceptance_verdict"] == "ACCEPTED_FOR_PRODUCTION", "UAT acceptance verdict not approved"
    assert len(uat_res["merkle_provenance_hash"]) == 64, "Invalid Merkle root hash length"
    print(f"  [Pass] UAT Suite Execution verified ({uat_res['total_scenarios']} scenarios, 100% Pass Rate)")

    # 2. Test Certificate Generator
    cert_md = UserAcceptanceTestRunner.generate_uat_certificate_markdown(uat_res)
    assert "Official User Acceptance Testing (UAT) Sign-Off Certificate" in cert_md, "Certificate export failed"
    assert uat_res["merkle_provenance_hash"] in cert_md, "Missing Merkle root in certificate"
    print("  [Pass] Official UAT Sign-Off Certificate generation verified")

    # 3. Contract execution check
    contract = execute_contract()
    assert contract["status"] == "SUCCESS", "Contract execution failed"
    print("  [Pass] Inter-Bridge Contract interface clean")

    print("=========================================================")
    print("User Acceptance Testing (UAT) Bridge Self-Test: 100% PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot User Acceptance Testing (UAT) Bridge")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    p_run = subparsers.add_parser("run", help="Execute UAT test suite")
    p_run.add_argument("--domains", nargs="+", default=["MEDICAID_MAGI", "SNAP", "TANF"], help="Target domains")

    p_cert = subparsers.add_parser("certificate", help="Generate official UAT Sign-Off Certificate")
    p_cert.add_argument("--approver", default="Chief Information Officer / Product Owner SME", help="Approver title")

    subparsers.add_parser("self_test", help="Execute bridge self-test assertions")

    args = parser.parse_args()

    if args.command == "run":
        print(run_uat_suite_cli(args.domains))
    elif args.command == "certificate":
        print(export_uat_certificate_cli(args.approver))
    elif args.command == "self_test":
        sys.exit(self_test())
    else:
        sys.exit(self_test())


if __name__ == "__main__":
    main()
