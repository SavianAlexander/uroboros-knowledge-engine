import sqlite3
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
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

"""
SQLite Repository for Persistent Crawler Jobs, URL Frontier Queue & Document Archives.
Ensures crash-resilience, ACID transactions, and zero duplicate crawls.
"""

def init_crawler_schema(conn: sqlite3.Connection):
    """Initialize relational crawler schema with indexes."""
    conn.execute("""
    CREATE TABLE IF NOT EXISTS crawler_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        seed_urls TEXT NOT NULL,
        config_json TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        pages_visited INTEGER NOT NULL DEFAULT 0,
        documents_downloaded INTEGER NOT NULL DEFAULT 0,
        chunks_indexed INTEGER NOT NULL DEFAULT 0,
        entities_extracted INTEGER NOT NULL DEFAULT 0,
        tables_extracted INTEGER NOT NULL DEFAULT 0,
        triplets_extracted INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crawler_jobs_status ON crawler_jobs(status);")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS crawler_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        depth INTEGER NOT NULL DEFAULT 0,
        priority INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'QUEUED',
        retry_count INTEGER NOT NULL DEFAULT 0,
        content_type TEXT DEFAULT '',
        sha256_hash TEXT DEFAULT '',
        error_message TEXT,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES crawler_jobs(id) ON DELETE CASCADE,
        UNIQUE(job_id, url)
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crawler_urls_queue ON crawler_urls(job_id, status, priority DESC, depth ASC);")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS crawler_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        content_type TEXT NOT NULL,
        content_text TEXT NOT NULL,
        file_path TEXT,
        file_size_bytes INTEGER DEFAULT 0,
        merkle_sha256 TEXT NOT NULL,
        merkle_dag_root TEXT DEFAULT '',
        chunk_count INTEGER DEFAULT 0,
        entities_json TEXT DEFAULT '{}',
        tables_json TEXT DEFAULT '[]',
        triplets_json TEXT DEFAULT '[]',
        metadata_json TEXT DEFAULT '{}',
        crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES crawler_jobs(id) ON DELETE CASCADE,
        UNIQUE(job_id, url)
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crawler_documents_job ON crawler_documents(job_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crawler_documents_merkle ON crawler_documents(merkle_sha256);")

    # Dynamic migrations for existing databases on disk
    for col, col_def in [
        ("merkle_dag_root", "TEXT DEFAULT ''"),
        ("entities_json", "TEXT DEFAULT '{}'"),
        ("tables_json", "TEXT DEFAULT '[]'"),
        ("triplets_json", "TEXT DEFAULT '[]'"),
        ("metadata_json", "TEXT DEFAULT '{}'")
    ]:
        try:
            conn.execute(f"ALTER TABLE crawler_documents ADD COLUMN {col} {col_def};")
        except sqlite3.OperationalError:
            pass

    for col, col_def in [
        ("entities_extracted", "INTEGER NOT NULL DEFAULT 0"),
        ("tables_extracted", "INTEGER NOT NULL DEFAULT 0"),
        ("triplets_extracted", "INTEGER NOT NULL DEFAULT 0")
    ]:
        try:
            conn.execute(f"ALTER TABLE crawler_jobs ADD COLUMN {col} {col_def};")
        except sqlite3.OperationalError:
            pass

    conn.commit()

def create_job(conn: sqlite3.Connection, job: CrawlJob) -> int:
    """Create a new crawler job and enqueue its seed URLs."""
    init_crawler_schema(conn)
    cur = conn.execute("""
    INSERT INTO crawler_jobs (name, seed_urls, config_json, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job.name,
        json.dumps(job.seed_urls),
        job.config.to_json(),
        job.status,
        datetime.now(timezone.utc).isoformat(),
        datetime.now(timezone.utc).isoformat()
    ))
    job_id = cur.lastrowid

    # Enqueue seed URLs
    for url in job.seed_urls:
        if url and url.strip():
            conn.execute("""
            INSERT OR IGNORE INTO crawler_urls (job_id, url, depth, priority, status)
            VALUES (?, ?, 0, 10, 'QUEUED')
            """, (job_id, url.strip()))

    conn.commit()
    return job_id

