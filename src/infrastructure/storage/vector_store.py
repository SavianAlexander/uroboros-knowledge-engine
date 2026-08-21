"""
Canonical Qdrant Vector & Payload Storage Engine (10-Tool Stack).
Supports high-throughput vector search, HNSW indexing (m=16, ef_construct=100),
Cosine distance metrics, and deterministic metadata pre-filtering (tenant_id, trust_type).
"""

import os
import sys
import uuid
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for Qdrant Client
HAS_QDRANT = False
try:
    import qdrant_client
    from qdrant_client import QdrantClient, AsyncQdrantClient, models
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
        HnswConfigDiff,
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


class QdrantVectorStore:
    """
    Qdrant-backed Vector & Payload store supporting HNSW indexing, Cosine distance,
    and deterministic payload pre-filtering.
    """

    def __init__(
        self,
        location: str = ":memory:",
        collection_name: str = "neuro_knowledge_vault",
        vector_dim: int = 384,
        hnsw_m: int = 16,
        hnsw_ef: int = 100
    ):
        self.location = location
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.hnsw_m = hnsw_m
        self.hnsw_ef = hnsw_ef
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
        """Provisions collection with Cosine distance and HNSW parameters if missing."""
        if not self.client:
            return
        collections = self.client.get_collections().collections
        existing_names = {c.name for c in collections}
        if self.collection_name not in existing_names:
            hnsw_diff = HnswConfigDiff(m=self.hnsw_m, ef_construct=self.hnsw_ef)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
                hnsw_config=hnsw_diff
            )
            logger.info("Created Qdrant collection '%s' (dim=%d, HNSW m=%d ef=%d)", self.collection_name, self.vector_dim, self.hnsw_m, self.hnsw_ef)

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
                    "source_url": c.get("source_url") or c.get("filepath", ""),
                    "filepath": c.get("filepath", "")
                }

                points.append(PointStruct(id=pt_id, vector=vec, payload=payload))

            self.client.upsert(collection_name=self.collection_name, points=points)
            return len(points)

        # Fallback in-memory storage
        for c in chunks:
            self._fallback_records.append(dict(c))
        return len(chunks)

    async def upsert_chunks_async(self, chunks: List[Dict[str, Any]]) -> int:
        """Asynchronous upsert wrapper."""
        return await asyncio.to_thread(self.upsert_chunks, chunks)

    def search_similarity(
        self,
        query_vector: List[float],
        top_k: int = 5,
        tenant_id: Optional[Union[str, int]] = None,
        trust_type: Optional[str] = None,
        doc_id: Optional[Union[str, int]] = None
    ) -> List[QdrantSearchResult]:
        """
        Executes vector similarity search with deterministic payload pre-filtering.
        """
        if len(query_vector) < self.vector_dim:
            query_vector = query_vector + [0.0] * (self.vector_dim - len(query_vector))
        elif len(query_vector) > self.vector_dim:
            query_vector = query_vector[:self.vector_dim]

        if self.client:
            conditions = []
            if tenant_id is not None:
                conditions.append(FieldCondition(key="tenant_id", match=MatchValue(value=str(tenant_id))))
            if trust_type is not None:
                conditions.append(FieldCondition(key="trust_type", match=MatchValue(value=str(trust_type))))
            if doc_id is not None:
                conditions.append(FieldCondition(key="doc_id", match=MatchValue(value=doc_id)))

            query_filter = Filter(must=conditions) if conditions else None

            try:
                # Support qdrant-client >= 1.7 search methods
                if hasattr(self.client, "search"):
                    hits = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=top_k,
                        query_filter=query_filter
                    )
                else:
                    hits = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        limit=top_k,
                        query_filter=query_filter
                    ).points
            except Exception as e:
                logger.warning("Qdrant search error, falling back to local scan: %s", e)
                hits = []

            results = []
            for hit in hits:
                p = hit.payload or {}
                results.append(
                    QdrantSearchResult(
                        id=str(hit.id),
                        score=float(hit.score),
                        payload=p,
                        content=p.get("content", ""),
                        doc_title=p.get("doc_title", "Document"),
                        tenant_id=p.get("tenant_id", "default"),
                        trust_type=p.get("trust_type", "general")
                    )
                )
            if results:
                return results

        # Fallback Cosine Sim scan
        results = []
        for r in self._fallback_records:
            if tenant_id is not None and str(r.get("tenant_id", "default")) != str(tenant_id):
                continue
            if trust_type is not None and str(r.get("trust_type", "general")) != str(trust_type):
                continue
            if doc_id is not None and str(r.get("doc_id", "")) != str(doc_id):
                continue

            r_vec = r.get("vector") or [0.0] * self.vector_dim
            sim = self._cosine_sim(query_vector, r_vec)
            results.append(
                QdrantSearchResult(
                    id=str(r.get("id", uuid.uuid4())),
                    score=sim,
                    payload=r,
                    content=r.get("content", ""),
                    doc_title=r.get("doc_title", "Document"),
                    tenant_id=r.get("tenant_id", "default"),
                    trust_type=r.get("trust_type", "general")
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    async def search_async(
        self,
        query_vector: List[float],
        top_k: int = 5,
        tenant_id: Optional[Union[str, int]] = None,
        trust_type: Optional[str] = None
    ) -> List[QdrantSearchResult]:
        """Asynchronous similarity search."""
        return await asyncio.to_thread(
            self.search_similarity,
            query_vector,
            top_k,
            tenant_id,
            trust_type
        )

    @staticmethod
    def _cosine_sim(a: List[float], b: List[float]) -> float:
        """Zero-dependency cosine similarity calculator."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


# Alias
QdrantVectorEngine = QdrantVectorStore
