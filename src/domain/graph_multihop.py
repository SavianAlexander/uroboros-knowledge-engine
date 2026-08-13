"""
Zero-dependency Multi-Hop GraphRAG Traversal Engine.
Traverses k-hop wikilink & tag edges (u -> v -> w) to discover relational reasoning pathways between vault documents.
"""

import sqlite3
from collections import defaultdict, deque
from typing import Dict, Any, List, Set, Optional
from src.shared.regex import RE_WIKILINKS


def find_multihop_pathways(start_doc: str, target_doc: Optional[str] = None, max_hops: int = 3) -> Dict[str, Any]:
    """
    Executes BFS multi-hop graph traversal to discover relational reasoning pathways.
    Zero-dependency stdlib implementation.
    """
    try:
        import os
        from src.infrastructure.database import get_db_connection, init_db, DB_FILE

        if DB_FILE and os.path.dirname(DB_FILE):
            os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
        init_db()
        with get_db_connection(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, content FROM files")
            rows = cursor.fetchall()

        if not rows:
            return {"pathways": [], "status": "success"}

        node_map = {r["id"]: r["filename"] for r in rows}
        name_to_id = {r["filename"].lower(): r["id"] for r in rows}

        if not start_doc or not isinstance(start_doc, str):
            return {"pathways": [], "status": "error", "message": "Invalid or missing start_doc parameter"}

        clean_start = start_doc.lower()
        clean_target = target_doc.lower() if target_doc and isinstance(target_doc, str) else None

        start_id = name_to_id.get(clean_start)
        target_id = name_to_id.get(clean_target) if clean_target else None

        if not start_id:
            # Fuzzy match start document
            for fn_lower, fid in name_to_id.items():
                if start_doc.lower() in fn_lower:
                    start_id = fid
                    break

        if not start_id:
            return {"pathways": [], "status": "error", "message": f"Start document '{start_doc}' not found"}

        # Build adjacency graph
        adj = defaultdict(set)
        for r in rows:
            u = r["id"]
            content = r["content"] or ""
            matches = RE_WIKILINKS.findall(content)
            for m in matches:
                target_title = m.strip().lower()
                if target_title in name_to_id:
                    v = name_to_id[target_title]
                    if u != v:
                        adj[u].add(v)
                        adj[v].add(u)  # Undirected graph traversal

        # BFS Pathway Discovery
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        discovered_pathways = []

        while queue:
            curr_node, path = queue.popleft()

            if len(path) > max_hops + 1:
                continue

            if target_id and curr_node == target_id:
                pathway_names = [node_map[nid] for nid in path]
                discovered_pathways.append({
                    "hops": len(path) - 1,
                    "path_ids": path,
                    "path_filenames": pathway_names
                })
                break

            if not target_id and len(path) > 1:
                pathway_names = [node_map[nid] for nid in path]
                discovered_pathways.append({
                    "hops": len(path) - 1,
                    "path_ids": path,
                    "path_filenames": pathway_names
                })

            for neighbor in adj[curr_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return {
            "start_document": node_map[start_id],
            "target_document": node_map[target_id] if target_id and target_id in node_map else None,
            "pathways": discovered_pathways[:10],
            "total_pathways_found": len(discovered_pathways),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
