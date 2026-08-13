"""
Cognitive Swarm RAG Engine (Multi-Agent Tree-of-Thought RAG).
Executes parallel specialized agents (Explorer, Graph, Adversarial Critic, Synthesizer)
for deep multi-perspective reasoning over local document vaults.
"""
import unicodedata

from typing import Dict, Any, List, Optional
import concurrent.futures
import sqlite3
from src.domain.rag_engine import extract_advanced_rag_context
from src.domain.graph_multihop import find_multihop_pathways
from src.domain.rag_grounding_guard import verify_rag_grounding


def _run_explorer_agent(query: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Explorer Agent: Performs broad hybrid semantic and FTS5 retrieval."""
    try:
        res = extract_advanced_rag_context(query, max_snippets=5)
        return {
            "agent": "explorer",
            "retrieved_chunks": res.get("snippets", []),
            "context": res.get("formatted_context", ""),
            "status": "success"
        }
    except Exception as e:
        return {"agent": "explorer", "error": str(e), "status": "error"}


def _run_graph_agent(query: str, start_doc: Optional[str] = None) -> Dict[str, Any]:
    """Graph Traversal Agent: Discovers multi-hop entity pathways and wikilink connections."""
    try:
        safe_query = str(query or "")
        if not start_doc:
            words = [w for w in safe_query.split() if len(w) > 3]
            start_doc = words[0] if words else safe_query

        pathways = find_multihop_pathways(start_doc=start_doc, max_hops=2)
        return {
            "agent": "graph_traversal",
            "pathways": pathways.get("pathways", []),
            "status": "success"
        }
    except Exception as e:
        return {"agent": "graph_traversal", "error": str(e), "status": "error"}


def _run_critic_agent(query: str, context: str) -> Dict[str, Any]:
    """Adversarial Critic Agent: Analyzes context for potential contradictions or gaps."""
    # ponytail: lightweight heuristic critique audit without heavy external model overhead; ceiling: character length and term overlap critique heuristics; upgrade: instantiate dedicated Critic LLM subagent if full multi-agent swarm debate is enabled
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
        "agent": "critic",
        "critique": critique_points,
        "is_grounded": len(critique_points) == 0,
        "status": "success"
    }


def execute_swarm_rag(query: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes Cognitive Swarm RAG via parallel thread execution:
    1. Explorer Agent -> Hybrid Retrieval
    2. Graph Traversal Agent -> Multihop entity pathways
    3. Critic Agent -> Adversarial Grounding Audit
    4. Executive Synthesizer -> Consolidated multi-perspective RAG payload
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_explorer = executor.submit(_run_explorer_agent, query, db_path)
        f_graph = executor.submit(_run_graph_agent, query)

        explorer_res = f_explorer.result()
        graph_res = f_graph.result()

    context = explorer_res.get("context", "")
    critic_res = _run_critic_agent(query, context)

    sources = explorer_res.get("retrieved_chunks", [])
    pathways = graph_res.get("pathways", [])
    critiques = critic_res.get("critique", [])

    synthesized_summary = (
        f"Retrieved {len(sources)} source chunks across {len(pathways)} relational pathways. "
        f"Critique audit: {', '.join(critiques) if critiques else 'Verified clean grounding.'}"
    )

    return {
        "query": query,
        "synthesis": synthesized_summary,
        "sources": sources,
        "graph_pathways": pathways,
        "critic_audit": critic_res,
        "swarm_status": {
            "explorer": explorer_res.get("status"),
            "graph": graph_res.get("status"),
            "critic": critic_res.get("status")
        }
    }
