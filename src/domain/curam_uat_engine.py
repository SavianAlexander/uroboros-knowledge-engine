"""
Backward-compatibility re-export facade for Cúram, Jira, and UAT engines.
Delegates to modular src.domain.curam_engine, src.domain.jira_engine, and src.domain.uat_engine.
"""

from src.domain.curam_engine import (
    CuramExpressRulesEngine,
    get_monthly_fpl,
    FPL_ANNUAL_BASE_2026,
    FPL_ANNUAL_PER_PERSON_2026,
    SNAP_MAX_ALLOTMENTS_2026,
    TANF_MAX_BENEFITS_2026
)
from src.domain.jira_engine import JiraTestCaseGenerator
from src.domain.uat_engine import UserAcceptanceTestRunner

__all__ = [
    "CuramExpressRulesEngine",
    "JiraTestCaseGenerator",
    "UserAcceptanceTestRunner",
    "get_monthly_fpl",
    "FPL_ANNUAL_BASE_2026",
    "FPL_ANNUAL_PER_PERSON_2026",
    "SNAP_MAX_ALLOTMENTS_2026",
    "TANF_MAX_BENEFITS_2026"
]
