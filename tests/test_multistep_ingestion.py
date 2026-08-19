import src.infrastructure.database as db
"""
Standalone assert-based test check for the multistep ingestion workflow.
Validates: Upload -> Directory Indexing -> Parser Fallback -> Auto-Tag Rules -> SQLite & FTS DB Storage.
"""
import os
import sys
import shutil
import tempfile
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import know

def test_multistep_ingestion():
    temp_dir = os.path.realpath(tempfile.mkdtemp(prefix="test_ingest_"))
    db_file = os.path.join(temp_dir, "test_ingest.db")
    db.DB_FILE = db_file
    if hasattr(know, "reset_db_connections"):
        know.reset_db_connections()
    know.init_db()

    # 1. Setup auto-tag rule
    conn = know.get_db()
    with conn:
        conn.execute("INSERT INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", ("quantum", "physics", 1))

    # 2. Prepare sample files for ingestion
    doc1 = os.path.join(temp_dir, "sample_quantum.txt")
    with open(doc1, "w", encoding="utf-8") as f:
        f.write("Exploring quantum entanglement and superposition principles.")

    doc2 = os.path.join(temp_dir, "empty.txt")
    with open(doc2, "w", encoding="utf-8") as f:
        f.write("")

    doc3 = os.path.join(temp_dir, "corrupt.pdf")
    with open(doc3, "w", encoding="utf-8") as f:
        f.write("Not a valid PDF header content")

    doc4 = os.path.join(temp_dir, "cp1252_sample.txt")
    with open(doc4, "wb") as f:
        f.write("René Descartes philosophy on quantum thought".encode("cp1252"))

    callback_called = [False]
    def cb():
        callback_called[0] = True

    # 3. Trigger directory indexing workflow with completion callback
    know.index_directory(temp_dir, on_complete_callback=cb)
    assert callback_called[0] is True, "Completion callback was not triggered"

    # 4. Assert ingestion results in SQLite database
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, file_size, content, acl_permissions FROM files WHERE filepath = ?", (doc1,))
    row1 = cursor.fetchone()
    assert row1 is not None, "Sample quantum text file was not ingested"
    assert "quantum entanglement" in row1["content"], "File content not extracted"
    assert row1["acl_permissions"] is not None, "ACL permissions metadata missing"
    assert ("ACL" in row1["acl_permissions"] or "readable" in row1["acl_permissions"] or "DACL" in row1["acl_permissions"] or "POSIX" in row1["acl_permissions"]), "ACL status missing"

    # Assert non-UTF8 CP1252 file handling
    cursor.execute("SELECT content FROM files WHERE filepath = ?", (doc4,))
    row4 = cursor.fetchone()
    assert row4 is not None, "CP1252 file was not ingested"
    assert "René Descartes" in row4["content"], "CP1252 multi-encoding fallback failed"

    # Assert 0-byte file handling
    cursor.execute("SELECT file_size, content FROM files WHERE filepath = ?", (doc2,))
    row2 = cursor.fetchone()
    assert row2 is not None, "Empty text file was not ingested"
    assert row2["file_size"] == 0, "Empty file size mismatch"

    # Assert corrupt PDF parser fallback
    cursor.execute("SELECT content FROM files WHERE filepath = ?", (doc3,))
    row3 = cursor.fetchone()
    assert row3 is not None, "Corrupt PDF was not ingested"
    assert "[Parsing Error:" in row3["content"], "Corrupt PDF error snippet missing"

    # Assert auto-tagging rule applied automatically
    cursor.execute("""
        SELECT t.tag FROM tags t
        JOIN files f ON t.file_id = f.id
        WHERE f.filepath = ?
    """, (doc1,))
    tags = [r["tag"] for r in cursor.fetchall()]
    assert "physics" in tags, f"Auto-tag 'physics' not applied to doc1, got {tags}"

    # Assert O(1) folder path migration
    new_dir = os.path.join(temp_dir, "moved_dir")
    know.migrate_folder_path(temp_dir, new_dir)
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files WHERE filepath LIKE ?", (new_dir + "%",))
    moved_count = cursor.fetchone()[0]
    assert moved_count > 0, "Folder migration path replacement failed"

    # Cleanup connection & temp dir
    try:
        conn.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
                pass
    print("[OK] Multistep ingestion workflow validation passed successfully.")

if __name__ == "__main__":
    test_multistep_ingestion()
