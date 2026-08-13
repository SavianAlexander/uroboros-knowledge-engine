import unittest
from fastapi.testclient import TestClient
from src.app.main import app

class TestVaultExport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_vault_json_export_endpoint(self):
        res = self.client.get("/api/export/vault/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers["content-type"], "application/json")
        data = res.json()
        self.assertEqual(data["system"], "Uroboros Knowledge Engine")
        self.assertIn("total_documents", data)
        self.assertIn("documents", data)
        self.assertIsInstance(data["documents"], list)

if __name__ == "__main__":
    unittest.main()
