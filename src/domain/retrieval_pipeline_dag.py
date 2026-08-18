"""
Dynamic Composable RAG Execution DAG Engine.
Chains Multi-Hop Query Decomposition, Sparse/Dense Hybrid Retrieval, ColBERT Late-Interaction MaxSim,
Counterfactual Boundary Retrieval, Self-RAG Active Reflection, and Speculative Draft Synthesis into a unified execution pipeline.
Standard: Python Standard Library (dataclasses, typing, time, logging, threading).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import time
import logging
import threading

logger = logging.getLogger(__name__)


@dataclass
class RetrievalPipelineMetrics:
    total_duration_ms: float = 0.0
    stages_executed: List[str] = field(default_factory=list)
    stage_latencies_ms: Dict[str, float] = field(default_factory=dict)
    initial_candidate_count: int = 0
    final_chunk_count: int = 0
    grounding_confidence: float = 1.0
    expansion_triggered: bool = False
    reflection_triggered: bool = False
    boundary_scenarios_count: int = 0
    speculative_drafts_count: int = 0


@dataclass
class RetrievalContext:
    query: str
    cleaned_query: str
    intent: str = "general"
    context_text: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    boundary_context: str = ""
    scenarios: List[Dict[str, Any]] = field(default_factory=list)
    speculative_drafts: List[Dict[str, Any]] = field(default_factory=list)
    best_speculative_draft: str = ""
    web_sources: List[Dict[str, Any]] = field(default_factory=list)
    domain_instructions: Optional[str] = None
    metrics: RetrievalPipelineMetrics = field(default_factory=RetrievalPipelineMetrics)


class RetrievalDAGPipeline:
    """
    Composable Retrieval Pipeline orchestrating the 6-stage SOTA RAG DAG:
    1. Intent Classification & Domain Plugin Interception
    2. Multi-Hop Query Decomposition & Multi-Channel Candidate Fetch (FTS5 + Dense Vectors + Graph)
    3. Counterfactual & Boundary Condition Retrieval
    4. Self-RAG Relevance Grading & Active Reflection Loop
    5. Speculative Dual-Tier Candidate Draft Synthesis
    6. Entropy Compression, Deduplication & Final Citation Attribution
    """

    def __init__(self, max_chunks: int = 5, jaccard_threshold: float = 0.70):
        self.max_chunks = max_chunks
        self.jaccard_threshold = jaccard_threshold

    def execute(
        self,
        query: str,
        enable_web: bool = False,
        domain_override: Optional[str] = None,
        enable_boundary: bool = False,
        enable_speculative: bool = True
    ) -> RetrievalContext:
        t_start = time.perf_counter()
        ctx = RetrievalContext(query=query, cleaned_query=query.strip())
        metrics = ctx.metrics

        # Stage 1: Domain SPI Interception & Intent Classification
        t_stage = time.perf_counter()
        from src.domain.intent_router import classify_query_intent
        ctx.intent = classify_query_intent(ctx.cleaned_query)

        from src.core.domain_plugin_spi import get_domain_registry
        registry = get_domain_registry()
        plugin = registry.get(domain_override) if domain_override else registry.find_handler(query)
        if plugin:
            ctx.domain_instructions = plugin.get_system_prompt_extension(query)
            metrics.stages_executed.append(f"plugin_intercept:{plugin.manifest.name}")
        metrics.stage_latencies_ms["stage_1_intent"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 2: Multi-Hop Decomposition & Multi-Channel Candidate Fetch
        t_stage = time.perf_counter()
        from src.domain.rag_engine import (
            extract_advanced_rag_context,
            decompose_multihop_query,
            derive_boundary_queries,
            grade_retrieval_relevance,
            reformulate_query,
            synthesize_speculative_drafts
        )

        sub_queries = decompose_multihop_query(ctx.cleaned_query)
        if len(sub_queries) > 1:
            metrics.stages_executed.append(f"multihop_decomposition:{len(sub_queries)}_parts")

        raw_context, citations = extract_advanced_rag_context(
            ctx.cleaned_query,
            max_chunks=self.max_chunks,
            jaccard_threshold=self.jaccard_threshold
        )
        metrics.initial_candidate_count = len(citations)
        metrics.stages_executed.append("multi_channel_fetch")
        metrics.stage_latencies_ms["stage_2_fetch"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 3: Counterfactual & Boundary Condition Retrieval
        t_stage = time.perf_counter()
        should_check_boundary = enable_boundary or ctx.intent in ("counterfactual_audit", "legal_compliance") or any(
            w in ctx.cleaned_query.lower() for w in ["exception", "limit", "penalty", "violation", "versus", "vs", "difference"]
        )
        if should_check_boundary:
            try:
                boundary_queries = derive_boundary_queries(ctx.cleaned_query)
                b_contexts = []
                for b_q in boundary_queries[:2]:
                    b_ctx, b_cites = extract_advanced_rag_context(b_q, max_chunks=2, jaccard_threshold=self.jaccard_threshold)
                    if b_ctx:
                        b_contexts.append(b_ctx)
                if b_contexts:
                    ctx.boundary_context = "\n\n".join(b_contexts)
                    ctx.scenarios = [
                        {"scenario": "Primary Affirmative Evidence", "query": ctx.cleaned_query, "citations": citations},
                        {"scenario": "Boundary & Exception Evidence", "queries": boundary_queries, "context": ctx.boundary_context}
                    ]
                    metrics.boundary_scenarios_count = len(ctx.scenarios)
                    metrics.stages_executed.append("counterfactual_boundary_retrieval")
            except Exception as e:
                logger.debug(f"[RetrievalDAG] Boundary scan error: {e}")
        metrics.stage_latencies_ms["stage_3_boundary"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 4: Self-RAG Relevance Grading & Active Reflection Loop
        t_stage = time.perf_counter()
        grade = grade_retrieval_relevance(ctx.cleaned_query, citations)
        metrics.grounding_confidence = grade.get("relevance_score", 1.0)

        if (len(citations) < 2 or grade.get("grounding_status") == "refinement_needed") and not raw_context:
            metrics.reflection_triggered = True
            try:
                refined_q = reformulate_query(ctx.cleaned_query, [c.get("citation", "") for c in citations])
                if refined_q and refined_q != ctx.cleaned_query:
                    re_context, re_cites = extract_advanced_rag_context(
                        refined_q,
                        max_chunks=self.max_chunks,
                        jaccard_threshold=self.jaccard_threshold
                    )
                    if re_context:
                        raw_context = (raw_context + "\n\n" + re_context).strip() if raw_context else re_context
                        citations = citations + [c for c in re_cites if c not in citations]
                        metrics.stages_executed.append("self_rag_reflection")
            except Exception as e:
                logger.debug(f"[RetrievalDAG] Self-RAG reflection error: {e}")

        # Web search fallback if requested or still empty
        if enable_web or len(citations) < 1:
            try:
                from src.domain.web_search import fetch_web_context
                ctx.web_sources = fetch_web_context(ctx.cleaned_query, max_results=3)
                if ctx.web_sources:
                    metrics.stages_executed.append("web_search")
            except Exception as e:
                logger.debug(f"[RetrievalDAG] Web search error: {e}")
        metrics.stage_latencies_ms["stage_4_reflection"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 5: Speculative Dual-Tier Draft Synthesis
        t_stage = time.perf_counter()
        if enable_speculative and citations:
            try:
                spec_res = synthesize_speculative_drafts(ctx.cleaned_query, citations)
                ctx.speculative_drafts = spec_res.get("drafts", [])
                ctx.best_speculative_draft = spec_res.get("best_draft", "")
                metrics.speculative_drafts_count = len(ctx.speculative_drafts)
                metrics.stages_executed.append("speculative_draft_synthesis")
            except Exception as e:
                logger.debug(f"[RetrievalDAG] Speculative draft synthesis error: {e}")
        metrics.stage_latencies_ms["stage_5_speculative"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 6: Entropy Compression & Token Budget Packing
        t_stage = time.perf_counter()
        if raw_context:
            try:
                from src.domain.adaptive_context_compressor import compress_context_entropy
                comp_res = compress_context_entropy([raw_context])
                if comp_res.get("compressed_chunks") and comp_res["compressed_chunks"][0]:
                    raw_context = comp_res["compressed_chunks"][0]
                    metrics.stages_executed.append("entropy_compression")
            except Exception:
                pass
        metrics.stage_latencies_ms["stage_6_compression"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 7: Domain Plugin Post-Retrieval Enrichment
        if plugin:
            citations = plugin.enrich_retrieval(query, citations)

        ctx.context_text = raw_context or ""
        ctx.citations = citations
        metrics.final_chunk_count = len(citations)
        metrics.total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)

        return ctx


# Global singleton executor
_dag_pipeline: Optional[RetrievalDAGPipeline] = None
_dag_lock = threading.Lock()

def get_retrieval_pipeline() -> RetrievalDAGPipeline:
    global _dag_pipeline
    if _dag_pipeline is None:
        with _dag_lock:
            if _dag_pipeline is None:
                _dag_pipeline = RetrievalDAGPipeline()
    return _dag_pipeline

# Epistemic 4-Pillar Aliases
RetrievalPipelineDAG = RetrievalDAGPipeline
create_retrieval_dag = lambda **kwargs: RetrievalDAGPipeline(**kwargs)

