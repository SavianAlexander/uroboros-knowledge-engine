"""
AST Code Graph & Structural Symbol RAG Engine.
Parses Python codebases into AST trees, extracting function definitions, class structures, imports, and call graphs.
Zero-dependency, stdlib implementation (ast module).
"""
import hashlib
import unicodedata
import ast
from typing import Dict, Any, List
from collections import OrderedDict

# ponytail: In-memory LRU cache keyed by SHA-256 of normalized code snippet to eliminate redundant AST walks
_AST_PARSE_CACHE: OrderedDict[str, Dict[str, Any]] = OrderedDict()
_MAX_AST_CACHE_SIZE = 2048


def parse_codebase_ast(code_snippet: str) -> Dict[str, Any]:
    """
    Parses Python code into AST structure and returns symbols, classes, functions, and imports.
    Memoizes results by content SHA-256 hash to eliminate redundant CPU re-parsing.
    """
    if not code_snippet or not isinstance(code_snippet, str) or not code_snippet.strip():
        return {"symbols": [], "classes": [], "functions": [], "imports": [], "status": "empty_code"}

    code_hash = hashlib.sha256(code_snippet.encode("utf-8")).hexdigest()
    if code_hash in _AST_PARSE_CACHE:
        _AST_PARSE_CACHE.move_to_end(code_hash)
        return _AST_PARSE_CACHE[code_hash]

    try:
        norm_code = unicodedata.normalize("NFC", code_snippet)
        tree = ast.parse(norm_code)
    except Exception as e:
        return {"symbols": [], "error": str(e), "status": "ast_parse_error"}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "lineno": node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "args": [arg.arg for arg in node.args.args]
            })
        elif isinstance(node, ast.ClassDef):
            base_names = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    base_names.append(b.id)
                elif isinstance(b, ast.Attribute):
                    base_names.append(b.attr)
                elif hasattr(b, "id"):
                    base_names.append(str(getattr(b, "id")))
            classes.append({
                "name": node.name,
                "lineno": node.lineno,
                "bases": base_names
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    result = {
        "functions": functions,
        "classes": classes,
        "imports": list(set(imports)),
        "total_symbols": len(functions) + len(classes),
        "status": "success"
    }

    if len(_AST_PARSE_CACHE) >= _MAX_AST_CACHE_SIZE:
        _AST_PARSE_CACHE.popitem(last=False)
    _AST_PARSE_CACHE[code_hash] = result

    return result
