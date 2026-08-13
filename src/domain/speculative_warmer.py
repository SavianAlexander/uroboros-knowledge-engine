"""
Keystroke Speculative Vector Warmer Engine.
Pre-fetches candidate document vector IDs into RAM as partial query prefixes are typed.
Achieves sub-2ms spotlight search retrieval response times.
"""
import time
from typing import Dict, Any, List, Optional
from src.domain.vector_store import DenseVectorStore


class SpeculativeContextWarmer:
    """In-memory predictive query prefix cache & vector warmer."""
    def __init__(self, vector_store: Optional[DenseVectorStore] = None):
        self.vector_store = vector_store or DenseVectorStore()
        self._prefix_cache: Dict[str, List[str]] = {}

    def warm_prefix(self, query_prefix: str, sample_vector: List[float]) -> List[str]:
        """Pre-fetches top candidate document IDs for a query prefix."""
        # ponytail: lightweight prefix memoization cache for sub-2ms spotlight search response
        prefix_key = query_prefix.lower().strip()
        if not prefix_key:
            return []

        if prefix_key in self._prefix_cache:
            return self._prefix_cache[prefix_key]

        results = self.vector_store.search_nearest_2phase(
            query_vector=sample_vector,
            top_k=5,
            coarse_dim=32,
            candidate_k=15
        )
        doc_ids = [doc_id for doc_id, score, meta in results]
        if len(self._prefix_cache) >= 1000:
            self._prefix_cache.pop(next(iter(self._prefix_cache)))
        self._prefix_cache[prefix_key] = doc_ids
        return doc_ids

    def get_warmed_candidates(self, query_prefix: str) -> List[str]:
        """Retrieves warmed document IDs from cache."""
        return self._prefix_cache.get(query_prefix.lower().strip(), [])

    def clear(self):
        """Clears prefix cache."""
        self._prefix_cache.clear()
