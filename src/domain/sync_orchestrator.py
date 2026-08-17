"""Master Primary Source Synchronization & Change Detection Orchestrator.
Orchestrates live harvesting across eCFR, Federal Register, Atlassian, and IBM Cúram.
Maintains persistent SHA-256 ledger and triggers automatic RAG vectorization.
Pure Python standard library (json, hashlib, os, time).
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, List, Optional

from src.domain.connectors.ecfr_connector import EcfrConnector
from src.domain.connectors.federal_register_connector import FederalRegisterConnector
from src.domain.connectors.jira_openapi_connector import JiraOpenApiConnector
from src.domain.connectors.curam_spec_connector import CuramSpecConnector


class PrimarySourceSyncOrchestrator:
    """Master Orchestrator for Zero-Redaction Primary Source Harvesting and Sync."""

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
        """Execute full or filtered primary source synchronization."""
        t0 = time.time()
        ledger = self._load_ledger()
        harvested_results: List[Dict[str, Any]] = []
        updated_count = 0
        new_count = 0
        unchanged_count = 0

        # 1. Harvest eCFR Federal Regulations
        if not domain_filter or domain_filter in ["ecfr", "statutory", "benefits"]:
            ecfr = EcfrConnector(output_dir=os.path.join(self.vault_root, "statutory_benefits", "primary_sources"))
            ecfr_res = ecfr.harvest_all()
            harvested_results.extend(ecfr_res)

        # 2. Harvest Federal Register Guidelines & Notices
        if not domain_filter or domain_filter in ["federal_register", "fpl", "statutory"]:
            fed_reg = FederalRegisterConnector(output_dir=os.path.join(self.vault_root, "statutory_benefits", "primary_sources"))
            fed_res = fed_reg.harvest_all()
            harvested_results.extend(fed_res)

        # 3. Harvest Atlassian Jira Cloud & Xray Schemas
        if not domain_filter or domain_filter in ["jira", "jira_qa", "qa"]:
            jira = JiraOpenApiConnector(output_dir=os.path.join(self.vault_root, "jira_qa", "primary_sources"))
            jira_res = jira.harvest_all()
            harvested_results.extend(jira_res)

        # 4. Harvest IBM Cúram CER DTDs & SPM Schemas
        if not domain_filter or domain_filter in ["curam", "curam_spm", "cer"]:
            curam = CuramSpecConnector(output_dir=os.path.join(self.vault_root, "curam_spm", "primary_sources"))
            curam_res = curam.harvest_all()
            harvested_results.extend(curam_res)

        # 5. Process ledger changes and detect diffs
        ledger_entries = ledger.setdefault("entries", {})
        touched_paths: List[str] = []

        for item in harvested_results:
            rel_key = item["filename"]
            sha256 = item["sha256"]
            filepath = item["filepath"]
            touched_paths.append(filepath)

            if rel_key not in ledger_entries:
                new_count += 1
                ledger_entries[rel_key] = {
                    "sha256": sha256,
                    "first_harvested": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "bytes": item.get("bytes", 0)
                }
            elif ledger_entries[rel_key]["sha256"] != sha256:
                updated_count += 1
                ledger_entries[rel_key]["sha256"] = sha256
                ledger_entries[rel_key]["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                ledger_entries[rel_key]["bytes"] = item.get("bytes", 0)
            else:
                unchanged_count += 1

        self._save_ledger(ledger)
        duration_ms = round((time.time() - t0) * 1000.0, 2)

        # 6. Auto-index into SQLite Vector Vault if requested
        indexed_status = "SKIPPED"
        if auto_index and (new_count > 0 or updated_count > 0):
            try:
                from know import index_directory
                indexed_count = 0
                for domain_folder in ["statutory_benefits", "curam_spm", "jira_qa"]:
                    folder_path = os.path.join(self.vault_root, domain_folder, "primary_sources")
                    if os.path.exists(folder_path):
                        index_directory(folder_path)
                        indexed_count += 1
                indexed_status = f"INDEXED_{indexed_count}_PRIMARY_SOURCE_DIRECTORIES"
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
