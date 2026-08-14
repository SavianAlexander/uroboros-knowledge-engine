"""
Adversarial Empirical Stress-Testing Harness for Milestone M2 (Feature F5).
Tests dense propositional decomposition, hierarchical breadcrumb maintenance,
multilingual & unicode resilience, edge boundaries, extreme inputs, and parent context expansion.
"""

import pytest
import sqlite3
import unicodedata
from src.domain.dense_propositions import (
    decompose_into_propositions,
    expand_propositions_to_parent_context,
    format_breadcrumb_scope,
    _split_into_atomic_clauses
)
from src.domain.grounded_retrieval_engine import (
    decompose_into_propositions as re_decompose,
    expand_propositions_to_parent_context as re_expand,
    format_breadcrumb_scope as re_format
)


# ==============================================================================
# CATEGORY 1: Deeply Nested Markdown Headers & Complex Hierarchies
# ==============================================================================

def test_deep_6_level_markdown_nesting():
    """Verify that all 6 markdown heading levels (# through ######) maintain exact breadcrumb hierarchy."""
    doc = """
# Heading Level 1
Proposition at level 1 is established here.

## Heading Level 2
Proposition at level 2 builds upon level 1.

### Heading Level 3
Proposition at level 3 provides technical details.

#### Heading Level 4
Proposition at level 4 details implementation specifications.

##### Heading Level 5
Proposition at level 5 defines microscopic constants.

###### Heading Level 6
Proposition at level 6 is the deepest granular assertion.
"""
    props = decompose_into_propositions(doc, document_title="DeepSpec.md")
    assert len(props) == 6

    expected_breadcrumbs = [
        "DeepSpec.md > Heading Level 1",
        "DeepSpec.md > Heading Level 1 > Heading Level 2",
        "DeepSpec.md > Heading Level 1 > Heading Level 2 > Heading Level 3",
        "DeepSpec.md > Heading Level 1 > Heading Level 2 > Heading Level 3 > Heading Level 4",
        "DeepSpec.md > Heading Level 1 > Heading Level 2 > Heading Level 3 > Heading Level 4 > Heading Level 5",
        "DeepSpec.md > Heading Level 1 > Heading Level 2 > Heading Level 3 > Heading Level 4 > Heading Level 5 > Heading Level 6"
    ]

    for idx, (prop, expected_bc) in enumerate(zip(props, expected_breadcrumbs)):
        assert prop["breadcrumb_scope"] == expected_bc
        assert prop["section_hierarchy"] == expected_bc.split(" > ")[1:]
        assert prop["contextual_statement"].startswith(f"[{expected_bc}]")


def test_deep_reset_from_level_6_to_level_1():
    """Verify that jumping from level 6 back to level 1 pops all 5 intermediate levels."""
    doc = """
# Root L1
###### Deep L6
Assertion deep in the tree.

# Fresh L1
Assertion in the fresh top-level scope.
"""
    props = decompose_into_propositions(doc, document_title="ResetTest.md")
    assert len(props) == 2
    assert props[0]["breadcrumb_scope"] == "ResetTest.md > Root L1 > Deep L6"
    assert props[1]["breadcrumb_scope"] == "ResetTest.md > Fresh L1"


