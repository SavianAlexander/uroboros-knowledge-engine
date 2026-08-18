"""
Sub-1ms Speculative Query Intent Router Engine.
Classifies query intent and dynamically routes execution to the optimal RAG pipeline.
Zero-dependency, stdlib implementation.
"""
import time
import unicodedata
from functools import lru_cache
from typing import Dict, Any, List, Tuple


@lru_cache(maxsize=1024)
def classify_query_intent(query: str) -> str:
    """Classifies query intent into canonical RAG pipeline categories."""
    if not query or not isinstance(query, str):
        return "hybrid_fact_retrieval"

    q_lower = unicodedata.normalize("NFC", str(query)).lower()

    if any(k in q_lower for k in ["def ", "class ", "import ", "function", "error", "bug", "traceback"]):
        return "code_search"
    elif any(k in q_lower for k in ["summary", "overview", "briefing", "report"]):
        return "executive_summary"
    elif any(k in q_lower for k in ["why", "conflict", "mismatch", "wrong", "compare"]):
        return "counterfactual_audit"
    else:
        return "hybrid_fact_retrieval"


@lru_cache(maxsize=1024)
def _route_query_intent_cached(query: str) -> Tuple[str, str]:
    intent = classify_query_intent(query)
    recommended_pipeline = {
        "code_search": "src.domain.ast_parser.parse_python_ast",
        "executive_summary": "src.domain.raptor_tree_indexer.build_raptor_tree",
        "counterfactual_audit": "src.domain.rag_engine.execute_counterfactual_rag",
        "hybrid_fact_retrieval": "src.domain.rag_engine.execute_swarm_rag"
    }.get(intent, "src.domain.rag_engine.extract_advanced_rag_context")
    return intent, recommended_pipeline


def route_query_intent(query: str) -> Dict[str, Any]:
    """
    Classifies query intent in sub-1ms and recommends the optimal RAG pipeline handler.
    # ponytail: sub-1ms speculative query intent router; ceiling: keyword/pattern rule classification; upgrade: use zero-shot intent classifier if dynamic multi-domain intent routing is added
    """
    t0 = time.perf_counter()
    intent, recommended_pipeline = _route_query_intent_cached(query)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 4)

    return {
        "status": "success",
        "query": query,
        "classified_intent": intent,
        "recommended_pipeline": recommended_pipeline,
        "routing_latency_ms": max(0.001, elapsed_ms)
    }
