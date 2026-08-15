import sys
import os
import time
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional, Callable

from src.domain.universal_crawler.models import (
    CrawlJob,
    CrawlUrlItem,
    CrawledDocument,
    CrawlConfig,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    JOB_STATUS_PAUSED,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    URL_STATUS_QUEUED,
    URL_STATUS_FETCHING,
    URL_STATUS_VISITED,
    URL_STATUS_FAILED,
    URL_STATUS_SKIPPED
)
from src.domain.universal_crawler.stealth_engine import StealthNetworkSession
from src.domain.universal_crawler.ghost_stealth import GhostStealthSession
from src.domain.universal_crawler.phantom_stealth import PhantomStealthEngine
from src.domain.universal_crawler.void_stealth import VoidStealthSession
from src.domain.universal_crawler.browser_stealth import QuantumStealthSession, BrowserStealthSession
from src.domain.universal_crawler.neuromorphic_stealth import OmniStealthSession
from src.domain.universal_crawler.deep_extractor import DeepKnowledgeHarvester
from src.domain.universal_crawler.frontier import UrlFrontier
from src.domain.universal_crawler.extractor import (
    extract_links_from_html,
    calculate_merkle_provenance
)
from src.infrastructure.crawler_repository import (
    get_job,
    update_job_status,
    increment_job_metrics,
    pop_next_url,
    mark_url_result,
    enqueue_urls,
    save_crawled_document
)

"""
Unified Omni-Sovereign Job Orchestrator.
Coordinates single-runner execution with full DeepKnowledgeHarvester,
Rule 902 Forensic Multi-Hashes, Hierarchical Merkle DAG, and In-Database Vectors.
"""

