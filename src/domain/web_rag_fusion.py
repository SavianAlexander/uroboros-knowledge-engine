"""
Autonomous Web & Vault Dual-Retrieval Fusion Engine.
Blends local vault snippets with real-time web search results for infinite up-to-date knowledge.
"""

from typing import Dict, Any, List, Optional
from src.domain.rag_engine import extract_advanced_rag_context
from src.domain.web_search import fetch_web_context


def execute_dual_fusion_rag(query: str, max_local_snippets: int = 3, max_web_results: int = 3) -> Dict[str, Any]:
    """
    Executes dual-retrieval fusion across local SQLite vault documents and live web search.
    # ponytail: zero-dependency stdlib fallback fusion retriever
    """
    formatted_ctx, local_snippets = extract_advanced_rag_context(query, max_chunks=max_local_snippets)

    web_results = []
    # Trigger web search if local snippets are sparse or query explicitly asks for online info
    if len(local_snippets) < 2 or "latest" in query.lower() or "news" in query.lower() or "current" in query.lower():
        try:
            web_results = fetch_web_context(query, max_results=max_web_results)
        except Exception:
            web_results = []

    merged_context = []
    sources = []

    for s in local_snippets:
        merged_context.append(f"[Local Vault - {s.get('filename', 'doc')}]: {s.get('snippet', '')}")
        sources.append({"type": "local", "title": s.get("filename", "Vault Doc"), "snippet": s.get("snippet", "")})

    for w in web_results:
        merged_context.append(f"[Web Live - {w.get('title', 'Web')}]: {w.get('snippet', '')}")
        sources.append({"type": "web", "title": w.get("title", "Web Result"), "snippet": w.get("snippet", ""), "url": w.get("link", "")})

    return {
        "status": "success",
        "query": query,
        "merged_context": "\n\n".join(merged_context),
        "total_sources": len(sources),
        "local_count": len(local_snippets),
        "web_count": len(web_results),
        "sources": sources
    }
