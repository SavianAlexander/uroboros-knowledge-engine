import os
import shutil
import unittest
from fastapi.testclient import TestClient
from src.app.main import app
from src.infrastructure.backup_scheduler import BACKUP_DIR, create_database_backup, list_backups, prune_old_backups

class TestBackupScheduler(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_backup_scheduler_lifecycle(self):
        # 1. Trigger backup via API endpoint
        res = self.client.post("/api/system/backup")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("backup_file", data)

        # 2. List backups via API endpoint
        res2 = self.client.get("/api/system/backups")
        self.assertEqual(res2.status_code, 200)
        b_data = res2.json()
        self.assertGreater(b_data["count"], 0)
        self.assertTrue(any(b["filename"] == data["backup_file"] for b in b_data["backups"]))

        # 3. Test prune function
        pruned = prune_old_backups(max_files=1)
        self.assertIsInstance(pruned, int)

if __name__ == "__main__":
    unittest.main()
