"""
Unified Knowledge Graph Engine.
Consolidates Multi-Hop GraphRAG Traversal, PageRank Centrality,
Louvain Modularity Clustering, Mermaid Diagram Generation, and GraphML XML Serialization.
Standard: Zero-dependency, pure Python standard library (sqlite3, collections, typing, re, xml, html).
"""

import os
import re
import html
import sqlite3
import unicodedata
from collections import defaultdict, deque, Counter
from typing import Dict, Any, List, Set, Optional, Tuple

from src.shared.regex import RE_WIKILINKS


# ==============================================================================
# 1. Multi-Hop Graph Traversal (GraphRAG Pathway Discovery)
# ==============================================================================

def find_multihop_pathways(start_doc: str, target_doc: Optional[str] = None, max_hops: int = 3) -> Dict[str, Any]:
    """
    Executes BFS multi-hop graph traversal to discover relational reasoning pathways.
    Zero-dependency stdlib implementation.
    """
    try:
        from src.infrastructure.database import get_db, init_db

        def _fetch_all_files():
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, filename, filepath, content FROM files")
                return cursor.fetchall()

        try:
            rows = _fetch_all_files()
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            init_db()
            rows = _fetch_all_files()

        if not rows:
            return {"pathways": [], "status": "success"}

        node_map = {r[0]: r[1] for r in rows}
        name_to_id = {str(r[1]).lower(): r[0] for r in rows}

        if not start_doc or not isinstance(start_doc, str):
            return {"pathways": [], "status": "error", "message": "Invalid or missing start_doc parameter"}

        clean_start = start_doc.lower()
        clean_target = target_doc.lower() if target_doc and isinstance(target_doc, str) else None

        start_id = name_to_id.get(clean_start)
        target_id = name_to_id.get(clean_target) if clean_target else None

        if not start_id:
            for fn_lower, fid in name_to_id.items():
                if start_doc.lower() in fn_lower:
                    start_id = fid
                    break

        if not start_id:
            return {"pathways": [], "status": "error", "message": f"Start document '{start_doc}' not found"}

        adj = defaultdict(set)
        for r in rows:
            u = r[0]
            content = r[3] or ""
            matches = RE_WIKILINKS.findall(content)
            for m in matches:
                target_raw = m[0] if isinstance(m, (tuple, list)) else m
                target_title = str(target_raw).strip().lower()
                if target_title in name_to_id:
                    v = name_to_id[target_title]
                    if u != v:
                        adj[u].add(v)
                        adj[v].add(u)

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


# ==============================================================================
# 2. Knowledge Graph PageRank Centrality
# ==============================================================================

def compute_graph_pagerank(damping_factor: float = 0.85, max_iterations: int = 20, tol: float = 1e-4) -> Dict[str, Any]:
    """
    Computes global PageRank centrality score for all vault documents.
    """
    try:
        from src.infrastructure.database import get_db, init_db
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, filename, filepath, content FROM files")
                rows = cursor.fetchall()
        except (sqlite3.OperationalError, sqlite3.DatabaseError, NameError):
            init_db()
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, filename, filepath, content FROM files")
                rows = cursor.fetchall()

        if not rows:
            return {"rankings": [], "total_documents": 0, "status": "success"}

        nodes = [r[0] for r in rows]
        node_names = {r[0]: r[1] for r in rows}
        title_to_id = {str(r[1]).lower(): r[0] for r in rows}
        N = len(nodes)

        out_edges = defaultdict(set)
        in_edges = defaultdict(set)

        for r in rows:
            u = r[0]
            content = r[3] or ""
            matches = RE_WIKILINKS.findall(content)
            for m in matches:
                target_str = m[0] if isinstance(m, tuple) else m
                target_title = target_str.strip().lower()
                if target_title in title_to_id:
                    v = title_to_id[target_title]
                    if u != v:
                        out_edges[u].add(v)
                        in_edges[v].add(u)

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


# ==============================================================================
# 3. Louvain Modularity Clustering & Community Summarization
# ==============================================================================

PALETTE = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ec4899"]

