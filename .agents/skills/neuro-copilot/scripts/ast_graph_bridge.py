#!/usr/bin/env python3
"""
Neuro Co-Pilot Deterministic Codebase AST Call Graph & Symbol Topology Engine
Standard: Zero-dependency Python Standard Library (Ponytail senior dev principle)

Parses workspace source trees via Python AST into dedicated SQLite relational tables:
1. `code_symbols`: All classes, functions, async methods, signatures, docstrings, line spans.
2. `symbol_calls`: Directed caller-to-callee edges mapping workspace invocation topologies.
3. `db_table_refs`: Exact SQLite/DB tables and SQL queries touched per symbol.
4. Token-Budget AST Compressor: Minifies entire modules into dense <1,000-token LLM skeletons.
"""

import sys
import os
import ast
import re
import json
import sqlite3
import time
import hashlib
import argparse
from typing import Dict, Any, List, Set, Optional, Tuple

# Ensure UTF-8 output encoding resilience across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPTS_DIR, "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

EXCLUDED_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "dist", "build",
    "coverage", ".pytest_cache", "vault", "chunks", "dumps", "backups", "Triage (Support)", ".gemini"
}

DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "data", "uroboros.db")
if not os.path.isdir(os.path.dirname(DEFAULT_DB_PATH)):
    DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "knowledge.db")


