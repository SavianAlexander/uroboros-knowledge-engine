"""
Semantic Query Intent Classifier & Disambiguator Engine.
Classifies queries into code_search, factual_lookup, tabular_math, analytical_summary, or comparative_analysis.
Zero-dependency, stdlib implementation.
"""

import re
from typing import Dict, Any

CODE_KEYWORDS = {"def", "function", "class", "import", "api", "struct", "code", "method", "enum", "const", "let", "var"}
MATH_KEYWORDS = {"table", "revenue", "quarter", "profit", "percent", "sum", "average", "total", "margin", "count"}
SUMMARY_KEYWORDS = {"summary", "overview", "briefing", "report", "explain", "architecture"}
COMPARE_KEYWORDS = {"vs", "versus", "compare", "difference", "contrast", "compared"}


def classify_query_intent(query: str) -> Dict[str, Any]:
    """
    Classifies user query intent and provides recommended search parameter presets.
    """
    if not query:
        return {"intent": "factual_lookup", "confidence": 1.0, "preset": {"top_k": 5, "rerank": True}, "status": "success"}

    words = set(re.findall(r'\b[a-zA-Z0-9_-]+\b', query.lower()))

    code_count = len(words.intersection(CODE_KEYWORDS))
    math_count = len(words.intersection(MATH_KEYWORDS))
    summary_count = len(words.intersection(SUMMARY_KEYWORDS))
    compare_count = len(words.intersection(COMPARE_KEYWORDS))

    if compare_count >= 1:
        intent = "comparative_analysis"
        preset = {"strategy": "subquery_table_diff", "top_k": 5, "side_by_side": True}
    elif code_count >= 1:
        intent = "code_search"
        preset = {"strategy": "cross_encoder", "top_k": 10, "entropy_chunking": True}
    elif math_count >= 1:
        intent = "tabular_math"
        preset = {"strategy": "schema_rag", "top_k": 5, "table_header_inject": True}
    elif summary_count >= 1:
        intent = "analytical_summary"
        preset = {"strategy": "parent_child", "top_k": 8, "speculative_synthesis": True}
    else:
        intent = "factual_lookup"
        preset = {"strategy": "auto_unified", "top_k": 5, "colbert_rerank": True}

    return {
        "query": query,
        "intent": intent,
        "recommended_preset": preset,
        "status": "success"
    }
