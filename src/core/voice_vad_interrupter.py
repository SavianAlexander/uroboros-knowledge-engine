"""
Real-Time Voice Activity Detection (VAD) & Instant Barge-In Interrupter.
Standard: Pure Python Standard Library + NumPy.
Ponytail Senior Dev Principle: Sub-1ms audio interruption state machine with zero external binary dependencies.
"""

import os
import sys
import time
import math
from typing import Dict, Any, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class VoiceActivityInterrupter:
    """Real-time VAD speech detector and barge-in audio cut controller."""

    def __init__(
        self,
        sample_rate: int = 24000,
        frame_duration_ms: int = 20,
        energy_threshold: float = 0.018,
        zcr_threshold: float = 0.015,
        consecutive_frames_to_trigger: int = 3
    ):
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        self.energy_threshold = energy_threshold
        self.zcr_threshold = zcr_threshold
        self.consecutive_frames_to_trigger = consecutive_frames_to_trigger

        self.consecutive_speech_count = 0
        self.is_interrupted = False
        self.last_interruption_time: Optional[float] = None

    def analyze_frame(self, frame_samples) -> Dict[str, Any]:
        """Analyze a 20ms audio frame for user voice activity."""
        if np is not None and isinstance(frame_samples, np.ndarray):
            if len(frame_samples) == 0:
                return {"is_speech": False, "rms": 0.0, "zcr": 0.0}
            rms = float(np.sqrt(np.mean(frame_samples ** 2)))
            zcr = float(np.sum(np.abs(np.diff(np.sign(frame_samples)))) / (2.0 * len(frame_samples)))
        elif isinstance(frame_samples, (list, tuple, bytes, bytearray)):
            if len(frame_samples) == 0:
                return {"is_speech": False, "rms": 0.0, "zcr": 0.0}
            # Convert bytes or list to float samples
            if isinstance(frame_samples, (bytes, bytearray)):
                import struct
                count = len(frame_samples) // 2
                ints = struct.unpack(f'<{count}h', frame_samples[:count * 2])
                samples = [x / 32768.0 for x in ints]
            else:
                samples = frame_samples
            rms = math.sqrt(sum(x ** 2 for x in samples) / len(samples))
            zero_crossings = 0
            for i in range(1, len(samples)):
                if (samples[i] >= 0 and samples[i - 1] < 0) or (samples[i] < 0 and samples[i - 1] >= 0):
                    zero_crossings += 1
            zcr = zero_crossings / (2.0 * len(samples))
        else:
            return {"is_speech": False, "rms": 0.0, "zcr": 0.0}

        is_speech = (rms >= self.energy_threshold) and (zcr >= self.zcr_threshold)

        if is_speech:
            self.consecutive_speech_count += 1
        else:
            self.consecutive_speech_count = max(0, self.consecutive_speech_count - 1)

        barge_in_triggered = False
        if self.consecutive_speech_count >= self.consecutive_frames_to_trigger:
            barge_in_triggered = True
            self.is_interrupted = True
            self.last_interruption_time = time.time()

        return {
            "is_speech": is_speech,
            "rms_energy": round(rms, 4),
            "zcr": round(zcr, 4),
            "speech_frame_streak": self.consecutive_speech_count,
            "barge_in_triggered": barge_in_triggered
        }

    @classmethod
    def execute_instant_barge_in(cls) -> Dict[str, Any]:
        """Instantly halt active speech playback and clear pending audio queues."""
        t0 = time.time()
        purged = False
        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
                purged = True
            except Exception:
                pass

        # Clear voice copilot audio queue
        try:
            from src.core.voice_bridge import VoiceBridge
            copilot = VoiceBridge.get_copilot()
            if copilot:
                copilot.audio_queue.clear_pending()
        except Exception:
            pass

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        return {
            "status": "barge_in_executed",
            "audio_purged": purged,
            "interruption_latency_ms": elapsed_ms,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
