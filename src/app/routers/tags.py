"""
Tag rules, synonyms, bookmarks, tag colors, query macros, tag aliases, notes, and peer sync endpoints.
"""
import hashlib
import json
import time
import os
import re
import sqlite3
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from src.shared.security import verify_path_containment
from src.infrastructure.database import get_db
from src.core.domain.models import (
    RuleRequest,
    TagColorRequest,
    MacroRequest,
    AliasRequest,
    SynonymRequest,
    BookmarkRequest,
    DeleteBookmarkRequest,
    NotesRequest,
    TagRequest,
    PeerRequest,
    SyncExchangeRequest,
)

router = APIRouter()

@router.get("/api/tags")
def get_all_tags_endpoint():
    """List all unique tags with custom colors."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tag, COALESCE(color, '#3b82f6') as color FROM (
                SELECT t.tag as tag, tm.color as color FROM tags t LEFT JOIN tag_metadata tm ON t.tag = tm.tag
                UNION
                SELECT tm.tag as tag, tm.color as color FROM tag_metadata tm
            ) ORDER BY tag ASC
        """)
        return {"tags": [{"tag": r[0], "color": r[1]} for r in cursor.fetchall()]}

@router.get("/api/suggested_tags")
@router.get("/api/file/suggested-tags")
def get_suggested_tags_endpoint(filepath: Optional[str] = None, path: Optional[str] = None):
    """Suggest relevant tags for a file based on content analysis."""
    target = filepath or path or ""
    if target and os.path.exists(target):
        try:
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            from src.core.domain.services import suggest_tags_from_text
            suggested = suggest_tags_from_text(content)
            return {"status": "success", "suggested_tags": suggested}
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in tags.py: {e}")
    return {"status": "success", "suggested_tags": []}

@router.post("/api/file/tag")
def add_file_tag_endpoint(req: TagRequest):
    """Assign tag to a file."""
    fp = req.get_path()
    verify_path_containment(fp)
    norm_path = os.path.abspath(fp) if fp else ""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM files WHERE filepath = ?", (norm_path,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT id FROM files WHERE filepath = ?", (fp,))
            row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="File not found in database")
        file_id = row[0]
        cursor.execute("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", (file_id, req.tag))
        conn.commit()
    return {"status": "success", "filepath": fp, "tag": req.tag}

@router.delete("/api/file/tag")
def delete_file_tag_endpoint(filepath: str, tag: str):
    """Remove tag from a file."""
    verify_path_containment(filepath)
    norm_path = os.path.abspath(filepath)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM files WHERE filepath = ?", (norm_path,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT id FROM files WHERE filepath = ?", (filepath,))
            row = cursor.fetchone()
        if row:
            file_id = row[0]
            cursor.execute("DELETE FROM tags WHERE file_id = ? AND tag = ?", (file_id, tag))
            conn.commit()
    return {"status": "success", "filepath": filepath, "tag": tag}

@router.get("/api/vault/active")
def get_active_vault_endpoint():
    """Retrieve active vault folder path."""
    try:
        from src.core.config import ACTIVE_DIR
        return {"active_vault": ACTIVE_DIR}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).warning("Swallowed error in tags.py")
        return {"active_vault": "dumps"}

@router.get("/api/rules")
def get_rules_endpoint():
    """List all auto-tag rules."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, pattern, tag, priority FROM auto_rules ORDER BY priority DESC")
        return {"rules": [dict(r) for r in cursor.fetchall()]}

@router.post("/api/rules")
def add_rule_endpoint(req: RuleRequest):
    """Add or replace an auto-tagging rule."""
    if not req.pattern:
        raise HTTPException(status_code=400, detail="Pattern cannot be empty")
    try:
        re.compile(req.pattern)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).warning(f"Swallowed error in tags.py: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {str(e)}")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", (req.pattern, req.tag, getattr(req, "priority", 0) or 0))
        conn.commit()
        try:
            conn.execute("PRAGMA wal_checkpoint(FULL)")
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in tags.py: {e}")
    return {"status": "success", "pattern": req.pattern, "tag": req.tag}

@router.post("/api/rules/test-preview")
def preview_rule_endpoint(req: RuleRequest):
    """Test preview an auto-tagging rule against sample input."""
    if not req.pattern:
        raise HTTPException(status_code=400, detail="Pattern cannot be empty")
    try:
        rx = re.compile(req.pattern, re.IGNORECASE)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).warning(f"Swallowed error in tags.py: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {str(e)}")

    matches = []
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filepath, filename, content FROM files")
        for row in cursor.fetchall():
            fp, fn, cnt = row["filepath"], row["filename"], row["content"] or ""
            if rx.search(fn) or rx.search(cnt):
                matches.append({"filepath": fp, "filename": fn})
    return {"status": "success", "matches": matches, "tag": req.tag}

@router.get("/api/synonyms")
def get_synonyms_endpoint():
    """List all word synonyms."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT word, substitutes FROM synonyms")
        return {"synonyms": [dict(r) for r in cursor.fetchall()]}

