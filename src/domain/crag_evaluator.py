"""
Corrective RAG (CRAG) & Self-Evaluation Module.
Classifies retrieval confidence into three states (CORRECT, AMBIGUOUS, INCORRECT)
and dynamically triggers query reformulation, secondary retrieval, or fallback.
"""

import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class CRAGState(str, Enum):
    """Three-state classification for Corrective RAG context evaluation."""
    CORRECT = "CORRECT"        # High confidence (>= 0.70): Proceed directly to generation
    AMBIGUOUS = "AMBIGUOUS"    # Partial match (0.35 - 0.69): Trigger query expansion & secondary retrieval
    INCORRECT = "INCORRECT"    # Low/zero match (< 0.35): Bypass generation, emit structured fallback


class CRAGEvaluator:
    """Evaluates retrieved context adequacy and orchestrates adaptive recovery."""

    HIGH_CONFIDENCE_THRESHOLD = 0.70
    MIN_RELEVANCE_THRESHOLD = 0.35

    @classmethod
    def evaluate_confidence(
        cls,
        candidate_chunks: List[Dict[str, Any]],
        query: str = ""
    ) -> Tuple[CRAGState, float]:
        """
        Classifies candidate context into CORRECT, AMBIGUOUS, or INCORRECT.
        Returns the classified CRAGState and the computed confidence score.
        """
        if not candidate_chunks:
            return CRAGState.INCORRECT, 0.0

        # Retrieve highest cross-encoder or hybrid score
        top_chunk = candidate_chunks[0]
        top_score = float(top_chunk.get("cross_score") or top_chunk.get("score") or 0.0)

        if top_score >= cls.HIGH_CONFIDENCE_THRESHOLD:
            return CRAGState.CORRECT, top_score
        elif top_score >= cls.MIN_RELEVANCE_THRESHOLD:
            return CRAGState.AMBIGUOUS, top_score
        else:
            return CRAGState.INCORRECT, top_score

    @classmethod
    def reformulate_query(cls, query: str, top_candidates: List[Dict[str, Any]]) -> str:
        """
        Generates a step-back / expanded search query for secondary CRAG retrieval.
        """
        from src.domain.query_transformer import AsyncQueryTransformer
        step_back = AsyncQueryTransformer.generate_step_back_query(query)
        
        # Incorporate domain terms from partial candidate matches if available
        if top_candidates:
            doc_title = top_candidates[0].get("doc_title", "")
            sec_header = top_candidates[0].get("section_header", "")
            if sec_header and sec_header.lower() not in step_back.lower():
                return f"{step_back} {sec_header}".strip()

        return step_back


async def execute_crag_retrieval_pipeline(
    query: str,
    auth_context: Optional[Any] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
    max_chunks: int = 5
) -> Dict[str, Any]:
    """
    Full End-to-End Corrective RAG (CRAG) Retrieval Orchestrator:
    1. Conversational Query Rewriter (coreference resolution)
    2. Primary Hybrid Retrieval with Multi-Tenant RBAC pre-filtering
    3. CRAG State Self-Evaluation (CORRECT / AMBIGUOUS / INCORRECT)
    4. Adaptive Secondary Retrieval Loop for AMBIGUOUS contexts
    5. Indirect Prompt Injection Defense & XML CDATA context fencing
    """
    from src.domain.query_rewriter import ConversationalQueryRewriter
    from src.domain.rag_engine import async_extract_advanced_rag_context
    from src.domain.context_optimizer import PromptInjectionSanitizer, XMLContextFencer

    # Stage 1: Conversational Pre-Retrieval Rewriting
    standalone_query = await ConversationalQueryRewriter.rewrite_query_async(query, chat_history)

    # Stage 2: Primary Retrieval
    ctx_text, citations, trace = await async_extract_advanced_rag_context(
        query=standalone_query,
        max_chunks=max_chunks,
        auth_context=auth_context,
        return_trace=True
    )

    resolved_parents = trace.get("resolved_parents", [])
    crag_state, confidence = CRAGEvaluator.evaluate_confidence(resolved_parents, standalone_query)

    # Stage 3: Adaptive Handling based on CRAG State
    if crag_state == CRAGState.CORRECT:
        fenced_context = XMLContextFencer.encapsulate_chunks(resolved_parents)
        return {
            "status": CRAGState.CORRECT.value,
            "query": standalone_query,
            "raw_query": query,
            "confidence": confidence,
            "context": fenced_context,
            "citations": citations,
            "resolved_parents": resolved_parents,
            "trace": trace
        }

    elif crag_state == CRAGState.AMBIGUOUS:
        logger.info(f"[CRAG] Ambiguous context (conf: {confidence:.2f}). Triggering secondary retrieval pass...")
        reformulated_query = CRAGEvaluator.reformulate_query(standalone_query, resolved_parents)

        # Secondary retrieval pass
        sec_ctx, sec_cites, sec_trace = await async_extract_advanced_rag_context(
            query=reformulated_query,
            max_chunks=max_chunks,
            auth_context=auth_context,
            return_trace=True
        )

        sec_parents = sec_trace.get("resolved_parents", [])
        
        # Merge & deduplicate primary and secondary parent candidate pools
        seen_ids = set()
        merged_parents = []
        for p in resolved_parents + sec_parents:
            p_id = p.get("parent_id") or p.get("id")
            if p_id not in seen_ids:
                seen_ids.add(p_id)
                merged_parents.append(p)

        # Re-evaluate merged pool
        new_state, new_conf = CRAGEvaluator.evaluate_confidence(merged_parents, standalone_query)
        fenced_context = XMLContextFencer.encapsulate_chunks(merged_parents)

        return {
            "status": new_state.value,
            "query": standalone_query,
            "reformulated_query": reformulated_query,
            "confidence": max(confidence, new_conf),
            "context": fenced_context,
            "citations": citations + [c for c in sec_cites if c not in citations],
            "resolved_parents": merged_parents,
            "trace": {
                "primary": trace,
                "secondary": sec_trace,
                "crag_loop_executed": True
            }
        }

    else:  # CRAGState.INCORRECT
        logger.warning(f"[CRAG] Incorrect / insufficient context (conf: {confidence:.2f}). Bypassing generation.")
        return {
            "status": CRAGState.INCORRECT.value,
            "error": "insufficient_context",
            "message": f"Insufficient verified domain context to answer query (Confidence: {confidence:.2f} < 0.35).",
            "query": standalone_query,
            "confidence": confidence,
            "context": "",
            "citations": [],
            "resolved_parents": [],
            "trace": trace
        }
