"""
AST Code Graph & Structural Symbol RAG Engine.
Parses Python codebases into AST trees, extracting function definitions, class structures, imports, and call graphs.
Zero-dependency, stdlib implementation (ast module).
"""

import ast
from typing import Dict, Any, List


def parse_codebase_ast(code_snippet: str) -> Dict[str, Any]:
    """
    Parses Python code into AST structure and returns symbols, classes, functions, and imports.
    """
    if not code_snippet:
        return {"symbols": [], "classes": [], "functions": [], "imports": [], "status": "empty_code"}

    try:
        tree = ast.parse(code_snippet)
    except Exception as e:
        return {"symbols": [], "error": str(e), "status": "ast_parse_error"}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "lineno": node.lineno,
                "args": [arg.arg for arg in node.args.args]
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "lineno": node.lineno,
                "bases": [b.id for b in node.bases if isinstance(b, ast.Name)]
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {
        "functions": functions,
        "classes": classes,
        "imports": list(set(imports)),
        "total_symbols": len(functions) + len(classes),
        "status": "success"
    }
