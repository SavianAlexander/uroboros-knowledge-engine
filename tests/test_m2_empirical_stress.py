"""
Comprehensive Empirical Stress and Adversarial Test Suite for Milestone 2.
Tests FTS5 query sanitization against SQLite FTS5 parser, Jaccard deduplication boundary conditions,
and WebSearchFetcher resilience under offline, DNS, timeout, and malformed payload conditions.
"""

import pytest
import sqlite3
import socket
import urllib.error
from unittest.mock import patch, MagicMock

from src.domain.rag_engine import (
    sanitize_fts_query,
    jaccard_deduplicate,
    _compute_word_jaccard,
    generate_hyde_expansion,
    rrf_rerank,
    extract_advanced_rag_context
)
from src.domain.web_search import WebSearchFetcher, fetch_web_context, strip_html_tags


# ============================================================================
# 1. FTS5 Query Sanitization Empirical Stress Tests
# ============================================================================

def test_fts5_sanitization_unbalanced_quotes(tmp_path):
    """Verify that unbalanced quotes are removed/handled without SQLite FTS syntax errors."""
    db_path = tmp_path / "test_fts5.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE VIRTUAL TABLE fts_files USING fts5(filepath, content);")
    conn.execute("INSERT INTO fts_files VALUES ('file1.txt', 'hello world python engine');")
    conn.commit()

    unbalanced_queries = [
        'hello "world',
        '"unbalanced quote',
        '""multiple"" "unbalanced ""',
        'quote"middle',
        '"""',
        '"',
    ]

    for q in unbalanced_queries:
        sanitized = sanitize_fts_query(q)
        assert '"' not in sanitized, f"Quote remained in sanitized query for '{q}': '{sanitized}'"
        try:
            cursor = conn.cursor()
            if sanitized:
                cursor.execute("SELECT * FROM fts_files WHERE fts_files MATCH ?", (sanitized,))
                cursor.fetchall()
        except sqlite3.OperationalError as e:
            pytest.fail(f"SQLite FTS5 syntax error for query '{q}' -> sanitized '{sanitized}': {e}")

    conn.close()


def test_fts5_sanitization_colons_and_specials(tmp_path):
    """Verify colons, column specs, and special symbols are safe for SQLite FTS5 MATCH."""
    db_path = tmp_path / "test_fts5.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE VIRTUAL TABLE fts_files USING fts5(filepath, content);")
    conn.execute("INSERT INTO fts_files VALUES ('file1.txt', 'title python search query content');")
    conn.commit()

    colon_and_special_queries = [
        "title:python",
        ":python",
        "content:",
        ":::colons:::",
        "nonexistent_column:term",
        "foo^2 +bar",
        "{foo bar}",
        "(parentheses OR test)",
        "slash/backslash\\semicolon;tilde~",
        "<tag> <= >= =",
        "comment--line",
        "star*",
        "***stars***",
        "\x00null\x1fctrl",
    ]

    for q in colon_and_special_queries:
        sanitized = sanitize_fts_query(q)
        try:
            cursor = conn.cursor()
            if sanitized:
                cursor.execute("SELECT * FROM fts_files WHERE fts_files MATCH ?", (sanitized,))
                cursor.fetchall()
        except sqlite3.OperationalError as e:
            pytest.fail(f"SQLite FTS5 syntax error for query '{q}' -> sanitized '{sanitized}': {e}")

    conn.close()


def test_fts5_sanitization_boolean_operators(tmp_path):
    """Verify boolean operator keywords (AND, OR, NOT, NEAR) are sanitized."""
    db_path = tmp_path / "test_fts5.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE VIRTUAL TABLE fts_files USING fts5(filepath, content);")
    conn.execute("INSERT INTO fts_files VALUES ('file1.txt', 'alpha beta gamma delta');")
    conn.commit()

    operator_queries = [
        "AND",
        "OR",
        "NOT",
        "NEAR",
        "NEAR/5",
        "alpha AND OR beta",
        "AND AND AND",
        "NOT NOT NOT",
        "alpha OR OR OR beta",
        "alpha NEAR beta",
        "alpha NEAR/3 beta",
        "alpha AND NOT beta",
        "and or not near",
    ]

    for q in operator_queries:
        sanitized = sanitize_fts_query(q)
        for word in sanitized.split():
            assert word.lower() not in ("and", "or", "not", "near"), f"Operator '{word}' found in sanitized query '{sanitized}' for input '{q}'"

        try:
            cursor = conn.cursor()
            if sanitized:
                cursor.execute("SELECT * FROM fts_files WHERE fts_files MATCH ?", (sanitized,))
                cursor.fetchall()
        except sqlite3.OperationalError as e:
            pytest.fail(f"SQLite FTS5 syntax error for query '{q}' -> sanitized '{sanitized}': {e}")

    conn.close()


