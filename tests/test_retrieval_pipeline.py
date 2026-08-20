"""
Unit and integration tests for Composable Retrieval Pipeline DAG and Typed Exception Hierarchy.
"""
import pytest
from src.core.retrieval_pipeline import (
    SearchQuery,
    SearchCandidate,
    SearchContext,
    RetrievalPipeline,
    FTS5KeywordStage,
    DenseVectorStage,
    RRFScoreFusionStage,
    ColBERTRerankStage,
    RecencyDecayStage,
    SourceCitationStage,
    create_standard_hybrid_pipeline
)
from src.shared.exceptions import (
    UroborosError,
    DocumentNotFoundError,
    QueryValidationError,
    DatabaseLockedError,
    SearchIndexError
)
from src.domain.query_intent import classify_query_intent, bandit_select_pipeline
from src.domain.reranking import compute_rrf_scores, binary_colbert_maxsim, explain_candidate_score
from src.domain.graph_engine import find_multihop_pathways, export_graph_to_graphml
from src.domain.verification_guards import verify_claims_and_consensus, evaluate_boundary_invariants


import unittest


class TestRetrievalPipeline(unittest.TestCase):
    def test_typed_exceptions_hierarchy(self):
        err = DocumentNotFoundError("Document 'test.md' was not found in vault")
        assert err.status_code == 404
        assert err.error_code == "DOCUMENT_NOT_FOUND"
        assert "test.md" in err.message
        d = err.to_dict()
        assert d["status"] == "error"
        assert d["error_code"] == "DOCUMENT_NOT_FOUND"

        val_err = QueryValidationError("Query contains invalid wildcard")
        assert val_err.status_code == 400
        assert val_err.error_code == "INVALID_QUERY_SYNTAX"

        db_err = DatabaseLockedError("Database write locked")
        assert db_err.status_code == 503
        assert db_err.error_code == "DATABASE_LOCKED_BUSY"


    def test_retrieval_pipeline_creation_and_execution(self):
        pipeline = create_standard_hybrid_pipeline()
        assert len(pipeline.stages) >= 4

        query = SearchQuery(raw_query="knowledge graph architecture", top_k=5, rrf_k=60)
        ctx = pipeline.execute(query)

        assert isinstance(ctx, SearchContext)
        assert ctx.total_latency_ms >= 0.0
        assert "fts5_keyword" in ctx.stage_metrics
        assert "dense_vector" in ctx.stage_metrics
        assert "rrf_score_fusion" in ctx.stage_metrics


    def test_rrf_score_fusion_stage(self):
        c1 = SearchCandidate(id=1, filepath="doc1.md", filename="doc1.md", content="Knowledge graph neural sync", fts_rank=1)
        c2 = SearchCandidate(id=2, filepath="doc2.md", filename="doc2.md", content="Distributed consensus protocol", vector_rank=1)

        ctx = SearchContext(query=SearchQuery(raw_query="neural consensus", top_k=10, rrf_k=60))
        ctx.fts_candidates = [c1]
        ctx.vector_candidates = [c2]

        stage = RRFScoreFusionStage(k=60)
        ctx = stage.process(ctx)

        assert len(ctx.candidates) == 2
        assert ctx.candidates[0].score > 0.0
        assert ctx.candidates[1].score > 0.0


    def test_source_citation_stage(self):
        c = SearchCandidate(
            id=1,
            filepath="guide.md",
            filename="guide.md",
            content="This is the introduction.\nKnowledge base retrieval systems require indexing.\nFinal conclusion."
        )
        ctx = SearchContext(query=SearchQuery(raw_query="retrieval systems", top_k=5))
        ctx.candidates = [c]

        stage = SourceCitationStage()
        ctx = stage.process(ctx)

        assert len(ctx.candidates[0].citations) >= 1
        assert ctx.candidates[0].citations[0]["line_number"] == 2
        assert "retrieval systems" in ctx.candidates[0].citations[0]["text"]


    def test_consolidated_query_intent_engine(self):
        res = classify_query_intent("def compute_rrf_scores(vector, fts):")
        assert res["status"] == "success"
        assert res["intent"] == "code_search"

        res_math = classify_query_intent("quarterly revenue profit table")
        assert res_math["status"] == "success"
        assert res_math["intent"] == "tabular_math"


    def test_consolidated_reranking_engine(self):
        vec_results = [{"id": "1", "filename": "doc1.md", "score": 0.95}]
        fts_results = [{"id": "2", "filename": "doc2.md", "score": -1.5}]
        fused = compute_rrf_scores(vec_results, fts_results, k=60)
        assert len(fused) == 2
        assert "rrf_score" in fused[0]

        q_tokens = [[0.5, -0.2, 0.8, -0.1]]
        d_tokens = [[0.5, -0.2, 0.8, -0.1], [-0.5, 0.2, -0.8, 0.1]]
        maxsim = binary_colbert_maxsim(q_tokens, d_tokens)
        assert maxsim > 0.0

        explanation = explain_candidate_score({"filename": "report.md", "fts_rank": 2, "pagerank_score": 0.05, "final_score": 0.08})
        assert explanation["status"] == "success"
        assert "report.md" in explanation["explanation"]


    def test_consolidated_graph_engine(self):
        graph_data = {
            "nodes": [{"id": "n1", "name": "Node A", "type": "doc", "group": 1}],
            "edges": [{"source": "n1", "target": "n2", "relation": "links", "weight": 2}]
        }
        graphml_xml = export_graph_to_graphml(graph_data)
        assert "<graphml" in graphml_xml
        assert 'id="n1"' in graphml_xml


    def test_consolidated_verification_guards(self):
        text = "The optical fiber transmits data at 450000 km/s across transatlantic routes."
        res = verify_claims_and_consensus(text)
        assert res["status"] == "success"
        assert "boundary_verification" in res


    def test_rag_query_cache_etag(self):
        from src.core.rag_query_cache import get_db_data_version, generate_query_etag
        v = get_db_data_version()
        assert isinstance(v, int)
        etag1 = generate_query_etag("distributed indexing", version=1)
        etag2 = generate_query_etag("distributed indexing", version=2)
        etag1_dup = generate_query_etag("distributed indexing", version=1)
        assert etag1 == etag1_dup
        assert etag1 != etag2
        assert len(etag1) == 16


    def test_typed_sse_events(self):
        from src.domain.sse_sync_stream import (
            format_rag_metadata_event,
            format_rag_delta_event,
            format_rag_finish_event
        )
        meta = format_rag_metadata_event("qwen2.5:7b", [{"doc_id": 1, "lines": [1, 5]}], prompt_tokens=150)
        assert "event: metadata" in meta
        assert "qwen2.5:7b" in meta

        delta = format_rag_delta_event(" neural", index=0)
        assert "event: delta" in delta
        assert "neural" in delta

        fin = format_rag_finish_event(total_tokens=42, latency_ms=125.4)
        assert "event: finish" in fin
        assert "125.4" in fin


    def test_database_self_healing(self):
        from src.domain.knowledge_self_healing import execute_database_self_healing
        res = execute_database_self_healing()
        assert res["status"] == "success"
        assert "database_health" in res
        assert "purged_orphan_chunks" in res


    def test_fre_902_merkle_certificate(self):
        from src.domain.vault_merkle_tree import generate_fre_902_certificate
        cert = generate_fre_902_certificate("nonexistent_test_doc.md")
        assert cert["status"] in ["not_found", "success"]


    def test_polyglot_ast_extraction(self):
        from src.domain.code_ast_extractor import extract_code_structure
        ts_code = """
        export interface UserProfile { id: string; name: string; }
        export async function fetchProfile(id: string) { return id; }
        const calculateScore = (x: number) => x * 2;
        """
        res = extract_code_structure(ts_code, filename="service.ts")
        assert res["status"] == "success"
        assert res["language"] == "typescript"
        fn_names = [f["name"] for f in res["functions"]]
        assert "fetchProfile" in fn_names
        assert "calculateScore" in fn_names
        assert any(c["name"] == "UserProfile" for c in res["classes"])


    def test_agent_episodic_scratchpad(self):
        from src.domain.agent_scratchpad import store_memory, recall_memory, list_session_memories
        session_id = "test_session_42"
        store_memory(session_id, "current_plan", {"step": 1, "action": "index_files"}, tags=["rag", "planner"])
        val = recall_memory(session_id, "current_plan")
        assert val is not None
        assert val["step"] == 1
        mems = list_session_memories(session_id)
        assert len(mems) >= 1
        assert any(m["key"] == "current_plan" for m in mems)


    def test_service_catalog_registry(self):
        from src.core.router_registry import get_service_catalog
        catalog = get_service_catalog()
        assert isinstance(catalog, list)
        assert len(catalog) > 0
        paths = [c["path"] for c in catalog]
        assert "/health" in paths or any("/api/" in p for p in paths)
