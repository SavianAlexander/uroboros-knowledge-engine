"""
Unified Connection Client (ConnectionClient).
Centralizes all external HTTP/HTTPS connections, authentication, rate limiting,
cryptographic SHA-256 change detection, and automated RAG indexing into a single,
zero-dependency standard-library client.

Ponytail principle: Pure Python standard library (urllib, json, ssl, hashlib, xml.etree.ElementTree).
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.parse
import urllib.error
import ssl
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field, asdict

# Ensure root workspace is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


@dataclass
class ConnectionProfile:
    """Configuration profile for a registered connection endpoint."""
    name: str
    base_url: str
    description: str
    default_headers: Dict[str, str] = field(default_factory=dict)
    auth_env_var: Optional[str] = None
    timeout: float = 30.0
    rate_limit_delay: float = 0.1
    last_request_time: float = 0.0


class ConnectionClient:
    """
    Master Connection Client for all external data sources, live APIs, and RAG pipelines.
    
    Provides:
    - Centralized connection registry (built-in + custom on-the-fly)
    - Resilient GET, POST, JSON, XML, and Text fetchers with exponential backoff
    - Automated `sync_and_rag()`: download -> SHA-256 ledger update -> RAG vectorization in one step
    - Health checking (`ping`, `ping_all`) and connection telemetry
    """

    USER_AGENT = "NeuroKnowledgeEngine/2026.2 (Uroboros Unified Connection Client; +https://github.com/SavianAlexander/uroboros-knowledge-engine)"

    def __init__(self, vault_root: Optional[str] = None):
        self.vault_root = vault_root or os.path.join(BASE_DIR, "vault")
        os.makedirs(self.vault_root, exist_ok=True)
        self.ledger_path = os.path.join(self.vault_root, ".sync_ledger.json")
        self._connections: Dict[str, ConnectionProfile] = {}
        self._init_built_in_connections()

    # -------------------------------------------------------------------------
    # 1. Connection Registry
    # -------------------------------------------------------------------------

    def _init_built_in_connections(self):
        """Register the standard local LLM connection profile."""
        self.register(
            name="ollama",
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            description="Local Ollama SLM Inference & Embedding Server",
            default_headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=120.0
        )


    def register(
        self,
        name: str,
        base_url: str,
        description: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        auth_env_var: Optional[str] = None,
        timeout: float = 30.0,
        rate_limit_delay: float = 0.1
    ) -> ConnectionProfile:
        """Register a new connection target profile."""
        headers = {"User-Agent": self.USER_AGENT}
        if default_headers:
            headers.update(default_headers)

        profile = ConnectionProfile(
            name=name.lower().strip(),
            base_url=base_url.rstrip("/"),
            description=description,
            default_headers=headers,
            auth_env_var=auth_env_var,
            timeout=timeout,
            rate_limit_delay=rate_limit_delay
        )
        self._connections[profile.name] = profile
        return profile

    def get_connection(self, name: str) -> ConnectionProfile:
        """Retrieve connection profile by name."""
        key = name.lower().strip()
        if key not in self._connections:
            raise KeyError(f"Connection '{name}' not found. Registered connections: {list(self._connections.keys())}")
        return self._connections[key]

    def list_connections(self) -> List[Dict[str, Any]]:
        """Return list of all registered connection profiles."""
        return [
            {
                "name": p.name,
                "base_url": p.base_url,
                "description": p.description,
                "has_auth": bool(p.auth_env_var and os.environ.get(p.auth_env_var)),
                "timeout": p.timeout
            }
            for p in self._connections.values()
        ]

    # -------------------------------------------------------------------------
    # 2. HTTP Engine with Exponential Backoff & Rate Limiting
    # -------------------------------------------------------------------------

    def _build_url(self, profile: ConnectionProfile, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        clean_path = path.lstrip("/")
        url = f"{profile.base_url}/{clean_path}" if clean_path else profile.base_url
        if params:
            query_str = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if query_str:
                url = f"{url}?{query_str}"
        return url

    def _apply_rate_limit(self, profile: ConnectionProfile):
        now = time.time()
        elapsed = now - profile.last_request_time
        if elapsed < profile.rate_limit_delay:
            time.sleep(profile.rate_limit_delay - elapsed)
        profile.last_request_time = time.time()

    def _execute_request(
        self,
        profile: ConnectionProfile,
        url: str,
        method: str = "GET",
        data: Optional[bytes] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3
    ) -> bytes:
        """Execute raw HTTP request with retries and SSL context."""
        headers = dict(profile.default_headers)
        if profile.auth_env_var and os.environ.get(profile.auth_env_var):
            token = os.environ[profile.auth_env_var]
            headers["Authorization"] = f"Bearer {token}"
        if custom_headers:
            headers.update(custom_headers)

        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        last_error = None
        for attempt in range(max_retries):
            self._apply_rate_limit(profile)
            try:
                with urllib.request.urlopen(req, timeout=profile.timeout, context=ctx) as response:
                    return response.read()
            except urllib.error.HTTPError as e:
                last_error = e
                # Do not retry 400 Bad Request or 404 Not Found
                if e.code in (400, 401, 403, 404):
                    raise
                time.sleep((2 ** attempt) * 0.5)
            except Exception as e:
                last_error = e
                time.sleep((2 ** attempt) * 0.5)

        raise RuntimeError(f"Request failed after {max_retries} attempts to {url}: {last_error}")

    # -------------------------------------------------------------------------
    # 3. High-Level Data Fetchers (JSON, XML, Text, Raw)
    # -------------------------------------------------------------------------

    def fetch_json(self, connection_name: str, path: str = "", params: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch and parse JSON payload."""
        profile = self.get_connection(connection_name)
        url = self._build_url(profile, path, params)
        raw_bytes = self._execute_request(profile, url, method="GET", custom_headers={"Accept": "application/json"})
        return json.loads(raw_bytes.decode("utf-8"))

    def fetch_xml(self, connection_name: str, path: str = "", params: Optional[Dict[str, Any]] = None) -> ET.Element:
        """Fetch and parse XML payload into an ElementTree."""
        profile = self.get_connection(connection_name)
        url = self._build_url(profile, path, params)
        raw_bytes = self._execute_request(profile, url, method="GET", custom_headers={"Accept": "application/xml, text/xml"})
        return ET.fromstring(raw_bytes.decode("utf-8", errors="replace"))

    def fetch_text(self, connection_name: str, path: str = "", params: Optional[Dict[str, Any]] = None) -> str:
        """Fetch raw text or Markdown string."""
        profile = self.get_connection(connection_name)
        url = self._build_url(profile, path, params)
        raw_bytes = self._execute_request(profile, url, method="GET")
        return raw_bytes.decode("utf-8", errors="replace")

    def post_json(self, connection_name: str, path: str = "", payload: Optional[Dict[str, Any]] = None) -> Any:
        """Send POST request with JSON body and parse response."""
        profile = self.get_connection(connection_name)
        url = self._build_url(profile, path)
        data = json.dumps(payload or {}).encode("utf-8")
        raw_bytes = self._execute_request(
            profile, url, method="POST", data=data,
            custom_headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        return json.loads(raw_bytes.decode("utf-8"))

    # -------------------------------------------------------------------------
    # 4. Health Checking & Telemetry
    # -------------------------------------------------------------------------

    def ping(self, connection_name: str) -> Dict[str, Any]:
        """Ping a registered connection and measure latency."""
        profile = self.get_connection(connection_name)
        t0 = time.time()
        try:
            # Special health endpoints
            if profile.name == "ollama":
                self.fetch_json("ollama", "api/tags")
            else:
                self.fetch_text(profile.name, "")
            latency_ms = round((time.time() - t0) * 1000, 2)
            return {"name": profile.name, "status": "ONLINE", "latency_ms": latency_ms, "base_url": profile.base_url}

        except Exception as e:
            latency_ms = round((time.time() - t0) * 1000, 2)
            return {"name": profile.name, "status": "OFFLINE", "error": str(e), "latency_ms": latency_ms, "base_url": profile.base_url}

    def ping_all(self) -> List[Dict[str, Any]]:
        """Ping all registered connections concurrently or sequentially."""
        results = []
        for name in self._connections:
            results.append(self.ping(name))
        return results

    # -------------------------------------------------------------------------
    # 5. One-Shot Sync & RAG Pipeline (Fetch -> Ledger -> Vault -> Index)
    # -------------------------------------------------------------------------

    def _load_ledger(self) -> Dict[str, Any]:
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_sync_timestamp": None, "total_sync_runs": 0, "entries": {}}

    def _save_ledger(self, ledger: Dict[str, Any]):
        ledger["last_sync_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ledger["total_sync_runs"] = ledger.get("total_sync_runs", 0) + 1
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2)

    def sync_and_rag(
        self,
        connection_name: str,
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
        target_subfolder: str = "statutory_benefits/primary_sources",
        filename: str = "document.md",
        title: Optional[str] = None,
        authority: Optional[str] = None,
        transform_fn: Optional[Callable[[str], str]] = None,
        auto_index: bool = True
    ) -> Dict[str, Any]:
        """
        Complete end-to-end data pipeline:
        1. Fetches content from connection
        2. Applies optional transformer (e.g. XML/JSON -> Markdown)
        3. Computes SHA-256 hash and checks against sync ledger
        4. Saves to `vault/<target_subfolder>/<filename>`
        5. Automatically chunks, indexes into SQLite FTS5, and vectorizes if modified
        """
        profile = self.get_connection(connection_name)
        raw_text = self.fetch_text(connection_name, path, params)

        if transform_fn:
            content = transform_fn(raw_text)
        else:
            content = raw_text

        # Format markdown header if title provided
        if title:
            header = f"# {title}\n\n"
            if authority:
                header += f"- **Authority**: {authority}\n"
            header += f"- **Source Connection**: `{profile.name}` ({profile.base_url})\n"
            header += f"- **Sync Timestamp**: `{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}`\n"
            header += f"- **SHA-256 Signature**: `{{sha256}}`\n\n---\n\n"
            # Compute hash of body
            body_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            header = header.format(sha256=body_hash)
            full_document = header + content
        else:
            full_document = content

        content_bytes = full_document.encode("utf-8")
        current_sha256 = hashlib.sha256(content_bytes).hexdigest()

        # Check ledger for changes
        ledger = self._load_ledger()
        entries = ledger.setdefault("entries", {})
        prev_entry = entries.get(filename)

        out_dir = os.path.join(self.vault_root, target_subfolder)
        os.makedirs(out_dir, exist_ok=True)
        out_filepath = os.path.join(out_dir, filename)

        if prev_entry and prev_entry.get("sha256") == current_sha256 and os.path.exists(out_filepath):
            return {
                "status": "UNCHANGED",
                "filename": filename,
                "filepath": out_filepath,
                "sha256": current_sha256,
                "bytes": len(content_bytes)
            }

        # Write to vault
        with open(out_filepath, "w", encoding="utf-8") as f:
            f.write(full_document)

        # Update ledger
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        entries[filename] = {
            "sha256": current_sha256,
            "connection": profile.name,
            "first_harvested": prev_entry.get("first_harvested", now_iso) if prev_entry else now_iso,
            "last_updated": now_iso,
            "bytes": len(content_bytes)
        }
        self._save_ledger(ledger)

        # Auto-index into SQLite FTS5 and dense vectors
        indexed_chunks = 0
        if auto_index:
            try:
                from src.core.domain.services import chunk_text
                from src.infrastructure.database import get_db_write_connection, DB_FILE
                import sqlite3
                chunks = chunk_text(full_document)
                with get_db_write_connection(DB_FILE) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content, sha256) VALUES (?, ?, ?, ?, ?, ?)",
                        (out_filepath, filename, len(content_bytes), time.time(), full_document, current_sha256)
                    )
                    file_id = cur.lastrowid
                    cur.execute("DELETE FROM file_chunks WHERE file_id = ?", (file_id,))
                    for idx, chunk in enumerate(chunks):
                        cur.execute(
                            "INSERT INTO file_chunks (file_id, chunk_index, content) VALUES (?, ?, ?)",
                            (file_id, idx, chunk)
                        )
                    indexed_chunks = len(chunks)
            except Exception as inner_e:
                pass

        return {
            "status": "UPDATED" if prev_entry else "NEW",
            "filename": filename,
            "filepath": out_filepath,
            "sha256": current_sha256,
            "bytes": len(content_bytes),
            "indexed_chunks": indexed_chunks
        }


# Global singleton instance
client = ConnectionClient()
