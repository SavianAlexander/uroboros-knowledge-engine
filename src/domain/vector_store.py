import os
import math
import json
import struct
import sqlite3
import threading
from typing import List, Dict, Tuple, Any

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
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
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
        with self._lock, sqlite3.connect(self.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doc_id, vector_blob, meta_json FROM embeddings")
            for row in cursor.fetchall():
                doc_id, blob, meta_json = row
                if blob:
                    try:
                        vec = struct.unpack(self._pack_format, blob)
                        self.vectors[doc_id] = vec
                        self.metadata[doc_id] = json.loads(meta_json) if meta_json else {}
                    except Exception:
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
            
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        normalized = tuple(v / norm for v in vector)
        
        meta_dict = meta or {}
        blob = struct.pack(self._pack_format, *normalized)
        meta_json = json.dumps(meta_dict)
        
        with self._lock:
            self.vectors[doc_id] = normalized
            self.metadata[doc_id] = meta_dict
            
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO embeddings (doc_id, vector_blob, meta_json) VALUES (?, ?, ?)", 
                (doc_id, blob, meta_json)
            )
            conn.commit()

    def search_nearest(self, query_vector: List[float], top_k: int = 10) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Return top_k nearest documents ranked by cosine similarity using fast zip iteration."""
        if not self.vectors or not query_vector:
            return []

        # Pad/truncate query
        vec_len = len(query_vector)
        if vec_len > self.dimension:
            query_vector = query_vector[:self.dimension]
        elif vec_len < self.dimension:
            query_vector = query_vector + [0.0] * (self.dimension - vec_len)

        q_norm = math.sqrt(sum(v * v for v in query_vector)) or 1.0
        q_normalized = tuple(v / q_norm for v in query_vector)

        results = []
        with self._lock:
            for doc_id, doc_vector in self.vectors.items():
                score = sum(a * b for a, b in zip(q_normalized, doc_vector))
                results.append((doc_id, score, self.metadata.get(doc_id, {})))

        # N-log-K optimization conceptually via sort+slice
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def clear(self):
        with self._lock:
            self.vectors.clear()
            self.metadata.clear()
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.execute("DELETE FROM embeddings")
            conn.commit()
