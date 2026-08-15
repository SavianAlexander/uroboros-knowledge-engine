import time
import threading
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
from src.domain.universal_crawler.phantom_stealth import PhantomStealthEngine, PhantomStealthSession
from src.domain.universal_crawler.void_stealth import VoidStealthSession
from src.domain.universal_crawler.browser_stealth import QuantumStealthSession, BrowserStealthSession
from src.domain.universal_crawler.neuromorphic_stealth import OmniStealthSession
from src.domain.universal_crawler.deep_extractor import DeepKnowledgeHarvester
from src.domain.universal_crawler.merkle_dag import MerkleDAG
from src.domain.universal_crawler.frontier import UrlFrontier
from src.domain.universal_crawler.rate_limiter import DomainRateLimiter
from src.domain.universal_crawler.extractor import (
    extract_links_from_html,
    extract_urls_from_sitemap_xml,
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
Asynchronous Multi-Worker Crawl Swarm with Apex Phantom-Tier Stealth & Deep Knowledge Extraction.
"""

class CrawlSwarm:
    """Enterprise multi-threaded concurrent crawl swarm with deep knowledge harvesting."""

    def __init__(self, db_path: str, max_workers: int = 4):
        self.db_path = db_path
        self.max_workers = max_workers
        self.rate_limiter = DomainRateLimiter(default_interval=0.8)
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Telemetry metrics
        self.stats = {
            "start_time": 0.0,
            "pages_crawled": 0,
            "docs_saved": 0,
            "chunks_indexed": 0,
            "entities_found": 0,
            "tables_found": 0,
            "triplets_found": 0,
            "bytes_downloaded": 0,
            "active_threads": 0,
            "latencies_ms": []
        }

    def request_stop(self):
        """Signal all workers in the swarm to gracefully stop."""
        self._stop_event.set()

    def _worker_loop(self, job_id: int, config: CrawlConfig, files_dir: Path, worker_id: int = 1):
        """Worker thread execution loop."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")

        # Choose Network Session Adapter
        mode = (config.stealth_mode or "adaptive_session").lower()
        if mode in ("adaptive_session", "omni", "omni_sovereign"):
            session = OmniStealthSession(session_seed=f"swarm_{worker_id}")
            fetch_fn = session.omni_fetch
        elif mode in ("async_pool", "quantum"):
            session = QuantumStealthSession()
            fetch_fn = session.quantum_fetch
        elif mode in ("proxy_rotation", "void"):
            session = VoidStealthSession()
            fetch_fn = session.void_fetch
        elif mode in ("browser_automation", "phantom"):
            session = PhantomStealthSession()
            fetch_fn = session.phantom_fetch
        elif mode in ("rotating_headers", "ghost"):
            session = GhostStealthSession()
            fetch_fn = session.ghost_fetch
        else:
            std_session = StealthNetworkSession(mode=config.stealth_mode)
            fetch_fn = std_session.fetch

        with self._lock:
            self.stats["active_threads"] += 1

        try:
            while not self._stop_event.is_set():
                with self._lock:
                    url_item = pop_next_url(conn, job_id)

                if not url_item:
                    break

                url = url_item.url
                depth = url_item.depth
                is_target_file = UrlFrontier.is_target_file_asset(url, config.file_extensions)

                # Acquire per-domain polite rate limit slot
                min_delay = 0.5 if config.stealth_mode in ("phantom", "ghost") else (0.2 if config.stealth_mode == "balanced" else 0.05)
                self.rate_limiter.acquire(url, min_delay=min_delay)

                # Fetch via Stealth Engine
                res_tuple = fetch_fn(url)
                if len(res_tuple) == 5:
                    content_bytes, content_type, status_code, err, telemetry = res_tuple
                else:
                    content_bytes, content_type, status_code, err = res_tuple
                    telemetry = {}

                if not content_bytes or status_code >= 400:
                    with self._lock:
                        mark_url_result(conn, url_item.id, URL_STATUS_FAILED, content_type=content_type or "", error_message=err or f"HTTP {status_code}")
                    continue

                file_size = len(content_bytes)
                file_path_on_disk = None

                # 1. XML Sitemap Discovery
                if "xml" in (content_type or "").lower() or url.endswith(".xml"):
                    xml_str = content_bytes.decode("utf-8", errors="ignore")
                    discovered_urls = extract_urls_from_sitemap_xml(xml_str, url)
                    to_enqueue = []
                    for link in discovered_urls:
                        if UrlFrontier.is_allowed_domain(link, config.allowed_domains):
                            is_file = UrlFrontier.is_target_file_asset(link, config.file_extensions)
                            prio = UrlFrontier.calculate_priority(link, depth + 1, is_file=is_file)
                            to_enqueue.append((link, depth + 1, prio))
                    with self._lock:
                        enqueue_urls(conn, job_id, to_enqueue)

                # 2. Binary / PDF Files
                if is_target_file or "pdf" in (content_type or "").lower():
                    parsed_url = urlparse(url)
                    raw_filename = Path(parsed_url.path).name or f"asset_{url_item.id}.pdf"
                    target_file = files_dir / raw_filename
                    with open(target_file, "wb") as f:
                        f.write(content_bytes)
                    file_path_on_disk = str(target_file)

                # 3. Discovered Hyperlinks for HTML
                if "html" in (content_type or "").lower() and depth < config.max_depth:
                    html_str = content_bytes.decode("utf-8", errors="ignore")
                    new_links = extract_links_from_html(html_str, url)
                    to_enqueue = []
                    for link in new_links:
                        if UrlFrontier.is_allowed_domain(link, config.allowed_domains):
                            is_file = UrlFrontier.is_target_file_asset(link, config.file_extensions)
                            prio = UrlFrontier.calculate_priority(link, depth + 1, is_file=is_file)
                            to_enqueue.append((link, depth + 1, prio))
                    with self._lock:
                        enqueue_urls(conn, job_id, to_enqueue)

                # Deep Knowledge Harvesting (Tables, Entities, Triplets)
                harvested = DeepKnowledgeHarvester.harvest(content_bytes, content_type or "text/html", url)
                title = harvested["title"]
                clean_text = harvested["text"]
                tables = harvested["tables"]
                entities = harvested["entities"]
                triplets = harvested["triplets"]
                meta = harvested["metadata"]

                # Hierarchical Merkle DAG Calculation
                dag_info = MerkleDAG.generate_document_dag(clean_text, url, {"job_id": job_id})
                merkle_dag_root = dag_info["merkle_root"]

                doc_meta = {
                    "job_id": job_id,
                    "content_type": content_type,
                    "status_code": status_code,
                    "depth": depth,
                    "stats": harvested["stats"],
                    **meta
                }
                merkle_hash = calculate_merkle_provenance(clean_text, url, doc_meta)

                # Save Document with Deep Knowledge Graph Data
                doc_obj = CrawledDocument(
                    job_id=job_id,
                    url=url,
                    title=title,
                    content_type=content_type or "text/html",
                    content_text=clean_text,
                    file_path=file_path_on_disk,
                    file_size_bytes=file_size,
                    merkle_sha256=merkle_hash,
                    merkle_dag_root=merkle_dag_root,
                    chunk_count=max(1, len(clean_text) // 500),
                    entities_json=json.dumps(entities, ensure_ascii=False),
                    tables_json=json.dumps(tables, ensure_ascii=False),
                    triplets_json=json.dumps(triplets, ensure_ascii=False),
                    metadata=doc_meta
                )

                total_ent = sum(len(v) for v in entities.values())
                total_tab = len(tables)
                total_trip = len(triplets)

                with self._lock:
                    save_crawled_document(conn, doc_obj)
                    mark_url_result(conn, url_item.id, URL_STATUS_VISITED, content_type=content_type, sha256_hash=merkle_hash)
                    increment_job_metrics(
                        conn,
                        job_id,
                        visited_inc=1,
                        docs_inc=1 if file_path_on_disk else 0,
                        chunks_inc=max(1, len(clean_text) // 500),
                        entities_inc=total_ent,
                        tables_inc=total_tab,
                        triplets_inc=total_trip
                    )

                    # Update Swarm Stats
                    self.stats["pages_crawled"] += 1
                    if file_path_on_disk:
                        self.stats["docs_saved"] += 1
                    self.stats["chunks_indexed"] += max(1, len(clean_text) // 500)
                    self.stats["entities_found"] += total_ent
                    self.stats["tables_found"] += total_tab
                    self.stats["triplets_found"] += total_trip
                    self.stats["bytes_downloaded"] += file_size
                    self.stats["latencies_ms"].append(telemetry.get("latency_ms", 0.0))
                    if len(self.stats["latencies_ms"]) > 100:
                        self.stats["latencies_ms"].pop(0)

                # Automatic RAG Vault & Core Knowledge Engine Ingestion
                if config.auto_rag_ingest and clean_text.strip():
                    try:
                        from src.domain.universal_crawler.auto_rag_bridge import AutoRAGBridge
                        with self._lock:
                            AutoRAGBridge.ingest_crawled_document(conn, doc_obj)
                    except Exception:
                        pass

                    try:
                        from src.domain.pr_legal_engine import PRLegalEngine
                        chunks = PRLegalEngine.parse_legal_ast_document(
                            clean_text,
                            title,
                            {"source_origin": f"Phantom Swarm #{job_id}", "source_url": url}
                        )
                        with self._lock:
                            for c in chunks:
                                c_meta = c["metadata"]
                                conn.execute("""
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
                                    f"Phantom Swarm #{job_id}",
                                    url,
                                    c["content"],
                                    c["merkle_sha256"]
                                ))
                            conn.commit()
                    except Exception:
                        pass

        finally:
            with self._lock:
                self.stats["active_threads"] -= 1
            conn.close()

    def run(self, job_id: int, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """Launch concurrent worker swarm."""
        master_conn = sqlite3.connect(self.db_path)
        master_conn.row_factory = sqlite3.Row
        job = get_job(master_conn, job_id)
        if not job:
            master_conn.close()
            return {"status": "error", "message": f"Job ID {job_id} not found"}

        update_job_status(master_conn, job_id, JOB_STATUS_RUNNING)
        cfg = job.config
        output_path = Path(cfg.output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        files_dir = output_path / f"job_{job_id}_files"
        files_dir.mkdir(exist_ok=True)

        self.stats["start_time"] = time.time()
        threads = []

        for i in range(self.max_workers):
            t = threading.Thread(
                target=self._worker_loop,
                args=(job_id, cfg, files_dir, i+1),
                name=f"OmniWorker-{job_id}-{i+1}",
                daemon=True
            )
            threads.append(t)
            t.start()

        while any(t.is_alive() for t in threads) and not self._stop_event.is_set():
            time.sleep(0.5)
            if progress_callback:
                elapsed = max(0.1, time.time() - self.stats["start_time"])
                avg_lat = sum(self.stats["latencies_ms"]) / len(self.stats["latencies_ms"]) if self.stats["latencies_ms"] else 0.0
                progress_callback({
                    "job_id": job_id,
                    "pages_crawled": self.stats["pages_crawled"],
                    "docs_saved": self.stats["docs_saved"],
                    "entities_found": self.stats["entities_found"],
                    "tables_found": self.stats["tables_found"],
                    "triplets_found": self.stats["triplets_found"],
                    "throughput_pages_sec": self.stats["pages_crawled"] / elapsed,
                    "throughput_kb_sec": (self.stats["bytes_downloaded"] / 1024.0) / elapsed,
                    "active_threads": self.stats["active_threads"],
                    "avg_latency_ms": avg_lat
                })

        for t in threads:
            t.join(timeout=2.0)

        final_status = JOB_STATUS_PAUSED if self._stop_event.is_set() else JOB_STATUS_COMPLETED
        update_job_status(master_conn, job_id, final_status)
        master_conn.close()

        return {
            "status": final_status,
            "job_id": job_id,
            "pages_crawled": self.stats["pages_crawled"],
            "docs_saved": self.stats["docs_saved"],
            "entities_found": self.stats["entities_found"],
            "tables_found": self.stats["tables_found"],
            "triplets_found": self.stats["triplets_found"],
            "chunks_indexed": self.stats["chunks_indexed"],
            "bytes_downloaded": self.stats["bytes_downloaded"]
        }
