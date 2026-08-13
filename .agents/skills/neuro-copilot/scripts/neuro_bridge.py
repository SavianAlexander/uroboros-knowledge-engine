#!/usr/bin/env python3
"""
Neuro Knowledge Engine CLI Bridge (Enterprise Tri-Engine Dominance Suite)
Dedicated zero-dependency CLI bridge for querying local RAG brain, ingesting documents,
executing HyDE query expansion, and auditing vault stats.

Standard Library only (Ponytail principle).
"""

import sys
import os
import json
import hashlib
import argparse

# Add project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

def query_brain(query_text: str, max_chunks: int = 5):
    """Query local Uroboros Knowledge Engine & RAG brain directly from CLI."""
    if not query_text:
        return json.dumps({"status": "error", "message": "Query string required"})
    try:
        from src.domain.rag_engine import extract_advanced_rag_context
        from src.core.model_manager import expand_query_with_llm
        expanded = expand_query_with_llm(query_text)
        context, citations = extract_advanced_rag_context(expanded, max_chunks=max_chunks)
        return json.dumps({
            "status": "success",
            "query": query_text,
            "expanded_query": expanded,
            "citations_count": len(citations),
            "citations": citations,
            "local_context_preview": context[:1000] if context else ""
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def ingest_path(target_path: str):
    """Ingest a file or directory into the local Neuro Knowledge Engine from CLI."""
    if not target_path or not os.path.exists(target_path):
        return json.dumps({"status": "error", "message": f"Target path '{target_path}' not found"})
    try:
        from know import index_directory
        count = index_directory(target_path)
        return json.dumps({"status": "success", "target": target_path, "indexed": count}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def get_vault_stats():
    """Retrieve vault file count, database size, and RAG status."""
    try:
        from know import db_status
        stats = db_status()
        return json.dumps({"status": "success", "vault_stats": stats}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def hyde_expand(query_text: str):
    """Generate HyDE expansion terms for a query using local LLM."""
    try:
        from src.core.model_manager import expand_query_with_llm
        exp = expand_query_with_llm(query_text)
        return json.dumps({"status": "success", "query": query_text, "expanded_query": exp}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def search_graph(entity_name: str):
    """Retrieve Knowledge Graph Wikilinks and co-occurring connections for an entity."""
    try:
        from know import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, filepath FROM files WHERE filename LIKE ? OR filepath LIKE ? LIMIT 10", (f"%{entity_name}%", f"%{entity_name}%"))
        matches = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return json.dumps({"status": "success", "entity": entity_name, "connected_files_count": len(matches), "matches": matches}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def self_test():
    """Run assert-based self-test suite for neuro_bridge.py."""
    print("=== Running Neuro Bridge Self-Test Suite ===")
    res_stats = json.loads(get_vault_stats())
    assert res_stats.get("status") in ["success", "notice"], "Vault stats query failed"
    print("  [Pass] get_vault_stats assertion clean")

    res_q = json.loads(query_brain("test query"))
    assert res_q.get("status") == "success", "query_brain failed"
    print("  [Pass] query_brain assertion clean")

    res_h = json.loads(hyde_expand("test query"))
    assert res_h.get("status") == "success", "hyde_expand failed"
    print("  [Pass] hyde_expand assertion clean")

    res_g = json.loads(search_graph("test"))
    assert res_g.get("status") == "success", "search_graph failed"
    print("  [Pass] search_graph assertion clean")
    print("Self-Test Complete: ALL ASSERTIONS PASSED (100% Success)")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Neuro Knowledge Engine CLI Bridge")
    subparsers = parser.add_subparsers(dest="command")

    q_parser = subparsers.add_parser("query", help="Query local RAG brain")
    q_parser.add_argument("--text", required=True, help="Query text string")
    q_parser.add_argument("--chunks", type=int, default=5, help="Max chunks to retrieve")

    i_parser = subparsers.add_parser("ingest", help="Ingest file or folder into vault")
    i_parser.add_argument("--path", required=True, help="Target file or directory path")

    h_parser = subparsers.add_parser("hyde_expand", help="Generate HyDE query expansion terms")
    h_parser.add_argument("--query", required=True, help="Query text string")

    g_parser = subparsers.add_parser("search_graph", help="Query Knowledge Graph Wikilinks")
    g_parser.add_argument("--entity", required=True, help="Entity name")

    subparsers.add_parser("stats", help="Get vault statistics")
    subparsers.add_parser("self_test", help="Run assertion self-tests")

    args = parser.parse_args()

    if not args.command or args.command == "stats":
        print(get_vault_stats())
    elif args.command == "query":
        print(query_brain(args.text, args.chunks))
    elif args.command == "ingest":
        print(ingest_path(args.path))
    elif args.command == "hyde_expand":
        print(hyde_expand(args.query))
    elif args.command == "search_graph":
        print(search_graph(args.entity))
    elif args.command == "self_test":
        sys.exit(self_test())

if __name__ == "__main__":
    main()
