"""
Cross-Document Entity Co-Occurrence Matrix Engine.
Builds entity co-occurrence matrices linking entities across disparate documents.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any, List


def compute_entity_cooccurrence_matrix(
    documents: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Computes entity co-occurrence frequency pairs across documents.
    """
    if not documents or not isinstance(documents, list):
        return {"cooccurrence_pairs": [], "total_documents_analyzed": 0, "status": "success"}

    valid_docs = [d for d in documents if isinstance(d, dict)]
    co_occurrences: Dict[str, int] = {}

    for doc in valid_docs:
        text = str(doc.get("content", "") or "")
        # Heuristic entity extraction: capitalized words
        entities = sorted(list(set(re.findall(r'\b[A-Z][a-z]{3,}\b', text))))
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                pair = f"{entities[i]} <-> {entities[j]}"
                co_occurrences[pair] = co_occurrences.get(pair, 0) + 1

    sorted_pairs = [{"pair": k, "frequency": v} for k, v in sorted(co_occurrences.items(), key=lambda x: x[1], reverse=True)]

    return {
        "cooccurrence_pairs": sorted_pairs[:10],
        "total_documents_analyzed": len(documents),
        "status": "success"
    }
