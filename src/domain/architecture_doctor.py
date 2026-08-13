"""
Codebase AST Architecture Doctor & Anti-Pattern Sentinel.
Audits python files for monolithic god objects, excessive function complexity, and import health.
Zero-dependency, stdlib implementation.
"""

import os
import ast
from typing import Dict, Any, List, Optional
from src.domain.ast_parser import parse_python_ast


def audit_file_architecture(filepath: str) -> Dict[str, Any]:
    """Audits a single python file for structural complexity anti-patterns."""
    if not os.path.exists(filepath) or not filepath.endswith(".py"):
        return {"status": "error", "message": "Invalid python file"}

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        lines = code.splitlines()
        ast_data = parse_python_ast(code, filename=os.path.basename(filepath))

        warnings = []
        if len(lines) > 400:
            warnings.append(f"File is large ({len(lines)} lines). Consider modularizing.")

        funcs = ast_data.get("functions", [])
        if len(funcs) > 15:
            warnings.append(f"High function count ({len(funcs)} functions). High complexity risk.")

        return {
            "status": "success",
            "filepath": filepath,
            "line_count": len(lines),
            "class_count": len(ast_data.get("classes", [])),
            "function_count": len(ast_data.get("functions", [])),
            "import_count": len(ast_data.get("imports", [])),
            "warnings": warnings,
            "health_score": max(100 - (len(warnings) * 20), 40)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def audit_codebase_architecture(root_dir: str = "src") -> Dict[str, Any]:
    """Scans all python files in root_dir for structural architecture health."""
    results = []
    total_health = 0.0
    scanned = 0

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)
                res = audit_file_architecture(full_path)
                if res.get("status") == "success":
                    results.append(res)
                    total_health += res.get("health_score", 100)
                    scanned += 1

    avg_health = round(total_health / float(scanned), 2) if scanned else 100.0

    return {
        "status": "success",
        "scanned_files": scanned,
        "average_architecture_health": avg_health,
        "file_reports": results[:10]
    }
