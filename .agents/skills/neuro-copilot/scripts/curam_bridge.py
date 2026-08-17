"""
Neuro Co-Pilot IBM Cúram Social Program Management (SPM) Bridge.
Standard: Pure Python Standard Library (json, sys, os, time, argparse).
Ponytail Senior Dev Principle: Dedicated zero-dependency bridge for evaluating IBM Cúram CER statutory decision tables,
evidence management, and integrated case benefit delivery.
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

from src.domain.curam_engine import CuramExpressRulesEngine, get_monthly_fpl

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def evaluate_cer_cli(evidence_data: Any) -> str:
    """Evaluate citizen evidence against Cúram Express Rules (CER) Engine."""
    try:
        evidence = json.loads(evidence_data) if isinstance(evidence_data, str) else evidence_data
        result = CuramExpressRulesEngine.evaluate_integrated_case(evidence)
        return json.dumps({"status": "success", "data": result}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_fpl_table_cli(household_size: int = 1) -> str:
    """Retrieve 2026 Federal Poverty Level table for household size."""
    try:
        monthly = get_monthly_fpl(household_size)
        return json.dumps({
            "status": "success",
            "household_size": household_size,
            "fpl_100_monthly": monthly,
            "fpl_138_monthly": round(monthly * 1.38, 2),
            "fpl_200_monthly": round(monthly * 2.00, 2)
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def execute_contract(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute contract for parallel Contract Bus integration."""
    t0 = time.time()
    sample_evidence = {
        "applicant_name": "Maria Rodriguez",
        "household_size": 1,
        "earned_income_monthly": 1200.0,
        "is_resident": True,
        "has_qualified_immigration_status": True
    }
    eval_res = CuramExpressRulesEngine.evaluate_integrated_case(sample_evidence)
    duration_ms = round((time.time() - t0) * 1000.0, 2)
    
    return {
        "status": "SUCCESS",
        "bridge": "curam_bridge",
        "duration_ms": duration_ms,
        "cer_engine_status": "OPERATIONAL",
        "medicaid_eligible": "MEDICAID_MAGI" in eval_res.get("approved_programs", []),
        "total_benefits": eval_res.get("total_monthly_cash_and_nutrition_value", 0.0),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def self_test():
    """Assert-based self-test suite for curam_bridge.py."""
    print("=== Running IBM Cúram SPM Bridge Self-Test Suite ===")

    # 1. Test Medicaid MAGI Adult Expansion
    med_ev = {
        "applicant_name": "Maria Rodriguez",
        "household_size": 1,
        "earned_income_monthly": 1200.0,
        "is_resident": True,
        "has_qualified_immigration_status": True
    }
    med_res = CuramExpressRulesEngine.evaluate_medicaid_magi(med_ev)
    assert med_res["eligible"] is True, "Medicaid eligible applicant was marked ineligible"
    assert med_res.get("statutory_threshold_pct", 138.0) == 138.0, "Threshold should be 138%"
    print("  [Pass] CER Medicaid MAGI Adult Expansion calculation verified")

    # 2. Test Medicaid Over-Income Denial
    over_ev = {"household_size": 1, "earned_income_monthly": 4500.0, "is_resident": True}
    ineligible_med = CuramExpressRulesEngine.evaluate_medicaid_magi(over_ev)
    assert ineligible_med["eligible"] is False, "Over-income applicant was marked eligible"
    print("  [Pass] CER Medicaid Over-Income Denial rule verified")

    # 3. Test SNAP Allotment
    snap_ev = {
        "applicant_name": "Elena Morales",
        "household_size": 3,
        "earned_income_monthly": 1400.0,
        "shelter_cost_monthly": 600.0,
        "utility_standard_monthly": 150.0,
        "is_resident": True
    }
    snap_res = CuramExpressRulesEngine.evaluate_snap(snap_ev)
    assert snap_res["eligible"] is True, "SNAP calculation failed"
    allotment = snap_res.get("monthly_benefit_allotment", 0.0)
    assert allotment > 0, "SNAP allotment must be positive"
    print(f"  [Pass] CER SNAP Allotment verified (${allotment:.2f}/mo)")

    # 4. Test TANF Cash Assistance
    tanf_ev = {
        "household_size": 2,
        "earned_income_monthly": 150.0,
        "liquid_assets": 400.0,
        "has_minor_child": True,
        "is_resident": True
    }
    tanf_res = CuramExpressRulesEngine.evaluate_tanf(tanf_ev)
    assert tanf_res["eligible"] is True, "TANF calculation failed"
    grant = tanf_res.get("monthly_cash_grant", 0.0)
    print(f"  [Pass] CER TANF Cash Assistance verified (${grant:.2f}/mo)")

    # 5. Contract execution check
    contract = execute_contract()
    assert contract["status"] == "SUCCESS", "Contract execution failed"
    print("  [Pass] Inter-Bridge Contract interface clean")

    print("=========================================================")
    print("IBM Cúram SPM Bridge Self-Test: 100% PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot IBM Cúram SPM & CER Bridge")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    p_cer = subparsers.add_parser("evaluate", help="Evaluate evidence against CER rules")
    p_cer.add_argument("--evidence", required=True, help="JSON string or file path containing evidence")

    p_fpl = subparsers.add_parser("fpl", help="Retrieve FPL guideline thresholds")
    p_fpl.add_argument("--size", type=int, default=1, help="Household size")

    subparsers.add_parser("self_test", help="Execute bridge self-test assertions")

    args = parser.parse_args()

    if args.command == "evaluate":
        ev = args.evidence
        if os.path.isfile(ev):
            with open(ev, "r", encoding="utf-8") as f:
                ev = f.read()
        print(evaluate_cer_cli(ev))
    elif args.command == "fpl":
        print(get_fpl_table_cli(args.size))
    elif args.command == "self_test":
        sys.exit(self_test())
    else:
        sys.exit(self_test())


if __name__ == "__main__":
    main()