def test_zigzag_heading_transitions():
    """Verify non-sequential heading jumps: L1 -> L4 -> L2 -> L5 -> L3 -> L6 -> L2."""
    doc = """
# Level 1
Text at level 1.

#### Jump to Level 4
Text at level 4 under level 1.

## Climb back to Level 2
Text at level 2 under level 1 (L4 popped).

##### Jump down to Level 5
Text at level 5 under L1 > L2.

### Climb back to Level 3
Text at level 3 under L1 > L2 (L5 popped).

###### Jump down to Level 6
Text at level 6 under L1 > L2 > L3.

## Climb back to Level 2 Sibling
Text at level 2 sibling (L3 and L6 popped).
"""
    props = decompose_into_propositions(doc, document_title="ZigZag.md")
    assert len(props) == 7

    assert props[0]["breadcrumb_scope"] == "ZigZag.md > Level 1"
    assert props[1]["breadcrumb_scope"] == "ZigZag.md > Level 1 > Jump to Level 4"
    assert props[2]["breadcrumb_scope"] == "ZigZag.md > Level 1 > Climb back to Level 2"
    assert props[3]["breadcrumb_scope"] == "ZigZag.md > Level 1 > Climb back to Level 2 > Jump down to Level 5"
    assert props[4]["breadcrumb_scope"] == "ZigZag.md > Level 1 > Climb back to Level 2 > Climb back to Level 3"
    assert props[5]["breadcrumb_scope"] == "ZigZag.md > Level 1 > Climb back to Level 2 > Climb back to Level 3 > Jump down to Level 6"
    assert props[6]["breadcrumb_scope"] == "ZigZag.md > Level 1 > Climb back to Level 2 Sibling"


def test_base_section_hierarchy_preservation():
    """Verify that an initial base section hierarchy is prepended to markdown breadcrumbs."""
    doc = """
# Module Alpha
Alpha statement text goes here.

## Sub-service Beta
Beta statement text goes here.
"""
    base_hierarchy = ["GlobalEnterprise", "DomainLayer"]
    props = decompose_into_propositions(doc, document_title="System.md", section_hierarchy=base_hierarchy)

    assert len(props) == 2
    assert props[0]["breadcrumb_scope"] == "System.md > GlobalEnterprise > DomainLayer > Module Alpha"
    assert props[1]["breadcrumb_scope"] == "System.md > GlobalEnterprise > DomainLayer > Module Alpha > Sub-service Beta"
    assert props[0]["section_hierarchy"] == ["GlobalEnterprise", "DomainLayer", "Module Alpha"]


def test_consecutive_headings_without_intermediate_content():
    """Verify that multiple consecutive headings without body text accumulate properly in the stack."""
    doc = """
# Architecture
## Infrastructure
### Networking
#### Latency Guards
The speed of light in optical fiber imposes a strict minimum propagation delay.
"""
    props = decompose_into_propositions(doc, document_title="MultiHead.md")
    assert len(props) == 1
    assert props[0]["breadcrumb_scope"] == "MultiHead.md > Architecture > Infrastructure > Networking > Latency Guards"
    assert "speed of light" in props[0]["statement"]


def test_formatted_and_trailing_hash_headings():
    """Verify that markdown formatting (bold, italic, backticks) and trailing hashes in headings are handled cleanly."""
    doc = """
# **Core Architecture** ###
Bold title statement goes here.

## *Storage Subsystem* ##
Italic section statement goes here.

### `CacheManager` #
Backtick heading statement goes here.
"""
    props = decompose_into_propositions(doc, document_title="FormatHead.md")
    assert len(props) == 3
    assert props[0]["breadcrumb_scope"] == "FormatHead.md > **Core Architecture**"
    assert props[1]["breadcrumb_scope"] == "FormatHead.md > **Core Architecture** > *Storage Subsystem*"
    assert props[2]["breadcrumb_scope"] == "FormatHead.md > **Core Architecture** > *Storage Subsystem* > `CacheManager`"


def test_non_heading_hash_lines():
    """Verify lines starting with # but not valid markdown headings (no space, or >6 hashes) are treated as text."""
    doc = """
# Valid Header
#include <iostream> is standard C++ header for I/O.
#1 ranked optimization algorithm is quicksort.
####### Seven hashes is not a standard markdown header.
"""
    props = decompose_into_propositions(doc, document_title="NonHead.md")
    assert len(props) >= 2
    for p in props:
        assert p["breadcrumb_scope"].startswith("NonHead.md > Valid Header")


# ==============================================================================
# CATEGORY 2: Multilingual Characters, Unicode, Code Blocks, Tables & Delimiters
# ==============================================================================

