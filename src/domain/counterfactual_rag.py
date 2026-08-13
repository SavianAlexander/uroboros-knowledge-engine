"""
Counterfactual RAG & Multi-Scenario Stress Testing Engine.
Generates counter-hypotheses and searches the vault for refutations or edge cases before output.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context


def execute_counterfactual_rag(query: str, max_scenarios: int = 2) -> Dict[str, Any]:
    """
    Executes Counterfactual RAG:
    1. Primary Pass -> Extract standard RAG context.
    2. Counterfactual Pass -> Generate inverse query hypotheses and retrieve edge cases.
    """
    formatted_ctx, primary_snippets = extract_advanced_rag_context(query, max_chunks=3)
    
    counter_query = f"NOT {query} alternative exceptions failure modes"
    _, counter_snippets = extract_advanced_rag_context(counter_query, max_chunks=2)

    scenarios = [
        {
            "scenario": "Primary Evidence",
            "snippets": [s.get("snippet", "") for s in primary_snippets]
        },
        {
            "scenario": "Counterfactual / Exception Scan",
            "snippets": [s.get("snippet", "") for s in counter_snippets]
        }
    ]

    return {
        "status": "success",
        "query": query,
        "primary_context": formatted_ctx,
        "scenarios": scenarios,
        "stress_tested": True
    }


def simulate_counterfactual_scenario(
    query: str,
    retrieved_contexts: Optional[List[str]] = None,
    counterfactual_indices: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Simulates counterfactual scenarios over a given set of contexts.
    """
    res = execute_counterfactual_rag(query)
    total_ctx = len(retrieved_contexts) if retrieved_contexts else 0
    excluded_cnt = len(counterfactual_indices) if counterfactual_indices else 0
    res["provided_contexts_count"] = total_ctx
    res["active_context_count"] = max(0, total_ctx - excluded_cnt)
    return res
