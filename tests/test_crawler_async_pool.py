import unittest
import json
from src.domain.universal_crawler.browser_stealth import (
    HumanMicroActionEngine,
    BrowserEvasionHooks,
    QuantumStealthSession,
    BrowserStealthSession
)
from src.domain.universal_crawler.concordance_engine import StatutoryConcordanceEngine
from src.domain.universal_crawler.vault_visualizer import KnowledgeVaultVisualizer

class TestQuantumCrawler(unittest.TestCase):
    """
    Unit test suite for Crawler Invisibility & Knowledge Vault Visualizer.
    """

    def test_human_micro_actions(self):
        """Verify execution of human micro-actions."""
        script = BrowserEvasionHooks.get_cdp_evasion_script()
        self.assertIn("webdriver", script)
        self.assertIn("window.chrome", script)
        self.assertIn("es-PR", script)

    def test_quantum_headers_and_locale(self):
        """Verify Quantum-tier canonical headers and locale preservation."""
        session = QuantumStealthSession()
        headers = session.get_quantum_headers("https://example.com/quantum/asset")
        self.assertEqual(headers["Host"], "example.com")
        self.assertIn("Chromium", headers["sec-ch-ua"])
        self.assertIn("es-PR", headers["Accept-Language"])

    def test_statutory_concordance_lifecycle(self):
        """Verify lifecycle state transitions across statutory corpora."""
        mock_docs = [
            {
                "id": 1,
                "title": "Ley Núm. 55-2020",
                "url": "https://example.com/ley55",
                "content_text": "Código Civil de Puerto Rico.",
                "entities_json": json.dumps({"leyes": ["55-2020"]}),
                "triplets_json": "[]"
            },
            {
                "id": 2,
                "title": "Ley Núm. 100-2022",
                "url": "https://example.com/ley100",
                "content_text": "Para enmendar la Ley Núm. 55-2020.",
                "entities_json": json.dumps({"leyes": ["100-2022", "55-2020"]}),
                "triplets_json": json.dumps([{"subject": "Ley Núm. 100-2022", "predicate": "enmienda_a", "object": "Ley Núm. 55-2020"}])
            },
            {
                "id": 3,
                "title": "Ley Núm. 200-2024",
                "url": "https://example.com/ley200",
                "content_text": "Para derogar la Ley Núm. 10-1950.",
                "entities_json": json.dumps({"leyes": ["200-2024", "10-1950"]}),
                "triplets_json": json.dumps([{"subject": "Ley Núm. 200-2024", "predicate": "deroga", "object": "Ley Núm. 10-1950"}])
            }
        ]
        concordance = StatutoryConcordanceEngine.build_concordance_matrix(mock_docs)
        self.assertEqual(concordance["total_statutes"], 3)
        self.assertEqual(concordance["lifecycle_status"]["Ley Núm. 55-2020"], "ENMENDADA")
        self.assertEqual(concordance["lifecycle_status"]["Ley Núm. 10-1950"], "DEROGADA")
        self.assertEqual(concordance["lifecycle_status"]["Ley Núm. 200-2024"], "VIGENTE")

    def test_jurisdictional_conflict_detection(self):
        """Verify automated discovery of conflicting jurisdictional mandates."""
        mock_docs = [
            {
                "id": 1,
                "title": "Ley de Salud",
                "content_text": "Se faculta a ASES para administrar los fondos federales de salud en Puerto Rico."
            },
            {
                "id": 2,
                "title": "Ley de Reorganización",
                "content_text": "Se faculta al Departamento de Salud para administrar los fondos federales de salud en Puerto Rico."
            }
        ]
        conflicts = StatutoryConcordanceEngine.detect_jurisdictional_conflicts(mock_docs)
        self.assertGreater(len(conflicts), 0)
        self.assertEqual(conflicts[0]["statute_a"], "Ley de Salud")
        self.assertEqual(conflicts[0]["statute_b"], "Ley de Reorganización")

    def test_interactive_vault_visualizer_html_generation(self):
        """Verify generation of self-contained interactive HTML5 application."""
        mock_docs = [{
            "id": 1,
            "title": "Ley Núm. 55-2020",
            "url": "https://example.com/doc",
            "content_text": "Contenido del Código Civil.",
            "entities_json": json.dumps({"leyes": ["55-2020"], "agencias": ["Tribunal Supremo"]}),
            "triplets_json": "[]"
        }]
        concordance = StatutoryConcordanceEngine.build_concordance_matrix(mock_docs)
        html = KnowledgeVaultVisualizer.generate_html("Test Corpus", mock_docs, concordance)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<canvas id=\"canvas\"></canvas>", html)
        self.assertIn("Ley Núm. 55-2020", html)
        self.assertIn("Node Inspector", html)

if __name__ == "__main__":
    unittest.main()
