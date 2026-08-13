import unittest
from fastapi.testclient import TestClient
from src.app.main import app

class TestSearchBookmarks(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_search_bookmarks_lifecycle(self):
        # 1. Create bookmark
        res = self.client.post("/api/search/bookmarks", json={
            "name": "Audit Query",
            "query": "accounting standards for leases",
            "search_mode": "rrf"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")

        # 2. List bookmarks
        res2 = self.client.get("/api/search/bookmarks")
        self.assertEqual(res2.status_code, 200)
        b_list = res2.json()["bookmarks"]
        self.assertTrue(any(b["name"] == "Audit Query" for b in b_list))

        # 3. Delete bookmark
        res3 = self.client.delete("/api/search/bookmarks/Audit%20Query")
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
