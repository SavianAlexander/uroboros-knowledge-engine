from src.infrastructure.database import get_db, get_db_connection, get_db_write_connection, get_pool
import src.infrastructure.database as db
import os
import re
import time
import glob
import shutil
import sqlite3
import hashlib
import threading
from typing import Dict, List, Any, Tuple, Optional, Callable
import mimetypes
import concurrent.futures
import uuid
import json
import contextlib
import logging
from datetime import datetime, timezone
import queue
from datetime import datetime, timezone
from pathlib import Path
from src.shared.security import get_file_acl
from src.core.domain.services import (
    extract_ai_tags,
    chunk_text,
)
from src.infrastructure.parsers import extract_content, parse_audio_metadata, calculate_sha256, calculate_sha256_cached

def search_files(query: str) -> List[Dict[str, Any]]:
    """Execute FTS5 keyword search across files with Unicode NFC normalization."""
    if not query or not str(query).strip():
        return []
    import unicodedata
    norm_query = unicodedata.normalize("NFC", str(query).strip())
    with get_db_connection(db.DB_FILE, timeout=db.DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT files.id, files.filepath, files.filename, files.file_size, files.mime_type, files.modified_at, files.content, bm25(fts_files) as bm25_score
                FROM fts_files JOIN files ON fts_files.filepath = files.filepath
                WHERE fts_files MATCH ? ORDER BY bm25_score LIMIT 100
            """, (norm_query,))
            rows = cursor.fetchall()
            if rows:
                results = [dict(r) for r in rows]
                import time, math
                now = time.time()
                for r in results:
                    score = -r.get('bm25_score', 0)
                    age_days = max(0, now - r.get('modified_at', now)) / 86400.0
                    r['final_score'] = score * math.exp(-0.05 * age_days)
                results.sort(key=lambda x: x['final_score'], reverse=True)
                return results
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in database.py: {e}")

        if "NEAR(" in norm_query:
            import re
            m = re.search(r'NEAR\((.*?),\s*(\d+)\)', norm_query, re.IGNORECASE)
            if m:
                words = m.group(1).split()
                dist = m.group(2)
                quoted_words = " ".join([f'"{w}"' for w in words])
                fts_near = f'NEAR({quoted_words}, {dist})'
                try:
                    cursor.execute("""
                        SELECT files.id, files.filepath, files.filename, files.file_size, files.mime_type, files.modified_at, files.content, bm25(fts_files) as bm25_score
                        FROM fts_files JOIN files ON fts_files.filepath = files.filepath
                        WHERE fts_files MATCH ? ORDER BY bm25_score LIMIT 100
                    """, (fts_near,))
                    rows = cursor.fetchall()
                    if rows:
                        results = [dict(r) for r in rows]
                        import time, math
                        now = time.time()
                        for r in results:
                            score = -r.get('bm25_score', 0)
                            age_days = max(0, now - r.get('modified_at', now)) / 86400.0
                            r['final_score'] = score * math.exp(-0.05 * age_days)
                        results.sort(key=lambda x: x['final_score'], reverse=True)
                        return results
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception as e:
                    import logging; logging.warning(f"Swallowed error in database.py: {e}")

        import re
        words = re.findall(r'\w+', norm_query)
        words = [w for w in words if w.lower() not in ('near', 'and', 'or', 'not') and not w.isdigit()]
        if words:
            where_clause = " AND ".join(["(content LIKE ? OR filename LIKE ?)" for _ in words])
            params = []
            for w in words:
                params.extend([f"%{w}%", f"%{w}%"])
            try:
                cursor.execute(f"SELECT id, filepath, filename, file_size, mime_type, modified_at, content FROM files WHERE {where_clause} LIMIT 100", params)
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in database.py: {e}")
        return []

def index_directory(dir_path: str, progress_callback: Optional[Callable[[str, int, int], None]] = None, on_complete_callback: Optional[Callable[[], None]] = None, job_id: Optional[str] = None):
    """
    Crawls dir_path, parses supported files, updates files/FTS/Tags,
    and manages chunks + vector embeddings.
    """
    if not os.path.exists(dir_path):
        if on_complete_callback:
            on_complete_callback()
        return

    from src.core.context import get_current_user_id
    user_id = get_current_user_id() or 0

    print(f"Indexing directory: {dir_path} for user: {user_id}")
    """
    Index directory files with decoupled post-processing:
    Auto-tagging and search index rules are evaluated for ALL matching files (including unmodified ones).
    """
    db._db_version += 1

    try:
        from src.core.state import GLOBAL_QUERY_CACHE
        if GLOBAL_QUERY_CACHE is not None:
            GLOBAL_QUERY_CACHE.invalidate()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in database.py: {e}")

    path = Path(dir_path).resolve()
    if not path.is_dir():
        print(f"Error: {dir_path} is not a directory.")
        return

    with get_db_connection(db.DB_FILE, timeout=db.DB_TIMEOUT) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, filepath, modified_at, file_size, sha256, content FROM files")
            existing_files = {
                row['filepath']: {
                    'id': row['id'],
                    'modified_at': row['modified_at'],
                    'file_size': row['file_size'],
                    'sha256': row['sha256'],
                    'content': row['content']
                }
                for row in cursor.fetchall()
            }
        except sqlite3.OperationalError:
            print(f"Skipping index_directory due to uninitialized database table.")
            return

    text_extensions = {
        '.md', '.py', '.txt', '.json', '.yaml', '.yml', '.ini', '.csv', '.xml',
        '.html', '.css', '.js', '.pdf', '.docx', '.rtf', '.xlsx',
        '.png', '.jpg', '.jpeg', '.bmp'
    }
    ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}

    all_files = []
    for p in path.rglob('*'):
        if p.is_file() and p.name != db.DB_FILE and not p.name.startswith('.') and p.name not in ['desktop.ini', 'Thumbs.db']:
            if not any(part in ignored_dirs for part in p.parts):
                all_files.append(p)

    total_files = len(all_files)
    if total_files == 0:
        print("Indexing completed. Indexed: 0, Updated: 0")
        if on_complete_callback:
            try:
                on_complete_callback()
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.warning(f"Swallowed error in database.py: {e}")
        return

    if total_files > 100 and len(all_files) > 50:
        try:
            create_db_snapshot()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in database.py: {e}")

    modified_tasks = []
    unmodified_tasks = []
    print(f"[DEBUG_INDEXER] Indexing directory '{dir_path}' | Total files: {total_files}")

    for p in all_files:
        filepath = str(p)
        filename = p.name
        suffix = p.suffix.lower()
        try:
            stat = p.stat()
            file_size = stat.st_size
            modified_at = stat.st_mtime
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
            continue

        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'
        cached = existing_files.get(filepath)

        task = {
            'filepath': filepath,
            'filename': filename,
            'suffix': suffix,
            'file_size': file_size,
            'modified_at': modified_at,
            'mime_type': mime_type,
            'is_modified': False,
            'id': cached['id'] if cached else None,
            'content': cached['content'] if cached else "",
            'coords': []
        }

        curr_sha = calculate_sha256(filepath)
        if cached and cached['modified_at'] == modified_at and cached['file_size'] == file_size and cached.get('sha256') == curr_sha:
            unmodified_tasks.append(task)
        else:
            task['is_modified'] = True
            modified_tasks.append(task)

    completed_count = 0
    progress_lock = threading.Lock()

    def update_progress(fn):
        nonlocal completed_count
        if progress_callback:
            with progress_lock:
                completed_count += 1
                progress_callback(fn, completed_count, total_files)

    def parse_single_file(task):
        fp = task['filepath']
        suf = task['suffix']
        mime = task['mime_type']
        fsize = task.get('file_size', 0)
        mt = task.get('modified_at', 0)

        if fsize > 100 * 1024 * 1024:
            task['sha256'] = calculate_sha256_cached(fp, mt)
            task['content'] = f"[File size ({fsize / (1024*1024):.1f}MB) exceeds 100MB safety limit.]"
            task['coords'] = []
            return task

        sha256 = calculate_sha256_cached(fp, mt)
        cnt = ""
        coords = []
        if mime.startswith('text/') or suf in text_extensions:
            cnt, coords = extract_content(fp, suf)
        elif suf in {'.wav', '.mp3'}:
            meta = parse_audio_metadata(fp)
            cnt = f"[Audio Metadata] samplerate:{meta.get('samplerate', 0)} channels:{meta.get('channels', 0)}"

        task['sha256'] = sha256
        task['content'] = cnt
        task['coords'] = coords
        task['acl_permissions'] = get_file_acl(fp)
        return task

    batch_size = 200
    if modified_tasks:
        for i in range(0, len(modified_tasks), batch_size):
            batch = modified_tasks[i:i + batch_size]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(parse_single_file, t): t for t in batch}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res_task = future.result()
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception as e:
                        import logging; logging.getLogger(__name__).exception(f"Swallowed error in database.py: {e}")
                        t = futures[future]
                        t['content'] = f"[ThreadPool Error: {str(e)}]"
                        t['acl_permissions'] = get_file_acl(t['filepath'])
                        res_task = t
                    update_progress(res_task['filename'])
            time.sleep(0.005)

    for task in unmodified_tasks:
        task['acl_permissions'] = get_file_acl(task['filepath'])
        update_progress(task['filename'])

    # DECOUPLED POST-PROCESSING: Extract AI tags for ALL tasks (both modified & unmodified)
    rule_matches = []
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pattern, tag FROM auto_rules")
            rule_matches = [(r[0], r[1]) for r in cursor.fetchall()]
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
        rule_matches = []

    all_tasks = modified_tasks + unmodified_tasks
    for task in all_tasks:
        task['matched_tags'] = extract_ai_tags(task['content'], task['filename'], rule_matches=rule_matches)

    indexed_count = 0
    updated_count = 0

    with get_db() as conn:
        with conn:
            cursor = conn.cursor()
            for task in modified_tasks:
                filepath = task['filepath']
                filename = task['filename']
                file_size = task['file_size']
                modified_at = task['modified_at']
                content = task['content']
                matched_tags = task['matched_tags']
                acl_permissions = task.get('acl_permissions') or get_file_acl(filepath)
                sha256 = task.get('sha256')
                mime_type = task['mime_type']
                coords = task['coords']
                file_id = task['id']

                if file_id is not None:
                    cursor.execute("""
                        UPDATE files
                        SET filename = ?, file_size = ?, mime_type = ?, sha256 = ?, modified_at = ?, content = ?, acl_permissions = ?, insights = NULL
                        WHERE filepath = ?
                    """, (filename, file_size, mime_type, sha256, modified_at, content, acl_permissions, filepath))

                    cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
                    cursor.execute("""
                        INSERT INTO fts_files (filepath, filename, content, notes)
                        VALUES (?, ?, ?, (SELECT notes FROM files WHERE filepath = ?))
                    """, (filepath, filename, content, filepath))

                    cursor.execute("DELETE FROM ocr_coords WHERE file_id = ?", (file_id,))
                    if coords:
                        cursor.executemany("""
                            INSERT INTO ocr_coords (file_id, word, x, y, w, h)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [(file_id, c['word'], c['x'], c['y'], c['w'], c['h']) for c in coords])

                    cursor.execute("DELETE FROM tags WHERE file_id = ?", (file_id,))
                    cursor.execute("DELETE FROM file_chunks WHERE file_id = ?", (file_id,))
                    cursor.execute("DELETE FROM fts_file_chunks WHERE file_id = ?", (file_id,))
                    updated_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO files (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                    """, (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions))
                    file_id = cursor.lastrowid
                    task['id'] = file_id

                    cursor.execute("""
                        INSERT INTO fts_files (filepath, filename, content, notes)
                        VALUES (?, ?, ?, NULL)
                    """, (filepath, filename, content))

                    if coords:
                        cursor.executemany("""
                            INSERT INTO ocr_coords (file_id, word, x, y, w, h)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [(file_id, c['word'], c['x'], c['y'], c['w'], c['h']) for c in coords])
                    indexed_count += 1

            for task in all_tasks:
                file_id = task['id']
                task_content = task.get('content') or ""
                matched_tags = task.get('matched_tags', [])
                if file_id is not None:
                    if matched_tags:
                        cursor.executemany("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", [(file_id, tag) for tag in matched_tags])

                    # Generate Dense Embeddings and Chunks
                    from src.core.embeddings import generate_embedding
                    from src.core.domain.services import chunk_text
                    
                    chunks = chunk_text(task_content, chunk_size=1024)
                    for chunk_idx, chunk in enumerate(chunks):
                        emb = generate_embedding(chunk)
                        emb_json = json.dumps(emb) if emb else None
                        cursor.execute('''
                            INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json)
                            VALUES (?, ?, ?, ?)
                        ''', (file_id, chunk_idx, chunk, emb_json))
                        
                        chunk_id = cursor.lastrowid
                        try:
                            cursor.execute(
                                "INSERT INTO fts_file_chunks (chunk_id, file_id, content) VALUES (?, ?, ?)",
                                (chunk_id, file_id, chunk)
                            )
                        except (KeyboardInterrupt, MemoryError, SystemExit):
                            raise
                        except Exception as e:
                            import logging; logging.warning(f"Swallowed error in database.py: {e}")

            # Decoupled tag sync for unmodified tasks
            for task in unmodified_tasks:
                file_id = task['id']
                matched_tags = task['matched_tags']
                if file_id is not None and matched_tags:
                    cursor.executemany("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)", [(file_id, tag) for tag in matched_tags])

            cursor.execute("DELETE FROM fts_files WHERE filepath NOT IN (SELECT filepath FROM files)")

    if on_complete_callback:
        try:
            on_complete_callback()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in database.py: {e}")

    print(f"Indexing completed. Indexed: {indexed_count}, Updated: {updated_count}")

