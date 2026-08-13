"""
Next-Gen Non-Scale RAG Frontiers Verification Suite.
Covers Voice Memo Search, Interactive Graph Topology, Zero-Latency Speculative Streamer, and Executive Briefing Generator.
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from src.domain.voice_rag import transcribe_and_search_voice_memo
from src.domain.graph_explorer import generate_graph_topology
from src.domain.speculative_streamer import generate_speculative_stream_chunks
from src.domain.executive_briefing import generate_executive_briefing


class TestNextGenNonScaleSupremacy(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_voice_memo_search(self):
        res = transcribe_and_search_voice_memo("GPU cluster setup architecture guide", top_k=5)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["transcribed_text"], "GPU cluster setup architecture guide")
        self.assertGreater(res["confidence_score"], 0.90)

    def test_02_graph_topology_explorer(self):
        res = generate_graph_topology()
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["node_count"], 0)
        self.assertGreater(res["edge_count"], 0)

    def test_03_speculative_streamer(self):
        response_text = "Quantum computing allows parallel evaluation of multiple state vectors simultaneously."
        chunks = generate_speculative_stream_chunks("prompt", response_text)
        self.assertGreater(len(chunks), 0)
        self.assertIn("speculative_preview", chunks[0])

    def test_04_executive_briefing(self):
        chunks = ["Document section 1 content.", "Document section 2 content."]
        res = generate_executive_briefing(chunks, title="Q3 Technical Briefing")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["title"], "Q3 Technical Briefing")
        self.assertGreater(len(res["action_items"]), 0)

    def test_05_voice_search_endpoint(self):
        payload = {"audio_transcript_payload": "Neural network optimization", "top_k": 5}
        res = self.client.post("/api/rag/voice/search", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_06_graph_topology_endpoint(self):
        payload = {"source_documents": [{"id": "doc1", "title": "Doc 1"}]}
        res = self.client.post("/api/rag/graph/topology", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_07_speculative_stream_endpoint(self):
        payload = {"prompt": "p", "base_response": "Streamed token response text."}
        res = self.client.post("/api/rag/stream/speculative", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    def test_08_executive_briefing_endpoint(self):
        payload = {"document_chunks": ["Chunk 1 content."], "title": "Summary Title"}
        res = self.client.post("/api/rag/briefing/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")


if __name__ == "__main__":
    unittest.main()
