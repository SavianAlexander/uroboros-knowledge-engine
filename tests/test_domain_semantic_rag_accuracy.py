import os
import sys
import unittest
import tempfile
import shutil
import time

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.core.config as config
import src.infrastructure.database as db
import know

from src.domain.entropy_chunker import chunk_by_semantic_entropy, compute_jaccard_distance
from src.domain.temporal_rag import apply_temporal_decay_scoring
from src.domain.rag_engine import align_cross_lingual_query
from src.domain.self_rag_critique import evaluate_relevance, evaluate_support, critique_rag_passages
from src.domain.legal_accuracy_engine import LegalAccuracyEngine


class TestDomainSemanticRAGAccuracy(unittest.TestCase):
    """Domain test suite for semantic RAG, entropy chunking, temporal decay, cross-lingual aligners, and legal accuracy."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_semantic_")
        self.db_backup = db.DB_FILE
        self.know_db_backup = getattr(know, "DB_FILE", db.DB_FILE)
        self.active_backup = config.ACTIVE_DIR
        db.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        know.DB_FILE = db.DB_FILE
        config.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        db.DB_FILE = self.db_backup
        know.DB_FILE = self.know_db_backup
        config.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_entropy_semantic_boundary_chunking(self):
        """Verify semantic entropy boundary chunking creates topic boundaries on vocabulary distance spikes.

        Preconditions: Multi-sentence text with abrupt shift from astrophysics to organic chemistry.
        Invariants: compute_jaccard_distance spikes across topic boundary, splitting text into distinct chunks.
        Expected Outcomes: Multiple chunks created, each chunk having boundary_entropy_score and sentence_count.
        """
        text = (
            "Black holes are astronomical objects with gravitational fields so strong that nothing can escape. "
            "Event horizons define the boundary where the escape velocity exceeds the speed of light. "
            "Benzene is an aromatic hydrocarbon with a chemical formula of C6H6 and cyclic planar structure. "
            "Electrophilic aromatic substitution is the primary reaction mechanism in organic benzene synthesis."
        )
        chunks = chunk_by_semantic_entropy(text, distance_threshold=0.60, max_chunk_size=300)
        self.assertGreater(len(chunks), 1)
        self.assertIn("chunk_index", chunks[0])
        self.assertIn("char_length", chunks[0])
        self.assertGreater(chunks[0]["sentence_count"], 0)

    def test_02_entropy_chunker_empty_and_short_text(self):
        """Verify (Angle 4 & 17) entropy chunker handling of empty strings, whitespace, and single sentences.

        Preconditions: None, empty string, whitespace string, and single sentence passed to chunk_by_semantic_entropy.
        Invariants: Safe handling without raising IndexError or ZeroDivisionError.
        Expected Outcomes: Empty inputs return empty list; single sentence returns single chunk.
        """
        self.assertEqual(chunk_by_semantic_entropy(""), [])
        self.assertEqual(chunk_by_semantic_entropy("   \n\t "), [])

        single_res = chunk_by_semantic_entropy("A single short sentence for test.")
        self.assertEqual(len(single_res), 1)
        self.assertEqual(single_res[0]["sentence_count"], 1)

    def test_03_temporal_exponential_decay_scoring(self):
        """Verify (Angle 19) exponential time-decay scoring (S_final = S_vec * e^(-lambda * delta_t_days)).

        Preconditions: Two document candidates with identical base scores but different timestamps (today vs 180 days ago).
        Invariants: Exponential time decay ranks the recent document with a higher final score.
        Expected Outcomes: First scored candidate is the recent document with higher final_temporal_score.
        """
        now_ts = time.time()
        candidates = [
            {"filename": "ancient_spec.md", "score": 0.90, "timestamp": now_ts - (180 * 86400)},
            {"filename": "fresh_spec.md", "score": 0.90, "timestamp": now_ts - (5 * 86400)}
        ]
        scored = apply_temporal_decay_scoring(candidates, half_life_days=90.0)
        self.assertEqual(len(scored), 2)
        self.assertEqual(scored[0]["filename"], "fresh_spec.md")
        self.assertGreater(scored[0]["final_temporal_score"], scored[1]["final_temporal_score"])
        self.assertAlmostEqual(scored[1]["decay_factor"], 0.25, delta=0.05)

    def test_04_cross_lingual_query_alignment(self):
        """Verify (Angle 10) cross-lingual semantic translation and diacritic stripping for non-English terms.

        Preconditions: Spanish query with accented characters ('informe de auditoría financiero').
        Invariants: align_cross_lingual_query normalizes Unicode (NFC/NFD) and translates keywords to English.
        Expected Outcomes: status='success', translated=True, aligned_query contains 'report audit financial'.
        """
        query = "informe de auditoría financiero"
        res = align_cross_lingual_query(query)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["translated"])
        self.assertIn("audit", res["aligned_query"])
        self.assertIn("financial", res["aligned_query"])
        self.assertIn("report", res["aligned_query"])

    def test_05_self_rag_critique_rubric_scoring(self):
        """Verify Self-RAG reflection token evaluation ([IsRel:Yes/No], [IsSup:FullySupported/NoSupport]).

        Preconditions: Query and matching context passage, and answer grounded in passage.
        Invariants: evaluate_relevance returns [IsRel:Yes] and evaluate_support returns [IsSup:FullySupported].
        Expected Outcomes: critique_rag_passages filters out irrelevant chunks and sorts by relevance score.
        """
        query = "quantum key distribution cryptography"
        relevant_chunk = "Quantum key distribution utilizes photon polarization states for unconditional cryptographic security."
        irrelevant_chunk = "Cooking pasta requires boiling salted water for 10 minutes."

        rel_res = evaluate_relevance(query, relevant_chunk)
        self.assertTrue(rel_res["relevant"])
        self.assertEqual(rel_res["token"], "[IsRel:Yes]")

        irrel_res = evaluate_relevance(query, irrelevant_chunk)
        self.assertFalse(irrel_res["relevant"])
        self.assertEqual(irrel_res["token"], "[IsRel:No]")

        sup_res = evaluate_support("Quantum key distribution uses photon polarization for security.", relevant_chunk)
        self.assertTrue(sup_res["supported"])
        self.assertEqual(sup_res["token"], "[IsSup:FullySupported]")

        critique = critique_rag_passages(query, [irrelevant_chunk, relevant_chunk])
        self.assertEqual(len(critique), 1)
        self.assertEqual(critique[0]["content"], relevant_chunk)

    def test_06_legal_accuracy_engine_sanitization_and_nfc(self):
        """Verify (Angle 14 & 10) legal-grade FTS5 query sanitization with NFC normalization.

        Preconditions: Raw search queries with malicious FTS5 operator syntax and unnormalized accents.
        Invariants: LegalAccuracyEngine.sanitize_fts5_query_legal strips operator tokens and quotes phrases.
        Expected Outcomes: Quoted phrase matching generated without dangerous FTS operators.
        """
        raw_query = "contract* OR (terms: 'breach') ^5"
        sanitized = LegalAccuracyEngine.sanitize_fts5_query_legal(raw_query)
        self.assertNotIn("*", sanitized)
        self.assertNotIn("^", sanitized)
        self.assertIn('"contract"', sanitized)
        self.assertIn('"terms"', sanitized)
        self.assertIn('"breach"', sanitized)

    def test_07_legal_accuracy_sha256_verification(self):
        """Verify cryptographic SHA-256 bitwise parity verification for SOC 2 Type II integrity.

        Preconditions: Text payload and expected hex SHA-256 digest.
        Invariants: verify_sha256_integrity returns True for exact match, False for altered byte.
        Expected Outcomes: 100% deterministic bitwise parity verification.
        """
        text = "SOC 2 Type II processing integrity guarantee."
        import hashlib
        correct_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        tampered_hash = hashlib.sha256(b"tampered").hexdigest()

        self.assertTrue(LegalAccuracyEngine.verify_sha256_integrity(text, correct_hash))
        self.assertFalse(LegalAccuracyEngine.verify_sha256_integrity(text, tampered_hash))
        self.assertFalse(LegalAccuracyEngine.verify_sha256_integrity(None, correct_hash))

    def test_08_legal_payload_strict_validation(self):
        """Verify (Angle 12) strict schema validation on legal API request payloads.

        Preconditions: JSON dictionaries with missing or null mandatory fields.
        Invariants: validate_api_payload_strict returns (False, error_msg) on missing fields.
        Expected Outcomes: Valid payload passes; missing/null field payload fails with descriptive error.
        """
        valid_payload = {"session_id": "s_123", "query": "audit laws", "user_id": "u_99"}
        is_valid, msg = LegalAccuracyEngine.validate_api_payload_strict(valid_payload, ["session_id", "query", "user_id"])
        self.assertTrue(is_valid)

        null_payload = {"session_id": "s_123", "query": None, "user_id": "u_99"}
        is_valid2, msg2 = LegalAccuracyEngine.validate_api_payload_strict(null_payload, ["session_id", "query", "user_id"])
        self.assertFalse(is_valid2)
        self.assertIn("cannot be null", msg2.lower())

        missing_payload = {"session_id": "s_123", "query": "audit laws"}
        is_valid3, msg3 = LegalAccuracyEngine.validate_api_payload_strict(missing_payload, ["session_id", "query", "user_id"])
        self.assertFalse(is_valid3)
        self.assertIn("missing", msg3.lower())

    def test_09_cosine_similarity_edge_cases_and_zero_division(self):
        """Verify (Angle 4 & 25) exact cosine similarity edge cases, zero vectors, and orthogonal vectors.

        Preconditions: Zero vectors [0, 0], orthogonal vectors [1, 0] vs [0, 1], and dimension mismatches.
        Invariants: calculate_exact_cosine_similarity clamps output strictly to [-1.0, 1.0] without ZeroDivisionError.
        Expected Outcomes: Zero vectors return 0.0; orthogonal vectors return 0.0; identical vectors return 1.0.
        """
        self.assertEqual(LegalAccuracyEngine.calculate_exact_cosine_similarity([0.0, 0.0], [1.0, 1.0]), 0.0)
        self.assertEqual(LegalAccuracyEngine.calculate_exact_cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(LegalAccuracyEngine.calculate_exact_cosine_similarity([1.0, 2.0], [1.0, 2.0]), 1.0)
        self.assertEqual(LegalAccuracyEngine.calculate_exact_cosine_similarity([], [1.0]), 0.0)

    def test_10_temporal_decay_half_life_ordering(self):
        """Verify temporal decay ordering preserves stable sort across multiple half-life tiers.

        Preconditions: 4 document candidates spanning 0, 45, 90, and 180 days age.
        Invariants: Scored candidates strictly ordered by final_temporal_score in descending order.
        Expected Outcomes: Array is sorted in monotonic descending order.
        """
        now = time.time()
        cands = [
            {"filename": f"doc_{age}.txt", "score": 1.0, "timestamp": now - (age * 86400)}
            for age in [180, 0, 90, 45]
        ]
        scored = apply_temporal_decay_scoring(cands, half_life_days=90.0)
        filenames_order = [s["filename"] for s in scored]
        self.assertEqual(filenames_order, ["doc_0.txt", "doc_45.txt", "doc_90.txt", "doc_180.txt"])


if __name__ == "__main__":
    unittest.main()
