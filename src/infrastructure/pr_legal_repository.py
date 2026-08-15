import sqlite3
import unicodedata
from typing import List, Dict, Any, Optional
from src.domain.pr_legal_engine import PRLegalEngine, STATUS_VIGENTE
from src.infrastructure.pr_legal_corpus import get_all_pr_statutory_sources, PR_LEADING_CASES_DATA

"""
SQLite Repository & Deterministic Indexing for Puerto Rico Legal Corpus.
Provides fast sub-2ms exact citation lookups, Merkle integrity auditing, and statutory RAG extraction.
"""

def init_pr_legal_schema(conn: sqlite3.Connection):
    """Create dedicated PR legal tables and indexes if they do not exist."""
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pr_legal_corpus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citation_key TEXT UNIQUE NOT NULL,
        canonical_citation TEXT NOT NULL,
        title TEXT NOT NULL,
        hierarchy_path TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'VIGENTE',
        effective_date TEXT,
        source_origin TEXT,
        source_url TEXT,
        content TEXT NOT NULL,
        merkle_sha256 TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pr_legal_citation_key ON pr_legal_corpus(citation_key);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pr_legal_status ON pr_legal_corpus(status);")

    # Table for D.P.R. jurisprudence precedents
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pr_legal_jurisprudence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_name TEXT NOT NULL,
        citation TEXT UNIQUE NOT NULL,
        year INTEGER,
        area TEXT,
        doctrine TEXT NOT NULL,
        related_statutes TEXT,
        merkle_sha256 TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pr_jurisprudence_citation ON pr_legal_jurisprudence(citation);")
    conn.commit()

def ingest_pr_statutory_corpus(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Ingest and index all curated Puerto Rico statutory sources into SQLite with Merkle integrity."""
    init_pr_legal_schema(conn)
    sources = get_all_pr_statutory_sources()
    total_chunks = 0

    for src in sources:
        doc_name = src["name"]
        raw_text = src["text"]
        meta = src["metadata"]
        chunks = PRLegalEngine.parse_legal_ast_document(raw_text, doc_name, meta)

        for chunk in chunks:
            c_meta = chunk["metadata"]
            conn.execute("""
            INSERT OR REPLACE INTO pr_legal_corpus (
                citation_key, canonical_citation, title, hierarchy_path,
                status, effective_date, source_origin, source_url, content, merkle_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk["citation_key"],
                chunk["canonical_citation"],
                doc_name,
                c_meta.get("hierarchy_path", ""),
                chunk["status"],
                c_meta.get("effective_date", ""),
                c_meta.get("source_origin", ""),
                c_meta.get("source_url", ""),
                chunk["content"],
                chunk["merkle_sha256"]
            ))
            total_chunks += 1

    # Ingest Leading Jurisprudence Precedents
    total_cases = 0
    for case in PR_LEADING_CASES_DATA:
        case_meta = {"citation_key": case["citation"], "status": "JURISPRUDENCE_VIGENTE"}
        merkle = PRLegalEngine.calculate_merkle_leaf(f"{case['case_name']} {case['doctrine']}", case_meta)
        conn.execute("""
        INSERT OR REPLACE INTO pr_legal_jurisprudence (
            case_name, citation, year, area, doctrine, related_statutes, merkle_sha256
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            case["case_name"],
            case["citation"],
            case["year"],
            case["area"],
            case["doctrine"],
            ", ".join(case["related_statutes"]),
            merkle
        ))
        total_cases += 1

    conn.commit()
    return {
        "status": "success",
        "ingested_statutory_chunks": total_chunks,
        "ingested_jurisprudence_cases": total_cases
    }

def lookup_pr_citation_exact(conn: sqlite3.Connection, query: str) -> Optional[Dict[str, Any]]:
    """Deterministic exact citation router. Resolves queries in < 2ms."""
    parsed = PRLegalEngine.parse_citation(query)
    if not parsed:
        return None

    citation_key = parsed.get("citation_key")
    if not citation_key:
        return None

    # Check statutory corpus table
    row = conn.execute(
        "SELECT * FROM pr_legal_corpus WHERE citation_key = ? LIMIT 1",
        (citation_key,)
    ).fetchone()

    if row:
        return {
            "match_type": "STATUTE_EXACT",
            "citation_key": row["citation_key"],
            "canonical_citation": row["canonical_citation"],
            "title": row["title"],
            "hierarchy_path": row["hierarchy_path"],
            "status": row["status"],
            "effective_date": row["effective_date"],
            "source_origin": row["source_origin"],
            "source_url": row["source_url"],
            "content": row["content"],
            "merkle_sha256": row["merkle_sha256"]
        }

    # Check jurisprudence table
    canon_cite = parsed.get("canonical_citation", "")
    case_row = conn.execute(
        "SELECT * FROM pr_legal_jurisprudence WHERE citation LIKE ? OR case_name LIKE ? LIMIT 1",
        (f"%{canon_cite}%", f"%{query}%")
    ).fetchone()

    if case_row:
        return {
            "match_type": "JURISPRUDENCE_EXACT",
            "case_name": case_row["case_name"],
            "citation": case_row["citation"],
            "year": case_row["year"],
            "area": case_row["area"],
            "doctrine": case_row["doctrine"],
            "related_statutes": case_row["related_statutes"],
            "merkle_sha256": case_row["merkle_sha256"]
        }

    return None

def query_pr_legal_hybrid(conn: sqlite3.Connection, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Hybrid legal search combining deterministic citation match with keyword containment.
    """
    results = []
    exact = lookup_pr_citation_exact(conn, query)
    if exact:
        results.append(exact)

    clean_q = unicodedata.normalize("NFC", query.strip().lower())
    terms = [t for t in clean_q.split() if len(t) > 3]

    if terms:
        # Search statutory provisions matching terms
        like_clauses = " AND ".join(["LOWER(content) LIKE ?" for _ in terms])
        params = [f"%{t}%" for t in terms]
        rows = conn.execute(
            f"SELECT * FROM pr_legal_corpus WHERE {like_clauses} LIMIT ?",
            (*params, limit)
        ).fetchall()

        for r in rows:
            if not any(res.get("citation_key") == r["citation_key"] for res in results):
                results.append({
                    "match_type": "STATUTE_KEYWORD",
                    "citation_key": r["citation_key"],
                    "canonical_citation": r["canonical_citation"],
                    "title": r["title"],
                    "hierarchy_path": r["hierarchy_path"],
                    "status": r["status"],
                    "content": r["content"],
                    "merkle_sha256": r["merkle_sha256"]
                })

    return results
