"""
Pillar 1: Retrieval & Grounding Domain Subpackage.
Encapsulates hybrid search, RAG pipelines, reranking, dense propositions, and vector operations.
"""
from src.domain.retrieval_pipeline_dag import RetrievalPipelineDAG, RetrievalDAGPipeline, create_retrieval_dag
from src.domain.rag_engine import (
    extract_advanced_rag_context,
    build_augmented_prompt,
    generate_hyde_expansion,
    execute_counterfactual_rag,
)
from src.domain.reranking import (
    reciprocal_rank_fusion,
    score_rerank_candidates,
    rerank_search_results_colbert,
)
from src.domain.epistemic_tiering import EpistemicTier, classify_epistemic_tier, tier_weighted_rank
from src.domain.vector_store import VectorStore
from src.domain.dense_propositions import extract_dense_propositions
from src.domain.entropy_chunker import chunk_by_semantic_entropy, compute_shannon_entropy
from src.domain.parent_child_retrieval import expand_child_chunks_to_parents
from src.domain.sublinear_ann_index import SublinearANNIndex
from src.domain.sparse_dense_fusion import fuse_sparse_dense_rankings
from src.domain.recency_decay import apply_recency_decay
from src.domain.smart_filter import parse_smart_query_filter
from src.domain.query_intent_classifier import classify_query_intent, route_query_intent
from src.domain.grounded_retrieval_engine import GroundedRetrievalEngine
from src.domain.grounding_scorecard import compute_grounding_scorecard, evaluate_grounding_scorecard
from src.domain.rag_evaluator import evaluate_rag_triad
from src.domain.source_citation_generator import generate_grounded_citations
from src.domain.hallucination_guard import evaluate_hallucination_risk

__all__ = [
    "RetrievalPipelineDAG",
    "RetrievalDAGPipeline",
    "create_retrieval_dag",
    "extract_advanced_rag_context",
    "build_augmented_prompt",
    "generate_hyde_expansion",
    "execute_counterfactual_rag",
    "reciprocal_rank_fusion",
    "score_rerank_candidates",
    "rerank_search_results_colbert",
    "EpistemicTier",
    "classify_epistemic_tier",
    "tier_weighted_rank",
    "VectorStore",
    "extract_dense_propositions",
    "chunk_by_semantic_entropy",
    "compute_shannon_entropy",
    "expand_child_chunks_to_parents",
    "SublinearANNIndex",
    "fuse_sparse_dense_rankings",
    "apply_recency_decay",
    "parse_smart_query_filter",
    "classify_query_intent",
    "route_query_intent",
    "GroundedRetrievalEngine",
    "compute_grounding_scorecard",
    "evaluate_grounding_scorecard",
    "evaluate_rag_triad",
    "generate_grounded_citations",
    "evaluate_hallucination_risk",
]