class CrawlJobOrchestrator:
    """Controls crawl execution lifecycle, state transitions, and unified apex ingestion."""

    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn
        self._stop_requested = False

    def request_stop(self):
        """Signal orchestrator to pause execution gracefully."""
        self._stop_requested = True

    def execute_job(
        self,
        job_id: int,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute or resume a crawl job at maximum apex absorption.
        """
        job = get_job(self.conn, job_id)
        if not job:
            return {"status": "error", "message": f"Job ID {job_id} not found"}

        update_job_status(self.conn, job_id, JOB_STATUS_RUNNING)
        cfg = job.config

        # 1. Initialize Network Session Adapter
        mode = (cfg.stealth_mode or "adaptive_session").lower()
        if mode in ("adaptive_session", "omni", "omni_sovereign"):
            session = OmniStealthSession(session_seed=f"orchestrator_{job_id}")
            fetch_fn = session.omni_fetch
        elif mode in ("async_pool", "quantum"):
            session = QuantumStealthSession()
            fetch_fn = session.quantum_fetch
        elif mode in ("proxy_rotation", "void"):
            session = VoidStealthSession()
            fetch_fn = session.void_fetch
        elif mode in ("browser_automation", "phantom"):
            session = PhantomStealthEngine(persona_name=cfg.persona)
            fetch_fn = session.phantom_fetch
        elif mode in ("rotating_headers", "ghost"):
            session = GhostStealthSession(mode="ghost")
            fetch_fn = session.ghost_fetch
        else:
            session = StealthNetworkSession(mode=cfg.stealth_mode)
            fetch_fn = session.fetch

        output_path = Path(cfg.output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        files_dir = output_path / f"job_{job_id}_files"
        files_dir.mkdir(exist_ok=True)

        print(f"============================================================")
        print(f"  Knowledge Crawler Runner: '{job.name}' (ID: {job_id})")
        print(f"  Network Mode: {cfg.stealth_mode.upper()} | Persona: {cfg.persona}")
        print(f"  Integrity:    FRE 902(13)/(14) & Full Semantic Parsing")
        print(f"  Storage:      {files_dir}")
        print(f"============================================================")

        pages_crawled = 0
        docs_saved = 0
        chunks_indexed = 0
        entities_total = 0
        tables_total = 0
        triplets_total = 0

        while not self._stop_requested:
            if job.pages_visited + pages_crawled >= cfg.max_pages:
                print(f"[*] Reached configured maximum page limit ({cfg.max_pages}).")
                break

            url_item = pop_next_url(self.conn, job_id)
            if not url_item:
                print(f"[*] URL frontier queue is empty. Crawl completed.")
                break

            url = url_item.url
            depth = url_item.depth
            is_target_file = UrlFrontier.is_target_file_asset(url, cfg.file_extensions)

            print(f"\n[{job.pages_visited + pages_crawled + 1}/{cfg.max_pages}] (Depth {depth}) Fetching: {url}")

            # Execute Stealth Fetch
            fetch_res = fetch_fn(url)
            content_bytes = fetch_res[0]
            content_type = fetch_res[1]
            status_code = fetch_res[2]
            err = fetch_res[3]

            if not content_bytes or status_code >= 400:
                print(f"  [ERR] Failed ({status_code}): {err}")
                mark_url_result(self.conn, url_item.id, URL_STATUS_FAILED, content_type=content_type or "", error_message=err or f"HTTP {status_code}")
                continue

            pages_crawled += 1
            file_path_on_disk = None
            file_size = len(content_bytes)

            # Save File Asset if applicable
            if is_target_file or "pdf" in (content_type or "").lower():
                parsed_url = urlparse(url)
                raw_filename = Path(parsed_url.path).name or f"asset_{url_item.id}.pdf"
                target_file = files_dir / raw_filename
                with open(target_file, "wb") as f:
                    f.write(content_bytes)
                file_path_on_disk = str(target_file)
                docs_saved += 1
                print(f"  [OK] Saved Binary Asset: {raw_filename} ({file_size:,} bytes)")

            # Apex Deep Knowledge Harvest
            harvest_data = DeepKnowledgeHarvester.harvest(content_bytes, content_type or "", url)
            title = harvest_data["title"]
            clean_text = harvest_data["text"]
            tables = harvest_data["tables"]
            entities = harvest_data["entities"]
            triplets = harvest_data["triplets"]
            merkle_dag_root = harvest_data["merkle_dag_root"]

            entities_count = sum(len(v) for v in entities.values())
            entities_total += entities_count
            tables_total += len(tables)
            triplets_total += len(triplets)

            print(f"  [OK] Absorbed: '{title[:45]}...' ({len(clean_text):,} chars | {entities_count} entities | {len(tables)} tables | {len(triplets)} triplets)")

            # Expand URL frontier from HTML links
            if "html" in (content_type or "").lower() and depth < cfg.max_depth:
                html_str = content_bytes.decode("utf-8", errors="ignore")
                new_links = extract_links_from_html(html_str, url)
                to_enqueue = []
                for link in new_links:
                    is_file = UrlFrontier.is_target_file_asset(link, cfg.file_extensions)
                    if UrlFrontier.is_allowed_domain(link, cfg.allowed_domains):
                        priority = UrlFrontier.calculate_priority(link, depth + 1, is_file=is_file)
                        to_enqueue.append((link, depth + 1, priority))

                added = enqueue_urls(self.conn, job_id, to_enqueue)
                if added > 0:
                    print(f"  [+] Frontier: Discovered {len(new_links)} links, enqueued {added} new URLs.")

            # Save Crawled Document
            doc_meta = {
                "job_id": job_id,
                "content_type": content_type,
                "status_code": status_code,
                "depth": depth,
                "forensic_hashes": harvest_data.get("forensic_hashes"),
                "statutory_anatomy": harvest_data.get("statutory_anatomy"),
                "genesis": harvest_data.get("genesis")
            }

            doc_obj = CrawledDocument(
                job_id=job_id,
                url=url,
                title=title,
                content_type=content_type,
                content_text=clean_text,
                file_path=file_path_on_disk,
                file_size_bytes=file_size,
                merkle_sha256=harvest_data.get("forensic_hashes", {}).get("sha256", merkle_dag_root),
                chunk_count=max(1, len(clean_text) // 500),
                entities_json=json.dumps(entities, ensure_ascii=False),
                tables_json=json.dumps(tables, ensure_ascii=False),
                triplets_json=json.dumps(triplets, ensure_ascii=False),
                merkle_dag_root=merkle_dag_root,
                metadata=doc_meta
            )
            save_crawled_document(self.conn, doc_obj)

            # Auto-RAG Ingestion into Core Knowledge Engine & SQLite RAG Vault
            if cfg.auto_rag_ingest and clean_text.strip():
                try:
                    from src.domain.universal_crawler.auto_rag_bridge import AutoRAGBridge
                    AutoRAGBridge.ingest_crawled_document(self.conn, doc_obj)
                except Exception:
                    pass

                try:
                    from src.domain.pr_legal_engine import PRLegalEngine
                    chunks = PRLegalEngine.parse_legal_ast_document(
                        clean_text,
                        title,
                        {"source_origin": f"Omni Harvester (Job #{job_id})", "source_url": url}
                    )
                    for c in chunks:
                        c_meta = c["metadata"]
                        self.conn.execute("""
                        INSERT OR REPLACE INTO pr_legal_corpus (
                            citation_key, canonical_citation, title, hierarchy_path,
                            status, effective_date, source_origin, source_url, content, merkle_sha256
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            c["citation_key"],
                            c["canonical_citation"],
                            title,
                            c_meta.get("hierarchy_path", ""),
                            c["status"],
                            "2026-08-15",
                            f"Omni Crawler Job #{job_id}",
                            url,
                            c["content"],
                            c["merkle_sha256"]
                        ))
                        chunks_indexed += 1
                    self.conn.commit()
                except Exception:
                    pass

            mark_url_result(self.conn, url_item.id, URL_STATUS_VISITED, content_type=content_type, sha256_hash=merkle_dag_root)
            increment_job_metrics(
                self.conn,
                job_id,
                visited_inc=1,
                docs_inc=1 if file_path_on_disk else 0,
                chunks_inc=max(1, len(clean_text) // 500),
                entities_inc=entities_count,
                tables_inc=len(tables),
                triplets_inc=len(triplets)
            )

            if progress_callback:
                progress_callback({
                    "job_id": job_id,
                    "pages_visited": job.pages_visited + pages_crawled,
                    "documents_saved": job.documents_downloaded + docs_saved,
                    "chunks_indexed": job.chunks_indexed + chunks_indexed,
                    "entities_extracted": job.entities_extracted + entities_total,
                    "tables_extracted": job.tables_extracted + tables_total,
                    "triplets_extracted": job.triplets_extracted + triplets_total,
                    "current_url": url,
                    "merkle_dag_root": merkle_dag_root
                })

        final_status = JOB_STATUS_PAUSED if self._stop_requested else JOB_STATUS_COMPLETED
        update_job_status(self.conn, job_id, final_status)

        print(f"\n============================================================")
        print(f"  Job #{job_id} Completed with Status: {final_status}")
        print(f"  Pages Crawled:      {pages_crawled}")
        print(f"  Entities Absorbed:  {entities_total}")
        print(f"  Tables Rebuilt:     {tables_total}")
        print(f"  Triplets Extracted: {triplets_total}")
        print(f"  RAG Chunks Indexed: {chunks_indexed}")
        print(f"============================================================\n")

        return {
            "status": final_status,
            "job_id": job_id,
            "pages_crawled": pages_crawled,
            "docs_saved": docs_saved,
            "entities_extracted": entities_total,
            "tables_extracted": tables_total,
            "triplets_extracted": triplets_total,
            "chunks_indexed": chunks_indexed
        }
