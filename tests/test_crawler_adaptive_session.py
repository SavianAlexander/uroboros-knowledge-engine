import unittest
import json
from src.domain.universal_crawler.neuromorphic_stealth import (
    NeuromorphicCognitiveEngine,
    OmniStealthSession
)
from src.domain.universal_crawler.genesis_engine import (
    LegislativeGenesisExtractor,
    LegalDepositionDossierSynthesizer
)
from src.domain.universal_crawler.vector_semantic_matrix import FastSemanticVectorMatrix

class TestOmniCrawler(unittest.TestCase):
    """
    Unit test suite for Universal Deep Neural Harvester & Cross-Examination Matrix.
    """

    def test_neuromorphic_keystroke_dynamics(self):
        """Verify human neuromuscular keystroke flight times and pauses."""
        text = "Ley de Reforma Contributiva"
        delays = NeuromorphicCognitiveEngine.calculate_keystroke_flight_times(text)
        self.assertEqual(len(delays), len(text))
        for d in delays:
            self.assertGreater(d, 0.0)

    def test_omni_stealth_headers(self):
        """Verify canonical TLS 1.3 headers for Universal session."""
        session = OmniStealthSession(session_seed="test_omni_seed")
        headers = session.get_omni_headers("https://sutra.oslpr.org/api/medidas")
        self.assertEqual(headers["Host"], "sutra.oslpr.org")
        self.assertIn("Chromium", headers["sec-ch-ua"])
        self.assertIn("es-PR", headers["Accept-Language"])

    def test_legislative_genesis_extraction(self):
        """Verify extraction of full bill journey (Radicación -> Informes -> Firma)."""
        sample_doc = """
        PROYECTO DEL SENADO 1234
        Fecha de Radicación: 15 de enero de 2024
        Informe Positivo de la Comisión de Hacienda
        Votación en el Senado: 20 a favor, 5 en contra
        Aprobada por el Gobernador el 30 de junio de 2024
        """
        genesis = LegislativeGenesisExtractor.extract_genesis_timeline(sample_doc, "P. del S. 1234")
        self.assertGreater(genesis["milestones_count"], 0)
        milestones = [m["milestone"] for m in genesis["timeline"]]
        self.assertIn("RADICACION", milestones)
        self.assertIn("INFORME_COMISION", milestones)
        self.assertIn("FIRMA_GOBERNADOR", milestones)

    def test_legal_deposition_dossier_synthesis(self):
        """Verify generation of structured cross-examination deposition dossiers."""
        mock_docs = [{
            "id": 1,
            "title": "Ley Núm. 101-2023",
            "content_text": """
            El Secretario de Salud deberá remitir informes trimestrales a la Asamblea Legislativa.
            Tendrá la obligación de mantener un registro electrónico de proveedores.
            Toda persona que viole este estatuto incurrirá en una multa de $5,000 por infracción.
            El término de cumplimiento será a más tardar a los 60 días.
            Véase 150 D.P.R. 450 para precedentes aplicables.
            """
        }]
        dossier = LegalDepositionDossierSynthesizer.generate_deposition_dossier("Salud", mock_docs)
        self.assertIn("CROSS-EXAMINATION DEPOSITION DOSSIER", dossier)
        self.assertIn("MANDATORY AFFIRMATIVE DUTIES", dossier)
        self.assertIn("deberá remitir", dossier)
        self.assertIn("multa de $5,000", dossier)
        self.assertIn("150 D.P.R. 450", dossier)

    def test_vector_semantic_embedding_and_cosine_ranking(self):
        """Verify zero-dependency 384-dimensional dense semantic vectors."""
        text_a = "Código Civil de Puerto Rico y derecho de familia"
        text_b = "Código Civil relativo a las sucesiones y testamentos"
        text_c = "Reglamento aeronáutico de navegación marítima"

        vec_a = FastSemanticVectorMatrix.vectorize_text(text_a)
        vec_b = FastSemanticVectorMatrix.vectorize_text(text_b)
        vec_c = FastSemanticVectorMatrix.vectorize_text(text_c)

        self.assertEqual(len(vec_a), 384)
        sim_ab = FastSemanticVectorMatrix.cosine_similarity(vec_a, vec_b)
        sim_ac = FastSemanticVectorMatrix.cosine_similarity(vec_a, vec_c)

        # Related legal text should have higher semantic similarity than unrelated text
        self.assertGreater(sim_ab, sim_ac)

        # Document ranking
        docs = [
            {"id": 1, "title": "Código Civil", "content_text": text_a},
            {"id": 2, "title": "Reglamento Marítimo", "content_text": text_c}
        ]
        ranked = FastSemanticVectorMatrix.rank_documents("derecho civil familiar", docs, top_k=2)
        self.assertEqual(ranked[0]["id"], 1)

if __name__ == "__main__":
    unittest.main()