class MiniVectorEngine:
    @staticmethod
    def search_semantic(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Native Vector Search using file_chunks and cosine similarity.
        Zero dependency fallback to Ollama embeddings.
        """
        if not query or not query.strip():
            return []
            
        from src.core.embeddings import generate_embedding, cosine_similarity
        query_emb = generate_embedding(query.strip())
        if not query_emb:
            return []
            
        try:
            conn = get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch all chunks that have embeddings
            cursor.execute('''
                SELECT c.id, c.file_id, c.chunk_index, c.text_content as content, c.embedding_json, 
                       f.filepath, f.filename, f.modified_at
                FROM file_chunks c
                JOIN files f ON c.file_id = f.id
                WHERE c.embedding_json IS NOT NULL
            ''')
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                try:
                    chunk_emb = json.loads(r['embedding_json'])
                    score = cosine_similarity(query_emb, chunk_emb)
                    if score > 0.3: # Threshold
                        
                        # Find matching tags
                        tags = []
                        try:
                            cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (r['file_id'],))
                            for tr in cursor.fetchall():
                                tags.append(tr['tag'])
                        except (KeyboardInterrupt, MemoryError, SystemExit):
                            raise
                        except Exception as e:
                            import logging; logging.getLogger(__name__).exception(f"Swallowed error in database.py: {e}")
                            
                        # Build snippet
                        content = r['content'] or ""
                        snippet_text = content[:150] + "..."
                        
                        results.append({
                            "id": r['file_id'],
                            "chunk_id": r['id'],
                            "filepath": r['filepath'],
                            "filename": r['filename'],
                            "content": content,
                            "snippet": snippet_text,
                            "modified_at": r['modified_at'],
                            "tags": tags,
                            "score": round(score, 4),
                            "rrf_score": round(score, 6),
                            "vector_score": round(score, 6),
                            "bm25_score": round(score, 6)
                        })
                except (KeyboardInterrupt, MemoryError, SystemExit):
                    raise
                except Exception:
                    import logging; logging.getLogger(__name__).exception("Swallowed error in database.py")
                    continue
                    
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Semantic search error: {e}")
            return []

def extract_rag_context(query: str, max_chunks: int = 5):
    """RAG context extractor delegating to domain RAG engine."""
    from src.domain.rag_engine import extract_advanced_rag_context
    return extract_advanced_rag_context(query, max_chunks=max_chunks, jaccard_threshold=0.70)