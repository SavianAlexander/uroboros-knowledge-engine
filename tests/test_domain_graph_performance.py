import src.core.config as config
import src.infrastructure.database as db
"""
Unit and Integration Performance Test Suite for Knowledge Graph & Wikilink Engine.
Benchmarks 1,000-node graph query execution latency (< 50ms), wikilink regex parsing,
and shared tag cluster edge generation.
"""

import os
import sys
from src.infrastructure.database import get_db_connection
import time
import shutil
import tempfile
import sqlite3
import statistics
import unittest
from fastapi.testclient import TestClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main
from src.domain.wikilink_parser import (
    WikilinkMatch,
    parse_wikilinks,
    normalize_target_title,
    slugify_title,
    extract_target_titles,
)


class TestWikilinkParserDomain(unittest.TestCase):
    """Unit tests for pure domain wikilink_parser module."""

    def test_01_wikilink_syntax_forms(self):
        """
        Preconditions: Raw text strings containing standard, aliased, anchored, and combined wikilink syntaxes.
        Invariants: Wikilink parser extracts target titles, anchors, display aliases, and slugified identifiers accurately.
        Outcomes: Verifies parsing fidelity across all 4 canonical wikilink syntax variants.
        """
        text = (
            "Here is [[Doc Alpha]], a link to [[Doc Beta|Second Document]], "
            "a section link [[Doc Gamma#Section 1]], and combined "
            "[[Doc Delta#Section 2|Fourth Document]]."
        )
        matches = parse_wikilinks(text)
        self.assertEqual(len(matches), 4)

        # Form 1: [[target]]
        self.assertEqual(matches[0].target_title, "Doc Alpha")
        self.assertIsNone(matches[0].anchor)
        self.assertIsNone(matches[0].alias)
        self.assertEqual(matches[0].slug, "doc_alpha")

        # Form 2: [[target|label]]
        self.assertEqual(matches[1].target_title, "Doc Beta")
        self.assertIsNone(matches[1].anchor)
        self.assertEqual(matches[1].alias, "Second Document")
        self.assertEqual(matches[1].slug, "doc_beta")

        # Form 3: [[target#anchor]]
        self.assertEqual(matches[2].target_title, "Doc Gamma")
        self.assertEqual(matches[2].anchor, "Section 1")
        self.assertIsNone(matches[2].alias)
        self.assertEqual(matches[2].slug, "doc_gamma")

        # Form 4: [[target#anchor|label]]
        self.assertEqual(matches[3].target_title, "Doc Delta")
        self.assertEqual(matches[3].anchor, "Section 2")
        self.assertEqual(matches[3].alias, "Fourth Document")
        self.assertEqual(matches[3].slug, "doc_delta")

    def test_02_normalize_and_slugify(self):
        """
        Preconditions: Document title strings containing file extension suffixes, punctuation, and leading/trailing whitespace.
        Invariants: Normalization strips extensions/spaces; slugification converts titles to lower_snakecase identifiers.
        Outcomes: Verifies target title normalization and slug generation logic.
        """
        self.assertEqual(normalize_target_title("  My Document.md  "), "My Document")
        self.assertEqual(normalize_target_title("Notes.TXT"), "Notes")
        self.assertEqual(normalize_target_title("  Plain Title  "), "Plain Title")

        self.assertEqual(slugify_title("  My Document.md  "), "my_document")
        self.assertEqual(slugify_title("Project-Architecture_v2.0.txt"), "project_architecture_v20")
        self.assertEqual(slugify_title(""), "")

    def test_03_extract_target_titles(self):
        """
        Preconditions: Document content containing repeated and anchored wikilinks.
        Invariants: Target title extraction preserves first-seen order and filters duplicate normalized target titles.
        Outcomes: Verifies order preservation and title deduplication during wikilink extraction.
        """
        content = "Check [[Alpha.md]], then [[Beta#sec|Label]], and [[Alpha]] again."
        titles = extract_target_titles(content)
        self.assertEqual(titles, ["Alpha", "Beta"])

    def test_04_empty_and_malformed(self):
        """
        Preconditions: Empty string, whitespace-only brackets, or non-wikilink text strings.
        Invariants: Wikilink parser returns empty list without throwing errors.
        Outcomes: Verifies safe handling and graceful degradation for empty or malformed inputs.
        """
        self.assertEqual(parse_wikilinks(""), [])
        self.assertEqual(parse_wikilinks("[[ ]]"), [])
        self.assertEqual(parse_wikilinks("No wikilinks here"), [])


