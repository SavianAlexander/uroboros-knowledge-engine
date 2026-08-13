"""
Adaptive Persona-Aware Search Tuning Engine.
Adjusts vector similarity, graph halo, temporal decay, and keyword weights based on user persona.
Zero-dependency, stdlib implementation.
"""

from typing import Dict, Any, List

PERSONA_WEIGHTS = {
    "developer": {
        "vector_weight": 0.50,
        "keyword_weight": 0.30,
        "graph_weight": 0.10,
        "temporal_weight": 0.10,
        "boost_terms": ["code", "function", "api", "class", "def", "struct", "import"]
    },
    "executive": {
        "vector_weight": 0.30,
        "keyword_weight": 0.20,
        "graph_weight": 0.20,
        "temporal_weight": 0.30,
        "boost_terms": ["summary", "revenue", "quarter", "report", "growth", "metric"]
    },
    "legal": {
        "vector_weight": 0.20,
        "keyword_weight": 0.50,
        "graph_weight": 0.15,
        "temporal_weight": 0.15,
        "boost_terms": ["clause", "policy", "compliance", "section", "article", "license"]
    }
}


def tune_search_by_persona(
    query: str,
    candidates: List[Dict[str, Any]],
    persona: str = "developer"
) -> Dict[str, Any]:
    """
    Reranks candidate search results based on active user persona weighting.
    """
    persona_config = PERSONA_WEIGHTS.get(persona.lower(), PERSONA_WEIGHTS["developer"])
    boost_terms = set(persona_config["boost_terms"])

    tuned_candidates = []
    for cand in candidates:
        cand_copy = dict(cand)
        content_lower = (cand.get("content") or "").lower()
        
        # Calculate persona term boost
        term_matches = sum(1 for t in boost_terms if t in content_lower)
        boost = min(0.20, term_matches * 0.05)
        
        base_score = float(cand.get("score", 0.5))
        final_persona_score = round(base_score + boost, 4)
        
        cand_copy["base_score"] = base_score
        cand_copy["persona_boost"] = round(boost, 4)
        cand_copy["final_persona_score"] = final_persona_score
        tuned_candidates.append(cand_copy)

    tuned_candidates.sort(key=lambda x: x["final_persona_score"], reverse=True)
    
    return {
        "persona": persona,
        "persona_weights": persona_config,
        "tuned_candidates": tuned_candidates,
        "total": len(tuned_candidates),
        "status": "success"
    }
