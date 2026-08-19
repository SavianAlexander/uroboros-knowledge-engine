"""
Domain Unit Test Suite: Expanded Deep Phonetic Lexicon & Speech Normalizer Engine.
Standard: Pure Python Standard Library (unittest, re).
Enterprise Naming & Domain Protocol Guard: test_speech_normalizer_expanded.py
Referencing Tududi Task #2021.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.speech_normalizer import SpeechNormalizer, PHONETIC_ACRONYM_RULES
from src.core.voice_streaming import StreamingNeuralSynthesizer


class TestSpeechNormalizerExpanded(unittest.TestCase):
    """Verify deep phonetic expansions across AI/ML, frameworks, infra, project terms, units, and markdown."""

    def test_rule_count_exceeds_target(self):
        """Verify the compiled phonetic regex rules dictionary exceeds 100+ items."""
        self.assertGreaterEqual(len(PHONETIC_ACRONYM_RULES), 100, f"Expected 100+ rules, found {len(PHONETIC_ACRONYM_RULES)}")

    def test_ai_ml_phonetic_expansions(self):
        """Verify AI/ML terminology is phonetically expanded for human-grade pronunciation."""
        cases = [
            ("Using HNSW indexing for vector search", "H-N-S-W"),
            ("Ranked with BM25 algorithm", "B-M 25"),
            ("Combined via RRF score fusion", "R-R-F"),
            ("Powered by LLaMA model architecture", "Lah-ma"),
            ("Quantized in GGUF format", "G-G-U-F"),
            ("Exported to ONNX graph format", "on-ix"),
            ("Query formulated with HyDE", "Hyde"),
            ("Fine-tuned using LoRA weights", "Low-rah"),
            ("MoE router handles Mixtral tokens", "Mix-trul"),
            ("Inferencing on Qwen model", "Kyoo-wen"),
            ("Vector embeddings from Nomic", "Nom-ik"),
            ("Late interaction with ColBERT MaxSim", "Coal-bear"),
            ("Features extracted with TF-IDF matrix", "T-F I-D-F"),
            ("Classified with k-NN classifier", "k-N-N"),
            ("Mixture of experts MoE routing", "M-o-E"),
            ("Optimized with RLHF and DPO techniques", "R-L-H-F"),
            ("Using RoPE rotary embeddings", "Rope"),
            ("Accelerated by FlashAttention kernels", "Flash Attention"),
            ("Reflected through Self-RAG tokens", "Self-Rag"),
            ("Calculated Cosine similarity", "co-sign"),
            ("Evaluated with BLEU and ROUGE metrics", "blue"),
            ("Calculated Perplexity score", "perplexity"),
        ]
        for raw, expected in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected.lower(), norm.lower(), f"Failed on '{raw}' -> got '{norm}'")

    def test_frameworks_phonetic_expansions(self):
        """Verify framework and library pronunciations."""
        cases = [
            ("Built with FastAPI and Uvicorn", "Fast A-P-I"),
            ("Validated by Pydantic models", "Pie-dan-tik"),
            ("Bundled using Vite and Webpack", "Veet"),
            ("UI crafted in React and Next.js", "React"),
            ("Deep learning in PyTorch and TensorFlow", "Pie-Torch"),
            ("Matrix math in NumPy and Pandas", "Num-pie"),
            ("E2E tests run by Playwright", "Play-write"),
            ("Styled with TailwindCSS classes", "Tailwind C-S-S"),
            ("Compiled with Babel", "Bab-el"),
            ("Backend in Django and Flask", "Jang-go"),
            ("Model training in Scikit-learn", "Sy-kit learn"),
            ("Neural layers in Keras", "Care-as"),
            ("Graphs plotted in Matplotlib and Seaborn", "Mat-plot-lib"),
            ("Database mapped via SQLAlchemy", "sequel alchemy"),
            ("Reactive frontend in Svelte and Vue.js", "Svelt"),
            ("State managed by Redux", "Ree-dux"),
        ]
        for raw, expected in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected.lower(), norm.lower(), f"Failed on '{raw}' -> got '{norm}'")

    def test_infra_and_dev_phonetic_expansions(self):
        """Verify infrastructure, database, DevOps and security term expansions."""
        cases = [
            ("Deployed on K8s cluster", "K-eights"),
            ("Orchestrated with Kubernetes", "Kubernetes"),
            ("Microservices over gRPC with Protobuf", "G-R-P-C"),
            ("Containerized with Docker", "Dock-er"),
            ("Secured via OAuth and JWT tokens", "O-Auth"),
            ("Communicating over REST and GraphQL", "rest"),
            ("Interactive CLI and SDK tools", "C-L-I"),
            ("Automated CI/CD pipeline", "C-I C-D"),
            ("Hosted on GitHub and GitLab", "Git-Hub"),
            ("Reviewed incoming PRs", "P-Rs"),
            ("SQLite operating in WAL mode", "write ahead log"),
            ("Full-text search via FTS5 virtual table", "F-T-S five"),
            ("Relational storage in PostgreSQL", "Postgres sequel"),
            ("In-memory cache with Redis", "Red-iss"),
            ("Unique record UUID and GUID identifiers", "U-U-I-D"),
            ("Accessing resource URL and URI endpoints", "U-R-L"),
            ("Reverse proxy through Nginx and Apache", "Engine-X"),
            ("Infra as code via Terraform and Ansible", "Terra-form"),
            ("Running Linux on Ubuntu and Debian", "Linux"),
            ("Windows subsystem WSL and WSL2", "W-S-L"),
            ("Connecting over SSH with SSL and TLS", "S-S-H"),
            ("Networking via TCP, UDP, IP, and DNS", "T-C-P"),
            ("Protecting against CORS, CSRF, and XSS", "cores"),
            ("Permission model uses RBAC", "R-back"),
            ("Standard CRUD operations with ACID guarantees", "crud"),
            ("Storage benchmarked at 10000 IOPS", "eye-ops"),
            ("Multi-cloud deployments on AWS, GCP, and Azure", "A-W-S"),
        ]
        for raw, expected in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected.lower(), norm.lower(), f"Failed on '{raw}' -> got '{norm}'")

    def test_project_and_units_and_versions(self):
        """Verify project names, version strings, and engineering units."""
        cases = [
            ("Welcome to Uroboros Knowledge Engine", "Oo-roh-bor-os"),
            ("Synthesized by Kokoro neural voice", "Koh-koh-roh"),
            ("Tracked in Tududi Task Master", "Too-doo-dee"),
            ("Configured in Antigravity IDE", "Anti-gravity"),
            ("Upgraded to v1.0.0 and v2.4", "version 1 point 0 point 0"),
            ("Search completed in 15ms latency", "15 milliseconds"),
            ("Processor clocked at 4.2GHz and 800MHz", "4.2 gigahertz"),
            ("Consuming 500MB RAM and 2GB VRAM", "500 megabytes"),
            ("Generating 120 tok/s throughput", "120 tokens per second"),
            ("Handling 300 QPS query rate", "300 queries per second"),
            ("Rendered at 60 fps smoothly", "60 frames per second"),
            ("Network bandwidth 10Gbps link", "10 gigabits per second"),
        ]
        for raw, expected in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected.lower(), norm.lower(), f"Failed on '{raw}' -> got '{norm}'")

    def test_code_block_and_markdown_sanitization(self):
        """Verify code blocks and markdown syntax are cleanly converted into spoken summaries."""
        raw_code = "Here is the function:\n```python\ndef calculate_loss(features, targets) -> float:\n    return sum(features)\n```\nDone."
        norm = SpeechNormalizer.normalize_for_speech(raw_code)
        self.assertIn("code snippet", norm.lower())
        self.assertIn("defining function calculate loss", norm.lower())
        self.assertNotIn("```", norm)

        raw_md = "## Architecture\nCheck **[Documentation](https://example.com)** for `fastapi` details. <think>Secret reasoning</think>"
        norm_md = SpeechNormalizer.normalize_for_speech(raw_md)
        self.assertNotIn("think", norm_md.lower())
        self.assertNotIn("https://", norm_md)
        self.assertNotIn("##", norm_md)
        self.assertNotIn("**", norm_md)
        self.assertIn("Fast A-P-I", norm_md)

    def test_currency_and_numbers_expansion(self):
        """Verify currency values are converted to spoken words."""
        cases = [
            ("Project budget is $15,000 allocated", "fifteen thousand dollars"),
            ("Valuation reached $2.5B in 2026", "2.5 billion dollars"),
            ("Monthly revenue is $500k", "500 thousand dollars"),
            ("Exact charge was $125.50 on invoice", "one hundred twenty-five dollars and fifty cents"),
        ]
        for raw, expected in cases:
            norm = SpeechNormalizer.normalize_for_speech(raw)
            self.assertIn(expected.lower(), norm.lower(), f"Failed on '{raw}' -> got '{norm}'")

    def test_acoustic_clause_streaming_splitting(self):
        """Verify clause splitter creates coherent sentences without choppy cadence."""
        long_text = "The neural engine boots within milliseconds. Next, the SQLite WAL mode enables concurrent readers. Finally, the HNSW vector index serves queries."
        clauses = StreamingNeuralSynthesizer.split_into_acoustic_clauses(long_text)
        self.assertGreaterEqual(len(clauses), 2)
        for clause in clauses:
            self.assertTrue(clause.strip().endswith((".", "!", "?")), f"Clause does not end cleanly: {clause}")


if __name__ == "__main__":
    unittest.main()
