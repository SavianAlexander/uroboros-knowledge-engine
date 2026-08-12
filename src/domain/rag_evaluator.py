import re
from typing import List, Dict, Any

_RE_WORDS = re.compile(r'\b[a-zA-Z0-9]{3,}\b')

def evaluate_rag_faithfulness(query: str, response: str, citations: List[Dict[str, Any]], context_text: str) -> Dict[str, Any]:
    """
    RAG Quality & Faithfulness Audit Evaluator.
    Calculates empirical Faithfulness Score, Context Precision Score, and Groundedness Ratio.
    """
    if not response or not response.strip():
        return {"faithfulness_score": 0.0, "context_precision_score": 0.0, "grounded_ratio": 0.0, "status": "empty"}

    res_words = set(w.lower() for w in _RE_WORDS.findall(response))
    ctx_words = set(w.lower() for w in _RE_WORDS.findall(context_text))

    if not res_words:
        return {"faithfulness_score": 1.0, "context_precision_score": 1.0, "grounded_ratio": 1.0, "status": "pass"}

    # Groundedness: overlap of response terms in retrieved context
    grounded_overlap = res_words.intersection(ctx_words)
    grounded_ratio = round(len(grounded_overlap) / len(res_words), 4)

    # Context Precision: signal density of citations
    num_citations = len(citations)
    precision = 1.0 if num_citations > 0 else 0.5
    if num_citations > 0:
        high_conf = sum(1 for c in citations if c.get("confidence_score", 0.0) > 0.01)
        precision = round(high_conf / num_citations, 4)

    faithfulness_score = round((grounded_ratio * 0.7) + (precision * 0.3), 4)

    return {
        "faithfulness_score": faithfulness_score,
        "context_precision_score": precision,
        "grounded_ratio": grounded_ratio,
        "status": "pass" if faithfulness_score >= 0.50 else "warning"
    }