@router.post("/api/synonyms")
def add_synonym_endpoint(req: SynonymRequest):
    """Add word synonym mapping."""
    with get_db() as conn:
        cursor = conn.cursor()
        sub_str = ",".join(req.synonyms) if req.synonyms else (req.synonym or "")
        cursor.execute("INSERT OR REPLACE INTO synonyms (word, substitutes) VALUES (?, ?)", (req.term, sub_str))
        conn.commit()
    return {"status": "success", "term": req.term}

@router.get("/api/tags/bookmarks")
def get_bookmarks_endpoint():
    """List all query bookmarks."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, query TEXT, search_mode TEXT)")
        cursor.execute("PRAGMA table_info(bookmarks)")
        cols = [r[1] if isinstance(r, (tuple, list)) else r["name"] for r in cursor.fetchall()]
        
        select_cols = [c for c in ["id", "name", "query", "search_mode"] if c in cols]
        if not select_cols:
            return {"bookmarks": []}
        
        allowed = {"id", "name", "query", "search_mode"}
        safe_cols = [c for c in select_cols if c in allowed]
        # ponytail: whitelist validated safe column interpolation; ceiling: fixed internal schema columns; upgrade: use ORM projection if dynamic schema migrations are enabled
        cursor.execute(f"SELECT {', '.join(safe_cols)} FROM bookmarks")
        rows = cursor.fetchall()
        bookmarks = []
        for idx, r in enumerate(rows, start=1):
            d = dict(r) if hasattr(r, "keys") else dict(zip(select_cols, r))
            if "id" not in d:
                d["id"] = idx
            if "query" in d and "query_string" not in d:
                d["query_string"] = d["query"]
            if "search_mode" not in d:
                d["search_mode"] = "keyword"
            bookmarks.append(d)
        return {"bookmarks": bookmarks}

@router.post("/api/bookmarks/add")
def add_bookmark_endpoint(req: BookmarkRequest):
    """Add or update a query bookmark."""
    b_name = req.name or "default"
    b_query = req.get_query()
    b_mode = req.search_mode or "keyword"
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, query TEXT, search_mode TEXT)")
        cursor.execute("INSERT OR REPLACE INTO bookmarks (name, query, search_mode) VALUES (?, ?, ?)", (b_name, b_query, b_mode))
        conn.commit()
    return {"status": "success", "name": b_name}

@router.post("/api/bookmarks/delete")
def delete_bookmark_endpoint(req: Optional[DeleteBookmarkRequest] = None, name: Optional[str] = None, id: Optional[str] = None):

    """Delete a query bookmark by ID or name."""
    b_id = id
    b_name = (req.name if req else None) or name
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, query TEXT, search_mode TEXT)")
        if b_id:
            cursor.execute("DELETE FROM bookmarks WHERE id = ?", (b_id,))
        elif b_name:
            cursor.execute("DELETE FROM bookmarks WHERE name = ?", (b_name,))
        conn.commit()
    return {"status": "success"}

@router.get("/api/notes")
@router.get("/api/file/notes")
def get_notes_endpoint(filepath: Optional[str] = None, path: Optional[str] = None):
    """Retrieve file notes."""
    fp = filepath or path or ""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT notes FROM files WHERE filepath = ?", (fp,))
        row = cursor.fetchone()
        return {"filepath": fp, "notes": row["notes"] if row and row["notes"] else ""}

@router.post("/api/notes")
@router.post("/api/file/notes")
def update_notes_endpoint(req: NotesRequest):
    """Update file notes in database and FTS index."""
    fp = req.get_path()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE files SET notes = ? WHERE filepath = ?", (req.notes, fp))
        cursor.execute("UPDATE fts_files SET notes = ? WHERE filepath = ?", (req.notes, fp))
        conn.commit()
    return {"status": "success", "filepath": fp}

@router.get("/api/tags/colors")
@router.get("/api/tags/color")
def get_tag_colors_endpoint():
    """List custom tag colors."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tag, color FROM tag_metadata")
        return {"colors": {row["tag"]: row["color"] for row in cursor.fetchall()}}

