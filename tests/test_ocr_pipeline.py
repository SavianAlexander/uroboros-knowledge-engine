"""
Unit test suite for Hybrid PDF/OCR Ingestion Pipeline & Telemetry Router.
"""

import unittest
import tempfile
import os
from src.domain.ocr_pipeline import HybridPDFIngestionEngine


class TestHybridPDFIngestionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = HybridPDFIngestionEngine(confidence_threshold=0.65)
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.engine.process_pdf("/invalid/path/to/missing.pdf")

    def test_trigger_tududi_review_task_for_low_confidence(self):
        mock_result = {
            "filename": "scanned_doc.pdf",
            "filepath": "/tmp/scanned_doc.pdf",
            "confidence_score": 0.35,
            "requires_ocr_review": True,
            "num_pages": 4,
            "total_words": 80
        }

        task = self.engine.trigger_tududi_review_task(mock_result, project_id=13)
        self.assertIsNotNone(task)
        self.assertIn("scanned_doc.pdf", task["name"])
        self.assertEqual(task["priority"], 2)
        self.assertEqual(task["project_id"], 13)
        self.assertIn("Antigravity", task["tags"])

    def test_trigger_tududi_review_task_skipped_for_high_confidence(self):
        mock_result = {
            "filename": "clean_text.pdf",
            "filepath": "/tmp/clean_text.pdf",
            "confidence_score": 0.95,
            "requires_ocr_review": False,
            "num_pages": 10,
            "total_words": 2500
        }

        task = self.engine.trigger_tududi_review_task(mock_result)
        self.assertIsNone(task)


if __name__ == "__main__":
    unittest.main()
