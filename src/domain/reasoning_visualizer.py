"""
Knowledge Graph Reasoning Path Visualizer.
Generates Mermaid.js diagram markup detailing multi-hop traversal pathways across document nodes.
"""

from typing import Dict, Any, List


def generate_mermaid_reasoning_diagram(pathways: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Converts multi-hop pathway results into Mermaid.js graph markup.
    # ponytail: zero-dependency Mermaid.js graph markup generator
    """
    if not pathways:
        return {"status": "empty", "mermaid_markup": "graph TD\n  Empty[No Pathways Found]"}

    lines = ["graph LR"]
    seen_edges = set()

    import unicodedata
    for idx, path in enumerate(pathways):
        filenames = path.get("path_filenames", [])
        for i in range(len(filenames) - 1):
            src_norm = unicodedata.normalize("NFC", str(filenames[i]))
            tgt_norm = unicodedata.normalize("NFC", str(filenames[i+1]))
            src = src_norm.replace(" ", "_").replace(".", "_")
            tgt = tgt_norm.replace(" ", "_").replace(".", "_")
            edge = f"  {src} -->|Hop {i+1}| {tgt}"
            if edge not in seen_edges:
                seen_edges.add(edge)
                lines.append(edge)

    markup = "\n".join(lines)
    return {
        "status": "success",
        "total_pathways_rendered": len(pathways),
        "total_edges": len(seen_edges),
        "mermaid_markup": markup
    }
