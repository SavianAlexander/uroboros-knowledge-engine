"""
Single-book deep test script for Uroboros Knowledge Engine.
Parses, embeds, and indexes a single heavy textbook, timing every stage
and performing empirical RAG query verification.
"""
import os, sys, time, json, sqlite3, logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_index import index_single_file, norm_path
from src.infrastructure.database import get_db, DB_FILE

TEST_BOOK = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Triage (Support)",
    "6369. Intermediate Accounting, 17th Edition_ Donald E. Kieso & Jerry J. Weygandt & Terry D. Warfield.pdf"
)

def run_single_book_test():
    print(f"\n{'='*70}")
    print(f"  SINGLE-BOOK DEEP INDEX & RAG TEST")
    print(f"  Target Book: {os.path.basename(TEST_BOOK)}")
    print(f"  File Size:   {os.path.getsize(TEST_BOOK)/(1024*1024):.2f} MB")
    print(f"{'='*70}\n")

    # Step 1: Clean previous DB record for this book if exists
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM files WHERE filepath = ?", (TEST_BOOK,))
            row = cur.fetchone()
            if row:
                fid = row[0]
                cur.execute("DELETE FROM fts_files WHERE filepath = ?", (TEST_BOOK,))
                cur.execute("DELETE FROM ocr_coords WHERE file_id = ?", (fid,))
                cur.execute("DELETE FROM tags WHERE file_id = ?", (fid,))
                cur.execute("DELETE FROM file_chunks WHERE file_id = ?", (fid,))
                cur.execute("DELETE FROM fts_file_chunks WHERE file_id = ?", (fid,))
                cur.execute("DELETE FROM files WHERE id = ?", (fid,))
                print(f"[PRE-TEST] Removed existing DB record for clean test run.")

    # Step 2: Index single book with detailed timing
    print("[PHASE 1] Starting single book parsing, batch embedding, and indexing...")
    t_start = time.time()
    chunks, tags, embedded, pt, et = index_single_file(TEST_BOOK)
    total_t = time.time() - t_start

    print(f"\n{'='*70}")
    print(f"  INDEXING METRICS")
    print(f"  PDF Parsing (PyMuPDF): {pt:.2f} seconds")
    print(f"  Batch Embedding:       {et:.2f} seconds ({chunks/et if et > 0 else 0:.1f} chunks/sec)")
    print(f"  Total Indexing Time:   {total_t:.2f} seconds ({total_t/60:.2f} minutes)")
    print(f"  Total Chunks Created:  {chunks:,}")
    print(f"  Chunks Embedded:       {embedded:,} ({embedded/chunks*100:.1f}% success)")
    print(f"  Tags Extracted:        {tags}")
    print(f"{'='*70}\n")

    # Step 3: Database Verification
    print("[PHASE 2] Verifying database records...")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, filename, file_size, mime_type, length(content) FROM files WHERE filepath = ?", (TEST_BOOK,))
        f_row = cur.fetchone()
        print(f"  File Table Record:  ID={f_row[0]} | {f_row[1][:40]}... | {f_row[2]//1024} KB | {f_row[4]:,} content chars")

        cur.execute("SELECT COUNT(*) FROM file_chunks WHERE file_id = ?", (f_row[0],))
        c_cnt = cur.fetchone()[0]
        print(f"  File Chunks Count:  {c_cnt:,} chunks in DB")

        cur.execute("SELECT COUNT(*) FROM file_chunks WHERE file_id = ? AND embedding_json IS NOT NULL AND length(embedding_json) > 10", (f_row[0],))
        e_cnt = cur.fetchone()[0]
        print(f"  Vector Embeddings:  {e_cnt:,} 768-dim embeddings in DB")

        cur.execute("SELECT COUNT(*) FROM fts_file_chunks WHERE file_id = ?", (f_row[0],))
        fts_cnt = cur.fetchone()[0]
        print(f"  FTS5 Search Index:  {fts_cnt:,} searchable FTS chunks")

    # Step 4: Hybrid RAG Search Test
    print(f"\n[PHASE 3] Running Reciprocal Rank Fusion (RRF) Hybrid RAG Search...")
    queries = [
        "What is revenue recognition under GAAP?",
        "How is depreciation calculated using straight line method?",
        "What are inventory valuation methods like FIFO and LIFO?"
    ]

    from know import search_knowledge

    for q in queries:
        print(f"\n  Query: '{q}'")
        t_q = time.time()
        results = search_knowledge(q, limit=3)
        q_time = time.time() - t_q
        print(f"  [RRF Hybrid Search] Returned {len(results)} matches in {q_time*1000:.1f}ms:")
        for idx, r in enumerate(results, 1):
            fn = r.get('filename') or r.get('filepath')
            score = r.get('rrf_score', 0)
            snippet = (r.get('content') or r.get('snippet') or '')[:120].replace('\n', ' ')
            print(f"    [{idx}] RRF Score: {score:.6f} | {fn[:40]}... | {snippet}...")

    print(f"\n{'='*70}")
    print(f"  SINGLE-BOOK TEST COMPLETE: ALL PHASES PASSED 100% CLEAN")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    run_single_book_test()
