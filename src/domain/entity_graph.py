"""
Entity Knowledge Graph & Multi-Hop Path Engine:
Constructs directional and co-occurrence graphs linking extracted entities,
documents, and technical concepts for multi-hop topological reasoning.
"""

import json
import sqlite3
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import deque, defaultdict


class EntityKnowledgeGraph:
    """
    Zero-Dependency In-Memory Relational Entity Graph with Multi-Hop Traversal.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}  # node_id -> {type, metadata}
        self.adjacency: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)  # u -> {v: {relation, weight}}

    def add_node(self, node_id: str, node_type: str = "entity", metadata: Optional[Dict[str, Any]] = None):
        """Adds or updates a node in the graph."""
        n_id = node_id.lower().strip()
        if n_id not in self.nodes:
            self.nodes[n_id] = {
                "id": n_id,
                "type": node_type,
                "metadata": metadata or {}
            }

    def add_edge(self, source: str, target: str, relationship: str = "RELATED_TO", weight: float = 1.0):
        """Adds a directional or bidirectional weighted edge between two nodes."""
        u = source.lower().strip()
        v = target.lower().strip()
        if u == v:
            return

        self.add_node(u)
        self.add_node(v)

        self.adjacency[u][v] = {
            "relationship": relationship,
            "weight": weight
        }
        # Add symmetric edge for co-occurrence / relatedness
        if relationship in ["CO_OCCURS_WITH", "RELATED_TO"]:
            self.adjacency[v][u] = {
                "relationship": relationship,
                "weight": weight
            }

    def build_from_chunks(self, chunks: List[Dict[str, Any]]):
        """Builds graph relationships from retrieved or indexed chunk list."""
        for c in chunks:
            raw_entities = c.get("entities")
            if not raw_entities and "entities_json" in c:
                try:
                    raw_entities = json.loads(c["entities_json"])
                except Exception:
                    raw_entities = []

            if not raw_entities:
                continue

            clean_entities = [str(e).lower().strip() for e in raw_entities if str(e).strip()]
            
            # Connect all entities co-occurring in the same chunk
            for i in range(len(clean_entities)):
                for j in range(i + 1, len(clean_entities)):
                    e1 = clean_entities[i]
                    e2 = clean_entities[j]
                    current_weight = self.adjacency[e1].get(e2, {}).get("weight", 0.0)
                    self.add_edge(e1, e2, relationship="CO_OCCURS_WITH", weight=current_weight + 1.0)

    def find_multi_hop_paths(self, source: str, target: str, max_depth: int = 3) -> List[List[str]]:
        """
        Finds all multi-hop paths between source and target entities up to max_depth.
        Uses BFS path finding.
        """
        src = source.lower().strip()
        dst = target.lower().strip()

        if src not in self.nodes or dst not in self.nodes:
            return []

        if src == dst:
            return [[src]]

        paths = []
        queue = deque([(src, [src])])

        while queue:
            current, path = queue.popleft()

            if len(path) > max_depth + 1:
                continue

            for neighbor in self.adjacency.get(current, {}):
                if neighbor == dst:
                    paths.append(path + [dst])
                elif neighbor not in path and len(path) <= max_depth:
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def get_neighborhood(self, entity: str, max_neighbors: int = 5) -> List[Dict[str, Any]]:
        """Returns sorted nearest neighboring entities with edge relationships."""
        e = entity.lower().strip()
        if e not in self.adjacency:
            return []

        neighbors = []
        for n, edge_data in self.adjacency[e].items():
            neighbors.append({
                "entity": n,
                "relationship": edge_data.get("relationship", "RELATED_TO"),
                "weight": edge_data.get("weight", 1.0)
            })

        neighbors.sort(key=lambda x: x["weight"], reverse=True)
        return neighbors[:max_neighbors]

    def format_topology_context(self, entities: List[str], max_neighbors: int = 4) -> str:
        """
        Renders a structured markdown block summarizing connected knowledge topology
        for inclusion in RAG context assemblies.
        """
        blocks = []
        for ent in entities:
            n_list = self.get_neighborhood(ent, max_neighbors=max_neighbors)
            if n_list:
                neighbor_str = ", ".join(f"{item['entity']} ({item['relationship']})" for item in n_list)
                blocks.append(f"- **{ent}** is topologically linked to: {neighbor_str}")

        if not blocks:
            return ""

        return "### [Graph Knowledge Topology]\n" + "\n".join(blocks)
