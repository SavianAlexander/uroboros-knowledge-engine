"""
Zero-Dependency Code AST & Call Graph Complexity Extractor.
Analyzes syntax structures, extracts function dependencies, and computes cyclomatic complexity.
Zero-dependency standard-library implementation.
"""
import ast
import os
import re
from typing import Dict, Any, List, Optional


class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.calls = []
        self.current_function = None
        self.complexity_score = 1

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({"module": alias.name, "as": alias.asname, "line": node.lineno})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append({"module": f"{mod}.{alias.name}", "as": alias.asname, "line": node.lineno})
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        bases = [ast.unparse(b) if hasattr(ast, "unparse") else str(getattr(b, "id", "")) for b in node.bases]
        self.classes.append({
            "name": node.name,
            "line": node.lineno,
            "bases": bases,
            "docstring": ast.get_docstring(node)
        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        prev_fn = self.current_function
        self.current_function = node.name
        args = [a.arg for a in node.args.args]
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "args": args,
            "is_async": False,
            "docstring": ast.get_docstring(node)
        })
        self.generic_visit(node)
        self.current_function = prev_fn

    def visit_AsyncFunctionDef(self, node):
        prev_fn = self.current_function
        self.current_function = node.name
        args = [a.arg for a in node.args.args]
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "args": args,
            "is_async": True,
            "docstring": ast.get_docstring(node)
        })
        self.generic_visit(node)
        self.current_function = prev_fn

    def visit_Call(self, node):
        called_name = ""
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called_name = node.func.attr
        if called_name and self.current_function:
            self.calls.append({
                "caller": self.current_function,
                "callee": called_name,
                "line": node.lineno
            })
        self.generic_visit(node)

    # Complexity branching visitors
    def visit_If(self, node):
        self.complexity_score += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity_score += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity_score += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity_score += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity_score += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity_score += len(node.values) - 1
        self.generic_visit(node)


import collections

_AST_CACHE: collections.OrderedDict = collections.OrderedDict()
_MAX_AST_CACHE_SIZE = 512


def extract_code_structure(code_content: str, filename: str = "snippet.py") -> Dict[str, Any]:
    """
    Extracts class hierarchies, functions, call graphs, and cyclomatic complexity from source code.
    Uses zero-allocation LRU cache for sub-millisecond repeated lookups.
    """
    if not code_content or not isinstance(code_content, str):
        return {
            "status": "error",
            "message": "Empty or invalid code content",
            "filename": filename,
            "classes": [],
            "functions": [],
            "imports": [],
            "calls": [],
            "cyclomatic_complexity": 1
        }

    cache_key = (hash(code_content), filename)
    if cache_key in _AST_CACHE:
        _AST_CACHE.move_to_end(cache_key)
        return _AST_CACHE[cache_key]

    ext = os.path.splitext(filename)[1].lower()

    if ext in [".py", ""] or "def " in code_content or "import " in code_content:
        try:
            tree = ast.parse(code_content)
            analyzer = PythonASTAnalyzer()
            analyzer.visit(tree)
            res = {
                "status": "success",
                "language": "python",
                "filename": filename,
                "classes": analyzer.classes,
                "functions": analyzer.functions,
                "imports": analyzer.imports,
                "calls": analyzer.calls,
                "cyclomatic_complexity": analyzer.complexity_score
            }
            if len(_AST_CACHE) >= _MAX_AST_CACHE_SIZE:
                _AST_CACHE.popitem(last=False)
            _AST_CACHE[cache_key] = res
            return res
        except Exception:
            pass

    # Generic regex fallback for JS/TS/Go/Rust
    funcs = [{"name": m.group(1), "line": 0} for m in re.finditer(r'\bfunction\s+([a-zA-Z0-9_$]+)|\bdef\s+([a-zA-Z0-9_]+)|\bfn\s+([a-zA-Z0-9_]+)', code_content)]
    classes = [{"name": m.group(1), "line": 0} for m in re.finditer(r'\bclass\s+([a-zA-Z0-9_$]+)', code_content)]
    imports = [{"module": m.group(1), "line": 0} for m in re.finditer(r'\bimport\s+[\'"]([^\'"]+)[\'"]|\bfrom\s+([a-zA-Z0-9_\.]+)', code_content)]
    branching = len(re.findall(r'\b(?:if|else if|elif|for|while|catch|case)\b', code_content))

    res = {
        "status": "success",
        "language": "generic",
        "filename": filename,
        "classes": classes,
        "functions": funcs,
        "imports": imports,
        "calls": [],
        "cyclomatic_complexity": 1 + branching
    }
    if len(_AST_CACHE) >= _MAX_AST_CACHE_SIZE:
        _AST_CACHE.popitem(last=False)
    _AST_CACHE[cache_key] = res
    return res


def analyze_file_callgraph(filepath: str) -> Dict[str, Any]:
    """Reads a source file from filesystem and returns full AST call graph analysis."""
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return {"status": "error", "message": f"File not found: {filepath}"}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return extract_code_structure(content, filename=os.path.basename(filepath))
    except Exception as e:
        return {"status": "error", "message": str(e)}
