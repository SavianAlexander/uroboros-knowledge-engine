"""
Cross-Document Entity Co-Occurrence Matrix Engine.
Builds entity co-occurrence matrices linking entities across disparate documents.
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from collections import defaultdict
from typing import Dict, Any, List

_STOP_ENTITIES = {"this", "that", "with", "from", "have", "been", "were"}
_RE_ENTITY_EXTRACT = re.compile(r'\b[A-Z][a-zA-Z0-9_-]{2,}\b')


def compute_entity_cooccurrence_matrix(
    documents: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Computes entity co-occurrence frequency pairs across documents.
    Supports proper nouns (Python, FastAPI) and acronyms (RAG, API, SQLite).
    """
    if not documents or not isinstance(documents, list):
        return {"cooccurrence_pairs": [], "total_documents_analyzed": 0, "status": "success"}

    valid_docs = [d for d in documents if isinstance(d, dict)]
    co_occurrences: Dict[str, int] = defaultdict(int)
    doc_freqs: Dict[str, int] = defaultdict(int)

    for doc in valid_docs:
        text = unicodedata.normalize("NFC", str(doc.get("content", "") or ""))
        # Heuristic entity extraction: proper nouns & uppercase acronyms
        raw_entities = set(_RE_ENTITY_EXTRACT.findall(text))
        entities = sorted([e for e in raw_entities if e.lower() not in _STOP_ENTITIES])

        for e in entities:
            doc_freqs[e] += 1

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                pair = f"{entities[i]} <-> {entities[j]}"
                co_occurrences[pair] += 1

    sorted_pairs = []
    for pair, freq in sorted(co_occurrences.items(), key=lambda x: x[1], reverse=True):
        e1, e2 = pair.split(" <-> ")
        union_count = doc_freqs.get(e1, 0) + doc_freqs.get(e2, 0) - freq
        jaccard_score = round(freq / float(max(1, union_count)), 4)
        sorted_pairs.append({
            "pair": pair,
            "entity_a": e1,
            "entity_b": e2,
            "frequency": freq,
            "jaccard_association": jaccard_score
        })

    return {
        "cooccurrence_pairs": sorted_pairs[:10],
        "total_documents_analyzed": len(valid_docs),
        "total_unique_entities": len(doc_freqs),
        "status": "success"
    }
