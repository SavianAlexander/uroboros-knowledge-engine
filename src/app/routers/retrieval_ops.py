"""
Granular operational RAG stages router.
Includes ColBERT reranking, MRL compression, grounding verification, entropy chunking,
speculative synthesis, active refinement, budget allocation, distractor filtering,
counterfactual simulation, SLA breaker, belief updates, and governance endpoints.
"""
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Body

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Declarative Pipeline Schemas
# ---------------------------------------------------------------------------

class ColBERTRerankRequest(BaseModel):
    query_tokens: List[List[float]] = Field(..., description="Query token embeddings matrix for late interaction")
    candidates: List[Dict[str, Any]] = Field(..., description="Document candidate chunks with token embeddings")


class MRLCompressRequest(BaseModel):
    embeddings: List[List[float]] = Field(..., description="Dense vector embeddings to truncate/compress")
    target_dim: int = Field(256, description="Target Matryoshka dimension (e.g. 128, 256, 512)")


class GroundingVerifyRequest(BaseModel):
    llm_response: str = Field(..., description="Generated LLM response text to verify against ground truth")
    source_chunks: List[str] = Field(..., description="Retrieved source context passages")
    threshold: float = Field(0.4, description="Minimum grounding alignment threshold")


class EntropyChunkRequest(BaseModel):
    text: str = Field(..., description="Raw document text to segment based on semantic entropy")
    distance_threshold: float = Field(0.65, description="Semantic distance boundary threshold")
    max_chunk_size: int = Field(500, description="Maximum token length per chunk")


class SpeculativeRAGRequest(BaseModel):
    query: str = Field(..., description="User query prompt")
    source_chunks: List[str] = Field(..., description="Retrieved context chunks for multi-hypothesis synthesis")


class ActiveRAGRequest(BaseModel):
    query: str = Field(..., description="User query prompt")
    initial_chunks: List[str] = Field(..., description="Initial retrieved passages")
    confidence_threshold: float = Field(0.40, description="Minimum confidence before triggering iterative refinement")


class BudgetAllocateRequest(BaseModel):
    total_token_budget: int = Field(4096, description="Total token capacity of prompt context window")
    vector_chunks: Optional[List[str]] = Field(None, description="Retrieved vector passage chunks")
    graph_halos: Optional[List[str]] = Field(None, description="Knowledge graph halo entity texts")
    entity_metadata: Optional[List[Dict[str, Any]]] = Field(None, description="Metadata key-value dictionaries")
    chat_history: Optional[List[Dict[str, Any]]] = Field(None, description="Prior conversational turn messages")


class DistractorFilterRequest(BaseModel):
    query: str = Field(..., description="User search query")
    candidates: List[Dict[str, Any]] = Field(..., description="Retrieved candidate chunks to filter")
    min_intent_overlap: float = Field(0.15, description="Minimum intent token overlap score")


class CrossLingualRequest(BaseModel):
    query: str = Field(..., description="Search query in any source language")
    source_lang: str = Field("auto", description="Source ISO language code or auto-detect")


class AnonymizeRequest(BaseModel):
    text: str = Field(..., description="Raw text containing potential PII or sensitive tokens")


class SelfHealRequest(BaseModel):
    auto_reindex: Optional[bool] = Field(True, description="Whether to automatically reindex drifted vectors")
    max_drift_threshold: Optional[float] = Field(0.15, description="Maximum allowable centroid drift threshold")
    dry_run: Optional[bool] = Field(False, description="Simulate self-healing pass without writing changes")


class SchemaRAGRequest(BaseModel):
    table_text: str = Field(..., description="Tabular raw text or CSV string")


class TemporalRAGRequest(BaseModel):
    candidates: List[Dict[str, Any]] = Field(..., description="Document candidates with modification timestamps")
    half_life_days: float = Field(90.0, description="Exponential decay half-life in days")


class ACLFilterRequest(BaseModel):
    candidates: List[Dict[str, Any]] = Field(..., description="Candidate documents with tenant ACL tags")
    user_tenant_id: str = Field(..., description="Tenant ID of requesting user")
    user_roles: List[str] = Field(..., description="Roles possessed by requesting user")


class LineageExplainRequest(BaseModel):
    query: str = Field(..., description="Original user prompt query")
    answer: str = Field(..., description="Synthesized answer text")
    source_chunks: List[str] = Field(..., description="Context chunks utilized")
    active_strategy: str = Field("auto_unified", description="Retrieval strategy name")
    latency_ms: float = Field(0.8, description="Execution latency in milliseconds")


class GroundingRewriteRequest(BaseModel):
    llm_response: str = Field(..., description="Raw LLM response requiring verification and rewriting")
    source_chunks: List[str] = Field(..., description="Ground truth source passage chunks")
    threshold: float = Field(0.4, description="Strict grounding threshold")


class DeepLinkRequest(BaseModel):
    citation_id: int = Field(..., description="Identifier of citation")
    source_document_text: str = Field(..., description="Complete source document text")
    target_sentence: str = Field(..., description="Target sentence to locate and deep-link")


class PersonaSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    candidates: List[Dict[str, Any]] = Field(..., description="Retrieved candidate documents")
    persona: str = Field("developer", description="Target persona type (e.g. developer, executive, researcher)")


class PreferenceFeedbackRequest(BaseModel):
    document_id: str = Field(..., description="Unique document ID")
    query: str = Field(..., description="Query associated with feedback")
    rating: int = Field(..., description="User preference rating (-1, 0, or 1)")


class VoiceSearchRequest(BaseModel):
    audio_transcript_payload: str = Field(..., description="Voice transcription payload")
    top_k: int = Field(5, description="Number of results to return")


class GraphTopologyRequest(BaseModel):
    source_documents: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents to construct graph topology from")


class SpeculativeStreamRequest(BaseModel):
    prompt: str = Field(..., description="User input prompt")
    base_response: str = Field(..., description="Base model draft response")
    draft_count: Optional[int] = Field(3, description="Number of speculative candidate streams")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(256, description="Maximum tokens per speculative chunk")


class ExecutiveBriefingRequest(BaseModel):
    document_chunks: List[str] = Field(..., description="Context chunks to synthesize into briefing")
    title: str = Field("Executive Briefing", description="Briefing title")
    max_action_items: Optional[int] = Field(10, description="Maximum number of action items")
    priority_filter: Optional[str] = Field(None, description="Optional priority level filter")
    target_audience: Optional[str] = Field("Executive", description="Audience tone and focus")


class RAGEvalRequest(BaseModel):
    query: str = Field(..., description="Evaluation query")
    answer: str = Field(..., description="Evaluated answer")
    retrieved_contexts: List[str] = Field(..., description="Retrieved contexts")
    golden_answer: Optional[str] = Field(None, description="Optional reference golden answer")


class SemanticDiffRequest(BaseModel):
    old_doc_text: str = Field(..., description="Original baseline document text")
    new_doc_text: str = Field(..., description="Modified target document text")


class QueryIntentRequest(BaseModel):
    query: str = Field(..., description="Search query string to classify")


class InjectionScanRequest(BaseModel):
    text: str = Field(..., description="Prompt string to scan for adversarial injections")


class CredibilityWeightRequest(BaseModel):
    candidates: List[Dict[str, Any]] = Field(..., description="Retrieved candidate documents to score for authority")


class FAQSynthesizeRequest(BaseModel):
    query_history: List[str] = Field(..., description="Historical search queries")


class AutoTunerRequest(BaseModel):
    historical_feedback: List[Dict[str, Any]] = Field(..., description="Historical click and rating feedback")
    current_weights: Optional[Dict[str, float]] = Field(None, description="Current retrieval channel weights")


class SyntheticQARequest(BaseModel):
    document_text: str = Field(..., description="Source document text for QA synthesis")
    max_triples: int = Field(5, description="Maximum number of synthetic QA triples to generate")


class CodeASTRequest(BaseModel):
    code_snippet: str = Field(..., description="Source code snippet to parse")


class VisualCanvasRequest(BaseModel):
    raw_document_layout: Dict[str, Any] = Field(..., description="Bounding box spatial layout")
    min_confidence: Optional[float] = Field(0.80, description="Minimum OCR confidence filter")
    extract_images: Optional[bool] = Field(True, description="Extract image region bounding boxes")
    extract_tables: Optional[bool] = Field(True, description="Extract table grid structures")


class CounterfactualRequest(BaseModel):
    base_query: str = Field(..., description="Base query prompt")
    base_contexts: List[str] = Field(..., description="Ground truth context passages")
    masked_chunk_indices: Optional[List[int]] = Field(None, description="Indices of chunks to mask or counterfactually alter")
    max_scenarios: Optional[int] = Field(2, description="Number of counterfactual variants to simulate")


class SLABreakerRequest(BaseModel):
    latency_ms: float = Field(..., description="Current observed retrieval latency in milliseconds")
    max_sla_ms: float = Field(50.0, description="SLA budget threshold in milliseconds")


class CryptoAuditRequest(BaseModel):
    query: str = Field(..., description="Audited query")
    answer: str = Field(..., description="Audited answer")
    contexts: List[str] = Field(..., description="Contexts used in generation")


class EpistemicBeliefRequest(BaseModel):
    new_claim: str = Field(..., description="New factual claim to integrate")
    existing_beliefs: Optional[List[Dict[str, Any]]] = Field(None, description="Current belief node graph")


class ContextMemoryRequest(BaseModel):
    chat_history: List[Dict[str, str]] = Field(..., description="Sequential conversational message turns")
    target_summary_len: int = Field(150, description="Target character or word length for summary")


class PredictivePrefetchRequest(BaseModel):
    active_query: str = Field(..., description="Current user search query")
    retrieved_contexts: List[str] = Field(..., description="Contexts currently retrieved")


class EntityCooccurrenceRequest(BaseModel):
    documents: List[Dict[str, str]] = Field(..., description="List of document dictionaries with text contents")


