import pytest
from src.domain.legal_rag_engine import LegalRegulatoryRAGEngine

def test_extract_legal_citations():
    text = (
        "Under 18 U.S.C. § 1030, computer fraud is prohibited. "
        "Additionally, 45 C.F.R. § 164.308 outlines HIPAA security rules, "
        "while Article 5(1)(b) GDPR governs purpose limitation."
    )
    cites = LegalRegulatoryRAGEngine.extract_legal_citations(text)
    
    assert any("18 U.S.C. § 1030" in c for c in cites)
    assert any("45 C.F.R. § 164.308" in c for c in cites)
    assert any("Article 5(1)(b)" in c for c in cites)

def test_chunk_legal_document():
    doc_text = (
        "TITLE 18 - CRIMES AND CRIMINAL PROCEDURE\n"
        "Section 1030 - Fraud in connection with computers.\n"
        "Whoever intentionally accesses a computer without authorization...\n\n"
        "ARTICLE 5 - PRINCIPLES RELATING TO PROCESSING OF PERSONAL DATA\n"
        "Personal data shall be processed lawfully, fairly and in a transparent manner..."
    )
    chunks = LegalRegulatoryRAGEngine.chunk_legal_document(doc_text, file_path="compliance/statutes.txt")
    
    assert len(chunks) >= 2
    assert chunks[0]["file_path"] == "compliance/statutes.txt"
    assert "Section" in chunks[0]["section_header"] or "TITLE" in chunks[0]["section_header"]

def test_classify_regulatory_frameworks():
    sample_gdpr = "Data subject has the right to be forgotten under personal data processing rules."
    frameworks = LegalRegulatoryRAGEngine.classify_regulatory_frameworks(sample_gdpr)
    assert "GDPR" in frameworks

    sample_hipaa = "Business associate agreement protects protected health information PHI."
    frameworks_hipaa = LegalRegulatoryRAGEngine.classify_regulatory_frameworks(sample_hipaa)
    assert "HIPAA" in frameworks_hipaa

def test_format_legal_rag_response():
    chunks = [{
        "chunk_index": 0,
        "file_path": "statutes/privacy.pdf",
        "section_header": "Article 17 GDPR",
        "content": "Right to erasure ('right to be forgotten')",
        "citations": ["Article 17 GDPR"],
        "frameworks": ["GDPR"]
    }]
    resp = LegalRegulatoryRAGEngine.format_legal_rag_response("GDPR erasure right", chunks)
    
    assert resp["status"] == "success"
    assert "Article 17 GDPR" in resp["pinpoint_citations"]
    assert resp["grounded_sources_count"] == 1
