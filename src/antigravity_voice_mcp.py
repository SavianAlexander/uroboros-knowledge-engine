"""
Antigravity Neural Voice MCP Server.
Standard: Pure Python Standard Library (json, sys, os, time, threading).
Ponytail Senior Dev Principle: Complete, zero-dependency JSON-RPC stdio MCP server for Antigravity AI featuring:
1. Master Neural Speech with Acoustic DSP Rack (`antigravity_speak`)
2. Engineering Milestone Announcer (`antigravity_announce_task`)
3. Executive Multi-Bullet Briefings (`antigravity_voice_brief`)
4. Procedural Tactical SFX Generator (`antigravity_play_sfx`)
5. Vector Persona Blending (`antigravity_blend_persona`)
6. Speech-to-Text Ear Transcriber (`antigravity_listen`)
7. Audio Device Discovery & Volume Master (`antigravity_list_audio_devices`)
8. Conversational Voice Memory Ledger (`antigravity_get_voice_history`)
9. 32-Band Real-Time FFT Spectrum Visualizer (`antigravity_get_spectrum`)
10. Proactive Tududi Voice Radar Sweep (`antigravity_trigger_tududi_radar`)
11. Full-Duplex Voice Call Intercom Start (`antigravity_start_call`)
12. Conversational In-Call Response with Roger Beep (`antigravity_call_respond`)
13. Instant VAD Barge-In Audio Cutoff (`antigravity_barge_in_cut`)
14. Voice Call Termination (`antigravity_end_call`)
15. Real-Time Call Telemetry & State (`antigravity_get_call_status`)
16. Runtime Voice Configuration (`antigravity_configure_voice`)
17. Engine Health Telemetry (`antigravity_get_status`)
"""

import os
import sys
import json
import time
import threading
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.voice_bridge import VoiceBridge, DOMAIN_PROFILES, KOKORO_PERSONAS
from src.core.voice_normalizer import VoiceNormalizer
from src.core.voice_persona_blend import VoicePersonaBlender
from src.core.voice_stt_ear import VoiceEarTranscriber
from src.core.voice_audio_router import VoiceAudioRouter
from src.core.voice_memory_ledger import VoiceMemoryLedger
from src.core.voice_spectrum_stream import VoiceSpectrumAnalyzer
from src.core.voice_tududi_radar import TududiVoiceRadarDaemon
from src.core.voice_call_intercom import VoiceCallIntercomEngine
from src.core.voice_vad_interrupter import VoiceActivityInterrupter
from src.core.voice_code_narrator import CodeSyntaxNarrator
from src.core.voice_document_reader import DocumentVoiceReader
from src.core.voice_studio_showcase import VoiceStudioShowcase
from src.core.voice_dsp import VoiceDSP
from src.core.audit_hashchain import GLOBAL_AUDIT_HASHCHAIN
from src.core.voice_command_parser import VoiceCommandParser
from src.core.voice_telemetry_exporter import AudioTelemetryExporter
from src.domain.eve_fleet_tactical_voice import EVEFleetTacticalVoice


# Global Voice Configuration State
VOICE_CONFIG = {
    "default_persona": "CALM_OPERATIONS",
    "default_voice": "af_bella",
    "default_speed": 1.0,
    "default_dsp": "STUDIO_DIRECT",
    "ducking_enabled": True
}


