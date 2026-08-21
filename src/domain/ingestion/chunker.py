"""
Production Chonkie-Powered Chunking Engine.
Primary Engine: chonkie (RecursiveChunker, SemanticChunker, SentenceChunker, TableChunker).
Resilient Fallback: AST Heading-aware Markdown Chunker with Table header preservation.
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
    TABLE = "table"


class ChunkPayload(BaseModel):
    """Pydantic v2 schema for chunk outputs with rich metadata."""
    chunk_index: int = Field(..., description="0-indexed position in document")
    content: str = Field(..., description="Raw text body of the chunk")
    doc_title: str = Field(default="Document", description="Title or basename of parent document")
    filepath: str = Field(default="", description="Source file path or canonical URL")
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


class TableChunker:
    """
    Dedicated chunker for tabular markdown data preserving column headers across chunk splits.
    """

    @staticmethod
    def chunk_table(
        table_text: str,
        doc_title: str = "Table Document",
        filepath: str = "",
        max_rows_per_chunk: int = 15
    ) -> List[ChunkPayload]:
        """
        Chunks markdown tables ensuring header rows (| Col 1 | Col 2 | and | --- | --- |) are repeated on each chunk.
        """
        lines = [line.strip() for line in table_text.strip().splitlines() if line.strip()]
        if not lines:
            return []

        # Find header and separator
        header_lines: List[str] = []
        data_rows: List[str] = []

        for idx, line in enumerate(lines):
            if "|" in line:
                if len(header_lines) < 2:
                    header_lines.append(line)
                else:
                    data_rows.append(line)
            else:
                if not header_lines:
                    header_lines.append(line)
                else:
                    data_rows.append(line)

        if not data_rows:
            # Entire table fits in one chunk
            return [
                ChunkPayload(
                    chunk_index=0,
                    content=table_text.strip(),
                    doc_title=doc_title,
                    filepath=filepath,
                    parent_header="Table",
                    header_breadcrumb=f"{doc_title} > Table",
                    trust_type="pricing" if "price" in table_text.lower() or "cost" in table_text.lower() else "general",
                    token_count=len(table_text.split())
                )
            ]

        header_prefix = "\n".join(header_lines)
        chunks: List[ChunkPayload] = []

        for i in range(0, len(data_rows), max_rows_per_chunk):
            batch_rows = data_rows[i:i + max_rows_per_chunk]
            chunk_content = f"{header_prefix}\n" + "\n".join(batch_rows)
            chunks.append(
                ChunkPayload(
                    chunk_index=len(chunks),
                    content=chunk_content.strip(),
                    doc_title=doc_title,
                    filepath=filepath,
                    parent_header="Table",
                    header_breadcrumb=f"{doc_title} > Table (Rows {i+1}-{i+len(batch_rows)})",
                    trust_type="pricing" if "price" in chunk_content.lower() or "cost" in chunk_content.lower() else "general",
                    token_count=len(chunk_content.split())
                )
            )

        return chunks


class UniversalChunker:
    """
    Universal Chunker orchestrator configurable for Recursive, Semantic, Sentence, and Table chunking.
    """

    def __init__(
        self,
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        semantic_threshold: float = 0.75
    ):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.semantic_threshold = semantic_threshold

    def chunk(self, text: str, doc_title: str = "Document", filepath: str = "") -> List[ChunkPayload]:
        """Chunks text using configured strategy."""
        return ProductionChunker.chunk_document(
            text=text,
            doc_title=doc_title,
            filepath=filepath,
            strategy=self.strategy,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap
        )


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
        """
        if not text or not str(text).strip():
            return []

        # Table strategy routing
        if strategy == ChunkingStrategy.TABLE or (isinstance(strategy, str) and strategy.lower() == "table"):
            return TableChunker.chunk_table(table_text=text, doc_title=doc_title, filepath=filepath)

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
        """Executes native Chonkie recursive, semantic, or sentence chunking."""
        strategy_str = strategy.value if isinstance(strategy, ChunkingStrategy) else str(strategy).lower()

        if strategy_str == "semantic":
            chunker = SemanticChunker(threshold=0.75, chunk_size=chunk_size)
        elif strategy_str == "sentence":
            chunker = SentenceChunker(chunk_size=chunk_size, chunk_overlap=overlap)
        else:
            chunker = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=overlap)

        raw_chunks = chunker.chunk(text)
        payloads: List[ChunkPayload] = []

        for idx, rc in enumerate(raw_chunks):
            content = rc.text if hasattr(rc, "text") else str(rc)
            token_cnt = rc.token_count if hasattr(rc, "token_count") else len(content.split())

            trust_type = ProductionChunker._classify_trust_pillar(content)
            intent_type = ProductionChunker._classify_micro_moment(content)

            payloads.append(
                ChunkPayload(
                    chunk_index=idx,
                    content=content,
                    doc_title=doc_title,
                    filepath=filepath,
                    parent_header=ProductionChunker._extract_primary_header(content),
                    header_breadcrumb=f"{doc_title} > Chunk {idx+1}",
                    trust_type=trust_type,
                    intent_type=intent_type,
                    token_count=token_cnt
                )
            )

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
        Deterministic AST heading-aware Markdown chunker.
        Preserves Markdown heading hierarchies and attaches 5-Pillar Trust taxonomy.
        """
        sections = re.split(r'(?=(?:^|\n)#{1,6}\s+)', text)
        sections = [s.strip() for s in sections if s.strip()]

        payloads: List[ChunkPayload] = []
        current_breadcrumb: List[str] = [doc_title]
        global_chunk_idx = 0

        for sec in sections:
            header_match = re.match(r'^(#{1,6})\s+(.+?)(?:\n|$)', sec)
            if header_match:
                level = len(header_match.group(1))
                h_text = header_match.group(2).strip()

                while len(current_breadcrumb) > level:
                    current_breadcrumb.pop()
                if len(current_breadcrumb) == level:
                    current_breadcrumb[-1] = h_text
                else:
                    current_breadcrumb.append(h_text)

                parent_header = h_text
            else:
                parent_header = current_breadcrumb[-1] if len(current_breadcrumb) > 1 else "General"

            words = sec.split()
            if len(words) <= chunk_size or chunk_size <= 0:
                trust_type = ProductionChunker._classify_trust_pillar(sec)
                intent_type = ProductionChunker._classify_micro_moment(sec)

                payloads.append(
                    ChunkPayload(
                        chunk_index=global_chunk_idx,
                        content=sec,
                        doc_title=doc_title,
                        filepath=filepath,
                        parent_header=parent_header,
                        header_breadcrumb=" > ".join(current_breadcrumb),
                        trust_type=trust_type,
                        intent_type=intent_type,
                        token_count=len(words)
                    )
                )
                global_chunk_idx += 1
            else:
                step = max(1, chunk_size - overlap)
                for w_idx in range(0, len(words), step):
                    chunk_words = words[w_idx:w_idx + chunk_size]
                    sub_content = " ".join(chunk_words)
                    trust_type = ProductionChunker._classify_trust_pillar(sub_content)
                    intent_type = ProductionChunker._classify_micro_moment(sub_content)

                    payloads.append(
                        ChunkPayload(
                            chunk_index=global_chunk_idx,
                            content=sub_content,
                            doc_title=doc_title,
                            filepath=filepath,
                            parent_header=parent_header,
                            header_breadcrumb=" > ".join(current_breadcrumb),
                            trust_type=trust_type,
                            intent_type=intent_type,
                            token_count=len(chunk_words)
                        )
                    )
                    global_chunk_idx += 1

        return payloads

    @staticmethod
    def _classify_trust_pillar(content: str) -> str:
        """Categorizes chunk into 5-Pillar Trust Taxonomy."""
        lower = content.lower()
        if any(w in lower for w in ["price", "pricing", "cost", "tier", "quote", "$", "usd", "license"]):
            return "pricing"
        if any(w in lower for w in ["problem", "issue", "bug", "error", "failure", "crash", "outage", "fault"]):
            return "problems"
        if any(w in lower for w in ["not a fit", "incompatible", "unsupported", "limitation", "deprecated", "cannot"]):
            return "not_a_fit"
        if any(w in lower for w in ["repair", "replace", "fix", "recover", "maintenance", "troubleshoot", "restore"]):
            return "repair_vs_replace"
        if any(w in lower for w in ["windows", "linux", "gpu", "vram", "ram", "cpu", "memory", "storage", "environment"]):
            return "environment_constraints"
        return "general"

    @staticmethod
    def _classify_micro_moment(content: str) -> str:
        """Categorizes chunk into 4 Micro-Moments Intent."""
        lower = content.lower()
        if any(w in lower for w in ["how to", "guide", "step", "install", "configure", "run", "execute"]):
            return "WANT_TO_DO"
        if any(w in lower for w in ["where", "near", "location", "address", "provider", "find"]):
            return "WANT_TO_GO_LOCATE"
        if any(w in lower for w in ["buy", "purchase", "order", "subscribe", "tier", "plan"]):
            return "WANT_TO_BUY_DECIDE"
        return "WANT_TO_KNOW"

    @staticmethod
    def _extract_primary_header(content: str) -> str:
        """Extracts first markdown heading or default."""
        m = re.search(r'^#{1,6}\s+(.+?)$', content, re.MULTILINE)
        return m.group(1).strip() if m else "General"
