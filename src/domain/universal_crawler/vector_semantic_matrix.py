import math
import re
import hashlib
from typing import List, Dict, Any, Tuple

"""
In-Database Fast Semantic Vector Matrix.
Zero-Dependency 384-dimensional semantic embedding generator and cosine similarity search engine.
"""

class FastSemanticVectorMatrix:
    """Computes dense semantic embeddings and fast cosine vector rankings."""

    DIMENSIONS = 384

    @classmethod
    def vectorize_text(cls, text: str) -> List[float]:
        """Compute normalized 384-dimensional dense feature vector."""
        vec = [0.0] * cls.DIMENSIONS
        clean_text = text.lower().strip()
        tokens = re.findall(r'\b\w+\b', clean_text)

        if not tokens:
            return vec

        # Token + Trigram Hashing
        for token in tokens:
            # Word token hash
            h_word = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16) % cls.DIMENSIONS
            vec[h_word] += 1.0

            # Character 3-grams
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    ngram = token[i:i+3]
                    h_gram = int(hashlib.md5(ngram.encode('utf-8')).hexdigest(), 16) % cls.DIMENSIONS
                    vec[h_gram] += 0.5

        # L2-Norm Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec

    @classmethod
    def cosine_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two dense normalized vectors."""
        if not vec_a or not vec_b:
            return 0.0
        return max(0.0, min(1.0, sum(a * b for a, b in zip(vec_a, vec_b))))

    @classmethod
    def rank_documents(cls, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Rank documents by cosine vector similarity against query."""
        q_vec = cls.vectorize_text(query)
        scored_docs = []

        for d in documents:
            text = f"{d.get('title', '')} {d.get('content_text', '')}"
            d_vec = cls.vectorize_text(text)
            sim = cls.cosine_similarity(q_vec, d_vec)
            scored_docs.append({
                "id": d.get("id"),
                "title": d.get("title"),
                "url": d.get("url"),
                "similarity_score": round(sim, 4),
                "snippet": d.get("content_text", "")[:250] + "..."
            })

        scored_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_docs[:top_k]