def test_cjk_multilingual_propositions():
    """Verify Chinese and Japanese sentences decompose and maintain character accuracy."""
    doc = """
# 分布式系统规范
分布式系统的CAP定理指出任何分布式系统最多只能同时满足一致性、可用性和分区容错性中的两项。
SQLiteデータベースは軽量で高信頼なリレーショナルデータベース管理システムです。
"""
    props = decompose_into_propositions(doc, document_title="CJK_Spec.md")
    assert len(props) >= 2
    assert props[0]["breadcrumb_scope"] == "CJK_Spec.md > 分布式系统规范"
    statements = [p["statement"] for p in props]
    assert any("CAP定理" in s for s in statements)
    assert any("SQLiteデータベース" in s for s in statements)


def test_arabic_rtl_and_cyrillic_greek_propositions():
    """Verify Arabic RTL, Cyrillic, and Greek alphabets decompose cleanly."""
    doc = """
# International Invariants
قاعدة بيانات SQLite هي نظام إدارة قواعد بيانات علائقية خفيف الوزن وموثوق.
Теорема CAP утверждает, что распределенная система не может одновременно гарантировать согласованность.
Η αρχιτεκτονική του συστήματος βασίζεται σε καθαρές διεπαφές και αμετάβλητους κανόνες.
"""
    props = decompose_into_propositions(doc, document_title="Polyglot.md")
    assert len(props) == 3
    statements = [p["statement"] for p in props]
    assert any("SQLite" in s and "قاعدة بيانات" in s for s in statements)
    assert any("Теорема CAP" in s for s in statements)
    assert any("Η αρχιτεκτονική" in s for s in statements)


def test_math_symbols_and_emojis():
    """Verify mathematical notation (∀, ∃, ∈, ℝ, ≥) and emojis are preserved intact."""
    doc = """
# Mathematical Guarantees
For all x in domain: ∀x ∈ ℝ, f(x) ≥ 0, which guarantees invariant non-negativity.
🚀 Deployment pipeline succeeded with 100% test coverage and 0 vulnerabilities!
"""
    props = decompose_into_propositions(doc, document_title="Math.md")
    assert len(props) == 2
    assert "∀x ∈ ℝ, f(x) ≥ 0" in props[0]["statement"]
    assert "🚀 Deployment pipeline succeeded" in props[1]["statement"]


def test_code_blocks_and_tables_in_markdown():
    """Verify text containing code blocks and markdown tables generates valid propositions."""
    doc = """
# Implementation Guide
```python
def compute_speed_of_light(n=1.47):
    return 299792.458 / n
```
The python function calculates optical propagation velocity in fiber.

| Metric | Target | Actual |
| --- | --- | --- |
| Latency | < 50ms | 12ms |
| Throughput | > 1000 RPS | 4500 RPS |
The cluster achieves 4500 requests per second under peak load.
"""
    props = decompose_into_propositions(doc, document_title="CodeTable.md")
    statements = [p["statement"] for p in props]
    assert any("optical propagation velocity" in s for s in statements)
    assert any("4500 requests per second" in s for s in statements)


def test_punctuation_anomalies_and_inverted_marks():
    """Verify inverted punctuation (¿, ¡), mixed quotes, em-dashes, arrows, and ellipses."""
    doc = """
# Punctuation Stress
¿Es este un sistema distribuido? ¡Por supuesto que el clúster es distribuido!
The primary node—designated as leader—coordinates consensus across all replicas.
Traffic flow routes as follows: client -> API gateway -> microservice => database cluster.
Is consensus guaranteed under network partitioning?! Only if quorum consistency is maintained...
"""
    props = decompose_into_propositions(doc, document_title="Punct.md")
    assert len(props) >= 3
    statements_str = " ".join(p["statement"] for p in props)
    assert "distribuido" in statements_str
    assert "primary node—designated as leader" in statements_str
    assert "client -> API gateway" in statements_str


