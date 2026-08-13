"""
Knowledge Graph Export Domain Module.
Provides zero-dependency GraphML XML serialization for Gephi, Cytoscape, and NetworkX.
"""

from typing import Dict, List, Any
import xml.etree.ElementTree as ET

def export_graph_to_graphml(graph_data: Dict[str, Any]) -> str:
    """
    Serializes Knowledge Graph nodes and edges into standard GraphML XML format.
    """
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

    for node in nodes:
        nid = str(node.get("id", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        label = str(node.get("name") or node.get("label") or nid).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        ntype = str(node.get("type", "node")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        group = str(node.get("group") or node.get("community", 0)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

        xml_lines.append(f'    <node id="{nid}">')
        xml_lines.append(f'      <data key="d0">{label}</data>')
        xml_lines.append(f'      <data key="d1">{ntype}</data>')
        xml_lines.append(f'      <data key="d2">{group}</data>')
        xml_lines.append('    </node>')

    for idx, edge in enumerate(edges, start=1):
        src = str(edge.get("source", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        target = str(edge.get("target", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        relation = str(edge.get("relation") or edge.get("type", "link")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
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
