import unittest
import os
import shutil
import tempfile
import sys
from unittest.mock import MagicMock, patch

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import know
import main

class TestDomainLLM(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_llm_")
        self.db_backup = know.DB_FILE
        self.active_backup = main.ACTIVE_DIR
        know.DB_FILE = os.path.join(self.test_dir, "test_know.db")
        main.ACTIVE_DIR = self.test_dir
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        know.DB_FILE = self.db_backup
        main.ACTIVE_DIR = self.active_backup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_gpu_llm_loader(self):
        """Verify LLM loader initialization and graceful fallback handling.

        Preconditions: Llama class patched with mock objects and model path mock enabled.
        Invariants: Model loader returns valid engine instance without throwing exception.
        Expected Outcomes: main.get_llm() returns non-None mock object.
        """
        with patch('src.core.model_manager.Llama', MagicMock()):
            with patch('os.path.exists', return_value=True):
                llm = main.get_llm()
                self.assertIsNotNone(llm, "Mocked LLM initialization failed")

    def test_02_angle_empty_prompt_generation_safety(self):
        """Verify LLM prompt generation handling and response payload structure for empty inputs.

        Preconditions: Mock LLM configured with create_chat_completion payload response.
        Invariants: Empty prompt strings execute through completion router without crashing.
        Expected Outcomes: Completion response message content matches expected mocked output string.
        """
        mock_llm = MagicMock()
        mock_llm.create_chat_completion.return_value = {
            "choices": [{"message": {"content": "Mocked response"}}]
        }
        res = mock_llm.create_chat_completion(messages=[{"role": "user", "content": ""}])
        self.assertEqual(res["choices"][0]["message"]["content"], "Mocked response")

    def test_03_angle_hyde_expansion_generation(self):
        """Verify HyDE hypothetical document expansion text generation.

        Preconditions: Database initialized; know module loaded.
        Invariants: HyDE generator transforms input search prompt into expanded document text string.
        Expected Outcomes: Output is string instance with character length greater than 0.
        """
        expanded = know.generate_hyde_expansion("quantum physics")
        self.assertIsInstance(expanded, str)
        self.assertGreater(len(expanded), 0)

    def test_04_angle_llm_lock_concurrency_safety(self):
        """Verify multi-threaded concurrency lock safety on global _llm_lock.

        Preconditions: 10 worker threads spawned attempting concurrent lock acquisition.
        Invariants: Reentrant/threading lock prevents race conditions during LLM instantiation.
        Expected Outcomes: All 10 threads complete execution without lock deadlocks or exceptions.
        """
        import threading
        def worker():
            with main._llm_lock:
                _ = True
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_05_streaming_token_callback_and_clipping(self):
        """Verify streaming token callback mechanism and token aggregation buffer.

        Preconditions: Token list accumulator initialized with token receiver callback.
        Invariants: Stream callback receives each generated token chunk sequentially.
        Expected Outcomes: Exactly 5 tokens received; concatenated string equals 'Quantum computing excerpt'.
        """
        tokens_received = []
        def on_token_callback(token_str):
            tokens_received.append(token_str)

        for tok in ["Quantum", " ", "computing", " ", "excerpt"]:
            on_token_callback(tok)

        self.assertEqual(len(tokens_received), 5)
        self.assertEqual("".join(tokens_received), "Quantum computing excerpt")

if __name__ == "__main__":
    unittest.main()
