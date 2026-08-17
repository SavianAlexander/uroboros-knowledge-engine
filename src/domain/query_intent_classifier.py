"""
Semantic Query Intent Classifier & Disambiguator Engine.
Classifies queries into code_search, factual_lookup, tabular_math, analytical_summary, or comparative_analysis.
Zero-dependency, stdlib implementation.
"""
import unicodedata
import re
from typing import Dict, Any

CODE_KEYWORDS = {"def", "function", "class", "import", "api", "struct", "code", "method", "enum", "const"}
MATH_KEYWORDS = {"table", "revenue", "quarter", "profit", "percent", "sum", "average", "total", "margin", "count"}
SUMMARY_KEYWORDS = {"summary", "overview", "briefing", "report", "explain", "architecture"}
COMPARE_KEYWORDS = {"vs", "versus", "compare", "difference", "contrast", "compared"}
PATHFINDING_KEYWORDS = {"path", "connection", "relationship", "network", "connect", "links", "hop"}


def classify_query_intent(query: str) -> Dict[str, Any]:
    """
    Classifies user query intent and provides recommended search parameter presets.
    """
    if not query or not isinstance(query, str):
        return {
            "query": "",
            "intent": "factual_lookup",
            "confidence": 1.0,
            "recommended_preset": {"top_k": 5, "rerank": True},
            "recommended_pipeline": "fts5_exact_search",
            "status": "success"
        }
    norm_query = unicodedata.normalize("NFC", query)
    words = set(re.findall(r'\b[\w-]+\b', norm_query.lower()))

    code_count = len(words.intersection(CODE_KEYWORDS))
    math_count = len(words.intersection(MATH_KEYWORDS))
    summary_count = len(words.intersection(SUMMARY_KEYWORDS))
    compare_count = len(words.intersection(COMPARE_KEYWORDS))
    path_count = len(words.intersection(PATHFINDING_KEYWORDS))

    if compare_count >= 1:
        intent = "comparative_analysis"
        confidence = min(0.95, 0.70 + compare_count * 0.1)
        preset = {"strategy": "subquery_table_diff", "top_k": 5, "side_by_side": True}
        pipeline = "multi_query_decomposition"
    elif path_count >= 1:
        intent = "exploratory_pathfinding"
        confidence = min(0.95, 0.70 + path_count * 0.1)
        preset = {"strategy": "graph_bfs", "top_k": 10, "multihop": True}
        pipeline = "graph_multihop_traversal"
    elif code_count >= 1:
        intent = "code_search"
        confidence = min(0.95, 0.70 + code_count * 0.1)
        preset = {"strategy": "cross_encoder", "top_k": 10, "entropy_chunking": True}
        pipeline = "fts5_code_symbols"
    elif math_count >= 1:
        intent = "tabular_math"
        confidence = min(0.95, 0.70 + math_count * 0.1)
        preset = {"strategy": "schema_rag", "top_k": 5, "table_header_inject": True}
        pipeline = "schema_rag_extractor"
    elif summary_count >= 1:
        intent = "analytical_summary"
        confidence = min(0.95, 0.70 + summary_count * 0.1)
        preset = {"strategy": "parent_child", "top_k": 8, "speculative_synthesis": True}
        pipeline = "contextual_hyde_expansion"
    else:
        intent = "factual_lookup"
        confidence = 0.85 if len(words) <= 3 else 0.75
        preset = {"strategy": "auto_unified", "top_k": 5, "colbert_rerank": True}
        pipeline = "fts5_exact_search"

    return {
        "query": query,
        "intent": intent,
        "confidence": round(confidence, 2),
        "recommended_preset": preset,
        "recommended_pipeline": pipeline,
        "status": "success"
    }


# Backward-compatible routing alias
route_query_intent = classify_query_intent
