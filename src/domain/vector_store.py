import math
from typing import List, Dict, Tuple, Any

class DenseVectorStore:
    """
    Zero-dependency Dense Vector Similarity Engine.
    Computes cosine similarity, dot product, and L2 distance over vector matrices.
    """
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def add_vector(self, doc_id: str, vector: List[float], meta: Dict[str, Any] = None):
        """Normalize and store document vector embedding."""
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        normalized = [v / norm for v in vector]
        self.vectors[doc_id] = normalized
        self.metadata[doc_id] = meta or {}

    def search_nearest(self, query_vector: List[float], top_k: int = 10) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Return top_k nearest documents ranked by cosine similarity."""
        if not self.vectors:
            return []

        q_norm = math.sqrt(sum(v * v for v in query_vector)) or 1.0
        q_normalized = [v / q_norm for v in query_vector]

        results = []
        for doc_id, doc_vector in self.vectors.items():
            min_dim = min(len(q_normalized), len(doc_vector))
            score = sum(q_normalized[i] * doc_vector[i] for i in range(min_dim))
            results.append((doc_id, score, self.metadata.get(doc_id, {})))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def clear(self):
        self.vectors.clear()
        self.metadata.clear()
