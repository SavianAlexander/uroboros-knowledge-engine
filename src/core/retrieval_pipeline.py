"""
Composable Retrieval Pipeline Engine (DAG / Protocol-based Stage Architecture).
Provides zero-overhead, modular search orchestration chaining FTS5 BM25, dense vector similarity,
Reciprocal Rank Fusion (RRF), ColBERT token reranking, recency decay, and source citation extraction.
Standard: Zero external dependencies, pure Python standard library + internal engine infrastructure.
"""

import time
import math
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Protocol, Callable, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SearchQuery:
    """Standard search query request payload."""
    raw_query: str
    top_k: int = 10
    rrf_k: int = 60
    vector_weight: float = 0.5
    fts_weight: float = 0.5
    tag_filter: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None
    min_score: float = 0.0
    enable_colbert: bool = False
    enable_recency_decay: bool = True
    decay_half_life_days: float = 30.0
    metadata_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchCandidate:
    """Normalized retrieved candidate record across search channels."""
    id: Optional[int] = None
    filepath: str = ""
    filename: str = ""
    title: str = ""
    content: str = ""
    score: float = 0.0
    fts_rank: Optional[int] = None
    fts_score: float = 0.0
    vector_rank: Optional[int] = None
    vector_score: float = 0.0
    colbert_score: Optional[float] = None
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filepath": self.filepath,
            "filename": self.filename,
            "title": self.title or self.filename,
            "content": self.content,
            "score": round(self.score, 6),
            "fts_rank": self.fts_rank,
            "fts_score": round(self.fts_score, 6) if self.fts_score else 0.0,
            "vector_rank": self.vector_rank,
            "vector_score": round(self.vector_score, 6) if self.vector_score else 0.0,
            "colbert_score": round(self.colbert_score, 6) if self.colbert_score is not None else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "citations": self.citations,
            "metadata": self.metadata
        }


@dataclass
class SearchContext:
    """Context bag carrying state, candidates, and execution telemetry across pipeline stages."""
    query: SearchQuery
    candidates: List[SearchCandidate] = field(default_factory=list)
    fts_candidates: List[SearchCandidate] = field(default_factory=list)
    vector_candidates: List[SearchCandidate] = field(default_factory=list)
    stage_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    total_latency_ms: float = 0.0


class SearchStage(Protocol):
    """Protocol for pluggable retrieval pipeline stages."""
    name: str

    def process(self, context: SearchContext) -> SearchContext:
        ...


class FTS5KeywordStage:
    """Retrieves keyword candidates via SQLite FTS5 index using BM25 scoring."""
    name: str = "fts5_keyword"

    def __init__(self, limit: int = 50):
        self.limit = limit

    def process(self, context: SearchContext) -> SearchContext:
        t0 = time.perf_counter()
        query_text = context.query.raw_query.strip()
        if not query_text:
            context.stage_metrics[self.name] = {"latency_ms": 0.0, "count": 0}
            return context

        try:
            from src.infrastructure.database import get_db
            from src.core.domain.services import sanitise_fts_query

            sanitized = sanitise_fts_query(query_text)
            if not sanitized:
                sanitized = query_text.replace('"', '""')

            results = []
            with get_db() as conn:
                cursor = conn.cursor()
                # Query FTS5 index with BM25 ranking
                cursor.execute("""
                    SELECT f.id, f.filepath, f.filename, f.content, f.created_at, f.updated_at,
                           bm25(files_fts) as rank_score
                    FROM files_fts fts
                    JOIN files f ON f.id = fts.rowid
                    WHERE files_fts MATCH ?
                    ORDER BY rank_score ASC
                    LIMIT ?
                """, (sanitized, self.limit))
                rows = cursor.fetchall()
                for rank_idx, r in enumerate(rows, start=1):
                    cand = SearchCandidate(
                        id=r["id"] if "id" in r.keys() else r[0],
                        filepath=r["filepath"] if "filepath" in r.keys() else r[1],
                        filename=r["filename"] if "filename" in r.keys() else r[2],
                        content=r["content"] if "content" in r.keys() else r[3],
                        created_at=r["created_at"] if "created_at" in r.keys() else r[4],
                        updated_at=r["updated_at"] if "updated_at" in r.keys() else r[5],
                        fts_rank=rank_idx,
                        fts_score=abs(float(r["rank_score"] if "rank_score" in r.keys() else r[6]))
                    )
                    results.append(cand)

            context.fts_candidates = results
            elapsed = (time.perf_counter() - t0) * 1000.0
            context.stage_metrics[self.name] = {"latency_ms": round(elapsed, 2), "count": len(results)}
        except Exception as e:
            logger.warning(f"FTS5KeywordStage warning: {e}")
            context.stage_metrics[self.name] = {"latency_ms": 0.0, "count": 0, "error": str(e)}

        return context