def test_fts5_sanitization_hyphen_minus_adversarial(tmp_path):
    """
    Adversarial test for hyphen / minus character in queries causing FTS5 column/minus parse errors.
    Empirically demonstrates whether sanitize_fts_query handles hyphens safely.
    """
    db_path = tmp_path / "test_fts5.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE VIRTUAL TABLE fts_files USING fts5(filepath, content);")
    conn.execute("INSERT INTO fts_files VALUES ('file1.txt', 'foo-bar test-case alpha-beta');")
    conn.commit()

    hyphen_queries = [
        "foo-bar",
        "-bar",
        "foo - bar",
        "foo -",
        "---",
        "c++",
        "web-search-engine",
    ]

    syntax_errors = []
    for q in hyphen_queries:
        sanitized = sanitize_fts_query(q)
        try:
            cursor = conn.cursor()
            if sanitized:
                cursor.execute("SELECT * FROM fts_files WHERE fts_files MATCH ?", (sanitized,))
                cursor.fetchall()
        except sqlite3.OperationalError as e:
            syntax_errors.append((q, sanitized, str(e)))

    conn.close()
    
    # Document the finding: 'foo-bar' -> 'foo-bar' causes 'sqlite3.OperationalError: no such column: bar'
    if syntax_errors:
        print(f"\n[EMPIRICAL VULNERABILITY CONFIRMED] FTS5 Hyphen Syntax Errors: {syntax_errors}")
    
    # Asserting safe behavior fails as expected, revealing the bug:
    assert len(syntax_errors) == 0, f"Vulnerability found: FTS5 queries with hyphens cause OperationalError: {syntax_errors}"


# ============================================================================
# 2. Jaccard Deduplication Empirical Boundary Tests
# ============================================================================

def test_jaccard_100_percent_duplicates():
    """Verify 100% duplicate snippets are deduplicated down to single snippet."""
    snippet_text = "The quick brown fox jumps over the lazy dog in the sunny forest"
    duplicates_str = [snippet_text] * 10
    res_str = jaccard_deduplicate(duplicates_str, threshold=0.70)
    assert len(res_str) == 1, f"Expected 1 kept snippet for 100% string duplicates, got {len(res_str)}"

    duplicates_dict = [{"snippet": snippet_text, "id": i} for i in range(10)]
    res_dict = jaccard_deduplicate(duplicates_dict, threshold=0.70)
    assert len(res_dict) == 1, f"Expected 1 kept dict snippet for 100% dict duplicates, got {len(res_dict)}"
    assert res_dict[0]["id"] == 0


def test_jaccard_partial_overlap_boundary_069_vs_071():
    """
    Test exact boundary conditions around threshold 0.70.
    - 0.6923 similarity (< 0.70) -> Should NOT be deduplicated (both kept).
    - 0.7143 similarity (>= 0.70) -> Should BE deduplicated (second dropped).
    """
    snippet_A_069 = "word01 word02 word03 word04 word05 word06 word07 word08 word09 alpha01 alpha02"
    snippet_B_069 = "word01 word02 word03 word04 word05 word06 word07 word08 word09 beta01 beta02"

    wA = set(snippet_A_069.split())
    wB = set(snippet_B_069.split())
    j_val_069 = _compute_word_jaccard(wA, wB)
    assert round(j_val_069, 4) == 0.6923, f"Expected Jaccard 0.6923, got {j_val_069}"

    res_069 = jaccard_deduplicate([snippet_A_069, snippet_B_069], threshold=0.70)
    assert len(res_069) == 2, f"At similarity {j_val_069:.4f} (< 0.70), expected both kept, got {len(res_069)}"

    snippet_C_071 = "word01 word02 word03 word04 word05 charlie01"
    snippet_D_071 = "word01 word02 word03 word04 word05 delta01"

    wC = set(snippet_C_071.split())
    wD = set(snippet_D_071.split())
    j_val_071 = _compute_word_jaccard(wC, wD)
    assert round(j_val_071, 4) == 0.7143, f"Expected Jaccard 0.7143, got {j_val_071}"

    res_071 = jaccard_deduplicate([snippet_C_071, snippet_D_071], threshold=0.70)
    assert len(res_071) == 1, f"At similarity {j_val_071:.4f} (>= 0.70), expected second dropped, got {len(res_071)}"


