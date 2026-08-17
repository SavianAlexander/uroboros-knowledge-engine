import os
import sqlite3
import time

def purge_zombie_records(db_path: str = "knowledge.db"):
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist.")
        return

    print(f"[*] Connecting to {db_path}...")
    conn = sqlite3.connect(db_path, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Step 1: Scan files table for non-existent files
    cursor.execute("SELECT id, filepath FROM files")
    all_files = cursor.fetchall()
    print(f"[*] Total files in database: {len(all_files)}")

    missing_ids = []
    missing_paths = []
    for row in all_files:
        fid = row["id"]
        fpath = row["filepath"]
        if not os.path.exists(fpath):
            missing_ids.append(fid)
            missing_paths.append(fpath)

    print(f"[*] Identified {len(missing_ids)} zombie file records pointing to non-existent paths.")

    if not missing_ids:
        print("[+] No zombie file records found.")
        conn.close()
        return

    # Batch delete in chunks of 500
    batch_size = 500
    total_purged = 0

    cursor.execute("BEGIN TRANSACTION;")
    try:
        for i in range(0, len(missing_ids), batch_size):
            chunk_ids = missing_ids[i:i + batch_size]
            chunk_paths = missing_paths[i:i + batch_size]
            placeholders = ",".join("?" for _ in chunk_ids)

            # 1. file_chunks
            cursor.execute(f"DELETE FROM file_chunks WHERE file_id IN ({placeholders})", chunk_ids)

            # 2. tags
            cursor.execute(f"DELETE FROM tags WHERE file_id IN ({placeholders})", chunk_ids)

            # 3. ocr_coords
            cursor.execute(f"DELETE FROM ocr_coords WHERE file_id IN ({placeholders})", chunk_ids)

            # 4. tf_idf_index
            cursor.execute(f"DELETE FROM tf_idf_index WHERE file_id IN ({placeholders})", chunk_ids)

            # 5. fts_files
            path_placeholders = ",".join("?" for _ in chunk_paths)
            cursor.execute(f"DELETE FROM fts_files WHERE filepath IN ({path_placeholders})", chunk_paths)

            # 6. files
            cursor.execute(f"DELETE FROM files WHERE id IN ({placeholders})", chunk_ids)

            total_purged += len(chunk_ids)
            print(f"    Purged batch {i // batch_size + 1}: {total_purged}/{len(missing_ids)} records")

        conn.commit()
        print("[+] All zombie records deleted from relational tables and FTS tables.")
    except Exception as ex:
        conn.rollback()
        print(f"[!] Error during deletion: {ex}")
        conn.close()
        raise

    # Rebuild FTS indexes if applicable
    print("[*] Optimizing / Rebuilding FTS5 indexes...")
    try:
        cursor.execute("INSERT INTO fts_files(fts_files) VALUES('rebuild');")
    except Exception as e:
        print(f"    fts_files rebuild note: {e}")

    try:
        cursor.execute("INSERT INTO fts_file_chunks(fts_file_chunks) VALUES('rebuild');")
    except Exception as e:
        print(f"    fts_file_chunks rebuild note: {e}")

    conn.commit()

    # Check remaining
    cursor.execute("SELECT COUNT(*) FROM files")
    remaining_count = cursor.fetchone()[0]
    print(f"[+] Remaining verified file records in database: {remaining_count}")

    # Check for any remaining missing
    cursor.execute("SELECT id, filepath FROM files")
    remaining_files = cursor.fetchall()
    still_missing = [r["id"] for r in remaining_files if not os.path.exists(r["filepath"])]
    print(f"[+] Still missing check: {len(still_missing)} (Expected: 0)")

    # Run checkpoint and VACUUM
    print("[*] Running PRAGMA wal_checkpoint(TRUNCATE)...")
    cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    conn.commit()
    conn.close()

    print("[*] Running VACUUM on database to reclaim disk space...")
    t0 = time.perf_counter()
    vac_conn = sqlite3.connect(db_path, timeout=120.0)
    vac_conn.execute("VACUUM;")
    vac_conn.close()
    print(f"[+] VACUUM complete in {round((time.perf_counter() - t0)*1000, 2)}ms.")

if __name__ == "__main__":
    purge_zombie_records()
