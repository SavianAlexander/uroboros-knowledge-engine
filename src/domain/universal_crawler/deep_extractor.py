import re
import json
import unicodedata
from typing import List, Dict, Any, Tuple, Optional, Set

"""
Deep Multi-Modal Knowledge Harvester & Entity Triplet Extractor.
Extracts:
1. Structured Table Reconstructions (HTML/PDF tables to Markdown & JSON)
2. Named Entities (Statutory Citations, Dates, Agencies, People, Penalties, Monetary)
3. RDF-Style Relationship Triplets (Subject -> Predicate -> Object)
4. Unified Multi-Schema Metadata (JSON-LD, Dublin Core, OpenGraph)
"""

class TableStructureReconstructor:
    """Extracts and formats tables from HTML/text into clean Markdown and structured JSON."""

    @staticmethod
    def extract_html_tables(html: str) -> List[Dict[str, Any]]:
        """Extract all <table> structures into Markdown and row-column matrices."""
        tables = []
        if not html:
            return tables

        table_matches = re.findall(r'<table[^>]*>(.*?)</table>', html, re.I | re.DOTALL)
        for t_idx, t_html in enumerate(table_matches, start=1):
            rows_data = []
            row_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', t_html, re.I | re.DOTALL)
            for r_html in row_matches:
                cols = re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', r_html, re.I | re.DOTALL)
                clean_cols = [re.sub(r'<[^>]+>', '', c).replace('&nbsp;', ' ').strip() for c in cols]
                if any(clean_cols):
                    rows_data.append(clean_cols)

            if rows_data:
                # Format as Markdown Table
                max_cols = max(len(r) for r in rows_data)
                padded_rows = [r + [''] * (max_cols - len(r)) for r in rows_data]
                header = padded_rows[0]
                md_table = "| " + " | ".join(header) + " |\n"
                md_table += "| " + " | ".join(["---"] * max_cols) + " |\n"
                for r in padded_rows[1:]:
                    md_table += "| " + " | ".join(r) + " |\n"

                tables.append({
                    "table_index": t_idx,
                    "row_count": len(padded_rows),
                    "column_count": max_cols,
                    "markdown": md_table,
                    "matrix": padded_rows
                })

        return tables

class EntityKnowledgeGraphExtractor:
    """Extracts high-value domain entities and RDF triplets (Subject -> Predicate -> Object)."""

    # Citation patterns (Statutes, Codes, Rules, D.P.R. jurisprudence)
    PATTERNS = {
        "leyes": r'(?:Ley\s+(?:N[úu]m\.?\s*)?(\d+[-–]\d{4}|\d+))',
        "articulos": r'(?:Art[íi]culo\s+([\d\w\.\-]+))',
        "secciones": r'(?:Secci[óo]n\s+([\d\w\.\-]+))',
        "dpr_cases": r'(\d+\s+D\.P\.R\.\s+\d+)',
        "agencias": r'(?:Oficina|Departamento|Negociado|Administraci[óo]n|Tribunal|Consejo|Comisi[óo]n)\s+(?:de\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+(?:\s+(?:de|del|y|en)\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)*)',
        "fechas": r'(?:\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+\d{4}\b|\b\d{4}-\d{2}-\d{2}\b)',
        "monedas": r'(?:\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d+)*\s+d[óo]lares\b)'
    }

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, List[str]]:
        """Extract typed entities from document text."""
        entities = {}
        for ent_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.I)
            clean_matches = list(set([m.strip() if isinstance(m, str) else m[0].strip() for m in matches if m]))
            entities[ent_type] = clean_matches
        return entities

    @classmethod
    def extract_knowledge_triplets(cls, text: str, source_title: str) -> List[Dict[str, str]]:
        """
        Extract semantic relationship triplets (Subject -> Predicate -> Object).
        """
        triplets = []
        sentences = re.split(r'[\.\n]\s+', text)

        for s in sentences:
            s_clean = s.strip()
            if not s_clean or len(s_clean) < 15:
                continue

            # 1. Enmiendas (Subject enmienda a Object)
            enmienda_match = re.search(r'(?:Para\s+enmendar|enmienda)\s+(?:el\s+Art[íi]culo\s+[\d\w\.\-]+(?:\s+de\s+la\s+)?|\s+la\s+)?(Ley\s+(?:N[úu]m\.?\s*)?[\d\w\-]+)', s_clean, re.I)
            if enmienda_match:
                triplets.append({
                    "subject": source_title,
                    "predicate": "enmienda_a",
                    "object": enmienda_match.group(1).strip()
                })

            # 2. Creación / Establecimiento (Subject crea/establece Object)
            crea_match = re.search(r'(?:Para\s+crear|Se\s+crea|crea|establece)\s+(?:la\s+|el\s+)?([“\"][^”\"]+[”\"]|Ley\s+(?:para|del)\s+[^;,\.\n]+|Oficina\s+de\s+[^;,\.\n]+|Departamento\s+de\s+[^;,\.\n]+)', s_clean, re.I)
            if crea_match:
                triplets.append({
                    "subject": source_title,
                    "predicate": "crea_entidad",
                    "object": crea_match.group(1).strip('“"”')
                })

            # 3. Adscripción / Delegación (Agencia adscrita a Institución)
            adscrito_match = re.search(r'([A-ZÁÉÍÓÚÑ][\wáéíóúñ\s]+?)\s+adscrit[oa]\s+(?:a[l]?|a\s+la)\s+([A-ZÁÉÍÓÚÑ][\wáéíóúñ\s]+)', s_clean, re.I)
            if adscrito_match:
                triplets.append({
                    "subject": adscrito_match.group(1).strip(),
                    "predicate": "adscrito_a",
                    "object": adscrito_match.group(2).strip()
                })

        return triplets

