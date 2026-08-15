import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

"""
Enhanced Data models and state definitions for the Universal Resilient Crawler & Job Engine.
"""

JOB_STATUS_PENDING = "PENDING"
JOB_STATUS_RUNNING = "RUNNING"
JOB_STATUS_PAUSED = "PAUSED"
JOB_STATUS_COMPLETED = "COMPLETED"
JOB_STATUS_FAILED = "FAILED"

URL_STATUS_QUEUED = "QUEUED"
URL_STATUS_FETCHING = "FETCHING"
URL_STATUS_VISITED = "VISITED"
URL_STATUS_FAILED = "FAILED"
URL_STATUS_SKIPPED = "SKIPPED"

@dataclass
class CrawlConfig:
    max_pages: int = 100
    max_depth: int = 3
    # Supported modes: 'adaptive_session' (alias 'omni'), 'browser_automation' (alias 'phantom'), 
    # 'proxy_rotation' (alias 'void'), 'async_pool' (alias 'quantum'), 'rotating_headers' (alias 'ghost'), 'direct'
    stealth_mode: str = "omni"
    persona: str = "Legal_Scholar" # 'Legal_Scholar', 'Academic_Auditor', 'Technical_Researcher'
    allowed_domains: List[str] = field(default_factory=list)
    download_files: bool = True     # Download PDFs, DOCXs, etc.
    file_extensions: List[str] = field(default_factory=lambda: [".pdf", ".docx", ".txt", ".md", ".json", ".html"])
    auto_rag_ingest: bool = True
    deep_knowledge_harvest: bool = True # Extract entities, tables, and triplets
    output_dir: str = "vault/crawler_downloads"

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> 'CrawlConfig':
        if not json_str:
            return cls()
        try:
            data = json.loads(json_str)
            return cls(**data)
        except Exception:
            return cls()

@dataclass
class CrawlJob:
    id: Optional[int] = None
    name: str = "Default Crawl Job"
    seed_urls: List[str] = field(default_factory=list)
    config: CrawlConfig = field(default_factory=CrawlConfig)
    status: str = JOB_STATUS_PENDING
    pages_visited: int = 0
    documents_downloaded: int = 0
    chunks_indexed: int = 0
    entities_extracted: int = 0
    tables_extracted: int = 0
    triplets_extracted: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class CrawlUrlItem:
    id: Optional[int] = None
    job_id: int = 0
    url: str = ""
    depth: int = 0
    priority: int = 0
    status: str = URL_STATUS_QUEUED
    retry_count: int = 0
    content_type: str = ""
    sha256_hash: str = ""
    error_message: Optional[str] = None
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class CrawledDocument:
    id: Optional[int] = None
    job_id: int = 0
    url: str = ""
    title: str = ""
    content_type: str = "text/html"
    content_text: str = ""
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    merkle_sha256: str = ""
    merkle_dag_root: str = ""
    chunk_count: int = 0
    entities_json: str = "{}"
    tables_json: str = "[]"
    triplets_json: str = "[]"
    metadata: Dict[str, Any] = field(default_factory=dict)
    crawled_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
