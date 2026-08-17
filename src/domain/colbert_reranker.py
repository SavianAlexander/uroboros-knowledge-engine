"""
ColBERT Late Interaction Reranker Engine.
Delegates to unified src.domain.reranking engine.
"""
from src.domain.reranking import (
    dot_product,
    normalize_vector,
    colbert_maxsim_score,
    rerank_documents_colbert
)
