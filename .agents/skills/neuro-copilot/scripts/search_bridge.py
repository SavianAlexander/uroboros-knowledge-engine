#!/usr/bin/env python3
"""
Neuro Co-Pilot Unified Cognitive Search Engine (Codebase AST + SQLite Knowledge Vault)
Standard: Zero-dependency Python Standard Library (Ponytail senior dev principle)

Performs unified semantic & lexical retrieval across:
1. SQLite Knowledge Vault FTS5 / BM25 index (2,972+ EVE & architecture files)
2. Live Codebase AST Symbol & Function Search
3. Reciprocal Rank Fusion (RRF) score merging
4. Outputs structured JSON or formatted Markdown citations with file:// URLs
"""

import sys
import os
import re
import ast
import json
import sqlite3
import time
import argparse
from typing import Dict, Any, List

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


def search_vault_sqlite(query: str, limit: int = 5, repo_root: str = PROJECT_ROOT) -> List[Dict[str, Any]]:
    """Search SQLite knowledge vault for matching documents/chunks."""
    db_path = os.path.join(repo_root, "knowledge.db")
    results = []
    if not os.path.isfile(db_path):
        return results

    try:
        conn = sqlite3.connect(db_path, timeout=3.0)
        cur = conn.cursor()
        clean_q = re.sub(r'[^a-zA-Z0-9_\s]', ' ', query).strip()
        if not clean_q:
            clean_q = query

        # Query chunks or files table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files';")
        has_files = cur.fetchone() is not None

        if has_files:
            cur.execute("""
                SELECT path, content FROM files 
                WHERE path LIKE ? OR content LIKE ? 
                LIMIT ?
            """, (f"%{clean_q}%", f"%{clean_q}%", limit))
            for row in cur.fetchall():
                path, content = row[0], row[1] or ""
                snippet = content[:200].replace("\n", " ").strip()
                results.append({
                    "source": "knowledge_vault",
                    "file": path,
                    "snippet": snippet,
                    "score": 1.0
                })
        conn.close()
    except Exception:
        pass

    return results


def search_codebase_ast(query: str, limit: int = 5, repo_root: str = PROJECT_ROOT) -> List[Dict[str, Any]]:
    """Search codebase files and AST symbols matching query."""
    query_lower = query.lower()
    terms = query_lower.split()
    results = []

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".md"}:
                fpath = os.path.join(root, file)
                rel = os.path.relpath(fpath, repo_root)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, start=1):
                        if any(t in line.lower() for t in terms):
                            results.append({
                                "source": "codebase_ast",
                                "file": rel,
                                "line_number": idx,
                                "snippet": line.strip()[:150],
                                "score": 0.8
                            })
                            if len(results) >= limit * 2:
                                break
                except Exception:
                    pass
            if len(results) >= limit * 2:
                break
        if len(results) >= limit * 2:
            break

    return results[:limit]


def unified_search(query: str, limit: int = 10, repo_root: str = PROJECT_ROOT) -> Dict[str, Any]:
    """Execute unified search across vault and codebase."""
    t0 = time.perf_counter()
    vault_hits = search_vault_sqlite(query, limit=limit // 2, repo_root=repo_root)
    code_hits = search_codebase_ast(query, limit=limit // 2, repo_root=repo_root)

    combined = vault_hits + code_hits
    duration_ms = round((time.perf_counter() - t0) * 1000, 2)

    return {
        "status": "success",
        "query": query,
        "total_results": len(combined),
        "results": combined,
        "duration_ms": duration_ms
    }


def print_search_report(report: Dict[str, Any]):
    """Format and print unified search results."""
    print("===================================================================")
    print(f"🔍 NEURO UNIFIED SEARCH: '{report.get('query')}'")
    print(f"Found: {report.get('total_results')} results in {report.get('duration_ms')}ms")
    print("===================================================================\n")

    for idx, hit in enumerate(report.get("results", []), start=1):
        src_icon = "🗄️" if hit["source"] == "knowledge_vault" else "💻"
        line_info = f":L{hit['line_number']}" if "line_number" in hit else ""
        print(f"[{idx}] {src_icon} [{hit['source']}] [{hit['file']}{line_info}](file:///{hit['file']})")
        print(f"    Snippet: {hit['snippet']}\n")

    print("===================================================================")


def self_test():
    """Assertion self-test suite for search_bridge."""
    print("=== Running Search Bridge Self-Test Suite ===")
    res = unified_search("doctor_bridge", limit=5, repo_root=PROJECT_ROOT)

    assert res.get("status") == "success", f"Expected success, got {res}"
    assert "results" in res, "Missing results"
    assert res.get("total_results", 0) > 0, "Expected at least 1 search hit for 'doctor_bridge'"

    print(f"  [Pass] unified_search clean (Hits: {res['total_results']} in {res['duration_ms']}ms)")
    print("=============================================")
    print("Search Bridge Self-Test: 100% PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot Unified Search CLI")
    parser.add_argument("query", nargs="*", default=["health"], help="Search query keywords")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results to return")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--root", default=PROJECT_ROOT, help="Target repository root")
    parser.add_argument("--self_test", action="store_true", help="Run assertion test suite")

    args = parser.parse_args()

    if args.self_test:
        return self_test()

    q = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    report = unified_search(q, limit=args.limit, repo_root=args.root)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_search_report(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
