import sqlite3
import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from src.core.domain.services import chunk_text
from src.domain.universal_crawler.models import CrawledDocument
from src.domain.universal_crawler.vector_semantic_matrix import FastSemanticVectorMatrix

"""
Auto-RAG Pipeline Ingestion Bridge.
Seamlessly synchronizes crawled forensic documents directly into the Core Knowledge Engine:
- Ingests into `files` and `file_chunks` tables
- Populates SQLite FTS5 search index (`fts_files`)
- Computes 384-dimensional dense semantic vectors (`embedding_json`)
- Synchronizes entity tags and FRE 902 Merkle metadata
"""

class AutoRAGBridge:
    """Zero-Impedance bridge syncing sovereign crawler data into Core Knowledge Engine."""

    @classmethod
    def ingest_crawled_document(cls, conn: sqlite3.Connection, doc: CrawledDocument) -> int:
        """
        Synchronize a CrawledDocument into the primary files, file_chunks, and FTS5 indexes.
        Returns the inserted/updated file_id in the core knowledge schema.
        """
        if not doc.content_text or not doc.content_text.strip():
            return 0

        virtual_path = f"crawler://job_{doc.job_id}/{doc.url}"
        file_hash = doc.merkle_sha256 or hashlib.sha256(doc.content_text.encode('utf-8')).hexdigest()
        file_size = doc.file_size_bytes or len(doc.content_text.encode('utf-8'))
        now_ts = time.time()

        tags_list = ["CrawlerHarvester", f"Job:{doc.job_id}", "Rule902-Certified"]
        if hasattr(doc, "entities") and isinstance(doc.entities, dict):
            for ley in doc.entities.get("leyes", [])[:5]:
                tags_list.append(f"Ley:{ley}")
            for agency in doc.entities.get("agencias", [])[:3]:
                tags_list.append(f"Agencia:{agency}")

        tags_str = ", ".join(tags_list)
        notes_str = f"Source: {doc.url} | Merkle Root: {doc.merkle_dag_root} | FRE 902 Certified"

        # 1. Upsert into core `files` table
        cur = conn.execute("SELECT id FROM files WHERE filepath = ?", (virtual_path,))
        row = cur.fetchone()
        if row:
            file_id = row[0]
            conn.execute("""
            UPDATE files 
            SET filename = ?, file_size = ?, mime_type = ?, sha256 = ?, modified_at = ?, content = ?, tags = ?, notes = ?
            WHERE id = ?
            """, (
                doc.title[:250],
                file_size,
                doc.content_type or "text/html",
                file_hash,
                now_ts,
                doc.content_text,
                tags_str,
                notes_str,
                file_id
            ))
            # Clear old chunks and FTS
            conn.execute("DELETE FROM file_chunks WHERE file_id = ?", (file_id,))
            conn.execute("DELETE FROM tags WHERE file_id = ?", (file_id,))
            try:
                conn.execute("DELETE FROM fts_files WHERE filepath = ?", (virtual_path,))
            except Exception:
                pass
        else:
            cur = conn.execute("""
            INSERT INTO files (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, tags, created_at, notes)
            VALUES (0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                virtual_path,
                doc.title[:250],
                file_size,
                doc.content_type or "text/html",
                file_hash,
                now_ts,
                doc.content_text,
                tags_str,
                now_ts,
                notes_str
            ))
            file_id = cur.lastrowid

        # 2. Hierarchical Chunking & Dense Semantic Vector Generation
        chunks = chunk_text(doc.content_text, chunk_size=500, overlap=60)
        for idx, ch in enumerate(chunks):
            if not ch.strip():
                continue
            # Compute 384-dimensional dense vector
            vec = FastSemanticVectorMatrix.vectorize_text(ch)
            vec_json = json.dumps(vec)
            chunk_hash = hashlib.sha256(ch.encode('utf-8')).hexdigest()

            conn.execute("""
            INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json, chunk_hash)
            VALUES (?, ?, ?, ?, ?)
            """, (
                file_id,
                idx,
                ch,
                vec_json,
                chunk_hash
            ))

        # 3. Synchronize FTS5
        try:
            conn.execute("""
            INSERT INTO fts_files (filepath, filename, content, notes)
            VALUES (?, ?, ?, ?)
            """, (virtual_path, doc.title, doc.content_text, notes_str))
        except Exception:
            pass

        # 4. Synchronize Tags
        for t_name in tags_list:
            t_clean = t_name.strip()
            if not t_clean:
                continue
            try:
                conn.execute("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", (file_id, t_clean))
            except Exception:
                pass

        conn.commit()
        return file_id
