import unittest
from fastapi.testclient import TestClient
from src.app.main import app
from src.domain.graph_export import export_graph_to_graphml

class TestGraphExport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_export_graph_to_graphml_serialization(self):
        sample_data = {
            "nodes": [
                {"id": "doc1", "name": "Accounting.pdf", "type": "document", "group": "finance"},
                {"id": "tag_accounting", "name": "accounting", "type": "tag", "group": "tag"}
            ],
            "edges": [
                {"source": "doc1", "target": "tag_accounting", "relation": "tagged_with", "weight": 1}
            ]
        }
        xml_out = export_graph_to_graphml(sample_data)
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', xml_out)
        self.assertIn('<graphml', xml_out)
        self.assertIn('<node id="doc1">', xml_out)
        self.assertIn('<data key="d0">Accounting.pdf</data>', xml_out)
        self.assertIn('<edge id="e1" source="doc1" target="tag_accounting">', xml_out)

    def test_02_graphml_export_endpoint(self):
        res = self.client.get("/api/graph/export?limit=10")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers["content-type"], "application/xml")
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', res.text)
        self.assertIn("<graphml", res.text)

if __name__ == "__main__":
    unittest.main()
