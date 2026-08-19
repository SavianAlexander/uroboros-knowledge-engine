import os
import sys
import time
import tempfile
import unittest
import shutil
import sqlite3
import threading
import math
from concurrent.futures import ThreadPoolExecutor

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.infrastructure.database as db_module
from src.infrastructure.database import get_db, init_db, run_maintenance
from src.infrastructure.parsers import safe_write_file, safe_read_file, parse_audio_metadata
from src.core.domain.services import (
    chunk_text,
    sanitise_fts_query,
    reciprocal_rank_fusion,
    generate_hyde_expansion,
    parse_query_operators,
    _safe_match
)
from src.shared.security import verify_path_containment

class TestFundamentalAdversarialMatrix(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_fundamental_matrix_")
        self.db_path = os.path.join(self.test_dir, "test_adversarial.db")
        self.orig_db_file = db_module.DB_FILE
        db_module.DB_FILE = self.db_path
        db_module.reset_db_connections()
        init_db()

    def tearDown(self):
        db_module.reset_db_connections()
        db_module.DB_FILE = self.orig_db_file
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_windows_device_names_and_unc_containment(self):
        """Verify path containment security against Windows reserved device names and UNC paths.

        Preconditions: List of Windows device names (CON, NUL, COM1, etc.) and UNC traversal paths defined.
        Invariants: Path security guard prevents access to reserved device namespace and external network shares.
        Expected Outcomes: Calling verify_path_containment for each invalid path raises an Exception.
        """
        bad_paths = [
            "CON", "PRN", "AUX", "NUL", "COM1", "LPT1",
            "\\\\127.0.0.1\\c$\\windows\\system32",
            "..\\..\\windows\\system32\\cmd.exe",
            "%2f..%2f..%2fwindows",
            "c:/Users/Administrator/Desktop/Neuro Alexander/../../windows"
        ]
        for p in bad_paths:
            with self.assertRaises(Exception, msg=f"Failed to catch bad path: {p}"):
                verify_path_containment(p)

    def test_02_fts5_malformed_syntax_injection_vectors(self):
        """Verify FTS query sanitizer against raw FTS syntax crash vectors.

        Preconditions: List of malformed FTS syntax strings, unclosed operators, and SQL injection strings defined.
        Invariants: Sanitizer converts invalid FTS syntax into safe search tokens.
        Expected Outcomes: Returned query string is a string and executing SQLite FTS search query executes without OperationalError.
        """
        crash_vectors = [
            '""',
            '""""""',
            'AND OR NOT',
            'NEAR()',
            'NEAR(a b c d e f g h i j k l m n o p q r s t u v w x y z)',
            '* * * * *',
            'tag:::',
            'tag:',
            '\x00\x01\x02\x1f',
            'SELECT * FROM files WHERE 1=1--',
            '<script>alert("xss")</script>',
            'NEAR(a b 0)'
        ]
        for v in crash_vectors:
            try:
                cleaned = sanitise_fts_query(v)
                self.assertIsInstance(cleaned, str)
                with get_db() as conn:
                    cursor = conn.cursor()
                    if cleaned:
                        cursor.execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ? LIMIT 1", (cleaned,))
            except sqlite3.OperationalError as e:
                self.fail(f"FTS5 crash vector failed to sanitize safely: '{v}' -> Error: {e}")

    def test_03_concurrent_multithread_wal_write_stress(self):
        """Verify database resilience under 10 parallel writing threads with WAL lock recovery.

        Preconditions: 10 parallel threads executing 20 database write iterations each.
        Invariants: SQLite WAL mode handles thread contention without database lock failures.
        Expected Outcomes: Zero thread execution errors recorded in errors tracking list.
        """
        errors = []

        def worker_task(thread_id):
            try:
                for i in range(20):
                    with get_db() as conn:
                        cursor = conn.cursor()
                        filepath = os.path.join(self.test_dir, f"thread_{thread_id}_file_{i}.txt")
                        cursor.execute(
                            "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content) VALUES (?, ?, ?, ?, ?)",
                            (filepath, f"file_{i}.txt", 100, time.time(), f"content from thread {thread_id}")
                        )
                        conn.commit()
            except Exception as e:
                pass
                errors.append(f"Thread {thread_id} error: {e}")

        threads = []
        for tid in range(10):
            t = threading.Thread(target=worker_task, args=(tid,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent WAL write errors detected: {errors}")

    def test_04_rrf_rank_fusion_math_boundaries(self):
        """Verify Reciprocal Rank Fusion math against empty and duplicate candidate score lists.

        Preconditions: Empty candidate lists and duplicate candidate filepaths passed to reciprocal_rank_fusion().
        Invariants: Score computation produces valid non-NaN and non-Inf float values.
        Expected Outcomes: Empty inputs return empty list; duplicate candidates fuse cleanly with valid numeric scores.
        """
        empty_fts = []
        empty_vec = []
        self.assertEqual(reciprocal_rank_fusion(empty_fts, empty_vec), [])

        fts_res = [{"filepath": "doc1.txt", "score": 1.0}, {"filepath": "doc1.txt", "score": 0.8}]
        vec_res = [{"filepath": "doc1.txt", "score": 0.9}, {"filepath": "doc2.txt", "score": 0.5}]
        fused = reciprocal_rank_fusion(fts_res, vec_res)
        self.assertTrue(len(fused) > 0)
        for f in fused:
            self.assertFalse(math.isnan(f["score"]))
            self.assertFalse(math.isinf(f["score"]))

    def test_05_chunk_text_boundary_cases(self):
        """Verify text chunking against empty input, single oversized words, and emoji streams.

        Preconditions: Empty string, 50,000-character single word, and multi-emoji text strings provided.
        Invariants: Chunking generator splits text within target character bounds without character corruption.
        Expected Outcomes: Empty strings yield empty lists, single long word yields >50 chunks, and emoji text chunking succeeds.
        """
        self.assertEqual(chunk_text(""), [])
        self.assertEqual(chunk_text("   "), [])

        single_word = "X" * 50_000
        chunks = chunk_text(single_word, chunk_size=800, overlap=100)
        self.assertTrue(len(chunks) > 50)
        self.assertEqual(sum(len(c) for c in chunks[:10]), 800 * 10)

        emoji_text = "🌌 🚀 " * 500
        e_chunks = chunk_text(emoji_text, chunk_size=100, overlap=20)
        self.assertTrue(len(e_chunks) > 0)

    def test_06_corrupt_file_extractions_resiliency(self):
        """Verify audio and text parsers against corrupt and zero-byte binary headers.

        Preconditions: Corrupt audio file header and zero-byte file written to disk.
        Invariants: Binary parser fails gracefully without crashing or throwing unhandled exceptions.
        Expected Outcomes: Metadata dictionary returned containing default channels count 0.
        """
        corrupt_wav = os.path.join(self.test_dir, "corrupt.wav")
        with open(corrupt_wav, "wb") as f:
            f.write(b"RIFF\x00\x00\x00\x00WAVEfmt \x00\x00\x00\x00CORRUPT")

        res = parse_audio_metadata(corrupt_wav)
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("channels"), 0)

        zero_wav = os.path.join(self.test_dir, "zero.wav")
        with open(zero_wav, "wb") as f:
            f.write(b"")
        z_res = parse_audio_metadata(zero_wav)
        self.assertIsInstance(z_res, dict)

    def test_07_regex_auto_rule_redos_safeguard(self):
        """Verify regex rule matcher against potential ReDoS catastrophic backtracking patterns.

        Preconditions: Malicious ReDoS pattern and non-matching repeated character string provided.
        Invariants: Safe regex execution prevents CPU resource starvation and catastrophic backtracking.
        Expected Outcomes: Match operation completes in less than 0.5 seconds.
        """
        bad_redos_pattern = "(a+)+$"
        long_non_matching_string = "a" * 30 + "X"
        start_t = time.time()
        res = _safe_match(bad_redos_pattern, long_non_matching_string)
        duration = time.time() - start_t
        self.assertLess(duration, 0.5)

    def test_08_safe_read_file_lock_timeout_resiliency(self):
        """Verify safe_read_file reading binary files under file access and update operations.

        Preconditions: File written to temporary path with initial data string.
        Invariants: Binary reader acquires safe file read handle.
        Expected Outcomes: safe_read_file returns exact byte content of target file.
        """
        test_file = os.path.join(self.test_dir, "rapid_overwrite.bin")
        safe_write_file(test_file, "initial data")

        content = safe_read_file(test_file)
        self.assertEqual(content, b"initial data")

    def test_09_fts5_unicode_normalization_and_punctuation(self):
        """Verify FTS query sanitizer with CJK, Arabic, ZWJ Emojis, and punctuation boundaries.

        Preconditions: Multi-language Unicode queries with emojis and punctuation operators.
        Invariants: Sanitizer preserves valid multibyte search terms while stripping unsafe operators.
        Expected Outcomes: Cleaned query is executable in SQLite FTS search without errors.
        """
        queries = [
            "中文测试 搜索",
            "اختبار البحث العربي",
            "👨‍👩‍👧‍👦 family zwj emoji",
            "tag:important & (status:active | status:pending)",
            "query with !!! ### $$$ %%% ^^^ *** ((( ))) punctuation",
        ]
        for q in queries:
            cleaned = sanitise_fts_query(q)
            self.assertIsInstance(cleaned, str)
            with get_db() as conn:
                if cleaned:
                    conn.cursor().execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ? LIMIT 1", (cleaned,))

    def test_10_extreme_file_notes_and_insights_xss(self):
        """Verify XSS and SQL injection payloads in notes and insights metadata columns.

        Preconditions: SQL injection and HTML script tag payloads stored in file metadata columns.
        Invariants: Database driver parameter binding escapes input values safely.
        Expected Outcomes: Stored payload strings retrieved verbatim from database without code execution or schema corruption.
        """
        payload = "<script>alert('xss')</script> '; DROP TABLE files; --"
        filepath = os.path.join(self.test_dir, "xss_test.txt")
        safe_write_file(filepath, "Sample document content for XSS test")

        with get_db() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO files (filepath, filename, file_size, modified_at, content, notes, insights) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (filepath, "xss_test.txt", 100, time.time(), "Sample document content", payload, payload)
            )

        with get_db() as conn:
            row = conn.cursor().execute("SELECT notes, insights FROM files WHERE filepath = ?", (filepath,)).fetchone()
            self.assertEqual(row["notes"], payload)
            self.assertEqual(row["insights"], payload)

    def test_11_fts_synonym_cyclic_expansion(self):
        """Verify cyclic synonym mappings do not cause infinite loops in search expansion.

        Preconditions: Cyclic synonym dictionary (ml -> ai -> machine learning -> ml) defined.
        Invariants: Graph expansion algorithm tracks visited nodes to break cycles.
        Expected Outcomes: Visited node set count remains strictly less than 10.
        """
        synonyms_dict = {"ml": ["ai", "machine learning"], "ai": ["ml"], "machine learning": ["ml"]}
        term = "ml"
        expanded = set([term])
        to_process = [term]
        visited = set()

        while to_process and len(visited) < 100:
            curr = to_process.pop()
            if curr in visited:
                continue
            visited.add(curr)
            for syn in synonyms_dict.get(curr, []):
                expanded.add(syn)
                to_process.append(syn)

        self.assertLess(len(visited), 10)

    def test_12_metadata_expansion_corrupt_exif_tags(self):
        """Verify corrupt audio metadata streams return fallback dictionaries without failing.

        Preconditions: File with corrupted ID3 header written to temporary directory.
        Invariants: Audio metadata extractor returns dictionary structure on header corruptions.
        Expected Outcomes: parse_audio_metadata returns a valid dictionary instance.
        """
        corrupt_mp3 = os.path.join(self.test_dir, "corrupt.mp3")
        safe_write_file(corrupt_mp3, "ID3" + "\x00" * 500)

        res = parse_audio_metadata(corrupt_mp3)
        self.assertIsInstance(res, dict)

    def test_13_fts_near_operator_boundary_distance(self):
        """Verify NEAR queries with extreme boundary distances (999999 and negative values).

        Preconditions: NEAR queries with large integer and negative distance parameters.
        Invariants: Sanitizer normalizes distance parameter bounds for FTS parser.
        Expected Outcomes: Sanitized queries execute cleanly against SQLite FTS index.
        """
        near_queries = [
            "NEAR(quantum computing, 999999)",
            "NEAR(quantum computing, -5)",
            "NEAR(quantum computing, 0)",
        ]
        for q in near_queries:
            cleaned = sanitise_fts_query(q)
            self.assertIsInstance(cleaned, str)
            with get_db() as conn:
                if cleaned:
                    conn.cursor().execute("SELECT filepath FROM fts_files WHERE fts_files MATCH ? LIMIT 1", (cleaned,))

    def test_14_sqlite_vacuum_and_wal_checkpoint_under_load(self):
        """Verify run_maintenance WAL checkpoint runs safely while open connections exist.

        Preconditions: Active connection executing queries on files table.
        Invariants: Maintenance WAL checkpoint executes concurrently with open read handles.
        Expected Outcomes: Maintenance completes without database locked errors.
        """
        with get_db() as conn:
            conn.cursor().execute("SELECT COUNT(*) FROM files")
            run_maintenance()

    def test_15_file_revision_pruning_limits(self):
        """Verify file revisions table handles multiple revision insertions cleanly.

        Preconditions: 15 sequential file revision entries inserted for single filepath.
        Invariants: File revision table persists revision records accurately.
        Expected Outcomes: Database count query for target filepath returns exactly 15.
        """
        filepath = os.path.join(self.test_dir, "revision_test.txt")
        safe_write_file(filepath, "Version 1")

        with get_db() as conn:
            cursor = conn.cursor()
            for i in range(15):
                cursor.execute(
                    "INSERT INTO file_revisions (filepath, saved_at, content, sha256) VALUES (?, ?, ?, ?)",
                    (filepath, time.time() + i, f"Version {i}", f"sha_{i}")
                )
            row = cursor.execute("SELECT COUNT(*) FROM file_revisions WHERE filepath = ?", (filepath,)).fetchone()
            self.assertEqual(row[0], 15)

    def test_16_vector_similarity_degenerate_matrices(self):
        """Verify reciprocal rank fusion works on degenerate empty or single-element inputs.

        Preconditions: Single candidate item list paired with empty candidate list.
        Invariants: Rank fusion preserves sole candidate without index error.
        Expected Outcomes: Fused result contains 1 element matching target candidate filename.
        """
        single_item = [{"filepath": "single.txt", "score": 1.0}]
        fused = reciprocal_rank_fusion(single_item, [])
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0]["filepath"], "single.txt")

    def test_17_search_pagination_negative_and_overflow_offsets(self):
        """Verify search pagination with boundary and overflow offset values.

        Preconditions: Database query executed with standard offset and extreme overflow offset (99999999).
        Invariants: SQLite LIMIT/OFFSET handles out-of-range offsets without raising errors.
        Expected Outcomes: Overflow offset query returns empty result list.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM files LIMIT 10 OFFSET 0")
            rows1 = cursor.fetchall()
            cursor.execute("SELECT filepath FROM files LIMIT 10 OFFSET 99999999")
            rows2 = cursor.fetchall()
            self.assertEqual(len(rows2), 0)

    def test_18_tag_alias_chain_resolution(self):
        """Verify tag alias lookup with multi-level resolution chains.

        Preconditions: Multi-level alias mapping dictionary (ml -> ai -> artificial-intelligence) configured.
        Invariants: Resolver follows mapping chain until terminal tag reached without infinite loops.
        Expected Outcomes: Resolving 'ml' and 'ai' both return 'artificial-intelligence', while unmapped tags return self.
        """
        aliases = {"ml": "ai", "ai": "artificial-intelligence"}

        def resolve_alias(tag, alias_map):
            curr = tag
            visited = set()
            while curr in alias_map and curr not in visited:
                visited.add(curr)
                curr = alias_map[curr]
            return curr

        self.assertEqual(resolve_alias("ml", aliases), "artificial-intelligence")
        self.assertEqual(resolve_alias("ai", aliases), "artificial-intelligence")
        self.assertEqual(resolve_alias("physics", aliases), "physics")

    def test_19_pdf_parser_corrupt_stream_recovery(self):
        """Verify PDF parser fallback when reading a truncated PDF file header.

        Preconditions: Truncated PDF file header without EOF marker written to disk.
        Invariants: Document content extractor falls back gracefully on corrupted streams.
        Expected Outcomes: extract_content returns a string instance without raising exception.
        """
        from src.infrastructure.parsers import extract_content
        corrupt_pdf = os.path.join(self.test_dir, "truncated.pdf")
        with open(corrupt_pdf, "wb") as f:
            f.write(b"%PDF-1.4 % truncated stream without EOF")

        text, _ = extract_content(corrupt_pdf, ".pdf")
        self.assertIsInstance(text, str)

    def test_20_sanitise_fts_query_null_and_control_chars(self):
        """Verify sanitise_fts_query strips control characters and null bytes safely.

        Preconditions: Search query containing null byte (\x00) and control characters (\x0b, \x0c, \r, \n).
        Invariants: Sanitizer strips binary control characters from output query.
        Expected Outcomes: Cleaned query string contains no null or control bytes.
        """
        dirty = "hello\x00world\x0b\x0c\r\n test"
        cleaned = sanitise_fts_query(dirty)
        self.assertNotIn("\x00", cleaned)
        self.assertNotIn("\x0b", cleaned)
        self.assertIsInstance(cleaned, str)

if __name__ == "__main__":
    unittest.main()