class DenseVectorStage:
    """Retrieves semantic candidates via dense embeddings and cosine similarity."""
    name: str = "dense_vector"

    def __init__(self, limit: int = 50):
        self.limit = limit

    def process(self, context: SearchContext) -> SearchContext:
        t0 = time.perf_counter()
        query_text = context.query.raw_query.strip()
        if not query_text:
            context.stage_metrics[self.name] = {"latency_ms": 0.0, "count": 0}
            return context

        try:
            from src.infrastructure.vector_engine import MiniVectorEngine
            raw_results = MiniVectorEngine.search(query_text, top_k=self.limit)
            vector_candidates = []
            for rank_idx, r in enumerate(raw_results, start=1):
                sim = float(r.get("similarity", r.get("score", 0.0)))
                cand = SearchCandidate(
                    id=r.get("id") or r.get("file_id"),
                    filepath=r.get("filepath") or r.get("path", ""),
                    filename=r.get("filename", ""),
                    title=r.get("title", ""),
                    content=r.get("content", ""),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at"),
                    vector_rank=rank_idx,
                    vector_score=sim
                )
                vector_candidates.append(cand)

            context.vector_candidates = vector_candidates
            elapsed = (time.perf_counter() - t0) * 1000.0
            context.stage_metrics[self.name] = {"latency_ms": round(elapsed, 2), "count": len(vector_candidates)}
        except Exception as e:
            logger.warning(f"DenseVectorStage warning: {e}")
            context.stage_metrics[self.name] = {"latency_ms": 0.0, "count": 0, "error": str(e)}

        return context


class RRFScoreFusionStage:
    """Fuses FTS5 and dense vector rank lists using Reciprocal Rank Fusion (RRF)."""
    name: str = "rrf_score_fusion"

    def __init__(self, k: int = 60, vector_weight: float = 0.5, fts_weight: float = 0.5):
        self.k = k
        self.vector_weight = vector_weight
        self.fts_weight = fts_weight

    def process(self, context: SearchContext) -> SearchContext:
        t0 = time.perf_counter()
        k_val = context.query.rrf_k or self.k
        w_vec = context.query.vector_weight if context.query.vector_weight is not None else self.vector_weight
        w_fts = context.query.fts_weight if context.query.fts_weight is not None else self.fts_weight

        merged: Dict[str, SearchCandidate] = {}

        # Process FTS candidates
        for cand in context.fts_candidates:
            key = cand.filepath or f"id_{cand.id}" or cand.filename
            if not key:
                continue
            if key not in merged:
                merged[key] = cand
            else:
                merged[key].fts_rank = cand.fts_rank
                merged[key].fts_score = cand.fts_score
                if not merged[key].content and cand.content:
                    merged[key].content = cand.content

            rrf_score = w_fts * (1.0 / (k_val + (cand.fts_rank or 999)))
            merged[key].score += rrf_score

        # Process Vector candidates
        for cand in context.vector_candidates:
            key = cand.filepath or f"id_{cand.id}" or cand.filename
            if not key:
                continue
            if key not in merged:
                merged[key] = cand
            else:
                merged[key].vector_rank = cand.vector_rank
                merged[key].vector_score = cand.vector_score
                if not merged[key].content and cand.content:
                    merged[key].content = cand.content

            rrf_score = w_vec * (1.0 / (k_val + (cand.vector_rank or 999)))
            merged[key].score += rrf_score

        # Sort by total fused RRF score descending
        fused_list = sorted(merged.values(), key=lambda x: x.score, reverse=True)
        context.candidates = fused_list[:context.query.top_k]

        elapsed = (time.perf_counter() - t0) * 1000.0
        context.stage_metrics[self.name] = {"latency_ms": round(elapsed, 2), "count": len(context.candidates)}
        return context