class KnowledgeDistillRequest(BaseModel):
    rag_interaction_logs: List[Dict[str, Any]] = Field(..., description="Recorded RAG queries and responses")
    format_type: str = Field("alpaca", description="Dataset export format (alpaca, sharegpt, csv)")


class FactCheckRequest(BaseModel):
    doc_a_clauses: List[str] = Field(..., description="Clauses from primary document")
    doc_b_clauses: List[str] = Field(..., description="Clauses from secondary document to cross-verify")


class UniversalPipelineRequest(BaseModel):
    raw_content: str = Field(..., description="Raw file or data content")
    format_type: str = Field("markdown", description="Source format (markdown, xml, html, json, csv)")


class ProvenanceTrackRequest(BaseModel):
    file_path: str = Field(..., description="Canonical path of file")
    file_content: str = Field(..., description="Current content of file")
    author: str = Field("system", description="Author or agent identity")


class MultiAgentConsensusRequest(BaseModel):
    query: str = Field(..., description="Complex query requiring multi-agent consensus")
    retrieved_contexts: List[str] = Field(..., description="Retrieved evidence chunks")


class VectorDriftAuditRequest(BaseModel):
    current_centroids: List[List[float]] = Field(..., description="Baseline cluster centroid vectors")
    new_embeddings: List[List[float]] = Field(..., description="Newly indexed embedding vectors")
    drift_threshold: float = Field(0.25, description="Maximum allowable cosine drift")


class TokenCompressRequest(BaseModel):
    text: str = Field(..., description="Text stream to compress")


class SystemHealthRequest(BaseModel):
    recent_latencies_ms: List[float] = Field(default_factory=lambda: [0.80, 1.10, 1.20], description="Sampled latencies in ms")
    cache_hits: int = Field(100, description="Total cache hit count")
    cache_misses: int = Field(5, description="Total cache miss count")


class CodeRefactorRequest(BaseModel):
    code_snippet: str = Field(..., description="Source code to analyze and refactor")


class SwarmDecomposeRequest(BaseModel):
    master_goal: str = Field(..., description="Master goal prompt for agent swarm")


class DocAlignRequest(BaseModel):
    code_snippet: str = Field(..., description="Code snippet to check docstring alignment against")


class ZKMaskRequest(BaseModel):
    sensitive_data: str = Field(..., description="Data to mask with cryptographic zero-knowledge proof")
    secret_salt: str = Field("uroboros_zk_salt", description="Secret salt for HMAC")


# ---------------------------------------------------------------------------
# Granular Operational Endpoints
# ---------------------------------------------------------------------------

@router.post("/api/rag/colbert/rerank")
def colbert_rerank_endpoint(req: ColBERTRerankRequest):
    """ColBERT Late Interaction token-level MaxSim reranking endpoint."""
    from src.domain.reranking import rerank_documents_colbert
    reranked = rerank_documents_colbert(req.query_tokens, req.candidates)
    return {"total": len(reranked), "results": reranked, "status": "success"}


@router.post("/api/rag/mrl/compress")
def mrl_compress_endpoint(req: MRLCompressRequest):
    """Matryoshka Representation Learning (MRL) dimension truncation endpoint."""
    from src.domain.mrl_compressor import batch_compress_embeddings
    compressed = batch_compress_embeddings(req.embeddings, req.target_dim)
    return {"target_dim": req.target_dim, "total": len(compressed), "compressed_embeddings": compressed, "status": "success"}


@router.post("/api/rag/grounding/verify")
def rag_grounding_verify_endpoint(req: GroundingVerifyRequest):
    """Self-Correction RAG Grounding & Hallucination Guard endpoint."""
    from src.domain.rag_grounding_guard import verify_rag_grounding
    return verify_rag_grounding(req.llm_response, req.source_chunks, req.threshold)


@router.post("/api/rag/chunking/entropy")
def entropy_chunking_endpoint(req: EntropyChunkRequest):
    """Dynamic Entropy-Based Semantic Boundary Chunker endpoint."""
    from src.domain.entropy_chunker import chunk_by_semantic_entropy
    chunks = chunk_by_semantic_entropy(req.text, req.distance_threshold, req.max_chunk_size)
    return {"total": len(chunks), "chunks": chunks, "status": "success"}


@router.post("/api/rag/speculative/synthesize")
def speculative_rag_endpoint(req: SpeculativeRAGRequest):
    """Speculative RAG Multi-Hypothesis Synthesis endpoint."""
    from src.domain.rag_engine import synthesize_speculative_rag
    return synthesize_speculative_rag(req.query, req.source_chunks)


@router.post("/api/rag/active/refine")
def active_rag_refine_endpoint(req: ActiveRAGRequest):
    """Active RAG Iterative Query Refinement Loop endpoint."""
    from src.domain.rag_engine import execute_active_rag_loop
    return execute_active_rag_loop(req.query, req.initial_chunks, req.confidence_threshold)


