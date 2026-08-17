"""
Zero-dependency PageRank centrality algorithm for Knowledge Graph documents.
Ranks document importance based on incoming/outgoing wikilinks and shared tag connections.
"""
import os
import sqlite3
from collections import defaultdict
from typing import Dict, Any, List
from src.shared.regex import RE_WIKILINKS


def compute_graph_pagerank(damping_factor: float = 0.85, max_iterations: int = 20, tol: float = 1e-4) -> Dict[str, Any]:
    """
    Computes global PageRank centrality score for all vault documents.
    Zero-dependency stdlib implementation.
    """
    try:
        from src.infrastructure.database import get_db_connection, DB_FILE, init_db
        nodes = []
        node_names = {}
        title_to_id = {}
        out_edges = defaultdict(set)
        in_edges = defaultdict(set)

        with get_db_connection(DB_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, filename FROM files")
                id_rows = cursor.fetchall()
            except (sqlite3.OperationalError, sqlite3.DatabaseError, NameError):
                init_db()
                cursor.execute("SELECT id, filename FROM files")
                id_rows = cursor.fetchall()

            if not id_rows:
                return {"rankings": [], "total_documents": 0, "status": "success"}

            for fid, fname in id_rows:
                nodes.append(fid)
                node_names[fid] = fname
                title_to_id[str(fname).lower()] = fid

            # Stream wikilink-containing files in memory-bounded batches
            cursor.execute("SELECT id, content FROM files WHERE content LIKE '%[[%'")
            while True:
                batch = cursor.fetchmany(250)
                if not batch:
                    break
                for u, content in batch:
                    if not content:
                        continue
                    matches = RE_WIKILINKS.findall(content)
                    for m in matches:
                        target_str = m[0] if isinstance(m, tuple) else m
                        target_title = target_str.strip().lower()
                        if target_title in title_to_id:
                            v = title_to_id[target_title]
                            if u != v:
                                out_edges[u].add(v)
                                in_edges[v].add(u)

        N = len(nodes)
        if N == 0:
            return {"rankings": [], "total_documents": 0, "status": "success"}

        # Pre-compute out-degrees and dangling node set
        out_degrees = {n: float(len(out_edges[n])) for n in nodes}
        dangling_nodes = [n for n in nodes if out_degrees[n] == 0.0]
        pagerank = {n: 1.0 / float(N) for n in nodes}

        for iteration in range(max_iterations):
            new_pagerank = {}
            diff = 0.0
            dangling_mass = sum(pagerank[d] for d in dangling_nodes)

            for u in nodes:
                rank_sum = 0.0
                for v in in_edges[u]:
                    out_deg = out_degrees[v]
                    if out_deg > 0.0:
                        rank_sum += pagerank[v] / out_deg

                new_val = (1.0 - damping_factor + damping_factor * dangling_mass) / float(N) + damping_factor * rank_sum
                diff += abs(new_val - pagerank[u])
                new_pagerank[u] = new_val

            pagerank = new_pagerank
            if diff < tol:
                break

        sorted_rankings = sorted(
            [
                {
                    "id": node_id,
                    "filename": node_names[node_id],
                    "pagerank_score": round(score, 6),
                    "inbound_links": len(in_edges[node_id]),
                    "outbound_links": len(out_edges[node_id])
                }
                for node_id, score in pagerank.items()
            ],
            key=lambda x: x["pagerank_score"],
            reverse=True
        )

        return {
            "damping_factor": damping_factor,
            "total_documents": N,
            "rankings": sorted_rankings,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
