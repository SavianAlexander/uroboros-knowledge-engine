"""
Production Qdrant Vector & Payload Storage Engine.
Supports high-throughput vector search, collection provisioning, and deterministic metadata pre-filtering.
"""

import os
import sys
import uuid
import logging
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for Qdrant Client
HAS_QDRANT = False
try:
    import qdrant_client
    from qdrant_client import QdrantClient, models
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
        SearchParams
    )
    HAS_QDRANT = True
except (ImportError, Exception) as e:
    HAS_QDRANT = False
    logger.info("Qdrant client not available, using in-memory vector store fallback: %s", e)


class QdrantSearchResult(BaseModel):
    """Pydantic v2 representation of a Qdrant search match."""
    id: Union[str, int]
    score: float
    payload: Dict[str, Any]
    content: str
    doc_title: str
    tenant_id: Union[str, int] = "default"
    trust_type: str = "general"


class QdrantVectorEngine:
    """
    Qdrant-backed Vector and Payload store supporting in-memory and local disk persistence.
    """

    def __init__(self, location: str = ":memory:", collection_name: str = "neuro_knowledge_vault", vector_dim: int = 384):
        self.location = location
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.client: Optional[Any] = None
        self._fallback_records: List[Dict[str, Any]] = []

        if HAS_QDRANT:
            try:
                self.client = QdrantClient(location=self.location)
                self._ensure_collection()
            except Exception as e:
                logger.warning("Failed to initialize QdrantClient at '%s': %s", self.location, e)
                self.client = None

    def _ensure_collection(self) -> None:
        """Provisions collection if it does not exist."""
        if not self.client:
            return
        collections = self.client.get_collections().collections
        existing_names = {c.name for c in collections}
        if self.collection_name not in existing_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE)
            )
            logger.info("Created Qdrant collection '%s' (dim=%d, distance=COSINE)", self.collection_name, self.vector_dim)

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Upserts a batch of chunk records containing 'vector' and metadata fields.
        """
        if not chunks:
            return 0

        if self.client:
            points: List[PointStruct] = []
            for c in chunks:
                vec = c.get("vector") or [0.0] * self.vector_dim
                # Ensure vector dimension matches
                if len(vec) < self.vector_dim:
                    vec = vec + [0.0] * (self.vector_dim - len(vec))
                elif len(vec) > self.vector_dim:
                    vec = vec[:self.vector_dim]

                raw_id = c.get("id")
                if raw_id is None:
                    pt_id = str(uuid.uuid4())
                elif isinstance(raw_id, int):
                    pt_id = raw_id
                else:
                    try:
                        uuid.UUID(str(raw_id))
                        pt_id = str(raw_id)
                    except (ValueError, TypeError):
                        pt_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(raw_id)))

                payload = {
                    "original_id": str(raw_id) if raw_id is not None else str(pt_id),
                    "doc_id": c.get("doc_id") or c.get("file_id", 0),
                    "chunk_index": c.get("chunk_index", 0),
                    "content": c.get("content", ""),
                    "doc_title": c.get("doc_title", "Document"),
                    "parent_id": c.get("parent_id"),
                    "parent_header": c.get("parent_header", "General"),
                    "tenant_id": c.get("tenant_id", "default"),
                    "trust_type": c.get("trust_type", "general"),
                    "intent_type": c.get("intent_type", "general"),
                    "source_type": c.get("source_type", "primary_doc"),
                    "filepath": c.get("filepath", "")
                }

                points.append(PointStruct(id=pt_id, vector=vec, payload=payload))

            self.client.upsert(collection_name=self.collection_name, points=points)
            return len(points)

        # Fallback in-memory storage
        for c in chunks:
            self._fallback_records.append(dict(c))
        return len(chunks)

    def search_similarity(
        self,
        query_vector: List[float],
        top_k: int = 5,
        tenant_id: Optional[Union[str, int]] = None,
        trust_type: Optional[str] = None
    ) -> List[QdrantSearchResult]:
        """
        Executes vector similarity search with deterministic payload pre-filtering.
        """
        if not query_vector:
            return []

        # Pad or slice query vector
        if len(query_vector) < self.vector_dim:
            query_vector = query_vector + [0.0] * (self.vector_dim - len(query_vector))
        elif len(query_vector) > self.vector_dim:
            query_vector = query_vector[:self.vector_dim]

        if self.client:
            # Build Qdrant filter
            must_conditions = []
            if tenant_id is not None:
                must_conditions.append(
                    FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))
                )
            if trust_type is not None and trust_type != "general":
                must_conditions.append(
                    FieldCondition(key="trust_type", match=MatchValue(value=trust_type))
                )

            query_filter = Filter(must=must_conditions) if must_conditions else None

            # Qdrant client query points
            hits = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k
            ).points

            results: List[QdrantSearchResult] = []
            for h in hits:
                payload = h.payload or {}
                results.append(QdrantSearchResult(
                    id=payload.get("original_id") or str(h.id),
                    score=float(h.score) if hasattr(h, "score") and h.score is not None else 1.0,
                    payload=payload,
                    content=payload.get("content", ""),
                    doc_title=payload.get("doc_title", "Document"),
                    tenant_id=payload.get("tenant_id", "default"),
                    trust_type=payload.get("trust_type", "general")
                ))
            return results

        # In-memory fallback dot product search
        results = []
        for r in self._fallback_records:
            if tenant_id is not None and str(r.get("tenant_id")) != str(tenant_id):
                continue
            if trust_type is not None and trust_type != "general" and r.get("trust_type") != trust_type:
                continue

            r_vec = r.get("vector") or [0.0] * self.vector_dim
            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_vector, r_vec))
            norm_a = sum(a * a for a in query_vector) ** 0.5 or 1.0
            norm_b = sum(b * b for b in r_vec) ** 0.5 or 1.0
            sim = dot / (norm_a * norm_b)

            results.append(QdrantSearchResult(
                id=r.get("id", str(uuid.uuid4())),
                score=round(sim, 4),
                payload=r,
                content=r.get("content", ""),
                doc_title=r.get("doc_title", "Document"),
                tenant_id=r.get("tenant_id", "default"),
                trust_type=r.get("trust_type", "general")
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