@router.post("/api/rag/budget/allocate")
def budget_allocate_endpoint(req: BudgetAllocateRequest):
    """Adaptive Context Window Budget Allocator endpoint."""
    from src.domain.context_budget_allocator import allocate_context_budget
    return allocate_context_budget(req.total_token_budget, req.vector_chunks, req.graph_halos, req.entity_metadata, req.chat_history)


@router.post("/api/rag/distractor/filter")
def distractor_filter_endpoint(req: DistractorFilterRequest):
    """Adversarial Noise & Distractor Filter endpoint."""
    from src.domain.distractor_filter import filter_distractor_chunks
    return filter_distractor_chunks(req.query, req.candidates, req.min_intent_overlap)


@router.post("/api/rag/governance/self-heal")
def self_heal_endpoint(req: Optional[SelfHealRequest] = None):
    """Autonomous Vector Index Self-Healing & Drift Detector endpoint."""
    from src.domain.index_self_healing import execute_index_self_healing
    return execute_index_self_healing()


@router.post("/api/rag/governance/cross-lingual")
def cross_lingual_endpoint(req: CrossLingualRequest):
    """Cross-Lingual Semantic Alignment & Transliteration endpoint."""
    from src.domain.multilingual_rag import align_cross_lingual_query
    return align_cross_lingual_query(req.query, req.source_lang)


@router.post("/api/rag/governance/anonymize")
def anonymize_endpoint(req: AnonymizeRequest):
    """Differential Privacy & PII Redaction Guard endpoint."""
    from src.domain.privacy_anonymizer import anonymize_text_pii
    return anonymize_text_pii(req.text)


@router.post("/api/rag/operational/schema")
def schema_rag_endpoint(req: SchemaRAGRequest):
    """Structured Tabular Schema RAG Extractor endpoint."""
    from src.domain.schema_rag import extract_tabular_schema_chunks
    chunks = extract_tabular_schema_chunks(req.table_text)
    return {"total": len(chunks), "chunks": chunks, "status": "success"}


@router.post("/api/rag/operational/temporal")
def temporal_rag_endpoint(req: TemporalRAGRequest):
    """Temporal Decay & Recency-Weighted Scoring endpoint."""
    from src.domain.temporal_rag import apply_temporal_decay_scoring
    scored = apply_temporal_decay_scoring(req.candidates, req.half_life_days)
    return {"total": len(scored), "scored_candidates": scored, "status": "success"}


@router.post("/api/rag/operational/acl-filter")
def acl_filter_endpoint(req: ACLFilterRequest):
    """Multi-Tenant ACL & Role Vector Isolation Guard endpoint."""
    from src.domain.acl_vector_guard import filter_candidates_by_acl
    return filter_candidates_by_acl(req.candidates, req.user_tenant_id, req.user_roles)


@router.post("/api/rag/lineage/explain")
def lineage_explain_endpoint(req: LineageExplainRequest):
    """Live RAG Lineage Telemetry Explainer endpoint."""
    from src.domain.rag_lineage_explainer import get_rag_lineage_telemetry
    return get_rag_lineage_telemetry(req.query, req.answer, req.source_chunks, req.active_strategy, req.latency_ms)


@router.post("/api/rag/grounding/rewrite")
def grounding_rewrite_endpoint(req: GroundingRewriteRequest):
    """Agentic Self-Correction RAG Rewriter endpoint."""
    from src.domain.self_correcting_rewriter import rewrite_grounded_answer
    return rewrite_grounded_answer(req.llm_response, req.source_chunks, req.threshold)


@router.post("/api/rag/citation/deep-link")
def citation_deep_link_endpoint(req: DeepLinkRequest):
    """Sentence-Level Deep Citation Linking endpoint."""
    from src.domain.citation_deep_linker import create_deep_citation_link
    return create_deep_citation_link(req.citation_id, req.source_document_text, req.target_sentence)


@router.post("/api/vector/search/persona")
def persona_search_endpoint(req: PersonaSearchRequest):
    """Adaptive Persona-Aware Search Tuning endpoint."""
    from src.domain.persona_search_tuner import tune_search_by_persona
    return tune_search_by_persona(req.query, req.candidates, req.persona)


@router.post("/api/rag/preference/feedback")
def preference_feedback_endpoint(req: PreferenceFeedbackRequest):
    """Instant Local RLHF Preference Optimization endpoint."""
    from src.domain.preference_learning import log_user_feedback
    return log_user_feedback(req.document_id, req.query, req.rating)


@router.post("/api/rag/voice/search")
def voice_search_endpoint(req: VoiceSearchRequest):
    """Voice Memo Search & Local Phoneme Transcriber endpoint."""
    from src.domain.voice_rag import transcribe_and_search_voice_memo
    return transcribe_and_search_voice_memo(req.audio_transcript_payload, req.top_k)


@router.post("/api/rag/graph/topology")
def graph_topology_endpoint(req: GraphTopologyRequest):
    """Interactive Knowledge Graph Topology endpoint."""
    from src.domain.graph_explorer import generate_graph_topology
    return generate_graph_topology(req.source_documents)


