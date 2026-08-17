import os
import math
import json
import struct
import heapq
import sqlite3
import threading
import contextlib
from typing import List, Dict, Tuple, Any
from src.infrastructure.database import get_db_connection

class DenseVectorStore:
    """
    Zero-dependency Dense Vector Similarity Engine with SQLite Persistence.
    Computes cosine similarity over vector matrices with in-memory caching and WAL DB packing.
    """
    def __init__(self, dimension: int = 128, db_path: str = "vectors.db"):
        self.dimension = dimension
        self.db_path = db_path
        self.vectors: Dict[str, Tuple[float, ...]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
        # Struct format string: e.g., '128f'
        self._pack_format = f"{dimension}f"
        
        self._init_db()
        self._load_from_db()

    def _init_db(self):
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    doc_id TEXT PRIMARY KEY,
                    vector_blob BLOB,
                    meta_json TEXT
                )
            """)
            conn.commit()

    def _load_from_db(self):
        with self._lock, get_db_connection(self.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doc_id, vector_blob, meta_json FROM embeddings")
            for row in cursor.fetchall():
                doc_id, blob, meta_json = row
                if blob:
                    try:
                        vec = struct.unpack(self._pack_format, blob)
                        self.vectors[doc_id] = vec
                        self.metadata[doc_id] = json.loads(meta_json) if meta_json else {}
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception:
                        import logging; logging.getLogger(__name__).exception("Swallowed error in vector_store.py")
                        pass # Ignore malformed blobs

    def add_vector(self, doc_id: str, vector: List[float], meta: Dict[str, Any] = None):
        """Normalize, cache, and persist document vector embedding."""
        if not vector:
            return
            
        # Ensure dimension matches (truncate or pad with zeros)
        vec_len = len(vector)
        if vec_len > self.dimension:
            vector = vector[:self.dimension]
        elif vec_len < self.dimension:
            vector = vector + [0.0] * (self.dimension - vec_len)
            
        norm = math.sqrt(math.fsum(v * v for v in vector)) or 1.0
        normalized = tuple(v / norm for v in vector)
        
        meta_dict = meta or {}
        blob = struct.pack(self._pack_format, *normalized)
        meta_json = json.dumps(meta_dict)
        
        with self._lock:
            self.vectors[doc_id] = normalized
            self.metadata[doc_id] = meta_dict
            
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO embeddings (doc_id, vector_blob, meta_json) VALUES (?, ?, ?)", 
                (doc_id, blob, meta_json)
            )
            conn.commit()

    def search_nearest(self, query_vector: List[float], top_k: int = 10) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Return top_k nearest documents ranked by cosine similarity using zero-allocation O(N log K) min-heap."""
        if not self.vectors or not query_vector or top_k <= 0:
            return []

        # Pad/truncate query
        vec_len = len(query_vector)
        if vec_len > self.dimension:
            query_vector = query_vector[:self.dimension]
        elif vec_len < self.dimension:
            query_vector = query_vector + [0.0] * (self.dimension - vec_len)

        q_norm = math.sqrt(math.fsum(v * v for v in query_vector)) or 1.0
        q_normalized = tuple(v / q_norm for v in query_vector)

        with self._lock:
            # Min-heap of size top_k: (score, doc_id)
            heap: List[Tuple[float, str]] = []
            for doc_id, doc_vector in self.vectors.items():
                score = math.fsum(a * b for a, b in zip(q_normalized, doc_vector))
                if len(heap) < top_k:
                    heapq.heappush(heap, (score, doc_id))
                elif score > heap[0][0]:
                    heapq.heapreplace(heap, (score, doc_id))
            
            # Sort top_k items in descending order
            heap.sort(key=lambda x: x[0], reverse=True)
            return [(doc_id, score, self.metadata.get(doc_id, {})) for score, doc_id in heap]

    def search_nearest_2phase(self, query_vector: List[float], top_k: int = 10, coarse_dim: int = 64, candidate_k: int = 50) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Two-phase Matryoshka Representation Learning (MRL) retrieval:
        1. Coarse Pass: Fast cosine similarity on truncated vectors (coarse_dim) to retrieve top candidates.
        2. Precision Pass: Full-dimension cosine rescoring on the top candidates.
        # ponytail: 2-phase MRL coarse-to-fine filtering with O(N log K) heap
        """
        if not self.vectors or not query_vector or top_k <= 0:
            return []

        vec_len = len(query_vector)
        if vec_len > self.dimension:
            q_full = query_vector[:self.dimension]
        else:
            q_full = query_vector + [0.0] * (self.dimension - vec_len)

        full_norm = math.sqrt(math.fsum(v * v for v in q_full)) or 1.0
        q_full_norm = tuple(v / full_norm for v in q_full)

        actual_coarse = min(coarse_dim, self.dimension)
        coarse_q = q_full_norm[:actual_coarse]
        coarse_q_norm_val = math.sqrt(math.fsum(v * v for v in coarse_q)) or 1.0
        coarse_q_norm = tuple(v / coarse_q_norm_val for v in coarse_q)

        target_candidates = max(candidate_k, top_k * 3)

        with self._lock:
            # 1. Coarse min-heap
            coarse_heap: List[Tuple[float, str, Tuple[float, ...]]] = []
            for doc_id, doc_vector in self.vectors.items():
                coarse_doc = doc_vector[:actual_coarse]
                coarse_doc_norm_val = math.sqrt(math.fsum(v * v for v in coarse_doc)) or 1.0
                coarse_score = math.fsum(a * (b / coarse_doc_norm_val) for a, b in zip(coarse_q_norm, coarse_doc))
                
                if len(coarse_heap) < target_candidates:
                    heapq.heappush(coarse_heap, (coarse_score, doc_id, doc_vector))
                elif coarse_score > coarse_heap[0][0]:
                    heapq.heapreplace(coarse_heap, (coarse_score, doc_id, doc_vector))

            # 2. Precision min-heap on coarse survivors
            prec_heap: List[Tuple[float, str]] = []
            for _, doc_id, doc_vector in coarse_heap:
                score = math.fsum(a * b for a, b in zip(q_full_norm, doc_vector))
                if len(prec_heap) < top_k:
                    heapq.heappush(prec_heap, (score, doc_id))
                elif score > prec_heap[0][0]:
                    heapq.heapreplace(prec_heap, (score, doc_id))

            prec_heap.sort(key=lambda x: x[0], reverse=True)
            return [(doc_id, score, self.metadata.get(doc_id, {})) for score, doc_id in prec_heap]

    def clear(self):
        with self._lock:
            self.vectors.clear()
            self.metadata.clear()
        with get_db_connection(self.db_path, timeout=30.0) as conn:
            conn.execute("DELETE FROM embeddings")
            conn.commit()
