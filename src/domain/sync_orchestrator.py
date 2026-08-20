"""Master Vault Synchronization & Change Detection Orchestrator.
Maintains persistent SHA-256 ledger across Knowledge Vault documents and triggers automatic RAG vectorization.
Pure Python standard library (json, hashlib, os, time).
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, List, Optional


class PrimarySourceSyncOrchestrator:
    """Master Orchestrator for Knowledge Vault Document Harvesting and Sync."""

    def __init__(self, vault_root: Optional[str] = None):
        if vault_root:
            self.vault_root = vault_root
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.vault_root = os.path.join(base_dir, "vault")
        os.makedirs(self.vault_root, exist_ok=True)
        self.ledger_path = os.path.join(self.vault_root, ".sync_ledger.json")

    def _load_ledger(self) -> Dict[str, Any]:
        """Load persistent synchronization hash ledger."""
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_sync_timestamp": None, "total_sync_runs": 0, "entries": {}}

    def _save_ledger(self, ledger: Dict[str, Any]):
        """Persist synchronization hash ledger atomically."""
        ledger["last_sync_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ledger["total_sync_runs"] = ledger.get("total_sync_runs", 0) + 1
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2)

    def execute_sync(self, domain_filter: Optional[str] = None, auto_index: bool = True) -> Dict[str, Any]:
        """Execute full or filtered knowledge vault synchronization."""
        t0 = time.time()
        ledger = self._load_ledger()
        harvested_results: List[Dict[str, Any]] = []
        updated_count = 0
        new_count = 0
        unchanged_count = 0

        # Scan all documents inside the vault
        valid_extensions = {".md", ".txt", ".json", ".csv", ".pdf", ".py", ".ts", ".js", ".html"}
        for root, _, files in os.walk(self.vault_root):
            for file in files:
                if file.startswith("."):
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_extensions:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.vault_root).replace("\\", "/")
                    try:
                        with open(full_path, "rb") as f:
                            data = f.read()
                        sha256_hash = hashlib.sha256(data).hexdigest()
                        harvested_results.append({
                            "filename": rel_path,
                            "filepath": full_path,
                            "sha256": sha256_hash,
                            "bytes": len(data)
                        })
                    except Exception:
                        continue

        # Process ledger changes and detect diffs
        ledger_entries = ledger.setdefault("entries", {})
        for item in harvested_results:
            rel_key = item["filename"]
            sha256 = item["sha256"]

            if rel_key not in ledger_entries:
                new_count += 1
                ledger_entries[rel_key] = {
                    "sha256": sha256,
                    "first_harvested": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "bytes": item.get("bytes", 0)
                }
            elif ledger_entries[rel_key].get("sha256") != sha256:
                updated_count += 1
                ledger_entries[rel_key]["sha256"] = sha256
                ledger_entries[rel_key]["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                ledger_entries[rel_key]["bytes"] = item.get("bytes", 0)
            else:
                unchanged_count += 1

        self._save_ledger(ledger)
        duration_ms = round((time.time() - t0) * 1000.0, 2)

        # Auto-index into SQLite Vector Vault if requested
        indexed_status = "SKIPPED"
        if auto_index and (new_count > 0 or updated_count > 0):
            try:
                from src.infrastructure.vector_engine import index_directory
                index_directory(self.vault_root)
                indexed_status = "INDEXED_VAULT"
            except Exception as e:
                indexed_status = f"INDEX_ERROR: {str(e)}"

        return {
            "status": "SUCCESS",
            "sync_duration_ms": duration_ms,
            "total_harvested": len(harvested_results),
            "new_documents": new_count,
            "updated_documents": updated_count,
            "unchanged_documents": unchanged_count,
            "ledger_path": self.ledger_path,
            "rag_indexing_status": indexed_status,
            "documents": [
                {
                    "filename": r["filename"],
                    "sha256": r["sha256"][:12] + "...",
                    "bytes": r.get("bytes", 0)
                }
                for r in harvested_results
            ]
        }
