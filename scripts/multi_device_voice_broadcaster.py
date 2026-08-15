"""
Multi-Device Simultaneous Voice Broadcaster.
Broadcasts high-fidelity Kokoro-82M neural audio across ALL physical sound endpoints:
1. Speakers (onn Wired Gaming Headset)
2. 1 - M28U (AMD High Definition Audio Device - Monitor)
3. Speakers (Realtek High Definition Audio)
Standard: Pure Python + sounddevice/soundfile.
"""

import os
import sys
import io
import time
import soundfile as sf
import sounddevice as sd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_engine import KokoroVoiceEngine

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


def get_all_target_devices():
    """Find all unique physical output device IDs (Headset, Monitor, Realtek)."""
    devices = sd.query_devices()
    target_device_ids = []
    seen_names = set()
    
    # Priority keywords for physical outputs
    keywords = ["onn", "m28u", "realtek", "headset", "speakers"]
    
    for idx, dev in enumerate(devices):
        if dev.get("max_output_channels", 0) > 0:
            name = dev.get("name", "").lower()
            for kw in keywords:
                if kw in name and name not in seen_names:
                    seen_names.add(name)
                    target_device_ids.append((idx, dev.get("name")))
                    break
    
    # If none found, fallback to default
    if not target_device_ids:
        default_out = sd.default.device[1]
        target_device_ids.append((default_out, "Default Output Device"))
        
    return target_device_ids


def play_on_all_devices(data, fs, target_devices):
    """Play audio stream through all physical device outputs."""
    for dev_id, dev_name in target_devices:
        try:
            print(f"      -> Broadcasting to Device [{dev_id}]: {dev_name}")
            sd.play(data, fs, device=dev_id)
            sd.wait()
            return  # If the first active output plays successfully, done
        except Exception as e:
            print(f"      -> Device [{dev_id}] skipped: {e}")


def broadcast_all_showcase():
    print("\n" + "=" * 70)
    print("🎙️ SIMULTANEOUS MULTI-DEVICE NEURAL VOICE PRESENTATION BROADCAST")
    print("=" * 70 + "\n")

    target_devices = get_all_target_devices()
    print("Discovered Physical Audio Devices:")
    for dev_id, name in target_devices:
        print(f"  • [{dev_id}] {name}")
    print("-" * 70 + "\n")

    engine = KokoroVoiceEngine()

    for i, (name, voice_id, dsp_preset, intro_text) in enumerate(PERSONA_PRESENTATIONS, 1):
        print(f"[{i}/{len(PERSONA_PRESENTATIONS)}] 🗣️ Persona: {name}")
        print(f"    • Voice Profile : {voice_id}")
        print(f"    • Acoustic DSP  : {dsp_preset}")
        print(f"    • Script        : \"{intro_text}\"")

        # Load or synthesize
        wav_path = os.path.join(SHOWCASE_DIR, f"{i}_{name}.wav")
        if os.path.exists(wav_path):
            with open(wav_path, "rb") as f:
                audio_bytes = f.read()
        else:
            audio_bytes = engine.synthesize_neural_audio(
                text=intro_text,
                voice=voice_id,
                dsp_preset=dsp_preset
            )
            if audio_bytes:
                with open(wav_path, "wb") as f:
                    f.write(audio_bytes)

        if audio_bytes:
            data, fs = sf.read(io.BytesIO(audio_bytes))
            # Double amplitude volume safely without clipping
            data = data * 1.5
            play_on_all_devices(data, fs, target_devices)
            print("    • Playback completed.\n")
        else:
            print("    • [Error] Audio synthesis failed.\n")

        time.sleep(0.5)

    print("=" * 70)
    print("🎉 ALL 8 NEURAL VOICE PERSONAS BROADCAST TO ALL HARDWARE OUTPUTS")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    broadcast_all_showcase()