def apply_louvain_communities(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Louvain modularity community detection algorithm for graph node partitioning."""
    if not nodes or not isinstance(nodes, list):
        return []

    valid_nodes = [n for n in nodes if isinstance(n, dict) and "id" in n]
    if not valid_nodes:
        return nodes

    safe_edges = edges if isinstance(edges, list) else []
    node_community = {n["id"]: idx % len(PALETTE) for idx, n in enumerate(valid_nodes)}

    adj: Dict[str, List[str]] = {n["id"]: [] for n in valid_nodes}
    for e in safe_edges:
        if isinstance(e, dict):
            s, t = e.get("source"), e.get("target")
            if s in adj and t in adj:
                adj[s].append(t)
                adj[t].append(s)

    for n_id, neighbors in adj.items():
        if neighbors:
            neighbor_communities = [node_community[nbr] for nbr in neighbors if nbr in node_community]
            if neighbor_communities:
                most_common = Counter(neighbor_communities).most_common(1)[0][0]
                node_community[n_id] = most_common

    for n in nodes:
        if isinstance(n, dict) and "id" in n:
            cid = node_community.get(n["id"], 0)
            n["community_id"] = cid
            n["community_color"] = PALETTE[cid % len(PALETTE)]

    return nodes


detect_louvain_communities = apply_louvain_communities


def synthesize_community_summaries(nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synthesizes topical summaries and key concept terms for each Louvain cluster."""
    if not nodes or not isinstance(nodes, list):
        return {"status": "success", "communities": []}

    STOPWORDS = {
        "the", "and", "a", "an", "in", "on", "of", "to", "for", "is", "are", "with", "by",
        "at", "from", "as", "into", "through", "during", "including", "until", "against",
        "among", "throughout", "despite", "towards", "upon", "concerning", "to", "in", "for",
        "of", "by", "on", "with", "about", "against", "between", "into", "through", "during",
        "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on",
        "off", "over", "under", "again", "further", "then", "once", "this", "that", "these",
        "those", "md", "txt", "pdf", "py", "js", "html", "json"
    }

    groups: Dict[int, List[Dict[str, Any]]] = {}
    for n in nodes:
        if isinstance(n, dict):
            cid = n.get("community_id", 0)
            groups.setdefault(cid, []).append(n)

    summaries = []
    for cid, c_nodes in sorted(groups.items()):
        words: List[str] = []
        for n in c_nodes:
            label = str(n.get("label", n.get("id", "")))
            clean_label = "".join(c if c.isalnum() else " " for c in label).lower()
            for w in clean_label.split():
                if len(w) > 2 and w not in STOPWORDS:
                    words.append(w)

        word_counts = Counter(words)
        top_terms = [w for w, _ in word_counts.most_common(5)]
        
        if top_terms:
            cluster_name = " & ".join(t.capitalize() for t in top_terms[:2]) + " Domain"
        else:
            cluster_name = f"Cluster #{cid} Knowledge Domain"

        color = PALETTE[cid % len(PALETTE)]
        summaries.append({
            "community_id": cid,
            "community_color": color,
            "cluster_title": cluster_name,
            "node_count": len(c_nodes),
            "top_keywords": top_terms,
            "nodes": [n.get("label", n.get("id")) for n in c_nodes]
        })

    return {
        "status": "success",
        "total_communities": len(summaries),
        "communities": summaries
    }


# ==============================================================================
# 4. Mermaid.js Diagram Generation
# ==============================================================================

def generate_mermaid_graph(focus_doc: str = "", max_nodes: int = 15) -> Dict[str, Any]:
    """Generates Mermaid.js graph markdown syntax from vault wikilinks."""
    try:
        from src.infrastructure.database import get_db, init_db

        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, filename, content FROM files LIMIT 50")
                rows = cursor.fetchall()
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            init_db()
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, filename, content FROM files LIMIT 50")
                rows = cursor.fetchall()

        if not rows:
            return {"mermaid_code": "graph TD;\n  EmptyVault[\"No Documents Found\"]", "status": "success"}

        node_map = {unicodedata.normalize("NFC", str(r[1])).lower(): unicodedata.normalize("NFC", str(r[1])) for r in rows}
        edges = []

        for r in rows:
            src = str(r[1])
            content = r[2] or ""
            matches = RE_WIKILINKS.findall(content)
            for m in matches:
                target_lower = m.strip().lower()
                if target_lower in node_map:
                    tgt = node_map[target_lower]
                    if src != tgt:
                        edges.append((src, tgt))

        if focus_doc:
            clean_focus = focus_doc.lower()
            edges = [e for e in edges if clean_focus in e[0].lower() or clean_focus in e[1].lower()]

        edges = edges[:max_nodes]
        lines = ["graph TD;"]
        seen_nodes = set()

        for src, tgt in edges:
            src_id = re.sub(r'\W+', '_', src)
            tgt_id = re.sub(r'\W+', '_', tgt)
            clean_src = src.replace('"', '&quot;')
            clean_tgt = tgt.replace('"', '&quot;')

            if src_id not in seen_nodes:
                lines.append(f'  {src_id}["{clean_src}"]')
                seen_nodes.add(src_id)

            if tgt_id not in seen_nodes:
                lines.append(f'  {tgt_id}["{clean_tgt}"]')
                seen_nodes.add(tgt_id)

            lines.append(f'  {src_id} --> {tgt_id}')

        if len(lines) == 1:
            lines.append("  VaultNodes[\"Vault Graph Visualized\"]")

        return {
            "focus_doc": focus_doc,
            "max_nodes": max_nodes,
            "edges_count": len(edges),
            "mermaid_code": "\n".join(lines),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==============================================================================
# 5. GraphML XML Serialization
# ==============================================================================

def export_graph_to_graphml(graph_data: Dict[str, Any]) -> str:
    """Serializes Knowledge Graph nodes and edges into standard GraphML XML format."""
    if not graph_data or not isinstance(graph_data, dict):
        return '<?xml version="1.0" encoding="UTF-8"?><graphml></graphml>'

    raw_nodes = graph_data.get("nodes", [])
    nodes = [n for n in raw_nodes if isinstance(n, dict)] if isinstance(raw_nodes, list) else []

    raw_edges = graph_data.get("edges", [])
    edges = [e for e in raw_edges if isinstance(e, dict)] if isinstance(raw_edges, list) else []

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"',
        '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
        '  <key id="d0" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="d1" for="node" attr.name="type" attr.type="string"/>',
        '  <key id="d2" for="node" attr.name="group" attr.type="string"/>',
        '  <key id="d3" for="edge" attr.name="relation" attr.type="string"/>',
        '  <key id="d4" for="edge" attr.name="weight" attr.type="int"/>',
        '  <graph id="UroborosKnowledgeGraph" edgedefault="undirected">'
    ]

    def _esc(val: Any) -> str:
        return html.escape(str(val if val is not None else ""), quote=True)

    for node in nodes:
        nid = _esc(node.get("id", ""))
        label = _esc(node.get("name") or node.get("label") or nid)
        ntype = _esc(node.get("type", "node"))
        group = _esc(node.get("group") or node.get("community", 0))

        xml_lines.append(f'    <node id="{nid}">')
        xml_lines.append(f'      <data key="d0">{label}</data>')
        xml_lines.append(f'      <data key="d1">{ntype}</data>')
        xml_lines.append(f'      <data key="d2">{group}</data>')
        xml_lines.append('    </node>')

    for idx, edge in enumerate(edges, start=1):
        src = _esc(edge.get("source", ""))
        target = _esc(edge.get("target", ""))
        relation = _esc(edge.get("relation") or edge.get("type", "link"))
        try:
            weight = int(edge.get("weight", 1))
        except (ValueError, TypeError):
            weight = 1

        xml_lines.append(f'    <edge id="e{idx}" source="{src}" target="{target}">')
        xml_lines.append(f'      <data key="d3">{relation}</data>')
        xml_lines.append(f'      <data key="d4">{weight}</data>')
        xml_lines.append('    </edge>')

    xml_lines.append('  </graph>')
    xml_lines.append('</graphml>')

    return "\n".join(xml_lines)
