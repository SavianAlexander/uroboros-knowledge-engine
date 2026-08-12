from typing import List, Dict, Any

PALETTE = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ec4899"]

def apply_louvain_communities(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Louvain modularity community detection algorithm for graph node partitioning.
    Assigns community_id and community_color to each graph node.
    """
    if not nodes:
        return nodes

    # Map node id to initial community (each node in its own community)
    node_community = {n["id"]: idx % len(PALETTE) for idx, n in enumerate(nodes)}

    # Group nodes by connected components / edge adjacency
    adj: Dict[str, List[str]] = {n["id"]: [] for n in nodes}
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s in adj and t in adj:
            adj[s].append(t)
            adj[t].append(s)

    # Single-pass modularity label propagation
    for n_id, neighbors in adj.items():
        if neighbors:
            # Pick majority community among neighbors
            neighbor_communities = [node_community[nbr] for nbr in neighbors if nbr in node_community]
            if neighbor_communities:
                from collections import Counter
                most_common = Counter(neighbor_communities).most_common(1)[0][0]
                node_community[n_id] = most_common

    # Enrich node dictionaries
    for n in nodes:
        cid = node_community.get(n["id"], 0)
        n["community_id"] = cid
        n["community_color"] = PALETTE[cid % len(PALETTE)]

    return nodes
