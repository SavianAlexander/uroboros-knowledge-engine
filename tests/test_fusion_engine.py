import unittest
import sqlite3
import json
from src.infrastructure.database import init_db, get_db
from src.infrastructure.crawler_repository import init_crawler_schema
from src.domain.universal_crawler.models import CrawledDocument
from src.domain.universal_crawler.auto_rag_bridge import AutoRAGBridge
from src.infrastructure.vector_engine import MiniVectorEngine

class TestFusionEngine(unittest.TestCase):
    """
    Unit test suite for Dual-Engine Sovereign Fusion & Cross-Corpus Auto-RAG Ingestion.
    """

    @classmethod
    def setUpClass(cls):
        init_db()
        with get_db() as conn:
            init_crawler_schema(conn)

    def test_auto_rag_bridge_direct_ingestion(self):
        """Verify AutoRAGBridge ingests crawled document into core files, file_chunks, and tags tables."""
        with get_db() as conn:
            doc = CrawledDocument(
                job_id=99,
                url="https://sutra.oslpr.org/medida/ley-10-2024",
                title="Ley Núm. 10-2024 de Transparencia Gubernamental",
                content_type="text/html",
                content_text="Se establece por la presente ley que toda agencia pública de Puerto Rico deberá publicar sus presupuestos y auditorías anuales en formato abierto dentro de los 60 días siguientes al cierre del año fiscal.",
                merkle_sha256="sha256_mock_12345",
                merkle_dag_root="dag_root_mock_12345",
                entities_json=json.dumps({
                    "leyes": ["10-2024"],
                    "agencias": ["Oficina de Gerencia y Presupuesto"]
                })
            )
            file_id = AutoRAGBridge.ingest_crawled_document(conn, doc)
            self.assertGreater(file_id, 0)

            # Verify files table record
            cur = conn.execute("SELECT id, filename, filepath, notes FROM files WHERE id = ?", (file_id,))
            file_row = cur.fetchone()
            self.assertIsNotNone(file_row)
            self.assertEqual(file_row[1], doc.title)
            self.assertIn("crawler://job_99", file_row[2])
            self.assertIn("FRE 902 Certified", file_row[3])

            # Verify file_chunks table records & dense embeddings
            cur = conn.execute("SELECT id, chunk_index, content, embedding_json FROM file_chunks WHERE file_id = ?", (file_id,))
            chunks = cur.fetchall()
            self.assertGreaterEqual(len(chunks), 1)
            emb = json.loads(chunks[0][3])
            self.assertEqual(len(emb), 384)

            # Verify tags linkage
            cur = conn.execute("SELECT tag FROM tags WHERE file_id = ?", (file_id,))
            tag_names = [r[0] for r in cur.fetchall()]
            self.assertIn("SovereignCrawler", tag_names)
            self.assertIn("Job:99", tag_names)
            self.assertIn("Rule902-Certified", tag_names)

    def test_cross_corpus_hybrid_rag_search(self):
        """Verify that FTS / Search finds the auto-ingested crawler documents."""
        with get_db() as conn:
            cur = conn.execute("SELECT filepath, filename, content FROM fts_files WHERE fts_files MATCH 'Transparencia'")
            rows = cur.fetchall()
            self.assertGreaterEqual(len(rows), 1)
            self.assertIn("crawler://job_99", rows[0][0])

if __name__ == "__main__":
    unittest.main()
