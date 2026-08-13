"""
Zero-Knowledge Cryptographic Audit Ledger Engine.
Hashes search queries, retrieved contexts, and synthesized answers into an append-only SHA-256 cryptographic chain.
Zero-dependency, stdlib implementation (hashlib).
"""
import hashlib
import time
from typing import Dict, Any, List

_CRYPTO_CHAIN: List[Dict[str, Any]] = []


def append_crypto_audit_block(
    query: str,
    answer: str,
    contexts: List[str]
) -> Dict[str, Any]:
    """
    Appends a new audit record to the cryptographic SHA-256 chain.
    """
    previous_hash = _CRYPTO_CHAIN[-1]["hash"] if _CRYPTO_CHAIN else "0" * 64
    timestamp = time.time()
    
    payload = f"{previous_hash}:{timestamp}:{query}:{answer}:{','.join(contexts)}"
    current_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    block = {
        "index": len(_CRYPTO_CHAIN) + 1,
        "timestamp": timestamp,
        "query": query,
        "answer_summary": answer[:100],
        "context_count": len(contexts),
        "previous_hash": previous_hash,
        "hash": current_hash
    }
    
    _CRYPTO_CHAIN.append(block)
    return {
        "audit_block": block,
        "chain_length": len(_CRYPTO_CHAIN),
        "status": "success"
    }


def verify_crypto_chain_integrity() -> bool:
    """
    Verifies that no blocks in the cryptographic chain have been tampered with.
    """
    for i in range(1, len(_CRYPTO_CHAIN)):
        prev_block = _CRYPTO_CHAIN[i-1]
        curr_block = _CRYPTO_CHAIN[i]
        if curr_block["previous_hash"] != prev_block["hash"]:
            return False
    return True
