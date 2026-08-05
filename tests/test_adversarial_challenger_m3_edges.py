"""
Adversarial Edge Correctness and Wikilink Stress Test Suite.
Evaluates wikilink parser syntax variants, target document matching,
directed `wikilink_to` edge creation, edge weight calculations,
and undirected `shared_tag_cluster` edge logic.
"""

import os
import sys
import time
import shutil
import tempfile
import sqlite3
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


class TestWikilinkParserSyntaxVariants(unittest.TestCase):
    """Stress tests for all wikilink parser syntax variants and boundary cases."""

    def test_01_standard_syntax_forms(self):
        """Verify the 4 standard wikilink syntax forms."""
        # 1. [[target]]
        m1 = parse_wikilinks("Link to [[Doc Alpha]]")
        self.assertEqual(len(m1), 1)
        self.assertEqual(m1[0].target_title, "Doc Alpha")
        self.assertIsNone(m1[0].anchor)
        self.assertIsNone(m1[0].alias)
        self.assertEqual(m1[0].slug, "doc_alpha")

        # 2. [[target|label]]
        m2 = parse_wikilinks("Link to [[Doc Alpha|Custom Display Label]]")
        self.assertEqual(len(m2), 1)
        self.assertEqual(m2[0].target_title, "Doc Alpha")
        self.assertIsNone(m2[0].anchor)
        self.assertEqual(m2[0].alias, "Custom Display Label")

        # 3. [[target#anchor]]
        m3 = parse_wikilinks("Link to [[Doc Alpha#Section 3]]")
        self.assertEqual(len(m3), 1)
        self.assertEqual(m3[0].target_title, "Doc Alpha")
        self.assertEqual(m3[0].anchor, "Section 3")
        self.assertIsNone(m3[0].alias)

        # 4. [[target#anchor|label]]
        m4 = parse_wikilinks("Link to [[Doc Alpha#Section 3|Custom Label]]")
        self.assertEqual(len(m4), 1)
        self.assertEqual(m4[0].target_title, "Doc Alpha")
        self.assertEqual(m4[0].anchor, "Section 3")
        self.assertEqual(m4[0].alias, "Custom Label")

    def test_02_trailing_extensions(self):
        """Stress test trailing extension stripping (.md, .txt, uppercase, other extensions)."""
        self.assertEqual(normalize_target_title("Document.md"), "Document")
        self.assertEqual(normalize_target_title("Document.MD"), "Document")
        self.assertEqual(normalize_target_title("Document.txt"), "Document")
        self.assertEqual(normalize_target_title("Document.TXT"), "Document")
        self.assertEqual(normalize_target_title("Document.pdf"), "Document.pdf")
        self.assertEqual(normalize_target_title("Document.docx"), "Document.docx")

        # Test within wikilinks
        m = parse_wikilinks("Check [[Notes.MD#Summary|My Notes]] and [[Spec.TXT]]")
        self.assertEqual(len(m), 2)
        self.assertEqual(m[0].target_title, "Notes")
        self.assertEqual(m[0].anchor, "Summary")
        self.assertEqual(m[0].alias, "My Notes")
        self.assertEqual(m[1].target_title, "Spec")

    def test_03_whitespace_handling(self):
        """Stress test leading, trailing, and internal whitespace variants."""
        text = "Check [[   Doc Alpha   ]], [[  Doc Beta  |  Label Beta  ]], and [[ Doc Gamma # Sec 1 | Label Gamma ]]"
        matches = parse_wikilinks(text)
        self.assertEqual(len(matches), 3)

        self.assertEqual(matches[0].target_title, "Doc Alpha")
        self.assertEqual(matches[1].target_title, "Doc Beta")
        self.assertEqual(matches[1].alias, "Label Beta")
        self.assertEqual(matches[2].target_title, "Doc Gamma")
        self.assertEqual(matches[2].anchor, "Sec 1")
        self.assertEqual(matches[2].alias, "Label Gamma")

    def test_04_special_characters_and_punctuation(self):
        """Stress test titles with punctuation, symbols, and numbers."""
        text = "See [[Doc_v1.0-alpha]], [[Project & Co (2026)]], and [[Deep/Nested/File.md]]"
        matches = parse_wikilinks(text)
        self.assertEqual(len(matches), 3)

        self.assertEqual(matches[0].target_title, "Doc_v1.0-alpha")
        self.assertEqual(matches[0].slug, "doc_v10_alpha")

        self.assertEqual(matches[1].target_title, "Project & Co (2026)")
        self.assertEqual(matches[1].slug, "project_co_2026")

        self.assertEqual(matches[2].target_title, "Deep/Nested/File")
        self.assertEqual(matches[2].slug, "deepnestedfile")

    def test_05_multiple_links_per_line_and_repetitions(self):
        """Test multiple links on a single line and repeated links to same target."""
        text = "First [[Doc A]], second [[Doc B]], third [[Doc A|Alias A]], fourth [[Doc A#Anchor]]."
        matches = parse_wikilinks(text)
        self.assertEqual(len(matches), 4)

        targets = [m.target_title for m in matches]
        self.assertEqual(targets, ["Doc A", "Doc B", "Doc A", "Doc A"])

        # extract_target_titles should deduplicate while preserving order
        unique_titles = extract_target_titles(text)
        self.assertEqual(unique_titles, ["Doc A", "Doc B"])

    def test_06_malformed_and_empty_brackets(self):
        """Test empty, whitespace-only, anchor-only, or alias-only brackets."""
        text = "Empty [[]], spaces [[   ]], anchor-only [[#heading]], alias-only [[|just alias]]"
        matches = parse_wikilinks(text)
        self.assertEqual(len(matches), 0)


