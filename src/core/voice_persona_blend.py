"""
Autonomous Neural Voice Persona Blending & Vector Interpolation Engine.
Standard: Pure Python Standard Library + NumPy (optional guard).
Ponytail Senior Dev Principle: Exact linear interpolation of 512-D Kokoro voice embedding tensors to generate unique custom timbres without retraining.
"""

import os
import sys
import math
import time
from typing import Dict, Any, List, Optional, Tuple


try:
    import numpy as np
except ImportError:
    np = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VOICES_BIN_PATH = os.path.join(BASE_DIR, "models", "kokoro", "voices.bin")
VOICES_JSON_PATH = os.path.join(BASE_DIR, "models", "kokoro", "voices.json")

# Signature Curated Vocal Timbre Persona Blends
SIGNATURE_PERSONA_BLENDS: Dict[str, Dict[str, float]] = {
    # Sovereign Legendary Personas (Awe & Gravitas)
    "ALEXANDER_SOVEREIGN": {"am_adam": 0.70, "bm_george": 0.20, "am_michael": 0.10},  # Commanding Imperator: Deep baritone, chest thump & magnetic authority
    "FREYA_VALKYRIE": {"bf_emma": 0.60, "af_sarah": 0.25, "af_bella": 0.15},          # Resolute Commander: Powerful, impassioned, crystalline noble authority
    "AURELIUS_STOIC": {"am_adam": 0.80, "bm_lewis": 0.20},                             # Philosopher Emperor / Kratos Gravitas: Visceral sub-bass thump & unshakable wisdom
    "NOCTURNA_SOLON": {"bm_george": 0.65, "am_adam": 0.35},                           # Shadow Strategist / Big Boss Aura: Textured, weathered operative authority
    
    # Classic AI & Signature Personas
    "CORTANA_PRIME": {"af_sky": 0.60, "af_bella": 0.25, "af_sarah": 0.15},            # Articulate, crystalline, warm Cortana AI
    "AURA_SHIP_AI": {"bf_emma": 0.85, "bf_isabella": 0.15},                           # British crystalline starship bridge AI
    "EXECUTIVE_ADVISOR": {"af_bella": 0.70, "af_nicole": 0.30},                       # Warm, engaging productivity & executive tone
    "TACTICAL_OFFICER": {"am_adam": 0.70, "bm_george": 0.30},                         # Deep, resonant tactical commander
    "CYBER_EXECUTIVE": {"bf_emma": 0.60, "af_bella": 0.40},                            # Polished, authoritative executive assistant
    "TACTICAL_COMMANDER": {"am_adam": 0.70, "bm_george": 0.30},                       # Deep resonant leader
    "COCKPIT_SYNTHESIS": {"bf_emma": 0.85, "af_sarah": 0.15},                          # Sharp, alert AURA AI
    "CONVERSATIONAL_FLOW": {"af_bella": 0.60, "af_sky": 0.40}                          # Ultra-natural conversational narrator
}

CUSTOM_PERSONAS_FILE = os.path.join(BASE_DIR, "data", "custom_voice_personas.json")



