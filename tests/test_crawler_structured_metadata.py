import unittest
import json
from src.domain.universal_crawler.forensic_vault import (
    ForensicChainOfCustody,
    EvidenceCertificateGenerator
)
from src.domain.universal_crawler.statutory_anatomy import (
    ExhaustiveStatutoryAnatomyParser,
    MultiSourceQuorumValidator
)

class TestForensicCrawler(unittest.TestCase):
    """
    Unit test suite for Court-Admissible Forensic Ingestion & Legal Chain of Custody.
    """

    def test_multi_hash_chain_of_custody(self):
        """Verify generation of SHA-512, SHA-256, and MD5 forensic checksums."""
        sample_bytes = b"LEGISLATURA DE PUERTO RICO - ESTATUTO OFICIAL"
        hashes = ForensicChainOfCustody.compute_forensic_hashes(sample_bytes)
        self.assertEqual(len(hashes["sha512"]), 128)
        self.assertEqual(len(hashes["sha256"]), 64)
        self.assertEqual(len(hashes["md5"]), 32)
        self.assertEqual(hashes["byte_size"], len(sample_bytes))

    def test_merkle_inclusion_proof(self):
        """Verify construction of branch inclusion proofs."""
        leaves = ["hash1", "hash2", "hash3", "hash4"]
        proof = ForensicChainOfCustody.generate_merkle_inclusion_proof("hash1", 0, leaves)
        self.assertEqual(len(proof), 2)
        self.assertEqual(proof[0]["sibling_hash"], "hash2")

    def test_evidence_certificate_generation(self):
        """Verify generation of Rule 902 Section (13)/(14) digital affidavit."""
        hashes = {"sha512": "abc512", "sha256": "def256", "md5": "123md5", "byte_size": 1024}
        cert = EvidenceCertificateGenerator.generate_affidavit_markdown(
            "Ley Núm. 55-2020",
            "https://sutra.oslpr.org/medidas/136624",
            hashes,
            "merkle_root_999",
            "2026-08-15T00:00:00Z"
        )
        self.assertIn("CERTIFICATE OF AUTHENTICITY", cert)
        self.assertIn("FRE 902(13)", cert)
        self.assertIn("SHA-512", cert)
        self.assertIn("abc512", cert)

    def test_evidence_certificate_json_ld(self):
        """Verify structured JSON-LD Section 902 certification."""
        hashes = {"sha512": "abc512", "sha256": "def256", "md5": "123md5", "byte_size": 1024}
        ld = EvidenceCertificateGenerator.generate_affidavit_json_ld(
            "Ley Núm. 55-2020",
            "https://sutra.oslpr.org/medidas/136624",
            hashes,
            "merkle_root_999",
            "2026-08-15T00:00:00Z"
        )
        self.assertEqual(ld["@type"], "Legislation")
        self.assertEqual(ld["evidenceCertification"]["legalStandard"], "FRE 902(13)/(14)")
        self.assertEqual(ld["evidenceCertification"]["sha512"], "abc512")

    def test_statutory_anatomy_parser(self):
        """Verify exhaustive decomposition of statutory preambles and clauses."""
        statute_text = """
        LEY NÚM. 55-2020
        EXPOSICIÓN DE MOTIVOS
        El Código Civil representa la columna vertebral del derecho privado.
        POR CUANTO: Es necesario modernizar las relaciones contractuales.
        DECRÉTASE POR LA ASAMBLEA LEGISLATIVA DE PUERTO RICO:
        Artículo 1. Título Preliminar.
        Las leyes obligan desde su promulgación.
        Cláusula de Separabilidad: Si cualquier disposición fuese declarada nula...
        Vigencia: Esta Ley empezará a regir a los ciento ochenta días de su aprobación.
        Aprobada en San Juan, Puerto Rico por el Gobernador.
        """
        anatomy = ExhaustiveStatutoryAnatomyParser.parse_complete_anatomy(statute_text, "Ley Núm. 55-2020")
        self.assertIn("columna vertebral", anatomy["exposicion_motivos"])
        self.assertEqual(len(anatomy["por_cuanto_clauses"]), 1)
        self.assertIn("DECRÉTASE", anatomy["formula_decretatoria"])
        self.assertEqual(len(anatomy["articulos"]), 1)
        self.assertIn("declarada nula", anatomy["clausula_separabilidad"])
        self.assertIn("ciento ochenta días", anatomy["clausula_vigencia"])
        self.assertGreater(len(anatomy["firmas"]), 0)

    def test_multi_source_quorum_validator(self):
        """Verify cross-source text parity and discrepancy discovery."""
        text_a = "El Estado Libre Asociado de Puerto Rico garantiza el debido proceso de ley."
        text_b = "El Estado Libre Asociado de Puerto Rico garantiza el debido proceso de ley."
        text_c = "El Estado Libre Asociado de Puerto Rico garantiza el debido proceso legal."

        res_perfect = MultiSourceQuorumValidator.calculate_text_consensus(text_a, text_b)
        self.assertTrue(res_perfect["is_perfect_parity"])
        self.assertEqual(res_perfect["consensus_score"], 1.0)

        res_diff = MultiSourceQuorumValidator.calculate_text_consensus(text_a, text_c)
        self.assertFalse(res_diff["is_perfect_parity"])
        self.assertGreater(res_diff["discrepancies_count"], 0)

if __name__ == "__main__":
    unittest.main()
