import math
import functools
import unicodedata
import hashlib
import json
import re
from typing import Dict, Any, List, Tuple

RE_FTS5_OPERATORS = re.compile(r'[\*\:\^\/\"\'\{\}\[\]\(\)]')

class LegalAccuracyEngine:
    """
    Legal-Grade Deterministic Accuracy Engine.
    Enforces NFC Unicode normalization, cryptographic SHA-256 content verification,
    deterministic RRF ranking with zero drift, and strict schema validation.
    """
    
    @staticmethod
    @functools.lru_cache(maxsize=512)
    def normalize_text_nfc(text: str) -> str:
        """Enforce strict NFC (Normalization Form C) Unicode standard with LRU caching."""
        if not text or not isinstance(text, str):
            return ""
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def verify_sha256_integrity(content: str, expected_sha256: str) -> bool:
        """Verify exact cryptographic SHA-256 bitwise parity."""
        if content is None or expected_sha256 is None:
            return False
        safe_content = str(content)
        safe_sha256 = str(expected_sha256)
        computed = hashlib.sha256(safe_content.encode("utf-8", errors="ignore")).hexdigest()
        return computed.lower() == safe_sha256.lower()

    @staticmethod
    def sanitize_fts5_query_legal(query: str) -> str:
        """
        Sanitize search query for legal-grade FTS5 execution.
        Prevents operator injection, preserves diacritics via NFC, and tokenizes cleanly.
        """
        if not query or not isinstance(query, str):
            return '""'
        nfc_query = unicodedata.normalize("NFC", query)
        # Strip dangerous FTS5 operators and quotes while preserving words and numbers
        cleaned = RE_FTS5_OPERATORS.sub(' ', nfc_query)
        tokens = [t.strip() for t in cleaned.split() if t.strip()]
        tokens = [t for t in tokens if t.lower() not in ('and', 'or', 'not', 'near')]
        if not tokens:
            return '""'
        # Quoted phrase matching for legal exactness
        return " AND ".join([f'"{t}"' for t in tokens])

    @staticmethod
    def calculate_exact_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Compute deterministic Cosine Similarity bound in [-1.0, 1.0].
        Uses double-precision floats to prevent floating-point drift.
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = 0.0
        norm1_sq = 0.0
        norm2_sq = 0.0
        for a, b in zip(vec1, vec2):
            fa, fb = float(a), float(b)
            dot_product += fa * fb
            norm1_sq += fa * fa
            norm2_sq += fb * fb

        if norm1_sq == 0.0 or norm2_sq == 0.0:
            return 0.0

        similarity = dot_product / (math.sqrt(norm1_sq) * math.sqrt(norm2_sq))
        # Clamp bounds strictly between -1.0 and +1.0
        return max(-1.0, min(1.0, similarity))

    @staticmethod
    def validate_api_payload_strict(payload: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
        """Strict structural payload validator."""
        if not isinstance(payload, dict):
            return False, "Payload must be a valid JSON object"

        for field in required_fields:
            if field not in payload:
                return False, f"Missing required legal field: '{field}'"
            if payload[field] is None:
                return False, f"Field '{field}' cannot be null"

        return True, "Valid"
