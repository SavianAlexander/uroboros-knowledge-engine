"""
Structured Tabular Schema RAG Extractor Engine.
Parses Markdown/CSV/JSON tables and injects column headers into individual row representations for lossless tabular vector indexing.
Zero-dependency, stdlib implementation.
"""

from typing import List, Dict, Any


def extract_tabular_schema_chunks(table_text: str) -> List[Dict[str, Any]]:
    """
    Extracts tabular chunks from a Markdown table string, injecting header schema into each row.
    """
    import unicodedata
    norm_table = unicodedata.normalize("NFC", table_text)
    lines = [line.strip() for line in norm_table.strip().split("\n") if line.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
    
    if len(table_lines) < 2:
        return [{"row_index": 0, "content": table_text, "headers": []}]

    headers = [col.strip() for col in table_lines[0].split("|")[1:-1]]
    data_lines = [l for l in table_lines[1:] if "---" not in l]

    chunks = []
    for idx, line in enumerate(data_lines):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        row_pairs = []
        for h, v in zip(headers, cols):
            row_pairs.append(f"{h}: {v}")
        
        row_representation = f"Table Row [{', '.join(row_pairs)}]"
        chunks.append({
            "row_index": idx,
            "content": row_representation,
            "headers": headers,
            "raw_line": line
        })

    return chunks