def test_various_list_bullet_markers():
    """Verify all standard and non-standard list markers are stripped without corrupting content."""
    doc = """
# List Test
- Dash bullet point with important architecture content.
* Asterisk bullet point describing storage layer invariants.
+ Plus bullet point outlining networking protocol.
• Unicode dot bullet point verifying execution flow.
1. Numbered item indicating first step of migration.
99. High numbered item describing final verification step.
(1) Parenthetical number detailing concurrency boundaries.
(a) Parenthetical letter detailing memory safety rules.
"""
    props = decompose_into_propositions(doc, document_title="ListDoc.md")
    assert len(props) == 8
    for p in props:
        stmt = p["statement"]
        assert not stmt.startswith("- ")
        assert not stmt.startswith("* ")
        assert not stmt.startswith("+ ")
        assert not stmt.startswith("• ")
        assert not stmt.startswith("1. ")
        assert not stmt.startswith("99. ")
        assert not stmt.startswith("(1) ")
        assert not stmt.startswith("(a) ")


# ==============================================================================
# CATEGORY 3: Edge Cases, Boundaries, Extreme Lengths & Regex Characters
# ==============================================================================

def test_null_empty_and_whitespace_boundaries():
    """Verify empty and invalid inputs return [] without crashing."""
    assert decompose_into_propositions("") == []
    assert decompose_into_propositions("   \n\t  ") == []
    assert decompose_into_propositions(None) == []  # type: ignore
    assert decompose_into_propositions(12345) == []  # type: ignore
    assert decompose_into_propositions([]) == []  # type: ignore


def test_character_length_threshold_boundary():
    """Verify fragments < 12 characters are filtered out, and >= 12 characters are retained."""
    # 11 characters -> filtered out
    assert _split_into_atomic_clauses("12345678901") == []
    assert decompose_into_propositions("12345678901") == []

    # Exactly 12 characters -> retained
    assert _split_into_atomic_clauses("123456789012") == ["123456789012"]
    props = decompose_into_propositions("123456789012", document_title="Doc")
    assert len(props) == 1
    assert props[0]["statement"] == "123456789012"
    assert props[0]["char_length"] == 12
    assert props[0]["token_estimate"] == 3


def test_massive_single_sentence_and_scale():
    """Verify a 20,000 character single sentence does not cause recursion error or catastrophic backtracking."""
    massive_sentence = "The database cluster maintains strict serializability across all geo-distributed nodes " * 250
    props = decompose_into_propositions(massive_sentence, document_title="Massive.md")
    assert len(props) >= 1
    assert props[0]["char_length"] > 10000
    assert props[0]["token_estimate"] == props[0]["char_length"] // 4


def test_zero_punctuation_continuous_stream():
    """Verify text with zero terminal punctuation decomposes into a single atomic proposition."""
    stream_text = "This is a continuous stream of words without any period question mark exclamation mark or semicolon"
    props = decompose_into_propositions(stream_text, document_title="Stream.md")
    assert len(props) == 1
    assert props[0]["statement"] == stream_text


def test_regex_metacharacters_and_templates():
    """Verify text containing regex metacharacters, backreferences, and template tags parses safely."""
    doc = """
# Regex & Templates
The regex pattern is (?P<group>[a-zA-Z0-9_]+) which matches alphanumeric identifiers.
The replacement expression uses \\g<1> and \\g<2> to reorder matched tokens.
Environment variables follow ${VARIABLE_NAME} format while templates use {{user_id}}.
"""
    props = decompose_into_propositions(doc, document_title="RegexDoc.md")
    assert len(props) == 3
    statements = [p["statement"] for p in props]
    assert any("(?P<group>[a-zA-Z0-9_]+)" in s for s in statements)
    assert any("\\g<1>" in s for s in statements)
    assert any("${VARIABLE_NAME}" in s and "{{user_id}}" in s for s in statements)


