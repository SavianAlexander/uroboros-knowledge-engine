"""
Unit and Integration Test Suite for Hardware Audio & Voice HUD Calibration.
Standard: Pure Python standard library with unittest/pytest assertions.
"""

import os
import sys
import unittest

# Ensure root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.calibrate_audio_hardware import (
    generate_synthetic_pcm_frame,
    calibrate_ambient_noise_floor,
    benchmark_vad_streaming_and_barge_in,
    run_full_audio_calibration
)


class TestAudioHardwareCalibration(unittest.TestCase):
    """Test suite verifying audio calibration and real-time VAD preemption."""

    def test_generate_synthetic_pcm_frame(self):
        frame = generate_synthetic_pcm_frame(sample_rate=24000, duration_ms=20, frequency=440.0)
        self.assertIsInstance(frame, bytes)
        # 24000 samples/sec * 0.02 sec * 2 bytes/sample = 960 bytes
        self.assertEqual(len(frame), 960)

    def test_calibrate_ambient_noise_floor(self):
        cal = calibrate_ambient_noise_floor(sample_frames=20)
        self.assertEqual(cal["benchmark"], "ambient_noise_calibration")
        self.assertGreater(cal["calibrated_energy_threshold"], 0.0)
        self.assertGreater(cal["calibrated_zcr_threshold"], 0.0)
        self.assertGreater(cal["elapsed_calibration_ms"], 0.0)

    def test_benchmark_vad_streaming_and_barge_in(self):
        vad_res = benchmark_vad_streaming_and_barge_in()
        self.assertEqual(vad_res["benchmark"], "vad_barge_in_verification")
        self.assertTrue(vad_res["sub_millisecond_processing"])
        self.assertTrue(vad_res["barge_in_executed"])
        self.assertTrue(vad_res["silence_endpoint_triggered"])
        self.assertGreaterEqual(vad_res["silence_hangover_measured_ms"], 400.0)

    def test_run_full_audio_calibration(self):
        scorecard = run_full_audio_calibration()
        self.assertEqual(scorecard["status"], "PASS")
        self.assertIn("ambient_noise_calibration", scorecard)
        self.assertIn("vad_and_barge_in_metrics", scorecard)


if __name__ == "__main__":
    unittest.main()
