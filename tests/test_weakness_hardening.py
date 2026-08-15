"""
Comprehensive Verification Suite for System Weakness Hardening & Architectural Upgrades:
1. Aho-Corasick Multi-Pattern Automaton in graph_link_synthesizer.py
2. Binary ColBERT MaxSim memoization & batch execution in binary_colbert.py
3. Multi-standard PII & secret compliance inspection in compliance_inspector.py
4. Multimodal HTML/Markdown table parsing & Ollama vision payload in multimodal_ocr_parser.py
5. Dynamic token density budgeting in prompt_optimizer.py
6. Cross-document contradiction & numerical collision matrix in contradiction_resolver.py
"""
import pytest
from src.domain.graph_link_synthesizer import (
    AhoCorasickAutomaton,
    auto_synthesize_wikilinks
)
from src.domain.binary_colbert import (
    binary_colbert_maxsim,
    batch_binary_colbert_maxsim,
    text_to_token_bitpacks,
    rerank_search_results_colbert
)
from src.domain.compliance_inspector import inspect_privacy_compliance
from src.domain.multimodal_ocr_parser import (
    parse_markdown_tables,
    parse_html_tables,
    parse_multimodal_document_layout,
    prepare_vision_model_payload
)
from src.domain.prompt_optimizer import (
    estimate_text_tokens,
    optimize_rag_prompt_density
)
from src.domain.contradiction_resolver import detect_text_pair_contradictions


# ============================================================================
# 1. Aho-Corasick Multi-Pattern Automaton Tests
# ============================================================================

def test_ahocorasick_basic_and_nested_matches():
    patterns = ["Quantum", "Quantum Computing", "Machine Learning", "Neural Network"]
    automaton = AhoCorasickAutomaton(patterns)
    text = "Exploring Quantum Computing and Machine Learning paradigms."
    matches = automaton.search_in_text(text)
    
    assert len(matches) >= 2
    matched_titles = [m[2] for m in matches]
    assert "Quantum Computing" in matched_titles
    assert "Machine Learning" in matched_titles


def test_auto_synthesize_wikilinks_ahocorasick():
    titles = ["SQLite", "WAL Mode", "FastAPI", "Full-Text Search"]
    text = "We configure SQLite with WAL Mode and use FastAPI for APIs."
    res = auto_synthesize_wikilinks(text, titles)
    
    assert res["status"] == "success"
    assert res["links_added"] >= 2
    assert "[[SQLite]]" in res["synthesized_text"]
    assert "[[WAL Mode]]" in res["synthesized_text"]
    assert "[[FastAPI]]" in res["synthesized_text"]


def test_auto_synthesize_wikilinks_no_double_linking():
    titles = ["SQLite", "FastAPI"]
    text = "Already linked [[SQLite]] and unlinked FastAPI."
    res = auto_synthesize_wikilinks(text, titles)
    
    assert res["status"] == "success"
    assert res["links_added"] == 1
    assert res["synthesized_text"] == "Already linked [[SQLite]] and unlinked [[FastAPI]]."


def test_auto_synthesize_ahocorasick_large_scale():
    # 500 synthetic concept titles
    titles = [f"Concept_{i}" for i in range(500)]
    titles.append("Critical Engine Architecture")
    text = "This document discusses Concept_42, Concept_128, and Critical Engine Architecture in detail."
    res = auto_synthesize_wikilinks(text, titles)
    
    assert res["status"] == "success"
    assert res["links_added"] == 3
    assert "[[Concept_42]]" in res["synthesized_text"]
    assert "[[Concept_128]]" in res["synthesized_text"]
    assert "[[Critical Engine Architecture]]" in res["synthesized_text"]


# ============================================================================
# 2. Binary ColBERT MaxSim Tests
# ============================================================================

def test_binary_colbert_memoized_scoring():
    q_tokens = [[0.5, -0.2, 0.1] * 22]
    d_tokens_1 = [[0.4, -0.1, 0.2] * 22]
    d_tokens_2 = [[-0.5, 0.2, -0.1] * 22]
    
    score_1 = binary_colbert_maxsim(q_tokens, d_tokens_1)
    score_2 = binary_colbert_maxsim(q_tokens, d_tokens_2)
    assert score_1 > score_2


def test_batch_binary_colbert_maxsim():
    q_bitpacks = text_to_token_bitpacks("distributed consensus raft")
    d1 = text_to_token_bitpacks("raft consensus algorithm in distributed systems")
    d2 = text_to_token_bitpacks("unrelated chocolate dessert recipe")
    
    scores = batch_binary_colbert_maxsim(q_bitpacks, [d1, d2])
    assert len(scores) == 2
    assert scores[0] > scores[1]