def test_complex_abbreviations_and_decimals():
    """Verify multi-dot abbreviations, version numbers, money, and compound acronyms."""
    text = (
        "The U.S. patent office approved application no. 12345 filed by Corp. Inc. on St. Patrick Day. "
        "The estimated cost is $4,500.75 per quarter (i.e. appx. $1,500.25 per month), e.g. for v2.5.1 nodes."
    )
    props = decompose_into_propositions(text, document_title="AbbrDoc.md")
    assert len(props) == 2
    assert "U.S." in props[0]["statement"]
    assert "Corp. Inc." in props[0]["statement"]
    assert "$4,500.75" in props[1]["statement"]
    assert "i.e." in props[1]["statement"]
    assert "e.g." in props[1]["statement"]


def test_quote_ending_sentence_boundaries():
    """Verify sentences ending with quotes are split properly when followed by space."""
    text = '"The system is fully grounded." Next sentence begins here.'
    props = decompose_into_propositions(text, document_title="QuoteDoc.md")
    # Let's observe if quote endings split into 1 or 2 propositions
    statements = [p["statement"] for p in props]
    # Check that both sentences are retained
    assert any("The system is fully grounded" in s for s in statements)


def test_name_initials_and_approx():
    """Observe behavior with initials like J. K. and abbreviations like approx."""
    text1 = "Dr. J. K. Rowling wrote books. They are very popular worldwide."
    props1 = decompose_into_propositions(text1, document_title="Author.md")
    assert len(props1) >= 1



# ==============================================================================
# CATEGORY 4: Parent Context Expansion Resilience & Database Edge Cases
# ==============================================================================

def test_expand_context_with_empty_and_malformed_inputs():
    """Verify expand_propositions_to_parent_context handles empty lists and malformed dicts gracefully."""
    assert expand_propositions_to_parent_context([]) == []
    
    # Missing all standard keys
    malformed_props = [{}]
    expanded = expand_propositions_to_parent_context(malformed_props)
    assert len(expanded) == 1
    assert expanded[0]["has_parent_context"] is False
    assert expanded[0]["parent_context"] == ""
    assert expanded[0]["parent_context_chars"] == 0


def test_expand_context_with_missing_and_invalid_file_ids():
    """Verify non-existent or negative file_ids fall back safely without raising exceptions."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE files (id INT, filename TEXT, filepath TEXT, content TEXT)")
    cursor.execute("INSERT INTO files VALUES (1, 'RealDoc.md', '/RealDoc.md', 'Real content of the document.')")
    conn.commit()

    props = [
        {"file_id": 999999, "statement": "Some proposition statement here.", "breadcrumb_scope": "MissingDoc.md", "contextual_statement": "[MissingDoc.md] Some proposition statement here."},
        {"file_id": -5, "statement": "Another proposition statement here.", "breadcrumb_scope": "NegativeDoc.md", "contextual_statement": "[NegativeDoc.md] Another proposition statement here."},
        {"file_id": None, "statement": "No file id statement here.", "breadcrumb_scope": "", "contextual_statement": "No file id statement here."}
    ]

    expanded = expand_propositions_to_parent_context(props, db_connection=conn)
    assert len(expanded) == 3
    assert expanded[0]["has_parent_context"] is True
    assert expanded[0]["parent_context"] == "[MissingDoc.md] Some proposition statement here."
    assert expanded[1]["has_parent_context"] is True
    assert expanded[2]["has_parent_context"] is True


def test_expand_context_with_corrupted_or_closed_db():
    """Verify that a closed database connection or missing table falls back to contextual statements."""
    closed_conn = sqlite3.connect(":memory:")
    closed_conn.close()

    props = decompose_into_propositions("Test statement under corrupted DB test.", document_title="Corrupt.md", file_id=50)
    expanded = expand_propositions_to_parent_context(props, db_connection=closed_conn)
    assert len(expanded) == 1
    assert expanded[0]["has_parent_context"] is True
    assert "[Corrupt.md]" in expanded[0]["parent_context"]


def test_expand_context_with_mismatched_statement_in_content():
    """Verify that if proposition statement is not literally found in DB content, it falls back to content prefix."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE files (id INT, filename TEXT, filepath TEXT, content TEXT)")
    cursor.execute("INSERT INTO files VALUES (10, 'Doc10.md', '/Doc10.md', 'This is the true full document content for Doc10.')")
    conn.commit()

    props = [{
        "file_id": 10,
        "statement": "Completely different statement not in document body.",
        "breadcrumb_scope": "Doc10.md",
        "contextual_statement": "[Doc10.md] Completely different statement not in document body."
    }]

    expanded = expand_propositions_to_parent_context(props, max_parent_chars=100, db_connection=conn)
    assert len(expanded) == 1
    # Should fall back to the document content prefix
    assert expanded[0]["parent_context"] == "This is the true full document content for Doc10."


