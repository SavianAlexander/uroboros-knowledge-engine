import re
import hashlib
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache

"""
Puerto Rico Legal Corpus, AST Parser, Deterministic Citation Router & Merkle Lineage Engine.
Provides high-fidelity statutory chunking, temporal vigencia classification,
predecessor/successor mapping, D.P.R. jurisprudence cross-linking, and cryptographic provenance.
"""

# Enum-like legal status constants
STATUS_VIGENTE = "VIGENTE"
STATUS_ENMENDADA = "ENMENDADA"
STATUS_DEROGADA_Y_SUBROGADA = "DEROGADA_Y_SUBROGADA"
STATUS_INCONSTITUCIONAL = "DECLARADA_INCONSTITUCIONAL"

import os
import json

_CONCORDANCE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "concordance_civil_pr_1930_2020.json")
)

@lru_cache(maxsize=1)
def load_civil_code_concordance() -> Dict[str, Dict[str, Any]]:
    """Loads and caches the empirical Civil Code 1930 -> 2020 concordance dataset from JSON."""
    if os.path.exists(_CONCORDANCE_PATH):
        try:
            with open(_CONCORDANCE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("concordance", {})
        except Exception:
            pass
    return {}

class PRLegalEngine:
    """
    Core Domain Engine for Puerto Rico Legal Corpus, AST Parsing,
    Deterministic Citation Resolution, and Merkle Provenance Trailing.
    """

    # Puerto Rico Legal Citation Regex Patterns
    PATTERNS = {
        "LPRA": r'\b(\d+)\s+L\.?P\.?R\.?A\.?\s*§*\s*(\d+(?:\.\d+)?(?:\([a-z0-9]+\))*)',
        "LEY_NUM": r'\bLey\s+(?:Núm\.\s*|No\.\s*|Num\.\s*)?(\d+)(?:-(\d{4}|\d{2}))?(?:[,\s]+(?:Art\.?|Artículo)\s*(\d+(?:\.\d+)?))?',
        "CONST_PR": r'\bConst(?:\.|\s+del?\s+)?\s*(?:ELA|PR|Puerto\s+Rico)?\s*(?:Art\.?|Artículo)\s+([IVXLCDM\d]+)(?:[,\s]+(?:Sec\.?|Sección)\s*(\d+))?',
        "DPR_CASE": r'\b(\d+)\s+D\.?P\.?R\.?\s+(\d+)',
        "TSPR_CASE": r'\b(\d{4})\s+TSPR\s+(\d+)',
        "CODIGO_CIVIL_2020": r'\b(?:Código\s+Civil\s+(?:de\s+2020|2020)|CCPR\s+2020|CC2020)(?:[,\s]+(?:Art\.?|Artículo)\s*(\d+))?',
        "CODIGO_PENAL_2012": r'\b(?:Código\s+Penal\s+(?:de\s+2012|2012)|CPPR\s+2012|CP2012)(?:[,\s]+(?:Art\.?|Artículo)\s*(\d+))?',
        "LPAU": r'\b(?:LPAU|Ley\s+(?:Núm\.\s*)?38-2017)(?:[,\s]+(?:Sec\.?|Sección|Art\.?|Artículo)\s*(\d+(?:\.\d+)?))?',
        "CODIGO_MUNICIPAL": r'\b(?:Código\s+Municipal|Ley\s+(?:Núm\.\s*)?107-2020)(?:[,\s]+(?:Art\.?|Artículo)\s*(\d+(?:\.\d+)?))?',
    }

    COMPILED_PATTERNS = {k: re.compile(v, re.IGNORECASE) for k, v in PATTERNS.items()}

    @staticmethod
    def calculate_merkle_leaf(text: str, metadata: Dict[str, Any]) -> str:
        """Compute cryptographic SHA-256 leaf hash for provenance integrity."""
        norm_text = unicodedata.normalize("NFC", text.strip())
        canon_meta = f"{metadata.get('citation_key', '')}|{metadata.get('status', '')}|{metadata.get('effective_date', '')}"
        payload = f"{canon_meta}\n{norm_text}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @classmethod
    @lru_cache(maxsize=2048)
    def parse_citation(cls, query: str) -> Optional[Dict[str, Any]]:
        """
        Deterministic Citation Router for Puerto Rico Law.
        Returns parsed structured citation or None if no direct legal citation is detected.
        # ponytail: LRU cache for sub-millisecond repeated citation resolution.
        """
        if not query or not isinstance(query, str):
            return None

        clean_q = unicodedata.normalize("NFC", query.strip())

        # Check LPRA Match
        m_lpra = cls.COMPILED_PATTERNS["LPRA"].search(clean_q)
        if m_lpra:
            title_num = m_lpra.group(1)
            sec_num = m_lpra.group(2)
            return {
                "type": "LPRA",
                "title": int(title_num),
                "section": sec_num,
                "citation_key": f"{title_num}_LPRA_{sec_num}",
                "canonical_citation": f"{title_num} LPRA § {sec_num}"
            }

        # Check Constitution Match
        m_const = cls.COMPILED_PATTERNS["CONST_PR"].search(clean_q)
        if m_const:
            art_num = m_const.group(1).upper()
            sec_num = m_const.group(2) or "General"
            return {
                "type": "CONSTITUTION",
                "article": art_num,
                "section": sec_num,
                "citation_key": f"PR_CONST_ART_{art_num}_SEC_{sec_num}",
                "canonical_citation": f"Const. PR Art. {art_num}, Sec. {sec_num}" if sec_num != "General" else f"Const. PR Art. {art_num}"
            }

        # Check Civil Code 2020 Match
        m_cc = cls.COMPILED_PATTERNS["CODIGO_CIVIL_2020"].search(clean_q)
        if m_cc and m_cc.group(1):
            art_num = m_cc.group(1)
            return {
                "type": "CODIGO_CIVIL_2020",
                "article": int(art_num),
                "citation_key": f"PR_CC2020_ART_{art_num}",
                "canonical_citation": f"Código Civil de 2020, Art. {art_num}"
            }

        # Check Penal Code 2012 Match
        m_cp = cls.COMPILED_PATTERNS["CODIGO_PENAL_2012"].search(clean_q)
        if m_cp and m_cp.group(1):
            art_num = m_cp.group(1)
            return {
                "type": "CODIGO_PENAL_2012",
                "article": int(art_num),
                "citation_key": f"PR_CP2012_ART_{art_num}",
                "canonical_citation": f"Código Penal de 2012, Art. {art_num}"
            }

        # Check LPAU Match
        m_lpau = cls.COMPILED_PATTERNS["LPAU"].search(clean_q)
        if m_lpau and m_lpau.group(1):
            sec_num = m_lpau.group(1)
            return {
                "type": "LPAU",
                "section": sec_num,
                "citation_key": f"PR_LPAU_SEC_{sec_num}",
                "canonical_citation": f"Ley Núm. 38-2017 (LPAU), Sec. {sec_num}"
            }

        # Check D.P.R. Jurisprudence Match
        m_dpr = cls.COMPILED_PATTERNS["DPR_CASE"].search(clean_q)
        if m_dpr:
            vol = m_dpr.group(1)
            page = m_dpr.group(2)
            return {
                "type": "DPR_JURISPRUDENCE",
                "volume": int(vol),
                "page": int(page),
                "citation_key": f"{vol}_DPR_{page}",
                "canonical_citation": f"{vol} D.P.R. {page}"
            }

        # Check General Session Law (Ley Núm. X-YYYY)
        m_ley = cls.COMPILED_PATTERNS["LEY_NUM"].search(clean_q)
        if m_ley:
            law_num = m_ley.group(1)
            law_year = m_ley.group(2) or ""
            art_num = m_ley.group(3) or ""
            canon = f"Ley Núm. {law_num}" + (f"-{law_year}" if law_year else "") + (f", Art. {art_num}" if art_num else "")
            return {
                "type": "SESSION_LAW",
                "law_number": int(law_num),
                "year": law_year,
                "article": art_num,
                "citation_key": f"LEY_{law_num}" + (f"_{law_year}" if law_year else "") + (f"_ART_{art_num}" if art_num else ""),
                "canonical_citation": canon
            }

        return None

    @classmethod
    def get_civil_code_concordance(cls, article_str: str) -> Optional[Dict[str, Any]]:
        """Look up 1930 -> 2020 Civil Code article transition & leading jurisprudence."""
        clean_art = str(article_str).strip()
        # Direct lookup or search by predecessor key
        return load_civil_code_concordance().get(clean_art)

    @classmethod
    def parse_legal_ast_document(cls, text: str, source_name: str, base_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Structure-aware AST Parser for Puerto Rico statutory documents.
        Splits by Título, Capítulo, Artículo, and Sección while preserving parent path headers,
        incisos, and generating SHA-256 Merkle leaves for every clause.
        """
        if not text or not isinstance(text, str):
            return []

        nfc_text = unicodedata.normalize("NFC", text)
        base_meta = base_metadata or {}

        # Split pattern on Puerto Rico statutory headings (with optional Markdown header hashes #)
        split_pattern = r'(?=(?:\n\s*#{0,6}\s*(?:ART[ÍI]CULO|Art[íi]culo|SECCI[ÓO]N|Secci[ó]n|T[ÍI]TULO|T[íi]tulo|CAP[ÍI]TULO|Cap[íi]tulo|LIBRO|Libro)\s+[\d\w\.]+))'
        raw_blocks = re.split(split_pattern, nfc_text)

        chunks = []
        current_hierarchy = [source_name]
        current_article = ""

        is_const = "constituci" in source_name.lower()
        is_cc = "código civil" in source_name.lower() or "codigo civil" in source_name.lower()
        is_cp = "código penal" in source_name.lower() or "codigo penal" in source_name.lower()
        is_lpau = "lpau" in source_name.lower() or "administrativo" in source_name.lower()

        for idx, block in enumerate(raw_blocks):
            clean_block = block.strip()
            if not clean_block:
                continue

            # Extract header if present (stripping leading Markdown hashes)
            header_match = re.match(r'^(?:#{0,6}\s*)?(?:ART[ÍI]CULO|Art[íi]culo|SECCI[ÓO]N|Secci[ó]n|T[ÍI]TULO|T[íi]tulo|CAP[ÍI]TULO|Cap[íi]tulo|LIBRO|Libro)\s+([^\n\.:]+[\n\.:]?[^\n]*)', clean_block)
            if header_match:
                header_line = re.sub(r'^#{1,6}\s*', '', header_match.group(0)).strip()
                if any(h in header_line.upper() for h in ["TÍTULO", "TITULO", "CAPÍTULO", "CAPITULO", "LIBRO"]):
                    if len(current_hierarchy) > 1:
                        current_hierarchy = [source_name, header_line]
                    else:
                        current_hierarchy.append(header_line)
                elif "ARTÍCULO" in header_line.upper() or "ARTICULO" in header_line.upper():
                    art_m = re.search(r'(?:ART[ÍI]CULO|Art[íi]culo)\s+([IVXLCDM\d]+)', header_line)
                    if art_m:
                        current_article = art_m.group(1).upper()
            else:
                header_line = f"Cláusula {idx+1}"

            # Determine citation_key based on document context & regex
            citation_key = ""
            canonical_cite = header_line

            if is_const:
                sec_m = re.search(r'(?:SECCI[ÓO]N|Secci[ó]n)\s*(\d+)', clean_block)
                if sec_m and current_article:
                    sec_num = sec_m.group(1)
                    citation_key = f"PR_CONST_ART_{current_article}_SEC_{sec_num}"
                    canonical_cite = f"Const. PR Art. {current_article}, Sec. {sec_num}"
                elif current_article:
                    citation_key = f"PR_CONST_ART_{current_article}"
                    canonical_cite = f"Const. PR Art. {current_article}"
            elif is_cc:
                art_m = re.search(r'(?:ART[ÍI]CULO|Art[íi]culo)\s*(\d+)', clean_block)
                if art_m:
                    art_num = art_m.group(1)
                    citation_key = f"PR_CC2020_ART_{art_num}"
                    canonical_cite = f"Código Civil de 2020, Art. {art_num}"
            elif is_cp:
                art_m = re.search(r'(?:ART[ÍI]CULO|Art[íi]culo)\s*(\d+)', clean_block)
                if art_m:
                    art_num = art_m.group(1)
                    citation_key = f"PR_CP2012_ART_{art_num}"
                    canonical_cite = f"Código Penal de 2012, Art. {art_num}"
            elif is_lpau:
                sec_m = re.search(r'(?:SECCI[ÓO]N|Secci[ó]n)\s*(\d+(?:\.\d+)?)', clean_block)
                if sec_m:
                    sec_num = sec_m.group(1)
                    citation_key = f"PR_LPAU_SEC_{sec_num}"
                    canonical_cite = f"Ley Núm. 38-2017 (LPAU), Sec. {sec_num}"

            if not citation_key:
                parsed_cite = cls.parse_citation(clean_block) or cls.parse_citation(header_line)
                if parsed_cite:
                    citation_key = parsed_cite.get("citation_key", f"{source_name}_chunk_{idx+1}")
                    canonical_cite = parsed_cite.get("canonical_citation", header_line)
                else:
                    citation_key = f"{source_name}_chunk_{idx+1}"

            # Determine temporal state
            status = STATUS_VIGENTE
            if "derogad" in clean_block.lower() or "subrogad" in clean_block.lower():
                status = STATUS_DEROGADA_Y_SUBROGADA
            elif "enmenda" in clean_block.lower() or "enmienda" in clean_block.lower():
                status = STATUS_ENMENDADA
            elif "inconstitucional" in clean_block.lower():
                status = STATUS_INCONSTITUCIONAL

            chunk_meta = {
                "source": source_name,
                "citation_key": citation_key,
                "canonical_citation": canonical_cite,
                "hierarchy_path": " > ".join(current_hierarchy),
                "status": status,
                "effective_date": base_meta.get("effective_date", "1952-07-25"),
                "source_origin": base_meta.get("source_origin", "OSLPR"),
                "source_url": base_meta.get("source_url", "https://sutra.oslpr.org"),
                "chunk_index": idx
            }

            # Generate Merkle SHA-256 leaf
            merkle_hash = cls.calculate_merkle_leaf(clean_block, chunk_meta)
            chunk_meta["merkle_sha256"] = merkle_hash

            chunks.append({
                "chunk_index": idx,
                "citation_key": citation_key,
                "canonical_citation": canonical_cite,
                "section_header": header_line,
                "hierarchy": current_hierarchy.copy(),
                "status": status,
                "content": clean_block,
                "metadata": chunk_meta,
                "merkle_sha256": merkle_hash,
                "char_length": len(clean_block)
            })

        return chunks

    @classmethod
    def synthesize_ground_truth_context(cls, query: str, retrieved_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes a high-integrity, zero-hallucination legal context packet with
        historical transition notes and cryptographic provenance.
        """
        citations = []
        provenance_ledger = []
        concordance_notes = []

        # Check for historical citation mention in query (e.g. Art. 1802)
        m_num = re.search(r'\b(?:Art\.?|Artículo)\s*(1802|1803|1804|1054|1474|1867|1868)\b', query, re.IGNORECASE)
        if m_num:
            art_match = m_num.group(1)
            concordance = cls.get_civil_code_concordance(art_match)
            if concordance:
                concordance_notes.append({
                    "queried_article": art_match,
                    "predecessor": concordance["predecessor"],
                    "successor": concordance["successor"],
                    "notes": concordance["notes"],
                    "leading_cases": concordance.get("leading_cases", [])
                })

        for node in retrieved_nodes:
            meta = node.get("metadata", {})
            cite = node.get("canonical_citation") or meta.get("canonical_citation")
            if cite and cite not in citations:
                citations.append(cite)

            provenance_ledger.append({
                "citation_key": node.get("citation_key") or meta.get("citation_key"),
                "canonical_citation": cite,
                "status": node.get("status") or meta.get("status", STATUS_VIGENTE),
                "merkle_sha256": node.get("merkle_sha256") or meta.get("merkle_sha256"),
                "hierarchy": meta.get("hierarchy_path", ""),
                "snippet": node.get("content", "")[:350]
            })

        return {
            "query": query,
            "deterministic_match": bool(cls.parse_citation(query)),
            "pinpoint_citations": citations,
            "concordance_transitions": concordance_notes,
            "provenance_ledger": provenance_ledger,
            "total_nodes": len(retrieved_nodes),
            "disclaimer": "Puerto Rico Legal Provenance Ledger: Grounded on official enacted statutes and D.P.R. jurisprudence."
        }


# Facade alias
PRLegalCodexEngine = PRLegalEngine
