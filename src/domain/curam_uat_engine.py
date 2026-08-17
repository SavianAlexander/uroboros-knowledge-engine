"""
Backward-compatibility re-export facade for Cúram, Jira, and UAT engines.
Delegates to modular src.domain.curam_engine, src.domain.jira_engine, and src.domain.uat_engine.
"""

from src.domain.curam_engine import (
    CuramExpressRulesEngine,
    get_monthly_fpl
)
from src.domain.jira_engine import JiraTestCaseGenerator
from src.domain.uat_engine import UserAcceptanceTestRunner

__all__ = [
    "CuramExpressRulesEngine",
    "JiraTestCaseGenerator",
    "UserAcceptanceTestRunner",
    "get_monthly_fpl"
]
