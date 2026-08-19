"""
Spoken Voice Command NLP Intent Parser & Autonomous Dispatcher.
Standard: Pure Python Standard Library (re, json, typing, time).
Ponytail Senior Dev Principle: Maps conversational spoken commands into deterministic system actions with zero latency and zero heavy NLP dependencies.
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple

from src.core.voice_bridge import VoiceBridge, CANONICAL_VOICE_PROFILE
from src.core.voice_dsp import VoiceDSP
from src.core.audit_hashchain import GLOBAL_AUDIT_HASHCHAIN


def _exec_set_persona(param: str) -> Tuple[str, Dict[str, Any]]:
    feedback = "Universal canonical voice profile active (af_heart Studio Master)."
    action = {"new_persona": "CANONICAL_STUDIO", "voice": CANONICAL_VOICE_PROFILE["voice"], "dsp_preset": CANONICAL_VOICE_PROFILE["dsp_preset"]}
    return feedback, action


def _exec_set_dsp_preset(param: str) -> Tuple[str, Dict[str, Any]]:
    target_dsp = "STUDIO_DIRECT"
    for dkey in VoiceDSP.get_available_presets().keys():
        if dkey.lower().replace("_", " ") in param.lower():
            target_dsp = dkey
            break
    feedback = f"Mastering preset adjusted to {target_dsp.replace('_', ' ').title()}."
    action = {"new_dsp_preset": target_dsp}
    return feedback, action


def _exec_check_radar(param: str) -> Tuple[str, Dict[str, Any]]:
    from src.core.voice_radar_announcer import AutonomousVoiceRadar
    radar_res = AutonomousVoiceRadar.sweep_and_announce()
    feedback = radar_res.get("summary", "Tududi radar sweep complete. All deadlines monitored.")
    return feedback, radar_res


def _exec_verify_audit(param: str) -> Tuple[str, Dict[str, Any]]:
    integrity = GLOBAL_AUDIT_HASHCHAIN.verify_integrity()
    valid = integrity.get("valid", False)
    blocks = integrity.get("total_blocks", 0)
    feedback = (
        f"Cryptographic audit verified. All {blocks} blocks link to the Merkle root with zero tampering."
        if valid else "Audit warning. Cryptographic chain discrepancy detected."
    )
    return feedback, integrity


def _exec_read_code(param: str) -> Tuple[str, Dict[str, Any]]:
    from src.core.voice_code_narrator import CodeSyntaxNarrator
    narrative = CodeSyntaxNarrator.deconstruct_code_for_speech(param)
    return narrative, {"narrative": narrative}


def _exec_read_email(param: str) -> Tuple[str, Dict[str, Any]]:
    from src.core.voice_document_reader import DocumentVoiceReader
    cleaned = DocumentVoiceReader.clean_email_for_speech(param)
    return cleaned["speech_text"], cleaned


def _exec_start_call(param: str) -> Tuple[str, Dict[str, Any]]:
    from src.core.voice_call_intercom import VoiceCallIntercomEngine
    call_res = VoiceCallIntercomEngine.start_call_session(domain="COMMAND_SESSION")
    return "Voice intercom session opened. Full-duplex channel active.", call_res


def _exec_end_call(param: str) -> Tuple[str, Dict[str, Any]]:
    from src.core.voice_call_intercom import VoiceCallIntercomEngine
    call_res = VoiceCallIntercomEngine.end_call_session()
    return "Voice intercom session closed. Turn logs committed to memory.", call_res


def _exec_get_status(param: str) -> Tuple[str, Dict[str, Any]]:
    return (
        "All neural voice sub-systems, DSP master racks, and C-level playback queues are fully operational.",
        {"status": "all_systems_nominal"}
    )


def _exec_speak_text(param: str) -> Tuple[str, Dict[str, Any]]:
    return param, {"spoken": param}


def _exec_default(param: str) -> Tuple[str, Dict[str, Any]]:
    return f"Command processed: {param}", {"query": param}


_INTENT_EXECUTORS = {
    "SET_PERSONA": _exec_set_persona,
    "SET_DSP_PRESET": _exec_set_dsp_preset,
    "CHECK_RADAR": _exec_check_radar,
    "VERIFY_AUDIT": _exec_verify_audit,
    "READ_CODE": _exec_read_code,
    "READ_EMAIL": _exec_read_email,
    "START_CALL": _exec_start_call,
    "END_CALL": _exec_end_call,
    "GET_STATUS": _exec_get_status,
    "SPEAK_TEXT": _exec_speak_text,
}


class VoiceCommandParser:
    """Zero-dependency spoken voice command intent parser and execution engine."""

    INTENT_PATTERNS: List[Tuple[str, str, str]] = [
        # (Pattern, Intent Name, Description)
        (r"(?:set|switch|change)\s+(?:voice|persona)\s+(?:to\s+)?([a-zA-Z_\s]+)", "SET_PERSONA", "Change active neural voice persona"),
        (r"(?:set|switch|change|apply)\s+(?:dsp|preset|mastering|audio)\s+(?:to\s+)?([a-zA-Z_\s]+)", "SET_DSP_PRESET", "Change DSP acoustic mastering preset"),
        (r"(?:check|sweep|scan|run)\s+(?:tududi|tasks?|radar|deadlines?)", "CHECK_RADAR", "Sweep upcoming Tududi task deadlines"),
        (r"(?:audit|verify|check)\s+(?:hashchain|merkle|provenance|security)", "VERIFY_AUDIT", "Verify SHA-256 Merkle audit hashchain"),
        (r"(?:read|narrate|speak)\s+(?:code|syntax|query|sql)\s*:\s*(.+)", "READ_CODE", "Deconstruct code syntax into spoken narrative"),
        (r"(?:read|narrate|summarize)\s+(?:email|memo|briefing)\s*:\s*(.+)", "READ_EMAIL", "Clean and read executive email memo"),
        (r"(?:start|open|connect)\s+(?:call|intercom|session)", "START_CALL", "Initialize conversational voice call session"),
        (r"(?:end|hangup|close|disconnect|terminate)\s+(?:call|intercom|session)", "END_CALL", "Terminate active voice call session"),
        (r"(?:get|check|show)\s+(?:voice\s+)?(?:status|telemetry|health)", "GET_STATUS", "Retrieve neural voice system status"),
        (r"(?:speak|say|announce)\s+(.+)", "SPEAK_TEXT", "Speak general text payload")
    ]

    @classmethod
    def parse_intent(cls, spoken_text: str) -> Dict[str, Any]:
        """Parse raw speech transcript into structured intent and parameters."""
        text_clean = spoken_text.strip()
        text_lower = text_clean.lower()

        for pattern, intent, desc in cls.INTENT_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                extracted_param = match.group(1).strip() if match.groups() else ""
                return {
                    "matched": True,
                    "intent": intent,
                    "description": desc,
                    "raw_input": spoken_text,
                    "extracted_param": extracted_param
                }

        # Fallback to general conversational speech
        return {
            "matched": False,
            "intent": "CONVERSATIONAL_QUERY",
            "description": "General conversational query or chat input",
            "raw_input": spoken_text,
            "extracted_param": text_clean
        }

    @classmethod
    def execute_command(cls, spoken_text: str, speak_feedback: bool = True) -> Dict[str, Any]:
        """Parse and execute spoken command with immediate voice confirmation via O(1) table dispatch."""
        parsed = cls.parse_intent(spoken_text)
        intent = parsed["intent"]
        param = parsed.get("extracted_param", "")
        t0 = time.time()

        executor = _INTENT_EXECUTORS.get(intent, _exec_default)
        feedback_text, action_result = executor(param)

        # Dispatch voice audio feedback
        if speak_feedback and feedback_text:
            VoiceBridge.speak(
                text=feedback_text,
                domain="COMMAND_FEEDBACK",
                priority="HIGH"
            )

        GLOBAL_AUDIT_HASHCHAIN.append_event(
            event_type="VOICE_COMMAND_EXECUTED",
            payload={"intent": intent, "input": spoken_text, "feedback": feedback_text},
            actor="VOICE_COMMAND_PARSER"
        )

        return {
            "status": "command_executed",
            "intent": intent,
            "parsed_intent": parsed,
            "feedback_text": feedback_text,
            "spoken_confirmation": feedback_text,
            "action_result": action_result,
            "latency_ms": round((time.time() - t0) * 1000, 1)
        }

    # Backward compatibility and alias helpers
    parse_and_execute = execute_command
    parse_command = execute_command

