"""
Comprehensive Unit Test Suite for Dense Propositional Decomposition & Breadcrumb Scoping (Milestone M2 / Feature F5).
Tests atomic extraction, breadcrumb formatting, markdown heading stacks, bullet lists, numbered clauses,
semicolon handling, token estimation, and parent context expansion via database integration.
"""

import pytest
import sqlite3
from src.domain.dense_propositions import (
    decompose_into_propositions,
    expand_propositions_to_parent_context,
    format_breadcrumb_scope,
    _split_into_atomic_clauses
)


import unittest


class TestDensePropositions(unittest.TestCase):
    def test_format_breadcrumb_scope(self):
        assert format_breadcrumb_scope("DocA", ["Sec1", "Sub2"]) == "DocA > Sec1 > Sub2"
        assert format_breadcrumb_scope("DocA", []) == "DocA"
        assert format_breadcrumb_scope("", ["Sec1", "Sub2"]) == "Sec1 > Sub2"
        assert format_breadcrumb_scope("", None) == ""
        assert format_breadcrumb_scope("  DocA  ", ["  Sec1  "]) == "DocA > Sec1"


    def test_basic_proposition_decomposition(self):
        text = "The system uses SQLite for persistent storage. All reads use WAL mode for concurrency."
        props = decompose_into_propositions(text, document_title="Architecture.md", section_hierarchy=["Storage"])

        assert len(props) == 2
        assert props[0]["proposition_id"] == "Architecture.md#prop_0"
        assert props[1]["proposition_id"] == "Architecture.md#prop_1"
        assert props[0]["breadcrumb_scope"] == "Architecture.md > Storage"
        assert props[0]["statement"] == "The system uses SQLite for persistent storage."
        assert props[0]["contextual_statement"] == "[Architecture.md > Storage] The system uses SQLite for persistent storage."
        assert props[0]["char_length"] == len(props[0]["statement"])
        assert props[0]["token_estimate"] == max(1, len(props[0]["statement"]) // 4)
        assert props[0]["file_id"] is None


    def test_file_id_proposition_id_generation(self):
        text = "Valid proposition statement for file id test."
        props = decompose_into_propositions(text, document_title="DocA", file_id=42)

        assert len(props) == 1
        assert props[0]["file_id"] == 42
        assert props[0]["proposition_id"] == "42#prop_0"


    def test_markdown_heading_hierarchy_tracking(self):
        md_text = """
    # System Architecture
    The platform is built on Clean Architecture principles.

    ## Data Layer
    All persistent state resides in SQLite tables.
    WAL mode enables concurrent read operations without blocking writers.

    ### Optimization Sublayer
    Temporary tables reside strictly in MEMORY.

    ## Network Layer
    Optical fiber latency lower bounds enforce physical causality.
    """
        props = decompose_into_propositions(md_text, document_title="Engine_Spec.md")

        assert len(props) >= 5

        # Check breadcrumb evolution across headings
        p0 = props[0]
        assert p0["breadcrumb_scope"] == "Engine_Spec.md > System Architecture"
        assert "Clean Architecture" in p0["statement"]

        p1 = props[1]
        assert p1["breadcrumb_scope"] == "Engine_Spec.md > System Architecture > Data Layer"
        assert "SQLite tables" in p1["statement"]

        p2 = props[2]
        assert p2["breadcrumb_scope"] == "Engine_Spec.md > System Architecture > Data Layer"
        assert "WAL mode" in p2["statement"]

        p3 = props[3]
        assert p3["breadcrumb_scope"] == "Engine_Spec.md > System Architecture > Data Layer > Optimization Sublayer"
        assert "MEMORY" in p3["statement"]

        p4 = props[4]
        # Sibling heading reset: Network Layer should pop Data Layer & Optimization Sublayer
        assert p4["breadcrumb_scope"] == "Engine_Spec.md > System Architecture > Network Layer"
        assert "Optical fiber" in p4["statement"]


    def test_bullet_and_numbered_list_decomposition(self):
        list_text = """
    Key architectural invariants:
    - First invariant: Speed of light limits latency across optical medium.
    * Second invariant: USL concurrency contention alpha is bounded by 0.05.
    • Third invariant: Carnot thermodynamic efficiency cannot be exceeded.
    + Fourth invariant: Shannon channel capacity sets the communication ceiling.
    1. Primary consensus rule: Tier 1 statutory authorities override commentary.
    2. Secondary consensus rule: Superseded documents suffer staleness penalties.
    (1) Specific clause: Checkpoints execute every 1000 transactions.
    (a) Sub-clause: Thread local connections close during reset.
    """
        props = decompose_into_propositions(list_text, document_title="Invariants.md")

        statements = [p["statement"] for p in props]
        assert any("Speed of light limits latency" in s for s in statements)
        assert any("USL concurrency contention" in s for s in statements)
        assert any("Carnot thermodynamic efficiency" in s for s in statements)
        assert any("Shannon channel capacity" in s for s in statements)
        assert any("Tier 1 statutory authorities" in s for s in statements)
        assert any("Superseded documents" in s for s in statements)
        assert any("Checkpoints execute every 1000" in s for s in statements)
        assert any("Thread local connections" in s for s in statements)

        # Bullet markers should not be present at start of statements
        for p in props:
            stmt = p["statement"]
            assert not stmt.startswith("- ")
            assert not stmt.startswith("* ")
            assert not stmt.startswith("• ")
            assert not stmt.startswith("+ ")
            assert not stmt.startswith("1. ")
            assert not stmt.startswith("2. ")


    def test_semicolon_compound_sentence_splitting(self):
        text = "The primary cache stores 1024 items in memory; background threads write evictions to disk."
        props = decompose_into_propositions(text, document_title="CacheSpec.md")

        assert len(props) == 2
        assert "The primary cache stores 1024 items in memory" in props[0]["statement"]
        assert "background threads write evictions to disk." in props[1]["statement"]


    def test_subminimal_fragment_filtration(self):
        text = "Short. Hi. No. Ok. This statement is sufficiently long and informative to pass filtration. Done. End."
        props = decompose_into_propositions(text, document_title="FilterTest.md")

        assert len(props) == 1
        assert "This statement is sufficiently long" in props[0]["statement"]


    def test_abbreviation_and_decimal_protection(self):
        text = "The system version is v3.2 and costs $10.50 per node, e.g. AWS c5.large, i.e. 4 vCPUs."
        props = decompose_into_propositions(text, document_title="CostSpec.md")

        assert len(props) == 1
        assert "e.g." in props[0]["statement"]
        assert "i.e." in props[0]["statement"]
        assert "10.50" in props[0]["statement"]
        assert "v3.2" in props[0]["statement"]


    def test_interrobang_and_ellipsis_handling(self):
        text = "Does the system maintain consistency across network partitions?! Yes, but with latency costs... All nodes verify consensus."
        props = decompose_into_propositions(text, document_title="ConsensusSpec.md")

        assert len(props) >= 2
        statements_str = " ".join(p["statement"] for p in props)
        assert "consistency across network partitions?!" in statements_str
        assert "latency costs..." in statements_str or "latency costs" in statements_str


    def test_empty_and_invalid_inputs(self):
        assert decompose_into_propositions("") == []
        assert decompose_into_propositions("   \n\t  ") == []
        assert decompose_into_propositions(None) == []  # type: ignore


    def test_expand_propositions_to_parent_context_with_db(self):
        # Create in-memory test database with files table
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                filepath TEXT,
                content TEXT
            )
        """)
        full_doc = (
            "SECTION 1: INTRODUCTION\n"
            "This is the opening preamble of the system specification.\n\n"
            "SECTION 2: STORAGE ENGINE\n"
            "The database layer operates under SQLite WAL mode with 30s timeouts. "
            "All transactions are strictly serialized to prevent race conditions. "
            "Periodic automated checkpoints maintain bounded log sizes.\n\n"
            "SECTION 3: SUMMARY\n"
            "Conclusion and closing remarks."
        )
        cursor.execute("INSERT INTO files (id, filename, filepath, content) VALUES (101, 'StorageEngine.md', '/docs/StorageEngine.md', ?)", (full_doc,))
        conn.commit()

        props = decompose_into_propositions(
            "All transactions are strictly serialized to prevent race conditions.",
            document_title="StorageEngine.md",
            file_id=101
        )
        assert len(props) == 1

        expanded = expand_propositions_to_parent_context(props, max_parent_chars=200, db_connection=conn)
        assert len(expanded) == 1
        exp_prop = expanded[0]
        assert exp_prop["has_parent_context"] is True
        assert exp_prop["parent_context_chars"] > 0
        assert "strictly serialized" in exp_prop["parent_context"]
        assert "SQLite WAL mode" in exp_prop["parent_context"]


    def test_expand_propositions_to_parent_context_fallback(self):
        # When no DB connection and no indexed file, fallback to contextual_statement
        props = decompose_into_propositions("Sample statement for fallback test.", document_title="MissingDoc.md")
        expanded = expand_propositions_to_parent_context(props, max_parent_chars=500, db_connection=None)

        assert len(expanded) == 1
        assert expanded[0]["has_parent_context"] is True
        assert "Sample statement for fallback test." in expanded[0]["parent_context"]
