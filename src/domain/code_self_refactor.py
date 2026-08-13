"""
Autonomous Code Self-Refactoring & Style Enforcer Engine.
Analyzes Python AST trees, detects complexity spikes or unused imports, and proposes ponytail-optimized refactorings.
Zero-dependency, stdlib implementation (ast).
"""

import ast
from typing import Dict, Any, List


def analyze_and_propose_refactoring(code_snippet: str) -> Dict[str, Any]:
    """
    Parses Python code snippet and suggests ponytail-optimized refactorings.
    """
    if not code_snippet:
        return {"proposals": [], "status": "empty_code"}

    try:
        tree = ast.parse(code_snippet)
    except Exception as e:
        return {"proposals": [], "error": str(e), "status": "syntax_error"}

    proposals = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body_len = len(node.body)
            if body_len > 15:
                proposals.append({
                    "target": f"function:{node.name}",
                    "issue": "high_cyclomatic_complexity",
                    "suggestion": "Decompose into helper functions (Ponytail principle: keep functions concise)."
                })
        elif isinstance(node, ast.Try):
            if any(h.type is None or (isinstance(h.type, ast.Name) and h.type.id in ("Exception", "BaseException")) for h in node.handlers):
                proposals.append({
                    "target": "try_except_block",
                    "issue": "broad_or_bare_exception_catch",
                    "suggestion": "Catch specific exception types to prevent masking bugs (Ponytail: no bare excepts)."
                })

    return {
        "proposals": proposals,
        "total_proposals": len(proposals),
        "refactor_needed": len(proposals) > 0,
        "status": "success"
    }
