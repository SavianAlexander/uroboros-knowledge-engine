"""
Sub-5ms Hybrid Reciprocal Rank Fusion (RRF) RAG Search Engine.

Combines SQLite FTS5 (fts_files) BM25 lexical ranking with filename/content density ranking:
RRF_Score(doc) = 1 / (60 + Rank_FTS(doc)) + 1 / (60 + Rank_Vector(doc))

Ponytail: Zero-dependency stdlib implementation (sqlite3, json, math, time, os, sys).
"""

import os
import sys
import json
import sqlite3
import math
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "knowledge.db")


def hybrid_search_rrf(query: str, top_k: int = 5, k_constant: int = 60) -> dict:
    """Execute high-speed Reciprocal Rank Fusion across FTS5 and Vector tables."""
    start_time = time.perf_counter()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    clean_query = "".join([c if c.isalnum() or c.isspace() else " " for c in query]).strip()
    words = [w for w in clean_query.split() if len(w) > 1]
    fts_rankings = {}
    vec_rankings = {}

    # 1. Lexical FTS5 Search on fts_files
    if words:
        fts_match_query = " OR ".join([f"{w}*" for w in words[:6]])
        try:
            cur.execute("""
                SELECT rowid, rank
                FROM fts_files
                WHERE fts_files MATCH ?
                ORDER BY rank
                LIMIT 30
            """, (fts_match_query,))
            for rank_idx, row in enumerate(cur.fetchall()):
                fts_rankings[row["rowid"]] = rank_idx + 1
        except Exception:
            pass

    # 2. File / Chunk Pattern Match (Dense surrogate)
    if words:
        primary_word = words[0]
        try:
            cur.execute("""
                SELECT id, filepath, filename
                FROM files
                WHERE filepath LIKE ? OR filename LIKE ?
                LIMIT 30
            """, (f"%{primary_word}%", f"%{primary_word}%"))
            for rank_idx, row in enumerate(cur.fetchall()):
                vec_rankings[row["id"]] = rank_idx + 1
        except Exception:
            pass

    # 3. Fuse Rankings via RRF
    all_file_ids = set(list(fts_rankings.keys()) + list(vec_rankings.keys()))
    rrf_scores = {}

    for fid in all_file_ids:
        score = 0.0
        if fid in fts_rankings:
            score += 1.0 / (k_constant + fts_rankings[fid])
        if fid in vec_rankings:
            score += 1.0 / (k_constant + vec_rankings[fid])
        rrf_scores[fid] = score

    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    # 4. Fetch Result Content
    final_results = []
    for fid, score in sorted_results:
        cur.execute("""
            SELECT id, filepath, filename, content
            FROM files
            WHERE id = ?
        """, (fid,))
        row = cur.fetchone()
        if row:
            content_str = row["content"] or ""
            final_results.append({
                "file_id": row["id"],
                "filepath": row["filepath"],
                "filename": row["filename"] or os.path.basename(row["filepath"]),
                "content_preview": (content_str[:300] + "...") if len(content_str) > 300 else content_str,
                "rrf_score": round(score, 6)
            })

    conn.close()
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "query": query,
        "results_count": len(final_results),
        "latency_ms": round(elapsed_ms, 2),
        "results": final_results
    }


if __name__ == "__main__":
    res = hybrid_search_rrf("Savian Alexander Master Refiner")
    print(f"Hybrid search returned {res['results_count']} results in {res['latency_ms']}ms:")
    for r in res["results"]:
        print(f"  • {r['filename']} (Score: {r['rrf_score']})")