@router.post("/api/rag/stream/speculative")
def speculative_stream_endpoint(req: SpeculativeStreamRequest):
    """Zero-Latency Speculative Response Streamer endpoint."""
    from src.domain.speculative_streamer import generate_speculative_stream_chunks
    chunks = generate_speculative_stream_chunks(req.prompt, req.base_response)
    if req.draft_count and req.draft_count < len(chunks):
        chunks = chunks[:req.draft_count]
    return {"total": len(chunks), "stream_chunks": chunks, "status": "success"}


@router.post("/api/rag/briefing/generate")
def executive_briefing_endpoint(req: ExecutiveBriefingRequest):
    """Automated Executive Briefing Generator endpoint."""
    from src.domain.executive_briefing import generate_executive_briefing
    briefing = generate_executive_briefing(req.document_chunks, req.title)
    if req.priority_filter and "action_items" in briefing:
        norm_p = req.priority_filter.strip().lower()
        briefing["action_items"] = [item for item in briefing["action_items"] if norm_p in str(item.get("priority", "")).lower()]
    if req.max_action_items and "action_items" in briefing:
        briefing["action_items"] = briefing["action_items"][:req.max_action_items]
    if req.target_audience:
        briefing["target_audience"] = req.target_audience
    return briefing


@router.post("/api/rag/eval/benchmark")
def rag_eval_benchmark_endpoint(req: RAGEvalRequest):
    """Automated RAG Evaluation & Golden Dataset Benchmarker endpoint."""
    from src.domain.rag_evaluator import evaluate_rag_triad
    return evaluate_rag_triad(req.query, req.answer, req.retrieved_contexts, req.golden_answer)


@router.post("/api/rag/diff/semantic")
def semantic_diff_endpoint(req: SemanticDiffRequest):
    """Semantic Document Diff & Version Evolution Comparator endpoint."""
    from src.domain.semantic_doc_diff import compare_semantic_doc_diff
    return compare_semantic_doc_diff(req.old_doc_text, req.new_doc_text)


@router.post("/api/rag/intent/classify")
def query_intent_classify_endpoint(req: QueryIntentRequest):
    """Semantic Query Intent Classifier & Disambiguator endpoint."""
    from src.domain.query_intent_classifier import classify_query_intent
    return classify_query_intent(req.query)


@router.post("/api/rag/safety/injection-guard")
def injection_scan_endpoint(req: InjectionScanRequest):
    """Adversarial Prompt Injection & Indirect Jailbreak Guard endpoint."""
    from src.domain.prompt_injection_guard import scan_prompt_injection
    return scan_prompt_injection(req.text)


@router.post("/api/rag/authority/weight")
def credibility_weight_endpoint(req: CredibilityWeightRequest):
    """Source Document Credibility & Authority Weighting endpoint."""
    from src.domain.source_credibility_weight import apply_source_credibility_weighting
    weighted = apply_source_credibility_weighting(req.candidates)
    return {"total": len(weighted), "weighted_candidates": weighted, "status": "success"}


@router.post("/api/rag/faq/synthesize")
def faq_synthesize_endpoint(req: FAQSynthesizeRequest):
    """Continuous Automatic FAQ & Knowledge Base Synthesizer endpoint."""
    from src.domain.faq_synthesizer import synthesize_faq_from_queries
    return synthesize_faq_from_queries(req.query_history)


@router.post("/api/rag/auto-tuner/optimize")
def auto_tuner_endpoint(req: AutoTunerRequest):
    """Self-Improving Search Weight & Chunk Tuner endpoint."""
    from src.domain.auto_weight_tuner import optimize_search_parameters
    return optimize_search_parameters(req.historical_feedback, req.current_weights)


@router.post("/api/rag/synthetic/generate-qa")
def synthetic_qa_endpoint(req: SyntheticQARequest):
    """Autonomous Synthetic QA Dataset Generator endpoint."""
    from src.domain.synthetic_qa_generator import generate_synthetic_qa_triples
    return generate_synthetic_qa_triples(req.document_text, req.max_triples)


@router.post("/api/rag/code/ast-parse")
def code_ast_endpoint(req: CodeASTRequest):
    """AST Code Graph & Structural Symbol RAG endpoint."""
    from src.domain.ast_code_rag import parse_codebase_ast
    return parse_codebase_ast(req.code_snippet)


@router.post("/api/rag/canvas/visual-parse")
def visual_canvas_endpoint(req: VisualCanvasRequest):
    """Multimodal Visual Canvas OCR & Bounding Box Extractor endpoint."""
    from src.domain.visual_canvas_rag import extract_visual_canvas_regions
    return extract_visual_canvas_regions(req.raw_document_layout)


@router.post("/api/rag/counterfactual/simulate")
def counterfactual_endpoint(req: CounterfactualRequest):
    """Counterfactual RAG Scenario Simulator endpoint."""
    from src.domain.rag_engine import simulate_counterfactual_scenario
    return simulate_counterfactual_scenario(req.base_query, req.base_contexts, req.masked_chunk_indices)


