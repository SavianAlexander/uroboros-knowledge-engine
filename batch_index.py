r"""
Per-file batch indexer for the Uroboros Knowledge Engine.
Indexes one file at a time, committing each to the DB independently.
Resumable: skips files already in the DB. Safe against Ollama crashes.

Usage:
  python -u batch_index.py "C:\path\to\directory"
  python -u batch_index.py  # defaults to Triage (Support)
"""
import os, sys, time, json, sqlite3, logging, hashlib

logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.parsers import extract_content
from src.infrastructure.database import get_db, DB_FILE
from src.core.embeddings import generate_embedding
from src.core.domain.services import chunk_text
from src.infrastructure.vector_engine import extract_ai_tags, get_file_acl

DEFAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Triage (Support)")
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def norm_path(p):
    return os.path.normcase(os.path.normpath(p))


def get_indexed_filepaths(conn):
    """Return set of normalized filepaths already in the DB."""
    cur = conn.execute("SELECT filepath FROM files")
    return {norm_path(row[0]) for row in cur.fetchall()}


def index_single_file(filepath, user_id=0):
    """Parse, embed, and write a single file to the DB. Returns (chunks, tags, embedded_count, parse_time, embed_time)."""
    filepath = os.path.normpath(filepath)
    if not os.path.exists(filepath):
        return (0, 0, 0, 0.0, 0.0)

    try:
        filename = os.path.basename(filepath)
        suffix = os.path.splitext(filepath)[1].lower()
        file_size = os.path.getsize(filepath)
        modified_at = os.path.getmtime(filepath)
    except (OSError, FileNotFoundError, PermissionError):
        return (0, 0, 0, 0.0, 0.0)

    # Parse
    t0 = time.time()
    content, coords = extract_content(filepath, suffix)
    parse_time = time.time() - t0

    if content.startswith("[Parsing Error") or content.startswith("[File Size Exceeds"):
        print(f"  PARSE ERROR: {content[:120]}")
        content = content[:500]

    # Compute SHA256 safely
    try:
        with open(filepath, "rb") as f:
            sha256 = hashlib.sha256(f.read(10 * 1024 * 1024)).hexdigest()
    except (OSError, FileNotFoundError, PermissionError):
        sha256 = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()

    mime_map = {
        ".pdf": "application/pdf", ".epub": "application/epub+zip",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".html": "text/html", ".htm": "text/html", ".txt": "text/plain",
        ".md": "text/markdown", ".csv": "text/csv", ".json": "application/json",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    }
    mime_type = mime_map.get(suffix, "application/octet-stream")

    # Tags & ACL
    matched_tags = extract_ai_tags(content, filename)
    acl_permissions = get_file_acl(filepath)

    # Import batch embedding function
    from src.core.embeddings import generate_embeddings_batch

    # Chunk + Embed (outside DB transaction)
    chunks_data = []
    raw_chunks = chunk_text(content, chunk_size=1024)
    t1 = time.time()

    # Check DB for pre-existing chunk hashes to skip duplicate vector generation!
    chunks_to_embed = []
    chunk_hashes = []
    cached_embeddings = {}

    with get_db() as conn:
        cur = conn.cursor()
        for chunk in raw_chunks:
            c_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
            chunk_hashes.append(c_hash)
            cur.execute("SELECT embedding_json FROM file_chunks WHERE chunk_hash = ? AND embedding_json IS NOT NULL AND embedding_json != '[]' LIMIT 1", (c_hash,))
            row = cur.fetchone()
            if row and row[0]:
                cached_embeddings[c_hash] = row[0]
            elif chunk not in chunks_to_embed:
                chunks_to_embed.append(chunk)

    new_embeddings = generate_embeddings_batch(chunks_to_embed, batch_size=64) if chunks_to_embed else []
    new_emb_map = {chunk: json.dumps(emb) if emb else None for chunk, emb in zip(chunks_to_embed, new_embeddings)}

    for chunk_idx, (chunk, c_hash) in enumerate(zip(raw_chunks, chunk_hashes)):
        emb_json = cached_embeddings.get(c_hash) or new_emb_map.get(chunk)
        chunks_data.append((chunk_idx, chunk, emb_json, c_hash))
    embed_time = time.time() - t1

    embedded_count = sum(1 for _, _, e, _ in chunks_data if e and e != "[]")

    # Fast DB write — single file, small transaction
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            # Clean up existing record if any
            cur.execute("SELECT id FROM files WHERE filepath = ?", (filepath,))
            existing = cur.fetchone()
            if existing:
                file_id = existing[0]
                cur.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
                cur.execute("DELETE FROM ocr_coords WHERE file_id = ?", (file_id,))
                cur.execute("DELETE FROM tags WHERE file_id = ?", (file_id,))
                cur.execute("DELETE FROM file_chunks WHERE file_id = ?", (file_id,))
                cur.execute("DELETE FROM fts_file_chunks WHERE file_id = ?", (file_id,))
                cur.execute("DELETE FROM files WHERE id = ?", (file_id,))

            cur.execute("""
                INSERT INTO files (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """, (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions))
            file_id = cur.lastrowid

            cur.execute("""
                INSERT INTO fts_files (filepath, filename, content, notes)
                VALUES (?, ?, ?, NULL)
            """, (filepath, filename, content))

            if coords:
                cur.executemany("""
                    INSERT INTO ocr_coords (file_id, word, x, y, w, h)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [(file_id, c['word'], c['x'], c['y'], c['w'], c['h']) for c in coords])

            if matched_tags:
                cur.executemany("INSERT OR IGNORE INTO tags (file_id, tag) VALUES (?, ?)",
                                [(file_id, tag) for tag in matched_tags])

            for chunk_idx, chunk, emb_json, c_hash in chunks_data:
                cur.execute("""
                    INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json, chunk_hash)
                    VALUES (?, ?, ?, ?, ?)
                """, (file_id, chunk_idx, chunk, emb_json, c_hash))
                chunk_id = cur.lastrowid
                try:
                    cur.execute("INSERT INTO fts_file_chunks (chunk_id, file_id, content) VALUES (?, ?, ?)",
                                (chunk_id, file_id, chunk))
                except Exception:
                    pass

    return len(chunks_data), len(matched_tags), embedded_count, parse_time, embed_time


def main():
    import argparse
    from concurrent.futures import ThreadPoolExecutor, as_completed
    parser = argparse.ArgumentParser(description="Job-based batch indexer for Uroboros Knowledge Engine")
    parser.add_argument("dir", nargs="?", default=DEFAULT_DIR, help="Directory to index")
    parser.add_argument("-n", "--limit", type=int, default=0, help="Limit number of files to process in this job run (0 = all)")
    parser.add_argument("-w", "--workers", type=int, default=1, help="Number of parallel worker threads (default=1)")
    args = parser.parse_args()

    target_dir = args.dir
    limit = args.limit

    # Collect all files
    all_files = []
    for root, dirs, fnames in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in fnames:
            all_files.append(os.path.join(root, fn))

    # Check which are already indexed
    with get_db() as conn:
        indexed = get_indexed_filepaths(conn)

    remaining = [f for f in all_files if norm_path(f) not in indexed]
    already_done = len(all_files) - len(remaining)

    if limit > 0:
        to_process = remaining[:limit]
    else:
        to_process = remaining

    print(f"\n{'='*60}")
    print(f"  JOB-BASED BATCH INDEXER")
    print(f"  Directory:       {target_dir}")
    print(f"  Total files:     {len(all_files)}")
    print(f"  Already indexed: {already_done}")
    print(f"  Remaining total: {len(remaining)}")
    print(f"  Job limit:       {limit if limit > 0 else 'All'}")
    print(f"  Processing:      {len(to_process)} files")
    print(f"{'='*60}\n")

    if not to_process:
        print("All requested files already indexed! Nothing to do.")
        return

    total_chunks = 0
    total_embedded = 0
    t_start = time.time()

    def process_file_worker(idx, filepath):
        fn = os.path.basename(filepath)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        try:
            chunks, tags, embedded, pt, et = index_single_file(filepath)
            return (True, idx, fn, size_mb, chunks, tags, embedded, pt, et, None)
        except Exception as e:
            return (False, idx, fn, size_mb, 0, 0, 0, 0, 0, str(e))

    num_workers = max(1, args.workers)
    if num_workers == 1:
        for i, filepath in enumerate(to_process, 1):
            success, idx, fn, size_mb, chunks, tags, embedded, pt, et, err = process_file_worker(i, filepath)
            if success:
                total_chunks += chunks
                total_embedded += embedded
                print(f"  [{already_done + i}/{len(all_files)}] {fn} ({size_mb:.1f} MB)... OK ({chunks} chunks, {embedded} embedded, parse:{pt:.1f}s embed:{et:.1f}s)")
            else:
                print(f"  [{already_done + i}/{len(all_files)}] {fn} ({size_mb:.1f} MB)... FAILED: {err}")
    else:
        print(f"Executing with {num_workers} parallel worker threads...")
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(process_file_worker, i, fp) for i, fp in enumerate(to_process, 1)]
            for fut in as_completed(futures):
                success, idx, fn, size_mb, chunks, tags, embedded, pt, et, err = fut.result()
                if success:
                    total_chunks += chunks
                    total_embedded += embedded
                    print(f"  [{already_done + idx}/{len(all_files)}] {fn} ({size_mb:.1f} MB)... OK ({chunks} chunks, {embedded} embedded, parse:{pt:.1f}s embed:{et:.1f}s)")
                else:
                    print(f"  [{already_done + idx}/{len(all_files)}] {fn} ({size_mb:.1f} MB)... FAILED: {err}")

    elapsed = time.time() - t_start
    rem_after = len(remaining) - len(to_process)
    print(f"\n{'='*60}")
    print(f"  JOB RUN COMPLETE")
    print(f"  Files processed this run: {len(to_process)}")
    print(f"  Files remaining overall:  {rem_after}")
    print(f"  Total chunks in run:      {total_chunks:,}")
    print(f"  Chunks embedded in run:   {total_embedded:,}")
    print(f"  Job time:                 {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"{'='*60}")

    # Final verification & WAL maintenance
    with get_db() as conn:
        cur = conn.cursor()
        for table in ["files", "file_chunks", "fts_files", "tags"]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {cur.fetchone()[0]}")

    from src.infrastructure.database import run_maintenance
    run_maintenance()


if __name__ == "__main__":
    main()
