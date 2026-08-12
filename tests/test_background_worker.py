import unittest
from src.domain.background_worker import DocumentSummarizerDaemon

class TestBackgroundWorker(unittest.TestCase):
    def test_daemon_instantiation_and_lifecycle(self):
        daemon = DocumentSummarizerDaemon(interval_seconds=100)
        self.assertFalse(daemon.is_alive())
        daemon.stop()
        self.assertFalse(daemon._running)

if __name__ == "__main__":
    unittest.main()