TOOLS_SCHEMA = [
    {
        "name": "antigravity_speak",
        "description": "Synthesize and speak clear natural voice messages using the Kokoro-82M neural engine with in-memory zero-disk C-level playback, acoustic DSP presets, pronunciation normalizer, and non-interrupting priority queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The exact text to speak. Markdown, acronyms, and tech terms are automatically normalized for fluent human pronunciation."
                },
                "persona": {
                    "type": "string",
                    "description": "Voice persona key ('AURA_SHIP_AI', 'TACTICAL_ADVISOR', 'FLEET_COMMANDER', 'INDUSTRY_OVERSEER', 'CALM_OPERATIONS') or voice ID ('bf_emma', 'af_sarah', 'am_adam', 'bm_george', 'af_bella', 'af_heart').",
                    "default": "CALM_OPERATIONS"
                },
                "speed": {
                    "type": "number",
                    "description": "Speech speed multiplier between 0.5 and 2.0 (default 1.0).",
                    "default": 1.0
                },
                "dsp_preset": {
                    "type": "string",
                    "description": "Acoustic DSP preset: 'STUDIO_DIRECT', 'COCKPIT_ACOUSTIC', 'RADIO_BANDPASS_300_3400HZ', 'LONG_RANGE_SQUELCH'.",
                    "default": "STUDIO_DIRECT"
                },
                "priority": {
                    "type": "string",
                    "enum": ["CRITICAL", "URGENT", "HIGH", "NORMAL", "INFO"],
                    "description": "Queue priority. 'CRITICAL' instantly preempts current playback and flushes lower priority backlog.",
                    "default": "NORMAL"
                },
                "sfx_intro": {
                    "type": "string",
                    "description": "Optional procedural SFX chime before speech: 'target_lock', 'warp_spool', 'shield_critical', 'armor_bleed', 'hull_breach'.",
                    "default": ""
                },
                "blocking": {
                    "type": "boolean",
                    "description": "If true, blocks until audio playback finishes.",
                    "default": False
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "antigravity_announce_task",
        "description": "Announce an engineering milestone, task status, or test pass/failure with specialized acoustic cues and voice persona.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_name": {"type": "string", "description": "Name or headline of the task/feature."},
                "state": {"type": "string", "enum": ["STARTED", "COMPLETED", "FAILED", "PAUSED", "AWAITING_INPUT"], "default": "COMPLETED"},
                "details": {"type": "string", "description": "Optional additional metrics or explanation.", "default": ""},
                "persona": {"type": "string", "description": "Voice persona to use.", "default": "INDUSTRY_OVERSEER"}
            },
            "required": ["task_name", "state"]
        }
    },
    {
        "name": "antigravity_voice_brief",
        "description": "Synthesize a multi-bullet executive or daily briefing with natural clause cadence and pause pacing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the briefing."},
                "items": {"type": "array", "items": {"type": "string"}, "description": "List of bullet points to narrate."},
                "persona": {"type": "string", "description": "Voice persona.", "default": "CALM_OPERATIONS"}
            },
            "required": ["title", "items"]
        }
    },
    {
        "name": "antigravity_play_sfx",
        "description": "Generate and play pure procedural tactical sound effects (warp spool, target lock, shield siren, hull breach, ambient drone).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sfx_name": {
                    "type": "string",
                    "enum": ["target_lock", "warp_spool", "shield_critical", "armor_bleed", "hull_breach", "cockpit_ambient"],
                    "description": "Name of procedural sound effect to generate."
                }
            },
            "required": ["sfx_name"]
        }
    },
    {
        "name": "antigravity_blend_persona",
        "description": "Linearly interpolate between two or more Kokoro voice embedding vectors to generate a custom signature timbre.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "weights": {
                    "type": "object",
                    "description": "Map of voice IDs to float weights (e.g. {'bf_emma': 0.7, 'af_bella': 0.3})."
                },
                "blend_name": {
                    "type": "string",
                    "description": "Name identifier for the custom vocal blend.",
                    "default": "custom_blend"
                }
            },
            "required": ["weights"]
        }
    },
    {
        "name": "antigravity_listen",
        "description": "Transcribe audio from microphone recording or an audio file using speech-to-text transcriber.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audio_path": {
                    "type": "string",
                    "description": "Optional path to WAV audio file. If omitted, captures from microphone.",
                    "default": ""
                },
                "duration_seconds": {
                    "type": "number",
                    "description": "Microphone capture duration in seconds.",
                    "default": 3.0
                }
            }
        }
    },
    {
        "name": "antigravity_list_audio_devices",
        "description": "Enumerate system audio output devices and hardware rendering endpoints.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_get_voice_history",
        "description": "Query the SQLite conversational voice memory ledger for recent dialogue logs and metrics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max turns to retrieve", "default": 10},
                "session_id": {"type": "string", "description": "Optional session ID filter"}
            }
        }
    },
    {
        "name": "antigravity_get_spectrum",
        "description": "Compute 32-band real-time FFT frequency spectrum and waveform envelope for UI visualizer.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "num_bands": {"type": "integer", "description": "Number of spectrum bands", "default": 32}
            }
        }
    },
    {
        "name": "antigravity_trigger_tududi_radar",
        "description": "Execute an immediate Tududi Task Master radar sweep and speak pending deadline alerts.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_start_call",
        "description": "Initiate an active interactive voice call / radio intercom session with rising connection chime and greeting.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona": {
                    "type": "string",
                    "description": "Persona for the call ('AURA_SHIP_AI', 'CALM_OPERATIONS', 'TACTICAL_ADVISOR', 'FLEET_COMMANDER').",
                    "default": "AURA_SHIP_AI"
                },
                "caller_name": {
                    "type": "string",
                    "description": "Name of the user/commander on the call.",
                    "default": "Commander Savian Alexander"
                }
            }
        }
    },
    {
        "name": "antigravity_call_respond",
        "description": "Speak conversational response in active call followed by radio Roger beep squelch tail.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The response message to speak."
                },
                "with_roger_beep": {
                    "type": "boolean",
                    "description": "Whether to append tactical NASA Apollo Roger beep.",
                    "default": True
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "antigravity_barge_in_cut",
        "description": "Instantly halt active speech playback in under 1 millisecond when the user begins speaking or interrupts.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_end_call",
        "description": "Terminate the active voice call session and play falling disconnect chime.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_get_call_status",
        "description": "Retrieve live state of the active voice call session and turn metrics.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_read_code",
        "description": "Deconstruct complex code snippets, git diffs, SQL queries, or CLI commands into smooth, human-like spoken narrative.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The raw code snippet, diff, or SQL statement to narrate."},
                "language": {"type": "string", "description": "Programming language (e.g. 'python', 'sql', 'bash', 'diff').", "default": "python"},
                "speak": {"type": "boolean", "description": "If true, speaks the narrative audio immediately.", "default": False},
                "persona": {"type": "string", "description": "Persona to speak narrative with.", "default": "CALM_OPERATIONS"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "antigravity_read_email",
        "description": "Clean long-form emails, strip boilerplates/disclaimers/links, and synthesize executive voice briefing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "raw_email": {"type": "string", "description": "Raw email text including optional headers."},
                "speak": {"type": "boolean", "description": "If true, speaks the executive summary immediately.", "default": False},
                "persona": {"type": "string", "description": "Persona to speak briefing with.", "default": "CALM_OPERATIONS"}
            },
            "required": ["raw_email"]
        }
    },
    {
        "name": "antigravity_showcase_personas",
        "description": "Audition and explore all neural voice personas with their custom acoustic DSP presets or retrieve studio catalog.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona": {"type": "string", "description": "Specific persona key to audition (e.g. 'AURA_SHIP_AI', 'ORACLE_ADVISOR', 'FLEET_COMMANDER')."},
                "custom_text": {"type": "string", "description": "Custom audition phrase."},
                "dsp_preset": {"type": "string", "description": "DSP acoustic preset override."},
                "speak": {"type": "boolean", "description": "If true, synthesizes and plays audio in-memory immediately.", "default": True}
            }
        }
    },
    {
        "name": "antigravity_apply_studio_master",
        "description": "Speak text processed through the high-fidelity studio mastering DSP pipeline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to master and speak."},
                "preset": {"type": "string", "description": "Acoustic preset ('STUDIO_MASTER', 'EXECUTIVE_PRESENCE', 'COMMANDER_TACTICAL', 'HOLOGRAPHIC_AURA').", "default": "EXECUTIVE_PRESENCE"},
                "persona": {"type": "string", "description": "Persona identifier.", "default": "ORACLE_ADVISOR"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "antigravity_verify_audit_hashchain",
        "description": "Cryptographically verify the SHA-256 Merkle audit hashchain for all voice, RAG, and AI operations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of recent blocks to inspect.", "default": 10}
            }
        }
    },
    {
        "name": "antigravity_parse_voice_command",
        "description": "Parse natural spoken command text and execute the corresponding action with spoken feedback.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Spoken natural language command string."},
                "speak_feedback": {"type": "boolean", "description": "If true, speaks synthesized confirmation audio.", "default": True}
            },
            "required": ["command"]
        }
    },
    {
        "name": "antigravity_get_audio_telemetry",
        "description": "Export real-time Prometheus or JSON telemetry metrics across voice, DSP, RAG cache, and audit hashchains.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "description": "Export format: 'json' or 'prometheus'.", "default": "json"}
            }
        }
    },
    {
        "name": "antigravity_broadcast_fleet_alert",
        "description": "Synthesize and broadcast tactical EVE fleet combat communications (cynos, warp disruption bubbles, compression cycles).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "alert_type": {"type": "string", "description": "Alert type (e.g. 'CYNO_BEACON_ACTIVE', 'INTERDICTOR_BUBBLE_DROP', 'MINING_COMPRESSION_CYCLE', 'FLEET_ANCHOR_COMMAND')."},
                "system": {"type": "string", "description": "Solar system name.", "default": "G-EURJ"},
                "speak": {"type": "boolean", "description": "If true, synthesizes and plays audio immediately.", "default": True}
            },
            "required": ["alert_type"]
        }
    },
    {
        "name": "antigravity_instant_speak",
        "description": "Speak text with ultra-low latency (<1ms cached, <25ms fresh) directly to the persistent hardware stream.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to speak."},
                "persona": {"type": "string", "description": "Voice persona (e.g. 'AURA_SHIP_AI', 'FLEET_COMMANDER', 'CALM_OPERATIONS').", "default": "AURA_SHIP_AI"},
                "dsp_preset": {"type": "string", "description": "Acoustic DSP Preset.", "default": "HOLOGRAPHIC_AURA"},
                "speed": {"type": "number", "description": "Playback speed multiplier.", "default": 1.0},
                "sync": {"type": "boolean", "description": "If true, blocks until audio playback finishes.", "default": False}
            },
            "required": ["text"]
        }
    },
    {
        "name": "antigravity_prewarm_voice_engine",
        "description": "Pre-warm neural ONNX model tensors and render essential tactical phrases into high-speed RAM cache.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_get_instant_streamer_stats",
        "description": "Retrieve performance telemetry, cache hits, and streaming metrics from the Instant Audio Streamer.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_configure_voice",
        "description": "Configure global default voice settings for Antigravity assistant.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "default_persona": {"type": "string", "description": "New default persona."},
                "default_speed": {"type": "number", "description": "New default speed multiplier."},
                "default_dsp": {"type": "string", "description": "New default DSP preset."}
            }
        }
    },
    {
        "name": "antigravity_voice_rag_query",
        "description": "Execute a SOTA Knowledge Vault RAG search and speak the factual answer directly into the user's headset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Knowledge search query to retrieve and speak."},
                "persona": {"type": "string", "description": "Spoken voice persona (e.g. AURA_SHIP_AI, ORACLE_ADVISOR, FLEET_COMMANDER)."},
                "dsp_preset": {"type": "string", "description": "Acoustic DSP mastering preset."},
                "max_sentences": {"type": "integer", "description": "Maximum sentences to synthesize for spoken summary."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "antigravity_synthesize_podcast_dialogue",
        "description": "Synthesize a multi-speaker roundtable conversation across distinct Kokoro neural personas.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "turns": {
                    "type": "array",
                    "description": "Array of dialogue turn objects: [{'speaker': 'Aura', 'persona': 'AURA_SHIP_AI', 'text': '...'}, ...]"
                },
                "pause_duration_s": {"type": "number", "description": "Pause between speakers in seconds."},
                "play_live": {"type": "boolean", "description": "Stream live audio to headset during synthesis."}
            },
            "required": ["turns"]
        }
    },
    {
        "name": "antigravity_voice_telemetry_sweep",
        "description": "Execute an empirical ESI fleet telemetry sweep in G-EURJ and speak the acoustic tactical report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "speak_alert": {"type": "boolean", "description": "Whether to speak the telemetry alert aloud."}
            }
        }
    },
    {
        "name": "antigravity_voice_record_note",
        "description": "Ingest a spoken brain dump note directly into vault/Notes and index into SQLite FTS5 database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Note title."},
                "content": {"type": "string", "description": "Transcript content of the note."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Categorization tags."},
                "speak_confirmation": {"type": "boolean", "description": "Whether to speak acoustic confirmation."}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "antigravity_voice_create_task",
        "description": "Create a top-level task in Tududi with acoustic voice confirmation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task name/title."},
                "note": {"type": "string", "description": "Detailed description."},
                "priority": {"type": "integer", "description": "Task priority level."},
                "project_id": {"type": "integer", "description": "Tududi project ID (default 14)."}
            },
            "required": ["title"]
        }
    },
    {
        "name": "antigravity_check_threat_radar",
        "description": "Evaluate nullsec threat radar metrics in G-EURJ or adjacent systems and dispatch klaxon warnings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system": {"type": "string", "description": "Solar system to sweep (default G-EURJ)."},
                "speak_alert": {"type": "boolean", "description": "Whether to speak tactical alert aloud."}
            }
        }
    },
    {
        "name": "antigravity_stream_pipeline_speak",
        "description": "Synthesize and stream text clauses with ultra-low perceived latency (<180ms TTFS).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Full text stream to chunk and synthesize."},
                "persona": {"type": "string", "description": "Voice persona."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "antigravity_check_market_arbitrage",
        "description": "Calculate live CCP ESI market arbitrage and regional spread between any source and target regions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "commodity": {"type": "string", "description": "Commodity, item, or mineral name (e.g. Isogen, Tritanium, Morphite, PLEX)."},
                "source_region": {"type": "string", "description": "Source market region (e.g. 'The Forge' / Jita, 'Domain' / Amarr, 'Sinq Laison'). Default 'The Forge'."},
                "target_region": {"type": "string", "description": "Target market region (e.g. 'Delve', 'Fountain', 'Catch'). Default 'Delve'."},
                "speak_report": {"type": "boolean", "description": "Whether to speak acoustic briefing."}
            }
        }
    },
    {
        "name": "antigravity_check_pi_sentinel",
        "description": "Audit planetary interaction colony status, extractor cycles, and customs offices.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "character": {"type": "string", "description": "Pilot name (default Savian Alexander)."},
                "speak_alert": {"type": "boolean", "description": "Whether to speak acoustic report."}
            }
        }
    },
    {
        "name": "antigravity_scan_vault_auto_watcher",
        "description": "Trigger an incremental filesystem delta scan and auto-index new vault documents into SQLite FTS5.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "antigravity_listen_and_transcribe",
        "description": "Record audio sample from the headset microphone and transcribe speech into text in real-time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "duration_seconds": {"type": "number", "description": "Microphone recording duration in seconds (default 3.0)."}
            }
        }
    },
    {
        "name": "antigravity_get_status",
        "description": "Retrieve active neural voice engine status, available personas, memory footprint, and audio history.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def _handle_speak(args: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.time()
    text = args.get("text", "")
    persona = args.get("persona") or VOICE_CONFIG["default_persona"]
    voice = KOKORO_PERSONAS.get(persona, persona)
    speed = float(args.get("speed", VOICE_CONFIG["default_speed"]))
    dsp_preset = args.get("dsp_preset") or VOICE_CONFIG["default_dsp"]
    priority = args.get("priority", "NORMAL")
    sfx_intro = args.get("sfx_intro", "")
    blocking = bool(args.get("blocking", False))

    clean_text = VoiceNormalizer.normalize_for_speech(text)
    res = VoiceBridge.speak(
        text=clean_text,
        domain="GENERAL",
        priority=priority,
        voice=voice,
        dsp_preset=dsp_preset,
        sfx_intro=sfx_intro if sfx_intro else None
    )
    res["original_text"] = text
    res["normalized_text"] = clean_text
    res["speed"] = speed

    # Log into SQLite Conversational Memory
    duration_ms = round((time.time() - t0) * 1000, 1)
    VoiceMemoryLedger.log_turn(
        speaker="Antigravity",
        raw_text=text,
        normalized_text=clean_text,
        persona=persona,
        duration_ms=duration_ms,
        domain="GENERAL"
    )
    return res


def _handle_announce_task(args: Dict[str, Any]) -> Dict[str, Any]:
    task_name = args.get("task_name", "")
    state = args.get("state", "COMPLETED").upper()
    details = args.get("details", "")
    persona = args.get("persona", "INDUSTRY_OVERSEER")
    voice = KOKORO_PERSONAS.get(persona, "bm_george")

    intro_sfx = "target_lock" if state == "COMPLETED" else "shield_critical" if state == "FAILED" else ""
    priority = "CRITICAL" if state == "FAILED" else "HIGH" if state == "STARTED" else "NORMAL"

    state_phrasing = {
        "STARTED": f"Started working on {task_name}.",
        "COMPLETED": f"Successfully completed {task_name}.",
        "FAILED": f"Task failure alert on {task_name}.",
        "PAUSED": f"Paused execution on {task_name}.",
        "AWAITING_INPUT": f"Execution paused. Awaiting your decision on {task_name}."
    }.get(state, f"Task update on {task_name}: {state}.")

    full_text = f"{state_phrasing} {details}".strip()
    clean_text = VoiceNormalizer.normalize_for_speech(full_text)

    res = VoiceBridge.speak(
        text=clean_text,
        domain="DEV_OPS",
        priority=priority,
        voice=voice,
        sfx_intro=intro_sfx if intro_sfx else None
    )
    res["task_name"] = task_name
    res["state"] = state

    VoiceMemoryLedger.log_turn(
        speaker="Antigravity",
        raw_text=full_text,
        normalized_text=clean_text,
        persona=persona,
        domain="DEV_OPS"
    )
    return res


def _handle_voice_brief(args: Dict[str, Any]) -> Dict[str, Any]:
    title = args.get("title", "Executive Briefing")
    items = args.get("items", [])
    persona = args.get("persona", "CALM_OPERATIONS")
    voice = KOKORO_PERSONAS.get(persona, "af_bella")

    bullet_text = " ... ".join(items)
    combined = f"{title}. ... {bullet_text} ... End of briefing."
    clean_text = VoiceNormalizer.normalize_for_speech(combined)

    res = VoiceBridge.speak(
        text=clean_text,
        domain="DAILY_BRIEF",
        priority="NORMAL",
        voice=voice
    )
    res["title"] = title
    res["item_count"] = len(items)

    VoiceMemoryLedger.log_turn(
        speaker="Antigravity",
        raw_text=combined,
        normalized_text=clean_text,
        persona=persona,
        domain="DAILY_BRIEF"
    )
    return res


def _handle_play_sfx(args: Dict[str, Any]) -> Dict[str, Any]:
    sfx_name = args.get("sfx_name", "target_lock")
    audio_bytes = VoiceBridge.play_sfx(sfx_name)
    return {
        "sfx_name": sfx_name,
        "generated": audio_bytes is not None,
        "bytes_len": len(audio_bytes) if audio_bytes else 0,
        "status": "playing"
    }


def _handle_blend_persona(args: Dict[str, Any]) -> Dict[str, Any]:
    weights = args.get("weights", {"bf_emma": 0.7, "af_bella": 0.3})
    blend_name = args.get("blend_name", "custom_blend")
    return VoicePersonaBlender.blend_personas(weights, custom_name=blend_name)


def _handle_listen(args: Dict[str, Any]) -> Dict[str, Any]:
    audio_path = args.get("audio_path", "")
    if audio_path and os.path.exists(audio_path):
        return VoiceEarTranscriber.transcribe_audio_file(audio_path)
    dur = float(args.get("duration_seconds", 3.0))
    rec = VoiceEarTranscriber.record_microphone_sample(duration_s=dur)
    transcription = VoiceEarTranscriber.transcribe_audio_file(rec["output_path"])
    transcription["recording_metadata"] = rec
    return transcription


def _handle_list_audio_devices(args: Dict[str, Any]) -> Dict[str, Any]:
    devices = VoiceAudioRouter.list_audio_output_devices()
    return {
        "devices": devices,
        "router_status": VoiceAudioRouter.get_router_status()
    }


def _handle_get_voice_history(args: Dict[str, Any]) -> Dict[str, Any]:
    limit = int(args.get("limit", 10))
    session_id = args.get("session_id")
    turns = VoiceMemoryLedger.get_recent_turns(limit=limit, session_id=session_id)
    metrics = VoiceMemoryLedger.get_voice_metrics()
    return {
        "turns": turns,
        "metrics": metrics
    }


def _handle_get_spectrum(args: Dict[str, Any]) -> Dict[str, Any]:
    num_bands = int(args.get("num_bands", 32))
    return VoiceSpectrumAnalyzer.analyze_audio_buffer(None, num_bands=num_bands)


def _handle_trigger_tududi_radar(args: Dict[str, Any]) -> Dict[str, Any]:
    return TududiVoiceRadarDaemon.execute_radar_sweep()


def _handle_start_call(args: Dict[str, Any]) -> Dict[str, Any]:
    persona = args.get("persona", "AURA_SHIP_AI")
    caller_name = args.get("caller_name", "Commander Savian Alexander")
    return VoiceCallIntercomEngine.start_call(persona=persona, caller_name=caller_name)


def _handle_call_respond(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    with_roger = bool(args.get("with_roger_beep", True))
    return VoiceCallIntercomEngine.respond_in_call(response_text=text, with_roger_beep=with_roger)


def _handle_barge_in_cut(args: Dict[str, Any]) -> Dict[str, Any]:
    return VoiceActivityInterrupter.execute_instant_barge_in()


def _handle_end_call(args: Dict[str, Any]) -> Dict[str, Any]:
    return VoiceCallIntercomEngine.end_call()


def _handle_get_call_status(args: Dict[str, Any]) -> Dict[str, Any]:
    return VoiceCallIntercomEngine.get_call_status()


def _handle_read_code(args: Dict[str, Any]) -> Dict[str, Any]:
    code = args.get("code", "")
    lang = args.get("language", "python")
    spoken_text = CodeSyntaxNarrator.deconstruct_code_for_speech(code, language=lang)
    res = {"language": lang, "spoken_narrative": spoken_text}
    if args.get("speak", False):
        voice_res = VoiceBridge.speak(
            text=spoken_text,
            domain="EXECUTIVE_BRIEF",
            voice=KOKORO_PERSONAS.get(args.get("persona", "CALM_OPERATIONS"), "af_bella")
        )
        res["voice_dispatch"] = voice_res
    return res


def _handle_read_email(args: Dict[str, Any]) -> Dict[str, Any]:
    raw_email = args.get("raw_email", "")
    cleaned = DocumentVoiceReader.clean_email_for_speech(raw_email)
    if args.get("speak", False):
        voice_res = VoiceBridge.speak(
            text=cleaned["speech_text"],
            domain="EXECUTIVE_BRIEF",
            voice=KOKORO_PERSONAS.get(args.get("persona", "CALM_OPERATIONS"), "af_bella")
        )
        cleaned["voice_dispatch"] = voice_res
    return cleaned


def _handle_showcase_personas(args: Dict[str, Any]) -> Dict[str, Any]:
    persona = args.get("persona")
    if persona:
        custom_text = args.get("custom_text")
        dsp_override = args.get("dsp_preset")
        speak_now = args.get("speak", True)
        return VoiceStudioShowcase.audition_persona(
            persona_key=persona,
            custom_text=custom_text,
            dsp_override=dsp_override,
            speak_now=speak_now
        )
    return VoiceStudioShowcase.get_studio_catalog()


def _handle_apply_studio_master(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    preset = args.get("preset", "EXECUTIVE_PRESENCE")
    persona = args.get("persona", "ORACLE_ADVISOR")
    voice = KOKORO_PERSONAS.get(persona, "af_sky")
    return VoiceBridge.speak(
        text=text,
        domain="STUDIO_SHOWCASE",
        priority="HIGH",
        voice=voice,
        dsp_preset=preset
    )


def _handle_verify_audit_hashchain(args: Dict[str, Any]) -> Dict[str, Any]:
    limit = args.get("limit", 10)
    integrity = GLOBAL_AUDIT_HASHCHAIN.verify_integrity()
    recent = GLOBAL_AUDIT_HASHCHAIN.get_recent_blocks(limit=limit)
    return {
        "integrity": integrity,
        "recent_blocks": recent
    }


def _handle_parse_voice_command(args: Dict[str, Any]) -> Dict[str, Any]:
    cmd_text = args.get("command", "")
    speak_fb = args.get("speak_feedback", True)
    return VoiceCommandParser.execute_command(spoken_text=cmd_text, speak_feedback=speak_fb)


def _handle_get_audio_telemetry(args: Dict[str, Any]) -> Dict[str, Any]:
    fmt = args.get("format", "json")
    if fmt == "prometheus":
        return {"format": "prometheus", "metrics": AudioTelemetryExporter.export_prometheus_metrics()}
    return AudioTelemetryExporter.get_telemetry_snapshot()


def _handle_broadcast_fleet_alert(args: Dict[str, Any]) -> Dict[str, Any]:
    alert_type = args.get("alert_type", "CYNO_BEACON_ACTIVE")
    system = args.get("system", "G-EURJ")
    speak_now = args.get("speak", True)
    return EVEFleetTacticalVoice.broadcast_tactical_alert(alert_type=alert_type, system=system, speak_now=speak_now)


def _handle_instant_speak(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.instant_audio_streamer import InstantVoiceClient
    text = args.get("text", "")
    persona = args.get("persona", "AURA_SHIP_AI")
    voice = KOKORO_PERSONAS.get(persona, persona)
    dsp_preset = args.get("dsp_preset", "HOLOGRAPHIC_AURA")
    speed = float(args.get("speed", 1.0))
    sync = bool(args.get("sync", False))
    return InstantVoiceClient.speak_instant(text, voice=voice, dsp_preset=dsp_preset, speed=speed, sync=sync)


def _handle_prewarm_voice_engine(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.instant_audio_streamer import InstantVoiceClient
    InstantVoiceClient.pre_warm_tactical_phrases()
    return {"status": "prewarmed", "message": "All neural ONNX weights and tactical phrase caches pinned in RAM."}


def _handle_get_instant_streamer_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.instant_audio_streamer import get_instant_streamer
    return {"status": "ok", "streamer_stats": get_instant_streamer().stats}


def _handle_configure_voice(args: Dict[str, Any]) -> Dict[str, Any]:
    if "default_persona" in args:
        VOICE_CONFIG["default_persona"] = args["default_persona"]
        VOICE_CONFIG["default_voice"] = KOKORO_PERSONAS.get(args["default_persona"], "af_bella")
    if "default_speed" in args:
        VOICE_CONFIG["default_speed"] = float(args["default_speed"])
    if "default_dsp" in args:
        VOICE_CONFIG["default_dsp"] = args["default_dsp"]
    return {"status": "updated", "config": VOICE_CONFIG}


def _handle_voice_rag_query(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_rag_bridge import VoiceRAGBridge
    query = args.get("query", "")
    persona = args.get("persona") or VOICE_CONFIG["default_persona"]
    dsp = args.get("dsp_preset") or VOICE_CONFIG["default_dsp"]
    max_sentences = int(args.get("max_sentences", 2))
    return VoiceRAGBridge.query_rag_and_speak(
        query=query,
        persona=persona,
        dsp_preset=dsp,
        sync=True,
        max_sentences=max_sentences
    )


def _handle_synthesize_podcast_dialogue(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_podcast_generator import VoicePodcastGenerator
    turns = args.get("turns", [])
    pause_s = float(args.get("pause_duration_s", 0.35))
    play_live = bool(args.get("play_live", False))
    return VoicePodcastGenerator.synthesize_dialogue(turns=turns, pause_duration_s=pause_s, play_live=play_live)


def _handle_voice_telemetry_sweep(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_fleet_telemetry_daemon import VoiceFleetTelemetryDaemon
    speak_alert = bool(args.get("speak_alert", True))
    return VoiceFleetTelemetryDaemon.execute_telemetry_sweep(speak_alert=speak_alert)


def _handle_voice_record_note(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_knowledge_ingest import VoiceKnowledgeIngest
    title = args.get("title", "Voice Note")
    content = args.get("content", "")
    tags = args.get("tags")
    speak = bool(args.get("speak_confirmation", True))
    return VoiceKnowledgeIngest.record_voice_note(title=title, content=content, tags=tags, speak_confirmation=speak)


def _handle_voice_create_task(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_knowledge_ingest import VoiceKnowledgeIngest
    title = args.get("title", "Voice Task")
    note = args.get("note", "")
    priority = int(args.get("priority", 1))
    project_id = int(args.get("project_id", 14))
    return VoiceKnowledgeIngest.create_voice_task(title=title, note=note, priority=priority, project_id=project_id, speak_confirmation=True)


def _handle_check_threat_radar(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.domain.eve_threat_radar import EveTacticalThreatRadar
    system = args.get("system", "G-EURJ")
    speak = bool(args.get("speak_alert", True))
    return EveTacticalThreatRadar.evaluate_system_threat(target_system=system, speak_alert=speak)


def _handle_stream_pipeline_speak(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_streaming_pipeline import VoiceStreamingPipeliner
    text = args.get("text", "")
    persona = args.get("persona") or VOICE_CONFIG["default_persona"]
    tokens = [w + " " for w in text.split()]
    return VoiceStreamingPipeliner.stream_and_speak(iter(tokens), persona=persona, sync=False)


def _handle_check_market_arbitrage(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.domain.eve_market_arbitrage import EveMarketArbitrage
    commodity = args.get("commodity", "Isogen")
    source_reg = args.get("source_region", "The Forge")
    target_reg = args.get("target_region", "Delve")
    speak = bool(args.get("speak_report", True))
    return EveMarketArbitrage.analyze_commodity_arbitrage(
        commodity_name=commodity,
        source_region=source_reg,
        target_region=target_reg,
        speak_report=speak
    )


def _handle_check_pi_sentinel(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.domain.eve_pi_sentinel import EvePISentinel
    char = args.get("character", "Savian Alexander")
    speak = bool(args.get("speak_alert", True))
    return EvePISentinel.audit_planetary_colonies(character_name=char, speak_alert=speak)


def _handle_scan_vault_auto_watcher(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.infrastructure.vault_auto_watcher import VaultAutoWatcher
    watcher = VaultAutoWatcher()
    return watcher.scan_and_index_delta()


def _handle_listen_and_transcribe(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.core.voice_stt_ear import VoiceEarTranscriber
    dur = float(args.get("duration_seconds", 3.0))
    return VoiceEarTranscriber.listen_and_transcribe(duration_s=dur)


def _handle_get_status(args: Dict[str, Any]) -> Dict[str, Any]:
    copilot = VoiceBridge.get_copilot()
    return {
        "engine": "Kokoro-82M ONNX Neural Suite",
        "supported_personas": KOKORO_PERSONAS,
        "preset_blends": VoicePersonaBlender.get_preset_blends(),
        "config": VOICE_CONFIG,
        "active_instance": copilot._local_kokoro_instance is not None if copilot else False,
        "sample_rate": 24000,
        "playback_engine": "Native In-Memory Win32 C-Level winsound (<15ms)",
        "call_status": VoiceCallIntercomEngine.get_call_status(),
        "normalizer": "VoiceNormalizer v2.0 Active",
        "memory_ledger": "SQLite Persistent Active",
        "router": VoiceAudioRouter.get_router_status()
    }


_TOOL_HANDLERS: Dict[str, Any] = {
    "antigravity_speak": _handle_speak,
    "antigravity_announce_task": _handle_announce_task,
    "antigravity_voice_brief": _handle_voice_brief,
    "antigravity_play_sfx": _handle_play_sfx,
    "antigravity_blend_persona": _handle_blend_persona,
    "antigravity_listen": _handle_listen,
    "antigravity_list_audio_devices": _handle_list_audio_devices,
    "antigravity_get_voice_history": _handle_get_voice_history,
    "antigravity_get_spectrum": _handle_get_spectrum,
    "antigravity_trigger_tududi_radar": _handle_trigger_tududi_radar,
    "antigravity_start_call": _handle_start_call,
    "antigravity_call_respond": _handle_call_respond,
    "antigravity_barge_in_cut": _handle_barge_in_cut,
    "antigravity_end_call": _handle_end_call,
    "antigravity_get_call_status": _handle_get_call_status,
    "antigravity_read_code": _handle_read_code,
    "antigravity_read_email": _handle_read_email,
    "antigravity_showcase_personas": _handle_showcase_personas,
    "antigravity_apply_studio_master": _handle_apply_studio_master,
    "antigravity_verify_audit_hashchain": _handle_verify_audit_hashchain,
    "antigravity_parse_voice_command": _handle_parse_voice_command,
    "antigravity_get_audio_telemetry": _handle_get_audio_telemetry,
    "antigravity_broadcast_fleet_alert": _handle_broadcast_fleet_alert,
    "antigravity_instant_speak": _handle_instant_speak,
    "antigravity_prewarm_voice_engine": _handle_prewarm_voice_engine,
    "antigravity_get_instant_streamer_stats": _handle_get_instant_streamer_stats,
    "antigravity_configure_voice": _handle_configure_voice,
    "antigravity_voice_rag_query": _handle_voice_rag_query,
    "antigravity_synthesize_podcast_dialogue": _handle_synthesize_podcast_dialogue,
    "antigravity_voice_telemetry_sweep": _handle_voice_telemetry_sweep,
    "antigravity_voice_record_note": _handle_voice_record_note,
    "antigravity_voice_create_task": _handle_voice_create_task,
    "antigravity_check_threat_radar": _handle_check_threat_radar,
    "antigravity_stream_pipeline_speak": _handle_stream_pipeline_speak,
    "antigravity_check_market_arbitrage": _handle_check_market_arbitrage,
    "antigravity_check_pi_sentinel": _handle_check_pi_sentinel,
    "antigravity_scan_vault_auto_watcher": _handle_scan_vault_auto_watcher,
    "antigravity_listen_and_transcribe": _handle_listen_and_transcribe,
    "antigravity_get_status": _handle_get_status,
}


def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Antigravity voice MCP tool calls via O(1) table dispatch."""
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}
    return handler(args)


def _process_jsonrpc_request(req: Dict[str, Any]) -> Dict[str, Any]:
    """Process single JSON-RPC MCP request with early exit."""
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "antigravity-voice-mcp",
                    "version": "2.2.0"
                }
            }
        }
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_SCHEMA}
        }
    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        tool_result = handle_tool_call(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_result, indent=2)
                    }
                ]
            }
        }
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method {method} not found"}
    }


def main():
    """Main JSON-RPC stdio MCP server loop with flat control flow."""
    for line in sys.stdin:
        line_str = line.strip()
        if not line_str:
            continue
        try:
            req = json.loads(line_str)
            res = _process_jsonrpc_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"[Antigravity Voice MCP Error] {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