class VoicePersonaBlender:
    """Zero-overhead Kokoro voice embedding vector interpolation engine."""

    _voices_cache: Optional[Dict[str, Any]] = None
    _blends_cache: Dict[str, Any] = {}

    @classmethod
    def _try_load_voices_json(cls, path: str) -> Optional[Dict[str, Any]]:
        """Attempt to load voices embedding dictionary from JSON format."""
        if not os.path.exists(path):
            return None
        try:
            import json
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            if isinstance(raw_data, dict):
                return {k: np.array(v, dtype=np.float32) for k, v in raw_data.items()}
        except Exception:
            pass
        return None

    @classmethod
    def _try_load_voices_bin(cls, path: str) -> Optional[Dict[str, Any]]:
        """Attempt to load voices embedding dictionary from binary pickle or npz format."""
        if not os.path.exists(path):
            return None
        try:
            import pickle
            with open(path, "rb") as f:
                data = pickle.load(f)
            if isinstance(data, dict):
                return {
                    k: (np.array(v, dtype=np.float32) if not isinstance(v, np.ndarray) else v)
                    for k, v in data.items()
                }
        except Exception:
            pass
        try:
            data = np.load(path, allow_pickle=True)
            return {k: np.array(data[k], dtype=np.float32) for k in data.files}
        except Exception:
            pass
        return None

    @classmethod
    def load_voices_embeddings(cls) -> Dict[str, Any]:
        """Load Kokoro voices from JSON or binary embedding pack with caching."""
        if cls._voices_cache is not None:
            return cls._voices_cache

        cls._voices_cache = {}
        if np is None:
            return cls._voices_cache

        if json_cache := cls._try_load_voices_json(VOICES_JSON_PATH):
            cls._voices_cache = json_cache
            return cls._voices_cache

        if bin_cache := cls._try_load_voices_bin(VOICES_BIN_PATH):
            cls._voices_cache = bin_cache
            return cls._voices_cache

        return cls._voices_cache

    @classmethod
    def get_blended_vector(cls, persona_or_weights: Any) -> Optional[Any]:
        """
        Get or compute a blended embedding vector (np.ndarray of shape (511, 1, 256))
        for passing directly into kokoro.create(voice=vector).
        """
        if np is None:
            return None

        # If already a numpy array, return directly
        if isinstance(persona_or_weights, np.ndarray):
            return persona_or_weights

        voices = cls.load_voices_embeddings()
        if not voices:
            return None

        # Check if single base voice name
        if isinstance(persona_or_weights, str):
            clean_key = persona_or_weights.strip()
            # Check cached computed blends
            if clean_key in cls._blends_cache:
                return cls._blends_cache[clean_key]
            # Check preset signature blends
            upper_key = clean_key.upper()
            if upper_key in SIGNATURE_PERSONA_BLENDS:
                weights = SIGNATURE_PERSONA_BLENDS[upper_key]
                vec = cls.calculate_blend_tensor(weights, voices)
                if vec is not None:
                    cls._blends_cache[clean_key] = vec
                    cls._blends_cache[upper_key] = vec
                    return vec
            # Check direct base voice
            if clean_key in voices:
                return voices[clean_key]
            # Fallback check
            if "af_sky" in voices:
                return voices["af_sky"]
            return None

        # If dictionary of weights
        if isinstance(persona_or_weights, dict):
            return cls.calculate_blend_tensor(persona_or_weights, voices)

        return None

    # Alias for tensor access
    get_persona_tensor = get_blended_vector


    @classmethod
    def calculate_blend_tensor(cls, persona_weights: Dict[str, float], voices: Dict[str, Any]) -> Optional[Any]:
        """Linearly interpolate voice embedding tensors using normalized weights."""
        if not persona_weights or not voices or np is None:
            return None

        total_weight = sum(persona_weights.values())
        if total_weight <= 0:
            return None

        norm_weights = {k: v / total_weight for k, v in persona_weights.items()}
        blended_vec = None

        for voice_name, weight in norm_weights.items():
            if voice_name in voices:
                vec = voices[voice_name]
                if blended_vec is None:
                    blended_vec = np.zeros_like(vec, dtype=np.float32)
                blended_vec += float(weight) * vec

        return blended_vec

    @classmethod
    def blend_personas(
        cls,
        persona_weights: Dict[str, float],
        custom_name: str = "custom_blend"
    ) -> Dict[str, Any]:
        """
        Linearly blend multiple voice embedding vectors.
        Example: {"af_sky": 0.6, "af_bella": 0.25, "af_sarah": 0.15} -> Cortana Prime.
        """
        total_weight = sum(persona_weights.values())
        if total_weight <= 0:
            return {"status": "error", "message": "Total weight must be greater than zero"}

        norm_weights = {k: v / total_weight for k, v in persona_weights.items()}
        voices = cls.load_voices_embeddings()
        blended_vec = cls.calculate_blend_tensor(norm_weights, voices)

        has_vectors = blended_vec is not None
        vector_dim = len(blended_vec) if has_vectors and hasattr(blended_vec, "__len__") else 0

        if has_vectors and custom_name:
            cls._blends_cache[custom_name] = blended_vec

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
        all_blends = dict(SIGNATURE_PERSONA_BLENDS)
        all_blends.update(cls.load_custom_personas())
        return all_blends

    @classmethod
    def load_custom_personas(cls) -> Dict[str, Dict[str, Any]]:
        """Load user-saved custom personas from disk."""
        if not os.path.exists(CUSTOM_PERSONAS_FILE):
            return {}
        try:
            import json
            with open(CUSTOM_PERSONAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def save_custom_persona(
        cls,
        name: str,
        weights: Dict[str, float],
        dsp_preset: str = "SOVEREIGN_AWE",
        description: str = ""
    ) -> Dict[str, Any]:
        """Save a new custom persona persistently to disk and cache."""
        import json
        clean_name = name.strip().upper().replace(" ", "_")
        existing = cls.load_custom_personas()
        
        persona_record = {
            "name": name.strip(),
            "id": clean_name,
            "weights": weights,
            "dsp_preset": dsp_preset,
            "description": description or f"Custom sovereign blend of {', '.join(weights.keys())}",
            "created_at": time.time()
        }
        
        existing[clean_name] = persona_record
        os.makedirs(os.path.dirname(CUSTOM_PERSONAS_FILE), exist_ok=True)
        with open(CUSTOM_PERSONAS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
            
        # Re-blend into memory cache
        cls.blend_personas(weights, custom_name=clean_name)
        return {"status": "success", "persona": persona_record}

    @classmethod
    def delete_custom_persona(cls, persona_id: str) -> bool:
        """Delete a custom persona from disk and cache."""
        import json
        clean_id = persona_id.strip().upper().replace(" ", "_")
        existing = cls.load_custom_personas()
        if clean_id in existing:
            del existing[clean_id]
            os.makedirs(os.path.dirname(CUSTOM_PERSONAS_FILE), exist_ok=True)
            with open(CUSTOM_PERSONAS_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
            cls._blends_cache.pop(clean_id, None)
            return True
        return False


