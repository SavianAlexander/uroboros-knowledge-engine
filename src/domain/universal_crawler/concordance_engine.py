import re
import json
from typing import List, Dict, Any, Tuple, Optional, Set

"""
Global Statutory Concordance & Temporal Legal Evolution Tracker.
Features:
1. Bidirectional Cross-Citation Matrix (Cites -> Cited By)
2. Temporal Evolution & Vigencia State Machine (Vigente, Enmendada, Derogada, Inconstitucional)
3. Statutory Conflict & Jurisdictional Overlap Detector
"""

class StatutoryConcordanceEngine:
    """Builds global citation concordances and tracks statutory lifecycles."""

    STATUS_VIGENTE = "VIGENTE"
    STATUS_ENMENDADA = "ENMENDADA"
    STATUS_DEROGADA = "DEROGADA"
    STATUS_INCONSTITUCIONAL = "INCONSTITUCIONAL"

    @classmethod
    def build_concordance_matrix(cls, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct complete cross-reference concordance graph across all crawled documents.
        """
        doc_map = {}
        citation_index = {}
        cites_graph = {}
        cited_by_graph = {}
        lifecycle_status = {}

        for d in documents:
            title = d.get("title", "Doc")
            url = d.get("url", "")
            doc_id = d.get("id", hash(url))
            doc_map[title] = {"id": doc_id, "url": url, "title": title}
            lifecycle_status[title] = cls.STATUS_VIGENTE

            # Parse entities & triplets
            ent_json = d.get("entities_json", "{}")
            ent_data = json.loads(ent_json) if isinstance(ent_json, str) else (ent_json or {})
            trip_json = d.get("triplets_json", "[]")
            trip_data = json.loads(trip_json) if isinstance(trip_json, str) else (trip_json or [])

            # Register cited statutes
            for ley in ent_data.get("leyes", []):
                canon_ley = f"Ley Núm. {ley}"
                citation_index.setdefault(canon_ley, set()).add(title)
                cites_graph.setdefault(title, set()).add(canon_ley)
                cited_by_graph.setdefault(canon_ley, set()).add(title)

            # Analyze lifecycle transitions from triplets & text
            for t in trip_data:
                subj = t.get("subject", "")
                pred = t.get("predicate", "")
                obj = t.get("object", "")

                if pred == "enmienda_a":
                    lifecycle_status[obj] = cls.STATUS_ENMENDADA
                elif pred in ("deroga", "deroga_a", "sustituye_a"):
                    lifecycle_status[obj] = cls.STATUS_DEROGADA

            # Check D.P.R. inconstitucionalidad
            content = d.get("content_text", "")
            if re.search(r'inconstitucional(?:idad)?\b', content, re.I):
                for ley in ent_data.get("leyes", []):
                    canon_ley = f"Ley Núm. {ley}"
                    lifecycle_status[canon_ley] = cls.STATUS_INCONSTITUCIONAL

        # Serialize sets to sorted lists for JSON compatibility
        return {
            "total_statutes": len(doc_map),
            "citation_index": {k: sorted(list(v)) for k, v in citation_index.items()},
            "cites_graph": {k: sorted(list(v)) for k, v in cites_graph.items()},
            "cited_by_graph": {k: sorted(list(v)) for k, v in cited_by_graph.items()},
            "lifecycle_status": lifecycle_status
        }

    @classmethod
    def detect_jurisdictional_conflicts(cls, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect overlapping jurisdictional assignments across distinct statutes.
        """
        conflicts = []
        mandate_registry = {}

        for d in documents:
            title = d.get("title", "Doc")
            content = d.get("content_text", "")
            matches = re.findall(r'(?:faculta|ordena|asigna\s+la\s+responsabilidad)\s+(?:al?\s+)?([A-ZÁÉÍÓÚÑ][\wáéíóúñ\s]+?)\s+(?:para|a\s+los\s+fines\s+de)\s+([^;,\.\n]+)', content, re.I)
            for agency, mandate in matches:
                clean_agency = agency.strip()
                clean_mandate = mandate.strip()[:60]
                mandate_key = re.sub(r'\s+', ' ', clean_mandate).lower()

                if mandate_key in mandate_registry:
                    prev_title, prev_agency = mandate_registry[mandate_key]
                    if prev_agency.lower() != clean_agency.lower():
                        conflicts.append({
                            "mandate": clean_mandate,
                            "statute_a": prev_title,
                            "agency_a": prev_agency,
                            "statute_b": title,
                            "agency_b": clean_agency
                        })
                else:
                    mandate_registry[mandate_key] = (title, clean_agency)

        return conflicts
