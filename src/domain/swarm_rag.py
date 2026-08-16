"""
Concurrent Multi-Pathway Hybrid RAG Engine.
Executes parallel multi-channel retrieval (lexical FTS5, graph Wikilink pathways, and grounding verification)
for comprehensive context synthesis across local document vaults.
Standard: Pure Python standard library (concurrent.futures, unicodedata, typing).
"""
import concurrent.futures
import unicodedata
from typing import Dict, Any, List, Optional

from src.domain.rag_engine import extract_advanced_rag_context
from src.domain.graph_multihop import find_multihop_pathways
from src.domain.rag_grounding_guard import verify_rag_grounding


def _run_explorer_stage(query: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Explorer Stage: Performs broad hybrid semantic and FTS5 retrieval."""
    try:
        res = extract_advanced_rag_context(query, max_snippets=5)
        return {
            "agent": "explorer",
            "stage": "lexical_vector_retrieval",
            "retrieved_chunks": res.get("snippets", []),
            "context": res.get("formatted_context", ""),
            "status": "success"
        }
    except Exception as e:
        return {"agent": "explorer", "stage": "lexical_vector_retrieval", "error": str(e), "status": "error"}


def _run_graph_stage(query: str, start_doc: Optional[str] = None) -> Dict[str, Any]:
    """Graph Traversal Stage: Discovers multi-hop entity pathways and wikilink connections."""
    try:
        safe_query = str(query or "")
        if not start_doc:
            words = [w for w in safe_query.split() if len(w) > 3]
            start_doc = words[0] if words else safe_query

        pathways = find_multihop_pathways(start_doc=start_doc, max_hops=2)
        return {
            "agent": "graph_traversal",
            "stage": "graph_pathways",
            "pathways": pathways.get("pathways", []),
            "status": "success"
        }
    except Exception as e:
        return {"agent": "graph_traversal", "stage": "graph_pathways", "error": str(e), "status": "error"}


def _run_critique_stage(query: str, context: str) -> Dict[str, Any]:
    """Verification Stage: Analyzes context for coverage gaps and entity alignment."""
    critique_points = []
    if not context or len(context.strip()) < 20:
        critique_points.append("Insufficient context retrieved for high confidence.")
    
    safe_query = unicodedata.normalize("NFC", str(query or ""))
    safe_context = unicodedata.normalize("NFC", str(context or ""))
    query_terms = [w.lower() for w in safe_query.split() if len(w) > 3]
    missing_terms = [w for w in query_terms if w not in safe_context.lower()]
    
    if missing_terms:
        critique_points.append(f"Query terms missing from retrieved context: {', '.join(missing_terms[:3])}")

    return {
        "agent": "adversarial_critic",
        "stage": "critique",
        "critique_points": critique_points,
        "is_grounded": len(critique_points) == 0,
        "status": "success"
    }


def execute_swarm_rag(query: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes concurrent multi-pathway hybrid retrieval combining:
    1. Lexical FTS5 + vector context
    2. Multi-hop Wikilink graph pathways
    3. Grounding alignment verification
    """
    if not query or not str(query).strip():
        return {"status": "empty_query", "query": "", "synthesized_context": ""}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_explorer = executor.submit(_run_explorer_stage, query, db_path)
        f_graph = executor.submit(_run_graph_stage, query)
        
        explorer_res = f_explorer.result()
        graph_res = f_graph.result()
        
        context_text = explorer_res.get("context", "")
        f_critique = executor.submit(_run_critique_stage, query, context_text)
        critique_res = f_critique.result()

    return {
        "query": query,
        "explorer_results": explorer_res,
        "graph_pathways": graph_res.get("pathways", []),
        "critique": critique_res,
        "synthesized_context": context_text,
        "status": "success"
    }
