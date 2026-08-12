import unittest
from src.domain.smart_filter import parse_natural_language_filter

class TestSmartFilter(unittest.TestCase):
    def test_parses_extension_tag_and_size(self):
        query = "pdf files tagged architecture size > 1mb"
        parsed = parse_natural_language_filter(query)
        self.assertEqual(parsed["filters"]["ext"], "pdf")
        self.assertEqual(parsed["filters"]["tag"], "architecture")
        self.assertEqual(parsed["filters"]["size_op"], ">")
        self.assertEqual(parsed["filters"]["size_bytes"], 1048576)

if __name__ == "__main__":
    unittest.main()