@router.post("/api/tags/colors")
@router.post("/api/tags/color")
def set_tag_color_endpoint(req: TagColorRequest):
    """Set custom tag color."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO tag_metadata (tag, color) VALUES (?, ?)", (req.tag, req.color))
        conn.commit()
    return {"status": "success", "tag": req.tag, "color": req.color}

@router.get("/api/macros")
def get_macros_endpoint():
    """List query macros."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, expansion FROM query_macros")
        return {"macros": [dict(r) for r in cursor.fetchall()]}

@router.post("/api/macros")
def set_macro_endpoint(req: MacroRequest):
    """Register query macro."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO query_macros (name, expansion) VALUES (?, ?)", (req.name, req.expansion))
        conn.commit()
    return {"status": "success", "name": req.name}

@router.get("/api/aliases")
def get_aliases_endpoint():
    """List tag aliases."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT alias, target FROM tag_aliases")
        return {"aliases": [dict(r) for r in cursor.fetchall()]}

@router.post("/api/aliases")
def set_alias_endpoint(req: AliasRequest):
    """Register tag alias mapping."""
    a = req.get_alias()
    t = req.get_target()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO tag_aliases (alias, target) VALUES (?, ?)", (a, t))
        conn.commit()
    return {"status": "success", "alias": a, "target": t, "tag": a, "canonical_tag": t}

@router.post("/api/rules/preview")
def test_preview_rule_endpoint(req: RuleRequest):
    """Preview auto-tagging rule matches against existing database files."""
    matches = []
    pattern_lower = req.pattern.lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filepath, filename, content FROM files")
        for row in cursor.fetchall():
            text = (row["filename"] or "") + " " + (row["content"] or "")
            if pattern_lower in text.lower():
                matches.append(dict(row))
    return {"status": "success", "pattern": req.pattern, "tag": req.tag, "matches": matches}

@router.get("/api/sync/peers")
@router.get("/api/peers")
def list_sync_peers_endpoint():
    """List registered P2P sync peers and active UDP broadcast discovered LAN nodes."""
    peers = []
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS sync_peers (id INTEGER PRIMARY KEY AUTOINCREMENT, address TEXT UNIQUE, name TEXT)")
        cursor.execute("SELECT id, address, name FROM sync_peers")
        rows = cursor.fetchall()
        for r in rows:
            if isinstance(r, (tuple, list)):
                peers.append({"id": r[0], "address": r[1], "name": r[2]})
            else:
                peers.append(dict(r))
    
    # Auto-discovered UDP broadcast peers
    try:
        from src.infrastructure.p2p_sync import get_active_peers
        active = get_active_peers()
        existing_addrs = {p["address"] for p in peers}
        for idx, p in enumerate(active, start=len(peers) + 1):
            addr = f"http://{p['ip']}:{p['port']}"
            if addr not in existing_addrs:
                peers.append({"id": idx, "address": addr, "name": f"Node-{p['node_id'][:6]}"})
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in tags.py: {e}")

    return {"status": "success", "peers": peers}

