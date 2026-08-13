"""
Zero-dependency MinHash & Jaccard similarity near-duplicate detector.
Identifies identical and near-duplicate vault documents.
"""

import re
import hashlib
from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple


def compute_shingles(text: str, k: int = 3) -> Set[str]:
    """Extracts word k-shingles from text."""
    if not text or not isinstance(text, (str, bytes)):
        return set()
    import unicodedata
    norm_text = unicodedata.normalize("NFC", str_text)
    words = re.findall(r'\b[\w-]+\b', norm_text.lower())
    if len(words) < k:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}


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
        import os
        from src.infrastructure.database import get_db_connection, init_db, DB_FILE

        init_db()
        with get_db_connection(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, content FROM files WHERE content IS NOT NULL LIMIT 50")
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
