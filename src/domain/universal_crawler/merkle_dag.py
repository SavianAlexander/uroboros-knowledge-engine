import hashlib
import unicodedata
from typing import List, Dict, Any, Tuple, Optional

"""
Hierarchical Merkle DAG Vault Ledger.
Constructs cryptographically verifiable Merkle Directed Acyclic Graphs (DAGs)
for every scraped document, section tree, and crawl job ledger.
"""

def hash_bytes(data: bytes) -> str:
    """Compute SHA-256 hash string."""
    return hashlib.sha256(data).hexdigest()

def hash_string(text: str) -> str:
    """Compute normalized SHA-256 hash string."""
    norm = unicodedata.normalize("NFC", text.strip())
    return hash_bytes(norm.encode('utf-8'))

class MerkleDAG:
    """Constructs multi-level Merkle trees for documents and crawls."""

    @staticmethod
    def build_paragraph_leaf_hashes(text: str) -> List[str]:
        """Split text into paragraph units and compute cryptographic leaf hashes."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip() if text.strip() else "EMPTY_DOC"]
        return [hash_string(p) for p in paragraphs]

    @classmethod
    def compute_merkle_root(cls, leaf_hashes: List[str]) -> str:
        """Compute the single cryptographic Merkle Root from an array of leaf hashes."""
        if not leaf_hashes:
            return hash_string("EMPTY_TREE")
        if len(leaf_hashes) == 1:
            return leaf_hashes[0]

        current_level = leaf_hashes[:]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if (i + 1) < len(current_level) else left
                combined = hash_string(f"{left}:{right}")
                next_level.append(combined)
            current_level = next_level

        return current_level[0]

    @classmethod
    def generate_document_dag(cls, doc_text: str, doc_url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build complete Merkle DAG structure for a document.
        Returns root hash, leaf count, and proof tree.
        """
        leaves = cls.build_paragraph_leaf_hashes(doc_text)
        merkle_root = cls.compute_merkle_root(leaves)

        return {
            "document_url": doc_url,
            "merkle_root": merkle_root,
            "leaf_count": len(leaves),
            "leaves": leaves,
            "metadata_signature": hash_string(f"{doc_url}|{metadata.get('job_id')}|{merkle_root}")
        }
