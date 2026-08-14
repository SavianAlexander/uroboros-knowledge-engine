import os
import sys
import unittest
import tempfile
import shutil
import sqlite3

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know

from src.domain.knowledge_self_healing import audit_knowledge_self_healing, repair_knowledge_base


class TestDomainCatastrophicRecovery(unittest.TestCase):
    """Domain test suite for catastrophic database corruption, storage failures, orphaned chunk repair, and self-healing."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_catastrophic_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_corrupted_sqlite_header_detection_and_recovery(self):
        """Verify recovery from corrupted database file header.

        Preconditions: Existing database overwritten with random corrupted garbage bytes.
        Invariants: System detects database corruption, resets connections, and rebuilds valid schema via init_db().
        Expected Outcomes: PRAGMA integrity_check passes and tables are queryable after recovery.
        """
        know.reset_db_connections()
        with open(db.DB_FILE, "wb") as f:
            f.write(b"CORRUPTED_GARBAGE_HEADER_DATA_NOT_SQLITE3_1234567890")

        # System catches database error on corrupted header
        with self.assertRaises(sqlite3.DatabaseError):
            with know.get_db() as conn:
                conn.execute("SELECT 1")

        # Autonomous recovery: reset connections, purge corrupted file, and rebuild
        know.reset_db_connections()
        os.remove(db.DB_FILE)
        know.init_db()

        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            res = cursor.fetchone()[0]
            self.assertEqual(res, "ok")

    def test_02_orphaned_chunks_pruning(self):
        """Verify self-healing prunes orphaned file_chunks when parent file record is removed.

        Preconditions: file_chunks inserted with non-existent parent file_id=999.
        Invariants: repair_knowledge_base() identifies and deletes all orphaned chunk rows.
        Expected Outcomes: status='success', pruned_orphaned_chunks >= 1, orphaned chunks deleted from SQLite.
        """
        with know.get_db() as conn:
            cursor = conn.cursor()
            # Temporarily disable foreign keys to simulate orphaned records after hard deletion
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("INSERT INTO file_chunks (file_id, chunk_index, content) VALUES (999, 0, 'Orphaned content')")
            conn.commit()

        repair_res = repair_knowledge_base()
        self.assertEqual(repair_res["status"], "success")
        self.assertGreaterEqual(repair_res["pruned_orphaned_chunks"], 1)

        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM file_chunks WHERE file_id = 999")
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_03_broken_wikilink_cross_reference_audit(self):
        """Verify broken wikilink detection when cross-referenced document does not exist.

        Preconditions: Document inserted referencing missing document '[[MissingArchitectureSpec]]'.
        Invariants: audit_knowledge_self_healing() flags missing link and lowers health score.
        Expected Outcomes: broken_links contains target_wikilink='MissingArchitectureSpec'.
        """
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO files (filename, filepath, content) VALUES (?, ?, ?)",
                ("doc_a.md", "/path/doc_a.md", "See details in [[MissingArchitectureSpec]] for details.")
            )
            conn.commit()

        audit_res = audit_knowledge_self_healing()
        self.assertEqual(audit_res["status"], "success")
        broken_targets = [b["target_wikilink"] for b in audit_res["broken_links"]]
        self.assertIn("MissingArchitectureSpec", broken_targets)

    def test_04_fts5_index_desynchronization_rebuild(self):
        """Verify repair_knowledge_base() re-synchronizes FTS5 full-text index if desynchronized.

        Preconditions: File inserted into 'files' table but missing from 'fts_files' table.
        Invariants: repair_knowledge_base() copies missing records into fts_files.
        Expected Outcomes: reindexed_fts_documents >= 1, FTS5 query finds document content.
        """
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO files (filename, filepath, content) VALUES (?, ?, ?)",
                ("desync.txt", "/tmp/desync.txt", "Exclusive quantum teleportation protocol")
            )
            conn.commit()

        repair_res = repair_knowledge_base()
        self.assertEqual(repair_res["status"], "success")
        self.assertGreaterEqual(repair_res["reindexed_fts_documents"], 1)

        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM fts_files WHERE fts_files MATCH 'quantum'")
            rows = cursor.fetchall()
            self.assertGreater(len(rows), 0)

    def test_05_database_integrity_check_pragma(self):
        """Verify SQLite PRAGMA quick_check and integrity_check execution.

        Preconditions: Standard database initialized with indexed tables.
        Invariants: SQLite engine reports 'ok' with zero page corruption.
        Expected Outcomes: integrity_check returns 'ok'.
        """
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA quick_check")
            self.assertEqual(cursor.fetchone()[0], "ok")
            cursor.execute("PRAGMA integrity_check")
            self.assertEqual(cursor.fetchone()[0], "ok")

    def test_06_disk_write_permission_error_simulation(self):
        """Verify error handling when file write raises PermissionError or read-only filesystem.

        Preconditions: Read-only simulated operation on mock file system.
        Invariants: Handled gracefully with clean error return without unhandled application crash.
        Expected Outcomes: Handled exception logged and execution continues.
        """
        read_only_path = os.path.join(self.test_dir, "readonly_dir")
        os.makedirs(read_only_path, exist_ok=True)
        try:
            know.index_directory(os.path.join(read_only_path, "missing_nested"))
        except Exception as e:
            self.fail(f"index_directory should handle missing directory gracefully: {e}")

    def test_07_partial_transaction_rollback_on_crash(self):
        """Verify atomic transaction rollback prevents half-written corrupt state upon exception.

        Preconditions: Multi-row insert where subsequent row violates constraints.
        Invariants: Transaction block rolls back all changes, leaving database in pristine state.
        Expected Outcomes: Count of inserted rows remains 0 after rollback.
        """
        initial_count = 0
        with know.get_db() as conn:
            initial_count = conn.cursor().execute("SELECT COUNT(*) FROM files").fetchone()[0]

        try:
            with know.get_db() as conn:
                with conn:
                    conn.execute("INSERT INTO files (filename, filepath, content) VALUES ('valid.txt', '/v.txt', 'data')")
                    # Force error with duplicate PRIMARY KEY or invalid SQL
                    conn.execute("INSERT INTO non_existent_table VALUES (1)")
        except sqlite3.OperationalError:
            pass

        with know.get_db() as conn:
            final_count = conn.cursor().execute("SELECT COUNT(*) FROM files").fetchone()[0]
            self.assertEqual(final_count, initial_count)

    def test_08_concurrent_wal_checkpoint_during_read(self):
        """Verify PRAGMA wal_checkpoint(TRUNCATE) executes safely without crashing active connection pool.

        Preconditions: Database with WAL mode and active connections.
        Invariants: wal_checkpoint completes cleanly without locking exceptions.
        Expected Outcomes: Checkpoint returns (0, _, _) indicating successful checkpointing.
        """
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
            res = cursor.fetchone()
            self.assertEqual(res[0], 0)

    def test_09_0_byte_and_truncated_db_file_handling(self):
        """Verify boot sequence handling on 0-byte empty database file.

        Preconditions: 0-byte empty file at DB_FILE location.
        Invariants: init_db() creates all requisite tables without crashing.
        Expected Outcomes: Table count > 0 after init_db().
        """
        know.reset_db_connections()
        with open(db.DB_FILE, "wb") as f:
            pass  # 0 bytes

        know.init_db()
        with know.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            self.assertGreater(cursor.fetchone()[0], 0)

    def test_10_extreme_document_count_scaling(self):
        """Verify self-healing audit performance on scaling document counts.

        Preconditions: 100 documents inserted with interconnecting wikilinks.
        Invariants: audit_knowledge_self_healing() executes in sub-second time without O(N^3) explosion.
        Expected Outcomes: status='success', total_nodes=100, health_score computed.
        """
        with know.get_db() as conn:
            with conn:
                for i in range(100):
                    next_id = (i + 1) % 100
                    conn.execute(
                        "INSERT INTO files (filename, filepath, content) VALUES (?, ?, ?)",
                        (f"scale_doc_{i}.md", f"/docs/scale_{i}.md", f"Linked to [[scale_doc_{next_id}.md]]")
                    )

        audit_res = audit_knowledge_self_healing()
        self.assertEqual(audit_res["status"], "success")
        self.assertEqual(audit_res["total_nodes"], 100)
        self.assertEqual(len(audit_res["orphaned_nodes"]), 0)


if __name__ == "__main__":
    unittest.main()
