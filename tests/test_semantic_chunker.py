import unittest
from src.core.domain.services import chunk_text

class TestSemanticChunker(unittest.TestCase):
    def test_markdown_table_preserved_in_chunk(self):
        markdown_content = (
            "# Document Title\n\n"
            "Introductory text.\n\n"
            "| Column A | Column B |\n"
            "| --- | --- |\n"
            "| Value 1 | Value 2 |\n"
            "| Value 3 | Value 4 |\n\n"
            "## Section 2\n\n"
            "Section 2 content details."
        )
        chunks = chunk_text(markdown_content, chunk_size=100)
        self.assertTrue(len(chunks) >= 2)
        # Verify table lines are kept intact in the same chunk
        table_chunk = [c for c in chunks if "| Column A |" in c][0]
        self.assertIn("| Value 1 | Value 2 |", table_chunk)
        self.assertIn("| Value 3 | Value 4 |", table_chunk)

if __name__ == "__main__":
    unittest.main()
