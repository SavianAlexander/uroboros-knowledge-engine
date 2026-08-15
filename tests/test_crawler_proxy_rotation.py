import unittest
import json
from src.domain.universal_crawler.void_stealth import (
    BehavioralEntropyEngine,
    WaybackFallbackResolver,
    VoidStealthSession
)
from src.domain.universal_crawler.knowledge_graph_engine import (
    StatutoryASTDeconstructor,
    KnowledgeGraphExporter,
    ExecutiveBriefingGenerator
)

class TestVoidCrawler(unittest.TestCase):
    """
    Unit test suite for Sovereign Void-Tier Invisibility & Knowledge Graph Matrix.
    """

    def test_behavioral_entropy_canvas_mask(self):
        """Verify deterministic session canvas & hardware entropy masking."""
        mask1 = BehavioralEntropyEngine.generate_canvas_entropy_mask("session_alpha")
        mask2 = BehavioralEntropyEngine.generate_canvas_entropy_mask("session_alpha")
        mask3 = BehavioralEntropyEngine.generate_canvas_entropy_mask("session_beta")
        self.assertEqual(mask1, mask2)
        self.assertNotEqual(mask1["color_noise"], mask3["color_noise"])
        self.assertIn("NVIDIA", mask1["webgl_vendor"])

    def test_void_stealth_session_headers(self):
        """Verify Void-tier HTTP/2 headers and language locales."""
        session = VoidStealthSession()
        headers = session.get_void_headers("https://example.com/corpus/doc1")
        self.assertEqual(headers["Host"], "example.com")
        self.assertIn("Chromium", headers["sec-ch-ua"])
        self.assertIn("es-PR", headers["Accept-Language"])
        self.assertIn("gzip", headers["Accept-Encoding"])

    def test_statutory_ast_deconstructor(self):
        """Verify hierarchical decomposition of complex legal text."""
        statute_text = """
        LIBRO PRIMERO: DE LAS PERSONAS
        TÍTULO I: DEL MATRIMONIO
        CAPÍTULO I: DISPOSICIONES GENERALES
        Artículo 101. Requisitos para contraer matrimonio.
        El matrimonio es una institución civil.
        (a) Consentimiento voluntario de ambas partes.
        (b) Capacidad legal de los contrayentes.
        """
        nodes = StatutoryASTDeconstructor.deconstruct(statute_text, "Código Civil")
        self.assertGreater(len(nodes), 0)
        types = [n["node_type"] for n in nodes]
        self.assertIn("LIBRO", types)
        self.assertIn("TITULO", types)
        self.assertIn("ARTICULO", types)
        # Check hierarchy breadcrumb
        art_node = next(n for n in nodes if n["node_type"] == "ARTICULO")
        self.assertIn("LIBRO:PRIMERO", art_node["hierarchy_path"])

    def test_knowledge_graph_graphml_export(self):
        """Verify GraphML XML synthesis from document collections."""
        mock_docs = [{
            "id": 1,
            "url": "https://example.com/law1",
            "title": "Ley de Salud",
            "entities_json": json.dumps({"leyes": ["55-2020"], "agencias": ["ASES"]}),
            "triplets_json": json.dumps([{"subject": "Ley de Salud", "predicate": "enmienda_a", "object": "Ley 55-2020"}])
        }]
        graphml = KnowledgeGraphExporter.export_graphml(mock_docs)
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', graphml)
        self.assertIn('<graphml', graphml)
        self.assertIn('Ley de Salud', graphml)
        self.assertIn('enmienda_a', graphml)

    def test_knowledge_graph_cytoscape_export(self):
        """Verify Cytoscape JSON structure."""
        mock_docs = [{
            "id": 1,
            "url": "https://example.com/law1",
            "title": "Ley de Salud",
            "triplets_json": json.dumps([{"subject": "Ley de Salud", "predicate": "crea_estatuto", "object": "Plan Vital"}])
        }]
        cyto = KnowledgeGraphExporter.export_cytoscape_json(mock_docs)
        self.assertIn("nodes", cyto)
        self.assertIn("edges", cyto)
        self.assertEqual(len(cyto["edges"]), 1)
        self.assertEqual(cyto["edges"][0]["data"]["label"], "crea_estatuto")

    def test_executive_briefing_synthesis(self):
        """Verify markdown executive briefing generation."""
        mock_docs = [{
            "id": 1,
            "url": "https://example.com/law1",
            "title": "Ley de Salud",
            "content_text": "El Departamento de Salud y ASES administran el plan según 142 D.P.R. 386.",
            "entities_json": json.dumps({"leyes": ["55-2020"], "agencias": ["Departamento de Salud", "ASES"], "dpr_cases": ["142 D.P.R. 386"]}),
            "triplets_json": json.dumps([{"subject": "Ley de Salud", "predicate": "asigna_fondos_a", "object": "ASES"}])
        }]
        brief = ExecutiveBriefingGenerator.generate_briefing("Puerto Rico Healthcare Corpus", mock_docs)
        self.assertIn("# Executive Intelligence Briefing", brief)
        self.assertIn("Departamento de Salud", brief)
        self.assertIn("142 D.P.R. 386", brief)
        self.assertIn("Total Corpus Volume", brief)

if __name__ == "__main__":
    unittest.main()
