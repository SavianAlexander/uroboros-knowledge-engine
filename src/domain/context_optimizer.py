"""
Context Assembly & Optimization Layer:
- ParentResolver: Resolves and deduplicates section-level parent contexts from granular child hits.
- AlternatingRankSorter: 'Lost in the Middle' attention layout reordering [R1, R3, R5, ..., R6, R4, R2].
- ContextCompactor: Deduplicates whitespace and formats structured citation attribution.
- GroundedGuardrail: Strict confidence threshold gating (0.35) with deterministic fallback.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Tuple, Optional
import src.infrastructure.database as db
from src.infrastructure.database import get_db_connection

logger = logging.getLogger(__name__)

RELEVANCE_THRESHOLD = 0.35


class ParentResolver:
    """Resolves section-level parent chunks from retrieved child chunk hits."""

    @staticmethod
    def resolve_parents_from_child_hits(
        child_hits: List[Dict[str, Any]],
        db_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Takes ranked child hits, fetches the full parent section text for each parent_id,
        and deduplicates so multiple hits in the same section do not duplicate tokens.
        Preserves ranking priority based on the highest-scoring child in each parent section.
        """
        if not child_hits:
            return []

        db_file = db_path or db.DB_FILE
        resolved_parents: List[Dict[str, Any]] = []
        seen_parent_ids = set()
        seen_file_ids = set()

        # Group child hits by parent_id
        parent_id_map: Dict[str, Dict[str, Any]] = {}
        missing_parent_hits: List[Dict[str, Any]] = []

        for hit in child_hits:
            p_id = hit.get("parent_id")
            if p_id:
                if p_id not in parent_id_map:
                    parent_id_map[p_id] = hit
            else:
                missing_parent_hits.append(hit)

        # Batch query parent_chunks from SQLite
        parent_records: Dict[str, Dict[str, Any]] = {}
        if parent_id_map:
            try:
                with get_db_connection(db_file) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    placeholders = ",".join(["?"] * len(parent_id_map))
                    cursor.execute(f"""
                        SELECT id, file_id, section_header, content, doc_title, domain_scope
                        FROM parent_chunks
                        WHERE id IN ({placeholders})
                    """, list(parent_id_map.keys()))
                    for r in cursor.fetchall():
                        parent_records[r["id"]] = dict(r)
            except Exception as e:
                logger.error(f"Failed to resolve parent chunks: {e}")

        # Also resolve missing parent IDs by file_id if parent_chunks exist for that file
        missing_file_ids = [h.get("id") for h in missing_parent_hits if h.get("id")]
        file_parents_map: Dict[int, List[Dict[str, Any]]] = {}
        if missing_file_ids:
            try:
                with get_db_connection(db_file) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    placeholders = ",".join(["?"] * len(missing_file_ids))
                    cursor.execute(f"""
                        SELECT id, file_id, section_header, content, doc_title, domain_scope
                        FROM parent_chunks
                        WHERE file_id IN ({placeholders})
                    """, missing_file_ids)
                    for r in cursor.fetchall():
                        file_parents_map.setdefault(r["file_id"], []).append(dict(r))
            except Exception:
                pass

        # Construct deduplicated ranked parent list
        for hit in child_hits:
            p_id = hit.get("parent_id")
            if p_id and p_id in parent_records:
                if p_id in seen_parent_ids:
                    continue
                seen_parent_ids.add(p_id)
                p_data = parent_records[p_id]
                resolved_parents.append({
                    "id": p_data.get("file_id", hit.get("id")),
                    "parent_id": p_id,
                    "chunk_id": hit.get("chunk_id"),
                    "filename": hit.get("filename", ""),
                    "filepath": hit.get("filepath", ""),
                    "doc_title": p_data.get("doc_title") or hit.get("doc_title", ""),
                    "section_header": p_data.get("section_header") or hit.get("parent_header", ""),
                    "content": p_data.get("content", hit.get("content", "")),
                    "domain_scope": p_data.get("domain_scope") or hit.get("domain_scope", "general"),
                    "score": hit.get("score", 0.0),
                    "cross_score": hit.get("cross_score", hit.get("score", 0.0)),
                    "rrf_score": hit.get("rrf_score", 0.0),
                    "is_parent": True
                })
            elif hit.get("id") in file_parents_map and file_parents_map[hit["id"]]:
                p_list = file_parents_map[hit["id"]]
                p_data = p_list[0]
                p_id_resolved = p_data["id"]
                if p_id_resolved in seen_parent_ids:
                    continue
                seen_parent_ids.add(p_id_resolved)
                resolved_parents.append({
                    "id": p_data.get("file_id", hit.get("id")),
                    "parent_id": p_id_resolved,
                    "chunk_id": hit.get("chunk_id"),
                    "filename": hit.get("filename", ""),
                    "filepath": hit.get("filepath", ""),
                    "doc_title": p_data.get("doc_title") or hit.get("doc_title", ""),
                    "section_header": p_data.get("section_header") or hit.get("parent_header", ""),
                    "content": p_data.get("content", hit.get("content", "")),
                    "domain_scope": p_data.get("domain_scope") or hit.get("domain_scope", "general"),
                    "score": hit.get("score", 0.0),
                    "cross_score": hit.get("cross_score", hit.get("score", 0.0)),
                    "rrf_score": hit.get("rrf_score", 0.0),
                    "is_parent": True
                })
            else:
                # Fallback for standalone chunks or legacy records
                f_id = hit.get("id")
                c_id = hit.get("chunk_id", f_id)
                dedup_key = f"chunk_{c_id}"
                if dedup_key in seen_parent_ids:
                    continue
                seen_parent_ids.add(dedup_key)
                resolved_parents.append({
                    "id": f_id,
                    "parent_id": None,
                    "chunk_id": c_id,
                    "filename": hit.get("filename", ""),
                    "filepath": hit.get("filepath", ""),
                    "doc_title": hit.get("doc_title", hit.get("filename", "")),
                    "section_header": hit.get("parent_header", "General"),
                    "content": hit.get("content", ""),
                    "domain_scope": hit.get("domain_scope", "general"),
                    "score": hit.get("score", 0.0),
                    "cross_score": hit.get("cross_score", hit.get("score", 0.0)),
                    "rrf_score": hit.get("rrf_score", 0.0),
                    "is_parent": False
                })

        return resolved_parents


