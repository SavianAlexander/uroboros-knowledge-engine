"""
Uroboros Knowledge Engine - Domain Layer Facade.
Exposes clean, cohesive APIs across the 7 Core Domain Subsystems:
1. Search & Hybrid Retrieval
2. Retrieval Augmented Generation (RAG)
3. Knowledge Graph & Traversal
4. Legal & Regulatory Intelligence
5. Security, Privacy & Compliance
6. System Telemetry & Process Management
7. Analytics & Data Profiling
"""

# 1. Search & Hybrid Retrieval
from src.domain.query_intent_classifier import classify_query_intent, route_query_intent
from src.domain.reranker import reciprocal_rank_fusion, score_rerank_candidates
from src.domain.sublinear_ann_index import SublinearANNIndex
from src.domain.sparse_dense_fusion import fuse_sparse_dense_rankings
from src.domain.recency_decay import apply_recency_decay
from src.domain.smart_filter import parse_smart_query_filter

# 2. RAG & Grounding
from src.domain.rag_engine import extract_advanced_rag_context, build_augmented_prompt, generate_hyde_expansion
from src.domain.dense_propositions import extract_dense_propositions
from src.domain.entropy_chunker import chunk_by_semantic_entropy, compute_shannon_entropy
from src.domain.parent_child_retrieval import expand_child_chunks_to_parents
from src.domain.grounding_scorecard import compute_grounding_scorecard, evaluate_grounding_scorecard
from src.domain.rag_evaluator import evaluate_rag_triad
from src.domain.source_citation_generator import generate_grounded_citations
from src.domain.hallucination_guard import evaluate_hallucination_risk
from src.domain.counterfactual_rag import execute_counterfactual_rag

# 3. Knowledge Graph & Traversal
from src.domain.hypergraph_router import HypergraphRouter
from src.domain.graph_multihop import find_multihop_pathways
from src.domain.louvain_clustering import detect_louvain_communities
from src.domain.wikilink_parser import extract_wikilinks, build_wikilink_graph
from src.domain.relational_schema_linker import RelationalSchemaLinker

# 4. Security, Privacy & Compliance
from src.domain.pii_privacy_guard import redact_pii_from_text, inspect_and_redact_pii
from src.domain.crypto_audit_ledger import CryptoAuditLedger
from src.domain.vault_merkle_tree import VaultMerkleTree
from src.domain.acl_permission_engine import AclPermissionEngine
from src.domain.zk_data_masker import pseudonymize_records

# 6. Telemetry & Process Management
from src.domain.system_telemetry import gather_system_telemetry, get_system_telemetry
from src.domain.system_health_telemetry import check_system_health
from src.domain.semantic_drift_monitor import track_semantic_drift
from src.domain.process_manager import ProcessManager

# 7. Analytics & Data Profiling
from src.domain.readability_analyzer import analyze_readability_metrics
from src.domain.statistical_data_profiler import profile_tabular_dataset
from src.domain.transcription_engine import TranscriptionEngine

__all__ = [
    # Search
    "classify_query_intent",
    "route_query_intent",
    "reciprocal_rank_fusion",
    "score_rerank_candidates",
    "SublinearANNIndex",
    "fuse_sparse_dense_rankings",
    "apply_recency_decay",
    "parse_smart_query_filter",
    # RAG
    "extract_advanced_rag_context",
    "build_augmented_prompt",
    "generate_hyde_expansion",
    "extract_dense_propositions",
    "chunk_by_semantic_entropy",
    "compute_shannon_entropy",
    "expand_child_chunks_to_parents",
    "compute_grounding_scorecard",
    "evaluate_grounding_scorecard",
    "evaluate_rag_triad",
    "generate_grounded_citations",
    "evaluate_hallucination_risk",
    "execute_counterfactual_rag",
    # Graph
    "HypergraphRouter",
    "find_multihop_pathways",
    "detect_louvain_communities",
    "extract_wikilinks",
    "build_wikilink_graph",
    "RelationalSchemaLinker",
    # Compliance
    "redact_pii_from_text",
    "inspect_and_redact_pii",
    "CryptoAuditLedger",
    "VaultMerkleTree",
    "AclPermissionEngine",
    "pseudonymize_records",
    # Telemetry
    "gather_system_telemetry",
    "get_system_telemetry",
    "check_system_health",
    "track_semantic_drift",
    "ProcessManager",
    # Analytics
    "analyze_readability_metrics",
    "profile_tabular_dataset",
    "TranscriptionEngine",
    # Unified Engines
    "bandit_select_pipeline",
    "compute_graph_pagerank",
    "generate_mermaid_graph",
    "export_graph_to_graphml",
    "rerank_search_results_colbert",
    "verify_claims_and_consensus",
]
from src.domain.query_intent import bandit_select_pipeline
from src.domain.graph_engine import compute_graph_pagerank, generate_mermaid_graph, export_graph_to_graphml
from src.domain.reranking import rerank_search_results_colbert
from src.domain.verification_guards import verify_claims_and_consensus
