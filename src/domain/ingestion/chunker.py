"""
Production Chonkie-Powered Chunking Engine.
Primary Engine: chonkie (RecursiveChunker, SemanticChunker, SentenceChunker).
Resilient Fallback: AST Heading-aware Markdown Chunker.
Output: Strict Pydantic v2 ChunkPayload objects preserving hierarchy & 5-Pillar Trust metadata.
"""

import os
import sys
import re
import math
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for Chonkie
HAS_CHONKIE = False
try:
    import chonkie
    from chonkie import RecursiveChunker, SentenceChunker, SemanticChunker, Chunk
    HAS_CHONKIE = True
except (ImportError, Exception) as e:
    HAS_CHONKIE = False
    logger.info("Chonkie library not available, using built-in AST Heading & Token Chunker fallback: %s", e)


class ChunkingStrategy(str, Enum):
    RECURSIVE = "recursive"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"


class ChunkPayload(BaseModel):
    """Pydantic v2 schema for chunk outputs with rich metadata."""
    chunk_index: int = Field(..., description="0-indexed position in document")
    content: str = Field(..., description="Raw text body of the chunk")
    doc_title: str = Field(default="Document", description="Title or basename of parent document")
    parent_id: Optional[Union[str, int]] = Field(default=None, description="Identifier of parent section")
    parent_header: str = Field(default="General", description="Immediate section header")
    header_breadcrumb: str = Field(default="Root", description="Full hierarchical path (e.g. Doc > Section > Sub)")
    trust_type: str = Field(default="general", description="5-Pillar Trust Taxonomy classification")
    intent_type: str = Field(default="general", description="4 Micro-Moments intent classification")
    source_type: str = Field(default="primary_doc", description="Source credibility tier")
    token_count: int = Field(default=0, description="Estimated or exact token count")
    entities: List[str] = Field(default_factory=list, description="Extracted named entities")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary domain attributes")

    def to_dict(self) -> Dict[str, Any]:
        """Converts model to serializable dictionary."""
        return self.model_dump()


class ProductionChunker:
    """
    Production-grade text chunker orchestrating Chonkie engines with AST metadata preservation.
    """

    @staticmethod
    def is_chonkie_available() -> bool:
        """Checks if chonkie package is active."""
        return HAS_CHONKIE

    @staticmethod
    def chunk_document(
        text: str,
        doc_title: str = "Document",
        filepath: str = "",
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
        chunk_size: int = 512,
        overlap: int = 64
    ) -> List[ChunkPayload]:
        """
        Chunks input document text into structured ChunkPayload objects.
        
        Args:
            text: Markdown or plain text document.
            doc_title: Document title or filename.
            filepath: Source filesystem path for attribution.
            strategy: Chunking strategy (recursive, sentence, semantic, hierarchical).
            chunk_size: Maximum token/character chunk size.
            overlap: Overlap size between adjacent chunks.
            
        Returns:
            List of validated ChunkPayload models.
        """
        if not text or not str(text).strip():
            return []

        # 1. Primary Engine: Chonkie Chunker
        if HAS_CHONKIE:
            try:
                return ProductionChunker._chonkie_chunk(
                    text=text,
                    doc_title=doc_title,
                    filepath=filepath,
                    strategy=strategy,
                    chunk_size=chunk_size,
                    overlap=overlap
                )
            except Exception as e:
                logger.warning("Chonkie chunking execution failed, falling back to AST chunker: %s", e)

        # 2. Resilient Fallback Engine: AST Heading & Sliding Window Chunker
        return ProductionChunker._fallback_ast_chunk(
            text=text,
            doc_title=doc_title,
            filepath=filepath,
            chunk_size=chunk_size,
            overlap=overlap
        )

    @staticmethod
    def _chonkie_chunk(
        text: str,
        doc_title: str,
        filepath: str,
        strategy: ChunkingStrategy,
        chunk_size: int,
        overlap: int
    ) -> List[ChunkPayload]:
        """Delegates to native Chonkie chunker instance."""
        if strategy == ChunkingStrategy.SENTENCE:
            chunker_inst = SentenceChunker(chunk_size=chunk_size, chunk_overlap=overlap)
        elif strategy == ChunkingStrategy.SEMANTIC:
            try:
                chunker_inst = SemanticChunker(chunk_size=chunk_size)
            except Exception:
                chunker_inst = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=overlap)
        else:
            chunker_inst = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=overlap)

        chonkie_chunks = chunker_inst.chunk(text)
        payloads: List[ChunkPayload] = []

        from src.core.domain.services import extract_chunk_attributes

        for idx, c in enumerate(chonkie_chunks):
            content_str = c.text if hasattr(c, "text") else str(c)
            attrs = extract_chunk_attributes(content_str, doc_title=doc_title, filepath=filepath)
            
            tok_count = getattr(c, "token_count", len(content_str.split()))

            payloads.append(ChunkPayload(
                chunk_index=idx,
                content=content_str,
                doc_title=doc_title,
                parent_id=f"p_{idx // 3}",
                parent_header="General",
                header_breadcrumb=f"{doc_title} > Chunk {idx+1}",
                trust_type=attrs.get("trust_type", "general"),
                intent_type=attrs.get("intent_type", "general"),
                source_type=attrs.get("source_type", "primary_doc"),
                token_count=tok_count,
                entities=attrs.get("entities", []),
                attributes=attrs.get("attributes_json", {})
            ))

        return payloads

    @staticmethod
    def _fallback_ast_chunk(
        text: str,
        doc_title: str,
        filepath: str,
        chunk_size: int,
        overlap: int
    ) -> List[ChunkPayload]:
        """
        Built-in AST markdown heading and paragraph preserving chunker.
        """
        from src.core.domain.services import semantic_markdown_chunker_hierarchical, extract_chunk_attributes

        hierarchy = semantic_markdown_chunker_hierarchical(
            text=text,
            filepath=filepath,
            parent_size=max(chunk_size * 2, 800),
            child_size=chunk_size,
            child_overlap=overlap
        )

        raw_children = hierarchy.get("child_chunks", [])
        payloads: List[ChunkPayload] = []

        for idx, raw in enumerate(raw_children):
            c_text = raw.get("raw_content") or raw.get("content") or ""
            p_hdr = raw.get("parent_header") or "General"
            d_title = raw.get("doc_title") or doc_title

            attrs = extract_chunk_attributes(c_text, doc_title=d_title, parent_headers=p_hdr, filepath=filepath)
            attrs_val = attrs.get("attributes_json")
            if isinstance(attrs_val, str):
                try:
                    parsed_attrs = json.loads(attrs_val)
                except Exception:
                    parsed_attrs = {}
            elif isinstance(attrs_val, dict):
                parsed_attrs = attrs_val
            else:
                parsed_attrs = {}

            payloads.append(ChunkPayload(
                chunk_index=idx,
                content=c_text,
                doc_title=d_title,
                parent_id=raw.get("parent_id"),
                parent_header=p_hdr,
                header_breadcrumb=f"{d_title} > {p_hdr}",
                trust_type=attrs.get("trust_type", "general"),
                intent_type=attrs.get("intent_type", "general"),
                source_type=attrs.get("source_type", "primary_doc"),
                token_count=len(c_text.split()),
                entities=attrs.get("entities", []),
                attributes=parsed_attrs
            ))

        return payloads
