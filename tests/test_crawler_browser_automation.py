import unittest
import sqlite3
import json
import time
from src.domain.universal_crawler.phantom_stealth import (
    SyntheticBiometrics,
    PersonaProfileManager,
    PhantomStealthEngine
)
from src.domain.universal_crawler.deep_extractor import (
    TableStructureReconstructor,
    EntityKnowledgeGraphExtractor,
    DeepKnowledgeHarvester
)
from src.domain.universal_crawler.merkle_dag import MerkleDAG
from src.domain.universal_crawler.models import CrawlJob, CrawlConfig
from src.infrastructure.crawler_repository import (
    init_crawler_schema,
    create_job,
    get_job,
    save_crawled_document,
    get_job_documents
)

class TestPhantomCrawler(unittest.TestCase):
    """
    Unit test suite for the Browser Automation & Deep Knowledge Extraction Engine.
    """

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_crawler_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_synthetic_biometric_bezier_trajectory(self):
        """Verify generation of smooth Bezier mouse trajectories."""
        start = (100, 200)
        end = (800, 600)
        trajectory = SyntheticBiometrics.generate_bezier_trajectory(start, end, steps=20)
        self.assertEqual(len(trajectory), 21)
        self.assertEqual(trajectory[0], start)
        self.assertAlmostEqual(trajectory[-1][0], end[0], delta=5)
        self.assertAlmostEqual(trajectory[-1][1], end[1], delta=5)

    def test_synthetic_saccade_delay_calculation(self):
        """Verify reading saccade gaze dwell calculation for personas."""
        delay_scholar = SyntheticBiometrics.calculate_saccade_delay(2000, persona="Legal_Scholar")
        delay_speed = SyntheticBiometrics.calculate_saccade_delay(2000, persona="Speed_Reader")
        self.assertGreater(delay_scholar, 0.5)
        self.assertGreater(delay_scholar, delay_speed)

    def test_phantom_canonical_headers(self):
        """Verify exact canonical headers and client hints for Phantom engine."""
        engine = PhantomStealthEngine(persona_name="Legal_Scholar")
        headers = engine.get_canonical_headers("https://sutra.oslpr.org/medidas/100")
        self.assertEqual(headers["Host"], "sutra.oslpr.org")
        self.assertIn("Chromium", headers["sec-ch-ua"])
        self.assertIn("es-PR", headers["Accept-Language"])
        self.assertIn("Upgrade-Insecure-Requests", headers)

    def test_table_structure_reconstruction(self):
        """Verify HTML table parsing into Markdown matrices."""
        html_table = """
        <table>
            <tr><th>Artículo</th><th>Materia</th><th>Vigencia</th></tr>
            <tr><td>Art. 1536</td><td>Responsabilidad Civil</td><td>Vigente</td></tr>
            <tr><td>Art. 1540</td><td>Culpa In Vigilando</td><td>Vigente</td></tr>
        </table>
        """
        tables = TableStructureReconstructor.extract_html_tables(html_table)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["row_count"], 3)
        self.assertEqual(tables[0]["column_count"], 3)
        self.assertIn("| Artículo | Materia | Vigencia |", tables[0]["markdown"])
        self.assertIn("Art. 1536", tables[0]["markdown"])

    def test_entity_extraction(self):
        """Verify typing and extraction of statutory entities."""
        legal_text = "El 15 de marzo de 2021, la Ley Núm. 55-2020 fue enmendada por el Artículo 12 de la Ley 235-2015 ante el Tribunal Supremo de Puerto Rico con una fianza de $50,000 dólares según 142 D.P.R. 386."
        entities = EntityKnowledgeGraphExtractor.extract_entities(legal_text)
        self.assertIn("55-2020", entities["leyes"])
        self.assertIn("235-2015", entities["leyes"])
        self.assertIn("12", entities["articulos"])
        self.assertIn("142 D.P.R. 386", entities["dpr_cases"])
        self.assertTrue(any("$50,000" in m or "dólares" in m for m in entities["monedas"]))

    def test_knowledge_triplet_extraction(self):
        """Verify RDF-style relationship extraction (Subject -> Predicate -> Object)."""
        text = "Para enmendar el Artículo 7 de la Ley 235-2015 a los fines de..."
        triplets = EntityKnowledgeGraphExtractor.extract_knowledge_triplets(text, "Medida PS0014")
        self.assertGreater(len(triplets), 0)
        self.assertEqual(triplets[0]["subject"], "Medida PS0014")
        self.assertEqual(triplets[0]["predicate"], "enmienda_a")
        self.assertIn("Ley 235-2015", triplets[0]["object"])

    def test_hierarchical_merkle_dag(self):
        """Verify multi-level Merkle DAG tree calculation."""
        doc_text = "Paragraph 1: El Estado Libre Asociado de Puerto Rico.\n\nParagraph 2: La Constitución de Puerto Rico consagra los derechos fundamentales."
        dag = MerkleDAG.generate_document_dag(doc_text, "https://sutra.oslpr.org/doc1", {"job_id": 1})
        self.assertEqual(dag["leaf_count"], 2)
        self.assertEqual(len(dag["merkle_root"]), 64)
        self.assertNotEqual(dag["leaves"][0], dag["leaves"][1])

    def test_deep_knowledge_harvester_pipeline(self):
        """Verify deep multi-modal harvester pipeline."""
        sample_html = """
        <html>
        <head><title>Ley Especial de Salud</title></head>
        <body>
            <h1>Ley Especial</h1>
            <p>Para crear la Ley del Plan Integral de Salud aprobada el 10 de enero de 2022.</p>
            <table><tr><th>Sección</th><th>Presupuesto</th></tr><tr><td>1</td><td>$100,000</td></tr></table>
        </body>
        </html>
        """
        harvested = DeepKnowledgeHarvester.harvest(sample_html.encode('utf-8'), "text/html", "https://example.com/ley")
        self.assertEqual(harvested["title"], "Ley Especial de Salud")
        self.assertEqual(harvested["stats"]["table_count"], 1)
        self.assertGreater(harvested["stats"]["char_count"], 50)
        self.assertIn("fechas", harvested["entities"])

if __name__ == "__main__":
    unittest.main()
