import pytest
from src.domain.legal_accuracy_engine import LegalAccuracyEngine

def test_unicode_nfc_normalization():
    # Test decomposed vs composed Unicode character equivalence
    decomposed = "caf\u0065\u0301"  # e + combining acute accent
    composed = "caf\u00e9"          # é composed
    
    norm_dec = LegalAccuracyEngine.normalize_text_nfc(decomposed)
    norm_comp = LegalAccuracyEngine.normalize_text_nfc(composed)
    
    assert norm_dec == norm_comp
    assert norm_dec == "café"

def test_sha256_integrity_verification():
    import hashlib
    content = "Legal Contract Text Integrity Test"
    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    assert LegalAccuracyEngine.verify_sha256_integrity(content, expected_hash)
    assert not LegalAccuracyEngine.verify_sha256_integrity(content + "tampered", expected_hash)

def test_fts5_legal_sanitization():
    query = "contract AND 'breach' OR (damages*)"
    sanitized = LegalAccuracyEngine.sanitize_fts5_query_legal(query)
    
    assert '"contract"' in sanitized
    assert '"breach"' in sanitized
    assert '"damages"' in sanitized
    assert "AND" in sanitized

def test_exact_cosine_similarity_bounds():
    vec_a = [1.0, 2.0, 3.0]
    vec_b = [1.0, 2.0, 3.0]
    
    sim = LegalAccuracyEngine.calculate_exact_cosine_similarity(vec_a, vec_b)
    assert abs(sim - 1.0) < 1e-9

    vec_c = [-1.0, -2.0, -3.0]
    sim_opposite = LegalAccuracyEngine.calculate_exact_cosine_similarity(vec_a, vec_c)
    assert abs(sim_opposite - (-1.0)) < 1e-9

def test_strict_payload_validation():
    payload = {"title": "Contract Agreement", "filepath": "docs/contract.pdf"}
    valid, msg = LegalAccuracyEngine.validate_api_payload_strict(payload, ["title", "filepath"])
    assert valid
    assert msg == "Valid"

    invalid_payload = {"title": "Contract Agreement"}
    valid, msg = LegalAccuracyEngine.validate_api_payload_strict(invalid_payload, ["title", "filepath"])
    assert not valid
    assert "Missing required legal field: 'filepath'" in msg