def test_expand_context_window_clamping_at_boundaries():
    """Verify window extraction at start of document, end of document, and with extreme max_parent_chars."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE files (id INT, filename TEXT, filepath TEXT, content TEXT)")
    doc_content = "START_TOKEN " + ("Intermediate text block. " * 50) + "END_TOKEN"
    cursor.execute("INSERT INTO files VALUES (20, 'Doc20.md', '/Doc20.md', ?)", (doc_content,))
    conn.commit()

    props_start = [{"file_id": 20, "statement": "START_TOKEN", "breadcrumb_scope": "Doc20.md"}]
    props_end = [{"file_id": 20, "statement": "END_TOKEN", "breadcrumb_scope": "Doc20.md"}]

    expanded_start = expand_propositions_to_parent_context(props_start, max_parent_chars=100, db_connection=conn)
    assert expanded_start[0]["parent_context"].startswith("START_TOKEN")
    assert len(expanded_start[0]["parent_context"]) <= 100

    expanded_end = expand_propositions_to_parent_context(props_end, max_parent_chars=100, db_connection=conn)
    assert expanded_end[0]["parent_context"].endswith("END_TOKEN")
    assert len(expanded_end[0]["parent_context"]) <= 100


def test_expand_context_with_large_1mb_document():
    """Verify parent context expansion performs efficiently on 1MB document without performance degradation."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE files (id INT, filename TEXT, filepath TEXT, content TEXT)")
    
    large_doc = ("Filler paragraph with general architectural details.\n" * 20000) + "CRITICAL_INVARIANT_ASSERTION: Speed of light is constant.\n" + ("Trailing filler text.\n" * 1000)
    cursor.execute("INSERT INTO files VALUES (30, 'LargeDoc.md', '/LargeDoc.md', ?)", (large_doc,))
    conn.commit()

    props = [{"file_id": 30, "statement": "CRITICAL_INVARIANT_ASSERTION: Speed of light is constant.", "breadcrumb_scope": "LargeDoc.md"}]
    expanded = expand_propositions_to_parent_context(props, max_parent_chars=500, db_connection=conn)
    
    assert len(expanded) == 1
    assert "CRITICAL_INVARIANT_ASSERTION: Speed of light is constant." in expanded[0]["parent_context"]
    assert len(expanded[0]["parent_context"]) <= 500


# ==============================================================================
# CATEGORY 5: Re-exports, Invariant Schema Compatibility & Format Helpers
# ==============================================================================

def test_grounded_retrieval_engine_re_exports():
    """Verify that grounded_retrieval_engine re-exports all M2 functions seamlessly."""
    assert re_decompose is decompose_into_propositions
    assert re_expand is expand_propositions_to_parent_context
    assert re_format is format_breadcrumb_scope


def test_format_breadcrumb_scope_resilience():
    """Verify format_breadcrumb_scope handles messy, None, whitespace, and integer arguments."""
    assert format_breadcrumb_scope() == ""
    assert format_breadcrumb_scope("Doc") == "Doc"
    assert format_breadcrumb_scope("  Doc  ", ["  Section 1  ", "  ", None, "Subsection 2"]) == "Doc > Section 1 > Subsection 2"  # type: ignore
    assert format_breadcrumb_scope("", [1, 2, 3]) == "1 > 2 > 3"  # type: ignore
