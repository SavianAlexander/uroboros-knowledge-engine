import re
import json
import xml.sax.saxutils as saxutils
from typing import List, Dict, Any, Tuple, Optional, Set
from datetime import datetime, timezone

"""
Sovereign Knowledge Graph Engine & Statutory AST Deconstructor.
Features:
1. Deep Statutory AST Deconstruction (Libro -> Título -> Capítulo -> Artículo -> Sección -> Inciso)
2. GraphML & Cytoscape.js Cross-Document Knowledge Graph Exporter
3. Automated Executive Intelligence Briefing Synthesizer
"""

class StatutoryASTDeconstructor:
    """Deconstructs legal, statutory, or structured technical texts into hierarchical AST trees."""

    PATTERNS = [
        ("LIBRO", r'^(?:LIBRO\s+([IVXLCDM\d]+|PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO|OCTAVO|NOVENO|DÉCIMO))\b[.:\s-]*(.*)$'),
        ("TITULO", r'^(?:T[ÍI]TULO\s+([IVXLCDM\d]+|[A-ZÁÉÍÓÚÑ]+))\b[.:\s-]*(.*)$'),
        ("CAPITULO", r'^(?:CAP[ÍI]TULO\s+([IVXLCDM\d]+|[A-ZÁÉÍÓÚÑ]+))\b[.:\s-]*(.*)$'),
        ("SUBCAPITULO", r'^(?:SUBCAP[ÍI]TULO\s+([IVXLCDM\d]+|[A-ZÁÉÍÓÚÑ]+))\b[.:\s-]*(.*)$'),
        ("ARTICULO", r'^(?:Art[íi]culo\s+([\d\w\.\-]+))\b[.:\s-]*(.*)$'),
        ("SECCION", r'^(?:Secci[óo]n\s+([\d\w\.\-]+))\b[.:\s-]*(.*)$'),
        ("INCISO", r'^\(([a-z\d]{1,3})\)\s+(.*)$')
    ]

    @classmethod
    def deconstruct(cls, text: str, document_title: str) -> List[Dict[str, Any]]:
        """Parse raw text into hierarchical AST nodes with breadcrumbs and citation keys."""
        lines = text.split("\n")
        nodes = []
        current_hierarchy = {"DOCUMENT": document_title}
        current_content_lines = []
        current_node_type = "PREAMBLE"
        current_identifier = "0"
        current_title = document_title

        def flush_node(force: bool = False):
            nonlocal current_content_lines
            node_text = "\n".join(current_content_lines).strip()
            if node_text or force:
                path_str = " > ".join([f"{k}:{v}" for k, v in current_hierarchy.items()])
                nodes.append({
                    "node_type": current_node_type,
                    "identifier": current_identifier,
                    "title": current_title,
                    "hierarchy_path": path_str,
                    "content": node_text or current_title,
                    "char_count": len(node_text)
                })
            current_content_lines = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            matched = False
            for tag, regex in cls.PATTERNS:
                m = re.match(regex, line_str, re.I)
                if m:
                    flush_node(force=False)
                    current_node_type = tag
                    current_identifier = m.group(1).strip()
                    current_title = m.group(2).strip() if len(m.groups()) > 1 else ""
                    current_hierarchy[tag] = f"{current_identifier} {current_title}".strip()
                    
                    # For structural headings like LIBRO, TITULO, CAPITULO, record structural node immediately
                    if tag in ("LIBRO", "TITULO", "CAPITULO", "SUBCAPITULO"):
                        flush_node(force=True)

                    matched = True
                    break

            if not matched:
                current_content_lines.append(line_str)

        flush_node(force=False)
        return nodes

