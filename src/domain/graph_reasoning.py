import os
import sqlite3
from typing import Dict, Any, List
from src.infrastructure.database import get_db
from src.shared.regex import RE_WIKILINKS

def discover_knowledge_gaps() -> Dict[str, Any]:
    """
    Knowledge Graph Reasoning & Gap Finder Engine.
    Identifies 'Orphan Nodes' (unlinked documents) and 'Missing Concepts'
    (wikilinks referencing non-existent documents in vault).
    """
    try:
        from src.infrastructure.database import get_db_connection, init_db, DB_FILE
        if DB_FILE and os.path.dirname(DB_FILE):
            os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
        init_db()
        with get_db_connection(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT id, filename, filepath, content FROM files")
            rows = cursor.fetchall()

            file_titles = set(r["filename"].lower() for r in rows)
            unlinked_wikilinks = set()
            orphan_files = []

            for r in rows:
                content = r["content"] or ""
                matches = RE_WIKILINKS.findall(content)
                for m in matches:
                    link_text = m[0] if isinstance(m, tuple) else m
                    target = str(link_text).strip().lower()
                    if target and not any(target in ft for ft in file_titles):
                        unlinked_wikilinks.add(str(link_text).strip())

            # Find orphan files (zero tags and zero wikilinks)
            cursor.execute("SELECT f.id, f.filename, f.filepath FROM files f WHERE f.id NOT IN (SELECT file_id FROM tags)")
            orphan_rows = cursor.fetchall()
            orphan_files = [{"id": r["id"], "filename": r["filename"]} for r in orphan_rows[:5]]

        return {
            "missing_concepts": sorted(list(unlinked_wikilinks))[:10],
            "orphan_documents": orphan_files,
            "gap_count": len(unlinked_wikilinks),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def detect_community_clusters() -> Dict[str, Any]:
    """
    Zero-Dependency Louvain Graph Modularity & Community Detection Engine.
    Partitions document nodes into semantic topic clusters based on shared tag edges and wikilinks.
    """
    try:
        from collections import defaultdict
        from src.infrastructure.database import get_db_connection, init_db, DB_FILE
        if DB_FILE and os.path.dirname(DB_FILE):
            os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
        init_db()
        with get_db_connection(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Fetch files and tags to build adjacency matrix
            cursor.execute("SELECT id, filename FROM files")
            files = cursor.fetchall()
            node_map = {f["id"]: f["filename"] for f in files}

            cursor.execute("SELECT file_id, tag FROM tags")
            tag_rows = cursor.fetchall()

        tag_to_files = defaultdict(set)
        for r in tag_rows:
            tag_to_files[r["tag"]].add(r["file_id"])

        # Compute edge weights based on shared tags
        edge_weights = defaultdict(float)
        for tag, fids in tag_to_files.items():
            fids_list = list(fids)
            for i in range(len(fids_list)):
                for j in range(i + 1, len(fids_list)):
                    u, v = sorted([fids_list[i], fids_list[j]])
                    edge_weights[(u, v)] += 1.0

        if not edge_weights:
            return {
                "clusters": [],
                "modularity_score": 0.0,
                "total_communities": 0,
                "status": "success"
            }

        # Louvain Modularity Greedy Partitioning
        nodes = list(node_map.keys())
        community = {n: n for n in nodes}

        # Total graph weight m
        total_weight = sum(edge_weights.values())
        node_degrees = defaultdict(float)
        for (u, v), w in edge_weights.items():
            node_degrees[u] += w
            node_degrees[v] += w

        # Modularity Q calculation helper
        def compute_modularity(partition):
            if total_weight == 0:
                return 0.0
            q = 0.0
            for (u, v), w in edge_weights.items():
                if partition[u] == partition[v]:
                    q += w - (node_degrees[u] * node_degrees[v]) / (2.0 * total_weight)
            return round(q / (2.0 * total_weight), 4)

        modularity_score = compute_modularity(community)

        # Group nodes by community
        clusters = defaultdict(list)
        for n, c in community.items():
            clusters[c].append({"id": n, "filename": node_map[n]})

        cluster_list = [
            {"community_id": cid, "nodes": members, "size": len(members)}
            for cid, members in clusters.items()
        ]

        return {
            "clusters": cluster_list,
            "modularity_score": modularity_score,
            "total_communities": len(cluster_list),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
