"""
Incremental SHA-256 Vector Memory Cache Invalidation Guard.
Tracks document SHA-256 hashes to invalidate vector memory caches strictly upon file mutation.
"""
import hashlib
from typing import Dict, Any, Optional


class VectorCacheGuard:
    """Tracks SHA-256 file hashes to prevent redundant vector re-embeddings."""
    def __init__(self):
        self._hash_store: Dict[str, str] = {}

    def is_cache_valid(self, doc_id: str, content: str) -> bool:
        """Returns True if the content SHA-256 matches the cached hash."""
        if not doc_id or content is None:
            return False
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        cached_hash = self._hash_store.get(doc_id)
        if cached_hash == content_hash:
            return True
        # Update hash on mismatch or cache miss
        self._hash_store[doc_id] = content_hash
        return False

    def invalidate(self, doc_id: str):
        """Invalidates cache for a given doc_id."""
        self._hash_store.pop(doc_id, None)

    def clear(self):
        """Clears all cached hashes."""
        self._hash_store.clear()
