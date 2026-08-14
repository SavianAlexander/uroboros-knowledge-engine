"""
Autonomous EVE Online Full-Duplex Voice Activity Detection (VAD) & Barge-In Controller.
Standard: Pure Python Standard Library + NumPy.
Ponytail Senior Dev Principle: Zero-latency RMS/ZCR speech state machine enabling instantaneous barge-in voice interruption.
"""

import os
import sys
import numpy as np
import time
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class VoiceActivityDetector:
    """Zero-dependency real-time Voice Activity Detection (VAD) and Barge-In Controller."""

    def __init__(
        self,
        sample_rate: int = 24000,
        frame_duration_ms: int = 20,
        energy_threshold: float = 0.015,
        zcr_threshold: float = 0.01
    ):
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        self.energy_threshold = energy_threshold
        self.zcr_threshold = zcr_threshold

        # State tracking
        self.current_state = "IDLE"  # IDLE, USER_SPEAKING, AI_SPEAKING, BARGE_IN_TRIGGERED
        self.consecutive_speech_frames = 0
        self.consecutive_silence_frames = 0
        self.vad_history: List[Dict[str, Any]] = []

    def set_ai_speaking_state(self, is_speaking: bool):
        """Notify VAD detector whether AI synthesis is actively playing out audio."""
        if is_speaking and self.current_state != "USER_SPEAKING":
            self.current_state = "AI_SPEAKING"
        elif not is_speaking and self.current_state == "AI_SPEAKING":
            self.current_state = "IDLE"

    def calculate_frame_metrics(self, frame_samples: np.ndarray) -> Tuple[float, float, bool]:
        """Calculate RMS Energy and Zero Crossing Rate (ZCR) of audio frame."""
        if len(frame_samples) == 0:
            return 0.0, 0.0, False

        # 1. RMS Energy
        rms = float(np.sqrt(np.mean(frame_samples ** 2)))
        # 2. Zero Crossing Rate
        zero_crossings = np.sum(np.abs(np.diff(np.sign(frame_samples)))) / (2.0 * len(frame_samples))
        # Speech decision rule
        is_speech = (rms > self.energy_threshold) and (zero_crossings > self.zcr_threshold)
        return rms, float(zero_crossings), is_speech

    def process_audio_frame(self, frame_samples: np.ndarray) -> Dict[str, Any]:
        """
        Process single 20ms audio frame and evaluate barge-in state transition.
        """
        rms, zcr, is_speech = self.calculate_frame_metrics(frame_samples)
        barge_in_event = False

        if is_speech:
            self.consecutive_speech_frames += 1
            self.consecutive_silence_frames = 0
        else:
            self.consecutive_silence_frames += 1
            self.consecutive_speech_frames = 0

        # State Machine Transitions
        if self.current_state == "AI_SPEAKING" and self.consecutive_speech_frames >= 3:
            # User interrupted AI speech!
            self.current_state = "BARGE_IN_TRIGGERED"
            barge_in_event = True
        elif self.consecutive_speech_frames >= 3:
            self.current_state = "USER_SPEAKING"
        elif self.consecutive_silence_frames >= 8:
            self.current_state = "IDLE"

        report = {
            "timestamp": time.time(),
            "state": self.current_state,
            "rms_energy": round(rms, 4),
            "zcr": round(zcr, 4),
            "is_speech": is_speech,
            "barge_in_triggered": barge_in_event
        }

        self.vad_history.append(report)
        return report