@router.post("/api/rag/sla/circuit-breaker")
def sla_circuit_breaker_endpoint(req: SLABreakerRequest):
    """Sub-50ms SLA Circuit Breaker endpoint."""
    from src.domain.sla_circuit_breaker import execute_with_sla_circuit_breaker
    return execute_with_sla_circuit_breaker(
        primary_func=lambda: {"res": "ColBERT Primary"},
        fallback_func=lambda: {"res": "FTS5 Fast Fallback"},
        latency_ms=req.latency_ms,
        max_sla_ms=req.max_sla_ms
    )


@router.post("/api/rag/audit/append-crypto")
def crypto_audit_endpoint(req: CryptoAuditRequest):
    """Zero-Knowledge Cryptographic Audit Ledger endpoint."""
    from src.domain.crypto_audit_ledger import append_crypto_audit_block
    return append_crypto_audit_block(req.query, req.answer, req.contexts)


@router.post("/api/rag/epistemic/update-belief")
def epistemic_belief_endpoint(req: EpistemicBeliefRequest):
    """Dynamic Epistemic Belief Graph endpoint."""
    from src.domain.epistemic_belief_graph import update_epistemic_belief_graph
    return update_epistemic_belief_graph(req.new_claim, req.existing_beliefs)


@router.post("/api/rag/memory/compress")
def context_memory_compress_endpoint(req: ContextMemoryRequest):
    """Hierarchical Context Window Summarization Memory endpoint."""
    from src.domain.context_memory_compressor import compress_context_memory
    return compress_context_memory(req.chat_history, req.target_summary_len)


@router.post("/api/rag/prefetch/predict")
def predictive_prefetch_endpoint(req: PredictivePrefetchRequest):
    """Predictive Search Intent Pre-Fetcher endpoint."""
    from src.domain.predictive_prefetch import predict_next_search_intents
    return predict_next_search_intents(req.active_query, req.retrieved_contexts)


@router.post("/api/rag/entity/cooccurrence")
def entity_cooccurrence_endpoint(req: EntityCooccurrenceRequest):
    """Cross-Document Entity Co-Occurrence Matrix endpoint."""
    from src.domain.entity_cooccurrence import compute_entity_cooccurrence_matrix
    return compute_entity_cooccurrence_matrix(req.documents)


@router.post("/api/rag/distill/export")
def knowledge_distill_export_endpoint(req: KnowledgeDistillRequest):
    """Zero-Cost Knowledge Distillation Dataset Exporter endpoint."""
    from src.domain.knowledge_distiller import export_knowledge_distillation_dataset
    return export_knowledge_distillation_dataset(req.rag_interaction_logs, req.format_type)


@router.post("/api/rag/fact-check/detect-contradictions")
def fact_check_endpoint(req: FactCheckRequest):
    """Semantic Contradiction & Fact-Check endpoint."""
    from src.domain.fact_check_engine import detect_semantic_contradictions
    return detect_semantic_contradictions(req.doc_a_clauses, req.doc_b_clauses)


@router.post("/api/rag/pipeline/ingest-universal")
def universal_pipeline_endpoint(req: UniversalPipelineRequest):
    """Universal Document & Data Format Pipeline endpoint."""
    from src.domain.universal_pipeline import ingest_universal_data_format
    return ingest_universal_data_format(req.raw_content, req.format_type)


@router.post("/api/rag/provenance/track")
def provenance_track_endpoint(req: ProvenanceTrackRequest):
    """Real-Time Data Lineage & Cryptographic Provenance Tracker endpoint."""
    from src.domain.data_provenance_tracker import track_data_provenance
    return track_data_provenance(req.file_path, req.file_content, req.author)


@router.post("/api/rag/consensus/multi-agent")
def multi_agent_consensus_endpoint(req: MultiAgentConsensusRequest):
    """Multi-Agent Reasoning Consensus Orchestrator endpoint."""
    from src.domain.multi_agent_consensus import orchestrate_multi_agent_consensus
    return orchestrate_multi_agent_consensus(req.query, req.retrieved_contexts)


@router.post("/api/rag/vector/drift-audit")
def vector_drift_audit_endpoint(req: VectorDriftAuditRequest):
    """Autonomous Vector Drift & Index Re-Balancing Agent endpoint."""
    from src.domain.vector_drift_agent import audit_vector_index_drift
    return audit_vector_index_drift(req.current_centroids, req.new_embeddings, req.drift_threshold)


@router.post("/api/rag/stream/compress-tokens")
def compress_tokens_endpoint(req: TokenCompressRequest):
    """Streaming Semantic Token Compressor endpoint."""
    from src.domain.streaming_token_compressor import compress_streaming_tokens
    return compress_streaming_tokens(req.text)