class KnowledgeGraphExporter:
    """Exports harvested multi-document knowledge graphs to standard GraphML and Cytoscape formats."""

    @staticmethod
    def export_graphml(documents: List[Dict[str, Any]]) -> str:
        """Generate XML GraphML representation for Gephi, Neo4j, or NetworkX."""
        nodes: Dict[str, Dict[str, str]] = {}
        edges: List[Dict[str, str]] = []

        for d in documents:
            doc_id = f"doc_{d.get('id', hash(d.get('url', '')))}"
            doc_title = d.get("title", "Document")
            nodes[doc_id] = {"label": doc_title, "type": "Document", "url": d.get("url", "")}

            # Entities as Nodes
            ent_json = d.get("entities_json", "{}")
            if isinstance(ent_json, str):
                try:
                    ent_data = json.loads(ent_json)
                except Exception:
                    ent_data = {}
            else:
                ent_data = ent_json or {}

            for ent_type, ent_list in ent_data.items():
                for e in ent_list:
                    ent_node_id = f"ent_{hash(e)}"
                    nodes[ent_node_id] = {"label": e, "type": ent_type, "url": ""}
                    edges.append({"source": doc_id, "target": ent_node_id, "relation": "mentions"})

            # Triplets as Directed Edges
            trip_json = d.get("triplets_json", "[]")
            if isinstance(trip_json, str):
                try:
                    trip_list = json.loads(trip_json)
                except Exception:
                    trip_list = []
            else:
                trip_list = trip_json or []

            for t in trip_list:
                s_id = f"ent_{hash(t['subject'])}"
                o_id = f"ent_{hash(t['object'])}"
                nodes[s_id] = {"label": t['subject'], "type": "Concept", "url": ""}
                nodes[o_id] = {"label": t['object'], "type": "Concept", "url": ""}
                edges.append({"source": s_id, "target": o_id, "relation": t['predicate']})

        # Build GraphML XML
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
        xml.append('  <key id="label" for="node" attr.name="label" attr.type="string"/>')
        xml.append('  <key id="type" for="node" attr.name="type" attr.type="string"/>')
        xml.append('  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>')
        xml.append('  <graph id="G" edgedefault="directed">')

        for n_id, n_data in nodes.items():
            esc_label = saxutils.escape(n_data["label"])
            esc_type = saxutils.escape(n_data["type"])
            xml.append(f'    <node id="{n_id}">')
            xml.append(f'      <data key="label">{esc_label}</data>')
            xml.append(f'      <data key="type">{esc_type}</data>')
            xml.append('    </node>')

        for e_idx, e in enumerate(edges):
            esc_rel = saxutils.escape(e["relation"])
            xml.append(f'    <edge id="e{e_idx}" source="{e["source"]}" target="{e["target"]}">')
            xml.append(f'      <data key="relation">{esc_rel}</data>')
            xml.append('    </edge>')

        xml.append('  </graph>')
        xml.append('</graphml>')
        return "\n".join(xml)

    @staticmethod
    def export_cytoscape_json(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Cytoscape.js compatible JSON structure."""
        elements = {"nodes": [], "edges": []}
        seen_nodes = set()

        for d in documents:
            doc_id = f"doc_{d.get('id', hash(d.get('url', '')))}"
            if doc_id not in seen_nodes:
                elements["nodes"].append({
                    "data": {"id": doc_id, "name": d.get("title", "Doc"), "type": "document"}
                })
                seen_nodes.add(doc_id)

            trip_json = d.get("triplets_json", "[]")
            trip_list = json.loads(trip_json) if isinstance(trip_json, str) else (trip_json or [])
            for t in trip_list:
                s_id = f"c_{hash(t['subject'])}"
                o_id = f"c_{hash(t['object'])}"
                if s_id not in seen_nodes:
                    elements["nodes"].append({"data": {"id": s_id, "name": t['subject'], "type": "concept"}})
                    seen_nodes.add(s_id)
                if o_id not in seen_nodes:
                    elements["nodes"].append({"data": {"id": o_id, "name": t['object'], "type": "concept"}})
                    seen_nodes.add(o_id)
                elements["edges"].append({
                    "data": {"source": s_id, "target": o_id, "label": t['predicate']}
                })

        return elements

class ExecutiveBriefingGenerator:
    """Generates comprehensive executive intelligence briefings from ingested corpora."""

    @staticmethod
    def generate_briefing(job_name: str, documents: List[Dict[str, Any]]) -> str:
        """Synthesizes key intelligence, statutory findings, and entity metrics into Markdown."""
        total_docs = len(documents)
        total_chars = sum(len(d.get("content_text", "")) for d in documents)
        all_entities = {}
        all_triplets = []

        for d in documents:
            ent = json.loads(d.get("entities_json", "{}")) if isinstance(d.get("entities_json"), str) else (d.get("entities_json") or {})
            for k, v in ent.items():
                all_entities.setdefault(k, set()).update(v)
            trip = json.loads(d.get("triplets_json", "[]")) if isinstance(d.get("triplets_json"), str) else (d.get("triplets_json") or [])
            all_triplets.extend(trip)

        md = []
        md.append(f"# Executive Intelligence Briefing: {job_name}")
        md.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | **Classification:** Sovereign Ingestion Vault\n")
        md.append("## 1. Executive Summary")
        md.append(f"- **Total Documents Ingested:** {total_docs}")
        md.append(f"- **Total Corpus Volume:** {total_chars:,} characters (~{total_chars//5:,} words)")
        md.append(f"- **Distinct Domain Entities Identified:** {sum(len(v) for v in all_entities.values())}")
        md.append(f"- **Semantic Knowledge Triplets Mapped:** {len(all_triplets)}\n")

        md.append("## 2. Key Statutory & Regulatory Findings")
        if "leyes" in all_entities and all_entities["leyes"]:
            sample_leyes = list(all_entities["leyes"])[:10]
            md.append(f"- **Referenced Statutes & Acts:** {', '.join(sample_leyes)}")
        if "agencias" in all_entities and all_entities["agencias"]:
            sample_ag = list(all_entities["agencias"])[:8]
            md.append(f"- **Key Government & Regulatory Authorities:** {', '.join(sample_ag)}")
        if "dpr_cases" in all_entities and all_entities["dpr_cases"]:
            sample_cases = list(all_entities["dpr_cases"])[:6]
            md.append(f"- **Supreme Court Jurisprudence (D.P.R.):** {', '.join(sample_cases)}")

        md.append("\n## 3. High-Priority Semantic Relationships")
        if all_triplets:
            for t in all_triplets[:8]:
                md.append(f"- `{t['subject']}` **{t['predicate']}** `{t['object']}`")
        else:
            md.append("- *No direct relationship triplets captured.*")

        md.append("\n## 4. Ingested Document Inventory")
        for idx, d in enumerate(documents[:15], start=1):
            md.append(f"{idx}. **{d.get('title', 'Document')}** — [{d.get('url', '')}]({d.get('url', '')})")

        return "\n".join(md)
