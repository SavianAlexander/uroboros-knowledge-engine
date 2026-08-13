"""
Zero-dependency Hypothetical Document Embeddings (HyDE) & Contextual Chunk Prefixing Engine.
Synthesizes hypothetical answer document representations to boost semantic vector recall.
"""

import re
from typing import Dict, Any, List


def generate_hypothetical_document(query: str) -> Dict[str, Any]:
    """
    Generates a structured hypothetical answer document representation for a user query.
    Zero-dependency stdlib implementation.
    """
    import unicodedata
    cleaned_query = unicodedata.normalize("NFC", query.strip())
    if not cleaned_query:
        return {"hypothetical_text": "", "keywords": [], "status": "success"}

    words = re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', cleaned_query.lower())
    title_terms = " ".join(w.capitalize() for w in words[:4])

    hypothetical_text = (
        f"Document Title: Overview of {title_terms}\n"
        f"Summary: This authoritative reference document explains {cleaned_query}. "
        f"It establishes key definitions, compliance rules, standards, and technical specifications regarding {title_terms}.\n"
        f"Key Takeaways: 1. Core principles of {title_terms}. 2. Regulatory standards and operational procedures."
    )

    return {
        "original_query": query,
        "hypothetical_title": f"Overview of {title_terms}",
        "hypothetical_text": hypothetical_text,
        "extracted_keywords": words,
        "status": "success"
    }


def format_contextual_chunk(chunk_text: str, parent_title: str, tags: List[str] = []) -> str:
    """
    Prepends parent document metadata & tags to child chunk text before vector embedding.
    """
    tag_str = ", ".join(tags) if tags else "General"
    prefix = f"[Document: {parent_title} | Tags: {tag_str}]\n"
    return prefix + chunk_text