@router.post("/api/sync/peers")
def add_sync_peer_endpoint(req: PeerRequest):
    """Register LAN sync peer."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sync_peers (address, name) VALUES (?, ?)", (req.address, req.name or ""))
        conn.commit()
    return {"status": "success", "peer": req.address}

class SyncDeltaRequest(BaseModel):
    filenames: Optional[List[str]] = None
    requested_files: Optional[List[str]] = None
    files: Optional[List[str]] = None

    def get_filenames(self) -> List[str]:
        return self.filenames or self.requested_files or self.files or []

@router.get("/api/sync/manifest")
def get_sync_manifest_endpoint():
    """Retrieve workspace synchronization manifest."""
    manifest = []
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filepath, filename, file_size, modified_at, content FROM files")
        for row in cursor.fetchall():
            manifest.append(dict(row))
    return {"status": "success", "manifest": manifest}

@router.get("/api/sync/hashes")
def get_sync_hashes_endpoint():
    """Return JSON map of local file SHA-256 hashes, sizes, and timestamps."""
    from src.infrastructure.p2p_sync import get_local_document_hashes
    hashes = get_local_document_hashes()
    return {"status": "success", "hashes": hashes}

@router.post("/api/sync/delta")
def get_sync_delta_endpoint(req: SyncDeltaRequest):
    """Accept requested filenames list, return content payloads for requested files."""
    requested = req.get_filenames()
    from src.infrastructure.p2p_sync import get_local_document_hashes
    from src.infrastructure.database import get_db, get_active_dir
    local_hashes = get_local_document_hashes()
    active_dir = get_active_dir()

    payloads = []
    db_needed = []
    
    # Pass 1: Disk lookups
    for fn in requested:
        info = local_hashes.get(fn, {})
        fp = info.get("filepath", "") or os.path.join(active_dir, fn)
        content = ""
        sha256_val = info.get("sha256", "")
        size = info.get("size", 0)
        mod_at = info.get("modified_at", 0.0)

        if fp and os.path.exists(fp) and os.path.isfile(fp):
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in tags.py: {e}")
            
            if not sha256_val and content:
                sha256_val = hashlib.sha256(content.encode("utf-8")).hexdigest()
                size = len(content.encode("utf-8"))

            payloads.append({
                "filename": fn,
                "content": content,
                "file_size": size,
                "modified_at": mod_at,
                "sha256": sha256_val
            })
        else:
            db_needed.append((fn, fp, sha256_val, size, mod_at))

    # Pass 2: Batched DB fallback
    if db_needed:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                filenames = [item[0] for item in db_needed]
                filepaths = [item[1] for item in db_needed]
                placeholders = ",".join(["?"] * len(filenames))
                
                cursor.execute(f"SELECT filename, filepath, content FROM files WHERE filename IN ({placeholders}) OR filepath IN ({placeholders})", tuple(filenames) + tuple(filepaths))
                db_results = { (r[0] or "", r[1] or ""): r[2] for r in cursor.fetchall() }
                
                for fn, fp, sha256_val, size, mod_at in db_needed:
                    content = db_results.get((fn, fp)) or db_results.get((fn, "")) or db_results.get(("", fp)) or ""
                    
                    if not sha256_val and content:
                        sha256_val = hashlib.sha256(content.encode("utf-8")).hexdigest()
                        size = len(content.encode("utf-8"))

                    payloads.append({
                        "filename": fn,
                        "content": content,
                        "file_size": size,
                        "modified_at": mod_at,
                        "sha256": sha256_val
                    })
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in tags.py: {e}")

    return {"status": "success", "files": payloads}

@router.post("/api/sync/exchange")
def sync_exchange_endpoint(req: SyncExchangeRequest):
    """Exchange sync manifests between peers, pull missing/modified files via HTTP delta protocol, and log transaction into sync_logs."""
    target_peer = getattr(req, "target_peer", None) or req.peer or ""
    synced = []
    total_bytes = 0

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                peer_address TEXT,
                direction TEXT,
                files_synced INTEGER,
                bytes_transferred INTEGER,
                status TEXT
            )
        """)
        conn.commit()

    if target_peer:
        target_peer_clean = target_peer.rstrip("/")
        if not target_peer_clean.startswith("http://") and not target_peer_clean.startswith("https://"):
            target_peer_clean = f"http://{target_peer_clean}"
        try:
            import urllib.request
            from src.infrastructure.p2p_sync import get_local_document_hashes, compute_sync_delta
            from src.infrastructure.database import get_active_dir
            from src.infrastructure.vector_engine import index_directory

            active_dir = get_active_dir()
            remote_hashes = None

            # 1. Attempt HTTP Delta Hash Exchange
            hashes_url = f"{target_peer_clean}/api/sync/hashes"
            try:
                with urllib.request.urlopen(hashes_url, timeout=5.0) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(res_data, dict) and "hashes" in res_data:
                        remote_hashes = res_data.get("hashes", {})
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception:
                import logging; logging.getLogger(__name__).warning("Swallowed error in tags.py")
                remote_hashes = None

            if remote_hashes is not None:
                local_hashes = get_local_document_hashes()
                delta = compute_sync_delta(local_hashes, remote_hashes)
                to_pull = delta.get("to_pull", [])

                if to_pull:
                    delta_url = f"{target_peer_clean}/api/sync/delta"
                    req_payload = json.dumps({"filenames": to_pull}).encode("utf-8")
                    req_obj = urllib.request.Request(delta_url, data=req_payload, headers={"Content-Type": "application/json"}, method="POST")
                    try:
                        with urllib.request.urlopen(req_obj, timeout=5.0) as resp:
                            delta_res = json.loads(resp.read().decode("utf-8"))
                            files_list = delta_res.get("files", [])
                            for item in files_list:
                                fn = os.path.basename(item.get("filename") or "synced_file.txt")
                                content = item.get("content") or ""
                                fp = os.path.join(active_dir, fn)
                                with open(fp, "w", encoding="utf-8") as f:
                                    f.write(content)
                                synced.append(fn)
                                total_bytes += len(content.encode("utf-8"))
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception:
                        import logging; logging.getLogger(__name__).warning("Swallowed error in tags.py")
                        manifest_url = f"{target_peer_clean}/api/sync/manifest"
                        try:
                            with urllib.request.urlopen(manifest_url, timeout=5.0) as resp:
                                data = json.loads(resp.read().decode("utf-8"))
                                peer_manifest = data.get("manifest", [])
                                for item in peer_manifest:
                                    fn = os.path.basename(item.get("filename") or "synced_file.txt")
                                    if fn in to_pull:
                                        content = item.get("content") or ""
                                        fp = os.path.join(active_dir, fn)
                                        with open(fp, "w", encoding="utf-8") as f:
                                            f.write(content)
                                        synced.append(fn)
                                        total_bytes += len(content.encode("utf-8"))
                        except Exception as e:
                            import logging; logging.getLogger(__name__).warning("Swallowed error in tags.py manifest fallback 1")
                            raise e
            else:
                manifest_url = f"{target_peer_clean}/api/sync/manifest"
                try:
                    with urllib.request.urlopen(manifest_url, timeout=5.0) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        peer_manifest = data.get("manifest", [])
                        for item in peer_manifest:
                            fn = os.path.basename(item.get("filename") or "synced_file.txt")
                            content = item.get("content") or ""
                            fp = os.path.join(active_dir, fn)
                            with open(fp, "w", encoding="utf-8") as f:
                                f.write(content)
                            synced.append(fn)
                            total_bytes += len(content.encode("utf-8"))
                except Exception as e:
                    import logging; logging.getLogger(__name__).warning("Swallowed error in tags.py manifest fallback 2")
                    raise e

            if synced:
                index_directory(active_dir)
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sync_logs (timestamp, peer_address, direction, files_synced, bytes_transferred, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (time.time(), target_peer, "pull", len(synced), total_bytes, "success"))
                conn.commit()

        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"Swallowed error in tags.py: {e}")
            try:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO sync_logs (timestamp, peer_address, direction, files_synced, bytes_transferred, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (time.time(), target_peer, "pull", 0, 0, "failed"))
                    conn.commit()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in tags.py: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to reach peer: {str(e)}")

    return {
        "status": "success",
        "peer": target_peer,
        "synced": synced,
        "files_synced": len(synced),
        "bytes_transferred": total_bytes,
        "sync_status": "in_sync"
    }

@router.get("/api/sync/logs")
def get_sync_logs_endpoint():
    """Retrieve P2P sync transaction logs."""
    logs = []
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                peer_address TEXT,
                direction TEXT,
                files_synced INTEGER,
                bytes_transferred INTEGER,
                status TEXT
            )
        """)
        cursor.execute("SELECT id, timestamp, peer_address, direction, files_synced, bytes_transferred, status FROM sync_logs ORDER BY id DESC")
        for r in cursor.fetchall():
            logs.append(dict(r))
    return {"status": "success", "logs": logs}

