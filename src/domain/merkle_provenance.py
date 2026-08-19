"""Facade for merkle_provenance in root domain namespace."""
from src.domain.synthesis.merkle_provenance import (
    MerkleProvenanceEngine,
    generate_merkle_provenance,
    verify_merkle_provenance,
    hash_pair
)

__all__ = [
    "MerkleProvenanceEngine",
    "generate_merkle_provenance",
    "verify_merkle_provenance",
    "hash_pair"
]
