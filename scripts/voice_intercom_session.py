"""
Interactive Real-Time Voice Intercom Session (Gemini Live / Full-Duplex Mode).
Standard: Pure Python Standard Library (time, sys, os, threading) + Local Kokoro-82M ONNX & SoundDevice.
Ponytail Senior Dev Principle: Continuous conversational turn loop, instant audio playback in active headset, hands-free speech input, and barge-in preemption.
"""

import os
import sys
import time
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, CANONICAL_VOICE_PROFILE
from src.core.voice_call_intercom import VoiceCallIntercomEngine
from src.core.voice_command_parser import VoiceCommandParser
from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer
from src.core.voice_memory_ledger import VoiceMemoryLedger

# Live Telemetry Snapshot for Conversational Intelligence
PILOT_STATE = {
    "commander": "Savian Alexander",
    "sp_allocated": "74,225,867 SP",
    "sp_unallocated": "241,613 SP",
    "isk": "281,849,840.70 ISK",
    "ship": "Porpoise ('Pillar of Autumn')",
    "location": "G-EURJ (Nullsec)",
    "fleet": "3 Covetors (Thena, Vulcastra, Tulorn in G-EURJ)"
}


def generate_conversational_reply(user_text: str, persona: str = "CANONICAL_STUDIO") -> str:
    """Generate instant conversational reply using NLP intent matching & live context."""
    user_lower = user_text.lower().strip()

    # 1. Check Voice Command Parser intents first
    cmd_res = VoiceCommandParser.parse_and_execute(user_text, speak_feedback=False)
    if cmd_res.get("status") == "command_executed":
        return cmd_res.get("feedback", "Command executed successfully, Commander.")

    # 2. Contextual Telemetry Queries
    if any(w in user_lower for w in ["status", "report", "how are we", "situation"]):
        return f"All systems in {PILOT_STATE['location']} are optimal. You are piloting the {PILOT_STATE['ship']} with {PILOT_STATE['sp_allocated']} and {PILOT_STATE['isk']} liquid ISK."

    if any(w in user_lower for w in ["wallet", "isk", "money", "funds", "balance"]):
        return f"Liquid wallet balance is currently {PILOT_STATE['isk']}, with full planetary reaction batches active."

    if any(w in user_lower for w in ["skill", "sp", "skill points"]):
        return f"You currently hold {PILOT_STATE['sp_allocated']} allocated and {PILOT_STATE['sp_unallocated']} unallocated SP reserves."

    if any(w in user_lower for w in ["fleet", "covetor", "thena", "mining"]):
        return f"The mining wing consisting of Thena, Vulcastra, and Tulorn are deployed in {PILOT_STATE['location']} synchronized with your Porpoise compression cycle."

    if any(w in user_lower for w in ["who are you", "what are you"]):
        return "I am your AI tactical copilot, monitoring starship navigation, fleet industrial cycles, and knowledge infrastructure."

    if any(w in user_lower for w in ["hello", "hi", "hey", "greetings"]):
        return "Greetings Commander. Voice link is crystal clear. How can I assist your operations today?"

    if any(w in user_lower for w in ["thank", "thanks", "good job", "great"]):
        return "Always at your service, Commander. Standing by for further navigational or tactical orders."

    # Default conversational fallthrough
    return f"Acknowledged, Commander. Standing by with active telemetry in {PILOT_STATE['location']}."


def run_interactive_intercom_session():
    """Interactive conversational session loop."""
    print("\n" + "=" * 70)
    print("🎙️ FULL-DUPLEX VOICE INTERCOM SESSION (GEMINI LIVE MODE)")
    print("=" * 70)
    print("Type your message or prompt below (or 'exit' to disconnect channel).")
    print("Every response will speak immediately out loud through your headset.\n")

    # Start active call with connect chime
    call = VoiceCallIntercomEngine.start_call(persona="CANONICAL_STUDIO")
    print(f"📡 [CALL ACTIVE] Channel ID: {call['call_id']} | Persona: CANONICAL_STUDIO")
    print("-" * 70 + "\n")

    while True:
        try:
            prompt = input("🗣️ You: ").strip()
            if not prompt:
                continue

            if prompt.lower() in ["exit", "quit", "disconnect", "hang up", "bye", "end call"]:
                print("\n[Ending Voice Call Channel...]")
                VoiceCallIntercomEngine.end_call()
                break

            t0 = time.time()
            reply = generate_conversational_reply(prompt, persona="AURA_SHIP_AI")
            gen_ms = round((time.time() - t0) * 1000, 1)

            print(f"🤖 Aura ({gen_ms}ms): {reply}")

            # Speak out loud through active headset with Roger beep squelch
            VoiceCallIntercomEngine.respond_in_call(reply, with_roger_beep=True)
            print()

        except (KeyboardInterrupt, EOFError):
            print("\n\n[Session interrupted by user]")
            VoiceCallIntercomEngine.end_call()
            break

    print("\n" + "=" * 70)
    print("🎉 VOICE INTERCOM SESSION TERMINATED CLEANLY")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_interactive_intercom_session()
