"""
Zero-dependency Hypothetical Document Embeddings (HyDE) & Contextual Chunk Prefixing Engine.
Synthesizes dynamic hypothetical answer document representations using local SLM neural models (qwen2.5:0.5b / deepseek-r1:1.5b)
to boost semantic vector recall.
"""
import unicodedata
import re
from typing import Dict, Any, List, Optional
from src.core.model_manager import expand_query_with_llm, get_fallback_llm


def generate_hypothetical_document(query: str, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates a dynamic hypothetical answer document representation for a user query using local SLM neural reasoning.
    Falls back gracefully to SLM query expansion if local neural chat engine is offline.
    """
    cleaned_query = unicodedata.normalize("NFC", query.strip())
    if not cleaned_query:
        return {"hypothetical_text": "", "keywords": [], "status": "success", "mode": "empty"}

    words = re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', cleaned_query.lower())
    title_terms = " ".join(w.capitalize() for w in words[:4]) or "System Architecture"

    hypothetical_text = ""
    engine_mode = "fallback_heuristic"

    # Attempt dynamic SLM generation via Ollama/Local LLM
    try:
        llm = get_fallback_llm()
        if llm and hasattr(llm, "stream_chat"):
            chosen_model = model_name or "qwen2.5:0.5b"
            prompt_msgs = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert technical and legal documentation generator. Given a search query, write a concise, "
                        "authoritative 2-3 paragraph hypothetical reference excerpt answering or addressing the query with exact "
                        "technical terminology, operational rules, and domain definitions. Do not include introductory conversational filler."
                    )
                },
                {"role": "user", "content": f"Query: {cleaned_query}"}
            ]
            chunks = list(llm.stream_chat(prompt_msgs, model_name=chosen_model, temperature=0.2, num_ctx=2048))
            hypo_slm = "".join(chunks).strip()
            if hypo_slm and len(hypo_slm) >= 20:
                hypothetical_text = hypo_slm
                engine_mode = f"neural_slm_{chosen_model}"
    except Exception:
        pass

    if not hypothetical_text:
        # Dynamic query expansion via expand_query_with_llm
        try:
            expanded_terms = expand_query_with_llm(cleaned_query)
        except Exception:
            expanded_terms = " ".join(words)

        hypothetical_text = (
            f"# Technical & Regulatory Reference: {title_terms}\n\n"
            f"## Context & Scope\n"
            f"This authoritative standard provides operative requirements, statutory definitions, and technical parameters regarding '{cleaned_query}'.\n\n"
            f"## Operative Principles & Domain Synthesis\n"
            f"Relevant specifications and related terms include: {expanded_terms}.\n"
            f"Key compliance criteria mandate verification of core state, cryptographic auditability, and deterministic decision boundaries."
        )

    return {
        "original_query": query,
        "hypothetical_title": f"Overview of {title_terms}",
        "hypothetical_text": hypothetical_text,
        "extracted_keywords": words,
        "mode": engine_mode,
        "status": "success"
    }


def format_contextual_chunk(chunk_text: str, parent_title: str, tags: List[str] = []) -> str:
    """
    Prepends parent document metadata & tags to child chunk text before vector embedding.
    """
    tag_str = ", ".join(tags) if tags else "General"
    prefix = f"[Document: {parent_title} | Tags: {tag_str}]\n"
    return prefix + chunk_text

