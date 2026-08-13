"""
Universal Document & Data Format Pipeline.
Standardizes disparate data inputs (JSON APIs, CSV spreadsheets, Markdown notes) into unified vector-graph chunks.
Zero-dependency, stdlib implementation.
"""

import json
import csv
from io import StringIO
from typing import Dict, Any, List


def ingest_universal_data_format(
    raw_content: str,
    format_type: str = "markdown"
) -> Dict[str, Any]:
    """
    Standardizes Markdown, CSV, or JSON into unified vector chunk payloads.
    """
    chunks = []
    
    if format_type.lower() == "csv":
        f = StringIO(raw_content)
        reader = csv.reader(f)
        headers = next(reader, [])
        for row in reader:
            chunk_str = " | ".join(f"{h}: {v}" for h, v in zip(headers, row))
            chunks.append(chunk_str)
    elif format_type.lower() == "json":
        try:
            data = json.loads(raw_content)
            if isinstance(data, list):
                for item in data:
                    chunks.append(json.dumps(item))
            else:
                chunks.append(json.dumps(data))
        except Exception:
            chunks.append(raw_content)
    else:  # markdown/text
        chunks = [c.strip() for c in raw_content.split("\n\n") if c.strip()]

    return {
        "format_type": format_type,
        "unified_chunks": chunks,
        "total_chunks": len(chunks),
        "status": "success"
    }