class AlternatingRankSorter:
    """
    'Lost in the Middle' Attention Optimization:
    Reorders retrieved parent contexts so highest-relevance items sit at the very start
    (primacy position) and second-highest at the very bottom (recency position).
    Layout pattern: [R1, R3, R5, ..., R6, R4, R2]
    """

    @staticmethod
    def reorder_lost_in_the_middle(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reorders items:
        1st -> index 0 (top)
        2nd -> index -1 (bottom)
        3rd -> index 1
        4th -> index -2
        ...
        """
        if len(items) <= 2:
            return items[:]

        reordered = [None] * len(items)
        left = 0
        right = len(items) - 1

        for i, item in enumerate(items):
            if i % 2 == 0:
                reordered[left] = item
                left += 1
            else:
                reordered[right] = item
                right -= 1

        return [x for x in reordered if x is not None]


class ContextCompactor:
    """Compacts context blocks and formats structured inline citations."""

    @staticmethod
    def compact_context_blocks(
        blocks: List[Dict[str, Any]],
        max_char_budget: int = 12000
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Compacts resolved parent blocks into a single structured context string
        with source attribution markers and returns metadata citations.
        """
        if not blocks:
            return "", []

        context_parts = []
        citations = []
        curr_chars = 0

        for b in blocks:
            d_title = b.get("doc_title") or b.get("filename") or "Document"
            s_header = b.get("section_header") or "Section"
            body = (b.get("content") or "").strip()
            
            # Format clean block
            header_line = f"### [Source: {d_title} | Section: {s_header}]"
            block_text = f"{header_line}\n{body}\n"

            if curr_chars + len(block_text) > max_char_budget and context_parts:
                break

            context_parts.append(block_text)
            curr_chars += len(block_text)

            citations.append({
                "doc_title": d_title,
                "section_header": s_header,
                "filename": b.get("filename", ""),
                "filepath": b.get("filepath", ""),
                "parent_id": b.get("parent_id"),
                "score": round(b.get("cross_score", b.get("score", 0.0)), 4),
                "is_parent": b.get("is_parent", False)
            })

        full_context = "\n---\n\n".join(context_parts).strip()
        return full_context, citations


class GroundedGuardrail:
    """Strict confidence gating and fallback message generator."""

    @staticmethod
    def verify_grounding_confidence(top_score: float, threshold: float = RELEVANCE_THRESHOLD) -> bool:
        """Returns True if the top candidate score meets or exceeds the relevance threshold."""
        return top_score >= threshold

    @staticmethod
    def get_fallback_insufficient_context_message(
        query: str,
        threshold: float = RELEVANCE_THRESHOLD
    ) -> str:
        """Deterministic, grounded refusal response when retrieved evidence is below threshold."""
        return (
            f"Insufficient verified context: No documents in the knowledge repository meet the required "
            f"confidence threshold ({threshold:.2f}) to answer this query with high precision."
        )
