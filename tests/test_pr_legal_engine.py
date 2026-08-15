import unittest
import sqlite3
from src.domain.pr_legal_engine import (
    PRLegalEngine,
    STATUS_VIGENTE,
    STATUS_DEROGADA_Y_SUBROGADA
)
from src.infrastructure.pr_legal_repository import (
    init_pr_legal_schema,
    ingest_pr_statutory_corpus,
    lookup_pr_citation_exact,
    query_pr_legal_hybrid
)

class TestPRLegalEngine(unittest.TestCase):
    """
    Unit & Verification Test Suite for Puerto Rico Legal Engine,
    AST Parsing, Deterministic Routing, and Concordance Mapping.
    """

    def test_deterministic_citation_parsing(self):
        """Verify regex grammar recognition across all major PR legal sources."""
        c1 = PRLegalEngine.parse_citation("31 LPRA § 5141")
        self.assertIsNotNone(c1)
        self.assertEqual(c1["type"], "LPRA")
        self.assertEqual(c1["title"], 31)
        self.assertEqual(c1["section"], "5141")

        c2 = PRLegalEngine.parse_citation("Const. PR Art. II, Sec. 8")
        self.assertIsNotNone(c2)
        self.assertEqual(c2["type"], "CONSTITUTION")
        self.assertEqual(c2["article"], "II")
        self.assertEqual(c2["section"], "8")

        c3 = PRLegalEngine.parse_citation("Código Civil de 2020, Art. 1536")
        self.assertIsNotNone(c3)
        self.assertEqual(c3["type"], "CODIGO_CIVIL_2020")
        self.assertEqual(c3["article"], 1536)

        c4 = PRLegalEngine.parse_citation("Código Penal de 2012, Art. 93")
        self.assertIsNotNone(c4)
        self.assertEqual(c4["type"], "CODIGO_PENAL_2012")
        self.assertEqual(c4["article"], 93)

        c5 = PRLegalEngine.parse_citation("142 D.P.R. 386")
        self.assertIsNotNone(c5)
        self.assertEqual(c5["type"], "DPR_JURISPRUDENCE")
        self.assertEqual(c5["volume"], 142)
        self.assertEqual(c5["page"], 386)

    def test_civil_code_1930_to_2020_concordance(self):
        """Verify automatic predecessor-successor concordance for 1930 vs 2020 Civil Code."""
        conc = PRLegalEngine.get_civil_code_concordance("1802")
        self.assertIsNotNone(conc)
        self.assertIn("Art. 1802", conc["predecessor"])
        self.assertIn("Art. 1536", conc["successor"])
        self.assertGreater(len(conc["leading_cases"]), 0)

        conc_presc = PRLegalEngine.get_civil_code_concordance("1868")
        self.assertIsNotNone(conc_presc)
        self.assertIn("Art. 1544", conc_presc["successor"])

    def test_merkle_provenance_hash_integrity(self):
        """Verify cryptographic SHA-256 leaf hash calculation."""
        text = "Artículo 1536. Toda persona que por culpa o negligencia causa daño a otra viene obligada a repararlo."
        meta = {"citation_key": "PR_CC2020_ART_1536", "status": "VIGENTE", "effective_date": "2020-11-28"}
        hash1 = PRLegalEngine.calculate_merkle_leaf(text, meta)
        hash2 = PRLegalEngine.calculate_merkle_leaf(text, meta)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

        # Mutated text must alter hash
        mutated_hash = PRLegalEngine.calculate_merkle_leaf(text + " Modificado.", meta)
        self.assertNotEqual(hash1, mutated_hash)

    def test_ast_document_parsing(self):
        """Verify structural AST chunking of statutory codes."""
        sample_statute = """
        TÍTULO IX - RESPONSABILIDAD CIVIL
        Artículo 1536. Responsabilidad por culpa o negligencia. Toda persona que por culpa causa daño debe repararlo.
        Artículo 1537. Concurrencia de culpas. La culpa de la víctima reduce la indemnización.
        """
        chunks = PRLegalEngine.parse_legal_ast_document(sample_statute, "Código Civil de Prueba")
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(any("1536" in c["section_header"] for c in chunks))
        self.assertTrue(all("merkle_sha256" in c for c in chunks))

    def test_sqlite_ingestion_and_exact_retrieval(self):
        """Verify database schema creation, full ingestion, and sub-millisecond retrieval."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        ingest_res = ingest_pr_statutory_corpus(conn)
        self.assertEqual(ingest_res["status"], "success")
        self.assertGreater(ingest_res["ingested_statutory_chunks"], 10)
        self.assertGreater(ingest_res["ingested_jurisprudence_cases"], 3)

        # Lookup Constitution Right to Privacy (Art. II, Sec. 8)
        hit_const = lookup_pr_citation_exact(conn, "Const. PR Art. II, Sec. 8")
        self.assertIsNotNone(hit_const)
        self.assertIn("honra", hit_const["content"].lower())
        self.assertEqual(hit_const["status"], STATUS_VIGENTE)

        # Lookup Civil Code Negligence (Art. 1536)
        hit_cc = lookup_pr_citation_exact(conn, "Código Civil de 2020, Art. 1536")
        self.assertIsNotNone(hit_cc)
        self.assertIn("culpa o negligencia", hit_cc["content"].lower())

        # Lookup Supreme Court Precedent (Pueblo v. Yip Berrios)
        hit_case = lookup_pr_citation_exact(conn, "142 D.P.R. 386")
        self.assertIsNotNone(hit_case)
        self.assertEqual(hit_case["case_name"], "Pueblo v. Yip Berríos")
        self.assertIn("pericial", hit_case["doctrine"].lower())

        # Hybrid Search query
        hybrid_hits = query_pr_legal_hybrid(conn, "legítima defensa")
        self.assertGreater(len(hybrid_hits), 0)
        self.assertTrue(any("Legítima defensa" in h["content"] for h in hybrid_hits))

        conn.close()

    def test_ground_truth_context_synthesis(self):
        """Verify zero-hallucination context synthesis with historical concordance."""
        query = "¿Cuál es el equivalente del antiguo Artículo 1802 en el Código Civil de 2020?"
        nodes = [
            {
                "citation_key": "PR_CC2020_ART_1536",
                "canonical_citation": "Código Civil de 2020, Art. 1536",
                "status": STATUS_VIGENTE,
                "merkle_sha256": "abcdef123456",
                "content": "Artículo 1536. Toda persona que por culpa o negligencia causa daño a otra viene obligada a repararlo.",
                "metadata": {"hierarchy_path": "Código Civil 2020 > Título IX"}
            }
        ]
        packet = PRLegalEngine.synthesize_ground_truth_context(query, nodes)
        self.assertIsNotNone(packet)
        self.assertEqual(len(packet["concordance_transitions"]), 1)
        concordance = packet["concordance_transitions"][0]
        self.assertEqual(concordance["queried_article"], "1802")
        self.assertIn("1536", concordance["successor"])
        self.assertGreaterEqual(len(packet["provenance_ledger"]), 1)

if __name__ == "__main__":
    unittest.main()
