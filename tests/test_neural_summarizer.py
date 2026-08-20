"""
Self-check unit test suite for Phase III SOTA Knowledge Engine features:
1. Vault Instruction Fine-Tuning Dataset Synthesizer
2. Executive Audio Briefing Generator
3. Codebase AST Architecture Doctor
"""

import os
import pytest
from src.domain.dataset_synthesizer import generate_vault_instruction_dataset
from src.domain.audio_briefing import generate_audio_podcast_script
from src.domain.architecture_doctor import audit_file_architecture, audit_codebase_architecture


import unittest


class TestNeuralSummarizer(unittest.TestCase):
    def test_dataset_synthesizer(self, tmp_path=None):
        if tmp_path is None:
            import tempfile, pathlib
            _temp_dir = tempfile.TemporaryDirectory()
            tmp_path = pathlib.Path(_temp_dir.name)

        out_jsonl = str(tmp_path / "synthetic_dataset.jsonl")
        res = generate_vault_instruction_dataset(output_path=out_jsonl, limit=5)
        assert res["status"] == "success"
        if res["total_generated"] > 0:
            assert os.path.exists(out_jsonl)


    def test_audio_briefing_script(self):
        res = generate_audio_podcast_script()
        assert res["status"] == "success"
        assert "script" in res
        assert len(res["script"]) > 0


    def test_architecture_doctor(self):
        res = audit_codebase_architecture(root_dir="src/domain")
        assert res["status"] == "success"
        assert res["scanned_files"] > 0
        assert "average_architecture_health" in res
