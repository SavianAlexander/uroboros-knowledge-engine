import unittest
from src.domain.daily_briefing import generate_daily_briefing

class TestDailyBriefing(unittest.TestCase):
    def test_generates_briefing_dict(self):
        res = generate_daily_briefing()
        self.assertEqual(res["status"], "success")
        self.assertIn("total_documents", res)
        self.assertIn("executive_summary", res)

if __name__ == "__main__":
    unittest.main()
