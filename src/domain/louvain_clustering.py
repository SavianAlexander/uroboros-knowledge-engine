from collections import Counter
from typing import List, Dict, Any

PALETTE = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ec4899"]

def apply_louvain_communities(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Community detection algorithm for graph node partitioning using multi-pass label propagation.
    Assigns community_id and community_color to each graph node.
    """
    if not nodes or not isinstance(nodes, list):
        return []

    valid_nodes = [n for n in nodes if isinstance(n, dict) and "id" in n]
    if not valid_nodes:
        return nodes

    safe_edges = edges if isinstance(edges, list) else []

    # Map node id to unique initial community
    node_community = {n["id"]: idx for idx, n in enumerate(valid_nodes)}

    # Build adjacency list
    adj: Dict[str, List[str]] = {n["id"]: [] for n in valid_nodes}
    for e in safe_edges:
        if isinstance(e, dict):
            s, t = e.get("source"), e.get("target")
            if s in adj and t in adj:
                adj[s].append(t)
                adj[t].append(s)

    # Multi-pass label propagation until convergence (max 5 iterations)
    for _ in range(5):
        changed = False
        for n_id, neighbors in adj.items():
            if neighbors:
                neighbor_communities = [node_community[nbr] for nbr in neighbors if nbr in node_community]
                if neighbor_communities:
                    most_common = Counter(neighbor_communities).most_common(1)[0][0]
                    if node_community[n_id] != most_common:
                        node_community[n_id] = most_common
                        changed = True
        if not changed:
            break

    # Normalize community IDs to compact 0-indexed integer identifiers
    unique_communities = sorted(set(node_community.values()))
    comm_map = {orig_c: new_idx for new_idx, orig_c in enumerate(unique_communities)}

    # Enrich node dictionaries
    for n in nodes:
        if isinstance(n, dict) and "id" in n:
            raw_cid = node_community.get(n["id"], 0)
            cid = comm_map.get(raw_cid, 0)
            n["community_id"] = cid
            n["community_color"] = PALETTE[cid % len(PALETTE)]

    return nodes

detect_louvain_communities = apply_louvain_communities

def synthesize_community_summaries(nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesizes executive topical summaries and key concept terms for each Louvain cluster.
    Pure stdlib implementation.
    """
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
        
        # Build intuitive cluster label
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
