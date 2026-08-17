"""
FastAPI Router for IBM Cúram SPM, CER Rules Decision Engine, Jira Xray/Zephyr QA, and UAT Certification.
Standard: Pure Python standard library + FastAPI / Pydantic.
Grounded in empirical statutory datasets (2026 guidelines).
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from src.domain.curam_engine import CuramExpressRulesEngine, get_monthly_fpl
from src.domain.jira_engine import JiraTestCaseGenerator, JiraApiBridge
from src.domain.uat_engine import UserAcceptanceTestRunner
from src.domain.statutory_data import load_statutory_policy

router = APIRouter(prefix="/api/curam", tags=["Cúram Social Program Management & QA Studio"])


class CuramEvidencePayload(BaseModel):
    applicant_name: str = Field(default="Anonymous Citizen", description="Full name of applicant")
    household_size: int = Field(default=1, ge=1, description="Number of household members")
    earned_income_monthly: float = Field(default=0.0, ge=0.0, description="Gross monthly wages/salary")
    unearned_income_monthly: float = Field(default=0.0, ge=0.0, description="Monthly SSDI, child support, or other income")
    shelter_cost_monthly: float = Field(default=0.0, ge=0.0, description="Monthly rent or mortgage")
    utility_standard_monthly: float = Field(default=150.0, ge=0.0, description="Standard Utility Allowance (SUA)")
    liquid_assets: float = Field(default=0.0, ge=0.0, description="Checking, savings, or cash resources")
    is_resident: bool = Field(default=True, description="State residency verification")
    has_qualified_immigration_status: bool = Field(default=True, description="Citizenship or lawful presence status")
    is_child_under_19: bool = Field(default=False, description="Child dependent indicator")
    is_pregnant: bool = Field(default=False, description="Pregnancy indicator")
    has_disability: bool = Field(default=False, description="Aged, Blind, or Disabled (ABD) status")
    has_minor_child: bool = Field(default=False, description="Minor dependent indicator for TANF")
    has_elderly_or_disabled_member: bool = Field(default=False, description="Elderly/disabled SNAP disregard flag")
    tanf_lifetime_months_received: int = Field(default=0, ge=0, description="Cumulative TANF receipt months")
    contract_rent_monthly: float = Field(default=1450.0, ge=0.0, description="Actual rent for Section 8 calculation")
    bedrooms: str = Field(default="2", description="Unit bedroom count (0, 1, 2, 3, 4)")
    region: str = Field(default="contiguous_48_and_dc", description="FPL region")


class JiraTestRequest(BaseModel):
    program: str = Field(default="MEDICAID_MAGI", description="Statutory program (MEDICAID_MAGI, CHIP, SNAP, TANF, WIC, CCDF, SECTION8, ALL)")
    format_type: str = Field(default="json", description="Output format: json or markdown")


class JiraPushRequest(BaseModel):
    program: str = Field(default="MEDICAID_MAGI", description="Target statutory program")
    project_key: str = Field(default="SPM", description="Jira project key")
    jira_base_url: Optional[str] = Field(default=None, description="Optional Jira Cloud base URL")
    api_token: Optional[str] = Field(default=None, description="Optional Jira API token")


class UATRunRequest(BaseModel):
    programs: List[str] = Field(
        default=["MEDICAID_MAGI", "CHIP", "SNAP", "TANF", "WIC", "CCDF", "SECTION8"],
        description="Programs to execute in UAT suite"
    )


@router.get("/policy/tables")
def get_statutory_policy_tables():
    """Retrieve full empirical statutory policy dataset (FPL, SNAP, TANF, CHIP, WIC, CCDF, Section 8)."""
    try:
        policy = load_statutory_policy()
        return {"status": "success", "data": policy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fpl/{household_size}")
def get_fpl_guidelines(household_size: int, region: str = "contiguous_48_and_dc"):
    """Query statutory 2026 Federal Poverty Level guidelines for a given household size."""
    try:
        fpl_100 = get_monthly_fpl(household_size, region=region)
        return {
            "status": "success",
            "household_size": household_size,
            "region": region,
            "fpl_100_monthly": fpl_100,
            "fpl_138_monthly": round(fpl_100 * 1.38, 2),
            "fpl_185_monthly": round(fpl_100 * 1.85, 2),
            "fpl_200_monthly": round(fpl_100 * 2.00, 2),
            "fpl_250_monthly": round(fpl_100 * 2.50, 2),
            "fpl_300_monthly": round(fpl_100 * 3.00, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cer/evaluate")
def evaluate_curam_rules(payload: CuramEvidencePayload, program: Optional[str] = None):
    """Evaluate citizen evidence against IBM Cúram Express Rules (CER) Engine across social programs."""
    try:
        evidence = payload.model_dump()
        if program and program.upper() != "ALL":
            p = program.upper()
            if "MEDICAID" in p:
                res = CuramExpressRulesEngine.evaluate_medicaid_magi(evidence)
            elif "CHIP" in p:
                res = CuramExpressRulesEngine.evaluate_chip(evidence)
            elif "SNAP" in p:
                res = CuramExpressRulesEngine.evaluate_snap(evidence)
            elif "TANF" in p:
                res = CuramExpressRulesEngine.evaluate_tanf(evidence)
            elif "WIC" in p:
                res = CuramExpressRulesEngine.evaluate_wic(evidence)
            elif "CCDF" in p:
                res = CuramExpressRulesEngine.evaluate_ccdf(evidence)
            elif "SEC" in p:
                res = CuramExpressRulesEngine.evaluate_section8(evidence)
            else:
                res = CuramExpressRulesEngine.evaluate_integrated_case(evidence)
            return {"status": "success", "program": program, "data": res}
        
        result = CuramExpressRulesEngine.evaluate_integrated_case(evidence)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/generate")
def generate_jira_test_cases(payload: JiraTestRequest):
    """Generate standardized Jira Xray/Zephyr-compatible test cases with full step-by-step procedure and traceability."""
    try:
        cases = JiraTestCaseGenerator.generate_suite_for_domain(payload.program)
        if payload.format_type.lower() == "markdown":
            md_content = JiraTestCaseGenerator.export_jira_markdown(cases)
            return {"status": "success", "program": payload.program, "format": "markdown", "markdown": md_content}
        return {
            "status": "success",
            "program": payload.program,
            "format": "json",
            "total_test_cases": len(cases),
            "test_cases": cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/push")
def push_jira_test_cases(payload: JiraPushRequest):
    """Synchronize synthesized test cases to Jira Cloud / Data Center or verified sandbox."""
    try:
        cases = JiraTestCaseGenerator.generate_suite_for_domain(payload.program)
        sync_res = JiraApiBridge.push_test_cases_to_jira(
            test_cases=cases,
            jira_base_url=payload.jira_base_url,
            project_key=payload.project_key,
            api_token=payload.api_token
        )
        return {"status": "success", "data": sync_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/uat/run")
def run_uat_suite(payload: UATRunRequest):
    """Execute automated User Acceptance Testing (UAT) scenarios and compute Merkle provenance proof."""
    try:
        suite_res = UserAcceptanceTestRunner.run_uat_suite(programs=payload.programs)
        return {"status": "success", "data": suite_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uat/certificate")
def get_uat_certificate(approver: str = Query(default="Chief Information Officer / Health & Human Services SME")):
    """Generate and return the official SOC 2 Merkle-attested UAT Sign-Off Certificate in markdown format."""
    try:
        suite_res = UserAcceptanceTestRunner.run_uat_suite()
        cert_md = UserAcceptanceTestRunner.generate_uat_certificate_markdown(suite_res, approver=approver)
        return {
            "status": "success",
            "approver": approver,
            "merkle_provenance_hash": suite_res.get("merkle_provenance_hash"),
            "certificate_markdown": cert_md
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