@router.get("/api/rag/telemetry/health")
@router.post("/api/rag/telemetry/health")
def system_health_telemetry_endpoint(req: Optional[SystemHealthRequest] = None):
    """Live System Health SLA Telemetry Dashboard API endpoint."""
    from src.domain.system_health_telemetry import compute_system_health_telemetry
    latencies = req.recent_latencies_ms if req else [0.80, 1.10, 1.20]
    hits = req.cache_hits if req else 100
    misses = req.cache_misses if req else 5
    return compute_system_health_telemetry(latencies, hits, misses)


@router.post("/api/rag/code/self-refactor")
def code_self_refactor_endpoint(req: CodeRefactorRequest):
    """Autonomous Code Self-Refactoring & Style Enforcer endpoint."""
    from src.domain.code_self_refactor import analyze_and_propose_refactoring
    return analyze_and_propose_refactoring(req.code_snippet)


@router.post("/api/rag/swarm/decompose")
def swarm_decompose_endpoint(req: SwarmDecomposeRequest):
    """Multi-Agent Task Decomposition & Sub-Task Swarm Manager endpoint."""
    from src.domain.rag_engine import decompose_goal_into_agent_swarm
    return decompose_goal_into_agent_swarm(req.master_goal)


@router.post("/api/rag/code/doc-align")
def code_doc_align_endpoint(req: DocAlignRequest):
    """Semantic Code-Text Alignment & Docstring Harmonizer endpoint."""
    from src.domain.code_doc_aligner import check_code_docstring_alignment
    return check_code_docstring_alignment(req.code_snippet)


@router.post("/api/rag/privacy/zk-mask")
def zk_mask_endpoint(req: ZKMaskRequest):
    """Quantum-Safe Zero-Knowledge Data Masker endpoint."""
    from src.domain.zk_data_masker import mask_payload_with_zk_proof
    return mask_payload_with_zk_proof(req.sensitive_data, req.secret_salt)


@router.post("/api/rag/swarm/execute")
def api_swarm_rag(req: Dict[str, Any] = Body(...)):
    """Cognitive Swarm RAG endpoint (Explorer, Graph, Critic, Synthesizer)."""
    from src.domain.rag_engine import execute_swarm_rag
    query = req.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query string is required")
    return execute_swarm_rag(query)


@router.post("/api/rag/memory/remember")
def api_remember(req: Dict[str, Any] = Body(...)):
    """Agentic Memory store endpoint."""
    from src.domain.agent_memory import remember
    key = req.get("key")
    val = req.get("value")
    if not key or val is None:
        raise HTTPException(status_code=400, detail="key and value are required")
    return remember(key, val, category=req.get("category", "preference"))


@router.get("/api/rag/memory/recall")
def api_recall(key: str, category: Optional[str] = None):
    """Agentic Memory recall endpoint."""
    from src.domain.agent_memory import recall
    return {"key": key, "value": recall(key, category=category)}


@router.get("/api/rag/perception/screen")
def api_screen_perception():
    """Workspace Screen Perception endpoint."""
    from src.domain.screen_perception import capture_screen_context
    return capture_screen_context()


@router.get("/api/rag/contradictions")
def api_contradictions(limit: int = 50):
    """Vault Contradiction & Fact Discrepancy Resolver endpoint."""
    from src.domain.contradiction_resolver import detect_vault_contradictions
    return detect_vault_contradictions(limit=limit)


@router.post("/api/rag/ast/parse")
def api_ast_parse(req: Dict[str, Any] = Body(...)):
    """AST Code-Flow Parser endpoint."""
    from src.domain.ast_parser import parse_python_ast
    code = req.get("code", "")
    filename = req.get("filename", "<api>")
    return parse_python_ast(code, filename=filename)


@router.post("/api/rag/dataset/synthesize")
def api_dataset_synthesize(req: Dict[str, Any] = Body(...)):
    """Vault Instruction Fine-Tuning Dataset Synthesizer endpoint."""
    from src.domain.dataset_synthesizer import generate_vault_instruction_dataset
    return generate_vault_instruction_dataset(limit=req.get("limit", 50))


@router.get("/api/rag/briefing/audio")
def api_audio_briefing():
    """Executive Audio Podcast Script Generator endpoint."""
    from src.domain.audio_briefing import generate_audio_podcast_script
    return generate_audio_podcast_script()


@router.get("/api/rag/architecture/audit")
def api_architecture_doctor(root_dir: str = "src/domain"):
    """Codebase AST Architecture Doctor endpoint."""
    from src.domain.architecture_doctor import audit_codebase_architecture
    return audit_codebase_architecture(root_dir=root_dir)


@router.post("/api/rag/fusion/execute")
def api_fusion_rag(req: Dict[str, Any] = Body(...)):
    """Dual Web & Vault Fusion RAG endpoint."""
    from src.domain.web_rag_fusion import execute_dual_fusion_rag
    query = req.get("query", "")
    return execute_dual_fusion_rag(query, max_local_snippets=req.get("max_local", 3), max_web_results=req.get("max_web", 2))


