"""
Counterfactual & Scenario Boundary Analysis Engine.
Generates inverse query hypotheses and retrieves boundary exception cases across the knowledge vault.
Standard: Pure Python standard library (unicodedata, re, typing).
"""
import unicodedata
import re
from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context

# Antonym and negation mapping for counterfactual query derivation
NEGATION_MAP = {
    "increase": "decrease reduction",
    "growth": "decline contraction",
    "success": "failure vulnerability",
    "enabled": "disabled bypass",
    "active": "inactive dormant",
    "compliant": "violation penalty non-compliant",
    "secure": "insecure exploit breach",
    "safe": "risk hazard defect",
    "valid": "invalid expired void"
}


def derive_counterfactual_query(query: str) -> str:
    """Derives a contrary/boundary search query by identifying keywords and applying antonym transformations."""
    tokens = re.findall(r'\b\w+\b', query.lower())
    transformed = []
    has_transformation = False
    
    for t in tokens:
        if t in NEGATION_MAP:
            transformed.append(NEGATION_MAP[t])
            has_transformation = True
        else:
            transformed.append(t)
            
    if not has_transformation:
        return f"{query} exceptions limitations failure modes"
    return " ".join(transformed)


def execute_counterfactual_rag(query: str, max_scenarios: int = 2) -> Dict[str, Any]:
    """
    Executes multi-scenario counterfactual retrieval:
    1. Primary Pass: Standard affirmative RAG context.
    2. Counterfactual Pass: Exception and contrary boundary scan.
    """
    if not query or not isinstance(query, str) or not query.strip():
        return {
            "status": "empty",
            "query": str(query or ""),
            "primary_context": "",
            "scenarios": [],
            "stress_tested": False
        }

    norm_query = unicodedata.normalize("NFC", str(query)).strip()
    formatted_ctx, primary_snippets = extract_advanced_rag_context(norm_query, max_chunks=3)
    
    counter_query = derive_counterfactual_query(norm_query)
    _, counter_snippets = extract_advanced_rag_context(counter_query, max_chunks=2)

    scenarios = [
        {
            "scenario": "Primary Evidence",
            "query_used": norm_query,
            "snippets": [s.get("snippet", "") if isinstance(s, dict) else str(s) for s in (primary_snippets or []) if s]
        },
        {
            "scenario": "Counterfactual / Exception Scan",
            "query_used": counter_query,
            "snippets": [s.get("snippet", "") if isinstance(s, dict) else str(s) for s in (counter_snippets or []) if s]
        }
    ]

    return {
        "status": "success",
        "query": query,
        "primary_context": formatted_ctx,
        "scenarios": scenarios[:max_scenarios],
        "stress_tested": True
    }


def simulate_counterfactual_scenario(
    query: str,
    retrieved_contexts: Optional[List[str]] = None,
    counterfactual_indices: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Simulates context exclusion / ablation scenarios over candidate contexts.
    """
    valid_ctx = [str(c) for c in (retrieved_contexts or []) if c]
    excluded_set = set(counterfactual_indices or [])
    
    active_snippets = [c for idx, c in enumerate(valid_ctx) if idx not in excluded_set]
    counterfactual_snippets = [c for idx, c in enumerate(valid_ctx) if idx in excluded_set]

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
        "provided_contexts_count": len(valid_ctx),
        "active_context_count": len(active_snippets),
        "stress_tested": True
    }
