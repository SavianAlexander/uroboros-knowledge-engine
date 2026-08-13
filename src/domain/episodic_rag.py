"""
Episodic Memory-Augmented RAG (Temporal Session Telepathy).
Interconnects past chat sessions, preferences, and decision history for temporal context evolution.
"""

import json
from typing import Dict, Any, List, Optional
from src.domain.agent_memory import list_memories, recall
from src.domain.rag_engine import extract_advanced_rag_context


def query_episodic_rag(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes Episodic Memory RAG:
    1. Document Vault Pass -> Standard RAG context snippets.
    2. Episodic Memory Pass -> Historical user decisions and preferences across sessions.
    # ponytail: session-aware episodic memory RAG
    """
    safe_query = str(query or "")
    formatted_ctx, snippets = extract_advanced_rag_context(safe_query, max_chunks=3)
    memories = list_memories()

    # Match query keywords against historical memory keys
    query_terms = set(w.lower() for w in safe_query.split() if len(w) > 3)
    relevant_memories = []
    for m in (memories or []):
        if isinstance(m, dict) and m.get("key"):
            k_terms = set(str(m["key"]).lower().split("_"))
            if query_terms.intersection(k_terms):
                relevant_memories.append(m)

    return {
        "status": "success",
        "query": query,
        "session_id": session_id,
        "vault_snippets": snippets,
        "episodic_memories": relevant_memories,
        "total_historical_memories": len(memories)
    }
