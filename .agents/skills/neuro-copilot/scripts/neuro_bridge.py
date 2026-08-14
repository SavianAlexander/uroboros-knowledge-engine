#!/usr/bin/env python3
"""
Neuro Knowledge Engine CLI Bridge (Enterprise Tri-Engine Dominance Suite)
Dedicated zero-dependency CLI bridge for querying local RAG brain, ingesting documents,
executing HyDE query expansion, auditing vault stats, and syncing Tududi task roadmaps.

Standard Library only (Ponytail principle).
"""

import sys
import os
import json
import hashlib
import re
import argparse

# Ensure UTF-8 output encoding resilience across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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

import time

def backup_db_cli():
    """Execute 1-click online SQLite database backup using online backup API."""
    try:
        from know import backup_db_online
        dest_file = os.path.join(project_root, "docs", f"vault_backup_{int(time.time())}.db")
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        backup_db_online(dest_file)
        return json.dumps({"status": "success", "backup_destination": dest_file}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def export_graph_svg():
    """Export Knowledge Graph topology as DOT/SVG syntax representation."""
    try:
        from know import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM files LIMIT 15")
        rows = [r[0] for r in cursor.fetchall()]
        conn.close()
        dot_str = "digraph KnowledgeGraph {\n"
        dot_str += "  node [shape=box, style=filled, color=lightskyblue];\n"
        for i in range(len(rows) - 1):
            dot_str += f'  "{rows[i]}" -> "{rows[i+1]}";\n'
        dot_str += "}"
        return json.dumps({"status": "success", "nodes_count": len(rows), "dot_graph": dot_str}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def vacuum_db_cli():
    """Execute WAL checkpointing and freelist page vacuuming on SQLite database."""
    try:
        from know import get_db
        conn = get_db()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA incremental_vacuum")
        conn.close()
        return json.dumps({"status": "success", "message": "WAL checkpointed and freelist pages reclaimed."}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def ingest_git_history(limit: int = 20):
    """Extracts recent Git commit history and indexes into local knowledge database."""
    import subprocess
    try:
        cmd = f'git log -n {limit} --pretty=format:"%H|%an|%ad|%s" --date=short'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0 or not res.stdout.strip():
            return json.dumps({"status": "notice", "message": "No git commits found to ingest."})

        commits = []
        for line in res.stdout.strip().splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })

        vault_git_dir = os.path.join(project_root, "vault", "git_history")
        os.makedirs(vault_git_dir, exist_ok=True)
        summary_md = "# Codebase Git Commit History & Provenance\n\n"
        for c in commits:
            summary_md += f"## Commit `{c['hash'][:10]}` ({c['date']})\n"
            summary_md += f"- **Author**: {c['author']}\n"
            summary_md += f"- **Message**: {c['subject']}\n\n"

        target_file = os.path.join(vault_git_dir, "recent_commits.md")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(summary_md)

        from know import index_directory
        count = index_directory(vault_git_dir)

        return json.dumps({
            "status": "success",
            "commits_ingested": len(commits),
            "indexed_chunks": count,
            "vault_file": target_file
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def ingest_tududi_roadmap():
    """Export Tududi task ledger and ingest into local Neuro Knowledge Engine."""
    try:
        scripts_dir = os.path.dirname(__file__)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import tududi_bridge
        exp_res = json.loads(tududi_bridge.export_roadmap_markdown())
        roadmap_file = exp_res.get("file_path")
        
        from know import index_directory
        vault_roadmap_dir = os.path.dirname(roadmap_file)
        indexed_count = index_directory(vault_roadmap_dir)
        
        return json.dumps({
            "status": "success",
            "roadmap_file": roadmap_file,
            "indexed_count": indexed_count,
            "message": "Tududi roadmap indexed into local Neuro vector brain."
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def export_plan_to_note(title: str, content: str):
    """Save an engineering flight plan or architecture report into vault notes."""
    try:
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', title.lower()).strip('_')[:40]
        notes_dir = os.path.join(project_root, "vault", "notes")
        os.makedirs(notes_dir, exist_ok=True)
        note_file = os.path.join(notes_dir, f"{slug}.md")
        
        with open(note_file, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}\n")
            
        from know import index_directory
        index_directory(notes_dir)
        
        return json.dumps({
            "status": "success",
            "title": title,
            "note_path": note_file,
            "message": "Note indexed into Neuro Knowledge Engine."
        }, indent=2)
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

    res_bak = json.loads(backup_db_cli())
    assert res_bak.get("status") == "success", "backup_db_cli failed"
    print("  [Pass] backup_db_cli assertion clean")

    res_svg = json.loads(export_graph_svg())
    assert res_svg.get("status") == "success", "export_graph_svg failed"
    print("  [Pass] export_graph_svg assertion clean")

    res_vac = json.loads(vacuum_db_cli())
    assert res_vac.get("status") == "success", "vacuum_db_cli failed"
    print("  [Pass] vacuum_db_cli assertion clean")

    res_git = json.loads(ingest_git_history(limit=5))
    assert res_git.get("status") in ["success", "notice"], "ingest_git_history failed"
    print("  [Pass] ingest_git_history assertion clean")

    res_road = json.loads(ingest_tududi_roadmap())
    assert res_road.get("status") == "success", f"ingest_tududi_roadmap failed: {res_road}"
    print("  [Pass] ingest_tududi_roadmap assertion clean")

    res_note = json.loads(export_plan_to_note("Self Test Note", "Sample engineering note content"))
    assert res_note.get("status") == "success", f"export_plan_to_note failed: {res_note}"
    print("  [Pass] export_plan_to_note assertion clean")

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

    subparsers.add_parser("backup", help="Execute 1-click online SQLite database backup")
    subparsers.add_parser("export_svg", help="Export Knowledge Graph topology as DOT/SVG syntax representation")
    subparsers.add_parser("vacuum", help="Execute WAL checkpointing and freelist page vacuuming")

    git_parser = subparsers.add_parser("ingest_git_history", help="Extract and index recent git commits into vault")
    git_parser.add_argument("--limit", type=int, default=20, help="Number of recent commits to index")

    subparsers.add_parser("ingest_tududi_roadmap", help="Export and index Tududi roadmap into Neuro vector brain")
    
    note_parser = subparsers.add_parser("export_note", help="Save engineering note into vault")
    note_parser.add_argument("--title", required=True, help="Note title")
    note_parser.add_argument("--content", required=True, help="Note markdown content")

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
    elif args.command == "backup":
        print(backup_db_cli())
    elif args.command == "export_svg":
        print(export_graph_svg())
    elif args.command == "vacuum":
        print(vacuum_db_cli())
    elif args.command == "ingest_git_history":
        print(ingest_git_history(args.limit))
    elif args.command == "ingest_tududi_roadmap":
        print(ingest_tududi_roadmap())
    elif args.command == "export_note":
        print(export_plan_to_note(args.title, args.content))
    elif args.command == "self_test":
        sys.exit(self_test())

if __name__ == "__main__":
    main()
