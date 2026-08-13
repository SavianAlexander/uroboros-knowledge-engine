import re
import unicodedata
from typing import List, Dict, Any, Tuple

class LegalRegulatoryRAGEngine:
    """
    Dedicated Legal & Regulatory RAG Engine.
    Provides section-aware statutory chunking, regex clause citation parsing,
    pin-point citation grounding, and regulatory framework risk classification.
    """

    CITATION_PATTERNS = [
        r'\b\d+\s+U\.S\.C\.\s+§+\s*\d+(?:\([a-z0-9]+\))*',       # U.S. Code (e.g. 18 U.S.C. § 1030)
        r'\b\d+\s+C\.F\.R\.\s+§+\s*\d+(?:\.\d+)?',              # Code of Federal Regs (e.g. 45 CFR § 164.308)
        r'\bArticle\s+\d+(?:\(\d+\))*(?:\([a-z]\))*',            # Statutory Articles (e.g. Article 5(1)(b) GDPR)
        r'\bFAR\s+\d+\.\d+(?:-\d+)?',                            # Federal Acquisition Regs (e.g. FAR 52.204-21)
        r'\bSection\s+\d+(?:\.\d+)*(?:\([a-z0-9]+\))*',          # Statutory Sections (e.g. Section 404(a))
        r'\b§+\s*\d+(?:\.\d+)*(?:\([a-z0-9]+\))*',              # Section symbol § (e.g. § 12.3)
    ]

    COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CITATION_PATTERNS]

    FRAMEWORKS = {
        "GDPR": [r"gdpr", r"data protection", r"data subject", r"right to be forgotten", r"personal data"],
        "HIPAA": [r"hipaa", r"phi", r"protected health information", r"business associate"],
        "SOC2": [r"soc 2", r"trust services criteria", r"security", r"availability", r"confidentiality"],
        "FAR_DFARS": [r"far\s+\d+", r"dfars", r"federal acquisition", r"defense federal"],
        "EU_AI_ACT": [r"eu ai act", r"high-risk ai", r"conformity assessment", r"transparency obligation"]
    }

    COMPILED_FRAMEWORKS = {
        name: re.compile(r'|'.join(patterns), re.IGNORECASE)
        for name, patterns in FRAMEWORKS.items()
    }

    @classmethod
    def extract_legal_citations(cls, text: str) -> List[str]:
        """Extract explicit statutory & regulatory clause citations from text with zero recompilation overhead."""
        if not text:
            return []
        
        nfc_text = unicodedata.normalize("NFC", text)
        citations = []
        for compiled_re in cls.COMPILED_PATTERNS:
            matches = compiled_re.findall(nfc_text)
            for m in matches:
                if m not in citations:
                    citations.append(m)
        return citations

    @classmethod
    def chunk_legal_document(cls, text: str, file_path: str = "") -> List[Dict[str, Any]]:
        """
        Hierarchical Regulatory Structure Chunking.
        Splits legal texts at Title, Section (§), and Article boundaries to preserve statutory context.
        """
        if not text:
            return []

        nfc_text = unicodedata.normalize("NFC", text)
        # Split on Section symbol § or Section / Article headers
        split_pattern = r'(?=(?:\n\s*(?:SECTION|Section|§|ARTICLE|Article|TITLE|Title)\s+\d+))'
        raw_sections = re.split(split_pattern, nfc_text)

        chunks = []
        for idx, sec in enumerate(raw_sections):
            sec_text = sec.strip()
            if not sec_text:
                continue

            cites = cls.extract_legal_citations(sec_text)
            frameworks = cls.classify_regulatory_frameworks(sec_text)
            
            # Extract section title header if present
            header_match = re.search(r'^(?:SECTION|Section|§|ARTICLE|Article|TITLE|Title)\s+[\d\.\(\)\w]+[^\n]*', sec_text)
            section_header = header_match.group(0).strip() if header_match else f"Section Chunk {idx+1}"

            chunks.append({
                "chunk_index": idx,
                "file_path": file_path,
                "section_header": section_header,
                "content": sec_text,
                "citations": cites,
                "frameworks": frameworks,
                "char_length": len(sec_text)
            })

        return chunks

    @classmethod
    def classify_regulatory_frameworks(cls, text: str) -> List[str]:
        """Classify text against major compliance frameworks (GDPR, HIPAA, SOC 2, FAR, EU AI Act)."""
        if not text:
            return []
        detected = []
        for name, compiled_re in cls.COMPILED_FRAMEWORKS.items():
            if compiled_re.search(text):
                detected.append(name)
        return detected

    @classmethod
    def format_legal_rag_response(cls, query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assemble pin-point legal RAG response with mandatory citation grounding matrix.
        """
        if not chunks or not isinstance(chunks, list):
            return {
                "status": "empty",
                "query": str(query or ""),
                "pinpoint_citations": [],
                "grounded_sources_count": 0,
                "sources": [],
                "legal_disclaimer": "This RAG response provides statutory citation mapping for regulatory analysis purposes."
            }

        all_citations = []
        grounded_sources = []
        valid_chunks = [c for c in chunks if isinstance(c, dict)]

        for c in valid_chunks:
            cites = c.get("citations", [])
            for cite in cites:
                if cite not in all_citations:
                    all_citations.append(cite)
            
            grounded_sources.append({
                "file": c.get("file_path", "Legal Document"),
                "section": c.get("section_header", "Clause"),
                "citations": cites,
                "frameworks": c.get("frameworks", []),
                "snippet": c.get("content", "")[:300] + "..."
            })

        return {
            "status": "success",
            "query": query,
            "pinpoint_citations": all_citations,
            "grounded_sources_count": len(grounded_sources),
            "sources": grounded_sources,
            "legal_disclaimer": "This RAG response provides statutory citation mapping for regulatory analysis purposes."
        }

    @classmethod
    def get_legal_rag_capabilities(cls) -> Dict[str, Any]:
        """Returns compliance framework capabilities and supported citation standards."""
        return {
            "engine_name": "Uroboros Legal & Regulatory RAG Engine",
            "supported_frameworks": list(cls.FRAMEWORKS.keys()),
            "citation_patterns_count": len(cls.CITATION_PATTERNS),
            "hierarchical_statutory_chunking": True,
            "status": "active"
        }
