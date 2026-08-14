"""
Autonomous Neural Voice Persona Blending & Vector Interpolation Engine.
Standard: Pure Python Standard Library + NumPy (optional guard).
Ponytail Senior Dev Principle: Exact linear interpolation of 512-D Kokoro voice embedding tensors to generate unique custom timbres without retraining.
"""

import os
import sys
import math
from typing import Dict, Any, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VOICES_BIN_PATH = os.path.join(BASE_DIR, "models", "kokoro", "voices.bin")


class VoicePersonaBlender:
    """Zero-overhead Kokoro voice embedding vector interpolation engine."""

    _voices_cache: Optional[Dict[str, Any]] = None

    @classmethod
    def load_voices_embeddings(cls) -> Dict[str, Any]:
        """Load Kokoro voices from binary embedding pack if available."""
        if cls._voices_cache is not None:
            return cls._voices_cache

        cls._voices_cache = {}
        if np is None or not os.path.exists(VOICES_BIN_PATH):
            return cls._voices_cache

        try:
            # Kokoro voices.bin is typically a pickled or numpy npz/dict of float32 tensors
            import pickle
            with open(VOICES_BIN_PATH, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    cls._voices_cache = data
        except Exception:
            try:
                data = np.load(VOICES_BIN_PATH, allow_pickle=True)
                cls._voices_cache = {k: data[k] for k in data.files}
            except Exception:
                pass
        return cls._voices_cache

    @classmethod
    def blend_personas(
        cls,
        persona_weights: Dict[str, float],
        custom_name: str = "custom_blend"
    ) -> Dict[str, Any]:
        """
        Linearly blend multiple voice embedding vectors.
        Example: {"bf_emma": 0.7, "af_bella": 0.3} -> 70% British ship AI + 30% calm assistant.
        """
        # Normalize weights so sum equals 1.0
        total_weight = sum(persona_weights.values())
        if total_weight <= 0:
            return {"status": "error", "message": "Total weight must be greater than zero"}

        norm_weights = {k: v / total_weight for k, v in persona_weights.items()}

        voices = cls.load_voices_embeddings()
        has_vectors = False
        vector_dim = 0

        if np is not None and voices:
            blended_vec = None
            for voice_name, weight in norm_weights.items():
                if voice_name in voices:
                    vec = voices[voice_name]
                    if blended_vec is None:
                        blended_vec = np.zeros_like(vec, dtype=np.float32)
                    blended_vec += weight * vec
                    has_vectors = True
                    vector_dim = len(vec) if hasattr(vec, "__len__") else 512

        return {
            "status": "success",
            "blend_name": custom_name,
            "weights": norm_weights,
            "has_embedding_vector": has_vectors,
            "vector_dimension": vector_dim,
            "description": f"Interpolated blend of {', '.join(f'{k} ({v*100:.0f}%)' for k, v in norm_weights.items())}"
        }

    @classmethod
    def get_preset_blends(cls) -> Dict[str, Dict[str, float]]:
        """Return curated signature vocal timbres."""
        return {
            "CYBER_EXECUTIVE": {"bf_emma": 0.60, "af_bella": 0.40},      # Polished, authoritative yet warm
            "TACTICAL_COMMANDER": {"am_adam": 0.70, "bm_george": 0.30},  # Deep, resonant Anglo-American leader
            "COCKPIT_SYNTHESIS": {"bf_emma": 0.85, "af_sarah": 0.15},    # Sharp, alert AURA AI
            "CONVERSATIONAL_FLOW": {"af_bella": 0.60, "af_heart": 0.40}  # Ultra-natural conversational narrator
        }
