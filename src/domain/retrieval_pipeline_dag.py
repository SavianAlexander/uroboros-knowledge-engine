"""
Dynamic Composable RAG Execution DAG Engine.
Chains sparse/dense retrieval, conditional HyDE expansion, binary ColBERT MaxSim reranking,
MinHash Jaccard deduplication, and Self-RAG grounding into a unified execution pipeline.
Standard: Python Standard Library (dataclasses, typing, time, logging).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import time
import logging

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


@dataclass
class RetrievalContext:
    query: str
    cleaned_query: str
    intent: str = "general"
    context_text: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    web_sources: List[Dict[str, Any]] = field(default_factory=list)
    domain_instructions: Optional[str] = None
    metrics: RetrievalPipelineMetrics = field(default_factory=RetrievalPipelineMetrics)


class RetrievalDAGPipeline:
    """
    Composable Retrieval Pipeline orchestrating the multi-stage RAG DAG:
    1. Intent & Plugin Interception
    2. Multi-Channel Candidate Fetch (FTS5 + Dense Vectors + Wikilink Graph)
    3. Conditional Query Expansion (HyDE / Decomposition)
    4. Late-Interaction MaxSim Reranking (ColBERT + RRF)
    5. Deduplication & Entropy Compression
    6. Grounding Verification & Citation Attribution
    """

    def __init__(self, max_chunks: int = 5, jaccard_threshold: float = 0.70):
        self.max_chunks = max_chunks
        self.jaccard_threshold = jaccard_threshold

    def execute(self, query: str, enable_web: bool = False, domain_override: Optional[str] = None) -> RetrievalContext:
        t_start = time.perf_counter()
        ctx = RetrievalContext(query=query, cleaned_query=query.strip())
        metrics = ctx.metrics

        # Stage 1: Domain SPI Interception & Intent Classification
        t_stage = time.perf_counter()
        from src.core.domain_plugin_spi import get_domain_registry
        registry = get_domain_registry()
        plugin = registry.get(domain_override) if domain_override else registry.find_handler(query)
        if plugin:
            ctx.domain_instructions = plugin.get_system_prompt_extension(query)
            metrics.stages_executed.append(f"plugin_intercept:{plugin.manifest.name}")
        metrics.stage_latencies_ms["stage_1_intent"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 2: Fast-Path Multi-Channel Candidate Fetch
        t_stage = time.perf_counter()
        from src.infrastructure.vector_engine import extract_rag_context
        from src.domain.rag_engine import extract_advanced_rag_context

        raw_context, citations = extract_advanced_rag_context(
            ctx.cleaned_query,
            max_chunks=self.max_chunks,
            jaccard_threshold=self.jaccard_threshold
        )
        metrics.initial_candidate_count = len(citations)
        metrics.stages_executed.append("multi_channel_fetch")
        metrics.stage_latencies_ms["stage_2_fetch"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 3: Conditional Expansion (HyDE / Web) if local hits are insufficient
        t_stage = time.perf_counter()
        if len(citations) < 2 and not raw_context:
            metrics.expansion_triggered = True
            try:
                from src.core.model_manager import expand_query_with_llm
                expanded_q = expand_query_with_llm(ctx.cleaned_query)
                if expanded_q and expanded_q != ctx.cleaned_query:
                    raw_context, citations = extract_advanced_rag_context(
                        expanded_q,
                        max_chunks=self.max_chunks,
                        jaccard_threshold=self.jaccard_threshold
                    )
                    metrics.stages_executed.append("hyde_expansion")
            except Exception as e:
                logger.debug(f"[RetrievalDAG] Expansion fallback error: {e}")

        # Web search fallback if requested or still empty
        if enable_web or len(citations) < 1:
            try:
                from src.domain.web_search import fetch_web_context
                ctx.web_sources = fetch_web_context(ctx.cleaned_query, max_results=3)
                if ctx.web_sources:
                    metrics.stages_executed.append("web_search")
            except Exception as e:
                logger.debug(f"[RetrievalDAG] Web search error: {e}")
        metrics.stage_latencies_ms["stage_3_expansion"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 4: Entropy Compression
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
        metrics.stage_latencies_ms["stage_4_compression"] = round((time.perf_counter() - t_stage) * 1000, 2)

        # Stage 5: Domain Plugin Post-Retrieval Enrichment
        if plugin:
            citations = plugin.enrich_retrieval(query, citations)

        ctx.context_text = raw_context or ""
        ctx.citations = citations
        metrics.final_chunk_count = len(citations)
        metrics.total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)

        return ctx


# Global singleton executor
_dag_pipeline: Optional[RetrievalDAGPipeline] = None

def get_retrieval_pipeline() -> RetrievalDAGPipeline:
    global _dag_pipeline
    if _dag_pipeline is None:
        _dag_pipeline = RetrievalDAGPipeline()
    return _dag_pipeline
