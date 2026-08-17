"""
Zero-dependency MinHash & Jaccard similarity near-duplicate detector.
Identifies identical and near-duplicate vault documents.
"""
import os
import unicodedata
import re
import hashlib
from collections import defaultdict
import threading
from collections import OrderedDict, defaultdict
from typing import Dict, Any, List, Set, Tuple

_SHINGLE_CACHE: OrderedDict[str, Tuple[str, ...]] = OrderedDict()
_SHINGLE_LOCK = threading.Lock()
_MAX_SHINGLE_CACHE = 512


def _compute_shingles_tuple(text: str, k: int = 3) -> Tuple[str, ...]:
    if not text or not isinstance(text, (str, bytes)):
        return ()
    raw_str = text.decode("utf-8", errors="ignore") if isinstance(text, bytes) else str(text)
    norm_text = unicodedata.normalize("NFC", raw_str)
    digest = hashlib.sha256(norm_text.encode("utf-8", "ignore")).hexdigest()[:16]

    with _SHINGLE_LOCK:
        if digest in _SHINGLE_CACHE:
            _SHINGLE_CACHE.move_to_end(digest)
            return _SHINGLE_CACHE[digest]

    words = re.findall(r'\b[\w-]+\b', norm_text.lower())
    if len(words) < k:
        res = (" ".join(words),) if words else ()
    else:
        res = tuple(" ".join(words[i:i+k]) for i in range(len(words) - k + 1))

    with _SHINGLE_LOCK:
        _SHINGLE_CACHE[digest] = res
        if len(_SHINGLE_CACHE) > _MAX_SHINGLE_CACHE:
            _SHINGLE_CACHE.popitem(last=False)
    return res


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
    Uses inverted shingle index for O(N * K) candidate pruning instead of O(N^2) pairwise comparisons.
    """
    try:
        from src.infrastructure.database import get_db, init_db

        init_db()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, content FROM files WHERE content IS NOT NULL LIMIT 250")
            rows = cursor.fetchall()

        shingles_by_file = {}
        inverted_index: Dict[str, List[int]] = defaultdict(list)

        for r in rows:
            content = r[3] or ""
            if len(content.strip()) > 30:
                f_id = r[0]
                sh = compute_shingles(content, k=3)
                shingles_by_file[f_id] = {
                    "id": f_id,
                    "filename": r[1],
                    "filepath": r[2],
                    "shingles": sh
                }
                for s in sh:
                    inverted_index[s].append(f_id)

        # Inverted index candidate generation: only compare files sharing >= 1 shingle
        candidate_pairs: Set[Tuple[int, int]] = set()
        for f_list in inverted_index.values():
            if len(f_list) > 1:
                for i in range(len(f_list)):
                    for j in range(i + 1, len(f_list)):
                        id1, id2 = f_list[i], f_list[j]
                        if id1 != id2:
                            candidate_pairs.add((min(id1, id2), max(id1, id2)))

        duplicate_pairs = []
        for id_a, id_b in candidate_pairs:
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