def test_jaccard_empty_strings_and_short_words():
    """Verify behavior with empty strings, whitespace, and short word tokens."""
    empty_list = jaccard_deduplicate([])
    assert empty_list == []

    # Note: _RE_WORDS is \b[a-zA-Z0-9]{2,}\b (words >= 2 chars)
    # Single-char words yield empty word sets!
    short_words = ["a b c d e", "a b c d e"]
    res_short = jaccard_deduplicate(short_words, threshold=0.70)
    assert len(res_short) == 2, "Snippets with only 1-char tokens have empty word sets and are both kept"

    # Empty string snippets
    empty_snippets = ["", "   ", "\t\n"]
    res_empty = jaccard_deduplicate(empty_snippets, threshold=0.70)
    assert len(res_empty) == 3, "Empty string snippets yield empty word sets and are kept"


# ============================================================================
# 3. WebSearchFetcher Network Resilience Stress Tests
# ============================================================================

def test_web_search_offline_mode():
    """Verify WebSearchFetcher returns [] gracefully when offline (URLError)."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError(reason="[Errno 11001] getaddrinfo failed")

        res = WebSearchFetcher.fetch("python programming", timeout=2.0)
        assert res == [], f"Expected [] in offline mode, got {res}"

        res_func = fetch_web_context("python programming", timeout=2.0)
        assert res_func == [], f"Expected [] in offline mode from fetch_web_context, got {res_func}"


def test_web_search_dns_resolution_failure():
    """Verify WebSearchFetcher returns [] on DNS resolution failure (socket.gaierror)."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = socket.gaierror(-2, "Name or service not known")

        res = WebSearchFetcher.fetch("fastapi backend", timeout=2.0)
        assert res == [], f"Expected [] on DNS failure, got {res}"


def test_web_search_request_timeout():
    """Verify WebSearchFetcher returns [] when request times out (socket.timeout / TimeoutError)."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = socket.timeout("The read operation timed out")

        res = WebSearchFetcher.fetch("deep learning", timeout=1.0)
        assert res == [], f"Expected [] on socket timeout, got {res}"

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        res = WebSearchFetcher.fetch("deep learning", timeout=1.0)
        assert res == [], f"Expected [] on TimeoutError, got {res}"


def test_web_search_http_errors():
    """Verify WebSearchFetcher handles 404, 500, 403 HTTP errors without crashing."""
    for status_code in [404, 500, 403, 503]:
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="https://api.duckduckgo.com",
                code=status_code,
                msg=f"HTTP Error {status_code}",
                hdrs={},
                fp=None
            )

            res = WebSearchFetcher.fetch("test query", timeout=1.0)
            assert res == [], f"Expected [] on HTTP {status_code}, got {res}"


def test_web_search_null_related_topics_edge_case():
    """
    Adversarial test for JSON payload where 'RelatedTopics' is null (None in Python dict).
    Demonstrates whether fetch_web_context raises TypeError and discards valid AbstractText.
    """
    mock_json_payload = '{"Heading": "Test", "AbstractText": "Summary excerpt", "AbstractURL": "https://example.com", "RelatedTopics": null}'

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = mock_json_payload.encode('utf-8')
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        res = fetch_web_context("test query")
        print(f"\n[EMPIRICAL VULNERABILITY CONFIRMED] RelatedTopics=null payload returned empty results: {res}")
        # Expecting abstract text to be preserved:
        # If res is [], then the abstract snippet was lost due to TypeError on null RelatedTopics!
        assert len(res) == 1, "Vulnerability found: 'RelatedTopics': null in JSON payload caused loss of abstract snippet"


def test_web_search_html_stripper():
    """Verify HTML snippet parser strips tags cleanly."""
    html_input = "<p>Hello <b>World</b>! <a href='http://test.com'>Link</a></p>"
    stripped = strip_html_tags(html_input)
    assert stripped == "Hello World ! Link" or "Hello World! Link" in stripped
    assert "<" not in stripped and ">" not in stripped
