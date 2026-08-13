"""
Multi-Language AST Code-Flow Graph Parser.
Parses Abstract Syntax Trees to extract classes, functions, imports, and call-graph dependencies.
Zero-dependency, stdlib Python ast implementation.
"""

import ast
from typing import Dict, Any, List, Set, Optional


class CodeASTVisitor(ast.NodeVisitor):
    """AST visitor to extract structural code entities and dependencies."""
    def __init__(self):
        self.classes: List[str] = []
        self.functions: List[str] = []
        self.imports: List[str] = []
        self.calls: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)


def parse_python_ast(source_code: str, filename: str = "<unknown>") -> Dict[str, Any]:
    """
    Parses Python source code into structural AST entities and graph edges.
    """
    if not source_code or not isinstance(source_code, str) or not source_code.strip():
        return {"status": "empty", "classes": [], "functions": [], "imports": [], "calls": []}

    try:
        tree = ast.parse(source_code, filename=filename)
        visitor = CodeASTVisitor()
        visitor.visit(tree)

        return {
            "status": "success",
            "filename": filename,
            "classes": visitor.classes,
            "functions": visitor.functions,
            "imports": visitor.imports,
            "calls": list(set(visitor.calls)),
            "graph_edges": [
                {"source": filename, "target": cls, "type": "defines_class"} for cls in visitor.classes
            ] + [
                {"source": filename, "target": func, "type": "defines_func"} for func in visitor.functions
            ] + [
                {"source": filename, "target": imp, "type": "imports"} for imp in visitor.imports
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "filename": filename,
            "classes": [],
            "functions": [],
            "imports": [],
            "calls": []
        }