@router.post("/api/rag/diff/synthesize")
def api_diff_synthesize(req: Dict[str, Any] = Body(...)):
    """Automated Git Diff & Refactoring Patch Synthesizer endpoint."""
    from src.domain.code_diff_synthesizer import generate_refactoring_patch
    orig = req.get("original_code", "")
    mod = req.get("modified_code", "")
    filepath = req.get("filepath", "module.py")
    return generate_refactoring_patch(orig, mod, filepath=filepath)


@router.get("/api/rag/benchmark")
def api_vector_benchmark(num_queries: int = 5, dimension: int = 128):
    """Vector Retrieval Benchmark Harness endpoint."""
    from src.domain.retrieval_benchmark import benchmark_vector_retrieval
    return benchmark_vector_retrieval(num_queries=num_queries, dimension=dimension)


@router.post("/api/rag/entity/resolve")
def api_entity_resolve(req: Dict[str, Any] = Body(...)):
    """Entity Resolver & Alias Merging endpoint."""
    from src.domain.entity_resolver import batch_resolve_entities
    entities = req.get("entities", [])
    return batch_resolve_entities(entities)


@router.post("/api/rag/prompt/optimize")
def api_prompt_optimize(req: Dict[str, Any] = Body(...)):
    """Dynamic Prompt Density Optimizer endpoint."""
    from src.domain.prompt_optimizer import optimize_rag_prompt_density
    query = req.get("query", "")
    chunks = req.get("chunks", [])
    budget = req.get("token_budget", 1000)
    return optimize_rag_prompt_density(query, chunks, token_budget=budget)


@router.post("/api/rag/compliance/inspect")
def api_compliance_inspect(req: Dict[str, Any] = Body(...)):
    """Autonomous Privacy & Compliance Inspector endpoint."""
    from src.domain.compliance_inspector import inspect_privacy_compliance
    text = req.get("text", "")
    return inspect_privacy_compliance(text)


@router.post("/api/rag/visualizer/mermaid")
def api_reasoning_visualizer(req: Dict[str, Any] = Body(...)):
    """Reasoning Graph Visualizer endpoint."""
    from src.domain.reasoning_visualizer import generate_mermaid_reasoning_diagram
    pathways = req.get("pathways", [])
    return generate_mermaid_reasoning_diagram(pathways)


@router.get("/api/rag/scoreboard")
def api_system_scoreboard():
    """Master System Scoreboard Telemetry endpoint."""
    from src.domain.system_scoreboard import generate_system_scoreboard
    return generate_system_scoreboard("src/domain")


@router.post("/api/rag/hypergraph/route")
def api_hypergraph_route(req: Dict[str, Any] = Body(...)):
    """Adaptive Query-Time Hyper-Graph Knowledge Router endpoint."""
    from src.domain.hypergraph_router import route_hypergraph_query
    query = req.get("query", "")
    entities = req.get("target_entities", [])
    return route_hypergraph_query(query, entities)


@router.post("/api/rag/fusion/rerank")
def api_sparse_dense_fusion_rerank(req: Dict[str, Any] = Body(...)):
    """Self-Evolving Sparse-Dense-ColBERT Fusion Reranker endpoint."""
    from src.domain.sparse_dense_fusion import rerank_sparse_dense_fusion
    query = req.get("query", "")
    candidate_chunks = req.get("candidate_chunks", [])
    return rerank_sparse_dense_fusion(query, candidate_chunks)


@router.post("/api/rag/noise/mask-entropy")
def api_mask_entropy_noise(req: Dict[str, Any] = Body(...)):
    """Entropy Differential Noise Masker endpoint."""
    from src.domain.rag_engine import mask_low_entropy_noise
    text_chunk = req.get("text_chunk", "")
    return mask_low_entropy_noise(text_chunk)


@router.post("/api/rag/ann/search")
def api_sublinear_ann_search(req: Dict[str, Any] = Body(...)):
    """Sub-Linear LSH-HNSW Vector Indexer endpoint."""
    from src.domain.sublinear_ann_index import search_sublinear_ann
    query_vec = req.get("query_vec", [])
    index_vecs = req.get("index_vectors", [])
    top_k = req.get("top_k", 5)
    return search_sublinear_ann(query_vec, index_vecs, top_k=top_k)


@router.post("/api/rag/crosslingual/bridge")
def api_crosslingual_bridge(req: Dict[str, Any] = Body(...)):
    """Multilingual Latent Vector Projection Bridge endpoint."""
    from src.domain.rag_engine import project_multilingual_vector
    text = req.get("text", "")
    src_lang = req.get("source_language", "auto")
    return project_multilingual_vector(text, source_language=src_lang)


@router.post("/api/rag/feedback/refine")
def api_feedback_refine(req: Dict[str, Any] = Body(...)):
    """Self-Supervised Retrieval Feedback Auto-Refiner endpoint."""
    from src.domain.retrieval_feedback_refiner import log_feedback_and_refine
    chunk_id = req.get("chunk_id", "chk_0")
    signal = req.get("feedback_signal", "click")
    return log_feedback_and_refine(chunk_id, feedback_signal=signal)
