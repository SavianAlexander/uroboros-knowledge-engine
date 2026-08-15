"""
Counterfactual RAG & Multi-Scenario Stress Testing Engine.
Generates counter-hypotheses and searches the vault for refutations or edge cases before output.
Zero-dependency, stdlib implementation.
"""
import unicodedata
from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context


def execute_counterfactual_rag(query: str, max_scenarios: int = 2) -> Dict[str, Any]:
    """
    Executes Counterfactual RAG:
    1. Primary Pass -> Extract standard RAG context.
    2. Counterfactual Pass -> Generate inverse query hypotheses and retrieve edge cases.
    """
    if not query or not isinstance(query, str) or not query.strip():
        return {
            "status": "empty",
            "query": str(query or ""),
            "primary_context": "",
            "scenarios": [],
            "stress_tested": False
        }
    norm_query = unicodedata.normalize("NFC", str(query))
    formatted_ctx, primary_snippets = extract_advanced_rag_context(norm_query, max_chunks=3)
    
    counter_query = f"alternative exceptions failure modes {query}"
    _, counter_snippets = extract_advanced_rag_context(counter_query, max_chunks=2)

    scenarios = [
        {
            "scenario": "Primary Evidence",
            "snippets": [s.get("snippet", "") if isinstance(s, dict) else str(s) for s in (primary_snippets or []) if s]
        },
        {
            "scenario": "Counterfactual / Exception Scan",
            "snippets": [s.get("snippet", "") if isinstance(s, dict) else str(s) for s in (counter_snippets or []) if s]
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
    Zero-dependency stdlib implementation.
    """
    valid_ctx = [str(c) for c in (retrieved_contexts or []) if c]
    excluded_set = set(counterfactual_indices or [])
    
    active_snippets = [c for idx, c in enumerate(valid_ctx) if idx not in excluded_set]
    counterfactual_snippets = [c for idx, c in enumerate(valid_ctx) if idx in excluded_set]

    total_ctx = len(valid_ctx)
    active_cnt = len(active_snippets)

    scenarios = [
        {
            "scenario": "Active Primary Contexts",
            "snippets": active_snippets
        },
        {
            "scenario": "Simulated Exclusions / Counterfactuals",
            "snippets": counterfactual_snippets
        }
    ]

    return {
        "status": "success",
        "query": str(query or ""),
        "primary_context": "\n".join(active_snippets),
        "scenarios": scenarios,
        "provided_contexts_count": total_ctx,
        "active_context_count": active_cnt,
        "stress_tested": True
    }
