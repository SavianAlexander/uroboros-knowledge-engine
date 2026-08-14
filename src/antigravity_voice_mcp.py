"""
Antigravity Dedicated Neural Voice MCP Server.
Standard: Pure Python Standard Library (json, sys, os, time, threading).
Ponytail Senior Dev Principle: Zero-dependency JSON-RPC stdio MCP server providing studio-grade voice synthesis, task announcements, soundscapes, and acoustic DSP mastering for Antigravity AI.
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
        "description": "Synthesize and speak clear natural voice messages using the Kokoro-82M neural engine with acoustic DSP presets, pronunciation normalizer, and non-interrupting priority queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The exact text to speak. Markdown, acronyms, and tech terms are automatically normalized for fluent human pronunciation."
                },
                "persona": {
                    "type": "string",
                    "description": "Voice persona key (e.g., 'AURA_SHIP_AI', 'TACTICAL_ADVISOR', 'FLEET_COMMANDER', 'INDUSTRY_OVERSEER', 'CALM_OPERATIONS') or voice ID ('bf_emma', 'af_sarah', 'am_adam', 'bm_george', 'af_bella', 'af_heart').",
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
                "task_name": {
                    "type": "string",
                    "description": "Name or headline of the task/feature."
                },
                "state": {
                    "type": "string",
                    "enum": ["STARTED", "COMPLETED", "FAILED", "PAUSED", "AWAITING_INPUT"],
                    "description": "The current execution state.",
                    "default": "COMPLETED"
                },
                "details": {
                    "type": "string",
                    "description": "Optional additional metrics or explanation.",
                    "default": ""
                },
                "persona": {
                    "type": "string",
                    "description": "Voice persona to use (default 'INDUSTRY_OVERSEER' / bm_george for DevOps).",
                    "default": "INDUSTRY_OVERSEER"
                }
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
                "title": {
                    "type": "string",
                    "description": "Title of the briefing (e.g. 'Daily Standup Briefing' or 'System Health Status')."
                },
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of bullet points to narrate."
                },
                "persona": {
                    "type": "string",
                    "description": "Voice persona (default 'CALM_OPERATIONS' / af_bella).",
                    "default": "CALM_OPERATIONS"
                }
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
        "name": "antigravity_configure_voice",
        "description": "Configure global default voice settings for Antigravity assistant.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "default_persona": {
                    "type": "string",
                    "description": "New default persona ('AURA_SHIP_AI', 'TACTICAL_ADVISOR', 'FLEET_COMMANDER', 'INDUSTRY_OVERSEER', 'CALM_OPERATIONS')."
                },
                "default_speed": {
                    "type": "number",
                    "description": "New default speed multiplier."
                },
                "default_dsp": {
                    "type": "string",
                    "description": "New default DSP preset."
                }
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


def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Antigravity voice MCP tool calls."""
    if name == "antigravity_speak":
        text = args.get("text", "")
        persona = args.get("persona") or VOICE_CONFIG["default_persona"]
        voice = KOKORO_PERSONAS.get(persona, persona)
        speed = float(args.get("speed", VOICE_CONFIG["default_speed"]))
        dsp_preset = args.get("dsp_preset") or VOICE_CONFIG["default_dsp"]
        priority = args.get("priority", "NORMAL")
        sfx_intro = args.get("sfx_intro", "")
        blocking = bool(args.get("blocking", False))

        # 1. Phonetic & Cadence Normalization
        clean_text = VoiceNormalizer.normalize_for_speech(text)

        # 2. Dispatch through VoiceBridge
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
        return res

    elif name == "antigravity_announce_task":
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
        return res

    elif name == "antigravity_voice_brief":
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
        return res

    elif name == "antigravity_play_sfx":
        sfx_name = args.get("sfx_name", "target_lock")
        audio_bytes = VoiceBridge.play_sfx(sfx_name)
        return {
            "sfx_name": sfx_name,
            "generated": audio_bytes is not None,
            "bytes_len": len(audio_bytes) if audio_bytes else 0,
            "status": "playing"
        }

    elif name == "antigravity_configure_voice":
        if "default_persona" in args:
            VOICE_CONFIG["default_persona"] = args["default_persona"]
            VOICE_CONFIG["default_voice"] = KOKORO_PERSONAS.get(args["default_persona"], "af_bella")
        if "default_speed" in args:
            VOICE_CONFIG["default_speed"] = float(args["default_speed"])
        if "default_dsp" in args:
            VOICE_CONFIG["default_dsp"] = args["default_dsp"]
        return {"status": "updated", "config": VOICE_CONFIG}

    elif name == "antigravity_get_status":
        copilot = VoiceBridge.get_copilot()
        return {
            "engine": "Kokoro-82M ONNX Studio",
            "supported_personas": KOKORO_PERSONAS,
            "config": VOICE_CONFIG,
            "active_instance": copilot._local_kokoro_instance is not None if copilot else False,
            "sample_rate": 24000,
            "precision": "Zero-Assumption High-Fidelity",
            "normalizer": "VoiceNormalizer v2.0 Active"
        }

    return {"error": f"Unknown tool: {name}"}


def main():
    """Main JSON-RPC stdio MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line_str = line.strip()
            if not line_str:
                continue

            req = json.loads(line_str)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "antigravity-voice-mcp",
                            "version": "2.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS_SCHEMA}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                tool_result = handle_tool_call(tool_name, tool_args)
                res = {
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
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method {method} not found"}
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"[Antigravity Voice MCP Error] {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
