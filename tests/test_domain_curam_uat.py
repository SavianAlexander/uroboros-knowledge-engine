"""
Domain Unit Test Suite: IBM Cúram SPM, Jira Test Case Generator & UAT Engine.
Standard: Pure Python Standard Library (unittest) + FastAPI TestClient.
Ponytail Senior Dev Principle: 100% assert-based test coverage with zero external mocking frameworks.
"""

import unittest
import json
import os
import sys

# Ensure repository root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.domain.curam_engine import CuramExpressRulesEngine, get_monthly_fpl
from src.domain.jira_engine import JiraTestCaseGenerator, JiraApiBridge
from src.domain.uat_engine import UserAcceptanceTestRunner
from src.domain.statutory_data import load_statutory_policy
from src.app.server import app
from fastapi.testclient import TestClient


class TestCuramUatDomainEngine(unittest.TestCase):
    """Test suite verifying Cúram CER decision logic, Jira test formatting, and UAT runner across 7 programs."""

    def test_statutory_policy_dataset_loading(self):
        """Verify empirical statutory policy dataset loads and contains 2026 guidelines."""
        policy = load_statutory_policy()
        self.assertIn("fpl_guidelines", policy)
        self.assertIn("snap", policy)
        self.assertIn("chip", policy)
        self.assertIn("wic", policy)
        self.assertIn("ccdf_childcare", policy)
        self.assertIn("section8_housing", policy)

    def test_monthly_fpl_calculation(self):
        """Verify statutory 2026 FPL calculations."""
        fpl_1 = get_monthly_fpl(1)
        self.assertAlmostEqual(fpl_1, 1304.17, places=1)
        fpl_4 = get_monthly_fpl(4)
        self.assertAlmostEqual(fpl_4, 2684.17, places=1)

    def test_medicaid_magi_eligible_adult(self):
        """Verify Medicaid MAGI Adult Expansion eligibility under 138% FPL."""
        evidence = {
            "applicant_name": "Maria Rodriguez",
            "household_size": 1,
            "earned_income_monthly": 1200.0,
            "unearned_income_monthly": 0.0,
            "is_resident": True,
            "has_qualified_immigration_status": True
        }
        res = CuramExpressRulesEngine.evaluate_medicaid_magi(evidence)
        self.assertTrue(res["eligible"])
        self.assertEqual(res["category"], "Medicaid MAGI Adult Expansion (138%)")
        self.assertEqual(res["decision_code"], "APPROVED")

    def test_medicaid_magi_over_income_denial(self):
        """Verify denial when income exceeds 138% FPL."""
        evidence_over = {
            "applicant_name": "David Torres",
            "household_size": 1,
            "earned_income_monthly": 4500.0,
            "is_resident": True,
            "has_qualified_immigration_status": True
        }
        res = CuramExpressRulesEngine.evaluate_medicaid_magi(evidence_over)
        self.assertFalse(res["eligible"])
        self.assertEqual(res["decision_code"], "DENIED")
        self.assertTrue(any("Excess Countable Income" in r for r in res["reason_codes"]))

    def test_chip_coverage(self):
        """Verify CHIP decision for uninsured child."""
        evidence_chip = {
            "applicant_name": "Leo Child",
            "household_size": 3,
            "earned_income_monthly": 4000.0,
            "is_child_under_19": True,
            "is_uninsured": True
        }
        res = CuramExpressRulesEngine.evaluate_chip(evidence_chip)
        self.assertTrue(res["eligible"])
        self.assertEqual(res["program"], "CHIP")

    def test_snap_allotment_calculation(self):
        """Verify SNAP Gross/Net test, 20% earned deduction, and monthly allotment."""
        evidence = {
            "applicant_name": "Carlos Gomez",
            "household_size": 3,
            "earned_income_monthly": 1600.0,
            "unearned_income_monthly": 0.0,
            "shelter_cost_monthly": 650.0,
            "utility_standard_monthly": 150.0,
            "liquid_assets": 500.0,
            "is_resident": True
        }
        res = CuramExpressRulesEngine.evaluate_snap(evidence)
        self.assertTrue(res["eligible"])
        self.assertEqual(res["max_possible_allotment"], 768.0)
        self.assertGreater(res["monthly_benefit_allotment"], 0.0)

    def test_tanf_cash_grant_calculation(self):
        """Verify TANF deprivation, asset cap, and monthly grant."""
        evidence = {
            "applicant_name": "Jessica Taylor",
            "household_size": 2,
            "earned_income_monthly": 150.0,
            "liquid_assets": 800.0,
            "has_minor_child": True,
            "tanf_lifetime_months_received": 10
        }
        res = CuramExpressRulesEngine.evaluate_tanf(evidence)
        self.assertTrue(res["eligible"])
        self.assertGreater(res["monthly_cash_grant"], 0.0)
        self.assertEqual(res["max_standard_grant"], 320.0)

    def test_wic_and_ccdf_evaluations(self):
        """Verify WIC nutritional package and CCDF child care copay."""
        wic_ev = {
            "household_size": 2,
            "earned_income_monthly": 1800.0,
            "is_pregnant": True,
            "has_nutritional_risk": True
        }
        wic_res = CuramExpressRulesEngine.evaluate_wic(wic_ev)
        self.assertTrue(wic_res["eligible"])
        self.assertEqual(wic_res["priority_tier"], "PRIORITY_I")

        ccdf_ev = {
            "household_size": 3,
            "earned_income_monthly": 2500.0,
            "has_child_under_13": True,
            "is_working_or_training": True
        }
        ccdf_res = CuramExpressRulesEngine.evaluate_ccdf(ccdf_ev)
        self.assertTrue(ccdf_res["eligible"])
        self.assertGreaterEqual(ccdf_res["copay_rate_percentage"], 0.0)

    def test_section8_housing_voucher(self):
        """Verify HUD Section 8 housing voucher and 30% tenant rent."""
        sec8_ev = {
            "household_size": 3,
            "earned_income_monthly": 1500.0,
            "bedrooms": "2",
            "contract_rent_monthly": 1500.0
        }
        res = CuramExpressRulesEngine.evaluate_section8(sec8_ev)
        self.assertTrue(res["eligible"])
        self.assertEqual(res["tenant_rent_contribution"], 450.0)
        self.assertEqual(res["housing_assistance_payment"], 1050.0)

    def test_integrated_multi_program_case(self):
        """Verify integrated PDC evaluation across all 7 statutory programs."""
        evidence = {
            "applicant_name": "Elena Morales",
            "household_size": 3,
            "earned_income_monthly": 1600.0,
            "unearned_income_monthly": 0.0,
            "shelter_cost_monthly": 650.0,
            "utility_standard_monthly": 150.0,
            "liquid_assets": 800.0,
            "is_resident": True,
            "has_qualified_immigration_status": True,
            "has_minor_child": True,
            "is_working_or_training": True
        }
        res = CuramExpressRulesEngine.evaluate_integrated_case(evidence)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["approved_programs_count"], 3)
        self.assertIn("SNAP", res["approved_programs"])
        self.assertIn("MEDICAID_MAGI", res["approved_programs"])

    def test_jira_test_case_generator_and_push(self):
        """Verify Jira Xray/Zephyr test case synthesis and push simulation."""
        cases = JiraTestCaseGenerator.generate_suite_for_domain("ALL")
        self.assertGreaterEqual(len(cases), 7)
        
        md_export = JiraTestCaseGenerator.export_jira_markdown(cases)
        self.assertIn("Jira Xray / Zephyr QA Test Specification Suite", md_export)
        self.assertIn("JIRA-TC-SNAP-001", md_export)

        push_res = JiraApiBridge.push_test_cases_to_jira(cases[:3], project_key="SPM")
        self.assertEqual(push_res["status"], "success")
        self.assertEqual(push_res["synced_count"], 3)

    def test_uat_suite_and_merkle_provenance(self):
        """Verify full UAT scenario matrix and Merkle provenance certificate."""
        uat_res = UserAcceptanceTestRunner.run_uat_suite()
        self.assertGreaterEqual(uat_res["total_scenarios"], 5)
        self.assertEqual(uat_res["acceptance_verdict"], "ACCEPTED_FOR_PRODUCTION")
        self.assertTrue(len(uat_res["merkle_provenance_hash"]) == 64)

        cert_md = UserAcceptanceTestRunner.generate_uat_certificate_markdown(uat_res)
        self.assertIn("Official User Acceptance Testing (UAT) Sign-Off Certificate", cert_md)
        self.assertIn(uat_res["merkle_provenance_hash"], cert_md)