class TestGraphEdgesAndWeightCalculations(unittest.TestCase):
    """Integration stress test for graph endpoint edge generation and weight calculations."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_challenger_m3_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_graph.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()
        self.client = TestClient(main.app)

    def tearDown(self):
        know.reset_db_connections()
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_07_directed_wikilink_edges_and_weights(self):
        """Verify directed wikilink_to edge directionality, weight aggregation, self-link filtering, and missing link handling."""
        with sqlite3.connect(know.DB_FILE) as conn:
            cursor = conn.cursor()
            # File 1: references File 2 THREE times, File 3 ONCE, references ITSELF once, and references missing File 99
            f1_content = (
                "Referencing [[File Two.md]], also [[File Two|2nd link]], and [[File Two#sec3|3rd link]]. "
                "Also see [[File Three]]. "
                "Self link [[File One]]. "
                "Missing link [[NonExistentDoc]]."
            )
            cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (1, 'c:/file1.md', 'File One.md', ?)", (f1_content,))
            cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (2, 'c:/file2.md', 'File Two.md', 'Content Two')")
            cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (3, 'c:/file3.md', 'File Three.md', 'Content Three')")
            conn.commit()

        response = self.client.get("/api/graph?limit=10&include_wikilinks=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        wikilink_edges = [e for e in data["edges"] if e["type"] == "wikilink_to"]
        
        # Should have exactly 2 edges: file_1 -> file_2 (weight 3) and file_1 -> file_3 (weight 1)
        self.assertEqual(len(wikilink_edges), 2)

        edge_map = {(e["source"], e["target"]): e["weight"] for e in wikilink_edges}
        
        # Verify directionality & weight
        self.assertIn(("file_1", "file_2"), edge_map)
        self.assertEqual(edge_map[("file_1", "file_2")], 3)

        self.assertIn(("file_1", "file_3"), edge_map)
        self.assertEqual(edge_map[("file_1", "file_3")], 1)

        # Verify no self-loop edge (file_1 -> file_1)
        self.assertNotIn(("file_1", "file_1"), edge_map)

        # Verify no missing node edge (file_1 -> file_99)
        for e in wikilink_edges:
            self.assertNotEqual(e["target"], "file_99")

    def test_08_case_insensitive_and_slug_title_matching(self):
        """Verify wikilinks resolve targets across case, extensions, and slug variations."""
        with sqlite3.connect(know.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (1, 'c:/src.md', 'Source.md', 'See [[target document]], [[TARGET_DOCUMENT.MD]], and [[target-document]]')")
            cursor.execute("INSERT INTO files (id, filepath, filename, content) VALUES (2, 'c:/tgt.md', 'Target Document.md', 'Target content')")
            conn.commit()

        response = self.client.get("/api/graph?include_wikilinks=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        wikilink_edges = [e for e in data["edges"] if e["type"] == "wikilink_to"]
        self.assertEqual(len(wikilink_edges), 1)

        edge = wikilink_edges[0]
        self.assertEqual(edge["source"], "file_1")
        self.assertEqual(edge["target"], "file_2")
        # All 3 wikilinks point to Target Document.md, so weight = 3
        self.assertEqual(edge["weight"], 3)

    def test_09_undirected_shared_tag_cluster_weight(self):
        """Verify shared_tag_cluster edges sum shared tags correctly and order IDs canonically (d1 < d2)."""
        with sqlite3.connect(know.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (10, 'c:/d10.md', 'd10.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (5, 'c:/d5.md', 'd5.md')")
            cursor.execute("INSERT INTO files (id, filepath, filename) VALUES (20, 'c:/d20.md', 'd20.md')")

            # d5 and d10 share 3 tags ("alpha", "beta", "gamma")
            # d10 and d20 share 1 tag ("gamma")
            # d5 and d20 share 1 tag ("gamma")
            tags = [
                (10, "alpha"), (10, "beta"), (10, "gamma"),
                (5, "alpha"), (5, "beta"), (5, "gamma"),
                (20, "gamma")
            ]
            cursor.executemany("INSERT INTO tags (file_id, tag) VALUES (?, ?)", tags)
            conn.commit()

        response = self.client.get("/api/graph?include_clusters=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        cluster_edges = [e for e in data["edges"] if e["type"] == "shared_tag_cluster"]
        edge_weights = {(e["source"], e["target"]): e["weight"] for e in cluster_edges}

        # Source ID should always be min(id), target should be max(id) -> file_5, file_10
        self.assertEqual(edge_weights.get(("file_5", "file_10")), 3)
        self.assertEqual(edge_weights.get(("file_5", "file_20")), 1)
        self.assertEqual(edge_weights.get(("file_10", "file_20")), 1)

        # Confirm no reverse edges (file_10 -> file_5)
        self.assertNotIn(("file_10", "file_5"), edge_weights)

    def test_10_tag_cluster_size_capping_behavior(self):
        """Verify super-common tags (> 100 documents) do not generate quadratic cluster blowup."""
        with sqlite3.connect(know.DB_FILE) as conn:
            cursor = conn.cursor()
            # Create 105 files
            file_rows = [(i, f"c:/doc_{i}.md", f"doc_{i}.md") for i in range(1, 106)]
            cursor.executemany("INSERT INTO files (id, filepath, filename) VALUES (?, ?, ?)", file_rows)

            # Assign 'popular_tag' to all 105 files (> 100 cap)
            tag_rows_pop = [(i, "popular_tag") for i in range(1, 106)]
            cursor.executemany("INSERT INTO tags (file_id, tag) VALUES (?, ?)", tag_rows_pop)

            # Assign 'rare_tag' to doc 1 and doc 2 (size 2 <= 100 cap)
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (1, 'rare_tag')")
            cursor.execute("INSERT INTO tags (file_id, tag) VALUES (2, 'rare_tag')")
            conn.commit()

        response = self.client.get("/api/graph?limit=200&include_clusters=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        cluster_edges = [e for e in data["edges"] if e["type"] == "shared_tag_cluster"]
        
        # Only rare_tag should generate a cluster edge (file_1 <-> file_2 with weight 1)
        # popular_tag (105 docs) should be capped and skipped
        self.assertEqual(len(cluster_edges), 1)
        self.assertEqual(cluster_edges[0]["source"], "file_1")
        self.assertEqual(cluster_edges[0]["target"], "file_2")
        self.assertEqual(cluster_edges[0]["weight"], 1)


if __name__ == "__main__":
    unittest.main()
