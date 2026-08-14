import os
import unittest
import know
from src.domain.file_diff import compare_text_content
from fastapi.testclient import TestClient
from src.app.main import app

class TestFileDiff(unittest.TestCase):
    def setUp(self):
        know.init_db()
        self.client = TestClient(app)
        os.makedirs("dumps", exist_ok=True)
        with open("dumps/test_a.txt", "w", encoding="utf-8") as f:
            f.write("Line 1\nLine 2\nLine 3\n")
        with open("dumps/test_b.txt", "w", encoding="utf-8") as f:
            f.write("Line 1\nLine 2 modified\nLine 3\nLine 4\n")

    def tearDown(self):
        for f in ["dumps/test_a.txt", "dumps/test_b.txt"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    def test_compare_text_content_additions_and_deletions(self):
        text_a = "line 1\nline 2\nline 3"
        text_b = "line 1\nline 2 modified\nline 3\nline 4"
        res = compare_text_content(text_a, text_b, "File A", "File B")
        
        self.assertIn("similarity_ratio", res)
        self.assertIn("similarity_pct", res)
        self.assertGreater(res["additions"], 0)
        self.assertGreater(res["deletions"], 0)
        self.assertIsInstance(res["diff_lines"], list)

    def test_file_diff_endpoint(self):
        res = self.client.get("/api/file/diff?file_a=dumps/test_a.txt&file_b=dumps/test_b.txt")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("similarity_ratio", data)
        self.assertEqual(data["file_a"], "dumps/test_a.txt")
        self.assertEqual(data["file_b"], "dumps/test_b.txt")

if __name__ == "__main__":
    unittest.main()
