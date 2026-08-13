import unittest
from fastapi.testclient import TestClient
from src.app.main import app
from src.infrastructure.database import log_audit_event, get_audit_ledger

class TestAuditLedger(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_audit_ledger_lifecycle(self):
        # 1. Log event
        log_audit_event("MAINTENANCE", "Automated WAL Checkpoint & Defrag", {"freelist_reclaimed": 100})

        # 2. Get event via function
        events = get_audit_ledger(limit=10)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]["event_type"], "MAINTENANCE")

        # 3. Get event via REST API
        res = self.client.get("/api/system/audit-ledger?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["count"], 0)
        self.assertEqual(data["events"][0]["event_type"], "MAINTENANCE")

if __name__ == "__main__":
    unittest.main()