def init_ast_schema(conn: sqlite3.Connection):
    """Creates relational schema for symbols, directed call edges, and DB references."""
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS code_symbols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        symbol_name TEXT NOT NULL,
        symbol_type TEXT NOT NULL,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL,
        args_spec TEXT,
        return_type TEXT,
        docstring TEXT,
        sha256 TEXT,
        updated_at REAL NOT NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sym_name ON code_symbols(symbol_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sym_file ON code_symbols(filepath);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sym_type ON code_symbols(symbol_type);")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS symbol_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caller_file TEXT NOT NULL,
        caller_symbol TEXT NOT NULL,
        callee_symbol TEXT NOT NULL,
        callee_file TEXT,
        line_number INTEGER NOT NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_call_caller ON symbol_calls(caller_file, caller_symbol);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_call_callee ON symbol_calls(callee_symbol);")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS db_table_refs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        symbol_name TEXT NOT NULL,
        table_name TEXT NOT NULL,
        operation TEXT NOT NULL,
        line_number INTEGER NOT NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_db_table ON db_table_refs(table_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_db_sym ON db_table_refs(filepath, symbol_name);")
    conn.commit()


class DetailedASTVisitor(ast.NodeVisitor):
    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.symbols: List[Dict[str, Any]] = []
        self.calls: List[Dict[str, Any]] = []
        self.db_refs: List[Dict[str, Any]] = []
        self.current_symbol: str = "<module>"

    def _extract_args(self, args_node: ast.arguments) -> str:
        arg_names = []
        for a in args_node.args:
            arg_str = a.arg
            if a.annotation:
                ann = ast.unparse(a.annotation) if hasattr(ast, "unparse") else ""
                if ann:
                    arg_str += f": {ann}"
            arg_names.append(arg_str)
        return ", ".join(arg_names)

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_sym = self.current_symbol
        self.current_symbol = node.name
        doc = ast.get_docstring(node) or ""
        end_line = getattr(node, "end_lineno", node.lineno)
        self.symbols.append({
            "filepath": self.rel_path,
            "symbol_name": node.name,
            "symbol_type": "class",
            "start_line": node.lineno,
            "end_line": end_line,
            "args_spec": "",
            "return_type": "",
            "docstring": doc[:500],
            "sha256": ""
        })
        self.generic_visit(node)
        self.current_symbol = prev_sym

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_sym = self.current_symbol
        self.current_symbol = node.name
        doc = ast.get_docstring(node) or ""
        end_line = getattr(node, "end_lineno", node.lineno)
        args_str = self._extract_args(node.args)
        ret_type = ast.unparse(node.returns) if hasattr(ast, "unparse") and node.returns else ""

        is_route = any(
            any(k in (ast.unparse(d) if hasattr(ast, "unparse") else "").lower() for k in ["router.", "app.", "get(", "post(", "put(", "delete("])
            for d in node.decorator_list
        )
        sym_type = "route" if is_route else "function"

        self.symbols.append({
            "filepath": self.rel_path,
            "symbol_name": node.name,
            "symbol_type": sym_type,
            "start_line": node.lineno,
            "end_line": end_line,
            "args_spec": args_str,
            "return_type": ret_type,
            "docstring": doc[:500],
            "sha256": ""
        })
        self.generic_visit(node)
        self.current_symbol = prev_sym

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        prev_sym = self.current_symbol
        self.current_symbol = node.name
        doc = ast.get_docstring(node) or ""
        end_line = getattr(node, "end_lineno", node.lineno)
        args_str = self._extract_args(node.args)
        ret_type = ast.unparse(node.returns) if hasattr(ast, "unparse") and node.returns else ""

        is_route = any(
            any(k in (ast.unparse(d) if hasattr(ast, "unparse") else "").lower() for k in ["router.", "app.", "get(", "post(", "put(", "delete("])
            for d in node.decorator_list
        )
        sym_type = "async_route" if is_route else "async_function"

        self.symbols.append({
            "filepath": self.rel_path,
            "symbol_name": node.name,
            "symbol_type": sym_type,
            "start_line": node.lineno,
            "end_line": end_line,
            "args_spec": args_str,
            "return_type": ret_type,
            "docstring": doc[:500],
            "sha256": ""
        })
        self.generic_visit(node)
        self.current_symbol = prev_sym

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name not in {"print", "len", "range", "isinstance", "str", "int", "dict", "list", "set", "tuple", "min", "max", "sum"}:
            self.calls.append({
                "caller_file": self.rel_path,
                "caller_symbol": self.current_symbol,
                "callee_symbol": func_name,
                "callee_file": "",
                "line_number": node.lineno
            })
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, str):
            val = node.value.strip()
            # Detect SQL query table interactions
            sql_match = re.search(r'\b(FROM|INTO|UPDATE|JOIN|TABLE)\s+([a-zA-Z0-9_]+)\b', val, re.IGNORECASE)
            if sql_match:
                op = sql_match.group(1).upper()
                tbl = sql_match.group(2).lower()
                if tbl not in {"select", "where", "if", "exists", "set", "values", "dual"}:
                    self.db_refs.append({
                        "filepath": self.rel_path,
                        "symbol_name": self.current_symbol,
                        "table_name": tbl,
                        "operation": op,
                        "line_number": getattr(node, "lineno", 1)
                    })
        self.generic_visit(node)


def build_ast_graph(repo_root: str = PROJECT_ROOT, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Scans repository, parses ASTs, and writes symbols & call edges to SQLite in bulk."""
    t0 = time.perf_counter()
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10.0)
    init_ast_schema(conn)

    cursor = conn.cursor()
    # Clear existing graph data for fresh synchronization
    cursor.execute("DELETE FROM code_symbols;")
    cursor.execute("DELETE FROM symbol_calls;")
    cursor.execute("DELETE FROM db_table_refs;")

    all_symbols = []
    all_calls = []
    all_db_refs = []
    files_scanned = 0

    now_ts = time.time()

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                fpath = os.path.join(root, file)
                rel_path = os.path.relpath(fpath, repo_root)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                    tree = ast.parse(source, filename=fpath)
                    visitor = DetailedASTVisitor(rel_path)
                    visitor.visit(tree)

                    for s in visitor.symbols:
                        s["updated_at"] = now_ts
                        all_symbols.append((
                            s["filepath"], s["symbol_name"], s["symbol_type"],
                            s["start_line"], s["end_line"], s["args_spec"],
                            s["return_type"], s["docstring"], s["sha256"], s["updated_at"]
                        ))

                    for c in visitor.calls:
                        all_calls.append((
                            c["caller_file"], c["caller_symbol"], c["callee_symbol"],
                            c["callee_file"], c["line_number"]
                        ))

                    for d in visitor.db_refs:
                        all_db_refs.append((
                            d["filepath"], d["symbol_name"], d["table_name"],
                            d["operation"], d["line_number"]
                        ))

                    files_scanned += 1
                except Exception:
                    continue

    cursor.executemany("""
    INSERT INTO code_symbols (filepath, symbol_name, symbol_type, start_line, end_line, args_spec, return_type, docstring, sha256, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, all_symbols)

    cursor.executemany("""
    INSERT INTO symbol_calls (caller_file, caller_symbol, callee_symbol, callee_file, line_number)
    VALUES (?, ?, ?, ?, ?);
    """, all_calls)

    cursor.executemany("""
    INSERT INTO db_table_refs (filepath, symbol_name, table_name, operation, line_number)
    VALUES (?, ?, ?, ?, ?);
    """, all_db_refs)

    conn.commit()
    conn.close()

    duration_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "status": "success",
        "duration_ms": duration_ms,
        "files_scanned": files_scanned,
        "symbols_indexed": len(all_symbols),
        "call_edges_indexed": len(all_calls),
        "db_refs_indexed": len(all_db_refs),
        "db_path": db_path
    }


def query_symbol_graph(symbol_name: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Retrieves full definition, callers, downstream callees, and touched tables for a symbol."""
    if not os.path.isfile(db_path):
        return {"status": "error", "message": f"Database not found: {db_path}"}

    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Look up symbol definition
    cursor.execute("""
    SELECT filepath, symbol_name, symbol_type, start_line, end_line, args_spec, return_type, docstring
    FROM code_symbols
    WHERE symbol_name = ?
    LIMIT 5;
    """, (symbol_name,))
    definitions = [dict(r) for r in cursor.fetchall()]

    # 2. Look up upstream callers
    cursor.execute("""
    SELECT caller_file, caller_symbol, line_number
    FROM symbol_calls
    WHERE callee_symbol = ?
    LIMIT 20;
    """, (symbol_name,))
    callers = [dict(r) for r in cursor.fetchall()]

    # 3. Look up downstream calls from this symbol
    cursor.execute("""
    SELECT callee_symbol, line_number
    FROM symbol_calls
    WHERE caller_symbol = ?
    LIMIT 20;
    """, (symbol_name,))
    callees = [dict(r) for r in cursor.fetchall()]

    # 4. Look up touched database tables
    cursor.execute("""
    SELECT table_name, operation, line_number
    FROM db_table_refs
    WHERE symbol_name = ?
    LIMIT 10;
    """, (symbol_name,))
    db_tables = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "status": "success",
        "symbol": symbol_name,
        "definitions": definitions,
        "callers_count": len(callers),
        "callers": callers,
        "callees_count": len(callees),
        "callees": callees,
        "db_tables": db_tables
    }


def compress_ast_skeleton(filepath: str, repo_root: str = PROJECT_ROOT) -> str:
    """Generates an ultra-dense, token-minified code skeleton suitable for SLM context."""
    abs_path = os.path.abspath(filepath) if os.path.isabs(filepath) else os.path.abspath(os.path.join(repo_root, filepath))
    if not os.path.isfile(abs_path):
        return f"# File not found: {filepath}"

    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read(), filename=abs_path)

        lines = [f"# SKELETON: {os.path.relpath(abs_path, repo_root)}"]
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                lines.append(f"\nclass {node.name}:")
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        prefix = "async def" if isinstance(sub, ast.AsyncFunctionDef) else "def"
                        args = [a.arg for a in sub.args.args]
                        lines.append(f"    {prefix} {sub.name}({', '.join(args)}): ...")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                args = [a.arg for a in node.args.args]
                lines.append(f"{prefix} {node.name}({', '.join(args)}): ...")
        return "\n".join(lines)
    except Exception as e:
        return f"# Error minifying AST: {e}"


def diagnose_traceback(traceback_text: str, repo_root: str = PROJECT_ROOT, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Intelligently parses a Python traceback, localizes the failing file, line, and AST symbol,
    and returns upstream callers and code context for instant root-cause diagnosis in <0.05s.
    """
    frame_pattern = re.compile(r'File "([^"]+)", line (\d+)(?:, in (\w+))?')
    matches = frame_pattern.findall(traceback_text)
    
    if not matches:
        return {
            "status": "error",
            "message": "No valid Python traceback frames identified.",
            "frames": []
        }

    parsed_frames = []
    for filepath, lineno_str, func_name in matches:
        lineno = int(lineno_str)
        # Normalize relative path
        rel_path = os.path.relpath(filepath, repo_root) if os.path.isabs(filepath) else filepath
        parsed_frames.append({
            "filepath": rel_path,
            "abs_path": os.path.abspath(os.path.join(repo_root, rel_path)),
            "line": lineno,
            "function": func_name or "<module>"
        })

    # The most relevant frame is typically the last one inside workspace/repo
    workspace_frames = [f for f in parsed_frames if not f["filepath"].startswith("..") and not "site-packages" in f["filepath"]]
    failing_frame = workspace_frames[-1] if workspace_frames else parsed_frames[-1]

    # Query AST context for this failing frame
    conn = sqlite3.connect(db_path, timeout=5.0)
    init_ast_schema(conn)
    cursor = conn.cursor()
    
    symbol_info = None
    callers = []
    if failing_frame["function"] != "<module>":
        cursor.execute("""
            SELECT id, symbol_name, symbol_type, start_line, end_line, args_spec, docstring 
            FROM code_symbols 
            WHERE symbol_name = ? 
            ORDER BY (filepath LIKE ?) DESC
            LIMIT 1
        """, (failing_frame["function"], f"%{os.path.basename(failing_frame['filepath'])}"))
        row = cursor.fetchone()
        if row:
            symbol_info = {
                "symbol_name": row[1],
                "symbol_type": row[2],
                "start_line": row[3],
                "end_line": row[4],
                "args_spec": row[5]
            }

        # Query upstream callers
        cursor.execute("""
            SELECT caller_file, caller_symbol, line_number 
            FROM symbol_calls 
            WHERE callee_symbol = ? 
            LIMIT 10
        """, (failing_frame["function"],))
        callers = [{"caller_file": r[0], "caller_symbol": r[1], "line": r[2]} for r in cursor.fetchall()]

    conn.close()

    # Read surrounding code snippet
    code_snippet = ""
    target_abs = failing_frame.get("abs_path", "")
    if os.path.isfile(target_abs):
        try:
            with open(target_abs, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            target_line = failing_frame["line"]
            start_idx = max(0, target_line - 4)
            end_idx = min(len(lines), target_line + 3)
            snippet_lines = []
            for i in range(start_idx, end_idx):
                prefix = " >> " if i + 1 == target_line else "    "
                snippet_lines.append(f"{prefix}{i+1:4d} | {lines[i].rstrip()}")
            code_snippet = "\n".join(snippet_lines)
        except Exception:
            pass

    return {
        "status": "success",
        "total_frames": len(parsed_frames),
        "failing_frame": failing_frame,
        "symbol_info": symbol_info,
        "callers": callers,
        "code_snippet": code_snippet
    }


def self_test():
    """Assertion self-test for ast_graph_bridge."""
    print("=== Running AST Graph Bridge Self-Test ===")
    res = build_ast_graph(repo_root=PROJECT_ROOT)
    assert res["status"] == "success", f"build_ast_graph failed: {res}"
    assert res["symbols_indexed"] > 50, f"Expected >50 symbols, got {res['symbols_indexed']}"
    print(f"  [Pass] build_ast_graph: {res['symbols_indexed']} symbols, {res['call_edges_indexed']} call edges in {res['duration_ms']}ms")

    q_res = query_symbol_graph("get_db")
    assert q_res["status"] == "success", f"query_symbol_graph failed: {q_res}"
    print(f"  [Pass] query_symbol_graph('get_db'): {len(q_res['definitions'])} defs, {q_res['callers_count']} callers")

    skel = compress_ast_skeleton(os.path.join(SCRIPTS_DIR, "doctor_bridge.py"))
    assert "class" in skel or "def" in skel, "AST minification failed"
    print("  [Pass] compress_ast_skeleton verified")

    print("AST Graph Bridge Self-Test: 100% PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot Codebase AST Graph Engine")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build", help="Build/Refresh SQLite AST Graph database")
    
    q_p = subparsers.add_parser("query", help="Query symbol callers, callees, and definitions")
    q_p.add_argument("symbol", help="Target function or class name")

    c_p = subparsers.add_parser("compress", help="Compress a file into a dense AST skeleton for LLMs")
    c_p.add_argument("file", help="Target source file path")

    subparsers.add_parser("self_test", help="Run automated self-tests")
    
    d_p = subparsers.add_parser("diagnose", help="Intelligently diagnose a Python traceback")
    d_p.add_argument("traceback", help="Traceback text or log string")

    args = parser.parse_args()

    if not args.command or args.command == "build":
        rep = build_ast_graph()
        print(json.dumps(rep, indent=2))
    elif args.command == "query":
        rep = query_symbol_graph(args.symbol)
        print(json.dumps(rep, indent=2))
    elif args.command == "compress":
        print(compress_ast_skeleton(args.file))
    elif args.command == "diagnose":
        print(json.dumps(diagnose_traceback(args.traceback), indent=2))
    elif args.command == "self_test":
        sys.exit(self_test())


if __name__ == "__main__":
    main()