class ColBERTRerankStage:
    """Applies fine-grained token-level MaxSim / ColBERT precision re-ranking."""
    name: str = "colbert_rerank"

    def __init__(self, top_n: int = 15):
        self.top_n = top_n

    def process(self, context: SearchContext) -> SearchContext:
        if not context.query.enable_colbert or not context.candidates:
            return context

        t0 = time.perf_counter()
        try:
            from src.domain.binary_colbert import rerank_search_results_colbert
            candidates_dict = [c.to_dict() for c in context.candidates[:self.top_n]]
            reranked = rerank_search_results_colbert(context.query.raw_query, candidates_dict)

            # Map back updated scores
            reranked_map = {r.get("filepath", ""): r.get("colbert_score", r.get("score", 0.0)) for r in reranked}
            for c in context.candidates:
                if c.filepath in reranked_map:
                    c.colbert_score = reranked_map[c.filepath]
                    # Blend ColBERT score smoothly with RRF score
                    c.score = 0.5 * c.score + 0.5 * float(c.colbert_score or 0.0)

            context.candidates.sort(key=lambda x: x.score, reverse=True)
            elapsed = (time.perf_counter() - t0) * 1000.0
            context.stage_metrics[self.name] = {"latency_ms": round(elapsed, 2), "count": len(context.candidates)}
        except Exception as e:
            logger.warning(f"ColBERTRerankStage warning: {e}")
            context.stage_metrics[self.name] = {"latency_ms": 0.0, "count": len(context.candidates), "error": str(e)}

        return context


class RecencyDecayStage:
    """Applies exponential recency decay weighting to retrieved documents."""
    name: str = "recency_decay"

    def __init__(self, half_life_days: float = 30.0):
        self.half_life_days = half_life_days

    def process(self, context: SearchContext) -> SearchContext:
        if not context.query.enable_recency_decay or not context.candidates:
            return context

        t0 = time.perf_counter()
        now = time.time()
        decay_constant = math.log(2) / (max(1.0, context.query.decay_half_life_days or self.half_life_days) * 86400.0)

        for c in context.candidates:
            ts = c.updated_at or c.created_at
            if ts and ts > 0:
                age_seconds = max(0.0, now - ts)
                decay_factor = math.exp(-decay_constant * age_seconds)
                # Apply subtle recency boost (0.85 base + 0.15 recency factor)
                multiplier = 0.85 + (0.15 * decay_factor)
                c.score *= multiplier

        context.candidates.sort(key=lambda x: x.score, reverse=True)
        elapsed = (time.perf_counter() - t0) * 1000.0
        context.stage_metrics[self.name] = {"latency_ms": round(elapsed, 2), "count": len(context.candidates)}
        return context


class SourceCitationStage:
    """Extracts grounded snippet citations, paragraph indices, and line numbers."""
    name: str = "source_citation"

    def process(self, context: SearchContext) -> SearchContext:
        if not context.candidates:
            return context

        t0 = time.perf_counter()
        query_words = set(context.query.raw_query.lower().split())

        for c in context.candidates:
            text = c.content or ""
            if not text:
                continue
            lines = text.splitlines()
            citations = []
            for idx, line in enumerate(lines, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                line_words = set(clean_line.lower().split())
                overlap = query_words.intersection(line_words)
                if overlap:
                    citations.append({
                        "line_number": idx,
                        "text": clean_line[:200],
                        "overlap_count": len(overlap)
                    })
                    if len(citations) >= 3:
                        break
            c.citations = citations

        elapsed = (time.perf_counter() - t0) * 1000.0
        context.stage_metrics[self.name] = {"latency_ms": round(elapsed, 2), "count": len(context.candidates)}
        return context


class RetrievalPipeline:
    """
    Modular execution engine for chaining search stages.
    Executes stages sequentially, records total latency, and formats output.
    """

    def __init__(self, stages: Optional[List[SearchStage]] = None):
        self.stages = stages or [
            FTS5KeywordStage(),
            DenseVectorStage(),
            RRFScoreFusionStage(),
            ColBERTRerankStage(),
            RecencyDecayStage(),
            SourceCitationStage()
        ]

    def add_stage(self, stage: SearchStage) -> "RetrievalPipeline":
        self.stages.append(stage)
        return self

    def execute(self, query: SearchQuery) -> SearchContext:
        t0 = time.perf_counter()
        context = SearchContext(query=query)

        for stage in self.stages:
            try:
                context = stage.process(context)
            except Exception as e:
                logger.error(f"Pipeline stage {getattr(stage, 'name', 'unknown')} failed: {e}")

        context.total_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return context


def create_standard_hybrid_pipeline() -> RetrievalPipeline:
    """Factory creating standard production Hybrid RRF + ColBERT RAG pipeline."""
    return RetrievalPipeline([
        FTS5KeywordStage(limit=50),
        DenseVectorStage(limit=50),
        RRFScoreFusionStage(k=60),
        ColBERTRerankStage(top_n=15),
        RecencyDecayStage(half_life_days=30.0),
        SourceCitationStage()
    ])


def create_fast_keyword_pipeline() -> RetrievalPipeline:
    """Factory creating ultra-fast FTS5-only search pipeline."""
    return RetrievalPipeline([
        FTS5KeywordStage(limit=25),
        SourceCitationStage()
    ])