# ============================================================================
# 3. Privacy & Compliance Inspector Tests
# ============================================================================

def test_compliance_inspector_comprehensive_pii():
    mock_jwt = "Bearer " + "eyJ" + "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + "eyJ" + "zdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThisToken. "
    sample_text = (
        "User email: dev@example.com, SSN: 123-45-6789, Phone: (555) 234-5678. "
        f"{mock_jwt}"
        "API Key: aiod_12345678901234567890123456789012."
    )
    res = inspect_privacy_compliance(sample_text)
    assert res["status"] == "privacy_risk"
    assert res["risk_score"] >= 0.8
    assert res["total_violations"] >= 4
    
    masked = res["masked_text"]
    assert "[REDACTED_EMAIL]" in masked
    assert "[REDACTED_SSN]" in masked
    assert "[REDACTED_PHONE]" in masked
    assert "[REDACTED_JWT_TOKEN]" in masked
    assert "[REDACTED_API_KEY]" in masked


def test_compliance_inspector_private_key():
    key_text = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0Y1234567890abcdefghijklmnopqrstuvwxyz\n"
        "-----END RSA PRIVATE KEY-----"
    )
    res = inspect_privacy_compliance(key_text)
    assert res["status"] == "privacy_risk"
    assert "[REDACTED_PRIVATE_KEY]" in res["masked_text"]


# ============================================================================
# 4. Multimodal Layout & Vision Parser Tests
# ============================================================================

def test_multimodal_html_table_parsing():
    html = """
    <table>
        <tr><th>Metric</th><th>Latency</th></tr>
        <tr><td>FTS5</td><td>1.2ms</td></tr>
        <tr><td>ColBERT</td><td>4.5ms</td></tr>
    </table>
    """
    tables = parse_html_tables(html)
    assert len(tables) == 1
    assert tables[0]["row_count"] == 2
    assert tables[0]["headers"] == ["Metric", "Latency"]
    assert tables[0]["rows"][0]["Metric"] == "FTS5"
    assert tables[0]["rows"][0]["Latency"] == "1.2ms"


def test_prepare_vision_model_payload():
    b64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    payload = prepare_vision_model_payload(b64_img, prompt="Transcribe table", model="qwen2-vl:7b")
    assert payload["model"] == "qwen2-vl:7b"
    assert payload["prompt"] == "Transcribe table"
    assert len(payload["images"]) == 1
    assert not payload["images"][0].startswith("data:image")


# ============================================================================
# 5. Dynamic Token Density Budgeting Tests
# ============================================================================

def test_estimate_text_tokens_content_types():
    code_text = "def calculate_matrix(a, b):\n    return [x * y for x, y in zip(a, b)]"
    prose_text = "This is a simple natural language paragraph explaining the algorithm."
    cjk_text = "这是一个关于知识库搜索引擎的说明文档。"
    
    t_code = estimate_text_tokens(code_text)
    t_prose = estimate_text_tokens(prose_text)
    t_cjk = estimate_text_tokens(cjk_text)
    
    assert t_code > 0
    assert t_prose > 0
    assert t_cjk > 0


def test_optimize_rag_prompt_density_budgeting():
    chunks = [
        "High performance SQLite WAL configuration with connection pooling.",
        "Detailed recipe for baking chocolate brownies with walnuts.",
        "SQLite indexing techniques using FTS5 virtual tables and BM25 ranking."
    ]
    res = optimize_rag_prompt_density("SQLite indexing performance", chunks, token_budget=50)
    assert res["status"] == "success"
    assert res["selected_chunk_count"] >= 1
    assert "SQLite" in res["optimized_prompt"]
    assert res["estimated_tokens_used"] <= 60


# ============================================================================
# 6. Contradiction & Claim Collision Tests
# ============================================================================

def test_detect_text_pair_contradictions_negation():
    doc_a = "The authentication service supports SAML SSO integration."
    doc_b = "The authentication service is deprecated and unsupported for SAML SSO."
    discrepancies = detect_text_pair_contradictions(doc_a, doc_b, "doc_a", "doc_b")
    
    assert len(discrepancies) >= 1
    types = [d["discrepancy_type"] for d in discrepancies]
    assert "negation_conflict" in types


def test_detect_text_pair_contradictions_numerical():
    doc_a = "System throughput benchmark is capped at 500 req/s under load."
    doc_b = "System throughput benchmark achieves 5000 req/s under heavy load."
    discrepancies = detect_text_pair_contradictions(doc_a, doc_b, "doc_a", "doc_b")
    
    assert len(discrepancies) >= 1
    types = [d["discrepancy_type"] for d in discrepancies]
    assert "numerical_mismatch" in types
