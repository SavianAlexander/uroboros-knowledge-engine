import unittest
from fastapi.testclient import TestClient
from src.app.main import app

class TestSystemMaintenance(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_execute_system_maintenance_endpoint(self):
        res = self.client.post("/api/system/maintenance")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("database", data)
        self.assertIn("file_count", data["database"])

if __name__ == "__main__":
    unittest.main()
