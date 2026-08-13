"""
Semantic Code-Text Alignment & Docstring Harmonizer Engine.
Compares function implementation logic against docstrings, identifying outdated documentation.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List
import ast


def check_code_docstring_alignment(code_snippet: str) -> Dict[str, Any]:
    """
    Checks alignment between function code arguments and docstrings.
    """
    if not code_snippet or not isinstance(code_snippet, str) or not code_snippet.strip():
        return {"alignment_issues": [], "status": "empty_code"}

    try:
        tree = ast.parse(code_snippet)
    except Exception as e:
        return {"alignment_issues": [], "error": str(e), "status": "syntax_error"}

    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            all_args = (
                getattr(node.args, "posonlyargs", []) +
                node.args.args +
                getattr(node.args, "kwonlyargs", [])
            )
            func_args = [a.arg for a in all_args if a.arg not in ("self", "cls")]
            
            if not doc:
                issues.append({"function": node.name, "issue": "missing_docstring"})
            else:
                missing_in_doc = [arg for arg in func_args if arg not in doc]
                if missing_in_doc:
                    issues.append({
                        "function": node.name,
                        "issue": "undocumented_args",
                        "missing_args": missing_in_doc
                    })

    return {
        "alignment_issues": issues,
        "is_aligned": len(issues) == 0,
        "status": "success"
    }
