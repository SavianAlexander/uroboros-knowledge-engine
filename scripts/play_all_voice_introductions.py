"""
Live Synchronous Voice Persona Showcase & WAV Exporter.
Standard: Pure Python Standard Library (winsound, os, sys, time, io).
Ponytail Senior Dev Principle: Synchronous foreground playback + WAV file export ensuring complete playback through Windows default audio device without daemon thread cutoffs.
"""

import os
import sys
import time
import winsound

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_engine import KokoroVoiceEngine
from src.core.voice_dsp import VoiceDSP
from src.core.voice_normalizer import VoiceNormalizer

SHOWCASE_DIR = os.path.join(BASE_DIR, "vault", "audio_showcase")
os.makedirs(SHOWCASE_DIR, exist_ok=True)

PERSONA_PRESENTATIONS = [
    (
        "AURA_SHIP_AI",
        "bf_emma",
        "TRANSCENDENTAL_AURA",
        "Greetings Commander. I am Aura, your shipboard neural intelligence. I monitor starship defensive shields, warp envelope harmonics, and navigational telemetry across New Eden."
    ),
    (
        "FLEET_COMMANDER",
        "am_adam",
        "SOVEREIGN_PRESENCE",
        "Fleet Commander speaking. I coordinate sovereign battle wings, cynosural jump bridges, and capital fleet engagements. Anchor on the flagship and prepare for warp."
    ),
    (
        "TACTICAL_ADVISOR",
        "af_sarah",
        "COMMANDER_TACTICAL",
        "Tactical Advisor standing by. I deliver rapid combat intelligence, threat interception scans, and warp disruption telemetry with zero latency."
    ),
    (
        "INDUSTRY_OVERSEER",
        "bm_george",
        "AWE_STUDIO_MASTER",
        "Industry Overseer reporting. I manage deep-space mining fleets, planetary reactions, and industrial ore compression aboard the Pillar of Autumn in G-EURJ."
    ),
    (
        "CALM_OPERATIONS",
        "af_bella",
        "STUDIO_DIRECT",
        "Calm Operations active. I manage background database indexing, system vitals, and continuous integration pipelines with quiet, uninterrupted precision."
    ),
    (
        "EXECUTIVE_DIRECTOR",
        "af_heart",
        "SOVEREIGN_PRESENCE",
        "Executive Director here. I analyze high-level strategic intelligence, asset reserves, and organizational milestones across all active operational projects."
    ),
    (
        "WARP_NAVIGATOR",
        "bf_isabella",
        "TRANSCENDENTAL_AURA",
        "Warp Navigator online. Plotting celestial transit vectors and safe navigational routes through Jita 4-4 and nullsec stargate perimeters."
    ),
    (
        "SOVEREIGN_ORACLE",
        "af_sky",
        "SOVEREIGN_PRESENCE",
        "I am the Sovereign Oracle. I certify deterministic truth, canonical game physics, and immutable cryptographic audit hashchains with zero assumptions."
    )
]


def play_all_showcase_synchronously():
    print("\n" + "=" * 70)
    print("🎙️ STARTING SYNCHRONOUS NEURAL VOICE LIVE AUDITION SHOWCASE")
    print("=" * 70 + "\n")

    engine = KokoroVoiceEngine()

    for i, (name, voice_id, dsp_preset, intro_text) in enumerate(PERSONA_PRESENTATIONS, 1):
        print(f"[{i}/{len(PERSONA_PRESENTATIONS)}] 🗣️ Speaking: {name}")
        print(f"    • Voice Profile : {voice_id}")
        print(f"    • Acoustic DSP  : {dsp_preset}")
        print(f"    • Script        : \"{intro_text}\"")

        # 1. Synthesize with exact voice profile and DSP mastering
        audio_bytes = engine.synthesize_neural_audio(
            text=intro_text,
            voice=voice_id,
            speed=1.0,
            dsp_preset=dsp_preset
        )

        if audio_bytes:
            # 2. Save WAV file for permanent access
            wav_path = os.path.join(SHOWCASE_DIR, f"{i}_{name}.wav")
            with open(wav_path, "wb") as f:
                f.write(audio_bytes)
            print(f"    • Exported WAV  : {wav_path} ({len(audio_bytes)} bytes)")

            # 3. Synchronous foreground playback through active headset
            print(f"    • Playing audio live to headset (Speakers onn Wired Gaming Headset)...")
            try:
                import sounddevice as sd
                import soundfile as sf
                import io
                data, fs = sf.read(io.BytesIO(audio_bytes))
                sd.play(data, fs)
                sd.wait()
            except Exception as e:
                import winsound
                winsound.PlaySound(audio_bytes, winsound.SND_MEMORY)
            print("    • Playback complete.\n")
        else:
            print("    • [Error]: Failed to synthesize audio bytes.\n")

        time.sleep(0.8)

    print("=" * 70)
    print("🎉 ALL 8 NEURAL VOICE PERSONAS HAVE INTRODUCED THEMSELVES LIVE")
    print(f"📁 All WAV recordings saved in: {SHOWCASE_DIR}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    play_all_showcase_synchronously()
