import unittest
from src.core.model_router import route_prompt_model

class TestModelRouter(unittest.TestCase):
    def test_routes_general_chat_to_7b(self):
        res = route_prompt_model("Hello, how are you today?")
        self.assertEqual(res["model"], "qwen2.5:7b")

    def test_routes_technical_code_to_14b(self):
        res = route_prompt_model("Write a python class implementing Louvain community detection algorithm")
        self.assertEqual(res["model"], "qwen2.5-coder:14b")

if __name__ == "__main__":
    unittest.main()
