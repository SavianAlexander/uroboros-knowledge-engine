"""
Zero-dependency Mermaid.js Graph Diagram Generator.
Converts vault document wikilinks into valid Mermaid.js graph diagram markdown strings.
"""

import re
import sqlite3
from typing import Dict, Any, List
from src.shared.regex import RE_WIKILINKS


def generate_mermaid_graph(focus_doc: str = "", max_nodes: int = 15) -> Dict[str, Any]:
    """
    Generates Mermaid.js graph markdown syntax from vault wikilinks.
    Zero-dependency stdlib implementation.
    """
    try:
        import os
        from src.infrastructure.database import get_db_connection, init_db, DB_FILE

        init_db()
        with get_db_connection(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, content FROM files LIMIT 50")
            rows = cursor.fetchall()

        if not rows:
            return {"mermaid_code": "graph TD;\n  EmptyVault[\"No Documents Found\"]", "status": "success"}

        import unicodedata
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

        # Filter edges if focus_doc specified
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

        mermaid_code = "\n".join(lines)

        return {
            "focus_doc": focus_doc,
            "max_nodes": max_nodes,
            "edges_count": len(edges),
            "mermaid_code": mermaid_code,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