class TestCuramFastApiEndpoints(unittest.TestCase):
    """Test suite verifying FastAPI endpoints for Cúram, Jira, and UAT."""

    def setUp(self):
        self.client = TestClient(app)

    def test_policy_tables_endpoint(self):
        resp = self.client.get("/api/curam/policy/tables")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("fpl_guidelines", data["data"])

    def test_fpl_endpoint(self):
        resp = self.client.get("/api/curam/fpl/3")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["household_size"], 3)
        self.assertAlmostEqual(data["fpl_100_monthly"], 2224.17, places=1)

    def test_cer_evaluate_endpoint(self):
        payload = {
            "applicant_name": "Test Citizen",
            "household_size": 2,
            "earned_income_monthly": 1500.0
        }
        resp = self.client.post("/api/curam/cer/evaluate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("programs", data["data"])

    def test_jira_generate_and_push_endpoint(self):
        resp = self.client.post("/api/curam/jira/generate", json={"program": "SNAP", "format_type": "json"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["program"], "SNAP")

        push_resp = self.client.post("/api/curam/jira/push", json={"program": "SNAP", "project_key": "SPM"})
        self.assertEqual(push_resp.status_code, 200)
        push_data = push_resp.json()
        self.assertEqual(push_data["status"], "success")

    def test_uat_run_endpoint(self):
        resp = self.client.post("/api/curam/uat/run", json={"programs": ["MEDICAID_MAGI", "SNAP"]})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("merkle_provenance_hash", data["data"])

    def test_uat_certificate_endpoint(self):
        resp = self.client.get("/api/curam/uat/certificate?approver=Chief%20Architect")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("certificate_markdown", data)
        self.assertIn("Chief Architect", data["certificate_markdown"])


if __name__ == "__main__":
    unittest.main()