def get_job(conn: sqlite3.Connection, job_id: int) -> Optional[CrawlJob]:
    """Retrieve crawler job by ID."""
    row = conn.execute("SELECT * FROM crawler_jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        return None
    
    # Handle older schema columns gracefully
    return CrawlJob(
        id=row["id"],
        name=row["name"],
        seed_urls=json.loads(row["seed_urls"]),
        config=CrawlConfig.from_json(row["config_json"]),
        status=row["status"],
        pages_visited=row["pages_visited"],
        documents_downloaded=row["documents_downloaded"],
        chunks_indexed=row["chunks_indexed"],
        entities_extracted=row["entities_extracted"] if "entities_extracted" in row.keys() else 0,
        tables_extracted=row["tables_extracted"] if "tables_extracted" in row.keys() else 0,
        triplets_extracted=row["triplets_extracted"] if "triplets_extracted" in row.keys() else 0,
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

def list_jobs(conn: sqlite3.Connection) -> List[CrawlJob]:
    """List all crawler jobs in descending order of creation."""
    init_crawler_schema(conn)
    rows = conn.execute("SELECT * FROM crawler_jobs ORDER BY id DESC").fetchall()
    jobs = []
    for row in rows:
        jobs.append(CrawlJob(
            id=row["id"],
            name=row["name"],
            seed_urls=json.loads(row["seed_urls"]),
            config=CrawlConfig.from_json(row["config_json"]),
            status=row["status"],
            pages_visited=row["pages_visited"],
            documents_downloaded=row["documents_downloaded"],
            chunks_indexed=row["chunks_indexed"],
            entities_extracted=row["entities_extracted"] if "entities_extracted" in row.keys() else 0,
            tables_extracted=row["tables_extracted"] if "tables_extracted" in row.keys() else 0,
            triplets_extracted=row["triplets_extracted"] if "triplets_extracted" in row.keys() else 0,
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        ))
    return jobs

def update_job_status(conn: sqlite3.Connection, job_id: int, status: str):
    """Update lifecycle status of a crawler job."""
    conn.execute("""
    UPDATE crawler_jobs 
    SET status = ?, updated_at = ?
    WHERE id = ?
    """, (status, datetime.now(timezone.utc).isoformat(), job_id))
    conn.commit()

def increment_job_metrics(
    conn: sqlite3.Connection,
    job_id: int,
    visited_inc: int = 0,
    docs_inc: int = 0,
    chunks_inc: int = 0,
    entities_inc: int = 0,
    tables_inc: int = 0,
    triplets_inc: int = 0
):
    """Atomically increment job execution metrics."""
    conn.execute("""
    UPDATE crawler_jobs 
    SET pages_visited = pages_visited + ?,
        documents_downloaded = documents_downloaded + ?,
        chunks_indexed = chunks_indexed + ?,
        entities_extracted = entities_extracted + ?,
        tables_extracted = tables_extracted + ?,
        triplets_extracted = triplets_extracted + ?,
        updated_at = ?
    WHERE id = ?
    """, (visited_inc, docs_inc, chunks_inc, entities_inc, tables_inc, triplets_inc, datetime.now(timezone.utc).isoformat(), job_id))
    conn.commit()

def enqueue_urls(conn: sqlite3.Connection, job_id: int, urls: List[Tuple[str, int, int]]) -> int:
    """
    Bulk enqueue newly discovered URLs with depth and priority.
    Returns the number of genuinely new URLs added (deduplicated).
    """
    added = 0
    for url, depth, priority in urls:
        clean_url = url.strip()
        if not clean_url:
            continue
        cur = conn.execute("""
        INSERT OR IGNORE INTO crawler_urls (job_id, url, depth, priority, status)
        VALUES (?, ?, ?, ?, 'QUEUED')
        """, (job_id, clean_url, depth, priority))
        if cur.rowcount > 0:
            added += 1
    conn.commit()
    return added

def pop_next_url(conn: sqlite3.Connection, job_id: int) -> Optional[CrawlUrlItem]:
    """Fetch next queued URL atomically and set status to FETCHING."""
    row = conn.execute("""
    SELECT * FROM crawler_urls 
    WHERE job_id = ? AND status = 'QUEUED'
    ORDER BY priority DESC, depth ASC, id ASC
    LIMIT 1
    """, (job_id,)).fetchone()

    if not row:
        return None

    url_id = row["id"]
    conn.execute("UPDATE crawler_urls SET status = 'FETCHING' WHERE id = ?", (url_id,))
    conn.commit()

    return CrawlUrlItem(
        id=row["id"],
        job_id=row["job_id"],
        url=row["url"],
        depth=row["depth"],
        priority=row["priority"],
        status=URL_STATUS_FETCHING,
        retry_count=row["retry_count"],
        content_type=row["content_type"] or "",
        sha256_hash=row["sha256_hash"] or "",
        error_message=row["error_message"],
        discovered_at=row["discovered_at"]
    )

def mark_url_result(
    conn: sqlite3.Connection,
    url_id: int,
    status: str,
    content_type: str = "",
    sha256_hash: str = "",
    error_message: Optional[str] = None
):
    """Mark the processing result for a URL item."""
    conn.execute("""
    UPDATE crawler_urls 
    SET status = ?, content_type = ?, sha256_hash = ?, error_message = ?
    WHERE id = ?
    """, (status, content_type, sha256_hash, error_message, url_id))
    conn.commit()

def save_crawled_document(conn: sqlite3.Connection, doc: CrawledDocument) -> int:
    """Save parsed document with Merkle DAG hash and knowledge entities into crawler_documents."""
    cur = conn.execute("""
    INSERT OR REPLACE INTO crawler_documents (
        job_id, url, title, content_type, content_text,
        file_path, file_size_bytes, merkle_sha256, merkle_dag_root, chunk_count,
        entities_json, tables_json, triplets_json, metadata_json, crawled_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc.job_id,
        doc.url,
        doc.title,
        doc.content_type,
        doc.content_text,
        doc.file_path,
        doc.file_size_bytes,
        doc.merkle_sha256,
        doc.merkle_dag_root,
        doc.chunk_count,
        doc.entities_json,
        doc.tables_json,
        doc.triplets_json,
        json.dumps(doc.metadata),
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    return cur.lastrowid

def get_job_documents(conn: sqlite3.Connection, job_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve saved documents for a specific job."""
    rows = conn.execute("""
    SELECT * FROM crawler_documents WHERE job_id = ? ORDER BY id DESC LIMIT ?
    """, (job_id, limit)).fetchall()
    return [dict(r) for r in rows]
