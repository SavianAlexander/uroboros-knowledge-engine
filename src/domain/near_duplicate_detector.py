"""
Zero-dependency MinHash & Jaccard similarity near-duplicate detector.
Identifies identical and near-duplicate vault documents.
"""
import os
import unicodedata
import re
import hashlib
from collections import defaultdict
import functools
from typing import Dict, Any, List, Set, Tuple


@functools.lru_cache(maxsize=2048)
def _compute_shingles_tuple(text: str, k: int = 3) -> Tuple[str, ...]:
    if not text or not isinstance(text, (str, bytes)):
        return ()
    raw_str = text.decode("utf-8", errors="ignore") if isinstance(text, bytes) else str(text)
    norm_text = unicodedata.normalize("NFC", raw_str)
    words = re.findall(r'\b[\w-]+\b', norm_text.lower())
    if len(words) < k:
        return (" ".join(words),) if words else ()
    return tuple(" ".join(words[i:i+k]) for i in range(len(words) - k + 1))


def compute_shingles(text: str, k: int = 3) -> Set[str]:
    """Extracts word k-shingles from text."""
    return set(_compute_shingles_tuple(text, k))


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard Similarity Ratio |A ∩ B| / |A ∪ B|."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return round(intersection / float(union), 4) if union > 0 else 0.0


def detect_near_duplicates(similarity_threshold: float = 0.80) -> Dict[str, Any]:
    """
    Scans vault files in database and identifies near-duplicate document pairs.
    Zero-dependency stdlib implementation.
    """
    try:
        from src.infrastructure.database import get_db, init_db

        init_db()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, content FROM files WHERE content IS NOT NULL LIMIT 100")
            rows = cursor.fetchall()

        shingles_by_file = {}
        for r in rows:
            content = r[3] or ""
            if len(content.strip()) > 30:
                shingles_by_file[r[0]] = {
                    "id": r[0],
                    "filename": r[1],
                    "filepath": r[2],
                    "shingles": compute_shingles(content, k=3)
                }

        file_ids = list(shingles_by_file.keys())
        duplicate_pairs = []

        for i in range(len(file_ids)):
            for j in range(i + 1, len(file_ids)):
                id_a = file_ids[i]
                id_b = file_ids[j]

                shingles_a = shingles_by_file[id_a]["shingles"]
                shingles_b = shingles_by_file[id_b]["shingles"]

                sim = jaccard_similarity(shingles_a, shingles_b)
                if sim >= similarity_threshold:
                    duplicate_pairs.append({
                        "file_a": shingles_by_file[id_a]["filename"],
                        "file_b": shingles_by_file[id_b]["filename"],
                        "path_a": shingles_by_file[id_a]["filepath"],
                        "path_b": shingles_by_file[id_b]["filepath"],
                        "jaccard_similarity": sim,
                        "similarity_pct": round(sim * 100, 2)
                    })

        duplicate_pairs.sort(key=lambda x: x["jaccard_similarity"], reverse=True)

        return {
            "duplicate_pairs": duplicate_pairs,
            "total_pairs_found": len(duplicate_pairs),
            "threshold_used": similarity_threshold,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def detect_near_duplicate_chunks(similarity_threshold: float = 0.80, limit: int = 150) -> Dict[str, Any]:
    """
    Scans file chunks across the vault to detect near-duplicate chunk clusters and token savings.
    """
    try:
        from src.infrastructure.database import get_db, init_db

        init_db()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fc.id, fc.file_id, f.filename, fc.chunk_index, fc.content 
                FROM file_chunks fc
                JOIN files f ON fc.file_id = f.id
                WHERE LENGTH(fc.content) > 40
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

        if not rows:
            return {
                "status": "success",
                "total_chunks_analyzed": 0,
                "duplicate_clusters": [],
                "potential_token_savings": 0
            }

        shingles_by_chunk = [
            {
                "chunk_id": r[0],
                "file_id": r[1],
                "filename": r[2],
                "chunk_index": r[3],
                "content_preview": (r[4][:120] + "...") if len(r[4]) > 120 else r[4],
                "char_length": len(r[4]),
                "shingles": compute_shingles(r[4], k=3)
            }
            for r in rows
        ]

        duplicate_clusters = []
        claimed_ids = set()
        total_token_savings = 0

        for i, c_a in enumerate(shingles_by_chunk):
            if c_a["chunk_id"] in claimed_ids:
                continue
            cluster = [c_a]
            for j in range(i + 1, len(shingles_by_chunk)):
                c_b = shingles_by_chunk[j]
                if c_b["chunk_id"] in claimed_ids:
                    continue
                sim = jaccard_similarity(c_a["shingles"], c_b["shingles"])
                if sim >= similarity_threshold:
                    cluster.append(c_b)
                    claimed_ids.add(c_b["chunk_id"])

            if len(cluster) > 1:
                claimed_ids.add(c_a["chunk_id"])
                # Estimate token savings (4 chars ~ 1 token)
                saved_chars = sum(c["char_length"] for c in cluster[1:])
                saved_tokens = max(1, saved_chars // 4)
                total_token_savings += saved_tokens
                duplicate_clusters.append({
                    "cluster_size": len(cluster),
                    "primary_file": cluster[0]["filename"],
                    "savings_tokens_approx": saved_tokens,
                    "items": [
                        {
                            "chunk_id": c["chunk_id"],
                            "filename": c["filename"],
                            "chunk_index": c["chunk_index"],
                            "preview": c["content_preview"]
                        }
                        for c in cluster
                    ]
                })

        return {
            "status": "success",
            "total_chunks_analyzed": len(rows),
            "total_duplicate_clusters": len(duplicate_clusters),
            "potential_token_savings": total_token_savings,
            "duplicate_clusters": duplicate_clusters
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "duplicate_clusters": []}