class TestDomainGraphPerformance(unittest.TestCase):
    """Integration and performance benchmark test suite for GET /api/graph."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_graph_perf_")
        self.db_backup = db.DB_FILE
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_graph.db")
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()
        self.client = TestClient(main.app)

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_graph_performance_1000_nodes(self):
        """
        Preconditions: Database seeded with 1,000 document records and tag associations.
        Invariants: Cold graph generation execution latency stays strictly under 50.0ms SLA threshold.
        Outcomes: Verifies 1,000-node graph payload structure and sub-50ms execution speed.
        """
        from src.app.routers.search import get_graph_data_endpoint

        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            file_rows = []
            now = time.time()
            for i in range(1, 1001):
                filepath = f"c:/data/doc_{i}.md"
                filename = f"doc_{i}.md"
                content = f"Document content {i} with link [[doc_{(i % 1000) + 1}.md]]"
                file_rows.append((filepath, filename, 1024, "text/markdown", now, content))
            
            cursor.executemany(
                "INSERT INTO files (filepath, filename, file_size, mime_type, modified_at, content) VALUES (?, ?, ?, ?, ?, ?)",
                file_rows
            )
            
            tag_rows = []
            for i in range(1, 101):
                tag_rows.append((i, "core"))
                if i % 2 == 0:
                    tag_rows.append((i, "benchmark"))
            
            cursor.executemany("INSERT INTO tags (file_id, tag) VALUES (?, ?)", tag_rows)
            conn.commit()

        response = self.client.get("/api/graph?limit=1000&include_wikilinks=true&include_clusters=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertGreaterEqual(len(data["nodes"]), 1000)

        from src.app.routers.search import _build_graph_cached
        latencies = []
        for _ in range(5):
            _build_graph_cached.cache_clear()
            t0 = time.perf_counter()
            result = get_graph_data_endpoint(limit=1000, include_wikilinks=True, include_clusters=True)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)
            self.assertGreaterEqual(len(result["nodes"]), 1000)

        cold_latency_ms = statistics.median(latencies)
        self.assertLess(cold_latency_ms, 50.0, f"Graph endpoint cold latency ({cold_latency_ms:.2f}ms) exceeded 50ms SLA threshold!")

    def test_02_wikilink_edge_extraction(self):
        """
        Preconditions: Database contains documents with embedded cross-document wikilinks.
        Invariants: Graph builder creates `wikilink_to` edges connecting document nodes.
        Outcomes: Verifies edge relationship extraction and correct source/target node pairing.
        """
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, content) VALUES (1, 'c:/a.md', 'Alpha.md', 'See [[Beta.md]] and [[Gamma.md#sec|Link]])')"
            )
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, content) VALUES (2, 'c:/b.md', 'Beta.md', 'Content B')"
            )
            cursor.execute(
                "INSERT INTO files (id, filepath, filename, content) VALUES (3, 'c:/c.md', 'Gamma.md', 'Content C')"
            )
            conn.commit()

        response = self.client.get("/api/graph?limit=10&include_wikilinks=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        wikilink_edges = [e for e in data["edges"] if e.get("type") == "wikilink_to"]
        self.assertEqual(len(wikilink_edges), 2)
        
        edge_pairs = set((e["source"], e["target"]) for e in wikilink_edges)
        self.assertIn(("file_1", "file_2"), edge_pairs)
        self.assertIn(("file_1", "file_3"), edge_pairs)

    def test_03_shared_tag_cluster_edges(self):
        """
        Preconditions: Database populated with documents sharing common knowledge tags.
        Invariants: Graph builder forms `shared_tag_cluster` edges with weights matching shared tag counts.
        Outcomes: Verifies cluster edge weight computation and document co-tag adjacency.
        """
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (1, 'c:/doc1.md', 'doc1.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (2, 'c:/doc2.md', 'doc2.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (3, 'c:/doc3.md', 'doc3.md')")
            
            tags = [
                (1, "t1"), (1, "t2"),
                (2, "t1"), (2, "t2"),
                (3, "t2")
            ]
            cursor.executemany("INSERT INTO tags (file_id, tag) VALUES (?, ?)", tags)
            conn.commit()

        response = self.client.get("/api/graph?limit=10&include_clusters=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        cluster_edges = [e for e in data["edges"] if e.get("type") == "shared_tag_cluster"]
        self.assertGreaterEqual(len(cluster_edges), 2)

        edge_map = {(e["source"], e["target"]): e["weight"] for e in cluster_edges}
        self.assertEqual(edge_map.get(("file_1", "file_2")), 2)
        self.assertEqual(edge_map.get(("file_2", "file_3")), 1)

    def test_04_query_parameter_filtering(self):
        """
        Preconditions: Database containing document nodes, wikilinks, and tags.
        Invariants: Endpoint query parameters (`limit`, `include_wikilinks`, `include_clusters`) restrict output contents.
        Outcomes: Verifies parameter filtering, node limits, and edge toggle options.
        """
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            for i in range(1, 11):
                cursor.execute(
                    "INSERT INTO files (id, filepath, filename, content) VALUES (?, ?, ?, ?)",
                    (i, f"c:/file_{i}.md", f"file_{i}.md", f"Link [[file_{i+1}.md]]")
                )
                cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, 'tagA')", (i,))
            conn.commit()

        res = self.client.get("/api/graph?limit=3")
        self.assertEqual(res.status_code, 200)
        doc_nodes = [n for n in res.json()["nodes"] if n["type"] == "document"]
        self.assertEqual(len(doc_nodes), 3)

        res_no_extra = self.client.get("/api/graph?include_wikilinks=false&include_clusters=false")
        self.assertEqual(res_no_extra.status_code, 200)
        edges = res_no_extra.json()["edges"]
        types = set(e["type"] for e in edges)
        self.assertNotIn("wikilink_to", types)
        self.assertNotIn("shared_tag_cluster", types)

    def test_05_schema_fields_and_dual_compatibility(self):
        """
        Preconditions: Database containing file metadata and tag entries.
        Invariants: Graph API JSON response populates both modern `edges` and legacy `links` array fields.
        Outcomes: Verifies JSON schema field compliance and backward compatibility aliases.
        """
        with get_db_connection(db.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO files (id, filepath, filename, file_size, mime_type, modified_at) VALUES (1, 'c:/a.md', 'a.md', 512, 'text/markdown', 123456)")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (1, 'demo')")
            conn.commit()

        res = self.client.get("/api/graph")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIn("links", data)
        self.assertEqual(data["edges"], data["links"])

        doc_node = [n for n in data["nodes"] if n["type"] == "document"][0]
        self.assertEqual(doc_node["id"], "file_1")
        self.assertEqual(doc_node["title"], "a.md")
        self.assertEqual(doc_node["filepath"], "c:/a.md")
        self.assertEqual(doc_node["path"], "c:/a.md")
        self.assertEqual(doc_node["size"], 512)
        self.assertEqual(doc_node["mime_type"], "text/markdown")
        self.assertEqual(doc_node["updated_at"], 123456)


if __name__ == "__main__":
    unittest.main()