class DeepKnowledgeHarvester:
    """Unified Deep Multi-Modal Content, Forensic Chain, and Knowledge Graph Extractor."""

    @classmethod
    def harvest(cls, raw_content: bytes, content_type: str, url: str) -> Dict[str, Any]:
        """
        Deep extraction pipeline returning:
        1. Clean text with zero omission
        2. Structured tables (Markdown & JSON)
        3. Typed legal entities
        4. RDF relationship triplets
        5. Merkle DAG root
        6. Rule 902 forensic multi-hashes (SHA-512, SHA-256, MD5)
        7. 384-dimensional dense semantic vectors
        8. Complete statutory anatomy breakdown
        9. Legislative genesis milestones
        """
        is_html = "html" in content_type.lower()
        is_json = "json" in content_type.lower()
        is_pdf = "pdf" in content_type.lower()

        text_content = ""
        title = "Document"
        tables = []
        meta = {}

        if is_html:
            from src.domain.universal_crawler.extractor import extract_clean_text_from_html
            html_str = raw_content.decode("utf-8", errors="ignore")
            title, text_content, meta = extract_clean_text_from_html(html_str)
            tables = TableStructureReconstructor.extract_html_tables(html_str)
        elif is_pdf:
            from src.domain.universal_crawler.extractor import extract_text_from_pdf_stream
            title, text_content = extract_text_from_pdf_stream(raw_content, url.split("/")[-1])
        elif is_json:
            from src.domain.universal_crawler.extractor import extract_text_from_json
            title, text_content = extract_text_from_json(raw_content)
        else:
            text_content = raw_content.decode("utf-8", errors="ignore")

        # 1. Extract entities and relationship triplets
        entities = EntityKnowledgeGraphExtractor.extract_entities(text_content)
        triplets = EntityKnowledgeGraphExtractor.extract_knowledge_triplets(text_content, title)

        # 2. Compute Hierarchical Merkle DAG root
        from src.domain.universal_crawler.merkle_dag import MerkleDAG
        dag = MerkleDAG.generate_document_dag(text_content, url, meta)
        merkle_root = dag["merkle_root"]
        leaf_count = dag["leaf_count"]

        # 3. Compute Rule 902 Forensic Multi-Hashes
        from src.domain.universal_crawler.forensic_vault import ForensicChainOfCustody
        forensic_hashes = ForensicChainOfCustody.compute_forensic_hashes(raw_content)

        # 4. Compute 384-dimensional Dense Semantic Vector
        from src.domain.universal_crawler.vector_semantic_matrix import FastSemanticVectorMatrix
        semantic_vector = FastSemanticVectorMatrix.vectorize_text(f"{title} {text_content}")

        # 5. Parse Exhaustive Statutory Anatomy
        from src.domain.universal_crawler.statutory_anatomy import ExhaustiveStatutoryAnatomyParser
        statutory_anatomy = ExhaustiveStatutoryAnatomyParser.parse_complete_anatomy(text_content, title)

        # 6. Extract Legislative Genesis
        from src.domain.universal_crawler.genesis_engine import LegislativeGenesisExtractor
        genesis = LegislativeGenesisExtractor.extract_genesis_timeline(text_content, title)

        return {
            "title": title,
            "text": text_content,
            "tables": tables,
            "entities": entities,
            "triplets": triplets,
            "metadata": meta,
            "merkle_dag_root": merkle_root,
            "forensic_hashes": forensic_hashes,
            "semantic_vector": semantic_vector,
            "statutory_anatomy": statutory_anatomy,
            "genesis": genesis,
            "stats": {
                "char_count": len(text_content),
                "word_count": len(text_content.split()),
                "table_count": len(tables),
                "triplet_count": len(triplets),
                "entity_count": sum(len(v) for v in entities.values()),
                "merkle_leaf_count": leaf_count
            }
        }
